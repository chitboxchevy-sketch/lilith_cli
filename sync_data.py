import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# The folder we want to watch
WATCH_PATH = "./personal_data"

class SyncHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            print(f"🔄 Change detected in {event.src_path}. Syncing to GitHub...")
            self.sync()

    def sync(self):
        try:
            # Stage, commit, and push the data folder
            subprocess.run(["git", "add", "personal_data/"], check=True)
            subprocess.run(["git", "commit", "-m", "Auto-sync personal data"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("✅ Data successfully pushed to GitHub.")
        except Exception as e:
            print(f"❌ Sync failed: {e}")

if __name__ == "__main__":
    event_handler = SyncHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_PATH, recursive=True)
    observer.start()
    print(f"👀 Watching {WATCH_PATH} for changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
