#!/usr/bin/env python3
"""
Common utility functions for the Rebecca Richards Photography Album Scraper.
This module contains reusable functions that are shared across multiple modules
to follow DRY (Don't Repeat Yourself) principles.
"""

import time
import re
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from selenium.webdriver.remote.webelement import WebElement

from ..core.logger import logger


class ClickStrategies:
    """
    Unified click strategies to handle element clicking with fallbacks.
    Eliminates duplicate click logic across modules.
    """
    
    @staticmethod
    def safe_click_with_js_fallback(element: WebElement, webdriver_manager, delay: float = 2.0) -> bool:
        """
        Attempt to click an element using JavaScript first (to avoid ElementClickInterceptedException),
        with direct click as fallback.
        
        Args:
            element: WebElement to click
            webdriver_manager: WebDriverManager instance
            delay: Delay after successful click
            
        Returns:
            bool: True if click successful, False otherwise
        """
        try:
            # Primary: JavaScript click (avoids intercepted exceptions)
            logger.network("Clicking element using JavaScript...")
            driver = webdriver_manager.get_driver()
            driver.execute_script("arguments[0].click();", element)
            time.sleep(delay)
            return True
            
        except Exception as js_error:
            logger.warning("JavaScript click failed, trying direct click as fallback...")
            try:
                # Fallback: Direct click
                element.click()
                time.sleep(delay)
                return True
                
            except Exception as direct_error:
                logger.error(f"Both click methods failed: JS({js_error}), Direct({direct_error})")
                return False


