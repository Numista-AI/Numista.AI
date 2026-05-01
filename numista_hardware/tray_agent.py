"""
Numista.AI Hardware Agent — System Tray Wrapper
================================================
Wraps auto_capture.py in a Windows system tray icon so it:
  - Starts silently when Windows boots
  - Shows live status in the tray tooltip
  - Has a right-click menu (Status / Open Log / Quit)

Dependencies: pip install pystray pillow
Build:        See build_agent.ps1
"""
import threading
import sys
import os
import logging
import time

# ─── Setup logging to a file (no console window in packaged .exe) ─────────────
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "numista_agent.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ]
)

import pystray
from PIL import Image, ImageDraw

# ─── Import the agent logic ───────────────────────────────────────────────────
# auto_capture.py must live in the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import auto_capture

# ─── Tray Icon Drawing ────────────────────────────────────────────────────────
def _make_icon(color="#4C8CDA"):
    """Draws a simple coin icon for the tray."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Outer gold ring
    draw.ellipse([2, 2, 62, 62], fill="#C9A84C", outline="#8B6B00", width=3)
    # Inner colored circle (changes with status)
    draw.ellipse([12, 12, 52, 52], fill=color)
    return img

_ICON_IDLE    = _make_icon("#4C8CDA")   # Blue — ready
_ICON_BUSY    = _make_icon("#FFAB00")   # Amber — scanning
_ICON_ERROR   = _make_icon("#FF5252")   # Red — error
_ICON_OK      = _make_icon("#00C853")   # Green — just saved a coin

# ─── Tray Logic ───────────────────────────────────────────────────────────────
_tray_icon: pystray.Icon | None = None

def _get_status_text():
    s = auto_capture.capture_status
    if s.get("error"):
        return f"Numista Agent ⚠ {s['error'][:40]}"
    if s.get("is_active"):
        step = s.get("current_step", "SCANNING")
        sharp = s.get("sharpness", 0)
        return f"Numista Agent 🔬 {step} | Sharpness: {sharp}"
    report = s.get("last_report")
    if report:
        slug = report.get("file_slug", "coin")
        return f"Numista Agent ✓ Ready — last scan: {slug}"
    return "Numista Agent — Ready"

def _update_tray_icon():
    """Keeps the tray icon color in sync with capture status."""
    global _tray_icon
    while _tray_icon is not None:
        s = auto_capture.capture_status
        if s.get("error"):
            icon_img = _ICON_ERROR
        elif s.get("is_active"):
            icon_img = _ICON_BUSY
        else:
            icon_img = _ICON_IDLE
        if _tray_icon:
            _tray_icon.icon = icon_img
            _tray_icon.title = _get_status_text()
        time.sleep(1)

def _open_log(icon, item):
    os.startfile(LOG_FILE)

def _quit(icon, item):
    global _tray_icon
    logging.info("[TRAY] User requested quit.")
    _tray_icon = None
    icon.stop()
    os._exit(0)

def _build_menu():
    return pystray.Menu(
        pystray.MenuItem("Numista.AI Hardware Agent", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Open Log File", _open_log),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", _quit),
    )

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    global _tray_icon
    logging.info("=" * 50)
    logging.info("  Numista.AI Hardware Agent starting...")
    logging.info(f"  Log file: {LOG_FILE}")
    logging.info("=" * 50)

    # Start the Firestore command watcher + Flask status server in background
    def _start_agent():
        try:
            auto_capture.start_command_watcher()
            logging.info("[TRAY] Firestore watcher started.")
            auto_capture.app.run(
                host="0.0.0.0", port=5000, debug=False, use_reloader=False
            )
        except Exception as e:
            logging.error(f"[TRAY] Agent error: {e}", exc_info=True)

    agent_thread = threading.Thread(target=_start_agent, daemon=True)
    agent_thread.start()

    # Start icon update thread
    _tray_icon = pystray.Icon(
        name="NumistaAgent",
        icon=_ICON_IDLE,
        title="Numista.AI Hardware Agent — Ready",
        menu=_build_menu(),
    )
    threading.Thread(target=_update_tray_icon, daemon=True).start()

    logging.info("[TRAY] System tray icon active.")
    _tray_icon.run()   # Blocks until quit


if __name__ == "__main__":
    main()
