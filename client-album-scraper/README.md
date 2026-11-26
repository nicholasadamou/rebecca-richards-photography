# Rebecca Richards Photography Album Scraper

This tool automatically scrapes all images from Rebecca Richards' client albums at https://www.rebeccarichardsevents.com/client-albums.

## 🚀 Quick Start

1. **Setup (one-time)**
   ```bash
   cd client-album-scraper
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Run the scraper**
   ```bash
   python3 scraper.py
   ```

3. **Find your images**
   ```
   scraped_images/
   ├── samantha-ben-engage/
   │   ├── image_001.jpg
   │   ├── image_002.jpg
   │   └── ...
   ├── another-album-name/
   │   └── ...
   ├── metadata.json              # 🆕 Album metadata & caching info
   └── albums_metadata.csv        # 🆕 Exportable spreadsheet data
   ```

4. **🆕 View metadata and statistics**
   ```bash
   # Show scraping statistics
   python3 metadata_utils.py --stats

   # List all albums with details
   python3 metadata_utils.py --list-albums

   # Show albums that failed
   python3 metadata_utils.py --failed
   ```

## 📋 What It Does

The scraper automates this process:

1. **Visits** the client albums page
2. **Checks** `metadata.json` to skip already processed albums 🆕
3. **Clicks** on each album thumbnail
4. **Extracts** album metadata (names, dates) from the page 🆕
5. **Finds** the "View Photos" link on each album page
6. **Navigates** to the gallery page (e.g., `/set/b1cd5f47-a630-44e4-b4d5-e3517701fda5`)
7. **Downloads** all high-quality images from each gallery
8. **Organizes** images into folders named after the album
9. **Saves** comprehensive metadata for future runs 🆕

## 🛠 Requirements

- **Python 3.7+**
- **Google Chrome browser**
- **ChromeDriver** (installed automatically via setup script)

### Python Packages
- `selenium` - Browser automation
- `requests` - HTTP requests for downloading images
- `pillow` - Image processing utilities

## ⚙️ Configuration

Edit these variables in `scraper.py`:

```python
# Configuration
output_directory = "scraped_images"    # Where to save images
headless_mode = True                   # Set False to see browser window
delay_seconds = 3                      # Delay between operations
```

## 🎯 Features

### Core Scraping
- **Automatic high-quality downloads** - Converts Wix image URLs to highest quality versions
- **Smart duplicate detection** - Avoids downloading the same image twice
- **Robust error handling** - Continues scraping even if individual albums fail
- **Organized output** - Creates folders named after album subdomains
- **Progress tracking** - Shows detailed progress and statistics

### 🆕 Metadata & Caching
- **Intelligent caching** - Automatically skips already processed albums using `metadata.json`
- **Album metadata extraction** - Extracts names ("Sarah & John Wedding") and dates ("June 15, 2019")
- **Success/failure tracking** - Records which albums processed successfully vs. failed
- **Resume capability** - Safely restart scraping without losing progress
- **Rich statistics** - Detailed breakdowns of albums, dates, and success rates
- **CSV export** - Export metadata to spreadsheet format
- **Failed album retry** - Automatically retries albums that previously failed

## 📊 Output Structure

```
scraped_images/
├── samantha-ben-engage/           # Album folder (cleaned name)
│   ├── ffc73c_8283ef35d26d.jpg   # High-quality images
│   ├── ffc73c_266263af3ed9.jpg
│   └── ...
├── another-couple-wedding/
│   └── ...
├── metadata.json                  # 🆕 Album metadata & caching info
└── albums_metadata.csv            # 🆕 Exportable CSV data
```

### 🆕 Metadata File Structure

The `metadata.json` contains rich information about each album:

```json
{
  "last_updated": "2025-09-20 02:15:30",
  "total_albums": 25,
  "albums": {
    "https://www.rebeccarichardsevents.com/album-123": {
      "name": "Sarah & Michael Wedding",
      "date": "June 15, 2019",
      "url": "https://www.rebeccarichardsevents.com/album-123",
      "clean_name": "sarah-michael-wedding",
      "images_downloaded": 42,
      "scraping_success": true,
      "added_at": "2025-09-20 02:15:30"
    }
  }
}
```

## 🐛 Troubleshooting

### ChromeDriver Issues
```bash
# Install/update ChromeDriver
brew install chromedriver
# Or download from: https://chromedriver.chromium.org/
```

### Python Dependencies
```bash
pip3 install -r requirements.txt
```

### Browser Issues
- Set `headless_mode = False` to see what's happening
- Increase `delay_seconds` if pages load slowly
- Check your internet connection

### No Images Found
- The website structure may have changed
- Try running with `headless_mode = False` to debug
- Check if the album pages actually have "View Photos" links

### 🆕 Metadata & Caching Issues

**Album not being skipped despite being processed:**
```bash
# Check if album exists in metadata
python3 metadata_utils.py --search "album-name"

