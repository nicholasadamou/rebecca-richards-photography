#!/usr/bin/env python3
"""
Metadata extraction service for the Rebecca Richards Photography Album Scraper.
Extracts album names, dates, and other metadata from gallery pages.
"""

import re
from typing import Dict, Optional, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from ..core.config import ScraperConfig
from ..web.webdriver_manager import WebDriverManager
from ..core.logger import logger


class MetadataExtractor:
    """
    Extracts metadata (name, date, etc.) from album pages.
    Single responsibility: Metadata extraction and parsing.
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
    
    def extract_album_metadata(self, album_url: str) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from an album page.
        
        Args:
            album_url: URL of the album page
            
        Returns:
            Dict containing extracted metadata
        """
        metadata = {
            'url': album_url,
            'name': None,
            'date': None,
            'description': None,
            'title': None,
            'extraction_success': False
        }
        
        try:
            driver = self.webdriver_manager.get_driver()
            
            # Look for the metadata container
            metadata_element = self._find_metadata_element()
            
            if metadata_element:
                # Extract name/title
                title_element = self._find_title_element(metadata_element)
                if title_element:
                    metadata['name'] = self._clean_text(title_element.text)
                    metadata['title'] = metadata['name']
                
                # Extract date
                date_element = self._find_date_element(metadata_element)
                if date_element:
                    metadata['date'] = self._parse_date(date_element.text)
                
                # Extract description if available
                desc_element = self._find_description_element(metadata_element)
                if desc_element:
                    metadata['description'] = self._clean_text(desc_element.text)
                
                # Generate clean name for filesystem
                if metadata['name']:
                    metadata['clean_name'] = self._clean_album_name(metadata['name'])
                
                metadata['extraction_success'] = True
                logger.success(f"Extracted metadata: {metadata['name']} ({metadata['date']})")
            
            else:
                logger.warning("Could not find metadata container, trying alternative methods...")
                # Try alternative extraction methods
                alt_metadata = self._extract_alternative_metadata()
                if alt_metadata:
                    metadata.update(alt_metadata)
                    metadata['extraction_success'] = True
        
        except Exception as e:
            logger.error("Error extracting metadata", exception=e)
            metadata['error'] = str(e)
        
        return metadata
    
    def _find_metadata_element(self) -> Optional[WebElement]:
        """
        Find the main metadata container element.
        
        Returns:
            WebElement: Metadata container or None
        """
        driver = self.webdriver_manager.get_driver()
        
        # Primary selectors based on the provided HTML structure
        metadata_selectors = [
            # Primary selector for the info element
            '.info-element-text',
            '[class*="info-element-text"]',
            
            # Alternative selectors
            '.info-element',
            '[data-hook="item-info"]',
            '[class*="item-info"]',
            '.album-info',
            '.gallery-info',
            
            # Generic info containers
            '[class*="info"]',
            '.text-info',
            '.content-info'
        ]
        
        for selector in metadata_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    # Check if this element contains both title and date-like content
                    element_text = element.text.strip()
                    if element_text and (
                        ('&' in element_text and len(element_text.split()) >= 2) or  # Name format like "Sarah & John"
                        any(month in element_text for month in ['January', 'February', 'March', 'April', 'May', 'June',
                                                              'July', 'August', 'September', 'October', 'November', 'December']) or
                        re.search(r'\b\d{1,2},?\s+\d{4}\b', element_text)  # Date pattern
                    ):
                        logger.success(f"Found metadata element with selector: {selector}")
                        return element
                        
            except Exception as e:
                continue
        
        return None
    
    def _find_title_element(self, metadata_element: WebElement) -> Optional[WebElement]:
        """
        Find the title/name element within the metadata container.
        
        Args:
            metadata_element: Parent metadata container
            
        Returns:
            WebElement: Title element or None
        """
        title_selectors = [
            '.info-element-title',
            '[data-hook="item-title"]',
            '.info-member.info-element-title',
            '[class*="title"]',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            '.album-title',
            '.gallery-title'
        ]
        
        for selector in title_selectors:
            try:
                title_elements = metadata_element.find_elements(By.CSS_SELECTOR, selector)
                if title_elements:
                    # Return the first one that has meaningful text
                    for elem in title_elements:
                        text = elem.text.strip()
                        if text and len(text) > 2:
                            return elem
            except Exception:
                continue
        
        return None
    
    def _find_date_element(self, metadata_element: WebElement) -> Optional[WebElement]:
        """
        Find the date element within the metadata container.
        
        Args:
            metadata_element: Parent metadata container
            
        Returns:
            WebElement: Date element or None
        """
        date_selectors = [
            '.info-element-description',
            '[data-hook="item-description"]',
            '.info-member.info-element-description',
            '[class*="description"]',
            '[class*="date"]',
            '.album-date',
            '.event-date'
        ]
        
        for selector in date_selectors:
            try:
                date_elements = metadata_element.find_elements(By.CSS_SELECTOR, selector)
                if date_elements:
                    for elem in date_elements:
                        text = elem.text.strip()
                        # Check if this looks like a date
                        if self._is_date_like(text):
                            return elem
            except Exception:
                continue
        
        return None
    
    def _find_description_element(self, metadata_element: WebElement) -> Optional[WebElement]:
        """
        Find additional description element.
        
        Args:
            metadata_element: Parent metadata container
            
        Returns:
            WebElement: Description element or None
        """
        desc_selectors = [
            '.description',
            '.album-description',
            '.event-description',
            'p'
        ]
        
        for selector in desc_selectors:
            try:
                desc_elements = metadata_element.find_elements(By.CSS_SELECTOR, selector)
                if desc_elements:
                    for elem in desc_elements:
                        text = elem.text.strip()
                        if text and not self._is_date_like(text) and len(text) > 10:
                            return elem
            except Exception:
                continue
        
        return None
    
    def _extract_alternative_metadata(self) -> Dict[str, Any]:
        """
        Try alternative methods to extract metadata when primary method fails.
        
        Returns:
            Dict with extracted metadata or empty dict
        """
        driver = self.webdriver_manager.get_driver()
        metadata = {}
        
        try:
            # Try to find any text that looks like album names and dates
            all_text_elements = driver.find_elements(By.XPATH, "//*[text()]")
            
            potential_titles = []
            potential_dates = []
            
            for element in all_text_elements:
                try:
                    text = element.text.strip()
                    if not text:
                        continue
                    
                    # Look for title patterns (names with &)
                    if '&' in text and len(text.split()) >= 2 and len(text.split()) <= 6:
                        potential_titles.append(text)
                    
                    # Look for date patterns
                    if self._is_date_like(text):
                        potential_dates.append(text)
                        
                except Exception:
                    continue
            
            # Select best candidates
            if potential_titles:
                metadata['name'] = self._clean_text(potential_titles[0])
                metadata['title'] = metadata['name']
            
            if potential_dates:
                metadata['date'] = self._parse_date(potential_dates[0])
            
            if potential_titles or potential_dates:
                logger.success(f"Alternative extraction found: {metadata.get('name', 'No name')} ({metadata.get('date', 'No date')})")
                return metadata
                
        except Exception as e:
            logger.warning("Alternative extraction failed", exception=e)
        
        return {}
    
    def _is_date_like(self, text: str) -> bool:
        """
        Check if text looks like a date.
        
        Args:
            text: Text to check
            
        Returns:
            bool: True if text appears to be a date
        """
        if not text or len(text) < 4:
            return False
        
        # Common date patterns
        date_patterns = [
            r'\b\w+\s+\d{1,2},?\s+\d{4}\b',  # "May 23, 2020" or "May 23 2020"
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # "5/23/2020" or "5-23-20"
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',  # "2020/5/23"
            r'\b\d{1,2}\s+\w+\s+\d{4}\b',  # "23 May 2020"
        ]
        
        # Check for month names
        months = ['january', 'february', 'march', 'april', 'may', 'june',
                 'july', 'august', 'september', 'october', 'november', 'december',
                 'jan', 'feb', 'mar', 'apr', 'may', 'jun',
                 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        
        text_lower = text.lower()
        has_month = any(month in text_lower for month in months)
        has_year = re.search(r'\b(19|20)\d{2}\b', text)
        
        if has_month and has_year:
            return True
        
        # Check for date patterns
        for pattern in date_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _parse_date(self, date_text: str) -> str:
        """
        Parse and normalize a date string.
        
        Args:
            date_text: Raw date text
            
        Returns:
            Cleaned and normalized date string
        """
        if not date_text:
            return ""
        
        # Clean up the text
        cleaned = re.sub(r'<[^>]+>', '', date_text)  # Remove HTML tags
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()  # Normalize whitespace
        
        # Try to extract just the date part if there's extra text
        date_patterns = [
            r'\b\w+\s+\d{1,2},?\s+\d{4}\b',  # "May 23, 2020"
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # "5/23/2020"
            r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',  # "2020/5/23"
            r'\b\d{1,2}\s+\w+\s+\d{4}\b',  # "23 May 2020"
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, cleaned, re.IGNORECASE)
            if match:
                return match.group().strip()
        
        return cleaned
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove HTML entities and tags
        cleaned = re.sub(r'&\w+;', ' ', text)  # Remove HTML entities like &amp;
        cleaned = re.sub(r'<[^>]+>', '', cleaned)  # Remove HTML tags
        
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def _clean_album_name(self, name: str) -> str:
        """
        Clean album name to be filesystem-safe.
        
        Args:
            name: Raw album name
            
        Returns:
            Cleaned album name suitable for directory names
        """
        if not name:
            return ""
        
        # Remove HTML entities and tags first
        cleaned = re.sub(r'&\w+;', ' ', name)  # Remove HTML entities like &amp;
        cleaned = re.sub(r'<[^>]+>', '', cleaned)  # Remove HTML tags
        
        # Remove special characters and normalize for filesystem
        cleaned = re.sub(r'[^\w\s-]', '', cleaned)  # Keep only word chars, spaces, hyphens
        cleaned = re.sub(r'\s+', '-', cleaned).strip('-')  # Replace spaces with hyphens
        cleaned = re.sub(r'-+', '-', cleaned)  # Replace multiple consecutive hyphens with single hyphen
        cleaned = cleaned.lower()  # Convert to lowercase
        
        # Ensure it's not empty and not too long
        if not cleaned:
            cleaned = "unknown-album"
        elif len(cleaned) > 100:  # Limit length for filesystem compatibility
            cleaned = cleaned[:100].rstrip('-')
        
        return cleaned
