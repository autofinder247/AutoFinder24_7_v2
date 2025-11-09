def filter_results(results, min_price=1000, max_price=8000, keywords=None):
    """
    Filters scraped Gumtree car results based on price range and keywords.
    """
    if not results:
        print("⚠️ No results to filter.")
        return []

    filtered = []
    keywords = [kw.lower() for kw in (keywords or [])]

    for car in results:
        try:
            price_text = ''.join([c for c in car['price'] if c.isdigit()])
            price = int(price_text) if price_text else 0

            if price < min_price or price > max_price:
                continue

            title = car["title"].lower()
            if keywords and not any(kw in title for kw in keywords):
                continue

            filtered.append(car)

        except Exception as e:
            print(f"⚠️ Error filtering car: {e}")

    print(f"✅ Filtered {len(filtered)} cars between £{min_price} - £{max_price}.")
    return filtered
