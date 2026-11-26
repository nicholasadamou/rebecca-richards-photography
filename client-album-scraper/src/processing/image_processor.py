#!/usr/bin/env python3
"""
Image processing classes for the Rebecca Richards Photography Album Scraper.
Handles image downloading, URL processing, and file management following SRP.
"""

import os
import re
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from ..core.config import ScraperConfig
from ..web.webdriver_manager import WebDriverManager
from ..core.logger import logger
from ..utils.common_utils import CommonUtils


class ImageUrlProcessor:
    """
    Processes and optimizes image URLs.
    Single responsibility: URL manipulation and optimization.
    """

    def __init__(self, config: ScraperConfig):
        """
        Initialize with configuration.

        Args:
            config: ScraperConfig instance
        """
        self.config = config

    def get_high_quality_image_url(self, img_url: str) -> str:
        """
        Convert image URL to highest quality version.
        Wix images have parameters like w_600,h_600 that can be modified.

        Args:
            img_url: Original image URL

        Returns:
            str: High quality image URL
        """
        if "wixstatic.com" in img_url:
            # Remove size restrictions and get original
            # Replace parameters like /v1/fill/w_600,h_600,fp_0.50_0.50,q_90,usm_1.00_0.66_0.01/
            # with higher quality settings
            pattern = r'/v1/fill/[^/]+/'
            replacement = f'/v1/fill/w_{self.config.high_quality_width},h_{self.config.high_quality_height},al_c,q_95/'

            high_quality_url = re.sub(pattern, replacement, img_url)

            # Remove webp conversion if present
            high_quality_url = re.sub(r'\.webp(\?.*)?$', '', high_quality_url)

            return high_quality_url

        return img_url

    def extract_filename_from_url(self, url: str, index: int) -> str:
        """
        Extract filename from URL or generate one.

        Args:
            url: Image URL
            index: Image index for fallback naming

        Returns:
            str: Clean filename
        """
        # Extract filename from URL
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)

        # Clean filename and ensure it has proper extension
        if not filename or filename == '/':
            filename = f"image_{index:03d}.jpg"
        elif not any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            filename += '.jpg'

        # Clean filename of invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

        return filename


class ImageDownloader:
    """
    Downloads images from URLs.
    Single responsibility: Image downloading and file management.
    """

    def __init__(self, config: ScraperConfig, webdriver_manager: WebDriverManager):
        """
        Initialize with configuration and WebDriver manager.

        Args:
            config: ScraperConfig instance
            webdriver_manager: WebDriverManager instance for referrer
        """
        self.config = config
        self.webdriver_manager = webdriver_manager

    def download_image(self, url: str, filepath: Path) -> bool:
        """
        Download an image from URL to filepath.

        Args:
            url: Image URL to download
            filepath: Path to save image to

        Returns:
            bool: True if download successful, False otherwise
        """
        try:
            headers = {
                'User-Agent': self.config.user_agent,
                'Referer': self.webdriver_manager.get_current_url()
            }

            response = requests.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return True
        except Exception as e:
            logger.error(f"Failed to download {url}", exception=e)
            return False

    def is_valid_download(self, filepath: Path) -> bool:
        """
        Check if downloaded file is valid (not too small).

        Args:
            filepath: Path to downloaded file

        Returns:
            bool: True if file is valid, False otherwise
        """
        try:
            return filepath.exists() and filepath.stat().st_size >= self.config.min_file_size_bytes
        except:
            return False


class AlbumDirectoryManager:
    """
    Manages album directory creation and file operations.
    Single responsibility: Directory and file management.
    """

    def __init__(self, config: ScraperConfig):
        """
        Initialize with configuration.

        Args:
            config: ScraperConfig instance
        """
        self.config = config

    def create_album_directory(self, album_name: str) -> Path:
        """
        Create album directory if it doesn't exist.

        Args:
            album_name: Name of the album for directory

        Returns:
            Path: Path to album directory
        """
        album_dir = self.config.output_dir / album_name
        album_dir.mkdir(exist_ok=True)
        return album_dir

    def file_exists(self, filepath: Path) -> bool:
        """
        Check if file already exists.
        
        Args:
            filepath: Path to check
            
        Returns:
            bool: True if file exists, False otherwise
        """
        return filepath.exists()
    
    def count_images_in_directory(self, album_name: str) -> int:
        """
        Count image files in an album directory using common utility.
        
        Args:
            album_name: Name of the album
            
        Returns:
            int: Number of image files found
        """
        album_dir = self.config.output_dir / album_name
        return CommonUtils.image_files.count_images_in_directory(album_dir)
    
    def album_exists_with_images(self, album_name: str) -> bool:
        """
        Check if album directory exists and contains images.
        
        Args:
            album_name: Name of the album
            
        Returns:
            bool: True if album directory exists and has images, False otherwise
        """
        return self.count_images_in_directory(album_name) > 0


