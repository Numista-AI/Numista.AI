"""
pcgs_service.py — Numista.AI PCGS Integration
==============================================
Uses the PCGS Public API (api.pcgs.com/publicapi) to enrich scan results
with population data, price guides, and composition info.

API uses Bearer token authentication (pre-obtained OAuth token from .env).
Free tier limit: 1,000 calls/day.

PCGS Number lookup strategy:
  - We maintain a local mapping of common US coins → PCGS numbers.
  - For unlisted coins, we attempt the CoinFacts search endpoint.
  - Falls back gracefully (returns None) so scans never fail.
"""

import os
import time
import logging
import requests
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

_TOKEN = os.getenv("PCGS_ACCESS_TOKEN")
_BASE  = "https://api.pcgs.com/publicapi"

# ─── Local PCGS Number Map ─────────────────────────────────────────────────────
# Format: (year_start, year_end, denomination, mint_marks) -> pcgs_no_base
# A "base" PCGS number is the no-mint-mark Philadelphia version.
# Mint-mark offsets are handled in _resolve_pcgs_number().
#
# Source: PCGS Numbering System reference book & CoinFacts catalog.
_PCGS_MAP = {
    # ── Lincoln Cents ──────────────────────────────────────────────────────────
    ("Lincoln Cent", "1c", range(1909, 1959)): 2000,    # Wheat reverse
    ("Lincoln Cent", "1c", range(1959, 2009)): 2950,    # Memorial reverse
    ("Lincoln Cent", "1c", range(2009, 2100)): 3000,    # Shield reverse

    # ── Jefferson Nickels ──────────────────────────────────────────────────────
    ("Jefferson Nickel", "5c", range(1938, 2100)): 3900,

    # ── Roosevelt Dimes ───────────────────────────────────────────────────────
    ("Roosevelt Dime", "10c", range(1946, 1965)): 5015,  # Silver (90%) ← KEY
    ("Roosevelt Dime", "10c", range(1965, 2100)): 5070,  # Clad

    # ── Mercury Dimes ─────────────────────────────────────────────────────────
    ("Mercury Dime", "10c", range(1916, 1946)):  4700,   # Silver

    # ── Washington Quarters ────────────────────────────────────────────────────
    ("Washington Quarter", "25c", range(1932, 1965)): 5790,  # Silver (90%)
    ("Washington Quarter", "25c", range(1965, 1999)): 5850,  # Clad
    # State Quarters, America the Beautiful, AWQ — PCGS numbers vary by design;
    # the API CoinFacts search is used for those.

    # ── Kennedy Half Dollars ───────────────────────────────────────────────────
    ("Kennedy Half Dollar", "50c", range(1964, 1965)): 6400,   # 90% Silver
    ("Kennedy Half Dollar", "50c", range(1965, 1971)): 6405,   # 40% Silver
    ("Kennedy Half Dollar", "50c", range(1971, 2100)): 6480,   # Clad/Proof

    # ── Franklin Half Dollars ──────────────────────────────────────────────────
    ("Franklin Half Dollar", "50c", range(1948, 1964)): 6315,  # Silver

    # ── Walking Liberty Half Dollars ───────────────────────────────────────────
    ("Walking Liberty Half Dollar", "50c", range(1916, 1948)): 6150,  # Silver

    # ── Morgan Dollars ────────────────────────────────────────────────────────
    ("Morgan Dollar", "$1", range(1878, 1905)): 7070,   # Silver
    ("Morgan Dollar", "$1", range(1921, 1922)): 7260,   # 1921 Morgan

    # ── Peace Dollars ─────────────────────────────────────────────────────────
    ("Peace Dollar", "$1", range(1921, 1936)): 7350,    # Silver

    # ── Eisenhower Dollars ────────────────────────────────────────────────────
    ("Eisenhower Dollar", "$1", range(1971, 1979)): 7376,

    # ── American Silver Eagle ─────────────────────────────────────────────────
    ("American Silver Eagle", "$1", range(1986, 2100)): 9401,  # .999 Silver

    # ── Barber Dimes ──────────────────────────────────────────────────────────
    ("Barber Dime", "10c", range(1892, 1917)): 4490,    # Silver
}

