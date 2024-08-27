import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import mimetypes
import concurrent.futures
import warnings

# Suppress the urllib3 warning
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

# Simple progress indicator
def print_progress(message):
    print(f"[INFO] {message}")

def rate_limited_get(url, timeout=10):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"[ERROR] Error fetching {url}: {str(e)}")
        return None

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
            print(f"[INFO] Downloaded: {url} as {path}")
            return True
        except IOError as e:
            print(f"[ERROR] Error saving file {path}: {str(e)}")
    else:
        print(f"[WARNING] Failed to download: {url}")
    return False

def create_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        print(f"[ERROR] Error creating directory {path}: {str(e)}")

def get_resource_type(url):
    _, ext = os.path.splitext(url)
    ext = ext.lower()
    if ext in ['.css']:
        return 'css'
    elif ext in ['.js']:
        return 'js'
    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
        return 'images'
    elif ext in ['.html', '.htm']:
        return 'html'
    else:
        return 'other'

def get_relative_path(url, base_url):
    parsed_url = urlparse(url)
    parsed_base = urlparse(base_url)
    if parsed_url.netloc != parsed_base.netloc:
        return None
    path = parsed_url.path
    if path.startswith('/'):
        path = path[1:]
    return path

def download_resource(url, base_url, base_dir, filename_map):
    try:
        relative_path = get_relative_path(url, base_url)
        if not relative_path:
            return None, None

        resource_type = get_resource_type(url)
        dir_path = os.path.dirname(relative_path)
        original_filename = os.path.basename(relative_path)
        clean_filename = sanitize_filename(original_filename)
        
        resource_path = os.path.join(base_dir, dir_path, resource_type, clean_filename)
        create_directory(os.path.dirname(resource_path))
        
        if download_file(url, resource_path):
            filename_map[original_filename] = os.path.join(dir_path, resource_type, clean_filename)
            return url, os.path.relpath(resource_path, base_dir)
    except Exception as e:
        print(f"[ERROR] Error downloading resource {url}: {str(e)}")
    return None, None

def update_file_references(file_path, filename_map):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for original, clean in filename_map.items():
            content = content.replace(original, clean)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"[ERROR] Error updating references in {file_path}: {str(e)}")

def scrape_and_reconstruct(url):
    print_progress(f"Analyzing and downloading files from {url}")
    response = rate_limited_get(url)
    if not response:
        print(f"[ERROR] Failed to fetch the main page: {url}")
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
        link.get('href') for link in soup.find_all('link', rel='stylesheet', href=True)
    ] + [
        script.get('src') for script in soup.find_all('script', src=True)
    ] + [
        img.get('src') for img in soup.find_all('img', src=True)
    ]

    resources = [urljoin(url, resource) for resource in resources if resource]

    # Download resources concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_resource = {
            executor.submit(download_resource, resource, url, base_dir, filename_map): resource
            for resource in resources
        }
        for future in concurrent.futures.as_completed(future_to_resource):
            original_url, new_path = future.result()
            if new_path:
                for tag in soup.find_all(['link', 'script', 'img']):
                    if tag.get('src') == original_url:
                        tag['src'] = new_path
                    elif tag.get('href') == original_url:
                        tag['href'] = new_path
    
    # Update references in HTML
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    # Update references in CSS and JS files
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(('.css', '.js')):
                file_path = os.path.join(root, file)
                update_file_references(file_path, filename_map)

    print_progress(f"Website scraped and reconstructed in '{base_dir}'.")

def main():
    url = input("Enter the URL of the website to scrape: ")
    scrape_and_reconstruct(url)

if __name__ == "__main__":
    main()
