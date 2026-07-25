# -*- mode: python ; coding: utf-8 -*-
# numista-agent.spec — PyInstaller build spec for numista-agent.exe
# Run: python build_agent.py

import os, sys
from pathlib import Path

_HERE = Path(SPECPATH)  # numista_hardware/
_BACKEND = _HERE.parent / "numista_backend"

_datas = [
    (str(_HERE / "identify_coin.py"),   "."),
    (str(_HERE / "pcgs_service.py"),    "."),
    (str(_HERE / "agent_config.py"),    "."),
    (str(_HERE / "agent_setup.py"),     "."),
    (str(_HERE / "auto_capture.py"),    "."),
    (str(_HERE / "install_cert.py"),    "."),
    (str(_HERE / "coin-schema.json"),   "."),
    (str(_HERE / ".env"),               "."),
]

_sa_key = _BACKEND / "serviceAccountKey.json.json"
if _sa_key.exists():
    _datas.append((str(_sa_key), "."))

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
        "google.oauth2.service_account",
        "google.auth.transport.requests",
        "cv2",
        "flask_cors",
        "tkinter",
        "tkinter.ttk",
        "tkinter.messagebox",
        "dotenv",
        "cryptography",
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
    name="numista-agent",
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
