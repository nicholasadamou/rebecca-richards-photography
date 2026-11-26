#!/usr/bin/env python3
"""
Rebecca Richards Photography Album Scraper

A web scraper to download images from Rebecca Richards Photography albums.

Usage:
    python3 scraper.py

Images will be saved to: ./scraped_images/[album-name]/
"""

import sys
from pathlib import Path

# Add src directory to path for imports
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from src.core.config import ScraperConfig
    from src.processing.album_scraper import AlbumScraper
    from src.core.logger import logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all source files are in the 'src' directory")
    sys.exit(1)


def create_config() -> ScraperConfig:
    """
    Create and configure the scraper configuration.

    Returns:
        ScraperConfig: Configured scraper settings
    """
    # You can customize these settings as needed
    config = ScraperConfig(
        output_dir=Path("scraped_images"),
        headless=True,  # Set to True for headless mode
        delay=3.0,
        # You can override other settings here if needed
    )

    return config


def main():
    """Main entry point for the enhanced scraper."""
    logger.header("🎨 Rebecca Richards Photography Album Scraper")

    # Create configuration
    config = create_config()

    # Display key configuration only
    logger.files(f"Output: {config.output_dir}")
    logger.network(f"URL: {config.client_albums_url}")

    # Create and run scraper using dependency injection
    try:
        with AlbumScraper(config) as scraper:
            success = scraper.scrape_all_albums()

            if success:
                stats = scraper.get_stats()
                logger.blank_line()
                logger.success("Scraping completed successfully!")
                logger.stats("Final Results:")
                logger.count("Albums processed", stats['albums_processed'])
                logger.count("Images downloaded", stats['total_downloaded'])
                logger.files(f"Check the '{config.output_dir}' folder for downloaded images.")
            else:
                logger.blank_line()
                logger.error("Scraping failed or completed with errors.")
                logger.info("Check the output above for details.")

    except KeyboardInterrupt:
        logger.blank_line()
        logger.blank_line()
        logger.warning("⏹️  Scraping interrupted by user")
        logger.info("Partial results may be available in the output directory")
    except Exception as e:
        logger.blank_line()
        logger.error("Unexpected error", exception=e)
        logger.info("Please check the error details above")


if __name__ == "__main__":
    main()
