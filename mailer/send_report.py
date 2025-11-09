import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email_report(recipient, subject, content):
    """
    Sends an email report via SendGrid.
    """
    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        message = Mail(
            from_email="autofinder247@gmail.com",
            to_emails=recipient,
            subject=subject,
            html_content=content
        )
        response = sg.send(message)
        print(f"✅ Email sent to {recipient} (Status: {response.status_code})")

    except Exception as e:
        print(f"❌ Email sending failed: {e}")
