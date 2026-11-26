"""
Core functionality package for the Rebecca Richards Photography Album Scraper.
Contains configuration, logging, and other foundational components.
"""

from .config import ScraperConfig
from .logger import logger

__all__ = ['ScraperConfig', 'logger']