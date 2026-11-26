#!/usr/bin/env python3
"""
Multi-threaded album processor for the Rebecca Richards Photography Album Scraper.
Provides concurrent album processing capabilities to significantly speed up the scraping process.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from selenium.webdriver.remote.webelement import WebElement

from ..core.config import ScraperConfig
from ..web.webdriver_manager import WebDriverManager
from ..web.element_interactions import (
    ScrollManager, ElementInteractor, ClickableElementFinder, ElementInspector
)
from ..metadata.album_name_extractor import AlbumNameExtractor
from ..processing.image_processor import ImageProcessor
from ..processing.gallery_scraper import GalleryScraper
from ..metadata.metadata_extractor import MetadataExtractor
from ..metadata.metadata_manager import MetadataManager
from ..core.logger import logger
from ..utils.common_utils import CommonUtils


@dataclass
class AlbumTask:
    """Represents a single album processing task."""
    album_element: WebElement
    album_index: int
    albums_url: str


class ThreadSafeAlbumProcessor:
    """
    Thread-safe album processor that handles individual albums.
    Each thread gets its own WebDriver instance and dependencies.
    """
    
    def __init__(self, config: ScraperConfig):
        """
        Initialize thread-safe album processor.
        
        Args:
            config: ScraperConfig instance
        """
        self.config = config
        
        # Shared metadata manager (thread-safe)
        self.metadata_manager = MetadataManager(config)
        
        # Thread-safe counters
        self._stats_lock = Lock()
        self._albums_processed = 0
        self._total_images = 0
    
    def create_thread_dependencies(self) -> Tuple[WebDriverManager, Any, Any, Any, Any]:
        """
        Create thread-specific dependencies including WebDriver.
        Each thread needs its own WebDriver instance.
        
        Returns:
            Tuple of (webdriver_manager, album_processor, gallery_scraper, element_interactor, window_manager)
        """
        # Create thread-specific WebDriver manager
        webdriver_manager = WebDriverManager(self.config)
        if not webdriver_manager.start_driver():
            raise Exception("Failed to start WebDriver for thread")
        
        # Initialize thread-specific services
        scroll_manager = ScrollManager(self.config, webdriver_manager)
        clickable_finder = ClickableElementFinder(self.config)
        element_interactor = ElementInteractor(
            self.config, webdriver_manager, scroll_manager, clickable_finder
        )
        
        # Initialize business logic services
        album_name_extractor = AlbumNameExtractor(self.config)
        image_processor = ImageProcessor(self.config, webdriver_manager)
        
        # Initialize metadata services (shared metadata_manager, thread-specific extractor)
        metadata_extractor = MetadataExtractor(self.config, webdriver_manager)
        
        # Initialize scraping services
        gallery_scraper = GalleryScraper(
            self.config, webdriver_manager, scroll_manager, 
            image_processor, use_threading=self.config.enable_threading
        )
        
        # Initialize processing services inline to avoid circular imports
        # AlbumPageProcessor equivalent functionality with metadata support
        class LocalAlbumPageProcessor:
            def __init__(self, config, webdriver_manager, element_interactor, album_name_extractor, gallery_scraper, metadata_extractor, metadata_manager):
                self.config = config
                self.webdriver_manager = webdriver_manager
                self.element_interactor = element_interactor
                self.album_name_extractor = album_name_extractor
                self.gallery_scraper = gallery_scraper
                self.metadata_extractor = metadata_extractor
                self.metadata_manager = metadata_manager
            
            def process_album_page(self, album_url, album_index):
                try:
                    logger.blank_line()
                    logger.progress(f"Processing album: {album_url}")
                    
                    # Check if album already processed using common utility
                    should_skip, existing_metadata = CommonUtils.metadata_check.should_skip_album(
                        self.metadata_manager, album_url, self.config.output_dir
                    )
                    if should_skip:
                        self.gallery_scraper.albums_processed += 1
                        return True
                    
                    # Navigate to album page
                    if not self.webdriver_manager.navigate_to(album_url):
                        return False
                        
                    time.sleep(self.config.delay)
                    
                    # Extract metadata from the album page
                    logger.metadata("Extracting album metadata...")
                    album_metadata = self.metadata_extractor.extract_album_metadata(album_url)
                    
                    # Use extracted name or fallback to legacy extraction
                    album_name = album_metadata.get('name')
                    if not album_name:
                        logger.warning("Metadata extraction failed, falling back to legacy name extraction...")
                        album_name = self.album_name_extractor.extract_album_name(
                            album_url, self.webdriver_manager, album_index
                        )
                        # Update metadata with legacy extracted name and generate clean name
                        album_metadata['name'] = album_name
                        album_metadata['title'] = album_name
                        album_metadata['clean_name'] = self.metadata_manager._clean_album_name(album_name)
                    
                    logger.files(f"Album name: {album_name}")
                    if album_metadata.get('date'):
                        logger.info(f"📅 Album date: {album_metadata['date']}")
                    
                    # Look for "View Photos" link
                    view_photos_link = self.gallery_scraper.element_finder.find_view_photos_link()
                    
                    if view_photos_link:
                        # Use common utility for clicking with fallback
                        if CommonUtils.click.safe_click_with_js_fallback(view_photos_link, self.webdriver_manager, self.config.delay * 2):
                            # Get or generate clean name for directory creation
                            clean_name = CommonUtils.name_processing.get_clean_name_from_metadata_or_generate(
                                album_metadata, album_name, self.metadata_manager
                            )
                            
                            # Scrape the gallery page using clean name for directory
                            images_downloaded = self.gallery_scraper.scrape_gallery_page(clean_name)
                            
                            if images_downloaded > 0:
                                # Save metadata after successful scraping using common utility
                                CommonUtils.metadata_update.save_successful_album_metadata(
                                    album_metadata, album_name, images_downloaded, self.metadata_manager
                                )
                                self.gallery_scraper.albums_processed += 1
                                return True
                            else:
                                # Save metadata for failed attempts using common utility
                                CommonUtils.metadata_update.save_failed_album_metadata(
                                    album_metadata, album_name, "No images downloaded", self.metadata_manager
                                )
                                return False
                        else:
                            # Save metadata for click failure using common utility
                            CommonUtils.metadata_update.save_failed_album_metadata(
                                album_metadata, album_name, "Failed to click 'View Photos' link", self.metadata_manager
                            )
                            return False
                    else:
                        # Save metadata for albums without View Photos link using common utility
                        CommonUtils.metadata_update.save_failed_album_metadata(
                            album_metadata, album_name, "No 'View Photos' link found", self.metadata_manager
                        )
                        return False
                        
                except Exception as e:
                    # Save metadata for unexpected errors using common utility
                    album_metadata_fallback = {
                        'url': album_url, 
                        'images_downloaded': 0, 
                        'scraping_success': False, 
                        'error': f"Unexpected error: {e}"
                    }
                    CommonUtils.error_handling.handle_metadata_save_error(
                        album_metadata_fallback, self.metadata_manager, "album processing"
                    )
                    logger.error(f"Error processing album page {album_url}", exception=e)
                    return False
        
        album_processor = LocalAlbumPageProcessor(
            self.config, webdriver_manager, element_interactor, 
            album_name_extractor, gallery_scraper, metadata_extractor, self.metadata_manager
        )
        
        # WindowManager equivalent functionality
        class LocalWindowManager:
            def __init__(self, webdriver_manager):
                self.webdriver_manager = webdriver_manager
            
            def return_to_albums_page(self, albums_url):
                logger.info("Returning to albums page...")
                
                # Check if we're in a new tab/window
                current_windows = self.webdriver_manager.get_window_handles()
                if len(current_windows) > 1:
                    # We opened a new tab, close it and go back to the original
                    logger.info("Closing new tab and returning to original albums page...")
                    self.webdriver_manager.close_current_window()  # Close current tab
                    self.webdriver_manager.switch_to_window(current_windows[0])  # Switch to first tab (albums page)
                else:
                    # We navigated in the same tab, go back to albums page
                    self.webdriver_manager.navigate_to(albums_url)
        
        window_manager = LocalWindowManager(webdriver_manager)
        
        return webdriver_manager, album_processor, gallery_scraper, element_interactor, window_manager
    
    def process_album_task(self, task: AlbumTask) -> Dict[str, Any]:
        """
        Process a single album task in a thread-safe manner.
        
        Args:
            task: AlbumTask to process
            
        Returns:
            Dict containing processing results
        """
        result = {
            'success': False,
            'album_index': task.album_index,
            'images_downloaded': 0,
            'error': None,
            'album_name': None
        }
        
        webdriver_manager = None
        
        try:
            # Reduced verbosity - only show major milestones
            
            # Create thread-specific dependencies
            webdriver_manager, album_processor, gallery_scraper, element_interactor, window_manager = self.create_thread_dependencies()
            
            # Navigate to albums page first
            if not webdriver_manager.navigate_to(task.albums_url):
                result['error'] = "Failed to navigate to albums page"
                return result
            
            time.sleep(self.config.delay)
            
            # Re-find the album element (since we're in a new WebDriver instance)
            # We need to get fresh album elements since WebElements can't be shared between threads
            gallery_scraper_for_elements = GalleryScraper(
                self.config, webdriver_manager, ScrollManager(self.config, webdriver_manager), 
                ImageProcessor(self.config, webdriver_manager), use_threading=False
            )
            
            album_elements = gallery_scraper_for_elements.get_album_elements_from_page()
            if not album_elements or len(album_elements) < task.album_index:
                result['error'] = f"Could not find album element at index {task.album_index}"
                return result
            
            # Get the correct album element for this thread
            album_element = album_elements[task.album_index - 1]  # Convert to 0-based index
            
            # Thread processing album silently
            
            # Use enhanced debugging for first few elements
            inspect_element = task.album_index <= 3
            
            if element_interactor.safe_click(album_element, inspect_first=inspect_element):
                # Wait for navigation
                time.sleep(self.config.delay)
                
                # Process the album page we landed on
                current_url = webdriver_manager.get_current_url()
                if album_processor.process_album_page(current_url, album_index=task.album_index):
                    result['success'] = True
                    result['images_downloaded'] = gallery_scraper.get_stats().get('total_downloaded', 0)
                    
                    # Update thread-safe stats
                    with self._stats_lock:
                        self._albums_processed += 1
                        self._total_images += result['images_downloaded']
                    
                    logger.success(f"Album {task.album_index}: {result['images_downloaded']} images")
                else:
                    result['error'] = "Failed to process album page"
                    logger.error(f"Album {task.album_index}: Processing failed")
            else:
                result['error'] = f"Failed to click album element {task.album_index}"
                
        except Exception as e:
            result['error'] = str(e)
        
        finally:
            # Clean up thread-specific WebDriver
            if webdriver_manager:
                try:
                    webdriver_manager.stop_driver()
                except Exception as cleanup_error:
                    logger.warning(f"Error cleaning up WebDriver for thread {task.album_index}", exception=cleanup_error)
        
        return result
    
    def get_stats(self) -> Dict[str, int]:
        """Get thread-safe statistics."""
        with self._stats_lock:
            return {
                'albums_processed': self._albums_processed,
                'total_downloaded': self._total_images
            }
    
    def should_skip_album(self, potential_url: str) -> bool:
        """
        Determine if an album should be skipped based on metadata.json.
        
        Args:
            potential_url: URL of the album to check
            
        Returns:
            bool: True if album should be skipped (already successfully processed)
        """
        try:
            existing_metadata = self.metadata_manager.get_album_metadata(potential_url)
            if existing_metadata:
                # Check if scraping was successful and has images
                if (existing_metadata.get('scraping_success') and 
                    existing_metadata.get('images_downloaded', 0) > 0):
                    
                    # Verify directory still exists
                    clean_name = existing_metadata.get('clean_name')
                    if clean_name:
                        album_dir = self.config.output_dir / clean_name
                        if album_dir.exists() and album_dir.is_dir():
                            return True
            return False
        except Exception:
            # If there's any error checking metadata, don't skip (safer to reprocess)
            return False
    
    def reset_stats(self) -> None:
        """Reset thread-safe statistics."""
        with self._stats_lock:
            self._albums_processed = 0
            self._total_images = 0


class ThreadedAlbumProcessor:
    """
    Multi-threaded album processor that coordinates concurrent album processing.
    Single responsibility: Managing concurrent album operations.
    """
    
    def __init__(self, config: ScraperConfig):
        """
        Initialize threaded album processor.
        
        Args:
            config: ScraperConfig instance
        """
        self.config = config
        self.thread_safe_processor = ThreadSafeAlbumProcessor(config)
    
    def process_albums_batch(self, album_elements: List[WebElement], 
                           albums_url: str) -> Tuple[int, int, List[Dict[str, Any]]]:
        """
        Process multiple albums using thread pool.
        
        Args:
            album_elements: List of album elements to process
            albums_url: URL of the albums page
            
        Returns:
            Tuple of (successful_albums, total_images_downloaded, results_list)
        """
        if not album_elements:
            logger.error("No albums to process")
            return 0, 0, []
        
        logger.progress(f"Starting threaded album processing of {len(album_elements)} albums using {self.config.max_album_threads} threads")
        
        # Display existing metadata statistics
        metadata_manager = self.thread_safe_processor.metadata_manager
        if metadata_manager.metadata_file.exists():
            metadata_stats = metadata_manager.get_stats()
            successful_albums = len([a for a in metadata_manager.get_all_albums() if a.get('scraping_success')])
            logger.info(f"Found existing metadata: {metadata_stats['total_albums']} albums ({successful_albums} successful)")
        else:
            logger.info("No existing metadata found - starting fresh")
        
        # Create album tasks
        tasks = []
        for i, album_element in enumerate(album_elements, 1):
            task = AlbumTask(
                album_element=album_element,
                album_index=i,
                albums_url=albums_url
            )
            tasks.append(task)
        
        # Execute album processing with thread pool
        results = []
        successful_albums = 0
        total_images_downloaded = 0
        
        with ThreadPoolExecutor(max_workers=self.config.max_album_threads) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self.thread_safe_processor.process_album_task, task): task 
                for task in tasks
            }
            
            # Process completed album processing
            for future in as_completed(future_to_task, timeout=self.config.album_thread_timeout * len(tasks)):
                task = future_to_task[future]
                
                try:
                    result = future.result(timeout=self.config.album_thread_timeout)
                    results.append(result)
                    
                    if result['success']:
                        successful_albums += 1
                        total_images_downloaded += result['images_downloaded']
                        logger.success(f"Album {result['album_index']} completed: {result['images_downloaded']} images")
                    else:
                        logger.error(f"Album {result['album_index']} failed: {result['error']}")
                        
                except Exception as e:
                    logger.error(f"Album {task.album_index} threw exception", exception=e)
                    results.append({
                        'success': False,
                        'album_index': task.album_index,
                        'images_downloaded': 0,
                        'error': str(e),
                        'album_name': None
                    })
        
        # Display final statistics including metadata
        final_metadata_stats = metadata_manager.get_stats()
        logger.success(f"Threaded album processing completed: {successful_albums}/{len(album_elements)} albums, {total_images_downloaded} total images")
        logger.stats(f"Final metadata: {final_metadata_stats['total_albums']} albums tracked, {final_metadata_stats['albums_with_dates']} with dates")
        logger.metadata(f"Metadata saved to: {metadata_manager.metadata_file}")
        
        return successful_albums, total_images_downloaded, results
    
    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return self.thread_safe_processor.get_stats()
    
    def reset_stats(self) -> None:
        """Reset processing statistics."""
        self.thread_safe_processor.reset_stats()