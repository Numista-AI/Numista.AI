import sys
import os
from pathlib import Path

# Add repo root first, then insert numista_backend at index 0 so 'import main'
# and 'from routes...' always resolve to numista_backend first.
root_path = str(Path(__file__).resolve().parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

backend_path = str(Path(__file__).resolve().parent / "numista_backend")
if backend_path in sys.path:
    sys.path.remove(backend_path)
sys.path.insert(0, backend_path)
