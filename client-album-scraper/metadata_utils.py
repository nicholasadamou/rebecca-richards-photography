#!/usr/bin/env python3
"""
Metadata utilities for the Rebecca Richards Photography Album Scraper.
Provides commands to view, export, and manage album metadata.

Usage:
    python3 metadata_utils.py --help
    python3 metadata_utils.py --stats
    python3 metadata_utils.py --export-csv
    python3 metadata_utils.py --list-albums
    python3 metadata_utils.py --cleanup
    python3 metadata_utils.py --year 2020
"""

import sys
import argparse
from pathlib import Path

# Add src directory to path for imports
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from src.config import ScraperConfig
    from src.metadata_manager import MetadataManager
    from src.logger import logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all source files are in the 'src' directory")
    sys.exit(1)


def show_stats(metadata_manager: MetadataManager):
    """Display metadata statistics."""
    stats = metadata_manager.get_stats()
    successful_albums = metadata_manager.get_successfully_processed_albums()
    failed_albums = metadata_manager.get_failed_albums()
    
    logger.header("📊 METADATA STATISTICS", width=40)
    logger.count("Total Albums", stats['total_albums'])
    logger.count("Successfully Processed", len(successful_albums))
    logger.count("Failed Processing", len(failed_albums))
    logger.count("Albums with Names", stats['albums_with_names'])
    logger.count("Albums with Dates", stats['albums_with_dates'])
    
    if successful_albums:
        total_images = sum(album.get('images_downloaded', 0) for album in successful_albums)
        logger.count("Total Images Downloaded", total_images)
    
    if stats['date_range']['earliest']:
        logger.info(f"Date Range: {stats['date_range']['earliest']} - {stats['date_range']['latest']}")
    
    if stats['common_years']:
        logger.blank_line()
        logger.info("Albums by Year:")
        sorted_years = sorted(stats['common_years'].items())
        for year, count in sorted_years:
            logger.info(f"  {year}: {count} albums")


def list_albums(metadata_manager: MetadataManager, year: int = None):
    """List all albums or albums from a specific year."""
    if year:
        albums = metadata_manager.get_albums_by_date_range(year, year)
        title = f"📅 ALBUMS FROM {year}"
    else:
        albums = metadata_manager.get_all_albums()
        title = "📚 ALL ALBUMS"
    
    logger.header(title, width=50)
    
    if not albums:
        logger.info("No albums found.")
        return
    
    for i, album in enumerate(albums, 1):
        name = album.get('name', 'Unknown')
        date = album.get('date', 'No date')
        images = album.get('images_downloaded', 'Unknown')
        success = album.get('scraping_success', False)
        status = "✅" if success else "❌"
        
        logger.info(f"{i:2d}. {status} {name}")
        logger.info(f"    📅 {date}")
        logger.info(f"    📸 {images} images")
        if album.get('url'):
            logger.info(f"    🔗 {album['url']}")
        logger.blank_line()


def export_csv(metadata_manager: MetadataManager):
    """Export metadata to CSV."""
    try:
        csv_file = metadata_manager.export_metadata_csv()
        logger.success(f"Metadata exported to: {csv_file}")
    except Exception as e:
        logger.error("Export failed", exception=e)


def list_failed_albums(metadata_manager: MetadataManager):
    """List albums that failed processing."""
    failed_albums = metadata_manager.get_failed_albums()
    logger.header("❌ FAILED ALBUMS", width=50)
    
    if not failed_albums:
        logger.info("No failed albums found.")
        return
    
    for i, album in enumerate(failed_albums, 1):
        name = album.get('name', 'Unknown')
        error = album.get('error', 'No error message')
        url = album.get('url', 'No URL')
        
        logger.info(f"{i:2d}. ❌ {name}")
        logger.info(f"    ⚠️  {error}")
        logger.info(f"    🔗 {url}")
        logger.blank_line()


def cleanup_metadata(metadata_manager: MetadataManager):
    """Clean up metadata for missing albums."""
    cleaned = metadata_manager.cleanup_metadata()
    if cleaned > 0:
        logger.success(f"🧩 Cleaned up {cleaned} metadata entries")
    else:
        logger.success("No cleanup needed - all metadata entries have corresponding directories")


def search_albums(metadata_manager: MetadataManager, search_term: str):
    """Search albums by name or date."""
    all_albums = metadata_manager.get_all_albums()
    matches = []
    
    search_lower = search_term.lower()
    for album in all_albums:
        name = album.get('name', '').lower()
        date = album.get('date', '').lower()
        
        if search_lower in name or search_lower in date:
            matches.append(album)
    
    logger.header(f"🔍 SEARCH RESULTS FOR '{search_term}'", width=50)
    
    if not matches:
        logger.info("No albums found.")
        return
    
    for i, album in enumerate(matches, 1):
        name = album.get('name', 'Unknown')
        date = album.get('date', 'No date')
        success = album.get('scraping_success', False)
        status = "✅" if success else "❌"
        
        logger.info(f"{i}. {status} {name} - {date}")


def main():
    parser = argparse.ArgumentParser(
        description='Rebecca Richards Photography Metadata Utilities',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--stats', action='store_true',
                       help='Show metadata statistics')
    parser.add_argument('--list-albums', action='store_true',
                       help='List all albums')
    parser.add_argument('--failed', action='store_true',
                       help='List albums that failed processing')
    parser.add_argument('--export-csv', action='store_true',
                       help='Export metadata to CSV')
    parser.add_argument('--cleanup', action='store_true',
                       help='Clean up metadata for missing albums')
    parser.add_argument('--year', type=int,
                       help='Show albums from specific year')
    parser.add_argument('--search', type=str,
                       help='Search albums by name or date')
    parser.add_argument('--output-dir', type=str,
                       help='Override output directory (default: scraped_images)')
    
    args = parser.parse_args()
    
    # Create configuration
    config = ScraperConfig()
    if args.output_dir:
        config.output_dir = Path(args.output_dir)
    
    # Initialize metadata manager
    metadata_manager = MetadataManager(config)
    
    # Check if metadata file exists
    if not metadata_manager.metadata_file.exists():
        logger.warning(f"No metadata file found at {metadata_manager.metadata_file}")
        logger.info("Run the scraper first to generate metadata.")
        return
    
    # Execute commands
    if args.stats:
        show_stats(metadata_manager)
    elif args.list_albums:
        list_albums(metadata_manager)
    elif args.failed:
        list_failed_albums(metadata_manager)
    elif args.export_csv:
        export_csv(metadata_manager)
    elif args.cleanup:
        cleanup_metadata(metadata_manager)
    elif args.year:
        list_albums(metadata_manager, args.year)
    elif args.search:
        search_albums(metadata_manager, args.search)
    else:
        # Show help if no command specified
        parser.print_help()
        print("🚀" + "="*50)
        print("QUICK COMMANDS:")
        print("  --stats          Show metadata statistics")
        print("  --list-albums    List all albums")
        print("  --failed         List albums that failed processing")
        print("  --year 2020      Show albums from 2020")
        print("  --search 'sarah' Search for albums containing 'sarah'")
        print("  --export-csv     Export to CSV file")
        print("  --cleanup        Clean up old metadata")


if __name__ == "__main__":
    main()