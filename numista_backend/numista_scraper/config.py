import os
from pathlib import Path

# Paths
SCRAPER_DIR = Path(__file__).parent
BACKEND_DIR = SCRAPER_DIR.parent
DB_PATH = BACKEND_DIR / "database" / "numista_coins.db"
KEY_PATH = BACKEND_DIR / "serviceAccountKey.json.json"

# GCP/Firebase Config
GCP_PROJECT = "studio-9101802118-8c9a8"
BUCKET_NAME = "numista-uploads-studio-9101802118-8c9a8"

# Scraper Settings
DEFAULT_DELAY = 1.5      # Delay in seconds between HTTP requests
BROWSER_DELAY = 3.0      # Delay in seconds for browser interactions
REQUEST_TIMEOUT = 30     # Timeout in seconds

# User Agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

# Sourcing Endpoints
PCGS_COINFACTS_SEARCH = "https://www.pcgs.com/search?q="
NUMISTA_SEARCH = "https://en.numista.com/catalogue/index.php"
HERITAGE_COINS_SEARCH = "https://coins.ha.com/c/search-results.zx"
HERITAGE_CURRENCY_SEARCH = "https://currency.ha.com/c/search-results.zx"
ERROR_REF_URL = "https://www.error-ref.com/"
COINWEEK_SEARCH = "https://coinweek.com/?s="

# ─── Rotating Proxy Pool & Bandwidth Circuit Breaker ────────────────────────
# Proxies are loaded lazily from Firestore (config/webshare_proxies) on first
# use, so Cloud Run containers share the same managed list without baking
# credentials into env vars. Local dev falls back to env vars if Firestore
# is unreachable.
# Includes an automated circuit breaker that disables proxies before reaching
# the 3.0 GB monthly bandwidth limit (default safety cap: 2.7 GB).

import time as _time
import random as _random
from datetime import datetime as _datetime, timezone as _tz

_proxy_pool: list = []       # Cached list of proxy URL strings
_proxy_index: int = 0        # Round-robin cursor

# Bandwidth Safety Circuit Breaker settings
DEFAULT_MAX_BANDWIDTH_GB: float = float(os.environ.get("MAX_PROXY_BANDWIDTH_GB", "2.7"))
_CHECK_INTERVAL_SEC: float = 300.0  # 5 minute caching interval for API/Firestore checks

_circuit_broken: bool = False
_circuit_reason: str = ""
_last_check_time: float = 0.0
_recorded_bytes: int = 0


def fetch_webshare_api_usage(token: str | None = None) -> tuple[int | None, int | None]:
    """
    Query Webshare API v2 to retrieve current billing cycle bandwidth usage and limit.
    Returns (used_bytes, limit_bytes) or (None, None) if unreachable / no token.
    """
    api_token = token or os.environ.get("WEBSHARE_API_TOKEN")
    if not api_token:
        return None, None
    try:
        import requests
        url = "https://proxy.webshare.io/api/v2/subscription/plan/"
        headers = {
            "Authorization": f"Token {api_token}",
            "X-Webshare-Source": "WebshareSkill/1.0 (LLM; Antigravity)"
        }
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            if results:
                plan = results[0]
                used_bytes = plan.get("bandwidth_used")
                limit_bytes = plan.get("bandwidth_limit")
                return used_bytes, limit_bytes
    except Exception as e:
        print(f"[config] Could not fetch Webshare API usage: {e}")
    return None, None


