import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config.settings import EMAIL_SETTINGS

def send_email_report(results):
    """Wysyła e-mail z raportem wyników."""
    try:
        html_content = "<h3>AutoFinder24/7 – Raport wyników</h3>"
        if results:
            html_content += "<ul>"
            for r in results:
                html_content += f"<li><a href='{r['url']}'>{r['title']}</a> – {r['price']}</li>"
            html_content += "</ul>"
        else:
            html_content += "<p>Brak nowych wyników.</p>"

        message = Mail(
            from_email=EMAIL_SETTINGS["sender"],
            to_emails=EMAIL_SETTINGS["recipient"],
            subject=EMAIL_SETTINGS["subject"],
            html_content=html_content
        )

        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(message)
        print("📨 Raport e-mail został wysłany.")
    except Exception as e:
        print(f"❌ Błąd podczas wysyłania e-maila: {e}")
