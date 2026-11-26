"""
Web interaction package for the Rebecca Richards Photography Album Scraper.
Contains WebDriver management and browser element interaction utilities.
"""

from .webdriver_manager import WebDriverManager
from .element_interactions import (
    ScrollManager, ElementInteractor, ClickableElementFinder, ElementInspector
)

__all__ = [
    'WebDriverManager',
    'ScrollManager', 
    'ElementInteractor', 
    'ClickableElementFinder', 
    'ElementInspector'
]