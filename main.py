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

@app.route("/update_config", methods=["POST"])
def update_config():
    data = request.form
    from config.settings import SEARCH_CONFIG

    SEARCH_CONFIG["location"] = data.get("location", "United Kingdom")
    SEARCH_CONFIG["min_price"] = int(data.get("min_price", 1000))
    SEARCH_CONFIG["max_price"] = int(data.get("max_price", 8000))
    SEARCH_CONFIG["keywords"] = [kw.strip() for kw in data.get("keywords", "").split(",") if kw.strip()]

    with open("config/settings.py", "w", encoding="utf-8") as f:
        f.write("SEARCH_CONFIG = " + json.dumps(SEARCH_CONFIG, indent=4))
    return render_template_string("<h3>✅ Ustawienia zapisane.</h3><a href='/'>⬅️ Wróć</a>")

# Upewnij się, że folder 'data' istnieje
os.makedirs("data", exist_ok=True)

app = Flask(__name__)

import json
import os

CONFIG_FILE = "data/config.json"

# Upewnij się, że plik istnieje
os.makedirs("data", exist_ok=True)
if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "location": "United Kingdom",
            "min_price": 1000,
            "max_price": 8000,
            "keywords": ["polo", "fiesta", "corsa", "ibiza", "micra"],
            "max_results": 30
        }, f, indent=4)

# Strona konfiguracji
@app.route("/config", methods=["GET", "POST"])
def config_page():
    if request.method == "POST":
        location = request.form.get("location")
        min_price = int(request.form.get("min_price"))
        max_price = int(request.form.get("max_price"))
        keywords = [k.strip() for k in request.form.get("keywords").split(",") if k.strip()]

        config = {
            "location": location,
            "min_price": min_price,
            "max_price": max_price,
            "keywords": keywords,
            "max_results": 30
        }

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        return "✅ Settings saved! Refresh page to continue."

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    return render_template_string("""
    <h2>🔧 AutoFinder24/7 – Search Config</h2>
    <form method="POST">
        <label>Location:</label><br>
        <input type="text" name="location" value="{{config.location}}"><br><br>

        <label>Min price:</label><br>
        <input type="number" name="min_price" value="{{config.min_price}}"><br><br>

        <label>Max price:</label><br>
        <input type="number" name="max_price" value="{{config.max_price}}"><br><br>

        <label>Keywords (comma-separated):</label><br>
        <input type="text" name="keywords" value="{{ ', '.join(config.keywords) }}"><br><br>

        <button type="submit">💾 Save settings</button>
    </form>
    """, config=config)

# ===== PANEL WWW =====
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>AutoFinder24/7 — Dashboard</title>
    <style>
        body {
            background-color: #0d0d0d;
            color: #d1d1d1;
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: row;
            height: 100vh;
            margin: 0;
        }
        .sidebar {
            width: 300px;
            background: #111;
            padding: 20px;
            box-shadow: 2px 0 5px rgba(0,0,0,0.5);
        }
        .content {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }
        h1 {
            color: #4CAF50;
            margin-top: 0;
        }
        label {
            display: block;
            margin-top: 10px;
            font-weight: bold;
        }
        input[type="text"], input[type="number"] {
            width: 100%;
            padding: 5px;
            margin-top: 5px;
            background: #222;
            border: 1px solid #333;
            color: #eee;
        }
        button {
            display: block;
            width: 100%;
            margin-top: 15px;
            padding: 10px;
            border: none;
            cursor: pointer;
            font-weight: bold;
            border-radius: 5px;
        }
        button:hover { opacity: 0.9; }
        .btn-refresh { background: #9C27B0; color: white; }
        .btn-email { background: #2196F3; color: white; }
        .btn-save { background: #4CAF50; color: white; }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 10px;
            border-bottom: 1px solid #333;
            text-align: left;
        }
        th { color: #4CAF50; }
        a { color: #4CAF50; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="sidebar">
        <h1>AutoFinder24/7</h1>
        <form method="POST" action="/update_config">
            <label>📍 Lokalizacja</label>
            <input type="text" name="location" value="{{ config['location'] }}">
            <label>💷 Cena minimalna</label>
            <input type="number" name="min_price" value="{{ config['min_price'] }}">
            <label>💷 Cena maksymalna</label>
            <input type="number" name="max_price" value="{{ config['max_price'] }}">
            <label>🔍 Słowa kluczowe (oddziel przecinkami)</label>
            <input type="text" name="keywords" value="{{ ', '.join(config['keywords']) }}">
            <button type="submit" class="btn-save">💾 Zapisz ustawienia</button>
        </form>
        <form method="POST" action="/refresh_data">
            <button type="submit" class="btn-refresh">🌀 Odśwież dane</button>
        </form>
        <form method="POST" action="/send_email">
            <button type="submit" class="btn-email">✉️ Wyślij testowy e-mail</button>
        </form>
    </div>
    <div class="content">
        <h2>📊 Wyniki wyszukiwania</h2>
        <p>Ostatnia aktualizacja: {{ timestamp }}</p>
        <table>
            <tr><th>Tytuł</th><th>Cena (£)</th><th>Miasto</th><th>Link</th></tr>
            {% for r in results %}
            <tr>
                <td>{{ r['title'] }}</td>
                <td>{{ r['price'] }}</td>
                <td>{{ r['location'] }}</td>
                <td><a href="{{ r['url'] }}" target="_blank">Otwórz</a></td>
            </tr>
            {% endfor %}
        </table>
    </div>
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




