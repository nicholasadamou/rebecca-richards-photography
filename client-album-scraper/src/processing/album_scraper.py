#!/usr/bin/env python3
"""
Main orchestrator class for the Rebecca Richards Photography Album Scraper.
Coordinates all other classes using dependency injection and follows SOLID principles.
"""

import time
from typing import Dict

from selenium.webdriver.common.by import By

from ..core.config import ScraperConfig
from ..core.logger import logger
from ..web.webdriver_manager import WebDriverManager
from ..web.element_interactions import (
    ScrollManager, ElementInteractor, ClickableElementFinder
)
from ..metadata.album_name_extractor import AlbumNameExtractor
from ..processing.image_processor import ImageProcessor
from ..processing.gallery_scraper import GalleryScraper
from ..processing.threaded_album_processor import ThreadedAlbumProcessor
from ..metadata.metadata_extractor import MetadataExtractor
from ..metadata.metadata_manager import MetadataManager
from ..utils.common_utils import CommonUtils


class AlbumPageProcessor:
    """
    Processes individual album pages.
    Single responsibility: Album page navigation and processing.
    """

    def __init__(self, config: ScraperConfig, webdriver_manager: WebDriverManager,
                 element_interactor: ElementInteractor, album_name_extractor: AlbumNameExtractor,
                 gallery_scraper: GalleryScraper, metadata_extractor: MetadataExtractor,
                 metadata_manager: MetadataManager):
        """
        Initialize with dependencies.

        Args:
            config: ScraperConfig instance
            webdriver_manager: WebDriverManager instance
            element_interactor: ElementInteractor instance
            album_name_extractor: AlbumNameExtractor instance
            gallery_scraper: GalleryScraper instance
            metadata_extractor: MetadataExtractor instance
            metadata_manager: MetadataManager instance
        """
        self.config = config
        self.webdriver_manager = webdriver_manager
        self.element_interactor = element_interactor
        self.album_name_extractor = album_name_extractor
        self.gallery_scraper = gallery_scraper
        self.metadata_extractor = metadata_extractor
        self.metadata_manager = metadata_manager

    def process_album_page(self, album_url: str, album_index: int) -> bool:
        """
        Process an individual album page to find and scrape the gallery.

        Args:
            album_url: URL of the album page to process
            album_index: Index of the album for fallback naming

        Returns:
            bool: True if processing successful, False otherwise
        """
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
                album_metadata['clean_name'] = CommonUtils.name_processing.clean_album_name(album_name)

            logger.files(f"Album name: {album_name}")
            if album_metadata.get('date'):
                logger.info(f"📅 Album date: {album_metadata['date']}")

            # Look for "View Photos" link
            view_photos_link = self.gallery_scraper.element_finder.find_view_photos_link()

            if view_photos_link:
                # Use common utility for clicking with fallback (reversed: direct click first in this case)
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


class WindowManager:
    """
    Manages window/tab operations.
    Single responsibility: Window and tab management.
    """

    def __init__(self, webdriver_manager: WebDriverManager):
        """
        Initialize with WebDriver manager.

        Args:
            webdriver_manager: WebDriverManager instance
        """
        self.webdriver_manager = webdriver_manager

    def return_to_albums_page(self, albums_url: str) -> None:
        """
        Return to the albums page, handling tabs appropriately.

        Args:
            albums_url: URL of the albums page to return to
        """
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


