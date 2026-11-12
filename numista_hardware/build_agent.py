"""
build_agent.py — Automation Build Script for Numista Desktop Agent (Secret-Free Hardened — Task 2 ARGON)
========================================================================================================
Packages numista_hardware/auto_capture.py and tray_agent.py into a single,
self-contained Windows executable: dist/numista-agent.exe (without secrets or static keys).
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


def verify_secret_free(exe_path: Path) -> None:
    from PyInstaller.archive.readers import CArchiveReader

    reader = CArchiveReader(str(exe_path))
    toc_keys = set(reader.toc.keys())
    forbidden_toc = (".env", "serviceaccountkey", ".key", ".crt")
    bad_toc = [k for k in toc_keys if any(f in k.lower() for f in forbidden_toc)]
    if bad_toc:
        exe_path.unlink(missing_ok=True)
        raise RuntimeError(f"Forbidden TOC entries found in {exe_path}: {bad_toc}")

    raw = exe_path.read_bytes()
    forbidden_bytes = (
        b"AIzaSy",
        b"7af45f7e0a341f369ff1a6034175825f8b9e81af",
        b"f2eb11c27044ca5d178e5e5a31678f037e88940b",
        b"BEGIN PRIVATE KEY",
        b"BEGIN RSA PRIVATE KEY",
    )
    for pat in forbidden_bytes:
        if pat in raw:
            exe_path.unlink(missing_ok=True)
            raise RuntimeError(f"Forbidden secret byte pattern found in {exe_path}")


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
        verify_secret_free(OUTPUT_EXE)
        size_mb = OUTPUT_EXE.stat().st_size / (1024 * 1024)
        print("=" * 60)
        print(f"  ✅ SUCCESS (Secret-Free Verified): {OUTPUT_EXE}")
        print(f"  Binary size: {size_mb:.2f} MB")
        print("=" * 60)
    else:
        print(f"❌ Build completed but executable missing at {OUTPUT_EXE}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_build()
