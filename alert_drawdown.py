# File: alert_drawdown.py

import json
import smtplib
import os
from pathlib import Path
from email.message import EmailMessage
from typing import List
import requests  # make sure you have this installed if using Slack

# ── CONFIGURATION ─────────────────────────────────────────────────────────────
RESULTS_DIR       = Path("results")
DRAWDOWN_LIMIT    = float(os.getenv("DRAWDOWN_ALERT_LIMIT", 0.1))  # 0.1 = 10%
SMTP_SERVER       = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT         = int(os.getenv("SMTP_PORT", 587))
SMTP_USER         = os.getenv("SMTP_USER", "you@example.com")
SMTP_PASS         = os.getenv("SMTP_PASS", "yourpassword")
ALERT_TO          = os.getenv("ALERT_TO", "you@example.com")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", None)  # e.g. "https://hooks.slack.com/…"

# ── EMAIL / SLACK HELPERS ──────────────────────────────────────────────────────
def send_email(smtp_server: str,
               port: int,
               username: str,
               password: str,
               to_addrs: List[str],
               subject: str,
               body: str):
    msg = EmailMessage()
    msg["From"]    = username
    msg["To"]      = ", ".join(to_addrs)
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(smtp_server, port) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(msg)

def send_slack(text: str):
    if not SLACK_WEBHOOK_URL:
        return
    requests.post(SLACK_WEBHOOK_URL, json={"text": text})

# ── MAIN ALERT ROUTINE ─────────────────────────────────────────────────────────
def run_alerts():
    alerts = []
    for stats_file in RESULTS_DIR.glob("*_stats.json"):
        stats = json.loads(stats_file.read_text())
        dd = stats.get("max_drawdown", 0.0)
        if dd >= DRAWDOWN_LIMIT:
            symbol = stats_file.stem.replace("_stats", "")
            alerts.append((symbol, dd))

    if not alerts:
        print("✅ No drawdown breaches.")
        return

    # Build alert message
    lines = [f"{sym}: drawdown {dd*100:.1f}% ≥ {DRAWDOWN_LIMIT*100:.1f}%"
             for sym, dd in alerts]
    body = "⚠️ Drawdown Alerts:\n\n" + "\n".join(lines)
    subject = f"Drawdown Alert: {len(alerts)} symbol(s) breached"

    # Send notifications
    send_email(
        SMTP_SERVER, SMTP_PORT,
        SMTP_USER, SMTP_PASS,
        [ALERT_TO],
        subject, body
    )
    print("✉️  Email alert sent.")
    send_slack(body)
    if SLACK_WEBHOOK_URL:
        print("📨 Slack alert sent.")

if __name__ == "__main__":
    run_alerts()
