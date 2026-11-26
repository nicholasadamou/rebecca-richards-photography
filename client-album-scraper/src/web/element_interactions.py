#!/usr/bin/env python3
"""
Element interaction classes for the Rebecca Richards Photography Album Scraper.
Handles clicking, scrolling, and element detection following SRP.
"""

import time
from typing import List, Tuple, Optional, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement

from ..core.config import ScraperConfig
from ..web.webdriver_manager import WebDriverManager
from ..core.logger import logger


class ElementInspector:
    """
    Inspects and analyzes web elements.
    Single responsibility: Element inspection and debugging.
    """
    
    @staticmethod
    def inspect_element_details(element: WebElement) -> Dict[str, Any]:
        """
        Inspect element details for debugging.
        
        Args:
            element: WebElement to inspect
            
        Returns:
            Dict containing element details
        """
        try:
            details = {
                'tag_name': element.tag_name,
                'class': element.get_attribute('class') or '',
                'id': element.get_attribute('id') or '',
                'onclick': element.get_attribute('onclick') or '',
                'href': element.get_attribute('href') or '',
                'data_hook': element.get_attribute('data-hook') or '',
                'role': element.get_attribute('role') or '',
                'is_displayed': element.is_displayed(),
                'is_enabled': element.is_enabled(),
                'size': element.size,
                'location': element.location
            }
            
            logger.info("Element details:")
            for key, value in details.items():
                if value:
                    logger.info(f"    {key}: {value}")
                    
            return details
        except Exception as e:
            logger.warning("Error inspecting element", exception=e)
            return {}


class ClickableElementFinder:
    """
    Finds clickable child elements within containers.
    Single responsibility: Finding clickable elements.
    """
    
    def __init__(self, config: ScraperConfig):
        """
        Initialize with configuration.
        
        Args:
            config: ScraperConfig instance
        """
        self.config = config
    
    def find_clickable_child(self, element: WebElement) -> WebElement:
        """
        Find the actual clickable child element within a container.
        
        Args:
            element: Container element to search within
            
        Returns:
            WebElement: Clickable child element or original element if none found
        """
        try:
            for selector in self.config.clickable_child_selectors:
                try:
                    clickable_child = element.find_element(By.CSS_SELECTOR, selector)
                    if clickable_child.is_displayed():
                        logger.info(f"Found clickable child: {selector}")
                        return clickable_child
                except:
                    continue
            
            # If no specific child found, return the original element
            return element
            
        except Exception as e:
            logger.warning("Error finding clickable child", exception=e)
            return element


