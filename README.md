# Web Scraper and Reconstructor

This Python application allows users to input a URL, analyze and download the website's elements, structure, source HTML, JavaScript, CSS, and other dependency files. It then reconstructs all the assets and files, inferring the best project structure.

## Features

- Scrapes and downloads HTML, CSS, JavaScript, and images from a given URL
- Reconstructs the website structure in a local directory
- Concurrent downloading of resources for improved performance
- Rate limiting to respect server resources
- Error handling and logging for reliable operation

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone this repository or download the script:

   ```
   git clone https://github.com/yourusername/web-scraper-reconstructor.git
   cd web-scraper-reconstructor
   ```

2. Install the required dependencies:

   ```
   pip install requests beautifulsoup4 ratelimit
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

3. The script will create a new directory named after the domain of the website and download all the resources into it.

4. Once completed, you'll find the reconstructed website in the newly created directory.

## Structure

The scraped website will be reconstructed with the following structure:

```
domain_name/
├── index.html
├── css/
│   └── [css files]
├── js/
│   └── [js files]
└── images/
    └── [image files]
```

## Logging

The script logs its activities, which can be found in the console output. This includes information about downloaded files, any errors encountered, and the final status of the scraping process.

## Limitations

- This scraper may not work perfectly with websites that rely heavily on client-side rendering or dynamic content loading.
- Some websites may block or rate-limit scraping attempts. Always ensure you have permission to scrape a website before doing so.
- The script currently only scrapes the initial URL provided and does not follow links to other pages on the site.

## Contributing

Contributions to improve the script are welcome. Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Disclaimer

Web scraping may be against the terms of service of some websites. Always ensure you have permission to scrape a website before doing so. Use this tool responsibly and ethically.

