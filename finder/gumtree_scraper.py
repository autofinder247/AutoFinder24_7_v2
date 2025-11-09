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
    """Pobiera ogłoszenia samochodowe z Gumtree UK."""
    log_message("🚀 get_gumtree_results() uruchomione!")

    search_url = build_search_url()
    log_message(f"🔍 Używany URL: {search_url}")

    results = []
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        listings = soup.select("li[data-q='search-result']")[:limit]
        log_message(f"📋 Znaleziono {len(listings)} ogłoszeń na stronie.")

        for listing in listings:
            title_elem = listing.select_one("h2 a span")
            price_elem = listing.select_one("strong[data-q='price']")
            link_elem = listing.select_one("a[href*='/classified']")
            city_elem = listing.select_one("div[data-q='location']")

            title = title_elem.text.strip() if title_elem else "No title"
            price = price_elem.text.strip() if price_elem else "No price"
            city = city_elem.text.strip() if city_elem else "Unknown"
            link = (
                BASE_URL + link_elem["href"]
                if link_elem and link_elem.get("href")
                else "No link"
            )

            results.append({
                "title": title,
                "price": price,
                "city": city,
                "link": link
            })

            time.sleep(random.uniform(0.3, 0.7))

        log_message(f"✅ Successfully scraped {len(results)} results.")
        return results

    except Exception as e:
        log_message(f"❌ Error fetching Gumtree data: {e}")
        return []


