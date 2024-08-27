# Web Scraper and Reconstructor

This Python application allows users to input a URL, analyze and download the website's elements, structure, source HTML, JavaScript, CSS, and other dependency files. It then reconstructs all the assets and files in the Downloads folder on your Mac, providing a visual progress indicator and a completion notification.

## Features

- Scrapes and downloads HTML, CSS, JavaScript, and images from a given URL
- Reconstructs the website structure in a local directory within the Downloads folder
- Concurrent downloading of resources for improved performance
- Rate limiting to respect server resources
- Error handling and logging for reliable operation
- Visual progress indicator using Shopify's cli-ui spinner
- System notification upon completion of the scraping process
- Colored and formatted console output for better readability

## Prerequisites

- Python 3.7+
- pip (Python package installer)
- macOS (for the current download path and notification system)

## Installation

1. Clone this repository or download the script:

   ```
   git clone https://github.com/yourusername/web-scraper-reconstructor.git
   cd web-scraper-reconstructor
   ```

2. Install the required dependencies:

   ```
   pip install requests beautifulsoup4 ratelimit cli-ui pync
   ```

## Usage

1. Run the script:

   ```
   python web_scraper.py
   ```

2. When prompted, enter the URL of the website you want to scrape:

   ```
   Enter the URL of the website to scrape: https://example.com
   ```

3. The script will display a spinner while it analyzes and downloads files.

4. Once completed, you'll receive a system notification, and the reconstructed website will be in a new directory within your Downloads folder.

## Structure

The scraped website will be reconstructed with the following structure in your Downloads folder:

```
~/Downloads/domain_name/
├── index.html
├── css/
│   └── [css files]
├── js/
│   └── [js files]
└── images/
    └── [image files]
```

## Console Output

The script uses cli-ui to provide colored and formatted output in the terminal:

- Green text for successful operations
- Yellow text for warnings
- Red text for errors

## Notification

Upon completion of the scraping process, you will receive a system notification indicating that the job is complete and where the files have been saved.

## Limitations

- This scraper may not work perfectly with websites that rely heavily on client-side rendering or dynamic content loading.
- Some websites may block or rate-limit scraping attempts. Always ensure you have permission to scrape a website before doing so.
- The script currently only scrapes the initial URL provided and does not follow links to other pages on the site.
- The current version is optimized for macOS. Some modifications may be needed for use on other operating systems.

## Contributing

Contributions to improve the script are welcome. Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Disclaimer

Web scraping may be against the terms of service of some websites. Always ensure you have permission to scrape a website before doing so. Use this tool responsibly and ethically.
