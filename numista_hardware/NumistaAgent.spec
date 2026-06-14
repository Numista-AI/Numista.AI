# -*- mode: python ; coding: utf-8 -*-
# NumistaAgent.spec — PyInstaller build spec
# Run: pyinstaller NumistaAgent.spec
#
# Bundles: tray_agent, agent_config, agent_setup, auto_capture,
#          identify_coin, pcgs_service, SSL cert/key, .env,
#          coin-schema.json, serviceAccountKey.json.json

import os, sys
from pathlib import Path

_HERE = Path(SPECPATH)  # numista_hardware/
_BACKEND = _HERE.parent / "numista_backend"

# ── Data files to bundle into the exe ─────────────────────────────────────────
_datas = [
    # Python modules that PyInstaller can't auto-discover (imported at runtime)
    (str(_HERE / "identify_coin.py"),   "."),
    (str(_HERE / "pcgs_service.py"),    "."),
    (str(_HERE / "agent_config.py"),    "."),
    (str(_HERE / "agent_setup.py"),     "."),
    (str(_HERE / "auto_capture.py"),    "."),
    (str(_HERE / "coin-schema.json"),   "."),
    # SSL cert + key (required for HTTPS on localhost:5000)
    (str(_HERE / "localhost.crt"),      "."),
    (str(_HERE / "localhost.key"),      "."),
    # Environment variables (.env) — loaded by python-dotenv in identify_coin
    (str(_HERE / ".env"),               "."),
]

# Bundle service account key if it exists
_sa_key = _BACKEND / "serviceAccountKey.json.json"
if _sa_key.exists():
    _datas.append((str(_sa_key), "."))
else:
    print(f"[SPEC WARNING] Service account key not found at {_sa_key}")
    print("  The agent will fall back to Application Default Credentials.")

a = Analysis(
    [str(_HERE / "tray_agent.py")],
    pathex=[str(_HERE)],
    binaries=[],
    datas=_datas,
    hiddenimports=[
        # pystray Windows backend
        "pystray._win32",
        "PIL._tkinter_finder",
        # Google Cloud
        "google.cloud.firestore",
        "google.cloud.storage",
        "google.oauth2.service_account",
        "google.auth.transport.requests",
        # OpenCV (cv2 is a C extension — PyInstaller usually catches it but list explicitly)
        "cv2",
        # Flask
        "flask_cors",
        # Tkinter (for agent_setup wizard)
        "tkinter",
        "tkinter.ttk",
        "tkinter.messagebox",
        # python-dotenv
        "dotenv",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="NumistaAgent",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,           # No black console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Use the coin icon if it exists
    icon=str(_HERE / "coin.ico") if (_HERE / "coin.ico").exists() else None,
)
