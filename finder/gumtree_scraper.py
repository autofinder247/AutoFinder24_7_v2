import requests
from bs4 import BeautifulSoup
import time
import random

BASE_URL = "https://www.gumtree.com"
SEARCH_URL = "https://www.gumtree.com/search?search_category=cars&search_location=uk"

def get_gumtree_results(limit=20):  
    print("🚀 get_gumtree_results() uruchomione!")
    print(f"🔍 Używany URL: {SEARCH_URL}")
    """Scrapes basic car listings from Gumtree UK."""
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }

    print("🔍 Fetching listings from Gumtree UK...")

    try:
        response = requests.get(SEARCH_URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        listings = soup.select("li.listing-link")[:limit]
        for listing in listings:
            title_elem = listing.select_one("h2.listing-title")
            price_elem = listing.select_one(".listing-price")
            link_elem = listing.select_one("a.listing-link")
            
            title = title_elem.text.strip() if title_elem else "No title"
            price = price_elem.text.strip() if price_elem else "No price"
            link = BASE_URL + link_elem["href"] if link_elem and "href" in link_elem.attrs else "No link"

            results.append({
                "title": title,
                "price": price,
                "link": link
            })

            time.sleep(random.uniform(0.5, 1.0))  # Simulate human-like delay
            
        print(f"✅ Znaleziono {len(results)} wyników.")
        print(f"✅ Successfully scraped {len(results)} results.")
        return results

    except Exception as e:
        print(f"❌ Error fetching Gumtree data: {e}")
        return []