def is_proxy_circuit_broken(force_check: bool = False) -> tuple[bool, str]:
    """
    Check if proxy usage is disabled or circuit-broken due to reaching the safety bandwidth limit.
    Returns (is_broken, reason).
    """
    global _circuit_broken, _circuit_reason, _last_check_time

    # 1. Environment variable override
    if os.environ.get("DISABLE_PROXIES") == "true":
        return True, "DISABLE_PROXIES environment variable is set to true"

    # Fast path if already broken and not forcing recheck
    if _circuit_broken and not force_check:
        return True, _circuit_reason

    now = _time.time()
    max_gb = float(os.environ.get("MAX_PROXY_BANDWIDTH_GB", DEFAULT_MAX_BANDWIDTH_GB))
    max_bytes = int(max_gb * 1024 * 1024 * 1024)

    # Check local session recorded bytes
    if _recorded_bytes >= max_bytes:
        _circuit_broken = True
        _circuit_reason = f"Local session proxy usage ({_recorded_bytes / (1024**3):.2f} GB) reached safety cap ({max_gb:.2f} GB)"
        return True, _circuit_reason

    # Periodic remote check (skipped during local tests if SKIP_REMOTE_PROXY_CHECK is set)
    if not os.environ.get("SKIP_REMOTE_PROXY_CHECK") and (force_check or (now - _last_check_time > _CHECK_INTERVAL_SEC)):
        _last_check_time = now
        try:
            from firebase_admin import firestore as _fs, initialize_app, _apps, credentials
            if not _apps:
                if os.path.exists(KEY_PATH):
                    cred = credentials.Certificate(str(KEY_PATH))
                    initialize_app(cred)
                else:
                    initialize_app()
            db = _fs.client()
            doc = db.collection("config").document("webshare_proxies").get()
            if doc.exists:
                doc_data = doc.to_dict() or {}
                # Check Firestore flags
                if doc_data.get("circuit_broken") is True or doc_data.get("disabled") is True:
                    _circuit_broken = True
                    _circuit_reason = doc_data.get("disabled_reason") or f"Disabled via Firestore config (circuit_broken=True)"
                    return True, _circuit_reason

                custom_max_gb = doc_data.get("max_bandwidth_gb")
                if custom_max_gb:
                    max_gb = float(custom_max_gb)
                    max_bytes = int(max_gb * 1024 * 1024 * 1024)

                # Check Webshare API if token is in Firestore or Env
                api_token = os.environ.get("WEBSHARE_API_TOKEN") or doc_data.get("api_token")
                if api_token:
                    used_bytes, limit_bytes = fetch_webshare_api_usage(api_token)
                    if used_bytes is not None and used_bytes >= max_bytes:
                        _circuit_broken = True
                        _circuit_reason = f"Webshare account bandwidth ({used_bytes / (1024**3):.2f} GB) reached safety cap ({max_gb:.2f} GB / 3.0 GB limit)"
                        print(f"[config] 🛑 PROXY CIRCUIT BREAKER ACTIVATED: {_circuit_reason}")
                        # Persist circuit broken status to Firestore
                        try:
                            db.collection("config").document("webshare_proxies").update({
                                "circuit_broken": True,
                                "disabled_reason": _circuit_reason,
                                "last_bandwidth_check": _datetime.now(_tz.utc).isoformat()
                            })
                        except Exception:
                            pass
                        return True, _circuit_reason
        except Exception as e:
            # Fall back silently on Firestore check errors
            pass

    return _circuit_broken, _circuit_reason


def reset_proxy_circuit_breaker() -> None:
    """Reset the circuit breaker status (e.g. for testing or new billing cycle)."""
    global _circuit_broken, _circuit_reason, _recorded_bytes, _last_check_time
    _circuit_broken = False
    _circuit_reason = ""
    _recorded_bytes = 0
    _last_check_time = 0.0


def record_proxy_bytes(bytes_count: int) -> None:
    """Record byte usage through proxy calls to enforce real-time session shutoff."""
    global _recorded_bytes
    if bytes_count > 0:
        _recorded_bytes += bytes_count
        max_gb = float(os.environ.get("MAX_PROXY_BANDWIDTH_GB", DEFAULT_MAX_BANDWIDTH_GB))
        if _recorded_bytes >= int(max_gb * 1024 * 1024 * 1024):
            is_proxy_circuit_broken(force_check=True)


def _load_proxy_pool() -> list:
    """Load proxy list from Firestore config/webshare_proxies."""
    try:
        from firebase_admin import firestore as _fs, initialize_app, _apps, credentials
        if not _apps:
            if os.path.exists(KEY_PATH):
                cred = credentials.Certificate(str(KEY_PATH))
                initialize_app(cred)
            else:
                initialize_app()
        db = _fs.client()
        doc = db.collection("config").document("webshare_proxies").get()
        if doc.exists:
            pool = doc.to_dict().get("proxies", [])
            if pool:
                return pool
    except Exception as e:
        print(f"[config] Could not load proxy pool from Firestore: {e}")
    # Fallback: env var (local dev / first boot before Firestore is ready)
    env_proxy = os.environ.get("NUMISTA_SCRAPE_HTTP_PROXY") or os.environ.get("NUMISTA_SCRAPE_HTTPS_PROXY")
    return [env_proxy] if env_proxy else []


def get_scrape_proxy() -> dict:
    """
    Return a requests-compatible proxy dict with the next proxy in the pool.
    Rotates round-robin so successive calls use different IPs.
    Returns {"http": None, "https": None} if no proxies are configured or circuit broken.
    """
    broken, reason = is_proxy_circuit_broken()
    if broken:
        return {"http": None, "https": None}
    global _proxy_pool, _proxy_index
    if not _proxy_pool:
        _proxy_pool = _load_proxy_pool()
    if not _proxy_pool:
        return {"http": None, "https": None}
    proxy_url = _proxy_pool[_proxy_index % len(_proxy_pool)]
    _proxy_index += 1
    return {"http": proxy_url, "https": proxy_url}


def get_random_scrape_proxy() -> dict:
    """
    Return a requests-compatible proxy dict with a randomly chosen proxy.
    Useful when you want unpredictable rotation rather than round-robin.
    Returns {"http": None, "https": None} if no proxies are configured or circuit broken.
    """
    broken, reason = is_proxy_circuit_broken()
    if broken:
        return {"http": None, "https": None}
    global _proxy_pool
    if not _proxy_pool:
        _proxy_pool = _load_proxy_pool() or []
    if not _proxy_pool:
        return {"http": None, "https": None}
    proxy_url = _random.choice(_proxy_pool)
    return {"http": proxy_url, "https": proxy_url}


# Legacy alias — keeps any existing code that references PROXIES working,
# but now it uses a randomly-picked proxy from the pool.
PROXIES = get_random_scrape_proxy()