class ScrollManager:
    """
    Handles all scrolling operations.
    Single responsibility: Page and element scrolling.
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
    
    def scroll_element_into_view(self, element: WebElement) -> None:
        """
        Scroll element into view.
        
        Args:
            element: Element to scroll into view
        """
        driver = self.webdriver_manager.get_driver()
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)
    
    def scroll_page_to_load_content(self) -> int:
        """
        Scroll down page to trigger lazy loading of all content.
        
        Returns:
            int: Number of scroll attempts made
        """
        driver = self.webdriver_manager.get_driver()
        logger.info("Scrolling down to load all content...")
        
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        for i in range(self.config.max_scroll_attempts):
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.config.scroll_delay)
            
            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # Try one more scroll to be sure
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    logger.success(f"All content loaded after {i+1} scrolls")
                    break
                    
            last_height = new_height
            logger.info(f"Scroll {i+1} complete, loading more content...")
        
        # Reset scroll position to top
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        return i + 1
    
    def scroll_gallery_to_load_images(self) -> int:
        """
        Scroll down gallery page to trigger lazy loading of all images.
        
        Returns:
            int: Final count of images loaded
        """
        driver = self.webdriver_manager.get_driver()
        previous_image_count = 0
        stable_count = 0
        
        for scroll_attempt in range(self.config.max_scroll_attempts):
            # Count current images
            try:
                current_images = driver.find_elements(
                    By.CSS_SELECTOR, 
                    "img[src*='wixstatic.com'], img[data-hook='gallery-item-image-img']"
                )
                current_count = len(current_images)
                
                logger.info(f"Scroll {scroll_attempt + 1}: Found {current_count} images")
                
                # Check if we found new images
                if current_count > previous_image_count:
                    stable_count = 0  # Reset stable count
                    previous_image_count = current_count
                else:
                    stable_count += 1
                
                # Stop if we've had several attempts with no new images
                if stable_count >= self.config.max_stable_scroll_checks:
                    logger.info(f"No new images found for {stable_count} consecutive scrolls, stopping")
                    break
                    
            except Exception as e:
                logger.warning(f"Error counting images on scroll {scroll_attempt + 1}", exception=e)
            
            # Scroll down to load more content
            try:
                # Scroll to bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for lazy loading
                
                # Also try scrolling the gallery container if it exists
                try:
                    gallery_containers = driver.find_elements(
                        By.CSS_SELECTOR, 
                        ".pro-gallery, .gallery-container, [data-hook*='gallery']"
                    )
                    if gallery_containers:
                        for container in gallery_containers:
                            driver.execute_script(
                                "arguments[0].scrollTop = arguments[0].scrollHeight;", 
                                container
                            )
                except:
                    pass  # Gallery container scrolling is optional
                    
                # Additional wait for images to load
                time.sleep(self.config.scroll_delay)
                
            except Exception as e:
                logger.warning(f"Error during scroll {scroll_attempt + 1}", exception=e)
                break
        
        # Final count
        try:
            final_images = driver.find_elements(
                By.CSS_SELECTOR, 
                "img[src*='wixstatic.com'], img[data-hook='gallery-item-image-img']"
            )
            final_count = len(final_images)
            logger.success(f"Finished scrolling. Total images loaded: {final_count}")
        except:
            final_count = 0
            logger.success("Finished scrolling gallery page")
        
        # Scroll back to top for a clean state
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        return final_count


class ElementInteractor:
    """
    Handles complex element interactions like clicking with retry logic.
    Single responsibility: Element interaction strategies.
    """
    
    def __init__(self, config: ScraperConfig, webdriver_manager: WebDriverManager, 
                 scroll_manager: ScrollManager, clickable_finder: ClickableElementFinder):
        """
        Initialize with dependencies.
        
        Args:
            config: ScraperConfig instance
            webdriver_manager: WebDriverManager instance
            scroll_manager: ScrollManager instance
            clickable_finder: ClickableElementFinder instance
        """
        self.config = config
        self.webdriver_manager = webdriver_manager
        self.scroll_manager = scroll_manager
        self.clickable_finder = clickable_finder
    
    def safe_click(self, element: WebElement, inspect_first: bool = False) -> bool:
        """
        Safely click an element with retry logic and enhanced debugging.
        
        Args:
            element: Element to click
            inspect_first: Whether to inspect element details first
            
        Returns:
            bool: True if click successful and navigation occurred, False otherwise
        """
        if inspect_first:
            logger.debug(f"Inspecting element: <{element.tag_name}> class='{element.get_attribute('class') or 'None'}'")
        
        driver = self.webdriver_manager.get_driver()
        
        # Store initial URL and window handles to detect navigation
        initial_url = driver.current_url
        initial_windows = driver.window_handles
        
        for attempt in range(self.config.max_click_attempts):
            # List of elements to try clicking, in order of preference
            elements_to_try = []
            
            try:
                # Scroll element into view
                self.scroll_manager.scroll_element_into_view(element)
                
                # Strategy 1: Try to find clickable children first
                clickable_child = self.clickable_finder.find_clickable_child(element)
                if clickable_child != element:
                    elements_to_try.append(("clickable_child", clickable_child))
                
                # Strategy 2: For gallery items, specifically look for the overlaying image
                try:
                    img_element = element.find_element(By.CSS_SELECTOR, "img[data-hook='gallery-item-image-img']")
                    if img_element.is_displayed():
                        elements_to_try.append(("gallery_image", img_element))
                        logger.debug("Found overlaying gallery image")
                except:
                    pass
                
                # Strategy 3: Try the original element
                elements_to_try.append(("original_element", element))
                
                # Try clicking each element in order
                for strategy_name, target_element in elements_to_try:
                    if self._try_click_element(target_element, strategy_name, attempt + 1, 
                                             initial_url, initial_windows):
                        return True
                        
            except Exception as e:
                logger.warning(f"Click attempt {attempt + 1} setup failed", exception=e)
                
            # If no strategy worked, try additional fallback approaches
            if attempt < self.config.max_click_attempts - 1:
                if self._try_fallback_methods(element, initial_url, initial_windows):
                    return True
                time.sleep(1)
        
        logger.error("All click methods failed for element")
        return False
    
    def _try_click_element(self, target_element: WebElement, strategy_name: str, 
                          attempt: int, initial_url: str, initial_windows: List[str]) -> bool:
        """Try clicking a specific element with navigation detection."""
        driver = self.webdriver_manager.get_driver()
        
        try:
            # Only show detailed attempts for debugging purposes
            if strategy_name == "clickable_child" or attempt > 1:
                logger.debug(f"Attempting {strategy_name} click on: {target_element.tag_name} (attempt {attempt})")
            target_element.click()
            
            # Wait a moment and check if navigation occurred (same tab or new tab)
            time.sleep(2)
            new_url = driver.current_url
            new_windows = driver.window_handles
            
            # Check if URL changed in current tab
            if new_url != initial_url:
                logger.success(f"Navigation successful with {strategy_name} (same tab): {initial_url} → {new_url}")
                return True
            
            # Check if a new tab/window was opened
            elif len(new_windows) > len(initial_windows):
                logger.success(f"New tab opened with {strategy_name}, switching to it")
                # Switch to the new tab
                new_window = [w for w in new_windows if w not in initial_windows][0]
                driver.switch_to.window(new_window)
                
                # Wait for the new page to load
                time.sleep(2)
                final_url = driver.current_url
                logger.success(f"Successfully switched to new tab: {final_url}")
                return True
            
            else:
                logger.warning(f"{strategy_name} click registered but no navigation detected")
                
        except Exception as click_error:
            # Only show detailed errors for specific strategies or repeated attempts
            if "element click intercepted" in str(click_error).lower():
                # Don't print the full stack trace for common interception errors
                logger.warning(f"{strategy_name} click intercepted, trying JavaScript fallback...")
            elif strategy_name == "clickable_child" or attempt > 1:
                logger.warning(f"{strategy_name} click failed: {type(click_error).__name__}")
            
            # If we get "element click intercepted", try JavaScript click
            if "element click intercepted" in str(click_error).lower():
                return self._try_javascript_click(target_element, strategy_name, 
                                                initial_url, initial_windows)
        
        return False
    
    def _try_javascript_click(self, target_element: WebElement, strategy_name: str,
                            initial_url: str, initial_windows: List[str]) -> bool:
        """Try JavaScript click as fallback for intercepted clicks."""
        driver = self.webdriver_manager.get_driver()
        
        # JavaScript click fallback is automatic, no need for verbose logging
        try:
            driver.execute_script("arguments[0].click();", target_element)
            time.sleep(2)
            
            # Check for navigation (same tab or new tab)
            js_new_url = driver.current_url
            js_new_windows = driver.window_handles
            
            if js_new_url != initial_url:
                logger.success(f"JavaScript click successful on {strategy_name} (same tab)")
                return True
            elif len(js_new_windows) > len(initial_windows):
                logger.success(f"JavaScript click opened new tab for {strategy_name}")
                # Switch to the new tab
                new_window = [w for w in js_new_windows if w not in initial_windows][0]
                driver.switch_to.window(new_window)
                time.sleep(2)
                logger.success(f"Successfully switched to new tab: {driver.current_url}")
                return True
        except Exception as js_error:
            logger.warning(f"JavaScript click on {strategy_name} failed", exception=js_error)
        
        return False
    
    def _try_fallback_methods(self, element: WebElement, initial_url: str, 
                            initial_windows: List[str]) -> bool:
        """Try additional fallback clicking methods."""
        driver = self.webdriver_manager.get_driver()
        logger.info("Trying additional fallback methods...")
        
        # Helper function to check for navigation
        def check_navigation_fallback():
            fallback_windows = driver.window_handles
            fallback_url = driver.current_url
            
            if fallback_url != initial_url:
                return True, "same_tab"
            elif len(fallback_windows) > len(initial_windows):
                new_window = [w for w in fallback_windows if w not in initial_windows][0]
                driver.switch_to.window(new_window)
                time.sleep(1)
                return True, "new_tab"
            return False, "none"
        
        # Try ActionChains move and click
        try:
            ActionChains(driver).move_to_element(element).click().perform()
            time.sleep(2)
            
            nav_success, nav_type = check_navigation_fallback()
            if nav_success:
                logger.success(f"ActionChains move and click successful ({nav_type})")
                return True
        except Exception as action_error:
            logger.warning("ActionChains move and click failed", exception=action_error)
        
        # Try JavaScript click directly on the element
        try:
            driver.execute_script("arguments[0].click();", element)
            time.sleep(2)
            
            nav_success, nav_type = check_navigation_fallback()
            if nav_success:
                logger.success(f"Direct JavaScript click successful ({nav_type})")
                return True
        except Exception as js_error:
            logger.warning("Direct JavaScript click failed", exception=js_error)
        
        # Try clicking with offset to avoid intercepted elements
        try:
            ActionChains(driver).move_to_element_with_offset(element, 5, 5).click().perform()
            time.sleep(2)
            
            nav_success, nav_type = check_navigation_fallback()
            if nav_success:
                logger.success(f"Offset click successful ({nav_type})")
                return True
        except Exception as offset_error:
            logger.warning("Offset click failed", exception=offset_error)
        
        return False
    
    def simple_click(self, element: WebElement) -> bool:
        """
        Simple click for straightforward navigation elements like links.
        
        Args:
            element: Element to click
            
        Returns:
            bool: True if click successful, False otherwise
        """
        try:
            logger.network("Clicking element...")
            element.click()
            return True
        except Exception as click_error:
            logger.error("Click failed", exception=click_error)
            
            # Fallback: try JavaScript click
            try:
                logger.info("Trying JavaScript click as fallback...")
                driver = self.webdriver_manager.get_driver()
                driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as js_error:
                logger.error("JavaScript click also failed", exception=js_error)
                return False