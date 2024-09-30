from urllib.parse import urljoin, urlparse, urldefrag
from urllib.robotparser import RobotFileParser

def get_robots_parser(base_url):
    rp = RobotFileParser()
    robots_url = urljoin(base_url, '/robots.txt')
    rp.set_url(robots_url)
    rp.read()
    return rp

def remove_fragment(url):
    return urldefrag(url)[0]

def is_valid_url(base_url, url):
    base_domain = urlparse(base_url).netloc
    url_domain = urlparse(url).netloc
    url_without_fragment = remove_fragment(url)
    return url_domain == base_domain and url_without_fragment.startswith(base_url)