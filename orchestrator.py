# File: orchestrator.py

import argparse
import json
import os
import smtplib
from email.message import EmailMessage

from optimize.optimize_batch_fixed import run_optimizer
from dashboard_generator import build_dashboard


def locate_jobs_file(path):
    """
    Resolve the jobs JSON path by:
      1) checking exactly as given
      2) interpreting relative to cwd
      3) checking under ./scripts/
      4) walking the entire cwd to find the file by name
    """
    # 1) exact path
    if os.path.exists(path):
        return os.path.abspath(path)

    # 2) relative to current working directory
    rel = os.path.join(os.getcwd(), path)
    if os.path.exists(rel):
        return os.path.abspath(rel)

    # 3) under './scripts/' subfolder
    candidate = os.path.join(os.getcwd(), 'scripts', os.path.basename(path))
    if os.path.exists(candidate):
        return os.path.abspath(candidate)

    # 4) recursive search for a matching filename
    basename = os.path.basename(path)
    for root, dirs, files in os.walk(os.getcwd()):
        if basename in files:
            return os.path.abspath(os.path.join(root, basename))

    # not found
    raise FileNotFoundError(
        f"Cannot find jobs file at '{path}' or in 'scripts/' or any subfolder"
    )


def send_email(
    smtp_server,
    port,
    username,
    password,
    to_addrs,
    subject,
    body,
    attachments
):
    """
    Send an email with the given attachments.
    """
    msg = EmailMessage()
    msg["From"]    = username
    msg["To"]      = ", ".join(to_addrs)
    msg["Subject"] = subject
    msg.set_content(body)

    for path in attachments:
        with open(path, 'rb') as f:
            data = f.read()
        msg.add_attachment(
            data,
            maintype="application",
            subtype="octet-stream",
            filename=os.path.basename(path)
        )

    with smtplib.SMTP(smtp_server, port) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(msg)

    print(f"📧 Report emailed to {', '.join(to_addrs)}")


def main():
    parser = argparse.ArgumentParser(
        description="Run batch optimizer, rebuild the HTML dashboard, and email the report"
    )
    parser.add_argument(
        '--jobs-file', required=True,
        help='Path to your jobs_list.json (e.g. jobs_list.json or scripts/jobs_list.json)'
    )
    parser.add_argument(
        '--summary-file', required=True,
        help='Where to write the JSON summary (e.g. optimize_results/orchestrator_summary.json)'
    )
    parser.add_argument(
        '--html-file', default='dashboard.html',
        help='Where to write the HTML dashboard'
    )
    args = parser.parse_args()

    # locate the jobs JSON file anywhere under project
    jobs_path = locate_jobs_file(args.jobs_file)

    # ensure output directory exists for summary
    summary_path = os.path.abspath(args.summary_file)
    os.makedirs(os.path.dirname(summary_path) or '.', exist_ok=True)
    csv_path = os.path.splitext(summary_path)[0] + '.csv'

    # 1) Run optimizer: writes CSV + JSON
    run_optimizer(
        jobs_path,
        output_csv=csv_path,
        output_json=summary_path
    )

    # 2) Load JSON summary & rebuild HTML dashboard
    with open(summary_path, 'r', encoding='utf-8') as f:
        summary = json.load(f)
    build_dashboard(summary, args.html_file)

    print("✅ Orchestration complete:")
    print(f"   • Jobs file:    {jobs_path}")
    print(f"   • JSON summary: {summary_path}")
    print(f"   • CSV output:   {csv_path}")
    print(f"   • HTML file:    {args.html_file}")

    # 3) Send the report via email
    send_email(
        smtp_server="smtp.gmail.com",
        port=587,
        username="kbokit27@gmail.com",
        password="hnpomcrgdcjspqth",
        to_addrs=["kbokit27@gmail.com"],
        subject="Orchestrator Summary Report",
        body=(
            "Hi,\n\n"
            "Please find attached the latest orchestrator summary in JSON, CSV, and HTML formats.\n\n"
            "Best,\nYour Trading Bot"
        ),
        attachments=[summary_path, csv_path, args.html_file]
    )


if __name__ == '__main__':
    main()