# Verify metadata shows success
cat scraped_images/metadata.json | grep -A 5 "album-url"
```

**Want to re-process a successful album:**
```bash
# Option 1: Delete the album directory
rm -rf scraped_images/album-name/

# Option 2: Remove from metadata.json (edit the file)
# Option 3: Change "scraping_success" to false in metadata.json
```

**View failed albums:**
```bash
python3 metadata_utils.py --failed
```

## 📊 Metadata Management 🆕

### View Statistics
```bash
python3 metadata_utils.py --stats
```
```
📊 METADATA STATISTICS
========================================
Total Albums: 25
Successfully Processed: 22
Failed Processing: 3
Albums with Names: 25
Albums with Dates: 23
Total Images Downloaded: 1,247
Date Range: 2018 - 2024
```

### List Albums
```bash
# All albums
python3 metadata_utils.py --list-albums

# Failed albums only
python3 metadata_utils.py --failed

# Albums from specific year
python3 metadata_utils.py --year 2020

# Search albums
python3 metadata_utils.py --search "sarah"
python3 metadata_utils.py --search "wedding"
```

### Export and Cleanup
```bash
# Export to CSV spreadsheet
python3 metadata_utils.py --export-csv

# Clean up old metadata entries
python3 metadata_utils.py --cleanup
```

### How Caching Works

The scraper now intelligently skips albums:

- ✅ **Skip**: Album in metadata with `"scraping_success": true` and images > 0
- 🔄 **Retry**: Album in metadata with `"scraping_success": false` (previous failure)
- 🆕 **Process**: New album not in metadata

**Example output:**
```
🔄 Album 'Sarah & Michael Wedding' already successfully processed (42 images in metadata), skipping...
⚠️  Album 'Failed Album' previously failed (No 'View Photos' link found), re-processing...
```

### Reset Everything
```bash
# Delete all scraped data and start fresh
rm scraped_images/metadata.json
rm -rf scraped_images/*/
```

## 🔧 Advanced Usage

### Custom Output Directory
```python
scraper = RebeccaAlbumScraper(output_dir="my_custom_folder")
```

### Non-headless Mode (for debugging)
```python
scraper = RebeccaAlbumScraper(headless=False)
```

### Adjust Timing
```python
scraper = RebeccaAlbumScraper(delay=5)  # Slower for unstable connections
```

## 📝 Notes

- **Respect the website** - The scraper includes delays to avoid overwhelming the server
- **High-quality images** - Automatically requests the highest quality versions available
- **Resume-friendly** - Won't re-download existing files
- **Cross-platform** - Works on macOS, Linux, and Windows (with minor setup differences)

## 🚨 Legal Notice

This tool is for educational purposes. Make sure you have permission to download the images and respect the website's terms of service and robots.txt file.

## 📞 Support

If you encounter issues:

1. Check the terminal output for specific error messages
2. Try running with `headless_mode = False` to see browser actions
3. Ensure Chrome and ChromeDriver versions are compatible
4. Check your internet connection and try again
