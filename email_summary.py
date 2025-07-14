#!/usr/bin/env python3
# email_summary.py

import os
import sys
import smtplib
import sqlite3
import pandas as pd
from email.message import EmailMessage

def load_summary(csv_path):
    # Load the CSV you just generated (opt_summary.csv or test_master_summary.csv)
    return open(csv_path, 'rb').read()

def send_report(smtp_host, smtp_port, username, password,
                sender, recipient, subject, body, attachment_bytes, attachment_name):
    msg = EmailMessage()
    msg['From']    = sender
    msg['To']      = recipient
    msg['Subject'] = subject
    msg.set_content(body)

    # attach the CSV
    msg.add_attachment(attachment_bytes,
                       maintype='text',
                       subtype='csv',
                       filename=attachment_name)

    with smtplib.SMTP(smtp_host, smtp_port) as s:
        s.starttls()                 # comment out if your server doesn’t use TLS
        s.login(username, password)
        s.send_message(msg)
        print(f"✅ Email sent to {recipient}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python email_summary.py path/to/opt_summary.csv")
        sys.exit(1)

    csv_path = sys.argv[1]
    data      = load_summary(csv_path)

    # === CONFIGURE THESE ===
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMPT_USER')      # e.g. your email
    SMTP_PASS = os.getenv('SMPT_PASS')      # your SMTP/app-password
    SENDER    = SMTP_USER
    RECIPIENT = os.getenv('EMAIL_TO', SMTP_USER)
    SUBJECT   = f"Trade Summary {os.path.basename(csv_path)}"
    BODY      = f"Please find attached the latest trade summary ({os.path.basename(csv_path)})."

    if not all([SMTP_USER, SMTP_PASS]):
        print("❌ Please set SMTP_USER and SMTP_PASS environment variables.")
        sys.exit(1)

    send_report(
        smtp_host     = SMTP_HOST,
        smtp_port     = SMTP_PORT,
        username      = SMTP_USER,
        password      = SMTP_PASS,
        sender        = SENDER,
        recipient     = RECIPIENT,
        subject       = SUBJECT,
        body          = BODY,
        attachment_bytes= data,
        attachment_name = os.path.basename(csv_path)
    )

if __name__ == "__main__":
    main()
