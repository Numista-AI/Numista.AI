import sys
import os
from pathlib import Path

# Add numista_backend to sys.path so tests can find 'main' and other modules
backend_path = str(Path(__file__).parent / "numista_backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Also add the root to sys.path
root_path = str(Path(__file__).parent)
if root_path not in sys.path:
    sys.path.insert(0, root_path)
