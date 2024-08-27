import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import mimetypes
import shutil

def download_file(url, path):
    response = requests.get(url)
    with open(path, 'wb') as f:
        f.write(response.content)

def get_file_extension(url, content_type):
    parsed = urlparse(url)
    ext = os.path.splitext(parsed.path)[1]
    if ext:
        return ext
    
    ext = mimetypes.guess_extension(content_type)
    return ext if ext else '.html'

def create_directory(path):
    os.makedirs(path, exist_ok=True)

def sanitize_filename(filename):
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()

def scrape_and_reconstruct(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    domain = urlparse(url).netloc
    base_dir = sanitize_filename(domain)
    
    create_directory(base_dir)
    
    # Download HTML
    with open(os.path.join(base_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    
    # Download CSS
    for css in soup.find_all('link', rel='stylesheet'):
        css_url = urljoin(url, css.get('href'))
        css_path = os.path.join(base_dir, 'css', os.path.basename(css_url))
        create_directory(os.path.dirname(css_path))
        download_file(css_url, css_path)
        css['href'] = os.path.relpath(css_path, base_dir)
    
    # Download JavaScript
    for script in soup.find_all('script', src=True):
        js_url = urljoin(url, script.get('src'))
        js_path = os.path.join(base_dir, 'js', os.path.basename(js_url))
        create_directory(os.path.dirname(js_path))
        download_file(js_url, js_path)
        script['src'] = os.path.relpath(js_path, base_dir)
    
    # Download images
    for img in soup.find_all('img', src=True):
        img_url = urljoin(url, img.get('src'))
        img_path = os.path.join(base_dir, 'images', os.path.basename(img_url))
        create_directory(os.path.dirname(img_path))
        download_file(img_url, img_path)
        img['src'] = os.path.relpath(img_path, base_dir)
    
    # Save updated HTML
    with open(os.path.join(base_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    print(f"Website scraped and reconstructed in the '{base_dir}' directory.")

def main():
    url = input("Enter the URL of the website to scrape: ")
    scrape_and_reconstruct(url)

if __name__ == "__main__":
    main()
