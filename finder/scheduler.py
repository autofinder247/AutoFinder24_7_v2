import schedule
import time
import datetime
from finder.gumtree_scraper import get_gumtree_results
from finder.filters import filter_results
from email.send_report import send_email_report
from config.settings import SEARCH_CONFIG, EMAIL_SETTINGS, SCHEDULE

def run_cycle():
    """
    Runs one scraping + filtering + emailing cycle.
    """
    now = datetime.datetime.now()
    hour = now.hour
    start = SCHEDULE["start_hour"]
    end = SCHEDULE["end_hour"]

    if start <= hour <= end:
        print(f"\n🕒 AutoFinder24/7 cycle started at {now.strftime('%Y-%m-%d %H:%M:%S')}")

        results = get_gumtree_results(SEARCH_CONFIG["max_results"])
        filtered = filter_results(
            results,
            min_price=SEARCH_CONFIG["min_price"],
            max_price=SEARCH_CONFIG["max_price"],
            keywords=SEARCH_CONFIG["keywords"]
        )

        # Format e-mail
        html_content = "<h3>AutoFinder24/7 — New Car Deals</h3><ul>"
        for r in filtered:
            html_content += f"<li><a href='{r['link']}'>{r['title']}</a> — {r['price']}</li>"
        html_content += "</ul>"

        send_email_report(
            recipient=EMAIL_SETTINGS["recipient"],
            subject=EMAIL_SETTINGS["subject"],
            content=html_content
        )

        print(f"✅ Cycle finished. Sent {len(filtered)} results.\n")

    else:
        print(f"🌙 {hour}:00 — Night hours, skipping cycle.")

def start_scheduler():
    """
    Sets up the automatic schedule.
    """
    interval = SCHEDULE["interval_minutes"]
    print(f"🕓 Scheduler active — interval: {interval} min (from {SCHEDULE['start_hour']}:00 to {SCHEDULE['end_hour']}:00)")

    run_cycle()
    schedule.every(interval).minutes.do(run_cycle)

    while True:
        schedule.run_pending()
        time.sleep(60)
