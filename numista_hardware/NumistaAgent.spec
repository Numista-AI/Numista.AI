# -*- mode: python ; coding: utf-8 -*-
# NumistaAgent.spec — PyInstaller build spec (Secret-Free Build — Task 2 ARGON)
# Run: pyinstaller NumistaAgent.spec

import os, sys
from pathlib import Path

_HERE = Path(SPECPATH)  # numista_hardware/

# ── Data files bundled into the exe (STRICTLY CODE/SCHEMA — NO SECRETS OR KEYS) ─
_datas = [
    (str(_HERE / "identify_coin.py"),   "."),
    (str(_HERE / "pcgs_service.py"),    "."),
    (str(_HERE / "agent_config.py"),    "."),
    (str(_HERE / "agent_setup.py"),     "."),
    (str(_HERE / "auto_capture.py"),    "."),
    (str(_HERE / "install_cert.py"),    "."),
    (str(_HERE / "coin-schema.json"),   "."),
]

if (_HERE / "assets" / "icon.ico").exists():
    _datas.append((str(_HERE / "assets" / "icon.ico"), "assets"))

a = Analysis(
    [str(_HERE / "tray_agent.py")],
    pathex=[str(_HERE)],
    binaries=[],
    datas=_datas,
    hiddenimports=[
        "pystray._win32",
        "PIL._tkinter_finder",
        "google.cloud.firestore",
        "google.cloud.storage",
        "google.auth.transport.requests",
        "cv2",
        "flask_cors",
        "tkinter",
        "tkinter.ttk",
        "tkinter.messagebox",
        "dotenv",
        "cryptography",
        "cryptography.x509",
        "cryptography.hazmat.primitives.asymmetric.rsa",
        "winreg",
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(_HERE / "coin.ico") if (_HERE / "coin.ico").exists() else None,
)
