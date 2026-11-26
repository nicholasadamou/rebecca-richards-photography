#!/usr/bin/env python3
"""
Multi-threaded image downloader for the Rebecca Richards Photography Album Scraper.
Provides concurrent downloading capabilities to significantly speed up the scraping process.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from threading import Lock
from typing import List, Dict, Any, Tuple
from pathlib import Path
from dataclasses import dataclass

from ..core.config import ScraperConfig
from ..processing.image_processor import ImageProcessor, ImageUrlProcessor, ImageDownloader, AlbumDirectoryManager
from ..core.logger import logger


@dataclass
class DownloadTask:
    """Represents a single image download task."""
    src: str
    album_dir: Path
    index: int
    album_name: str


class ThreadSafeImageProcessor:
    """
    Thread-safe wrapper around ImageProcessor components.
    Ensures thread safety for multi-threaded downloads.
    """
    
    def __init__(self, config: ScraperConfig, webdriver_manager):
        """
        Initialize thread-safe image processor.
        
        Args:
            config: ScraperConfig instance
            webdriver_manager: WebDriverManager instance for referrer
        """
        self.config = config
        self.webdriver_manager = webdriver_manager
        
        # Create components (these are thread-safe)
        self.url_processor = ImageUrlProcessor(config)
        self.downloader = ImageDownloader(config, webdriver_manager)
        self.directory_manager = AlbumDirectoryManager(config)
        
        # Thread-safe counter
        self._download_lock = Lock()
        self._total_downloaded = 0
    
    def process_download_task(self, task: DownloadTask) -> Dict[str, Any]:
        """
        Process a single download task in a thread-safe manner.
        
        Args:
            task: DownloadTask to process
            
        Returns:
            Dict containing download results
        """
        result = {
            'success': False,
            'filepath': None,
            'filename': None,
            'skipped': False,
            'error': None,
            'task': task
        }
        
        try:
            # Get high quality version of image URL
            high_quality_src = self.url_processor.get_high_quality_image_url(task.src)
            
            # Extract filename from URL
            filename = self.url_processor.extract_filename_from_url(high_quality_src, task.index)
            filepath = task.album_dir / filename
            
            result['filename'] = filename
            result['filepath'] = filepath
            
            # Skip if already exists
            if self.directory_manager.file_exists(filepath):
                logger.info(f"Skipping existing file: {filename}")
                result['skipped'] = True
                result['success'] = True
                return result
            
            logger.progress(f"Downloading {task.index}: {filename}")
            
            # Download the image
            if self.downloader.download_image(high_quality_src, filepath):
                # Check if file downloaded properly
                if self.downloader.is_valid_download(filepath):
                    result['success'] = True
                    with self._download_lock:
                        self._total_downloaded += 1
                else:
                    logger.warning(f"Downloaded file seems too small, trying original URL: {filename}")
                    filepath.unlink()  # Delete small file
                    
                    # Try downloading original URL
                    if self.downloader.download_image(task.src, filepath):
                        if self.downloader.is_valid_download(filepath):
                            result['success'] = True
                            with self._download_lock:
                                self._total_downloaded += 1
                        else:
                            result['error'] = "Both high-quality and original downloads failed validation"
                    else:
                        result['error'] = "Original URL download failed"
            else:
                result['error'] = "High-quality URL download failed"
                
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error processing image {task.index}", exception=e)
        
        return result
    
    def get_download_count(self) -> int:
        """Get thread-safe download count."""
        with self._download_lock:
            return self._total_downloaded
    
    def reset_download_count(self) -> None:
        """Reset thread-safe download count."""
        with self._download_lock:
            self._total_downloaded = 0


class ThreadedImageDownloader:
    """
    Multi-threaded image downloader that coordinates concurrent downloads.
    Single responsibility: Managing concurrent download operations.
    """
    
    def __init__(self, config: ScraperConfig, webdriver_manager):
        """
        Initialize threaded downloader.
        
        Args:
            config: ScraperConfig instance
            webdriver_manager: WebDriverManager instance
        """
        self.config = config
        self.thread_safe_processor = ThreadSafeImageProcessor(config, webdriver_manager)
    
    def download_images_batch(self, unique_images: Dict[str, Any], album_dir: Path, 
                            album_name: str) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Download multiple images using thread pool.
        
        Args:
            unique_images: Dict of {src: img_element} for images to download
            album_dir: Directory to save images to
            album_name: Name of the album for logging
            
        Returns:
            Tuple of (successful_downloads, results_list)
        """
        if not unique_images:
            logger.error("No images to download")
            return 0, []
        
        logger.progress(f"Starting threaded download of {len(unique_images)} images using {self.config.max_download_threads} threads")
        
        # Create download tasks
        tasks = []
        for i, (src, img_element) in enumerate(unique_images.items(), 1):
            task = DownloadTask(
                src=src,
                album_dir=album_dir,
                index=i,
                album_name=album_name
            )
            tasks.append(task)
        
        # Execute downloads with thread pool
        results = []
        successful_downloads = 0
        
        with ThreadPoolExecutor(max_workers=self.config.max_download_threads) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self.thread_safe_processor.process_download_task, task): task 
                for task in tasks
            }
            
            # Process completed downloads
            for future in as_completed(future_to_task, timeout=self.config.thread_timeout * len(tasks)):
                task = future_to_task[future]
                
                try:
                    result = future.result(timeout=self.config.thread_timeout)
                    results.append(result)
                    
                    if result['success'] and not result['skipped']:
                        successful_downloads += 1
                        
                    # Progress indicator
                    completed = len(results)
                    if completed % 5 == 0 or completed == len(tasks):  # Show progress every 5 downloads
                        logger.stats(f"Progress: {completed}/{len(tasks)} downloads processed")
                        
                except Exception as e:
                    logger.error(f"Download thread failed for {task.album_name} image {task.index}", exception=e)
                    results.append({
                        'success': False,
                        'error': str(e),
                        'task': task
                    })
        
        logger.success(f"Threaded download completed: {successful_downloads} new images downloaded")
        return successful_downloads, results
    
    def download_images_sequential_fallback(self, unique_images: Dict[str, Any], 
                                          album_dir: Path, album_name: str) -> int:
        """
        Fallback to sequential download if threading fails.
        
        Args:
            unique_images: Dict of {src: img_element} for images to download
            album_dir: Directory to save images to  
            album_name: Name of the album for logging
            
        Returns:
            int: Number of successful downloads
        """
        logger.warning("Falling back to sequential download mode")
        
        downloaded_count = 0
        for i, (src, img_element) in enumerate(unique_images.items(), 1):
            task = DownloadTask(
                src=src,
                album_dir=album_dir,
                index=i,
                album_name=album_name
            )
            
            result = self.thread_safe_processor.process_download_task(task)
            
            if result['success'] and not result['skipped']:
                downloaded_count += 1
                
            # Add delay for sequential mode
            time.sleep(self.config.download_delay)
        
        return downloaded_count
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get download statistics.
        
        Returns:
            Dict containing download stats
        """
        return {
            'total_downloaded': self.thread_safe_processor.get_download_count()
        }
    
    def reset_stats(self) -> None:
        """Reset download statistics."""
        self.thread_safe_processor.reset_download_count()