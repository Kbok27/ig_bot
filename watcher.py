# File: watcher.py

import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Path to watch
RESULTS_DIR = Path(__file__).parent / "results"
# Minimum seconds between triggers (to debounce rapid file writes)
DEBOUNCE_SECONDS = 1

class ResultsChangeHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self._last_run = 0

    def on_any_event(self, event):
        # Ignore directory events
        if event.is_directory:
            return

        now = time.time()
        if now - self._last_run < DEBOUNCE_SECONDS:
            return
        self._last_run = now

        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Change detected: {event.src_path}")
        # Call your dashboard generator (adjust command if needed)
        try:
            subprocess.run(
                ["python", "dashboard_generator.py"],
                check=True
            )
            print("✅ Dashboard regenerated successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error regenerating dashboard: {e}")

def main():
    # Ensure the results directory exists
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    event_handler = ResultsChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, str(RESULTS_DIR), recursive=False)
    observer.start()

    print(f"Watching '{RESULTS_DIR}' for changes. Press Enter to exit.")
    try:
        input()
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
        print("Watcher stopped.")

if __name__ == "__main__":
    main()
