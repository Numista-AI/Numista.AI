import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

# --- CONFIGURATION ---
INBOX_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Numista_Brain_Inbox"
LOG_FILE = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\brain_watcher.log"

# Images dropped this sprint — no absorb_image() exists yet.
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.xls', '.md', '.csv', '.json'}

# Directories whose contents are never processed, regardless of depth.
_EXCLUDE_DIR_NAMES = {"Brain Sorter", "_absorbed", "node_modules", "__pycache__"}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)


class BrainInboxHandler(FileSystemEventHandler):

    def _should_process(self, event) -> bool:
        """Shared gate for on_created and on_modified."""
        if event.is_directory:
            return False
        file_path = Path(event.src_path)
        if any(part in _EXCLUDE_DIR_NAMES for part in file_path.parts):
            return False
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return False
        return True

    def on_created(self, event):
        if self._should_process(event):
            logging.info(f"on_created: {Path(event.src_path).name}")
            self.process_file(Path(event.src_path))

    def on_modified(self, event):
        """Permanent handler — also serves as the retry path for absorb_failed docs."""
        if self._should_process(event):
            logging.info(f"on_modified: {Path(event.src_path).name}")
            self.process_file(Path(event.src_path))

    def process_file(self, file_path: Path):
        # Size-stable check: wait until file stops changing and is non-zero.
        # Prevents partial reads during OneDrive / active-download writes.
        MAX_STABILITY_CHECKS = 5
        STABILITY_SLEEP_SEC = 3
        size_before = -1
        for _ in range(MAX_STABILITY_CHECKS):
            try:
                size_after = os.path.getsize(file_path)
            except OSError:
                size_after = -1
            if size_after == size_before and size_after > 0:
                break
            size_before = size_after
            time.sleep(STABILITY_SLEEP_SEC)
        else:
            logging.warning(
                f"File not stable after {MAX_STABILITY_CHECKS} checks, skipping: {file_path.name}. "
                f"OneDrive/OS will fire another event when the write completes."
            )
            return

        # Read bytes exactly once — these same bytes are hashed and sent to Gemini.
        # absorb_document never re-opens the file.
        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
        except OSError as e:
            logging.error(f"Could not read {file_path.name}: {e}")
            return

        # Sidecar: individual file intent (.txt file with same stem)
        user_intent = None
        sidecar_path = file_path.with_suffix('.txt')
        if sidecar_path.exists() and sidecar_path != file_path:
            try:
                with open(sidecar_path, 'r', encoding='utf-8') as f:
                    user_intent = f.read().strip()
                logging.info(f"Found sidecar intent for {file_path.name}")
            except Exception as e:
                logging.error(f"Error reading sidecar {sidecar_path}: {e}")

        # Folder-level _INTENT.txt fallback — capped, treated as context not commands.
        if not user_intent:
            intent_path = file_path.parent / "_INTENT.txt"
            if intent_path.exists():
                try:
                    with open(intent_path, 'r', encoding='utf-8') as f:
                        user_intent = f.read().strip()[:2000]
                    logging.info(f"Using folder _INTENT.txt for {file_path.name}")
                except Exception as e:
                    logging.error(f"Error reading _INTENT.txt in {file_path.parent}: {e}")

        # Hand off to Brain Processor with the pre-read bytes.
        from brain_processor import absorb_document
        try:
            logging.info(f"Handing off '{file_path.name}' to Brain Processor...")
            absorb_document(file_path, file_bytes, user_intent)
            logging.info(f"Processing complete for '{file_path.name}'")
        except Exception as e:
            logging.error(f"Error processing '{file_path.name}': {e}")


if __name__ == "__main__":
    if not os.path.exists(INBOX_DIR):
        os.makedirs(INBOX_DIR)

    event_handler = BrainInboxHandler()
    observer = Observer()
    observer.schedule(event_handler, INBOX_DIR, recursive=True)

    # Event-only mode — no startup sync.
    # Pre-existing inbox files absorb on next on_created or on_modified event.
    # Do NOT restore the os.walk startup loop.
    logging.info(
        f"Numista Brain Watcher started on {INBOX_DIR}. "
        f"Event-only mode — pre-existing files absorb on next create/modify event."
    )
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
