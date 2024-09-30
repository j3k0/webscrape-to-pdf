#!/usr/bin/env python3

import argparse
import requests
from bs4 import BeautifulSoup
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from urllib.parse import urljoin, urlparse, urldefrag
import time
from urllib.robotparser import RobotFileParser
import random
import sys
import os
from requests_cache import CacheMixin, SQLiteCache
from requests import Session

# Constants
USER_AGENT = 'YourScraperBot/1.0 (+http://example.com/bot)'
DEFAULT_DELAY = 1  # Default delay between requests in seconds
DEFAULT_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".website_to_pdf_cache")

class CachedSession(CacheMixin, Session):
    pass

def get_robots_parser(base_url):
    rp = RobotFileParser()
    robots_url = urljoin(base_url, '/robots.txt')
    rp.set_url(robots_url)
    rp.read()
    return rp

def remove_fragment(url):
    return urldefrag(url)[0]

def create_cached_session(cache_dir):
    return CachedSession(
        cache_name=os.path.join(cache_dir, 'cache'),
        backend='sqlite',
        expire_after=None,  # Cache doesn't expire
    )

def scrape_page(url, session):
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract and return the relevant content
        # This is a placeholder and needs to be implemented
        return soup.get_text()
    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return ""

def is_valid_url(base_url, url):
    base_domain = urlparse(base_url).netloc
    url_domain = urlparse(url).netloc
    url_without_fragment = remove_fragment(url)
    return url_domain == base_domain and url_without_fragment.startswith(base_url)

def crawl_websites(base_urls, session=None, verbose=False, delay=DEFAULT_DELAY):
    if session is None:
        session = create_cached_session(DEFAULT_CACHE_DIR)
        session.headers.update({'User-Agent': USER_AGENT})

    all_results = []
    for base_url in base_urls:
        robots_parser = get_robots_parser(base_url)
        results = crawl_website(base_url, base_url, session=session, robots_parser=robots_parser, verbose=verbose, delay=delay)
        all_results.extend(results)
    
    return all_results

def crawl_website(base_url, current_url, visited=None, session=None, robots_parser=None, verbose=False, delay=DEFAULT_DELAY):
    if visited is None:
        visited = set()
    if session is None:
        session = create_cached_session(DEFAULT_CACHE_DIR)
        session.headers.update({'User-Agent': USER_AGENT})
    if robots_parser is None:
        robots_parser = get_robots_parser(base_url)
    
    current_url = remove_fragment(current_url)
    
    # Check if the URL has already been visited
    if current_url in visited:
        if verbose:
            print(f"Skipping already visited URL: {current_url}", file=sys.stderr)
        return []

    if not is_valid_url(base_url, current_url):
        return []

    if not robots_parser.can_fetch(USER_AGENT, current_url):
        if verbose:
            print(f"Robots.txt disallows scraping: {current_url}", file=sys.stderr)
        return []

    # Mark the URL as visited before scraping
    visited.add(current_url)
    if verbose:
        print(f"Scraping: {current_url}", file=sys.stderr)
    
    time.sleep(delay + random.random() * delay)  # Add a small random delay

    content = scrape_page(current_url, session)
    results = [(current_url, content)]

    try:
        response = session.get(current_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            next_url = remove_fragment(urljoin(current_url, link['href']))
            # Only crawl the next URL if it hasn't been visited
            if next_url not in visited:
                results.extend(crawl_website(base_url, next_url, visited, session, robots_parser, verbose, delay))
    except requests.RequestException as e:
        if verbose:
            print(f"Error crawling {current_url}: {e}", file=sys.stderr)

    return results

def create_pdf(content, output_file):
    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter
    y = height - 40
    for url, text in content:
        c.drawString(40, y, f"URL: {url}")
        y -= 20
        for line in text.split('\n'):
            c.drawString(40, y, line[:100])  # Limit line length to prevent overflow
            y -= 15
            if y < 40:
                c.showPage()
                y = height - 40
    c.save()

def main():
    parser = argparse.ArgumentParser(description="Scrape multiple websites and create a PDF.")
    parser.add_argument("urls", nargs='+', help="The base URLs to scrape")
    parser.add_argument("-o", "--output", help="The output PDF file name (default: stdout)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    parser.add_argument("--cache-dir", help="Directory to store the cache (default: ~/.website_to_pdf_cache)")
    parser.add_argument("-d", "--delay", type=float, default=DEFAULT_DELAY, 
                        help=f"Delay between requests in seconds (default: {DEFAULT_DELAY})")
    args = parser.parse_args()

    # Determine cache directory
    cache_dir = args.cache_dir or os.environ.get('WEBSITE_TO_PDF_CACHE_DIR') or DEFAULT_CACHE_DIR
    
    if args.verbose:
        print(f"Using cache directory: {cache_dir}", file=sys.stderr)
        print(f"Using delay: {args.delay} seconds", file=sys.stderr)

    os.makedirs(cache_dir, exist_ok=True)
    session = create_cached_session(cache_dir)
    session.headers.update({'User-Agent': USER_AGENT})

    try:
        content = crawl_websites(args.urls, session=session, verbose=args.verbose, delay=args.delay)
        
        if args.output:
            create_pdf(content, args.output)
            if args.verbose:
                print(f"PDF created: {args.output}", file=sys.stderr)
        else:
            # Print content to stdout
            for url, text in content:
                print(f"URL: {url}")
                print(text)
                print("---")
        
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())