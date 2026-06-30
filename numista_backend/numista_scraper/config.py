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

# Proxy settings (can be populated via environment variables)
PROXIES = {
    "http": os.environ.get("NUMISTA_SCRAPE_HTTP_PROXY"),
    "https": os.environ.get("NUMISTA_SCRAPE_HTTPS_PROXY"),
}
