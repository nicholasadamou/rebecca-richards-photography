"""
Rebecca Richards Photography Album Scraper
Organized package structure for maintainability and clarity.
"""

# Core functionality
from .core import ScraperConfig, logger

# Web interactions
from .web import (
    WebDriverManager, ScrollManager, ElementInteractor, 
    ClickableElementFinder, ElementInspector
)

# Processing components
from .processing import (
    AlbumScraper, AlbumPageProcessor, WindowManager, GalleryScraper,
    ImageProcessor, ImageUrlProcessor, ImageDownloader, AlbumDirectoryManager,
    ThreadedAlbumProcessor, ThreadSafeAlbumProcessor, AlbumTask, ThreadedImageDownloader
)

# Metadata handling
from .metadata import (
    MetadataExtractor, MetadataManager, AlbumNameExtractor,
    AlbumNameStrategy, SubdomainExtractionStrategy, PathExtractionStrategy,
    PageContentExtractionStrategy
)

# Utilities
from .utils import (
    CommonUtils, ClickStrategies, AlbumMetadataChecker, AlbumNameProcessor,
    MetadataUpdater, ErrorHandlingUtils, ImageFileUtils, NavigationUtils
)

__all__ = [
    # Core
    'ScraperConfig', 'logger',
    
    # Web
    'WebDriverManager', 'ScrollManager', 'ElementInteractor',
    'ClickableElementFinder', 'ElementInspector',
    
    # Processing
    'AlbumScraper', 'AlbumPageProcessor', 'WindowManager', 'GalleryScraper',
    'ImageProcessor', 'ImageUrlProcessor', 'ImageDownloader', 'AlbumDirectoryManager',
    'ThreadedAlbumProcessor', 'ThreadSafeAlbumProcessor', 'AlbumTask', 'ThreadedImageDownloader',
    
    # Metadata
    'MetadataExtractor', 'MetadataManager', 'AlbumNameExtractor',
    'AlbumNameStrategy', 'SubdomainExtractionStrategy', 'PathExtractionStrategy',
    'PageContentExtractionStrategy',
    
    # Utils
    'CommonUtils', 'ClickStrategies', 'AlbumMetadataChecker', 'AlbumNameProcessor',
    'MetadataUpdater', 'ErrorHandlingUtils', 'ImageFileUtils', 'NavigationUtils'
]

#!/usr/bin/env python3
"""
Rebecca Richards Photography Album Scraper - Source Package
"""

__version__ = "2.0.0"
__author__ = "Nicholas Adamou"