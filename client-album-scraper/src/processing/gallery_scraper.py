#!/usr/bin/env python3
"""
Gallery scraping service for the Rebecca Richards Photography Album Scraper.
Handles finding and collecting images from gallery pages following SRP.
"""

import time
from pathlib import Path
from typing import List, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from ..core.config import ScraperConfig
from ..web.webdriver_manager import WebDriverManager
from ..web.element_interactions import ScrollManager
from ..processing.image_processor import ImageProcessor
from ..processing.threaded_downloader import ThreadedImageDownloader
from ..core.logger import logger


class GalleryElementFinder:
    """
    Finds gallery elements and images on pages.
    Single responsibility: Element location and identification.
    """

    def __init__(self, config: ScraperConfig, webdriver_manager: WebDriverManager):
        """
        Initialize with configuration and WebDriver manager.

        Args:
            config: ScraperConfig instance
            webdriver_manager: WebDriverManager instance
        """
        self.config = config
        self.webdriver_manager = webdriver_manager

    def find_gallery_container(self) -> WebElement:
        """
        Find the correct gallery container with all album elements.

        Returns:
            WebElement: Gallery container element or None if not found
        """
        driver = self.webdriver_manager.get_driver()

        for selector in self.config.gallery_container_selectors:
            try:
                containers = self.webdriver_manager.wait_for_elements(By.CSS_SELECTOR, selector)
                if containers:
                    logger.success(f"Found container with selector: {selector}")

                    # Check if container has children
                    for container in containers:
                        child_count = driver.execute_script(
                            "return arguments[0].childElementCount;", container
                        )
                        logger.stats(f"Container has {child_count} children")

                        if child_count > 0:
                            return container
            except Exception as e:
                logger.warning(f"Error finding container with selector {selector}", exception=e)

        return None

    def find_album_elements(self, container: WebElement) -> List[WebElement]:
        """
        Find all album elements within a container.

        Args:
            container: Container element to search within

        Returns:
            List[WebElement]: List of album elements
        """
        driver = self.webdriver_manager.get_driver()

        # Get direct children of the gallery container
        logger.info("Getting direct children of gallery container...")
        album_elements = driver.execute_script(
            "return Array.from(arguments[0].children);", container
        )
        logger.stats(f"Found {len(album_elements)} direct children of gallery container")

        # If direct approach didn't work well, try CSS selectors
        if not album_elements or len(album_elements) < 10:  # We should have many more
            logger.warning("Direct children approach did not find enough elements, trying selectors...")

            # Find clickable album items within the gallery container
            gallery_id = container.get_attribute('id') or ''
            gallery_class = container.get_attribute('class') or ''

            # Build selector based on found container
            container_selector = f"#{gallery_id}" if gallery_id else f".{gallery_class.replace(' ', '.')}"

            clickable_selectors = [
                f"{container_selector} .gallery-item-container",    # Gallery item containers
                f"{container_selector} .item-action",              # Item actions within container
                f"{container_selector} [data-hook='item-action']", # Data-hook based
                f"{container_selector} .gallery-item",             # Generic gallery items
                f"{container_selector} > *",                       # Direct children
                ".pro-gallery-margin-container .gallery-item-container",  # Fallback to original selectors
                ".gallery-item-container"                          # Global search
            ]

            # Reset album_elements since we're trying a different approach
            album_elements = []
            for selector in clickable_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        album_elements.extend(elements)
                        logger.success(f"Found {len(elements)} elements with: {selector}")
                        break  # Use first successful selector
                except Exception as e:
                    logger.warning(f"Selector '{selector}' failed", exception=e)

        return self._filter_clickable_elements(album_elements)

    def _filter_clickable_elements(self, album_elements: List[WebElement]) -> List[WebElement]:
        """
        Filter album elements to only include clickable ones.

        Args:
            album_elements: List of potential album elements

        Returns:
            List[WebElement]: List of clickable elements
        """
        # Remove duplicates and filter clickable elements
        unique_elements = []
        seen_elements = set()

        for element in album_elements:
            try:
                # Get element ID or create unique identifier
                element_id = element.get_attribute('id') or element.get_attribute('data-id')
                if not element_id:
                    # Use location as unique identifier
                    location = element.location
                    element_id = f"{location['x']}_{location['y']}"

                if element_id not in seen_elements:
                    seen_elements.add(element_id)
                    unique_elements.append(element)
            except:
                # If we can't get a unique ID, still add it
                unique_elements.append(element)

        logger.stats(f"Found {len(unique_elements)} unique album elements to process")

        # Verify elements are clickable
        clickable_elements = []
        for i, element in enumerate(unique_elements):
            try:
                # Check if element is displayed
                if element.is_displayed():
                    clickable_elements.append(element)
            except Exception as e:
                logger.warning(f"Error checking element {i+1}", exception=e)

        logger.success(f"Found {len(clickable_elements)} visible elements that should be clickable")
        return clickable_elements

    def find_gallery_images(self) -> List[WebElement]:
        """
        Find all gallery images on the current page.

        Returns:
            List[WebElement]: List of image elements
        """
        driver = self.webdriver_manager.get_driver()

        all_images = []
        for selector in self.config.image_selectors:
            try:
                images = driver.find_elements(By.CSS_SELECTOR, selector)
                if images:
                    all_images.extend(images)
                    logger.success(f"Found {len(images)} images with selector: {selector}")
                    break  # Use first successful selector to avoid duplicates
            except Exception as e:
                logger.warning(f"Selector '{selector}' failed", exception=e)

        return all_images

    def find_view_photos_link(self) -> WebElement:
        """
        Find the "View Photos" link on an album page.

        Returns:
            WebElement: View Photos link element or None if not found
        """
        driver = self.webdriver_manager.get_driver()

        for selector in self.config.view_photos_selectors:
            try:
                if ":contains" in selector:
                    # Use XPath for text-based search
                    xpath = f"//a[contains(text(), 'View Photos')]"
                    links = driver.find_elements(By.XPATH, xpath)
                else:
                    links = driver.find_elements(By.CSS_SELECTOR, selector)

                if links:
                    logger.success(f"Found 'View Photos' link with selector: {selector}")
                    return links[0]
            except Exception as e:
                continue

        logger.error("Could not find 'View Photos' link")
        # Try to find any link that might lead to gallery
        all_links = driver.find_elements(By.TAG_NAME, "a")
        for link in all_links:
            href = link.get_attribute('href')
            text = link.get_attribute('textContent') or ""
            if href and ('/set/' in href or 'gallery' in href.lower() or 'view' in text.lower()):
                logger.success(f"Found potential gallery link: {href}")
                return link

        return None


