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

# ─── Import the agent logic & certificate installer ───────────────────────────
import auto_capture
import install_cert

# ─── Single-Instance Mutex Check (Windows) ────────────────────────────────────
_single_instance_mutex = None

def _acquire_single_instance():
    global _single_instance_mutex
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            mutex_name = "Global\\NumistaAgentSingleInstanceMutex"
            _single_instance_mutex = kernel32.CreateMutexW(None, False, mutex_name)
            last_error = kernel32.GetLastError()
            ERROR_ALREADY_EXISTS = 183
            if last_error == ERROR_ALREADY_EXISTS:
                logging.warning("[TRAY] Another instance of NumistaAgent is already running. Exiting.")
                sys.exit(0)
        except Exception as e:
            logging.warning(f"[TRAY] Single instance check warning: {e}")

# ─── Windows Autostart Registry Helper ─────────────────────────────────────────
def _is_autostart_enabled():
    if sys.platform != "win32":
        return False
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ,
        )
        winreg.QueryValueEx(key, "NumistaAgent")
        winreg.CloseKey(key)
        return True
    except Exception:
        return False

def _toggle_autostart(icon, item):
    if sys.platform != "win32":
        return
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE | winreg.KEY_READ,
        )
        if _is_autostart_enabled():
            winreg.DeleteValue(key, "NumistaAgent")
            logging.info("[TRAY] Windows autostart disabled.")
        else:
            exe_path = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(sys.argv[0])
            winreg.SetValueEx(key, "NumistaAgent", 0, winreg.REG_SZ, f'"{exe_path}"')
            logging.info(f"[TRAY] Windows autostart enabled → \"{exe_path}\"")
        winreg.CloseKey(key)
    except Exception as e:
        logging.error(f"[TRAY] Failed to toggle autostart: {e}")

# ─── Tray Icon Drawing ────────────────────────────────────────────────────────
def _make_icon(color="#00C853"):
    """Draws a coin icon for the tray: gold ring + coloured centre."""
    img  = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([2, 2, 62, 62], fill="#C9A84C", outline="#8B6B00", width=3)
    draw.ellipse([12, 12, 52, 52], fill=color)
    return img


_ICON_GREEN  = _make_icon("#00C853")   # Green  — online / connected & ready
_ICON_YELLOW = _make_icon("#FFAB00")   # Yellow — linking / unpaired / scanning
_ICON_RED    = _make_icon("#FF5252")   # Red    — error / offline

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
        email = auto_capture.USER_EMAIL or _cfg.get_user_email() or None
        if s.get("error"):
            icon_img = _ICON_RED
        elif not email:
            icon_img = _ICON_YELLOW
        elif s.get("is_active"):
            icon_img = _ICON_YELLOW
        else:
            icon_img = _ICON_GREEN

        if _tray_icon:
            _tray_icon.icon  = icon_img
            _tray_icon.title = _get_status_text()
        time.sleep(1)

# ─── Menu actions ─────────────────────────────────────────────────────────────
def _open_numista(icon, item):
    webbrowser.open("https://numista.ai")

def _open_log(icon, item):
    if os.path.exists(LOG_FILE):
        os.startfile(LOG_FILE)
    else:
        logging.warning(f"[TRAY] Log file not found at {LOG_FILE}")

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
    logging.info("[TRAY] User requested quit — performing clean shutdown.")
    _tray_icon = None
    icon.stop()
    os._exit(0)

# ─── Dynamic status label in menu ────────────────────────────────────────────
def _status_label():
    s = auto_capture.capture_status
    email = auto_capture.USER_EMAIL or _cfg.get_user_email() or None
    if s.get("error"):
        return f"🔴  Status: Error — {s['error'][:30]}"
    if s.get("is_active"):
        return f"🟡  Status: Scanning — {s.get('current_step', '…')}"
    if not email:
        return "🟡  Status: Linking / Unpaired"
    return f"🟢  Status: Connected ({email})"

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
        pystray.MenuItem(
            "Auto-Start on Login",
            _toggle_autostart,
            checked=lambda item: _is_autostart_enabled(),
        ),
        pystray.MenuItem("Open Log File",            _open_log),
        pystray.MenuItem("Switch Account / Settings…", _open_settings),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", _quit),
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


# ─── ITEM 11 (v4.1): Authenticated Pairing Session State ─────────────────────
# The firebase_token is retained in memory for the FULL duration of the capture
# session — not dropped after the pairing handshake.
# The agent uses this token to authenticate all Firestore writes during the session,
# ensuring writes are JWT-bound to the paired user's uid.
# On disconnect / re-pair: session cleared entirely. Token, uid, and email all
# refreshed from the new pairing payload.
#
# NON-NEGOTIABLE:
#   - Token is NEVER written to any file, database, or log.
#   - Token is NEVER printed to stdout/stderr.
#   - Only uid and email appear in tray_agent log messages.
#
_session_lock = threading.Lock()
_session: dict = {
    "uid": None,
    "email": None,
    "_firebase_token": None,  # Retained in memory ONLY — never persisted or logged
}


