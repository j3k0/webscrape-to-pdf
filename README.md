# WebScrape2PDF

![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

WebScrape2PDF is a powerful Python tool that crawls multiple websites, scrapes their content, and generates a single PDF document. It's perfect for creating offline archives, documentation, or research materials.

## 🚀 Features

- 🕷️ Recursively crawls multiple websites within their respective domains
- 🤖 Respects robots.txt rules for ethical scraping
- ⏱️ Implements polite scraping with configurable delays between requests
- 📄 Generates a single PDF with the scraped content from all sites
- 🗣️ Supports verbose mode for debugging
- 📁 Flexible output to file or stdout
- 💾 Implements persistent caching with ETag support for efficient repeated runs
- 🔧 Configurable cache directory
- 🔄 Implements a retry strategy for scraping errors (50 attempts with 10-second delays)
- 🌐 Handles JavaScript-rendered content using Selenium

## 🛠️ Installation

1. Clone this repository:
   ```
   git clone https://github.com/j3k0/webscrape2pdf.git
   cd webscrape2pdf
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install the package:
   ```
   pip install .
   ```

## 📖 Usage

After installation, use the `webscrape2pdf` command:

```
webscrape2pdf [options] URL [URL ...]
```

### Arguments:
- `URL`: The base URLs to scrape (at least one required, can specify multiple)

### Options:
- `-o OUTPUT`, `--output OUTPUT`: The output PDF file name (default: stdout)
- `-v`, `--verbose`: Increase output verbosity
- `--cache-dir CACHE_DIR`: Directory to store the cache
- `-d DELAY`, `--delay DELAY`: Delay between requests in seconds (default: 1)
- `--force-cache`: Always use cached version if available, ignoring ETag
- `-h`, `--help`: Show help message and exit

### Examples:

1. Scrape multiple websites and save as PDF:
   ```
   webscrape2pdf https://example.com https://another-example.com -o output.pdf
   ```

2. Scrape multiple websites and print content to stdout:
   ```
   webscrape2pdf https://example.com https://another-example.com
   ```

3. Scrape with verbose output, custom cache directory, and faster delay:
   ```
   webscrape2pdf https://example.com -o output.pdf -v --cache-dir /path/to/cache -d 0.5
   ```

4. Scrape your own website with no delay:
   ```
   webscrape2pdf https://your-own-website.com -o output.pdf -d 0
   ```

## 💾 Caching

WebScrape2PDF uses a persistent cache to improve performance and reduce unnecessary network requests. The cache respects ETags to ensure only changed content is re-downloaded.

Configure the cache directory (in order of priority):

1. Command-line argument: `--cache-dir /path/to/cache`
2. Environment variable: `WEBSITE_TO_PDF_CACHE_DIR=/path/to/cache`
3. Default location: `~/.webscrape2pdf_cache`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [Requests](https://docs.python-requests.org/en/master/) for HTTP requests
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [xhtml2pdf](https://github.com/xhtml2pdf/xhtml2pdf) for PDF generation
- [Selenium](https://www.selenium.dev/) for handling JavaScript-rendered content

## 📞 Support

If you encounter any problems or have any questions, please [open an issue](https://github.com/j3k0/webscrape2pdf/issues) on GitHub.

---

Made with ❤️ by [Jean-Christophe Hoelt](https://github.com/j3k0)

