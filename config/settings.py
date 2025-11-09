import os
from datetime import time

# ===================================
# 🔧 PODSTAWOWA KONFIGURACJA
# ===================================

SEARCH_CONFIG = {
    "location": "United Kingdom",
    "min_price": 1000,
    "max_price": 8000,
    "keywords": ["polo", "fiesta", "corsa", "ibiza", "micra"],
    "max_results": 30
}

# ===================================
# 📩 EMAIL USTAWIENIA
# ===================================

EMAIL_SETTINGS = {
    "sender": "autofinder247@gmail.com",
    "recipient": "autofinder247@gmail.com",
    "subject": "AutoFinder24/7 — Daily UK Car Listings Report"
}

# ===================================
# 🕐 HARMONOGRAM (CZAS UK)
# ===================================

SCHEDULE = {
    "start_hour": 8,
    "end_hour": 23,
    "interval_minutes": 180  # co 3 godziny
}

# ===================================
# 🔐 API KEY (pobierany automatycznie z Render lub środowiska lokalnego)
# ===================================

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
