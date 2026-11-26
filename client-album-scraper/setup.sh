#!/bin/bash
# Setup script for Rebecca Richards Photography Album Scraper

echo "🎨 Rebecca Richards Photography Album Scraper Setup"
echo "=================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip3 is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ pip3 found: $(pip3 --version)"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Check if Chrome is installed
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null && ! ls /Applications/Google\ Chrome.app &> /dev/null; then
    echo "⚠️  Chrome browser not found. Please install Google Chrome."
fi

# Install ChromeDriver
echo "🌐 Installing ChromeDriver..."

# Check if ChromeDriver is already installed
if command -v chromedriver &> /dev/null; then
    echo "✅ ChromeDriver already installed: $(chromedriver --version)"
else
    # Try to install via Homebrew on macOS
    if command -v brew &> /dev/null; then
        echo "📥 Installing ChromeDriver via Homebrew..."
        brew install chromedriver
        if [ $? -eq 0 ]; then
            echo "✅ ChromeDriver installed successfully"
        else
            echo "❌ Failed to install ChromeDriver via Homebrew"
            echo "Please install manually from: https://chromedriver.chromium.org/"
            exit 1
        fi
    else
        echo "❌ Homebrew not found. Please install ChromeDriver manually:"
        echo "   1. Go to https://chromedriver.chromium.org/"
        echo "   2. Download the version matching your Chrome browser"
        echo "   3. Extract and place chromedriver in your PATH"
        exit 1
    fi
fi

# Make scraper executable
chmod +x scraper.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Run the scraper: python3 scraper.py"
echo "   2. Images will be saved to: ./scraped_images/"
echo ""
echo "⚙️  Configuration options in scraper.py:"
echo "   - output_directory: Change where images are saved"
echo "   - headless_mode: Set to False to see browser window"
echo "   - delay_seconds: Adjust timing between operations"
echo ""
echo "🚀 Ready to scrape! Run: python3 scraper.py"