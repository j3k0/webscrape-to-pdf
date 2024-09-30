# Website to PDF Scraper

This Python script crawls multiple websites starting from given URLs, scrapes the content of all pages under the same domains, and generates a single PDF containing the scraped content.

## Features

- Recursively crawls multiple websites within their respective domains
- Respects robots.txt rules
- Implements polite scraping with configurable delays between requests
- Generates a single PDF with the scraped content from all sites
- Supports verbose mode for debugging
- Can output to a file or stdout
- Implements persistent caching with ETag support for efficient repeated runs
- Configurable cache directory
- Implements a retry strategy for scraping errors (50 attempts with 10-second delays)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/website-to-pdf-scraper.git
   cd website-to-pdf-scraper
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

```
python website_to_pdf.py [-h] [-o OUTPUT] [-v] [--cache-dir CACHE_DIR] [-d DELAY] url [url ...]
```

Arguments:
- `url`: The base URLs to scrape (at least one required, can specify multiple)
- `-o OUTPUT`, `--output OUTPUT`: The output PDF file name (optional, default: stdout)
- `-v`, `--verbose`: Increase output verbosity (optional)
- `--cache-dir CACHE_DIR`: Directory to store the cache (optional)
- `-d DELAY`, `--delay DELAY`: Delay between requests in seconds (optional, default: 1)
- `-h`, `--help`: Show help message and exit

Examples:
1. Scrape multiple websites and save as PDF:
   ```
   python website_to_pdf.py https://example.com https://another-example.com -o output.pdf
   ```

2. Scrape multiple websites and print content to stdout:
   ```
   python website_to_pdf.py https://example.com https://another-example.com
   ```

3. Scrape with verbose output, custom cache directory, and faster delay:
   ```
   python website_to_pdf.py https://example.com https://another-example.com -o output.pdf -v --cache-dir /path/to/cache -d 0.1
   ```

4. Scrape your own website with no delay:
   ```
   python website_to_pdf.py https://your-own-website.com -o output.pdf -d 0
   ```

## Caching

The script uses a persistent cache to improve performance for repeated runs and reduce unnecessary network requests. The cache respects ETags, ensuring that only changed content is re-downloaded.

You can configure the cache directory in three ways (in order of priority):

1. Command-line argument: `--cache-dir /path/to/cache`
2. Environment variable: `WEBSITE_TO_PDF_CACHE_DIR=/path/to/cache`
3. Default location: `~/.website_to_pdf_cache`

// ... (rest of the README content)