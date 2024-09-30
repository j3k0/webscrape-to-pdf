import os

USER_AGENT = 'YourScraperBot/1.0 (+http://example.com/bot)'
DEFAULT_DELAY = 1  # Default delay between requests in seconds
DEFAULT_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".webscrape2pdf_cache")
MAX_RETRIES = 50
RETRY_DELAY = 10