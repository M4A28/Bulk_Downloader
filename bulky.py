import os
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import argparse
import re
import time
import random
import json


# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RESET = '\033[0m'

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "en-US,en;q=0.5",
}

async def download_image(session, img_url, save_directory):
    try:
        start_time = time.time()
        async with session.get(img_url, headers=HEADERS) as response:
            img_name = os.path.join(save_directory, re.sub(r'[^A-Za-z0-9-_.]+', '', os.path.basename(img_url)) or f'default_{random.randint(1, 1000)}')

            if not response.headers.get('content-type', '').startswith('image'):
                print(f"{RED}Skipped non-image: {img_url}{RESET}")
                return 0, 0, 0

            with open(img_name, 'wb') as img_file:
                img_file.write(await response.read())

            download_time = time.time() - start_time
            print(f"Downloaded: {img_url} to {img_name}{GREEN} ({download_time:.2f} seconds){RESET}")
            return 1, os.path.getsize(img_name), download_time

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"{RED}Received 403 error. Retrying after 20 seconds...{RESET}")
            await asyncio.sleep(20)
            return await download_image(session, img_url, save_directory)
        else:
            raise
    except Exception as e:
        print(f"{RED}Error downloading {img_url}: {e}{RESET}")
        return 0, 0, 0

async def download_images_async(url, save_directory):
    os.makedirs(save_directory, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            print(f"{RED}Failed to retrieve the page. Status code: {response.status_code}{RESET}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        img_urls = [urljoin(url, img['src']) for img in soup.find_all('img', src=True)]

        tasks = [download_image(session, img_url, save_directory) for img_url in img_urls]
        results = await asyncio.gather(*tasks)

        total_size, total_download_time, num_all_files = sum(result[1] for result in results), sum(result[2] for result in results), sum(result[0] for result in results)
        image_links, num_images = img_urls, num_all_files

        print_results(results, total_size, total_download_time, num_all_files, num_images, image_links, soup.title.string, save_directory)

def colorize(text, color):
    return f"{color}{text}{RESET}"

def format_size_color(size_mb):
    return colorize(f"{size_mb:.2f} MB", GREEN) if size_mb < 30 else (colorize(f"{size_mb:.2f} MB", BLUE) if size_mb < 60 else colorize(f"{size_mb:.2f} MB", RED))

def format_time(milliseconds):
    return colorize(f"{milliseconds:.2f} milliseconds", GREEN) if milliseconds < 5000 else (colorize(f"{milliseconds / 1000:.2f} seconds", BLUE) if milliseconds < 15000 else colorize(f"{milliseconds / 1000:.2f} seconds", RED))

def format_count(value):
    return colorize(str(value), GREEN)

def print_results(results, total_size, total_download_time, num_all_files, num_images, image_links, title, save_directory):
    sanitized_title = re.sub(r'[^\w.-]', '', title) or 'untitled'
    export_filename_json = f"{sanitized_title}_images.json"
    export_filename = f"{sanitized_title}_images.txt"
    export_filepath_txt = os.path.join(save_directory, export_filename)
    export_filepath_json = os.path.join(save_directory, export_filename_json)
    
    existing_data = {'image_links': [], 'all_links': []}
    if os.path.exists(export_filepath_json):
        with open(export_filepath_json, 'r') as existing_file:
            existing_data = json.load(existing_file)
    existing_data['image_links'].extend(image_links)

    
    with open(export_filepath_txt, 'w') as export_file:
        export_file.write('\n'.join(image_links))
    
    with open(export_filepath_json, 'w') as export_file_json:
        json.dump(existing_data, export_file_json, indent=2)

    print(f"{BLUE}Finished downloading images.{RESET}")
    print(f"Total time taken: {format_time(total_download_time)}")
    print(f"Total file size: {format_size_color(total_size / (1024 * 1024))}")
    print(f"Number of all files: {format_count(num_all_files)}")
    print(f"Number of images downloaded: {format_count(num_images)}")
    print(f"Image links exported to TXT: {format_count(export_filepath_txt)}")
    print(f"Image links exported to JSON: {format_count(export_filepath_json)}")
def create_directory_from_url(url):
    return re.sub(r'[^A-Za-z0-9-_.]+', '', urlparse(url).netloc) or f'default_{random.randint(1, 1000)}'

def main():
    parser = argparse.ArgumentParser(description="Download all images from a website and export image links.")
    parser.add_argument("url", help="Website URL")
    parser.add_argument("directory", help="Directory to save images", nargs='?')

    args = parser.parse_args()
    args.directory = args.directory or create_directory_from_url(args.url)

    print(f"{BLUE}Creating directory: {format_count(args.directory)}{RESET}")
    asyncio.run(download_images_async(args.url, args.directory))

if __name__ == "__main__":
    main()
