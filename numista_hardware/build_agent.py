"""
build_agent.py — Automation Build Script for Numista Desktop Agent
===================================================================
Packages numista_hardware/auto_capture.py and tray_agent.py into a single,
self-contained Windows executable: dist/numista-agent.exe.
"""

import sys
import os
import subprocess
from pathlib import Path

for stream in (sys.stdout, sys.stderr):
    if stream is not None and hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass

HERE = Path(__file__).parent.resolve()
SPEC_FILE = HERE / "numista-agent.spec"
DIST_DIR = HERE / "dist"
OUTPUT_EXE = DIST_DIR / "numista-agent.exe"

def run_build():
    print("=" * 60)
    print("  Numista.AI Desktop Agent PyInstaller Builder")
    print(f"  Spec file: {SPEC_FILE}")
    print("=" * 60)

    if not SPEC_FILE.exists():
        print(f"❌ Spec file not found: {SPEC_FILE}", file=sys.stderr)
        sys.exit(1)

    cmd = [sys.executable, "-m", "PyInstaller", str(SPEC_FILE), "--noconfirm", "--clean"]
    print(f"[BUILD] Executing: {' '.join(cmd)}")

    res = subprocess.run(cmd, cwd=str(HERE))
    if res.returncode != 0:
        print(f"❌ PyInstaller build failed with return code {res.returncode}", file=sys.stderr)
        sys.exit(res.returncode)

    if OUTPUT_EXE.exists():
        size_mb = OUTPUT_EXE.stat().st_size / (1024 * 1024)
        print("=" * 60)
        print(f"  ✅ SUCCESS: {OUTPUT_EXE}")
        print(f"  Binary size: {size_mb:.2f} MB")
        print("=" * 60)
    else:
        print(f"❌ Build completed but executable missing at {OUTPUT_EXE}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_build()