# Silver composition lookup table (year, denomination) → composition string
# This is the authoritative source for the "is silver?" determination.
_SILVER_COMPOSITIONS = {
    # Dimes
    ("Mercury Dime",    "10c"): ("90% Silver, 10% Copper", 0.07234),   # Troy oz Ag
    ("Barber Dime",     "10c"): ("90% Silver, 10% Copper", 0.07234),
    ("Roosevelt Dime (Silver)", "10c"): ("90% Silver, 10% Copper", 0.07234),

    # Quarters
    ("Washington Quarter (Silver)", "25c"): ("90% Silver, 10% Copper", 0.18084),
    ("Barber Quarter",  "25c"): ("90% Silver, 10% Copper", 0.18084),
    ("Standing Liberty Quarter", "25c"): ("90% Silver, 10% Copper", 0.18084),

    # Halves
    ("Franklin Half Dollar",       "50c"): ("90% Silver, 10% Copper", 0.36169),
    ("Walking Liberty Half Dollar","50c"): ("90% Silver, 10% Copper", 0.36169),
    ("Kennedy Half Dollar (90%)",  "50c"): ("90% Silver, 10% Copper", 0.36169),
    ("Kennedy Half Dollar (40%)",  "50c"): ("40% Silver, 60% Copper", 0.14792),

    # Dollars
    ("Morgan Dollar",  "$1"): ("90% Silver, 10% Copper", 0.77344),
    ("Peace Dollar",   "$1"): ("90% Silver, 10% Copper", 0.77344),
    ("American Silver Eagle", "$1"): ("99.9% Silver", 1.000),
    ("Peace Dollar (2021)", "$1"): ("99.9% Silver", 0.858),  # Modern commemorative

    # World / Misc
    ("Mercury Dime Gold", "10c"): ("Gold — Not Silver", 0.0),
}

# Year-range rules for determining silver composition by denomination alone:
_SILVER_YEAR_RULES = [
    # (denomination_keywords, year_range, is_silver, composition, troy_oz_ag)
    (["dime", "10c"],      range(1796, 1965), True,  "90% Silver, 10% Copper", 0.07234),
    (["quarter", "25c"],   range(1796, 1965), True,  "90% Silver, 10% Copper", 0.18084),
    (["half", "50c"],      range(1796, 1965), True,  "90% Silver, 10% Copper", 0.36169),
    (["half", "50c"],      range(1965, 1971), True,  "40% Silver, 60% Copper", 0.14792),
    (["dollar", "$1"],     range(1794, 1936), True,  "90% Silver, 10% Copper", 0.77344),
    (["silver eagle"],     range(1986, 2100), True,  "99.9% Silver",            1.000),
    (["morgan"],           range(1878, 2100), True,  "90% Silver, 10% Copper", 0.77344),
    (["peace"],            range(1921, 1936), True,  "90% Silver, 10% Copper", 0.77344),
    (["mercury"],          range(1916, 1946), True,  "90% Silver, 10% Copper", 0.07234),
    (["walking liberty"],  range(1916, 1948), True,  "90% Silver, 10% Copper", 0.36169),
    (["franklin"],         range(1948, 1964), True,  "90% Silver, 10% Copper", 0.36169),
    (["barber"],           range(1892, 1917), True,  "90% Silver, 10% Copper", 0.07234),
]

# Year-range rules for determining gold composition by denomination alone:
# (keywords, year_range, composition, troy_oz_au)
_GOLD_YEAR_RULES = [
    (["double eagle", "twenty dollars", "$20", "20 dollars"], range(1849, 1934), "Gold (90% Gold, 10% Copper)", 0.96750),
    (["half eagle", "five dollars", "$5", "5 dollars"],       range(1795, 1930), "Gold (90% Gold, 10% Copper)", 0.24188),
    (["quarter eagle", "2.5 gold", "2-1/2 dollars", "two and a half"], range(1796, 1930), "Gold (90% Gold, 10% Copper)", 0.12094),
    (["three dollars", "$3", "3 dollars"],                    range(1854, 1890), "Gold (90% Gold, 10% Copper)", 0.14513),
    (["one dollar", "gold dollar", "$1 gold", "1 dollar gold"], range(1849, 1890), "Gold (90% Gold, 10% Copper)", 0.04837),
    (["eagle", "ten dollars", "$10", "10 dollars"],           range(1795, 1934), "Gold (90% Gold, 10% Copper)", 0.48375),
]



