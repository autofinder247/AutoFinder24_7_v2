import requests
from bs4 import BeautifulSoup
import time
import random
import os
from datetime import datetime
from config.settings import SEARCH_CONFIG

BASE_URL = "https://www.gumtree.com"
LOG_FILE = "data/logs.txt"

def log_message(message):
    """Zapisuje komunikaty diagnostyczne do pliku logów"""
    os.makedirs("data", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def build_search_url():
    """Tworzy dynamiczny adres URL na podstawie SEARCH_CONFIG."""
    location = SEARCH_CONFIG.get("location", "united-kingdom").replace(" ", "-")
    min_price = SEARCH_CONFIG.get("min_price", 0)
    max_price = SEARCH_CONFIG.get("max_price", 10000)
    keywords = "+".join(SEARCH_CONFIG.get("keywords", []))

    url = (
        f"{BASE_URL}/search?search_category=cars"
        f"&search_location={location}"
        f"&min_price={min_price}"
        f"&max_price={max_price}"
    )
    if keywords:
        url += f"&q={keywords}"
    return url


def get_gumtree_results(limit=20):
    """Scrapes basic car listings from Gumtree UK."""
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0 Safari/537.36"
    }

    print("🔍 Fetching listings from Gumtree UK...")

    try:
        search_url = build_search_url()
        response = requests.get(search_url, headers=headers, timeout=10)

        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Nowa struktura Gumtree: każdy listing to <article> z a[href*='/p/cars/']
        listings = soup.select("article a[href*='/p/cars/']")[:limit]

        for link_elem in listings:
            title = link_elem.get_text(strip=True)
            link = link_elem["href"]
            if not link.startswith("http"):
                link = BASE_URL + link

            # Cena jest często w sąsiednim <span>
            parent = link_elem.find_parent("article")
            price_elem = parent.select_one("span[data-testid='listing-price']") if parent else None
            price = price_elem.get_text(strip=True) if price_elem else "No price"

            results.append({
                "title": title,
                "price": price,
                "link": link
            })

            time.sleep(random.uniform(0.5, 1.0))

        print(f"✅ Successfully scraped {len(results)} results.")
        return results

    except Exception as e:
        print(f"❌ Error fetching Gumtree data: {e}")
        return []




