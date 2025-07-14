# File: serve_dashboard_tray.py

"""
Standalone Dashboard Tray App with Logging, Alerts, Export & Email Integration
Dependencies:
  pip install watchdog pystray pillow plyer
Package with PyInstaller:
  pyinstaller --onefile --windowed serve_dashboard_tray.py
"""

import os
import sys
import argparse
import threading
import time
import subprocess
import logging
import json
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

import pandas as pd
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import pystray
from PIL import Image, ImageDraw
from plyer import notification
from email_summary import send_report
import dashboard_generator as dg

# Constants
DEBOUNCE_SECONDS = 2.0
PORT = 8000
RESULTS_DIR = 'results'
SYMBOLS = ['BTCUSD.a']
CONFIGS = [1, 2]
DASHBOARD_OUTPUT = 'dashboard.html'
LOG_FILE = 'dashboard_tray.log'
ALERTS_FILE = 'alerts.json'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)


def load_alerts():
    if not os.path.isfile(ALERTS_FILE):
        logging.warning("No alerts.json found — skipping alerts.")
        return {}
    with open(ALERTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_overall_metrics():
    lst = []
    for sym in SYMBOLS:
        for idx in CONFIGS:
            tfile = os.path.join(RESULTS_DIR, f"{sym}_result_{idx}.csv")
            efile = os.path.join(RESULTS_DIR, f"{sym}_equity_{idx}.csv")
            if os.path.exists(tfile) and os.path.exists(efile):
                trades = pd.read_csv(tfile)
                equity = pd.read_csv(efile)
                lst.append(dg.compute_metrics(trades, equity))
    if not lst:
        return {}
    return {
        'total_trades':  sum(m['total_trades'] for m in lst),
        'total_profit':  sum(m['total_profit'] for m in lst),
        'win_rate':      sum(m['win_rate'] for m in lst) / len(lst),
        'avg_win':       sum(m['avg_win'] for m in lst) / len(lst),
        'avg_loss':      sum(m['avg_loss'] for m in lst) / len(lst),
        'max_drawdown':  min(m['max_drawdown'] for m in lst),
        'sharpe':        sum(m['sharpe'] for m in lst) / len(lst)
    }


def notify_alert(method, key, val, thr, cond):
    msg = f"{key} {cond} {thr} (current: {val:.2f})"
    title = "Trading Dashboard Alert"
    if method == "desktop":
        notification.notify(title=title, message=msg, timeout=8)
    elif method == "email":
        send_report(
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            username="kbokit27@gmail.com",
            password="hnpomcrgdcjspqth",
            sender="kbokit27@gmail.com",
            recipient="kbokit27@gmail.com",
            subject=title,
            body=msg,
            attachment_bytes=b"",
            attachment_name="alert.txt"
        )
    logging.info(f"Alert fired ({method}): {msg}")


def check_alerts():
    alerts = load_alerts()
    if not alerts:
        return
    metrics = compute_overall_metrics()
    for key, rule in alerts.items():
        val = metrics.get(key)
        if val is None:
            continue
        cond = rule.get("condition")
        thr = rule.get("threshold")
        method = rule.get("method")
        if (cond == ">" and val > thr) or (cond == "<" and val < thr):
            notify_alert(method, key, val, thr, cond)


class CsvHandler(PatternMatchingEventHandler):
    def __init__(self, cmd):
        super().__init__(patterns=["*.csv"], ignore_directories=True)
        self.cmd = cmd
        self._last = 0

    def on_any_event(self, event):
        now = time.time()
        if now - self._last < DEBOUNCE_SECONDS:
            return
        self._last = now
        logging.info(f"Detected CSV change: {event.src_path}")
        try:
            subprocess.run(self.cmd, check=True)
            logging.info("Dashboard regenerated successfully.")
            check_alerts()
        except subprocess.CalledProcessError as e:
            logging.error(f"Error regenerating dashboard: {e}")


def create_tray_icon(server_thread, observer):
    img = Image.new('RGB', (64, 64), color='white')
    d = ImageDraw.Draw(img)
    d.rectangle([16, 16, 48, 48], outline='black', width=2)
    def shutdown_all():
        logging.info("Shutting down (via Quit)...")
        observer.stop(); server_thread.shutdown(); icon.stop()
    def on_quit(icon_obj, item): shutdown_all()
    menu = pystray.Menu(pystray.MenuItem('Quit', on_quit))
    icon = pystray.Icon('dashboard', img, 'Dashboard', menu)
    icon.run()


class HTTPServerThread(threading.Thread):
    def __init__(self, directory, port):
        super().__init__(daemon=True)
        self.directory = directory; self.port = port; self._orig = os.getcwd()
    def run(self):
        os.chdir(self.directory)
        self.httpd = TCPServer(("", self.port), SimpleHTTPRequestHandler)
        logging.info(f"Starting HTTP on {self.port}")
        try: self.httpd.serve_forever()
        finally: os.chdir(self._orig)
    def shutdown(self): self.httpd.shutdown()


def export_json():
    base = os.path.dirname(os.path.abspath(__file__))
    cmd = [sys.executable,
           os.path.join(base,'dashboard_generator.py'),
           '--symbols', *SYMBOLS,
           '--configs', *map(str,CONFIGS),
           '--results-dir', RESULTS_DIR,
           '--output', DASHBOARD_OUTPUT]
    subprocess.run(cmd, check=True)
    json_path = os.path.splitext(DASHBOARD_OUTPUT)[0] + '.json'
    print(f"✅ Data export written: {json_path}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dashboard Tray App')
    parser.add_argument('command', nargs='?', choices=['serve','export_json'], default='serve')
    args = parser.parse_args()

    if args.command == 'export_json':
        export_json(); sys.exit(0)

    # Build and start CSV watcher
    base = os.path.dirname(os.path.abspath(__file__))
    cmd = [sys.executable, os.path.join(base,'dashboard_generator.py'),
           '--symbols', *SYMBOLS,'--configs', *map(str,CONFIGS),
           '--results-dir', RESULTS_DIR,'--output', DASHBOARD_OUTPUT]
    observer = Observer(); handler = CsvHandler(cmd)
    observer.schedule(handler, path=RESULTS_DIR, recursive=False)
    observer.start(); logging.info(f"Watching '{RESULTS_DIR}' for CSV changes.")

    # Initial build + alerts
    try: subprocess.run(cmd, check=True); logging.info("Initial dashboard generated."); check_alerts()
    except Exception as e: logging.error(f"Init build error: {e}")

    # HTTP server + tray icon
    server = HTTPServerThread(base, PORT); server.start()
    print(f"📡 Serving HTTP on port {PORT}.")
    print(f"🔗 http://localhost:{PORT}/{DASHBOARD_OUTPUT}")
    create_tray_icon(server, observer)
    observer.join(); logging.info("Exited.")
