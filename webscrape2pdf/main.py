#!/usr/bin/env python3

from .cli import parse_arguments
from .scraper import crawl_websites, create_driver, create_cached_session
from .pdf_generator import create_pdf
from .config import DEFAULT_CACHE_DIR
import os
import sys

def main():
    args = parse_arguments()

    # Determine cache directory
    cache_dir = args.cache_dir or os.environ.get('WEBSITE_TO_PDF_CACHE_DIR') or DEFAULT_CACHE_DIR
    
    if args.verbose:
        print(f"Using cache directory: {cache_dir}", file=sys.stderr)
        print(f"Using delay: {args.delay} seconds", file=sys.stderr)
        if args.force_cache:
            print("Forcing use of cached content when available", file=sys.stderr)
        if args.use_selenium:
            print("Using Selenium for JavaScript-rendered content", file=sys.stderr)

    os.makedirs(cache_dir, exist_ok=True)

    try:
        driver = create_driver() if args.use_selenium else None
        session = create_cached_session(cache_dir, force_cache=args.force_cache)
        content = crawl_websites(args.urls, driver=driver, session=session, verbose=args.verbose, delay=args.delay, use_selenium=args.use_selenium)
        
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
        if 'driver' in locals() and driver:
            driver.quit()

if __name__ == "__main__":
    sys.exit(main())