class AlbumScraper:
    """
    Main orchestrator class that coordinates all album scraping operations.
    Follows dependency injection principles and orchestrates the entire scraping process.
    """

    def __init__(self, config: ScraperConfig):
        """
        Initialize the album scraper with configuration.
        Uses dependency injection to set up all required services.

        Args:
            config: ScraperConfig instance with all settings
        """
        self.config = config

        # Initialize core services
        self.webdriver_manager = WebDriverManager(config)

        # Initialize interaction services
        self.scroll_manager = ScrollManager(config, self.webdriver_manager)
        self.clickable_finder = ClickableElementFinder(config)
        self.element_interactor = ElementInteractor(
            config, self.webdriver_manager, self.scroll_manager, self.clickable_finder
        )

        # Initialize business logic services
        self.album_name_extractor = AlbumNameExtractor(config)
        self.image_processor = ImageProcessor(config, self.webdriver_manager)

        # Initialize metadata services
        self.metadata_extractor = MetadataExtractor(config, self.webdriver_manager)
        self.metadata_manager = MetadataManager(config)

        # Initialize scraping services
        self.gallery_scraper = GalleryScraper(
            config, self.webdriver_manager, self.scroll_manager,
            self.image_processor, use_threading=config.enable_threading
        )

        # Initialize processing services
        self.album_processor = AlbumPageProcessor(
            config, self.webdriver_manager, self.element_interactor,
            self.album_name_extractor, self.gallery_scraper,
            self.metadata_extractor, self.metadata_manager
        )

        # Initialize utility services
        self.window_manager = WindowManager(self.webdriver_manager)

        # Initialize threaded album processor if enabled
        if self.config.enable_album_threading:
            self.threaded_album_processor = ThreadedAlbumProcessor(self.config)
        else:
            self.threaded_album_processor = None

    def scrape_all_albums(self) -> bool:
        """
        Main method to scrape all albums.

        Returns:
            bool: True if scraping completed successfully, False otherwise
        """
        logger.header("🚀 Starting Rebecca Richards Photography Album Scraper")
        logger.files(f"Images will be saved to: {self.config.output_dir.absolute()}")

        # Display existing metadata statistics
        if self.metadata_manager.metadata_file.exists():
            metadata_stats = self.metadata_manager.get_stats()
            successful_albums = len([a for a in self.metadata_manager.get_all_albums() if a.get('scraping_success')])
            logger.info(f"Found existing metadata: {metadata_stats['total_albums']} albums ({successful_albums} successful)")
        else:
            logger.info("No existing metadata found - starting fresh")

        if not self.webdriver_manager.start_driver():
            return False

        try:
            # Get all album elements
            album_elements = self.gallery_scraper.get_album_elements_from_page()

            if not album_elements:
                logger.error("No albums found to process")
                return False

            logger.blank_line()
            logger.progress(f"Processing {len(album_elements)} albums...")

            # Check if we should use threaded album processing
            if (self.config.enable_album_threading and
                self.threaded_album_processor and
                len(album_elements) >= 2):  # Use threading for 2+ albums

                logger.progress(f"Using threaded album processing with {self.config.max_album_threads} threads")

                # Close the main WebDriver since threads will create their own
                self.webdriver_manager.stop_driver()

                # Process albums using threading
                successful_albums, total_images_downloaded, results = self.threaded_album_processor.process_albums_batch(
                    album_elements, self.config.client_albums_url
                )

                logger.blank_line()
                logger.success(f"Threaded processing complete: {successful_albums}/{len(album_elements)} albums, {total_images_downloaded} images")

                # Log detailed results
                for result in results:
                    if result['success']:
                        logger.success(f"Album {result['album_index']}: {result['images_downloaded']} images")
                    else:
                        logger.error(f"Album {result['album_index']}: {result['error']}")

            else:
                # Use sequential processing
                logger.info("Using sequential album processing")

                # Process each album sequentially
                for i, album_element in enumerate(album_elements, 1):
                    try:
                        logger.blank_line()
                        logger.separator("=", 50)
                        logger.progress(f"Processing album {i}/{len(album_elements)}")

                        # Try to extract URL before processing to check metadata early
                        try:
                            # Get potential URL from the element
                            potential_url = None

                            # Try to find a link within the element
                            links = album_element.find_elements(By.TAG_NAME, "a")
                            if links:
                                potential_url = links[0].get_attribute('href')

                            # If we have a potential URL, check if it's already processed
                            if potential_url and self._should_skip_album(potential_url):
                                logger.info(f"Skipping album {i} based on metadata")
                                continue

                        except Exception as url_check_error:
                            # If we can't check the URL, proceed with normal processing
                            logger.warning("Could not pre-check album URL", exception=url_check_error)

                        # Use enhanced debugging for first few elements to understand the structure
                        inspect_element = i <= 3  # Inspect first 3 elements for debugging

                        if self.element_interactor.safe_click(album_element, inspect_first=inspect_element):
                            # Wait for navigation
                            time.sleep(self.config.delay)

                            # Process the album page we landed on
                            current_url = self.webdriver_manager.get_current_url()
                            self.album_processor.process_album_page(current_url, album_index=i)

                            # Return to albums page
                            self.window_manager.return_to_albums_page(self.config.client_albums_url)
                            time.sleep(self.config.delay)
                        else:
                            logger.warning(f"Failed to click album {i}")

                    except Exception as e:
                        logger.error(f"Error processing album {i}", exception=e)
                        continue

            # Log final summary
            stats = self.get_stats()
            metadata_stats = self.metadata_manager.get_stats()
            logger.blank_line()
            logger.separator("=", 50)
            logger.success("🎉 SCRAPING COMPLETED!")
            logger.stats("Final Statistics:")
            logger.count("Albums processed", stats['albums_processed'])
            logger.count("Total images downloaded", stats['total_downloaded'])
            logger.count("Albums with metadata", metadata_stats['total_albums'])
            logger.count("Albums with dates", metadata_stats['albums_with_dates'])
            logger.files(f"Images saved to: {self.config.output_dir.absolute()}")
            logger.metadata(f"Metadata saved to: {self.metadata_manager.metadata_file}")
            logger.separator("=", 50)

            return True

        except Exception as e:
            logger.error("Critical error during scraping", exception=e)
            return False

        finally:
            self.webdriver_manager.stop_driver()

    def get_stats(self) -> Dict[str, int]:
        """
        Get comprehensive scraping statistics.

        Returns:
            Dict containing all scraping statistics
        """
        if self.config.enable_album_threading and self.threaded_album_processor:
            # Get stats from threaded processor
            threaded_stats = self.threaded_album_processor.get_stats()
            # Combine with gallery scraper stats if available
            gallery_stats = self.gallery_scraper.get_stats()

            return {
                'albums_processed': threaded_stats.get('albums_processed', gallery_stats.get('albums_processed', 0)),
                'total_downloaded': threaded_stats.get('total_downloaded', gallery_stats.get('total_downloaded', 0))
            }
        else:
            return self.gallery_scraper.get_stats()

    def reset_stats(self) -> None:
        """Reset all scraping statistics."""
        self.gallery_scraper.reset_stats()
        if self.config.enable_album_threading and self.threaded_album_processor:
            self.threaded_album_processor.reset_stats()

    def _should_skip_album(self, album_url: str) -> bool:
        """
        Determine if an album should be skipped based on metadata.json using common utility.

        Args:
            album_url: URL of the album to check

        Returns:
            bool: True if album should be skipped (already successfully processed)
        """
        should_skip, _ = CommonUtils.metadata_check.should_skip_album(
            self.metadata_manager, album_url, self.config.output_dir
        )
        return should_skip

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.webdriver_manager.stop_driver()