class GalleryScraper:
    """
    Main gallery scraper that coordinates gallery operations.
    Orchestrates element finding, scrolling, and image collection.
    """
    def __init__(self, config: ScraperConfig, webdriver_manager: WebDriverManager,
                 scroll_manager: ScrollManager, image_processor: ImageProcessor,
                 use_threading: bool = True):
        """
        Initialize with configuration and dependencies.

        Args:
            config: ScraperConfig instance
            webdriver_manager: WebDriverManager instance
            scroll_manager: ScrollManager instance
            image_processor: ImageProcessor instance
            use_threading: Whether to use multi-threaded downloads
        """
        self.config = config
        self.webdriver_manager = webdriver_manager
        self.scroll_manager = scroll_manager
        self.image_processor = image_processor
        self.use_threading = use_threading

        # Initialize components
        self.element_finder = GalleryElementFinder(config, webdriver_manager)

        # Initialize threaded downloader if enabled
        if use_threading:
            self.threaded_downloader = ThreadedImageDownloader(config, webdriver_manager)

        # Stats
        self.albums_processed = 0

    def get_album_elements_from_page(self) -> List[WebElement]:
        """
        Get all album elements from the client albums page.

        Returns:
            List[WebElement]: List of album elements
        """
        logger.network(f"Loading client albums page: {self.config.client_albums_url}")

        try:
            # Navigate to client albums page
            if not self.webdriver_manager.navigate_to(self.config.client_albums_url):
                return []

            time.sleep(self.config.delay * 2)  # Wait for page to load

            # Scroll down to ensure all content is loaded
            self.scroll_manager.scroll_page_to_load_content()

            # Find the gallery container
            gallery_container = self.element_finder.find_gallery_container()

            if not gallery_container:
                logger.error("Could not find gallery container with albums")
                return []

            # Get child count after scrolling
            driver = self.webdriver_manager.get_driver()
            child_count = driver.execute_script(
                "return arguments[0].childElementCount;", gallery_container
            )
            logger.stats(f"Gallery container now has {child_count} child elements")

            # Find album elements
            return self.element_finder.find_album_elements(gallery_container)

        except Exception as e:
            logger.error("Error loading client albums page", exception=e)
            return []

    def scrape_gallery_page(self, album_name: str) -> int:
        """
        Scrape all images from the current gallery page.

        Args:
            album_name: Name of the album for organization

        Returns:
            int: Number of images downloaded
        """
        logger.progress(f"Scraping gallery for album: {album_name}")

        # Skip if album already processed
        if self.image_processor.is_album_processed(album_name):
            existing_count = self.image_processor.count_existing_images(album_name)
            logger.warning(f"Album '{album_name}' already processed ({existing_count} images), skipping...")
            return existing_count

        # Create album directory
        album_dir = self.image_processor.directory_manager.create_album_directory(album_name)

        # Wait for initial images to load
        time.sleep(self.config.delay)

        # Scroll down to trigger lazy loading and load all images
        logger.info("Scrolling gallery page to load all images via lazy loading...")
        self.scroll_manager.scroll_gallery_to_load_images()

        # Find all gallery images
        all_images = self.element_finder.find_gallery_images()

        # Remove duplicates based on src attribute
        unique_images = {}
        for img in all_images:
            try:
                src = img.get_attribute('src')
                if src and src not in unique_images:
                    unique_images[src] = img
            except Exception:
                continue

        logger.stats(f"Found {len(unique_images)} unique images to download")

        if not unique_images:
            logger.error("No images found on gallery page")
            return 0

        if self.use_threading and len(unique_images) > 3:  # Use threading for 4+ images
            try:
                downloaded_count, results = self.threaded_downloader.download_images_batch(
                    unique_images, album_dir, album_name
                )
            except Exception as e:
                logger.warning("Threaded download failed", exception=e)
                logger.info("Falling back to sequential download...")
                downloaded_count = self._download_images_sequential(unique_images, album_dir, album_name)
        else:
            # Use sequential download for small batches or when threading is disabled
            downloaded_count = self._download_images_sequential(unique_images, album_dir, album_name)

        logger.success(f"Downloaded {downloaded_count} images for album: {album_name}")
        return downloaded_count

    def _download_images_sequential(self, unique_images: Dict[str, Any], album_dir: Path, album_name: str) -> int:
        """
        Download images sequentially (fallback method).

        Args:
            unique_images: Dict of {src: img_element} for images to download
            album_dir: Directory to save images to
            album_name: Name of the album for logging

        Returns:
            int: Number of successful downloads
        """
        logger.progress(f"Sequential download starting for album: {album_name}")
        downloaded_count = 0
        for i, (src, img_element) in enumerate(unique_images.items(), 1):
            result = self.image_processor.process_and_download_image(src, album_dir, i)

            if result['success'] and not result['skipped']:
                downloaded_count += 1

        logger.success(f"Sequential download completed for album: {album_name} ({downloaded_count} images)")
        return downloaded_count

    def get_stats(self) -> Dict[str, int]:
        """
        Get scraping statistics.

        Returns:
            Dict containing scraping stats
        """
        stats = {
            'albums_processed': self.albums_processed,
        }

        # Add stats from appropriate downloader
        if self.use_threading and hasattr(self, 'threaded_downloader'):
            stats.update(self.threaded_downloader.get_stats())
        else:
            stats.update(self.image_processor.get_download_stats())

        return stats

    def reset_stats(self) -> None:
        """Reset scraping statistics."""
        self.albums_processed = 0
        if self.use_threading and hasattr(self, 'threaded_downloader'):
            self.threaded_downloader.reset_stats()
        self.image_processor.reset_stats()
