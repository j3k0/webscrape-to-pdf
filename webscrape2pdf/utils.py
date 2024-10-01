from urllib.parse import urljoin, urlparse, urldefrag, parse_qs
from urllib.robotparser import RobotFileParser

def get_robots_parser(base_url):
    rp = RobotFileParser()
    robots_url = urljoin(base_url, '/robots.txt')
    rp.set_url(robots_url)
    rp.read()
    return rp

def remove_fragment(url):
    return urldefrag(url)[0]

def is_wikimedia_site(url, logged_in_domains):
    wikimedia_domains = [
        'wikipedia.org',
        'wikimedia.org',
        'wiktionary.org',
        'wikiquote.org',
        'wikibooks.org',
        'wikisource.org',
        'wikinews.org',
        'wikiversity.org',
        'wikidata.org',
        'wikivoyage.org',
        'mediawiki.org'
    ]
    domain = urlparse(url).netloc
    return any(domain.endswith(wiki_domain) for wiki_domain in wikimedia_domains) or domain in logged_in_domains

def is_valid_url(base_url, url, logged_in_domains):
    base_domain = urlparse(base_url).netloc
    url_domain = urlparse(url).netloc
    url_without_fragment = remove_fragment(url)
    
    # Parse the query string
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    # If it's a Wikimedia site (including logged-in domains)
    if is_wikimedia_site(url, logged_in_domains):
        # Ignore if it has any query parameters
        if query_params:
            return False
        # Ignore if the URL contains "Special:"
        if "Special:" in parsed_url.path:
            return False
    
    # Allow image URLs
    if url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
        return False
    
    return url_domain == base_domain and url_without_fragment.startswith(base_url)