class PCGSService:
    """
    Provides PCGS API lookups and local silver determination for coin scan results.
    """

    # --- Caching for live spot prices ---
    _live_spot_cache = None
    _last_spot_update = 0
    _CACHE_TTL = 3600  # 60 minutes
    _DEFAULT_SPOT = 32.50  # USD baseline fallback

    def __init__(self):
        self.token = _TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }

    # ─── Public: Full Enrich ──────────────────────────────────────────────────

    def enrich_coin(self, coin_data: dict) -> dict:
        """
        Main entry point. Given a coin_data dict from Gemini, returns an
        enriched dict with:
          - metal_content (string)
          - is_silver (bool)
          - is_gold (bool)
          - silver_troy_oz (float, 0.0 if not silver)
          - gold_troy_oz (float, 0.0 if not gold)
          - melt_value_estimate (string, e.g. "$1.83")
          - pcgs_data (dict or None — raw API response)
          - pcgs_number (int or None)
        """
        year        = coin_data.get("year")
        denomination = (coin_data.get("denomination") or "").lower()
        series      = (coin_data.get("program_series") or "").lower()
        mint_mark   = (coin_data.get("mint_mark") or "").upper().strip()

        enriched = dict(coin_data)
        enriched["is_silver"]         = False
        enriched["is_gold"]           = False
        enriched["silver_troy_oz"]    = 0.0
        enriched["gold_troy_oz"]      = 0.0
        enriched["metal_content"]     = "Clad (Copper-Nickel)"
        enriched["melt_value_estimate"] = "< $0.01"
        enriched["pcgs_data"]         = None
        enriched["pcgs_number"]       = None

        # ── Step 1: Determine metal composition from year + denomination ──
        silver_result = self._determine_silver(year, denomination, series)
        gold_result   = self._determine_gold(year, denomination, series)

        if silver_result:
            comp, troy_oz = silver_result
            enriched["is_silver"]      = True
            enriched["silver_troy_oz"] = troy_oz
            enriched["metal_content"]  = comp
            melt_est = self._estimate_melt_value(troy_oz)
            enriched["melt_value_estimate"] = melt_est
            logging.info(f"[PCGS] Silver detected: {comp}  •  {troy_oz:.5f} troy oz  •  Melt ≈ {melt_est}")
        elif gold_result:
            comp, troy_oz = gold_result
            enriched["is_gold"]        = True
            enriched["gold_troy_oz"]   = troy_oz
            enriched["metal_content"]  = comp
            melt_est = self._estimate_gold_melt_value(troy_oz)
            enriched["melt_value_estimate"] = melt_est
            logging.info(f"[PCGS] Gold detected: {comp}  •  {troy_oz:.5f} troy oz  •  Melt ≈ {melt_est}")
        else:
            logging.info(f"[PCGS] Not precious: {year} {denomination} {series}")

        # ── Step 2: PCGS API lookup (if token is available) ──────────────
        if self.token:
            pcgs_no = self._resolve_pcgs_number(year, denomination, series, mint_mark)
            if pcgs_no:
                enriched["pcgs_number"] = pcgs_no
                pcgs_data = self._fetch_coinfacts(pcgs_no)
                if pcgs_data:
                    enriched["pcgs_data"] = pcgs_data
                    # Override metal_content if PCGS has a more precise answer
                    pcgs_metal = pcgs_data.get("metalContent") or pcgs_data.get("composition")
                    if pcgs_metal and not enriched["is_silver"] and not enriched["is_gold"]:
                        enriched["metal_content"] = pcgs_metal
                    logging.info(f"[PCGS] CoinFacts retrieved → PCGS#{pcgs_no}")
        else:
            logging.warning("[PCGS] No PCGS_ACCESS_TOKEN in .env — skipping API lookup.")

        return enriched

    # ─── Silver Determination ─────────────────────────────────────────────────

    def _determine_silver(self, year, denomination: str, series: str):
        """
        Returns (composition_str, troy_oz_ag) if the coin is silver, else None.
        Uses year-range rules — no network call required.
        """
        if not year:
            return None
        try:
            year_int = int(year)
        except (ValueError, TypeError):
            return None

        combined = f"{denomination} {series}".lower()

        # Exclude gold coins from silver detection
        gold_keywords = ["gold", "half eagle", "quarter eagle", "double eagle"]
        if any(gkw in combined for gkw in gold_keywords) and "silver" not in combined:
            return None

        for keywords, year_range, is_silver, comp, troy_oz in _SILVER_YEAR_RULES:
            if not is_silver:
                continue
            if year_int not in year_range:
                continue
            if any(kw in combined for kw in keywords):
                return (comp, troy_oz)

        return None

    def _fetch_live_silver_spot(self) -> float:
        """
        Fetches the current silver spot price from Yahoo Finance via yfinance.
        Includes a 60-minute cache. Falls back to _DEFAULT_SPOT if API fails.
        """
        now = time.time()
        if PCGSService._live_spot_cache and (now - PCGSService._last_spot_update < PCGSService._CACHE_TTL):
            return PCGSService._live_spot_cache

        logging.info("[PCGS] Fetching live silver spot price from Yahoo Finance (SI=F)...")
        try:
            # Use Comex Silver Futures (SI=F) as a reliable proxy for spot
            ticker = yf.Ticker("SI=F")
            # Get the latest close price from the current day
            hist = ticker.history(period="1d")
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])
                if price > 0:
                    PCGSService._live_spot_cache = price
                    PCGSService._last_spot_update = now
                    logging.info(f"[PCGS] Live silver spot updated: ${price:.2f}/oz")
                    return price
            
            logging.warning("[PCGS] yfinance returned empty/zero data for SI=F.")
        except Exception as e:
            logging.error(f"[PCGS] Failed to fetch live silver spot: {e}")

        # Fallback to cache if exists, else default
        return PCGSService._live_spot_cache or PCGSService._DEFAULT_SPOT

    def _estimate_melt_value(self, troy_oz: float) -> str:
        """
        Returns an approximate melt value string using the live spot price.
        """
        spot = self._fetch_live_silver_spot()
        melt = troy_oz * spot
        return f"~${melt:.2f}"

    # ─── Gold Determination ───────────────────────────────────────────────────

    # --- Caching for live gold spot price ---
    _live_gold_spot_cache = None
    _last_gold_spot_update = 0

    def _determine_gold(self, year, denomination: str, series: str):
        """
        Returns (composition_str, troy_oz_au) if the coin is gold, else None.
        Uses year-range rules — no network call required.
        """
        if not year:
            return None
        try:
            year_int = int(year)
        except (ValueError, TypeError):
            return None

        combined = f"{denomination} {series}".lower()

        # Exclude silver coins from gold detection
        if "silver" in combined or "clad" in combined:
            return None

        # 1. Modern Gold Eagle (1986-present)
        if "gold eagle" in combined or ("eagle" in combined and year_int >= 1986):
            if "50" in combined or "fifty" in combined:
                return ("Gold (91.67% Gold, 3% Silver, 5.33% Copper)", 1.00)
            elif "25" in combined or "twenty-five" in combined:
                return ("Gold (91.67% Gold, 3% Silver, 5.33% Copper)", 0.50)
            elif "10" in combined or "ten" in combined:
                return ("Gold (91.67% Gold, 3% Silver, 5.33% Copper)", 0.25)
            elif "5" in combined or "five" in combined:
                return ("Gold (91.67% Gold, 3% Silver, 5.33% Copper)", 0.10)
            return ("Gold (91.67% Gold, 3% Silver, 5.33% Copper)", 1.00)

        # 2. Modern Gold Buffalo (2006-present)
        if "buffalo" in combined and "gold" in combined and year_int >= 2006:
            return ("Gold (99.99% Gold)", 1.00)

        # 3. Pre-1933 Gold Coins (range rules)
        for keywords, year_range, comp, troy_oz in _GOLD_YEAR_RULES:
            if year_int not in year_range:
                continue
            if any(kw in combined for kw in keywords):
                return (comp, troy_oz)

        return None

    def _fetch_live_gold_spot(self) -> float:
        """
        Fetches the current gold spot price from Yahoo Finance via yfinance.
        Includes a 60-minute cache. Falls back to $2350.0 if API fails.
        """
        now = time.time()
        if PCGSService._live_gold_spot_cache and (now - PCGSService._last_gold_spot_update < PCGSService._CACHE_TTL):
            return PCGSService._live_gold_spot_cache

        logging.info("[PCGS] Fetching live gold spot price from Yahoo Finance (GC=F)...")
        try:
            ticker = yf.Ticker("GC=F")
            hist = ticker.history(period="1d")
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])
                if price > 0:
                    PCGSService._live_gold_spot_cache = price
                    PCGSService._last_gold_spot_update = now
                    logging.info(f"[PCGS] Live gold spot updated: ${price:.2f}/oz")
                    return price
            
            logging.warning("[PCGS] yfinance returned empty/zero data for GC=F.")
        except Exception as e:
            logging.error(f"[PCGS] Failed to fetch live gold spot: {e}")

        return PCGSService._live_gold_spot_cache or 2350.0

    def _estimate_gold_melt_value(self, troy_oz: float) -> str:
        """
        Returns an approximate gold melt value string using the live spot price.
        """
        spot = self._fetch_live_gold_spot()
        melt = troy_oz * spot
        return f"~${melt:.2f}"


    # ─── PCGS Number Resolution ────────────────────────────────────────────────

    def _resolve_pcgs_number(self, year, denomination: str, series: str, mint_mark: str) -> int | None:
        """
        Returns the best-matching PCGS catalog number for the given coin.
        Tries the local map first, then falls back to the CoinFacts search API.
        """
        if not year:
            return None
        try:
            year_int = int(year)
        except (ValueError, TypeError):
            return None

        denom_lower  = denomination.lower()
        series_lower = series.lower()

        # Search local map
        for (series_key, denom_key, year_range), base_no in _PCGS_MAP.items():
            if year_int not in year_range:
                continue
            if denom_key.lower() not in denom_lower and denom_key.lower() not in series_lower:
                continue
            if series_key.lower() not in series_lower and series_key.lower() not in denom_lower:
                continue
            # Apply mint mark offset (P=+0, D=+1, S=+2, O=+3, CC=+4)
            offset = {"": 0, "P": 0, "D": 1, "S": 2, "O": 3, "CC": 4, "W": 5}.get(mint_mark, 0)
            return base_no + offset

        # Fallback: try the API's CoinFacts search endpoint
        try:
            resp = requests.get(
                f"{_BASE}/coindetail/GetCoinFactsIdByCoinName",
                headers=self.headers,
                params={"CoinName": f"{year} {denomination} {series}".strip()},
                timeout=5,
            )
            if resp.status_code == 200:
                result = resp.json()
                if isinstance(result, list) and result:
                    return result[0].get("PCGSNo")
                elif isinstance(result, dict):
                    return result.get("PCGSNo")
        except Exception as e:
            logging.warning(f"[PCGS] Search API call failed: {e}")

        return None

    # ─── PCGS CoinFacts Fetch ─────────────────────────────────────────────────

    def _fetch_coinfacts(self, pcgs_no: int) -> dict | None:
        """
        Calls the GetCoinFactsByPCGSNo endpoint and returns the response dict.
        Returns None on any failure so the caller degrades gracefully.
        """
        try:
            resp = requests.get(
                f"{_BASE}/coindetail/GetCoinFactsByPCGSNo",
                headers=self.headers,
                params={"PCGSNo": pcgs_no},
                timeout=8,
            )
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 401:
                logging.error("[PCGS] 401 Unauthorized — check PCGS_ACCESS_TOKEN in .env")
            elif resp.status_code == 429:
                logging.warning("[PCGS] 429 Rate limited — daily limit may be reached")
            else:
                logging.warning(f"[PCGS] API returned {resp.status_code}: {resp.text[:200]}")
        except requests.exceptions.Timeout:
            logging.warning("[PCGS] API request timed out")
        except Exception as e:
            logging.error(f"[PCGS] Unexpected error: {e}")
        return None

    def fetch_cert(self, cert_number: str) -> dict | None:
        """
        Looks up a PCGS-graded coin by its certificate number.
        Useful for slabbed coins the user places under the microscope.
        """
        try:
            resp = requests.get(
                f"{_BASE}/coindetail/GetCoinFactsByCertNo",
                headers=self.headers,
                params={"CertNo": cert_number},
                timeout=8,
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            logging.error(f"[PCGS] Cert lookup failed: {e}")
        return None
