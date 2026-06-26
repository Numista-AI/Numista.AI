"""
Numista.AI Hardware Agent — System Tray Wrapper
================================================
Wraps auto_capture.py in a Windows system tray icon so it:
  - Shows a first-run setup wizard if not configured
  - Starts silently when Windows boots (via registry autostart)
  - Serves https://localhost:5000 (HTTPS so Chrome on numista.ai can reach it)
  - Shows live status in the tray tooltip
  - Has a rich right-click menu

Dependencies: pip install pystray pillow
Build:        See build_agent.ps1
"""

import threading
import sys
import os

# If running on Windows, hide the console window immediately to act like a windowless background service
if sys.platform == 'win32':
    try:
        import ctypes
        kernel32 = ctypes.WinDLL('kernel32')
        user32 = ctypes.WinDLL('user32')
        hWnd = kernel32.GetConsoleWindow()
        if hWnd != 0:
            user32.ShowWindow(hWnd, 0)  # SW_HIDE = 0
    except Exception:
        pass

# Force stdout/stderr to use UTF-8 and handle encoding errors gracefully (especially on Windows)
for stream in (sys.stdout, sys.stderr):
    if stream is not None:
        try:
            stream.reconfigure(encoding='utf-8', errors='backslashreplace')
        except Exception:
            pass

import logging
import time
import webbrowser

# ─── PyInstaller bundle path helper ──────────────────────────────────────────
def _bundle_path(*parts):
    """Return the path to a bundled resource (works in both dev and .exe)."""
    if hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, *parts)

# ─── Config (must import before auto_capture to avoid hardcoded email) ────────
sys.path.insert(0, _bundle_path())
from agent_config import AgentConfig

_cfg = AgentConfig()

# ─── Setup logging to %APPDATA%\NumistaAI\numista_agent.log ─────────────────
LOG_FILE = str(AgentConfig.get_log_path())
_handlers = [logging.FileHandler(LOG_FILE, encoding="utf-8")]
if sys.stdout is not None:
    _handlers.append(logging.StreamHandler(sys.stdout))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    handlers=_handlers,
)

import pystray
from PIL import Image, ImageDraw

