#!/usr/bin/env python3
"""
Metadata management service for the Rebecca Richards Photography Album Scraper.
Handles saving and loading of album metadata to/from JSON files.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..core.config import ScraperConfig
from ..core.logger import logger


class MetadataManager:
    """
    Manages album metadata persistence to JSON files.
    Single responsibility: Metadata file management and caching.
    """
    
    def __init__(self, config: ScraperConfig):
        """
        Initialize with configuration.
        
        Args:
            config: ScraperConfig instance
        """
        self.config = config
        self.metadata_file = config.output_dir / "metadata.json"
        self._metadata_cache = None
        self._last_loaded = 0
        self.cache_ttl = 30  # Cache for 30 seconds
    
    def load_metadata(self) -> Dict[str, Any]:
        """
        Load metadata from the JSON file.
        
        Returns:
            Dict containing all album metadata
        """
        # Use cache if it's recent
        current_time = time.time()
        if (self._metadata_cache is not None and 
            current_time - self._last_loaded < self.cache_ttl):
            return self._metadata_cache
        
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Handle both old format (direct dict) and new format (nested with albums key)
                    if 'albums' in data:
                        self._metadata_cache = data['albums']
                    else:
                        self._metadata_cache = data
                    self._last_loaded = current_time
                    logger.metadata(f"Loaded metadata for {len(self._metadata_cache)} albums from {self.metadata_file}")
                    return self._metadata_cache
            else:
                logger.info("No existing metadata file found, starting fresh")
                self._metadata_cache = {}
                self._last_loaded = current_time
                return self._metadata_cache
                
        except (json.JSONDecodeError, IOError) as e:
            logger.warning("Error loading metadata file", exception=e)
            logger.info("Starting with empty metadata")
            self._metadata_cache = {}
            self._last_loaded = current_time
            return self._metadata_cache
    
    def save_metadata(self, metadata: Dict[str, Any]) -> bool:
        """
        Save metadata to the JSON file.
        
        Args:
            metadata: Complete metadata dict to save
            
        Returns:
            bool: True if saved successfully
        """
        try:
            # Ensure output directory exists
            self.config.output_dir.mkdir(exist_ok=True, parents=True)
            
            # Add timestamp
            save_data = {
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_albums": len(metadata),
                "albums": metadata
            }
            
            # Write with pretty formatting
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            # Update cache
            self._metadata_cache = metadata
            self._last_loaded = time.time()
            
            logger.metadata(f"Saved metadata for {len(metadata)} albums to {self.metadata_file}")
            return True
            
        except (IOError, json.JSONEncodeError) as e:
            logger.error("Error saving metadata", exception=e)
            return False
    
    def add_album_metadata(self, album_metadata: Dict[str, Any]) -> bool:
        """
        Add or update metadata for a single album.
        
        Args:
            album_metadata: Metadata for one album
            
        Returns:
            bool: True if added successfully
        """
        if not album_metadata.get('url'):
            logger.warning("Cannot add album metadata without URL")
            return False
        
        # Load existing metadata
        all_metadata = self.load_metadata()
        
        # Use URL as the key for consistency
        album_key = album_metadata['url']
        
        # Add album name as secondary key if available
        if album_metadata.get('name'):
            # Also store by clean album name for easy lookup
            clean_name = self._clean_album_name(album_metadata['name'])
            album_metadata['clean_name'] = clean_name
        
        # Add timestamp
        album_metadata['added_at'] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Store the metadata
        all_metadata[album_key] = album_metadata
        
        # Save back to file
        return self.save_metadata(all_metadata)
    
    def get_album_metadata(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific album by URL or name.
        
        Args:
            identifier: Album URL or name to look up
            
        Returns:
            Album metadata dict or None if not found
        """
        all_metadata = self.load_metadata()
        
        # Try direct URL lookup first
        if identifier in all_metadata:
            return all_metadata[identifier]
        
        # Try to find by clean name
        clean_identifier = self._clean_album_name(identifier)
        for album_data in all_metadata.values():
            if (album_data.get('clean_name') == clean_identifier or 
                self._clean_album_name(album_data.get('name', '')) == clean_identifier):
                return album_data
        
        return None
    
    def album_exists_in_metadata(self, identifier: str) -> bool:
        """
        Check if an album exists in the metadata.
        
        Args:
            identifier: Album URL or name to check
            
        Returns:
            bool: True if album exists in metadata
        """
        return self.get_album_metadata(identifier) is not None
    
    def get_all_albums(self) -> List[Dict[str, Any]]:
        """
        Get all album metadata as a list.
        
        Returns:
            List of all album metadata dicts
        """
        all_metadata = self.load_metadata()
        return list(all_metadata.values())
    
    def get_successfully_processed_albums(self) -> List[Dict[str, Any]]:
        """
        Get only albums that were successfully processed.
        
        Returns:
            List of successfully processed album metadata dicts
        """
        all_albums = self.get_all_albums()
        return [album for album in all_albums if album.get('scraping_success') and album.get('images_downloaded', 0) > 0]
    
    def get_failed_albums(self) -> List[Dict[str, Any]]:
        """
        Get only albums that failed processing.
        
        Returns:
            List of failed album metadata dicts
        """
        all_albums = self.get_all_albums()
        return [album for album in all_albums if album.get('scraping_success') is False]
    
    def get_albums_by_date_range(self, start_year: Optional[int] = None, 
                                end_year: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get albums within a specific date range.
        
        Args:
            start_year: Minimum year (inclusive)
            end_year: Maximum year (inclusive)
            
        Returns:
            List of album metadata dicts within the date range
        """
        all_albums = self.get_all_albums()
        filtered = []
        
        for album in all_albums:
            album_date = album.get('date', '')
            if not album_date:
                continue
            
            try:
                # Extract year from date string
                import re
                year_match = re.search(r'\b(19|20)\d{2}\b', album_date)
                if year_match:
                    album_year = int(year_match.group())
                    
                    # Check range
                    if start_year and album_year < start_year:
                        continue
                    if end_year and album_year > end_year:
                        continue
                    
                    filtered.append(album)
                    
            except (ValueError, AttributeError):
                # Skip albums with unparseable dates
                continue
        
        return filtered
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the metadata collection.
        
        Returns:
            Dict with metadata statistics
        """
        all_albums = self.get_all_albums()
        
        stats = {
            'total_albums': len(all_albums),
            'albums_with_dates': 0,
            'albums_with_names': 0,
            'date_range': {'earliest': None, 'latest': None},
            'common_years': {}
        }
        
        import re
        for album in all_albums:
            if album.get('date'):
                stats['albums_with_dates'] += 1
                
                # Extract year for statistics
                year_match = re.search(r'\b(19|20)\d{2}\b', album['date'])
                if year_match:
                    year = int(year_match.group())
                    stats['common_years'][year] = stats['common_years'].get(year, 0) + 1
                    
                    if not stats['date_range']['earliest'] or year < stats['date_range']['earliest']:
                        stats['date_range']['earliest'] = year
                    if not stats['date_range']['latest'] or year > stats['date_range']['latest']:
                        stats['date_range']['latest'] = year
            
            if album.get('name'):
                stats['albums_with_names'] += 1
        
        return stats
    
    def cleanup_metadata(self) -> int:
        """
        Clean up metadata by removing entries for albums that no longer have directories.
        
        Returns:
            int: Number of entries cleaned up
        """
        all_metadata = self.load_metadata()
        cleaned_metadata = {}
        cleaned_count = 0
        
        for url, album_data in all_metadata.items():
            clean_name = album_data.get('clean_name')
            if clean_name:
                album_dir = self.config.output_dir / clean_name
                if album_dir.exists() and album_dir.is_dir():
                    cleaned_metadata[url] = album_data
                else:
                    logger.info(f"Removing metadata for missing album: {clean_name}")
                    cleaned_count += 1
            else:
                # Keep entries without clean names for now
                cleaned_metadata[url] = album_data
        
        if cleaned_count > 0:
            self.save_metadata(cleaned_metadata)
            logger.success(f"Cleaned up {cleaned_count} metadata entries")
        
        return cleaned_count
    
    def _clean_album_name(self, name: str) -> str:
        """
        Clean album name to match directory naming conventions.
        
        Args:
            name: Raw album name
            
        Returns:
            Cleaned album name suitable for directories
        """
        if not name:
            return ""
        
        import re
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
    
    def export_metadata_csv(self, output_file: Optional[Path] = None) -> Path:
        """
        Export metadata to CSV format for external analysis.
        
        Args:
            output_file: Optional custom output file path
            
        Returns:
            Path to the created CSV file
        """
        import csv
        
        if not output_file:
            output_file = self.config.output_dir / "albums_metadata.csv"
        
        all_albums = self.get_all_albums()
        
        # Define CSV headers
        headers = ['name', 'date', 'url', 'clean_name', 'description', 'added_at', 'extraction_success']
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers, extrasaction='ignore')
                writer.writeheader()
                
                for album in all_albums:
                    writer.writerow(album)
            
            logger.success(f"Exported {len(all_albums)} albums to CSV: {output_file}")
            return output_file
            
        except IOError as e:
            logger.error("Error exporting to CSV", exception=e)
            raise