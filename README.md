# Bulky
## Overview
The Bulky is a Python script that downloads all images from a specified website and exports the image links to both TXT and JSON files. 
The script utilizes asynchronous programming with the aiohttp library for efficient image downloading.

## Features
- Downloads all images from a given website.
- Exports image links to both TXT and JSON files.
- Supports asynchronous downloading for improved performance.
- Handles non-image content gracefully.
## Prerequisites
- Python 3.6 or above

Required Python packages can be installed using:
```zsh
pip3 install aiohttp requests beautifulsoup4
```
## Usage
Command-line Arguments
- <url>: Website URL from which to download images.
- <directory> (Optional): Directory to save images. If not provided, the script creates a directory based on the website's domain.
## Running the Script
Open a terminal or command prompt.
Navigate to the directory containing the script.
Run the script with the following command:
```zsh
python3 bulky.py <url> <directory>
```
## Example
```bash
python3 bulky.py https://example.com
```
## Additional Information
- The script employs asynchronous programming to download images concurrently, improving efficiency.
- Image links are exported to both TXT and JSON files for reference.
- Non-image content is gracefully skipped during the download process.
