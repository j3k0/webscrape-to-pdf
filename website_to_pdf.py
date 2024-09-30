#!/usr/bin/env python3

import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
import time
from urllib.robotparser import RobotFileParser
import random
import sys
import os
from requests_cache import CacheMixin, SQLiteCache
from requests import Session
from xhtml2pdf import pisa
import io
import re
import undetected_chromedriver as uc
import requests_cache
from requests.exceptions import RequestException

# Constants
USER_AGENT = 'YourScraperBot/1.0 (+http://example.com/bot)'
DEFAULT_DELAY = 1  # Default delay between requests in seconds
DEFAULT_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".website_to_pdf_cache")

MAX_RETRIES = 50
RETRY_DELAY = 10

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

def create_cached_session(cache_dir, force_cache=False):
    session = CachedSession(
        cache_name=os.path.join(cache_dir, 'cache'),
        backend='sqlite',
        expire_after=None,  # Cache doesn't expire
    )
    if force_cache:
        # Always use cached response if available, regardless of age or ETag
        session.cache.ignore_cache_control = True
        session.cache.old_data_on_error = True
    return session

def create_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return uc.Chrome(options=options)

def retry_scrape(func, *args, **kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"Error scraping (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                print(f"Max retries reached. Giving up on scraping.")
                raise

def scrape_page(url, driver, session):
    def _scrape():
        try:
            # First, try to get the page from the cache
            response = session.get(url, expire_after=-1)  # -1 means use cached version if available
            if not response.from_cache:
                # If not in cache, use Selenium to fetch and render the page
                driver.get(url)
                time.sleep(5)  # Wait for JavaScript to render content
                html = driver.page_source
                # Store the fetched content in the cache
                session.cache.set(url, html)
            else:
                html = response.text

            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract the main content (you may need to adjust this selector)
            main_content = soup.find('main') or soup.find('body')
            
            # Add base URL to ensure relative links work
            base_tag = soup.new_tag('base', href=url)
            main_content.insert(0, base_tag)
            
            # Convert internal links to absolute URLs
            for a in main_content.find_all('a', href=True):
                a['href'] = urljoin(url, a['href'])
            
            # Wrap the content in a div with some basic styling
            wrapped_content = f"""
            <div style="font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto;">
                <h1>{soup.title.string if soup.title else url}</h1>
                {main_content}
            </div>
            """
            return wrapped_content
        except Exception as e:
            print(f"Error in _scrape function: {e}")
            raise

    try:
        return retry_scrape(_scrape)
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return f"<p>Error scraping {url}: {e}</p>"

def is_valid_url(base_url, url):
    base_domain = urlparse(base_url).netloc
    url_domain = urlparse(url).netloc
    url_without_fragment = remove_fragment(url)
    return url_domain == base_domain and url_without_fragment.startswith(base_url)

def crawl_websites(base_urls, driver=None, session=None, verbose=False, delay=DEFAULT_DELAY):
    if driver is None:
        driver = create_driver()
    if session is None:
        session = create_cached_session(DEFAULT_CACHE_DIR)

    all_results = []
    for base_url in base_urls:
        robots_parser = get_robots_parser(base_url)
        results = crawl_website(base_url, base_url, driver=driver, session=session, robots_parser=robots_parser, verbose=verbose, delay=delay)
        all_results.extend(results)
    
    return all_results

def crawl_website(base_url, current_url, visited=None, driver=None, session=None, robots_parser=None, verbose=False, delay=DEFAULT_DELAY):
    if visited is None:
        visited = set()
    if driver is None:
        driver = create_driver()
    if session is None:
        session = create_cached_session(DEFAULT_CACHE_DIR)
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

    content = scrape_page(current_url, driver, session)
    results = [(current_url, content)]

    try:
        response = session.get(current_url, expire_after=-1)
        if not response.from_cache:
            driver.get(current_url)
            time.sleep(5)  # Wait for JavaScript to render content
            html = driver.page_source
            session.cache.set(current_url, html)
        else:
            html = response.text

        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a', href=True):
            next_url = remove_fragment(urljoin(current_url, link['href']))
            # Only crawl the next URL if it hasn't been visited
            if next_url not in visited:
                results.extend(crawl_website(base_url, next_url, visited, driver, session, robots_parser, verbose, delay))
    except Exception as e:
        if verbose:
            print(f"Error crawling {current_url}: {e}", file=sys.stderr)

    return results

def create_pdf(content, output_file):
    html_content = """
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {
                size: letter;
                margin: 2cm;
            }
            body {
                font-family: Arial, sans-serif;
                font-size: 12px;
                line-height: 1.6;
            }
            h1 {
                font-size: 18px;
                color: #333;
                margin-top: 20px;
            }
            h2 {
                font-size: 16px;
                color: #444;
            }
            a {
                color: #0066cc;
                text-decoration: none;
            }
        </style>
    </head>
    <body>
    """
    
    for url, html in content:
        # Parse the HTML content
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove all image tags
        for img in soup.find_all('img'):
            img.decompose()
        
        # Remove all script tags
        for script in soup.find_all('script'):
            script.decompose()
        
        # Remove all style tags
        for style in soup.find_all('style'):
            style.decompose()
        
        # Convert relative URLs to absolute
        for a in soup.find_all('a', href=True):
            a['href'] = urljoin(url, a['href'])
        
        cleaned_html = str(soup)
        
        # Remove any remaining problematic characters or patterns
        cleaned_html = re.sub(r'[^\x00-\x7F]+', ' ', cleaned_html)
        
        html_content += f"<h1>URL: {url}</h1>{cleaned_html}<hr>"
    
    html_content += "</body></html>"
    
    result_file = io.BytesIO()
    
    try:
        pdf = pisa.pisaDocument(io.BytesIO(html_content.encode("UTF-8")), result_file)
        
        if not pdf.err:
            with open(output_file, 'wb') as f:
                f.write(result_file.getvalue())
            print(f"PDF created successfully: {output_file}")
        else:
            print(f"Error creating PDF: {pdf.err}")
    except Exception as e:
        print(f"An error occurred while creating the PDF: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Scrape multiple websites and create a PDF.")
    parser.add_argument("urls", nargs='+', help="The base URLs to scrape")
    parser.add_argument("-o", "--output", help="The output PDF file name (default: stdout)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    parser.add_argument("--cache-dir", help="Directory to store the cache (default: ~/.website_to_pdf_cache)")
    parser.add_argument("-d", "--delay", type=float, default=DEFAULT_DELAY, 
                        help=f"Delay between requests in seconds (default: {DEFAULT_DELAY})")
    parser.add_argument("--force-cache", action="store_true", help="Always use cached version if available, ignoring ETag")
    args = parser.parse_args()

    # Determine cache directory
    cache_dir = args.cache_dir or os.environ.get('WEBSITE_TO_PDF_CACHE_DIR') or DEFAULT_CACHE_DIR
    
    if args.verbose:
        print(f"Using cache directory: {cache_dir}", file=sys.stderr)
        print(f"Using delay: {args.delay} seconds", file=sys.stderr)
        if args.force_cache:
            print("Forcing use of cached content when available", file=sys.stderr)

    os.makedirs(cache_dir, exist_ok=True)

    try:
        driver = create_driver()
        session = create_cached_session(cache_dir, force_cache=args.force_cache)
        content = crawl_websites(args.urls, driver=driver, session=session, verbose=args.verbose, delay=args.delay)
        
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
    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    sys.exit(main())