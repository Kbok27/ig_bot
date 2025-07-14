# File: live_dashboard_watcher.py

import argparse
import subprocess
import sys
import os
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

DEBOUNCE_SECONDS = 2.0

class CsvChangeHandler(PatternMatchingEventHandler):
    def __init__(self, cmd, debounce=DEBOUNCE_SECONDS):
        super().__init__(patterns=["*.csv"], ignore_directories=True)
        self.cmd = cmd
        self.debounce = debounce
        self._last_run = 0

    def on_created(self, event):
        self._run()

    def on_modified(self, event):
        self._run()

    def _run(self):
        now = time.time()
        if now - self._last_run < self.debounce:
            return
        self._last_run = now

        print(f"🔄 Change detected. Regenerating dashboard at {time.strftime('%X')}...")
        try:
            subprocess.run(self.cmd, check=True)
            print("✅ Dashboard regenerated.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error regenerating dashboard: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Watch a results directory and re-run dashboard_generator on CSV changes"
    )
    parser.add_argument(
        '--results-dir', '-r',
        default='results',
        help='Directory containing your CSV result files'
    )
    parser.add_argument(
        '--dashboard-output', '-o',
        default='dashboard.html',
        help='Output HTML filename for the dashboard'
    )
    parser.add_argument(
        '--symbols', '-s',
        nargs='+',
        default=['BTCUSD.a'],
        help='Symbols to pass through to dashboard_generator'
    )
    parser.add_argument(
        '--configs', '-c',
        nargs='+',
        type=int,
        default=[1, 2],
        help='Config indices to pass through to dashboard_generator'
    )
    args = parser.parse_args()

    # Build the command once
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cmd = [
        sys.executable,
        os.path.join(base_dir, 'dashboard_generator.py'),
        '--symbols', *args.symbols,
        '--configs', *map(str, args.configs),
        '--results-dir', args.results_dir,
        '--output', args.dashboard_output
    ]

    event_handler = CsvChangeHandler(cmd)
    observer = Observer()
    observer.schedule(event_handler, path=args.results_dir, recursive=False)
    observer.start()

    print(f"👀 Watching '{args.results_dir}' for CSV changes. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    main()
