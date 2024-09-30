import argparse
from .config import DEFAULT_DELAY, DEFAULT_CACHE_DIR

def parse_arguments():
    parser = argparse.ArgumentParser(description="Scrape multiple websites and create a PDF.")
    parser.add_argument("urls", nargs='+', help="The base URLs to scrape")
    parser.add_argument("-o", "--output", help="The output PDF file name (default: stdout)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    parser.add_argument("--cache-dir", help="Directory to store the cache (default: ~/.webscrape2pdf_cache)")
    parser.add_argument("-d", "--delay", type=float, default=DEFAULT_DELAY, 
                        help=f"Delay between requests in seconds (default: {DEFAULT_DELAY})")
    parser.add_argument("--force-cache", action="store_true", help="Always use cached version if available, ignoring ETag")
    return parser.parse_args()