class AlbumMetadataChecker:
    """
    Common logic for checking if albums have already been processed.
    Eliminates duplicate metadata checking logic.
    """
    
    @staticmethod
    def should_skip_album(metadata_manager, album_url: str, output_dir: Path) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Determine if an album should be skipped based on existing metadata.
        
        Args:
            metadata_manager: MetadataManager instance
            album_url: URL of the album to check
            output_dir: Base output directory for albums
            
        Returns:
            Tuple[bool, Optional[Dict]]: (should_skip, existing_metadata)
        """
        try:
            existing_metadata = metadata_manager.get_album_metadata(album_url)
            if not existing_metadata:
                return False, None
                
            # Check if scraping was successful and has images
            if (existing_metadata.get('scraping_success') and 
                existing_metadata.get('images_downloaded', 0) > 0):
                
                # Verify directory still exists
                clean_name = existing_metadata.get('clean_name')
                if clean_name:
                    album_dir = output_dir / clean_name
                    if album_dir.exists() and album_dir.is_dir():
                        # Count existing images for verification
                        image_files = list(album_dir.glob('*.jpg')) + list(album_dir.glob('*.png')) + list(album_dir.glob('*.jpeg'))
                        images_count = existing_metadata.get('images_downloaded', len(image_files))
                        logger.info(f"Album '{existing_metadata.get('name', 'Unknown')}' already successfully processed ({images_count} images in metadata), skipping...")
                        return True, existing_metadata
                    else:
                        logger.warning(f"Metadata indicates success but directory missing for '{existing_metadata.get('name', 'Unknown')}', re-processing...")
                else:
                    logger.warning("Metadata exists but no clean_name found for album, re-processing...")
            else:
                # Album was attempted but failed, check if we should retry
                if existing_metadata.get('scraping_success') is False:
                    logger.warning(f"Album '{existing_metadata.get('name', 'Unknown')}' previously failed ({existing_metadata.get('error', 'Unknown error')}), re-processing...")
                else:
                    logger.info("Album found in metadata but status unclear, re-processing...")
                    
            return False, existing_metadata
            
        except Exception as e:
            logger.warning(f"Error checking album metadata: {e}")
            return False, None


class AlbumNameProcessor:
    """
    Common logic for processing album names and generating clean names.
    Eliminates duplicate name processing logic.
    """
    
    @staticmethod
    def clean_album_name(album_name: str) -> str:
        """
        Clean album name for use as directory name.
        
        Args:
            album_name: Original album name
            
        Returns:
            str: Clean album name safe for directory use
        """
        if not album_name:
            return "unknown-album"
            
        # Remove common photography-related suffixes
        clean_name = re.sub(r'\s+(photography|photos?|album|session|event)$', '', album_name, flags=re.IGNORECASE)
        
        # Replace problematic characters with underscores
        clean_name = re.sub(r'[<>:"/\\|?*]', '_', clean_name)
        
        # Replace spaces with hyphens or underscores for better readability
        clean_name = re.sub(r'\s+', '_', clean_name)
        
        # Remove consecutive underscores
        clean_name = re.sub(r'_+', '_', clean_name)
        
        # Remove leading/trailing underscores
        clean_name = clean_name.strip('_')
        
        # Ensure it's not empty
        if not clean_name:
            return "unknown-album"
            
        return clean_name
    
    @staticmethod
    def get_clean_name_from_metadata_or_generate(album_metadata: Dict[str, Any], album_name: str, metadata_manager) -> str:
        """
        Get clean name from metadata or generate it.
        
        Args:
            album_metadata: Album metadata dictionary
            album_name: Album name to use for generation
            metadata_manager: MetadataManager instance for clean name generation
            
        Returns:
            str: Clean name for directory creation
        """
        clean_name = album_metadata.get('clean_name')
        if not clean_name:
            if hasattr(metadata_manager, '_clean_album_name'):
                clean_name = metadata_manager._clean_album_name(album_name)
            else:
                clean_name = AlbumNameProcessor.clean_album_name(album_name)
            album_metadata['clean_name'] = clean_name
        return clean_name


class MetadataUpdater:
    """
    Common patterns for updating metadata after album processing.
    Eliminates duplicate metadata updating logic.
    """
    
    @staticmethod
    def save_successful_album_metadata(album_metadata: Dict[str, Any], album_name: str, 
                                     images_downloaded: int, metadata_manager) -> None:
        """
        Save metadata for successfully processed album.
        
        Args:
            album_metadata: Album metadata dictionary
            album_name: Name of the album
            images_downloaded: Number of images downloaded
            metadata_manager: MetadataManager instance
        """
        album_metadata['images_downloaded'] = images_downloaded
        album_metadata['scraping_success'] = True
        metadata_manager.add_album_metadata(album_metadata)
        logger.metadata(f"Saved metadata for album: {album_name}")
    
    @staticmethod
    def save_failed_album_metadata(album_metadata: Dict[str, Any], album_name: str, 
                                 error: str, metadata_manager) -> None:
        """
        Save metadata for failed album processing.
        
        Args:
            album_metadata: Album metadata dictionary
            album_name: Name of the album
            error: Error message describing the failure
            metadata_manager: MetadataManager instance
        """
        album_metadata['images_downloaded'] = 0
        album_metadata['scraping_success'] = False
        album_metadata['error'] = error
        metadata_manager.add_album_metadata(album_metadata)
        logger.warning(f"Saved failure metadata for album: {album_name}")


class ErrorHandlingUtils:
    """
    Common error handling patterns and utilities.
    Provides consistent error handling across modules.
    """
    
    @staticmethod
    def safe_execute_with_fallback(primary_action, fallback_action, 
                                  primary_description: str, fallback_description: str):
        """
        Execute a primary action with a fallback if it fails.
        
        Args:
            primary_action: Primary function to execute
            fallback_action: Fallback function to execute if primary fails
            primary_description: Description of primary action for logging
            fallback_description: Description of fallback action for logging
            
        Returns:
            Tuple[bool, Any]: (success, result)
        """
        try:
            logger.progress(f"Attempting {primary_description}...")
            result = primary_action()
            return True, result
        except Exception as primary_error:
            logger.warning(f"{primary_description} failed: {primary_error}")
            try:
                logger.progress(f"Attempting {fallback_description}...")
                result = fallback_action()
                return True, result
            except Exception as fallback_error:
                logger.error(f"Both {primary_description} and {fallback_description} failed")
                logger.error(f"Primary error: {primary_error}")
                logger.error(f"Fallback error: {fallback_error}")
                return False, None
    
    @staticmethod
    def handle_metadata_save_error(metadata_dict: Dict[str, Any], metadata_manager, 
                                  context: str = "album processing"):
        """
        Safely handle metadata saving with error handling.
        
        Args:
            metadata_dict: Metadata to save
            metadata_manager: MetadataManager instance
            context: Context description for logging
        """
        try:
            metadata_manager.add_album_metadata(metadata_dict)
        except Exception as e:
            logger.warning(f"Failed to save metadata during {context}", exception=e)


class ImageFileUtils:
    """
    Common image file handling utilities.
    Eliminates duplicate image handling logic.
    """
    
    @staticmethod
    def count_images_in_directory(album_dir: Path) -> int:
        """
        Count image files in a directory.
        
        Args:
            album_dir: Directory to count images in
            
        Returns:
            int: Number of image files found
        """
        if not album_dir.exists() or not album_dir.is_dir():
            return 0
            
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'}
        image_count = 0
        
        try:
            for file_path in album_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                    image_count += 1
        except Exception as e:
            logger.warning(f"Error counting images in {album_dir}", exception=e)
            return 0
            
        return image_count
    
    @staticmethod
    def get_image_file_list(album_dir: Path, extensions: Optional[List[str]] = None) -> List[Path]:
        """
        Get list of image files in a directory.
        
        Args:
            album_dir: Directory to search
            extensions: List of extensions to look for (default: common image formats)
            
        Returns:
            List[Path]: List of image file paths
        """
        if extensions is None:
            extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff']
            
        image_files = []
        
        if album_dir.exists() and album_dir.is_dir():
            try:
                for file_path in album_dir.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in extensions:
                        image_files.append(file_path)
            except Exception as e:
                logger.warning(f"Error listing images in {album_dir}", exception=e)
                
        return sorted(image_files)


class NavigationUtils:
    """
    Common navigation patterns for web scraping.
    Eliminates duplicate navigation logic.
    """
    
    @staticmethod
    def safe_navigate_with_retry(webdriver_manager, url: str, max_retries: int = 3, delay: float = 1.0) -> bool:
        """
        Navigate to URL with retry logic.
        
        Args:
            webdriver_manager: WebDriverManager instance
            url: URL to navigate to
            max_retries: Maximum number of retry attempts
            delay: Delay between attempts
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                if webdriver_manager.navigate_to(url):
                    time.sleep(delay)
                    return True
                    
                if attempt < max_retries - 1:
                    logger.warning(f"Navigation attempt {attempt + 1} failed, retrying...")
                    time.sleep(delay * 2)  # Exponential backoff
                    
            except Exception as e:
                logger.warning(f"Navigation attempt {attempt + 1} failed with exception: {e}")
                if attempt < max_retries - 1:
                    time.sleep(delay * 2)
                    
        logger.error(f"Failed to navigate to {url} after {max_retries} attempts")
        return False


# Convenience class that groups all utilities for easy import
class CommonUtils:
    """
    Convenience class that provides access to all common utilities.
    Can be imported as a single class to access all utilities.
    """
    
    click = ClickStrategies
    metadata_check = AlbumMetadataChecker
    name_processing = AlbumNameProcessor
    metadata_update = MetadataUpdater
    error_handling = ErrorHandlingUtils
    image_files = ImageFileUtils
    navigation = NavigationUtils