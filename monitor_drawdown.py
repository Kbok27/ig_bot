# File: monitor_drawdown.py

import os
import time
import argparse
import pandas as pd
import ctypes
import urllib.request
import json
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ------------ Configuration -------------
# Hardcoded SMTP settings for email alerts
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT   = 587
SMTP_USER   = "kbokit27@gmail.com"
SMTP_PASS   = "hnpomcrgdcjspqth"
TO_EMAILS   = ["kbokit27@gmail.com"]

# Optional Slack webhook (leave None to disable)
SLACK_WEBHOOK_URL = None  # e.g. "https://hooks.slack.com/services/XXX/YYY/ZZZ"

# Monitoring parameters
SYMBOLS     = ["BTCUSD.a"]
CONFIGS     = [1]
THRESHOLD   = 5.0    # percent drawdown threshold
INTERVAL    = 60     # seconds between polls
RESULTS_DIR = "results"
# History log file
LOG_FILE    = os.path.join(RESULTS_DIR, "alert_history.json")
# ----------------------------------------


def send_desktop_alert(title: str, message: str):
    """
    Show a Windows desktop alert via MessageBox.
    """
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)


def send_slack_alert(webhook_url: str, message: str):
    """
    Post a message to a Slack Incoming Webhook.
    """
    payload = {'text': message}
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    urllib.request.urlopen(req)


def send_email(smtp_server, port, username, password, to_addrs, subject, body):
    """
    Send an email via SMTP using provided credentials.
    """
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = ", ".join(to_addrs)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(username, password)
        server.sendmail(username, to_addrs, msg.as_string())


def compute_max_drawdown(equity: pd.DataFrame, bal_col: str) -> float:
    """
    Compute max drawdown percentage of an equity curve.
    Returns a negative percentage.
    """
    peak = equity[bal_col].cummax()
    drawdowns = (equity[bal_col] - peak) / peak * 100
    return drawdowns.min()


def log_alert(record: dict):
    """
    Append an alert record to the JSON log file.
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)
    # Load existing log
    if os.path.isfile(LOG_FILE):
        with open(LOG_FILE, 'r') as fp:
            data = json.load(fp)
    else:
        data = []
    # Append and save
    data.append(record)
    with open(LOG_FILE, 'w') as fp:
        json.dump(data, fp, indent=2)


def main():
    print(f"🔔 Monitoring drawdown <= -{THRESHOLD}% every {INTERVAL}s")
    sent = set()

    while True:
        for symbol in SYMBOLS:
            for cfg in CONFIGS:
                path = os.path.join(RESULTS_DIR, f"{symbol}_equity_{cfg}.csv")
                if not os.path.isfile(path):
                    continue

                equity = pd.read_csv(path)
                bal_col = next((c for c in equity.columns if 'balance' in c.lower()), equity.columns[0])
                max_dd = compute_max_drawdown(equity, bal_col)

                key = (symbol, cfg)
                if max_dd <= -THRESHOLD and key not in sent:
                    title = f"Drawdown Alert: {symbol} #{cfg}"
                    message = f"Max drawdown reached {max_dd:.2f}% (threshold {THRESHOLD}%)"
                    print(f"🚨 {title} - {message}")

                    # Desktop popup
                    send_desktop_alert(title, message)

                    # Slack alert
                    if SLACK_WEBHOOK_URL:
                        try:
                            send_slack_alert(SLACK_WEBHOOK_URL, message)
                        except Exception as e:
                            print(f"⚠️ Slack alert failed: {e}")

                    # Email alert
                    try:
                        send_email(
                            smtp_server=SMTP_SERVER,
                            port=SMTP_PORT,
                            username=SMTP_USER,
                            password=SMTP_PASS,
                            to_addrs=TO_EMAILS,
                            subject=title,
                            body=message
                        )
                        print("✅ Email alert sent")
                    except Exception as e:
                        print(f"⚠️ Email alert failed: {e}")

                    # Log alert history
                    record = {
                        'timestamp': datetime.datetime.now().isoformat(),
                        'symbol': symbol,
                        'config': cfg,
                        'drawdown': max_dd
                    }
                    log_alert(record)

                    sent.add(key)
        time.sleep(INTERVAL)

if __name__ == '__main__':
    main()
