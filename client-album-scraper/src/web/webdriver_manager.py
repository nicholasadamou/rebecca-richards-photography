#!/usr/bin/env python3
"""
WebDriver management for the Rebecca Richards Photography Album Scraper.
Handles all WebDriver setup, configuration, and lifecycle management.
"""

import sys
from typing import Optional, List

# Import logger first so we can use it in error handling
from ..core.config import ScraperConfig
from ..core.logger import logger

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
except ImportError:
    logger.error("Required packages not installed!")
    logger.info("Please install with: pip3 install selenium requests pillow")
    logger.info("\nAlso install ChromeDriver:")
    logger.info("brew install chromedriver  # macOS")
    logger.info("Or download from: https://chromedriver.chromium.org/")
    sys.exit(1)


class WebDriverManager:
    """
    Manages WebDriver lifecycle and configuration.
    Follows Single Responsibility Principle - only handles WebDriver management.
    """
    
    def __init__(self, config: ScraperConfig):
        """
        Initialize WebDriver manager with configuration.
        
        Args:
            config: ScraperConfig instance with browser settings
        """
        self.config = config
        self.driver: Optional[webdriver.Chrome] = None
        self._chrome_options = None
    
    def _setup_chrome_options(self) -> Options:
        """Setup Chrome options based on configuration."""
        if self._chrome_options is None:
            self._chrome_options = Options()
            
            # Add all configured options
            for option in self.config.get_chrome_options():
                self._chrome_options.add_argument(option)
        
        return self._chrome_options
    
    def start_driver(self) -> bool:
        """
        Start the Chrome WebDriver.
        
        Returns:
            bool: True if driver started successfully, False otherwise
        """
        if self.driver is not None:
            logger.warning("WebDriver already running")
            return True
            
        try:
            options = self._setup_chrome_options()
            self.driver = webdriver.Chrome(options=options)
            self.driver.implicitly_wait(self.config.page_load_timeout)
            logger.success("Chrome WebDriver started successfully")
            return True
        except WebDriverException as e:
            logger.error("Failed to start Chrome WebDriver", exception=e)
            logger.info("Make sure ChromeDriver is installed and in PATH")
            logger.info("Install with: brew install chromedriver")
            return False
    
    def stop_driver(self) -> None:
        """Stop the WebDriver and clean up resources."""
        if self.driver:
            try:
                self.driver.quit()
                logger.success("WebDriver stopped")
            except Exception as e:
                logger.warning("Error stopping WebDriver", exception=e)
            finally:
                self.driver = None
    
    def get_driver(self) -> webdriver.Chrome:
        """
        Get the WebDriver instance.
        
        Returns:
            webdriver.Chrome: The WebDriver instance
            
        Raises:
            RuntimeError: If driver is not started
        """
        if self.driver is None:
            raise RuntimeError("WebDriver not started. Call start_driver() first.")
        return self.driver
    
    def wait_for_elements(self, by: By, value: str, timeout: Optional[int] = None) -> List:
        """
        Wait for elements to be present and return them.
        
        Args:
            by: Selenium By locator type
            value: Selector value
            timeout: Optional timeout override
            
        Returns:
            List of elements found, empty list if timeout
        """
        if self.driver is None:
            raise RuntimeError("WebDriver not started. Call start_driver() first.")
            
        timeout = timeout or self.config.page_load_timeout
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            elements = wait.until(EC.presence_of_all_elements_located((by, value)))
            return elements
        except TimeoutException:
            logger.warning(f"Timeout waiting for elements: {value}")
            return []
    
    def navigate_to(self, url: str) -> bool:
        """
        Navigate to a URL.
        
        Args:
            url: URL to navigate to
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        if self.driver is None:
            raise RuntimeError("WebDriver not started. Call start_driver() first.")
            
        try:
            self.driver.get(url)
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to {url}", exception=e)
            return False
    
    def get_current_url(self) -> str:
        """Get current URL."""
        if self.driver is None:
            raise RuntimeError("WebDriver not started. Call start_driver() first.")
        return self.driver.current_url
    
    def get_window_handles(self) -> List[str]:
        """Get current window handles."""
        if self.driver is None:
            raise RuntimeError("WebDriver not started. Call start_driver() first.")
        return self.driver.window_handles
    
    def switch_to_window(self, window_handle: str) -> None:
        """Switch to a specific window."""
        if self.driver is None:
            raise RuntimeError("WebDriver not started. Call start_driver() first.")
        self.driver.switch_to.window(window_handle)
    
    def close_current_window(self) -> None:
        """Close current window."""
        if self.driver is None:
            raise RuntimeError("WebDriver not started. Call start_driver() first.")
        self.driver.close()
    
    def __enter__(self):
        """Context manager entry."""
        self.start_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_driver()