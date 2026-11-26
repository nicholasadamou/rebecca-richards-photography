#!/usr/bin/env python3
"""
Configuration management for the Rebecca Richards Photography Album Scraper.
Centralizes all configuration settings following the Single Responsibility Principle.
"""

from pathlib import Path
from dataclasses import dataclass
from typing import List


@dataclass
class ScraperConfig:
    """Configuration settings for the album scraper."""

    # URLs
    base_url: str = "https://www.rebeccarichardsevents.com"

    # Directories
    output_dir: Path = Path("scraped_images")

    # Browser settings
    headless: bool = True
    window_size: str = "1920,1080"
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

    # Timing settings
    delay: float = 3.0
    page_load_timeout: int = 15
    scroll_delay: float = 1.5
    download_delay: float = 0.5

    # Retry settings
    max_click_attempts: int = 3
    max_scroll_attempts: int = 15
    max_stable_scroll_checks: int = 3

    # Image settings
    high_quality_width: int = 2000
    high_quality_height: int = 2000
    min_file_size_bytes: int = 1000

    # Threading settings
    enable_threading: bool = True  # Enable multi-threaded downloads
    max_download_threads: int = 4  # Number of concurrent download threads
    thread_timeout: float = 60.0   # Timeout for individual download threads
    threading_threshold: int = 4   # Minimum images needed to use threading

    # Album-level threading settings
    enable_album_threading: bool = False  # Enable multi-threaded album processing - This has issues currently (TODO)
    max_album_threads: int = 2  # Number of concurrent album processing threads
    album_thread_timeout: float = 300.0  # Timeout for individual album processing (5 minutes)

    # Selectors
    gallery_container_selectors: List[str] = None
    image_selectors: List[str] = None
    clickable_child_selectors: List[str] = None
    view_photos_selectors: List[str] = None
    metadata_selectors: List[str] = None
    title_selectors: List[str] = None
    date_selectors: List[str] = None

    def __post_init__(self):
        """Initialize default selectors after dataclass creation."""
        if self.gallery_container_selectors is None:
            self.gallery_container_selectors = [
                ".pro-gallery-margin-container",
                "#pro-gallery-margin-container",
                ".pro-gallery",
                ".gallery-container",
                "[data-hook='gallery']"
            ]

        if self.image_selectors is None:
            self.image_selectors = [
                "img[data-hook='gallery-item-image-img']",  # Wix gallery images
                ".gallery-item img",                         # Generic gallery images
                ".pro-gallery img",                          # Pro gallery images
                "img[src*='wixstatic.com']",                # Wix static images
                ".gallery img",                             # Fallback gallery images
            ]

        if self.clickable_child_selectors is None:
            self.clickable_child_selectors = [
                "a",                    # Direct links
                "button",               # Buttons
                "[role='button']",      # Elements with button role
                "[onclick]",            # Elements with onclick handlers
                "[data-hook*='action']", # Wix action elements
                ".item-link",           # Item links
                ".gallery-item-link",   # Gallery item links
                "img",                  # Sometimes images are clickable
            ]

        if self.view_photos_selectors is None:
            self.view_photos_selectors = [
                "a[href*='/set/']",                    # Direct link to gallery set
                "a:contains('View Photos')",           # Text-based search
                "a[href*='gallery']",                  # Gallery link
                ".gallery-link",                      # Class-based
                "a[data-hook*='view']",               # Wix data-hook
            ]

        if self.metadata_selectors is None:
            self.metadata_selectors = [
                ".info-element-text",                  # Primary metadata container
                "[class*='info-element-text']",       # Partial class match
                ".info-element",                       # Alternative info element
                "[data-hook='item-info']",            # Data-hook based
                "[class*='item-info']",               # Item info containers
                ".album-info",                         # Album info
                ".gallery-info",                      # Gallery info
                "[class*='info']",                    # Generic info containers
            ]

        if self.title_selectors is None:
            self.title_selectors = [
                ".info-element-title",                 # Primary title element
                "[data-hook='item-title']",           # Data-hook title
                ".info-member.info-element-title",    # Specific class combo
                "[class*='title']",                   # Any title class
                "h1, h2, h3, h4, h5, h6",             # Header elements
                ".album-title",                       # Album title
                ".gallery-title",                     # Gallery title
            ]

        if self.date_selectors is None:
            self.date_selectors = [
                ".info-element-description",          # Primary date container
                "[data-hook='item-description']",     # Data-hook description
                ".info-member.info-element-description",  # Specific class combo
                "[class*='description']",             # Any description class
                "[class*='date']",                    # Date-specific classes
                ".album-date",                        # Album date
                ".event-date",                        # Event date
            ]

        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)

    @property
    def client_albums_url(self) -> str:
        """Get the client albums URL."""
        return f"{self.base_url}/client-albums"

    def get_chrome_options(self) -> List[str]:
        """Get Chrome browser options."""
        options = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            f"--window-size={self.window_size}",
            f"--user-agent={self.user_agent}"
        ]

        if self.headless:
            options.append("--headless")

        return options