def _session_pair(uid: str, email: str, firebase_token: str) -> None:
    """Atomically update session state on pairing.  Token is stored in RAM only."""
    with _session_lock:
        _session["uid"] = uid
        _session["email"] = email
        _session["_firebase_token"] = firebase_token  # NOT logged, NOT written to disk
    logging.info(f"[TRAY] Session paired: uid={uid!r} email={email!r} (token held in memory)")


def _session_clear() -> None:
    """Wipe all session state on disconnect / re-pair."""
    with _session_lock:
        _session["uid"] = None
        _session["email"] = None
        _session["_firebase_token"] = None
    logging.info("[TRAY] Session cleared — awaiting new pairing.")


def get_session_token() -> str | None:
    """Return the in-memory firebase_token for the current session, or None if unpaired.
    Use this to authenticate Firestore writes.  Never log the return value."""
    with _session_lock:
        return _session.get("_firebase_token")


def _register_pair_v2_route() -> None:
    """Register /pair-v2 on auto_capture.app (done once, before Flask starts).
    This is the ITEM 11 authenticated pairing endpoint:
      POST /pair-v2  {uid, email, firebase_token}
    The existing /pair route (auto_capture.py line ~785) is left unchanged
    to preserve backward compatibility with older clients.
    """
    from flask import request as _req, jsonify as _json

    @auto_capture.app.route("/pair-v2", methods=["POST", "OPTIONS"])
    def _pair_v2():
        if _req.method == "OPTIONS":
            return "", 204
        data = _req.json or {}
        uid   = data.get("uid",   "")
        email = data.get("email", "")
        token = data.get("firebase_token", "")

        if not email or not uid:
            return _json({"status": "error", "message": "uid and email required"}), 400

        if not token:
            # Fail-open only if no token provided — still requires uid + email
            logging.warning(
                "[TRAY] /pair-v2 called without firebase_token — session NOT authenticated"
            )
        else:
            _session_pair(uid, email, token)
            # Also update the legacy USER_EMAIL so existing Firestore paths work
            auto_capture.set_user_email(email)

        return _json({"status": "success", "paired_email": email})

    @auto_capture.app.route("/unpair", methods=["POST", "OPTIONS"])
    def _unpair():
        if _req.method == "OPTIONS":
            return "", 204
        _session_clear()
        auto_capture.USER_EMAIL              = None
        auto_capture.FIRESTORE_COINS_PATH    = None
        auto_capture.FIRESTORE_COMMANDS_PATH = None
        return _json({"status": "cleared"})

    logging.info("[TRAY] /pair-v2 and /unpair routes registered on auto_capture.app.")

# ─── Agent thread: Firestore watcher + HTTPS Flask server ─────────────────────
def _start_agent():
    # Ensure SSL certificate is generated and registered in Windows Root store
    cert, key = install_cert.ensure_ssl_cert()

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
    ports_to_try = [8443, 5000]
    bound = False
    for port in ports_to_try:
        if os.path.exists(cert) and os.path.exists(key):
            ctx = _ssl.SSLContext(_ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(cert, key)
            logging.info(f"[TRAY] SSL cert loaded ({cert}) — serving HTTPS on port {port}")
            try:
                auto_capture.app.run(
                    host="0.0.0.0", port=port,
                    debug=False, use_reloader=False,
                    threaded=True,
                    ssl_context=ctx,
                )
                bound = True
                break
            except Exception as e:
                logging.warning(f"[TRAY] Could not bind Flask HTTPS on port {port}: {e}")
        else:
            logging.warning(f"[TRAY] Serving HTTP on port {port}")
            try:
                auto_capture.app.run(
                    host="0.0.0.0", port=port,
                    debug=False, use_reloader=False,
                    threaded=True,
                )
                bound = True
                break
            except Exception as e:
                logging.warning(f"[TRAY] Could not bind Flask HTTP on port {port}: {e}")
    if not bound:
        logging.error("[TRAY] Failed to bind Flask server on ports 8443 and 5000.")

# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    global _tray_icon

    _acquire_single_instance()

    logging.info("=" * 55)
    logging.info("  Numista.AI Hardware Agent v2.0")
    logging.info(f"  Log file: {LOG_FILE}")
    logging.info("=" * 55)

    _patch_auto_capture_user()
    if _cfg.get_user_email():
        logging.info(f"[TRAY] Restored saved account: {_cfg.get_user_email()!r}")
    else:
        logging.info("[TRAY] No saved account — waiting for web app to pair via /pair endpoint.")

    # ITEM 11: Register /pair-v2 route (firebase_token retained for full session)
    _register_pair_v2_route()

    # Start Firestore watcher + Flask server in background daemon thread
    agent_thread = threading.Thread(target=_start_agent, daemon=True)
    agent_thread.start()

    # Build and run the system tray icon on the main OS thread (blocks until exit)
    _tray_icon = pystray.Icon(
        name="NumistaAgent",
        icon=_ICON_GREEN,
        title="Numista.AI Hardware Agent — open Numista.AI to link",
        menu=_build_menu(),
    )

    threading.Thread(target=_update_tray_icon, daemon=True).start()
    logging.info("[TRAY] System tray icon active.")
    _tray_icon.run()


if __name__ == "__main__":
    main()

