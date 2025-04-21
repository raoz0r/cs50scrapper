import time
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from .utils import normalize_url

RETRY_COUNT = 3
RETRY_DELAY = 10 # seconds

def fetch_and_parse(url):

    # Fetch the URL (with retries) and parse into hierarchical dict.

    last_exc = None
    for attempt in range(1, RETRY_COUNT +1):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            html = resp.text
            break
        except Exception as e:
            last_exc = e
            print(f"[Attempt {attempt}] Error Fecthing {url}: {e}") # TODO Log it '#error-handling'
            if attempt < RETRY_COUNT:
                time.sleep(RETRY_DELAY) 
    else:
        raise last_exc
    
    soup = BeautifulSoup(html, "html.parser")
    # Extract <h1> title text and sanitized id

    h1 = soup.find("h1")
    if not h1:
        raise RuntimeError("No <h1> found on page") # TODO Log it '#error-handling'
    
    # e.g <a href="#week-0-functions"><em>Functions</em></a>

    anchor = h1.find("a", href=True)
    raw = anchor["href"].lstrip("#") if anchor else h1.get_text().strip()
    title = raw.replace(" ", "-").lower()

    # Build Hierachy from the first top-level list (<ul> or <ol>) after <h1>

    container = h1.find_next_sibling(["ul", "ol"])
    structure = {"title": title}
    if container:
        structure["content"] = _parse_list(container, url)
    else:
        structure["content"] = {}

    return structure

def _parse_list(node, base_url):

    # Recursively parse a <ul> or <ol> into a list of dicts: [{"label": "...", "url": "...", "children": [...]}, ...]
    items = []

    for li in node.find_all("li", recursive=False):
        entry = {}

        # label: if there's text before a nested list or link

        text = li.get_text(strip=True)
        entry["label"] = text

        # links in this <li> (only top-level)

        a = li.find("a", href=True)
        if a:
            href = normalize_url(urljoin(base_url, a["href"]))
            entry["url"] = href
        
        # children: any nested <ul> or <ol>

        child_list = li.find(["ul", "ol"], recursive=False)
        if child_list:
            entry["children"] = _parse_list(child_list, base_url)
        
        items.append(entry)
    return items



# Signature: requests.get(url, params=None, **kwargs) -> Response
# Docs: https://docs.python-requests.org/en/master/api/#requests.get

# Signature: urljoin(base: str, url: str) -> str
# Docs: https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urljoin

# Signature: find(name=None, attrs={}, recursive=True, text=None, **kwargs)
# Docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find

# Signature: Response.raise_for_status() -> None
# Docs: https://docs.python-requests.org/en/master/api/#requests.Response.raise_for_status

# Signature: BeautifulSoup(markup, parser) -> BeautifulSoup
# Docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/#beautifulsoup

# Docs: https://docs.python.org/3/library/time.html#time.sleep