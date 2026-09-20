import time
import httpx
from bs4 import BeautifulSoup
from app.core.cache import scrape_cache

ORDERING_KEYWORDS = ["order online", "order now", "delivery", "zomato", "swiggy"]
MENU_KEYWORDS = ["menu", "price", "₹", "rs.", "inr"]
CONTACT_KEYWORDS = ["contact", "phone", "email", "address"]


def fetch(url: str) -> str | None:
    cached = scrape_cache.get(url)
    if cached is not None:
        return cached
    try:
        start = time.time()
        response = httpx.get(url, timeout=10, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
        elapsed_ms = int((time.time() - start) * 1000)
        html = response.text
        scrape_cache.set(url, (html, elapsed_ms))
        return (html, elapsed_ms)
    except Exception:
        return None


def analyze(fetch_result) -> dict:
    if not fetch_result:
        return {
            "has_online_ordering": None,
            "has_menu_pricing": None,
            "mobile_friendly": None,
            "seo_title": None,
            "seo_description": None,
            "contact_info_present": None,
            "load_time_ms": None,
            "fetch_failed": True,
        }
    html, load_time_ms = fetch_result
    soup = BeautifulSoup(html, "html.parser")
    text_lower = soup.get_text().lower()

    title_tag = soup.find("title")
    description_tag = soup.find("meta", attrs={"name": "description"})
    viewport_tag = soup.find("meta", attrs={"name": "viewport"})

    return {
        "has_online_ordering": any(k in text_lower for k in ORDERING_KEYWORDS),
        "has_menu_pricing": any(k in text_lower for k in MENU_KEYWORDS),
        "mobile_friendly": viewport_tag is not None,
        "seo_title": title_tag.get_text().strip() if title_tag else None,
        "seo_description": description_tag.get("content").strip() if description_tag and description_tag.get("content") else None,
        "contact_info_present": any(k in text_lower for k in CONTACT_KEYWORDS),
        "load_time_ms": load_time_ms,
        "fetch_failed": False,
    }
