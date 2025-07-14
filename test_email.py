# File: test_email.py

import smtplib
from email.message import EmailMessage
from typing import List

def send_email(smtp_server: str,
               port: int,
               username: str,
               password: str,
               to_addrs: List[str],
               subject: str,
               body: str):
    """
    Send a simple plain-text email.
    """
    msg = EmailMessage()
    msg["From"]    = username
    msg["To"]      = ", ".join(to_addrs)
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(smtp_server, port) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(msg)
    print("✅ Test email sent!")

if __name__ == "__main__":
    send_email(
        smtp_server="smtp.gmail.com",
        port=587,
        username="kbokit27@gmail.com",
        password="hnpomcrgdcjspqth",
        to_addrs=["kbokit27@gmail.com"],
        subject="🔔 Test Alert from Your Trading Bot",
        body=(
            "Hello Brent,\n\n"
            "This is a test email from your live dashboard/alert system.\n"
            "If you’re seeing this, your send_email configuration is working!\n\n"
            "– Your Trading Bot"
        )
    )
