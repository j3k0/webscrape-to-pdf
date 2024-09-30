import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import undetected_chromedriver as uc
from requests_cache import CacheMixin
from requests import Session
import sys

from .config import USER_AGENT, MAX_RETRIES, RETRY_DELAY
from .utils import remove_fragment, is_valid_url, get_robots_parser

class CachedSession(CacheMixin, Session):
    pass

def create_cached_session(cache_dir, force_cache=False):
    session = CachedSession(
        cache_name=cache_dir,
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

def crawl_websites(base_urls, driver=None, session=None, verbose=False, delay=1):
    if driver is None:
        driver = create_driver()
    if session is None:
        session = create_cached_session(cache_dir)

    all_results = []
    for base_url in base_urls:
        robots_parser = get_robots_parser(base_url)
        results = crawl_website(base_url, base_url, driver=driver, session=session, robots_parser=robots_parser, verbose=verbose, delay=delay)
        all_results.extend(results)
    
    return all_results

def crawl_website(base_url, current_url, visited=None, driver=None, session=None, robots_parser=None, verbose=False, delay=1):
    if visited is None:
        visited = set()
    if driver is None:
        driver = create_driver()
    if session is None:
        session = create_cached_session(cache_dir)
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