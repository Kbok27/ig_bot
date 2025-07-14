import os
import smtplib
from email.message import EmailMessage
from slack_sdk import WebClient

# Slack configuration (set these env vars in your shell)
SLACK_TOKEN   = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#trading-bot")
slack_client  = WebClient(token=SLACK_TOKEN)

def slack_alert(text: str):
    """
    Send a Slack message to SLACK_CHANNEL.
    """
    try:
        slack_client.chat_postMessage(channel=SLACK_CHANNEL, text=text)
    except Exception as e:
        print(f"[⚠️] Slack alert failed: {e}")

# Email configuration (set these env vars in your shell)
EMAIL_HOST = os.getenv("SMTP_HOST")
EMAIL_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USER = os.getenv("SMTP_USER")
EMAIL_PASS = os.getenv("SMTP_PASS")
EMAIL_TO   = os.getenv("ALERT_EMAIL_TO")

def email_alert(subject: str, body: str):
    """
    Send an email alert via SMTP.
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"]    = EMAIL_USER
    msg["To"]      = EMAIL_TO
    msg.set_content(body)
    try:
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
    except Exception as e:
        print(f"[⚠️] Email alert failed: {e}")
