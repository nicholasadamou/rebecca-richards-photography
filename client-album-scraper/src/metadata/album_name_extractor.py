#!/usr/bin/env python3
"""
Album name extraction service for the Rebecca Richards Photography Album Scraper.
Handles all album naming logic with different strategies following SRP.
"""

import re
from abc import ABC, abstractmethod
from typing import Optional, List
from urllib.parse import urlparse
from selenium.webdriver.common.by import By

from ..core.config import ScraperConfig
from ..web.webdriver_manager import WebDriverManager
from ..core.logger import logger


class AlbumNameStrategy(ABC):
    """Abstract base class for album name extraction strategies."""
    
    @abstractmethod
    def extract_name(self, url: str, webdriver_manager: Optional[WebDriverManager] = None) -> Optional[str]:
        """
        Extract album name using this strategy.
        
        Args:
            url: URL to extract name from
            webdriver_manager: Optional WebDriver manager for page-based extraction
            
        Returns:
            Optional[str]: Extracted album name or None if strategy fails
        """
        pass


class SubdomainExtractionStrategy(AlbumNameStrategy):
    """Extract album name from URL subdomain."""
    
    def extract_name(self, url: str, webdriver_manager: Optional[WebDriverManager] = None) -> Optional[str]:
        """
        Extract album name from subdomain like 'samantha-ben-engage.rebeccarichardsevents.com'.
        
        Args:
            url: URL to extract subdomain from
            webdriver_manager: Not used for this strategy
            
        Returns:
            Optional[str]: Extracted subdomain or None if not found
        """
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname or ''
            
            # Extract subdomain from hostname
            if "rebeccarichardsevents.com" in hostname:
                # Remove the main domain
                subdomain = hostname.replace(".rebeccarichardsevents.com", "")
                
                # If it starts with www., remove that part to get the actual subdomain
                if subdomain.startswith("www."):
                    subdomain = subdomain[4:]  # Remove "www."
                
                # Only return if we have a meaningful subdomain (not just empty or "www")
                if subdomain and subdomain != "www":
                    # Clean up the subdomain to be a valid folder name
                    album_name = re.sub(r'[<>:"/\\|?*]', '_', subdomain)
                    return album_name
                    
        except Exception as e:
            logger.warning(f"Error extracting subdomain from {url}", exception=e)
            
        return None


class PathExtractionStrategy(AlbumNameStrategy):
    """Extract album name from URL path segments."""
    
    def extract_name(self, url: str, webdriver_manager: Optional[WebDriverManager] = None) -> Optional[str]:
        """
        Extract album name from URL path like '/client-albums/album-name'.
        
        Args:
            url: URL to extract path from
            webdriver_manager: Not used for this strategy
            
        Returns:
            Optional[str]: Extracted album name from path or None if not found
        """
        try:
            parsed = urlparse(url)
            path = parsed.path or ""
            
            # If it's a path-based album (like /client-albums/album-name)
            if "/client-albums/" in path:
                path_parts = path.split("/")
                for i, part in enumerate(path_parts):
                    if part == "client-albums" and i + 1 < len(path_parts):
                        album_name = path_parts[i + 1]
                        # Clean up the album name
                        album_name = re.sub(r'[<>:"/\\|?*]', '_', album_name)
                        return album_name if album_name else None
            
            # Extract from path segments
            path_segments = [p for p in path.split("/") if p and p != "client-albums"]
            if path_segments:
                album_name = path_segments[-1]  # Use last segment
                album_name = re.sub(r'[<>:"/\\|?*]', '_', album_name)
                return album_name
                
        except Exception as e:
            logger.warning(f"Error extracting path from {url}", exception=e)
            
        return None


class PageContentExtractionStrategy(AlbumNameStrategy):
    """Extract album name from page content (titles, headings, etc.)."""
    
    def __init__(self, config: ScraperConfig):
        """
        Initialize with configuration.
        
        Args:
            config: ScraperConfig instance
        """
        self.config = config
    
    def extract_name(self, url: str, webdriver_manager: Optional[WebDriverManager] = None) -> Optional[str]:
        """
        Extract album name from page content.
        
        Args:
            url: URL (not used for this strategy, uses current page)
            webdriver_manager: WebDriver manager for accessing page content
            
        Returns:
            Optional[str]: Extracted album name from page content or None if not found
        """
        if not webdriver_manager:
            return None
            
        try:
            driver = webdriver_manager.get_driver()
            
            # Try multiple strategies to get album name from page
            name_selectors = [
                "h1",  # Main heading
                "h2",  # Secondary heading
                ".album-title",
                "[data-hook*='title']",
                ".gallery-title",
                "title",  # Page title
            ]
            
            for selector in name_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.get_attribute('textContent') or element.text
                        if text and text.strip() and len(text.strip()) > 3:
                            # Clean the text
                            clean_name = re.sub(r'[<>:"/\\|?*]', '_', text.strip())
                            clean_name = re.sub(r'\s+', '_', clean_name)
                            if clean_name and clean_name.lower() not in ['client_albums', 'rr_photography', 'rebecca_richards']:
                                return clean_name[:50]  # Limit length
                except:
                    continue
                    
        except Exception as e:
            logger.warning("Error extracting album name from page content", exception=e)
            
        return None


class AlbumNameExtractor:
    """
    Main album name extraction service that uses multiple strategies.
    Follows Strategy Pattern and Single Responsibility Principle.
    """
    
    def __init__(self, config: ScraperConfig):
        """
        Initialize with configuration and strategies.
        
        Args:
            config: ScraperConfig instance
        """
        self.config = config
        
        # Initialize strategies in order of preference
        self.strategies: List[AlbumNameStrategy] = [
            SubdomainExtractionStrategy(),
            PageContentExtractionStrategy(config),
            PathExtractionStrategy(),
        ]
    
    def extract_album_name(self, url: str, webdriver_manager: Optional[WebDriverManager] = None, 
                          album_index: Optional[int] = None) -> str:
        """
        Extract album name using multiple strategies.
        
        Args:
            url: URL to extract album name from
            webdriver_manager: Optional WebDriver manager for page-based extraction
            album_index: Optional album index for fallback naming
            
        Returns:
            str: Extracted album name or fallback name
        """
        # Try each strategy in order
        for strategy in self.strategies:
            try:
                album_name = strategy.extract_name(url, webdriver_manager)
                if album_name:
                    logger.files(f"Album name extracted using {strategy.__class__.__name__}: {album_name}")
                    return album_name
            except Exception as e:
                logger.warning(f"Strategy {strategy.__class__.__name__} failed", exception=e)
                continue
        
        # Fallback: use index-based naming
        if album_index is not None:
            fallback_name = f"album_{album_index:03d}"
            logger.files(f"Using fallback album name: {fallback_name}")
            return fallback_name
        
        # Ultimate fallback
        fallback_name = "unknown-album"
        logger.files(f"Using ultimate fallback album name: {fallback_name}")
        return fallback_name
    
    def add_strategy(self, strategy: AlbumNameStrategy) -> None:
        """
        Add a new extraction strategy.
        
        Args:
            strategy: AlbumNameStrategy instance to add
        """
        self.strategies.append(strategy)
    
    def clear_strategies(self) -> None:
        """Clear all strategies."""
        self.strategies.clear()