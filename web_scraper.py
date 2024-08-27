import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import mimetypes
import concurrent.futures
import logging
from requests.exceptions import RequestException
from ratelimit import limits, sleep_and_retry

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Rate limiting: 5 requests per second
@sleep_and_retry
@limits(calls=5, period=1)
def rate_limited_get(url, timeout=10):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response
    except RequestException as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        return None

def download_file(url, path):
    response = rate_limited_get(url)
    if response:
        try:
            with open(path, 'wb') as f:
                f.write(response.content)
            logger.info(f"Downloaded: {url}")
        except IOError as e:
            logger.error(f"Error saving file {path}: {str(e)}")
    else:
        logger.warning(f"Failed to download: {url}")

def get_file_extension(url, content_type):
    parsed = urlparse(url)
    ext = os.path.splitext(parsed.path)[1]
    if ext:
        return ext
    
    ext = mimetypes.guess_extension(content_type)
    return ext if ext else '.html'

def create_directory(path):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as e:
        logger.error(f"Error creating directory {path}: {str(e)}")

def sanitize_filename(filename):
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()

def download_resource(url, base_dir, resource_type):
    try:
        resource_url = urljoin(url, resource_type.get('href') or resource_type.get('src'))
        resource_path = os.path.join(base_dir, resource_type.name, sanitize_filename(os.path.basename(resource_url)))
        create_directory(os.path.dirname(resource_path))
        download_file(resource_url, resource_path)
        return resource_type, os.path.relpath(resource_path, base_dir)
    except Exception as e:
        logger.error(f"Error downloading resource {resource_url}: {str(e)}")
        return resource_type, None

def scrape_and_reconstruct(url):
    response = rate_limited_get(url)
    if not response:
        logger.error(f"Failed to fetch the main page: {url}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    domain = urlparse(url).netloc
    base_dir = sanitize_filename(domain)
    
    create_directory(base_dir)
    
    # Download HTML
    with open(os.path.join(base_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    
    # Prepare resource downloads
    resources = [
        *soup.find_all('link', rel='stylesheet'),
        *soup.find_all('script', src=True),
        *soup.find_all('img', src=True)
    ]

    # Download resources concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_resource = {
            executor.submit(download_resource, url, base_dir, resource): resource
            for resource in resources
        }
        for future in concurrent.futures.as_completed(future_to_resource):
            resource, new_path = future.result()
            if new_path:
                if resource.name == 'link':
                    resource['href'] = new_path
                else:
                    resource['src'] = new_path
    
    # Save updated HTML
    with open(os.path.join(base_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    logger.info(f"Website scraped and reconstructed in the '{base_dir}' directory.")

def main():
    url = input("Enter the URL of the website to scrape: ")
    scrape_and_reconstruct(url)

if __name__ == "__main__":
    main()
