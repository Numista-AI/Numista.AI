import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path

# --- CONFIGURATION ---
INBOX_DIR = r"C:\Users\ericd\Documents\MyVertexProject\Numista_Brain_Inbox"
LOG_FILE = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\brain_watcher.log"
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.xls', '.jpg', '.jpeg', '.png'}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class BrainInboxHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        # Only process supported extensions, skip sidecar/temp files
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return
            
        logging.info(f"New file detected: {file_path.name}")
        self.process_file(file_path)

    def process_file(self, file_path: Path):
        # Wait a moment to ensure file is fully written/closed by OS
        time.sleep(2) 
        
        # Check for sidecar instruction file (.txt)
        sidecar_path = file_path.with_suffix('.txt')
        user_intent = None
        if sidecar_path.exists() and sidecar_path != file_path:
            try:
                with open(sidecar_path, 'r', encoding='utf-8') as f:
                    user_intent = f.read().strip()
                logging.info(f"Found sidecar instructions for {file_path.name}")
            except Exception as e:
                logging.error(f"Error reading sidecar {sidecar_path}: {e}")

        # Trigger Processor
        from brain_processor import absorb_document
        try:
            logging.info(f"Handing off '{file_path.name}' to Brain Processor...")
            absorb_document(file_path, user_intent)
            logging.info(f"Processing complete for '{file_path.name}'")
        except Exception as e:
            logging.error(f"Error processing '{file_path.name}': {e}")

if __name__ == "__main__":
    if not os.path.exists(INBOX_DIR):
        os.makedirs(INBOX_DIR)
        
    event_handler = BrainInboxHandler()
    observer = Observer()
    observer.schedule(event_handler, INBOX_DIR, recursive=True)
    
    # --- STARTUP SYNC ---
    logging.info("Starting initial sync of existing files...")
    for root, dirs, files in os.walk(INBOX_DIR):
        for file in files:
            file_path = Path(root) / file
            if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                logging.info(f"Syncing existing file: {file_path.name}")
                event_handler.process_file(file_path)
    
    logging.info(f"Numista Brain Watcher started on {INBOX_DIR}")
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
