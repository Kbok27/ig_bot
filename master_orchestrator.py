# File: master_orchestrator.py

import argparse
import subprocess
import sys
from pathlib import Path

def run_optimizer(jobs_file: Path, trades_csv: Path, summary_json: Path):
    cmd = [
        sys.executable, "-m", "optimize.optimize_batch_extended_v2",
        "--jobs-file", str(jobs_file),
        "--output-csv", str(trades_csv),
        "--output-json", str(summary_json),
    ]
    print(f">>> Running optimizer: {' '.join(cmd)}")
    subprocess.check_call(cmd)

def export_stats(stats_dir: Path):
    cmd = [sys.executable, "export_stats.py", "--stats-dir", str(stats_dir)]
    print(f">>> Exporting stats: {' '.join(cmd)}")
    subprocess.check_call(cmd)

def generate_dashboards():
    # Your existing dashboard_generator call, e.g.:
    cmd = [sys.executable, "dashboard_generator.py"]
    print(f">>> Generating dashboards: {' '.join(cmd)}")
    subprocess.check_call(cmd)

def main():
    p = argparse.ArgumentParser(description="Master orchestrator")
    p.add_argument("--jobs-file",   required=True, help="Path to jobs JSON")
    p.add_argument("--trades-csv",  required=True, help="Where to write trades CSV")
    p.add_argument("--summary-json",required=True, help="Where to write summary JSON")
    p.add_argument("--stats-dir",   default="results", help="Folder for stats JSON")
    args = p.parse_args()

    jobs_file    = Path(args.jobs_file)
    trades_csv   = Path(args.trades_csv)
    summary_json = Path(args.summary_json)
    stats_dir    = Path(args.stats_dir)

    # 1) Run the batch optimizer
    run_optimizer(jobs_file, trades_csv, summary_json)

    # 2) Re-export all stats JSON for dashboard filtering
    export_stats(stats_dir)

    # 3) Generate fresh dashboard PNGs and HTML
    generate_dashboards()

    print("✅ Orchestration complete.")

if __name__ == "__main__":
    main()
