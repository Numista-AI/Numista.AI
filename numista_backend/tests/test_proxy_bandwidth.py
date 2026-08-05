import os
import sys
import pytest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from numista_scraper.config import (
    DEFAULT_MAX_BANDWIDTH_GB,
    get_scrape_proxy,
    get_random_scrape_proxy,
    is_proxy_circuit_broken,
    reset_proxy_circuit_breaker,
    record_proxy_bytes,
    fetch_webshare_api_usage
)

@pytest.fixture(autouse=True)
def cleanup_circuit_breaker():
    """Reset circuit breaker and environment before and after each test."""
    reset_proxy_circuit_breaker()
    old_env = os.environ.get("DISABLE_PROXIES")
    old_cap = os.environ.get("MAX_PROXY_BANDWIDTH_GB")
    old_skip = os.environ.get("SKIP_REMOTE_PROXY_CHECK")
    
    os.environ.pop("DISABLE_PROXIES", None)
    os.environ.pop("MAX_PROXY_BANDWIDTH_GB", None)
    os.environ["SKIP_REMOTE_PROXY_CHECK"] = "true"
    
    yield
    
    reset_proxy_circuit_breaker()
    if old_env is not None:
        os.environ["DISABLE_PROXIES"] = old_env
    else:
        os.environ.pop("DISABLE_PROXIES", None)
    if old_cap is not None:
        os.environ["MAX_PROXY_BANDWIDTH_GB"] = old_cap
    else:
        os.environ.pop("MAX_PROXY_BANDWIDTH_GB", None)
    if old_skip is not None:
        os.environ["SKIP_REMOTE_PROXY_CHECK"] = old_skip
    else:
        os.environ.pop("SKIP_REMOTE_PROXY_CHECK", None)


def test_default_max_bandwidth_cap():
    assert DEFAULT_MAX_BANDWIDTH_GB == 2.7


def test_disable_proxies_env_var():
    os.environ["DISABLE_PROXIES"] = "true"
    broken, reason = is_proxy_circuit_broken(force_check=True)
    assert broken is True
    assert "DISABLE_PROXIES" in reason
    assert get_scrape_proxy() == {"http": None, "https": None}
    assert get_random_scrape_proxy() == {"http": None, "https": None}


def test_session_bytes_circuit_breaker_trigger():
    # Set small cap for testing (0.001 GB = ~1 MB)
    os.environ["MAX_PROXY_BANDWIDTH_GB"] = "0.001"
    
    # 500 KB should not trigger
    record_proxy_bytes(500_000)
    broken, _ = is_proxy_circuit_broken()
    assert broken is False
    
    # Exceeding 1MB (600 KB more -> 1.1 MB total)
    record_proxy_bytes(600_000)
    broken, reason = is_proxy_circuit_broken()
    assert broken is True
    assert "Local session proxy usage" in reason
    assert get_scrape_proxy() == {"http": None, "https": None}


def test_reset_circuit_breaker():
    os.environ["MAX_PROXY_BANDWIDTH_GB"] = "0.001"
    record_proxy_bytes(2_000_000)
    assert is_proxy_circuit_broken()[0] is True
    
    reset_proxy_circuit_breaker()
    os.environ["MAX_PROXY_BANDWIDTH_GB"] = "2.7"
    assert is_proxy_circuit_broken()[0] is False


def test_webshare_api_fetch_handles_missing_token():
    used, limit = fetch_webshare_api_usage(token=None)
    assert used is None
    assert limit is None
