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

# ─── Rotating Proxy Pool ─────────────────────────────────────────────────────
# Proxies are loaded lazily from Firestore (config/webshare_proxies) on first
# use, so Cloud Run containers share the same managed list without baking
# credentials into env vars.  Local dev falls back to the env vars if Firestore
# is unreachable.

import random as _random

_proxy_pool: list = []       # Cached list of proxy URL strings
_proxy_index: int = 0        # Round-robin cursor


def _load_proxy_pool() -> list:
    """Load proxy list from Firestore config/webshare_proxies."""
    try:
        from firebase_admin import firestore as _fs
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
    Returns {"http": None, "https": None} if no proxies are configured.
    """
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
    """
    global _proxy_pool
    if not _proxy_pool:
        _proxy_pool = _load_proxy_pool()
    if not _proxy_pool:
        return {"http": None, "https": None}
    proxy_url = _random.choice(_proxy_pool)
    return {"http": proxy_url, "https": proxy_url}


# Legacy alias — keeps any existing code that references PROXIES working,
# but now it uses a randomly-picked proxy from the pool.
PROXIES = get_random_scrape_proxy()
