"""
Processing package for the Rebecca Richards Photography Album Scraper.
Contains main scraping logic, image processing, and album handling.
"""

from .album_scraper import AlbumScraper, AlbumPageProcessor, WindowManager
from .gallery_scraper import GalleryScraper
from .image_processor import ImageProcessor, ImageUrlProcessor, ImageDownloader, AlbumDirectoryManager
from .threaded_album_processor import ThreadedAlbumProcessor, ThreadSafeAlbumProcessor, AlbumTask
from .threaded_downloader import ThreadedImageDownloader

__all__ = [
    'AlbumScraper',
    'AlbumPageProcessor', 
    'WindowManager',
    'GalleryScraper',
    'ImageProcessor',
    'ImageUrlProcessor',
    'ImageDownloader',
    'AlbumDirectoryManager',
    'ThreadedAlbumProcessor',
    'ThreadSafeAlbumProcessor',
    'AlbumTask',
    'ThreadedImageDownloader'
]