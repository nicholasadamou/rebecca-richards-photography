"""
Metadata package for the Rebecca Richards Photography Album Scraper.
Contains metadata extraction, management, and album name processing.
"""

from .metadata_extractor import MetadataExtractor
from .metadata_manager import MetadataManager
from .album_name_extractor import (
    AlbumNameExtractor, AlbumNameStrategy, SubdomainExtractionStrategy,
    PathExtractionStrategy, PageContentExtractionStrategy
)

__all__ = [
    'MetadataExtractor',
    'MetadataManager',
    'AlbumNameExtractor',
    'AlbumNameStrategy',
    'SubdomainExtractionStrategy',
    'PathExtractionStrategy',
    'PageContentExtractionStrategy'
]