class ImageProcessor:
    """
    Main image processor that coordinates all image-related operations.
    Orchestrates URL processing, downloading, and file management.
    """

    def __init__(self, config: ScraperConfig, webdriver_manager: WebDriverManager):
        """
        Initialize with configuration and dependencies.

        Args:
            config: ScraperConfig instance
            webdriver_manager: WebDriverManager instance
        """
        self.config = config
        self.webdriver_manager = webdriver_manager

        # Initialize components
        self.url_processor = ImageUrlProcessor(config)
        self.downloader = ImageDownloader(config, webdriver_manager)
        self.directory_manager = AlbumDirectoryManager(config)

        # Stats
        self.total_downloaded = 0

    def process_and_download_image(self, src: str, album_dir: Path, index: int) -> Dict[str, Any]:
        """
        Process image URL and download image.

        Args:
            src: Original image source URL
            album_dir: Directory to save image to
            index: Image index for naming

        Returns:
            Dict containing download results
        """
        result = {
            'success': False,
            'filepath': None,
            'filename': None,
            'skipped': False,
            'error': None
        }

        try:
            # Get high quality version of image URL
            high_quality_src = self.url_processor.get_high_quality_image_url(src)

            # Extract filename from URL
            filename = self.url_processor.extract_filename_from_url(high_quality_src, index)
            filepath = album_dir / filename

            result['filename'] = filename
            result['filepath'] = filepath

            # Skip if already exists
            if self.directory_manager.file_exists(filepath):
                logger.info(f"Skipping existing file: {filename}")
                result['skipped'] = True
                result['success'] = True
                return result

            logger.progress(f"Downloading {index}: {filename}")

            # Download the image
            if self.downloader.download_image(high_quality_src, filepath):
                # Check if file downloaded properly
                if self.downloader.is_valid_download(filepath):
                    result['success'] = True
                    self.total_downloaded += 1
                else:
                    logger.warning("Downloaded file seems too small, trying original URL")
                    filepath.unlink()  # Delete small file

                    # Try downloading original URL
                    if self.downloader.download_image(src, filepath):
                        if self.downloader.is_valid_download(filepath):
                            result['success'] = True
                            self.total_downloaded += 1
                        else:
                            result['error'] = "Both high-quality and original downloads failed validation"
                    else:
                        result['error'] = "Original URL download failed"
            else:
                result['error'] = "High-quality URL download failed"

            # Small delay between downloads
            time.sleep(self.config.download_delay)

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error processing image {index}", exception=e)

        return result

    def get_download_stats(self) -> Dict[str, int]:
        """
        Get download statistics.

        Returns:
            Dict containing download stats
        """
        return {
            'total_downloaded': self.total_downloaded
        }

    def reset_stats(self) -> None:
        """Reset download statistics."""
        self.total_downloaded = 0
    
    def get_album_info(self, album_name: str) -> Dict[str, Any]:
        """
        Get comprehensive information about an album.
        
        Args:
            album_name: Name of the album
            
        Returns:
            Dict containing album information
        """
        album_dir = self.config.output_dir / album_name
        
        return {
            'name': album_name,
            'exists': album_dir.exists(),
            'image_count': self.count_existing_images(album_name),
            'is_processed': self.is_album_processed(album_name),
            'directory_path': str(album_dir)
        }

    def is_album_processed(self, album_name: str) -> bool:
        """
        Check if an album has already been processed by verifying if its directory exists.

        Args:
            album_name: Name of the album

        Returns:
            bool: True if album directory exists and contains images, False otherwise
        """
        return self.directory_manager.album_exists_with_images(album_name)
    
    def count_existing_images(self, album_name: str) -> int:
        """
        Count the number of images already downloaded for an album.
        
        Args:
            album_name: Name of the album
            
        Returns:
            int: Number of image files in the album directory
        """
        return self.directory_manager.count_images_in_directory(album_name)
