import schedule
import time
import datetime
import threading
import json
from flask import Flask, render_template_string, request
from finder.gumtree_scraper import get_gumtree_results
from finder.filters import filter_results
from mailer.send_report import send_email_report
from config.settings import SEARCH_CONFIG
import os

# Upewnij się, że folder 'data' istnieje
os.makedirs("data", exist_ok=True)

app = Flask(__name__)

# ===== PANEL WWW =====
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AutoFinder24/7 Dashboard</title>
<style>
body { background-color: #0d0d0d; color: #d1d1d1; font-family: Arial, sans-serif; }
h1 { color: #4CAF50; }
button { background-color: #4CAF50; color: black; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; }
button:hover { background-color: #66ff66; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; }
th, td { padding: 10px; border-bottom: 1px solid #333; text-align: left; }
tr:hover { background-color: #1a1a1a; }
a { color: #4CAF50; text-decoration: none; }
.rating { font-weight: bold; }
.green { color: #4CAF50; }
.yellow { color: #FFD700; }
.red { color: #ff5050; }
</style>
</head>
<body>
<h1>AutoFinder24/7 — Market Intelligence</h1>
<p>Last updated: {{ timestamp }}</p>
<form method="post" action="/send_email">
<button type="submit">📧 Wyślij testowy e-mail</button>
</form>
<table>
<tr><th>Title</th><th>Price (£)</th><th>Market (£)</th><th>Rating</th><th>Link</th></tr>
{% for r in results %}
<tr>
<td>{{ r['title'] }}</td>
<td>{{ r['price'] }}</td>
<td>{{ r.get('market_price', '-') }}</td>
<td class="rating {% if 'Bargain' in r.get('rating','') %}green{% elif 'Fair' in r.get('rating','') %}yellow{% elif 'Over' in r.get('rating','') %}red{% endif %}">{{ r.get('rating','-') }}</td>
<td><a href="{{ r['url'] }}" target="_blank">View</a></td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def dashboard():
    try:
        with open("data/results.json", "r", encoding="utf-8") as f:
            results = json.load(f)
    except Exception:
        results = []
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template_string(HTML_TEMPLATE, results=results, timestamp=timestamp)

@app.route("/send_email", methods=["POST"])
def manual_send():
    try:
        with open("data/results.json", "r", encoding="utf-8") as f:
            results = json.load(f)
    except:
        results = []
    send_email_report(results)
    return "📨 Testowy e-mail wysłany! Odśwież stronę, aby wrócić."

# ===== HARMONOGRAM =====
def job():
    now = datetime.datetime.now()
    hour = now.hour
    if 8 <= hour < 24:
        print(f"\n🕒 AutoFinder24/7 – uruchomienie {now.strftime('%Y-%m-%d %H:%M:%S')}")
        results = get_gumtree_results(SEARCH_CONFIG)
        filtered = filter_results(results, SEARCH_CONFIG)
        send_email_report(filtered)

        with open("data/results.json", "w", encoding="utf-8") as f:
            json.dump(filtered, f, ensure_ascii=False, indent=4)

        with open("data/logs.txt", "a", encoding="utf-8") as log:
            log.write(f"[{now}] Cykl wykonany, {len(filtered)} wyników\n")

        print("✅ Zakończono cykl.\n")
    else:
        print(f"🌙 {now.strftime('%H:%M')} – czas nocny, pomijam cykl.")

def run_scheduler():
    job()
    schedule.every().hour.do(job)
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=run_scheduler, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)


