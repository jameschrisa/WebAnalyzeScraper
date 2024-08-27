import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import mimetypes
import concurrent.futures
from cli_ui import info, error, warning, setup, spinner
import pync
import filetype

setup(quiet=True)

def rate_limited_get(url, timeout=10):
    # ... (keep the existing rate_limited_get function)

def sanitize_filename(filename):
    # Remove hash from filename
    clean_name = re.sub(r'\.[a-f0-9]{8,}\.', '.', filename)
    return "".join([c for c in clean_name if c.isalpha() or c.isdigit() or c in (' ', '-', '_', '.')]).rstrip()

def download_file(url, path):
    response = rate_limited_get(url)
    if response:
        try:
            with open(path, 'wb') as f:
                f.write(response.content)
            info(f"Downloaded: {url} as {path}")
            return True
        except IOError as e:
            error(f"Error saving file {path}: {str(e)}")
    else:
        warning(f"Failed to download: {url}")
    return False

def create_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        error(f"Error creating directory {path}: {str(e)}")

def download_resource(url, base_dir, resource_type, filename_map):
    try:
        resource_url = urljoin(url, resource_type.get('href') or resource_type.get('src'))
        original_filename = os.path.basename(urlparse(resource_url).path)
        clean_filename = sanitize_filename(original_filename)
        resource_path = os.path.join(base_dir, resource_type.name, clean_filename)
        create_directory(os.path.dirname(resource_path))
        if download_file(resource_url, resource_path):
            filename_map[original_filename] = clean_filename
            return resource_type, os.path.relpath(resource_path, base_dir)
    except Exception as e:
        error(f"Error downloading resource {resource_url}: {str(e)}")
    return resource_type, None

def update_file_references(file_path, filename_map):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for original, clean in filename_map.items():
        content = content.replace(original, clean)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def scrape_and_reconstruct(url):
    with spinner(f"Analyzing and downloading files from {url}"):
        response = rate_limited_get(url)
        if not response:
            error(f"Failed to fetch the main page: {url}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        domain = urlparse(url).netloc
        
        downloads_folder = os.path.expanduser("~/Downloads")
        base_dir = os.path.join(downloads_folder, sanitize_filename(domain))
        
        create_directory(base_dir)
        
        filename_map = {}
        
        # Download HTML
        html_path = os.path.join(base_dir, 'index.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        # Prepare resource downloads
        resources = [
            *soup.find_all('link', rel='stylesheet'),
            *soup.find_all('script', src=True),
            *soup.find_all('img', src=True)
        ]

        # Download resources concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_resource = {
                executor.submit(download_resource, url, base_dir, resource, filename_map): resource
                for resource in resources
            }
            for future in concurrent.futures.as_completed(future_to_resource):
                resource, new_path = future.result()
                if new_path:
                    if resource.name == 'link':
                        resource['href'] = new_path
                    else:
                        resource['src'] = new_path
        
        # Update references in HTML
        update_file_references(html_path, filename_map)
        
        # Update references in CSS and JS files
        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith(('.css', '.js')):
                    file_path = os.path.join(root, file)
                    update_file_references(file_path, filename_map)
    
    info(f"Website scraped and reconstructed in '{base_dir}'.")
    
    # Send notification
    pync.notify(
        f"Website {url} has been scraped and saved in {base_dir}",
        title="Web Scraping Complete"
    )

def main():
    url = input("Enter the URL of the website to scrape: ")
    scrape_and_reconstruct(url)

if __name__ == "__main__":
    main()