# ─── Load .env BEFORE importing auto_capture / identify_coin ─────────────────
# identify_coin.py raises EnvironmentError at module level if GOOGLE_API_KEY
# is missing. Load the bundled .env now so all keys are in os.environ first.
_env_path = _bundle_path(".env")
if os.path.exists(_env_path):
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_path, override=False)
        logging.info("[TRAY] Loaded .env from bundle: %s", _env_path)
    except Exception as _e:
        logging.warning("[TRAY] Could not load .env via dotenv: %s", _e)
        # Fallback: parse manually
        with open(_env_path, encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _, _v = _line.partition("=")
                    os.environ.setdefault(_k.strip(), _v.strip())
else:
    logging.warning("[TRAY] .env not found at %s — API keys may be missing", _env_path)

# ─── Import the agent logic ───────────────────────────────────────────────────
import auto_capture

# ─── Tray Icon Drawing ────────────────────────────────────────────────────────
def _make_icon(color="#4C8CDA"):
    """Draws a coin icon for the tray: gold ring + coloured centre."""
    img  = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([2, 2, 62, 62], fill="#C9A84C", outline="#8B6B00", width=3)
    draw.ellipse([12, 12, 52, 52], fill=color)
    return img


_ICON_IDLE  = _make_icon("#4C8CDA")   # Blue  — ready / online
_ICON_BUSY  = _make_icon("#FFAB00")   # Amber — scanning
_ICON_ERROR = _make_icon("#FF5252")   # Red   — error / offline
_ICON_OK    = _make_icon("#00C853")   # Green — just saved a coin

# ─── Global tray reference ────────────────────────────────────────────────────
_tray_icon: pystray.Icon | None = None

# ─── Status tooltip ──────────────────────────────────────────────────────────
def _get_status_text():
    s = auto_capture.capture_status
    email = auto_capture.USER_EMAIL or _cfg.get_user_email() or None
    email_label = email if email else "Unpaired — open Numista.AI to link"
    if s.get("error"):
        return f"Numista Agent ⚠ {s['error'][:40]}"
    if s.get("is_active"):
        step  = s.get("current_step", "SCANNING")
        sharp = s.get("sharpness", 0)
        return f"Numista Agent 🔬 {step} | Sharpness: {sharp} | {email_label}"
    report = s.get("last_report")
    if report:
        slug = report.get("file_slug", "coin")
        return f"Numista Agent ✓ Ready — last scan: {slug} | {email_label}"
    return f"Numista Agent — Ready | {email_label}"

# ─── Icon updater (background thread) ────────────────────────────────────────
def _update_tray_icon():
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
            _tray_icon.icon  = icon_img
            _tray_icon.title = _get_status_text()
        time.sleep(1)

# ─── Menu actions ─────────────────────────────────────────────────────────────
def _open_numista(icon, item):
    webbrowser.open("https://numista.ai")

def _open_log(icon, item):
    os.startfile(LOG_FILE)

def _open_settings(icon, item):
    """Re-open the setup wizard so the user can change their email."""
    from agent_setup import run_setup_wizard_in_thread

    def _on_done(email, device):
        logging.info(f"[SETTINGS] Config updated → {email!r} on {device!r}")
        _cfg.reload()
        # Restart auto_capture's user references
        _patch_auto_capture_user()
        if _tray_icon:
            _tray_icon.title = _get_status_text()

    run_setup_wizard_in_thread(on_complete=_on_done)

def _quit(icon, item):
    global _tray_icon
    logging.info("[TRAY] User requested quit.")
    _tray_icon = None
    icon.stop()
    os._exit(0)

# ─── Dynamic status label in menu ────────────────────────────────────────────
def _status_label():
    s = auto_capture.capture_status
    email = auto_capture.USER_EMAIL or _cfg.get_user_email() or None
    if s.get("error"):
        return f"⚠  Error: {s['error'][:30]}"
    if s.get("is_active"):
        return f"🔬  Scanning — {s.get('current_step', '…')}"
    if s.get("last_report"):
        return "✓  Online — scan complete"
    if not email:
        return "🟡  Unpaired — open Numista.AI to link"
    return "🟢  Online — Ready"

def _build_menu():
    return pystray.Menu(
        # Status line (non-clickable)
        pystray.MenuItem(
            lambda item: _status_label(),
            None,
            enabled=False,
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Open Numista.AI",          _open_numista),
        pystray.MenuItem("Open Log File",            _open_log),
        pystray.MenuItem("Switch Account / Settings…", _open_settings),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", _quit),
    )

# ─── Patch auto_capture USER_EMAIL from config ───────────────────────────────
def _patch_auto_capture_user():
    """Override the hardcoded USER_EMAIL in auto_capture with config value."""
    email = _cfg.get_user_email()
    if not email:
        return
    auto_capture.USER_EMAIL             = email
    auto_capture.FIRESTORE_COINS_PATH   = f"users/{email}/coins"
    auto_capture.FIRESTORE_COMMANDS_PATH = f"commands/{email}/pending"
    logging.info(f"[TRAY] auto_capture USER_EMAIL → {email!r}")

# ─── Agent thread: Firestore watcher + HTTPS Flask server ─────────────────────
def _start_agent():
    # Fix certificate path for packaged exe
    cert = _bundle_path("localhost.crt")
    key  = _bundle_path("localhost.key")

    try:
        auto_capture.start_command_watcher()
        logging.info("[TRAY] Firestore command watcher started.")
    except Exception as e:
        logging.error(f"[TRAY] Command watcher failed to start: {e}", exc_info=True)

    # Start the idle preview thread so the Flutter app shows the camera feed
    # immediately — before the user presses Start Scan.
    import threading as _threading
    _preview_thread = _threading.Thread(
        target=auto_capture._idle_preview_worker,
        daemon=True,
        name="IdlePreview",
    )
    _preview_thread.start()
    logging.info("[TRAY] Idle preview thread launched.")

    import ssl as _ssl
    if os.path.exists(cert) and os.path.exists(key):
        ctx = _ssl.SSLContext(_ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(cert, key)
        logging.info(f"[TRAY] SSL cert loaded ({cert}) — serving HTTPS on port 5000")
        try:
            auto_capture.app.run(
                host="0.0.0.0", port=5000,
                debug=False, use_reloader=False,
                ssl_context=ctx,
            )
        except Exception as e:
            logging.error(f"[TRAY] Flask (HTTPS) error: {e}", exc_info=True)
    else:
        logging.warning("[TRAY] No SSL cert found — serving HTTP (Chrome will block from HTTPS pages)")
        logging.warning(f"[TRAY] Expected: {cert}")
        try:
            auto_capture.app.run(
                host="0.0.0.0", port=5000,
                debug=False, use_reloader=False,
            )
        except Exception as e:
            logging.error(f"[TRAY] Flask (HTTP) error: {e}", exc_info=True)

# ─── First-run wizard guard ────────────────────────────────────────────────────
def _ensure_configured():
    """
    If no config exists, block until the user completes the setup wizard.
    Returns True if configured, False if user cancelled.
    """
    if _cfg.is_configured():
        return True

    logging.info("[TRAY] No config found — launching setup wizard.")

    _configured = threading.Event()
    _cancelled  = [False]

    def _on_complete(email, device):
        _cfg.reload()
        _configured.set()

    def _on_cancel():
        _cancelled[0] = True
        _configured.set()

    # Run wizard (wizard is its own Tk main loop — must run on main thread
    # before pystray takes over, which is why we call this before _tray_icon.run())
    from agent_setup import run_setup_wizard
    run_setup_wizard(on_complete=_on_complete, on_cancel=_on_cancel)

    if _cancelled[0]:
        logging.warning("[TRAY] User cancelled setup — agent cannot start without an email.")
        return False
    return True

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    global _tray_icon

    logging.info("=" * 55)
    logging.info("  Numista.AI Hardware Agent v2.0")
    logging.info(f"  Log file: {LOG_FILE}")
    logging.info("=" * 55)

    # [1] Apply any previously saved email config to auto_capture.
    #     If no email is stored yet, the agent starts in "Unpaired" state.
    #     The Flutter web app will call POST /pair automatically when the user
    #     opens the Microscope Scanner page, so no manual entry is needed.
    _patch_auto_capture_user()
    if _cfg.get_user_email():
        logging.info(f"[TRAY] Restored saved account: {_cfg.get_user_email()!r}")
    else:
        logging.info("[TRAY] No saved account — waiting for web app to pair via /pair endpoint.")

    # [2] Start Firestore watcher + Flask server in background
    agent_thread = threading.Thread(target=_start_agent, daemon=True)
    agent_thread.start()

    # [3] Build and run the system tray icon (blocks until quit)
    _tray_icon = pystray.Icon(
        name="NumistaAgent",
        icon=_ICON_IDLE,
        title="Numista.AI Hardware Agent — open Numista.AI to link",
        menu=_build_menu(),
    )

    threading.Thread(target=_update_tray_icon, daemon=True).start()
    logging.info("[TRAY] System tray icon active.")
    _tray_icon.run()


if __name__ == "__main__":
    main()
