import os
import requests
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from google.cloud import firestore
import google.auth
from google.genai import types

from services.greysheet_quota_service import GreysheetQuotaService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("greysheet_service")

# Production API Endpoint
BASE_URL = "https://cpgpublicapiv2.greysheet.com/api"

# Default fallback credentials for development/testing
DEFAULT_API_KEY = "1FCAE3B4-966A-4F25-AFA1-BE242C26856B"
DEFAULT_API_TOKEN = "D876F1BA-DDC4-4F80-B155-509AB3B6B970"

class GreysheetService:
    def __init__(self, db: Optional[firestore.Client] = None):
        self._db = db
        self._api_key = None
        self._api_token = None
        self._headers = None
        self._leaf_nodes_cache = None  # In-memory cache of leaf nodes
        self._collectibles_cache = {}  # Cache of node_id -> collectibles list
        self._pricing_cache = {}       # Cache of gsid -> pricing data list
        self._quota_service = GreysheetQuotaService(db=db)
        
    def _lazy_init(self):
        """Lazy load credentials and setup headers."""
        if self._headers:
            return
            
        # 1. Try to read from environment variables
        self._api_key = os.environ.get("GREYSHEET_API_KEY")
        self._api_token = os.environ.get("GREYSHEET_API_TOKEN")
        
        # 2. Try Firestore config if DB is available and env vars are missing
        if (not self._api_key or not self._api_token) and self._db:
            try:
                doc = self._db.collection("config").document("greysheet").get()
                if doc.exists:
                    data = doc.to_dict()
                    self._api_key = self._api_key or data.get("apiKey")
                    self._api_token = self._api_token or data.get("apiToken")
                    logger.info("[Greysheet] Loaded credentials from Firestore config/greysheet")
            except Exception as e:
                logger.warning(f"[Greysheet] Failed to load credentials from Firestore: {e}")
                
        # 3. Fallback to user-provided dev credentials
        self._api_key = self._api_key or DEFAULT_API_KEY
        self._api_token = self._api_token or DEFAULT_API_TOKEN
        
        self._headers = {
            "x-api-key": self._api_key,
            "x-api-token": self._api_token,
            "Content-Type": "application/json"
        }
        logger.info("[Greysheet] GreysheetService initialized.")

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        self._lazy_init()
        
        # Hard cap check before making external call
        if self._quota_service.is_hard_cap_engaged():
            logger.warning(f"[Greysheet] Hard cap (50,000 calls) engaged. Skipping external call to {endpoint}.")
            return None

        url = f"{BASE_URL}/{endpoint}"
        query_params = dict(params) if params else {}
        if "apiLevel" not in query_params:
            query_params["apiLevel"] = "advanced"
        try:
            # Bypass SSL certificate verification for expired host certs
            response = requests.get(url, headers=self._headers, params=query_params, verify=False, timeout=15)
            if response.status_code == 200:
                # Increment atomic call count on successful response
                self._quota_service.increment_call_count()
                return response.json()
            else:
                logger.error(f"[Greysheet] API Error: {url} returned status {response.status_code}: {response.text[:200]}")
                return None
        except Exception as e:
            logger.error(f"[Greysheet] HTTP Error calling {url}: {e}")
            return None

    def get_node_children(self, node_id: int) -> List[Dict[str, Any]]:
        """Fetch children of a parent node."""
        res = self._get("GetNodeChildrenRequest", {"NodeId": node_id})
        return res.get("Data", []) if res else []

    def get_collectible_by_node(self, node_id: int) -> List[Dict[str, Any]]:
        """Fetch all collectibles under a leaf node with 24h cache TTL."""
        if node_id in self._collectibles_cache:
            return self._collectibles_cache[node_id]

        # 1. Try Firestore Cache
        cache_key = f"node_collectible_{node_id}"
        if self._db:
            try:
                doc_ref = self._db.collection("greysheet_cache").document(cache_key)
                doc = doc_ref.get()
                if doc.exists:
                    cache_data = doc.to_dict()
                    updated_at = cache_data.get("updated_at")
                    if self._quota_service.is_cache_valid(updated_at, ttl_hours=24) or self._quota_service.is_hard_cap_engaged():
                        logger.info(f"[Greysheet Cache] Hit (24h TTL) for {cache_key}")
                        data = cache_data.get("data", [])
                        self._collectibles_cache[node_id] = data
                        return data
            except Exception as e:
                logger.warning(f"[Greysheet Cache] Error reading cache for {cache_key}: {e}")

        # 2. Call direct API
        res = self._get("GetCollectibleByNodeRequest", {"NodeId": node_id})
        data = res.get("Data", []) if res else []
        self._collectibles_cache[node_id] = data

        # 3. Write Firestore Cache
        if self._db and data:
            try:
                self._db.collection("greysheet_cache").document(cache_key).set({
                    "data": data,
                    "updated_at": datetime.now(timezone.utc)
                })
                logger.info(f"[Greysheet Cache] Wrote cache for {cache_key}")
            except Exception as e:
                logger.warning(f"[Greysheet Cache] Error writing cache for {cache_key}: {e}")

        return data

    def get_pricing(self, gsid: int) -> List[Dict[str, Any]]:
        """Fetch pricing table for a specific GSID with 24h cache TTL."""
        if gsid in self._pricing_cache:
            return self._pricing_cache[gsid]

        # 1. Try Firestore Cache (24h TTL)
        cache_key = f"pricing_{gsid}"
        if self._db:
            try:
                doc_ref = self._db.collection("greysheet_cache").document(cache_key)
                doc = doc_ref.get()
                if doc.exists:
                    cache_data = doc.to_dict()
                    updated_at = cache_data.get("updated_at")
                    if self._quota_service.is_cache_valid(updated_at, ttl_hours=24) or self._quota_service.is_hard_cap_engaged():
                        logger.info(f"[Greysheet Cache] Hit (24h TTL) for {cache_key}")
                        data = cache_data.get("data", [])
                        self._pricing_cache[gsid] = data
                        return data
            except Exception as e:
                logger.warning(f"[Greysheet Cache] Error reading cache for {cache_key}: {e}")

        # 2. Call direct API
        res = self._get("GetPricingRequest", {"Gsid": gsid})
        data = res.get("Data", []) if res else []
        self._pricing_cache[gsid] = data

        # 3. Write Firestore Cache
        if self._db and data:
            try:
                self._db.collection("greysheet_cache").document(cache_key).set({
                    "data": data,
                    "updated_at": datetime.now(timezone.utc)
                })
                logger.info(f"[Greysheet Cache] Wrote cache for {cache_key}")
            except Exception as e:
                logger.warning(f"[Greysheet Cache] Error writing cache for {cache_key}: {e}")

        return data

    def get_collectible(self, gsid: int) -> Optional[Dict[str, Any]]:
        """Fetch a single collectible's metadata by GSID with 24h cache TTL."""
        # 1. Try Firestore Cache
        cache_key = f"collectible_{gsid}"
        if self._db:
            try:
                doc_ref = self._db.collection("greysheet_cache").document(cache_key)
                doc = doc_ref.get()
                if doc.exists:
                    cache_data = doc.to_dict()
                    updated_at = cache_data.get("updated_at")
                    if self._quota_service.is_cache_valid(updated_at, ttl_hours=24) or self._quota_service.is_hard_cap_engaged():
                        logger.info(f"[Greysheet Cache] Hit (24h TTL) for {cache_key}")
                        return cache_data.get("data")
            except Exception as e:
                logger.warning(f"[Greysheet Cache] Error reading cache for {cache_key}: {e}")

        # 2. Call direct API
        res = self._get("GetCollectibleRequest", {"Gsid": gsid})
        data_val = None
        if res and res.get("Data"):
            data = res.get("Data")
            data_val = data[0] if isinstance(data, list) and len(data) > 0 else None

        # 3. Write Firestore Cache
        if self._db and data_val:
            try:
                self._db.collection("greysheet_cache").document(cache_key).set({
                    "data": data_val,
                    "updated_at": datetime.now(timezone.utc)
                })
                logger.info(f"[Greysheet Cache] Wrote cache for {cache_key}")
            except Exception as e:
                logger.warning(f"[Greysheet Cache] Error writing cache for {cache_key}: {e}")

        return data_val

    def crawl_all_us_leaf_nodes(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Recursively crawl U.S. Coins (NodeId=1) to retrieve all leaf nodes.
        Leaf nodes are nodes with CollectibleChildrenCountLive > 0 or NodeChildrenCountLive == 0.
        """
        if self._leaf_nodes_cache and not force_refresh:
            return self._leaf_nodes_cache

        logger.info("[Greysheet] Crawling U.S. Coins catalog nodes...")
        leaf_nodes = []
        queue = [{"Id": 1, "Name": "U.S. Coins"}]  # Start with U.S. Coins
        visited = set()

        while queue:
            current = queue.pop(0)
            node_id = current["Id"]
            if node_id in visited:
                continue
            visited.add(node_id)

            children = self.get_node_children(node_id)
            if not children:
                # Leaf node
                leaf_nodes.append(current)
            else:
                for child in children:
                    child_id = child.get("Id")
                    child_name = child.get("Name", "")
                    live_collectibles = child.get("CollectibleChildrenCountLive", 0)
                    live_children = child.get("NodeChildrenCountLive", 0)
                    
                    child_info = {
                        "Id": child_id,
                        "Name": child_name,
                        "ParentNode_Id": node_id
                    }

                    if live_collectibles > 0:
                        leaf_nodes.append(child_info)
                    
                    if live_children > 0:
                        queue.append(child_info)
                    elif live_collectibles == 0:
                        leaf_nodes.append(child_info)

        self._leaf_nodes_cache = leaf_nodes
        logger.info(f"[Greysheet] Found {len(leaf_nodes)} U.S. Coins leaf nodes.")
        return leaf_nodes

    # ── Denomination normaliser ───────────────────────────────────────────────
    # Maps how the app stores denominations → Greysheet catalog naming.
    # Greysheet uses "$5 Liberty Gold", "$10 Indian Gold", etc.
    # Our DB stores "Five Dollars (Half Eagle)", "Ten Dollars (Eagle)", etc.
    # Without this map the fuzzy matcher picks up the wrong keyword (e.g. "half")
    # from "Half Eagle" and matches Half Cents/Dimes/Dollars instead of gold coins.
    _DENOM_NORM_MAP: List[tuple] = [
        # Word-form gold denominations (must be checked BEFORE generic keyword fallback)
        ("double eagle",    "$20 gold"),
        ("twenty dollar",   "$20 gold"),
        ("twenty dollars",  "$20 gold"),
        ("ten dollar",      "$10 gold"),
        ("ten dollars",     "$10 gold"),
        ("eagle",           "$10 gold"),   # plain "eagle" = $10 gold eagle
        ("five dollar",     "$5 gold"),
        ("five dollars",    "$5 gold"),
        ("half eagle",      "$5 gold"),    # half eagle = $5 face value gold
        ("quarter eagle",   "$2.50 gold"),
        ("two and half",    "$2.50 gold"),
        ("three dollar",    "$3 gold"),
        ("three dollars",   "$3 gold"),
        ("four dollar",     "$4 gold"),
        ("stella",          "$4 gold"),
        ("one dollar gold", "$1 gold"),
    ]

    @staticmethod
    def _normalise_denomination(denomination: str) -> List[str]:
        """
        Returns a list of Greysheet-compatible search terms for a given stored
        denomination string.  Always returns the original denomination as well so
        exact or partial matches still work for standard coins.
        """
        terms = [denomination.lower()]
        denom_lower = denomination.lower()
        for pattern, replacement in GreysheetService._DENOM_NORM_MAP:
            if pattern in denom_lower:
                terms.insert(0, replacement)   # prefer the normalised term
                break
        return terms

    # ── Plain-language validation ──────────────────────────────────────────────

    # Series-family keywords: maps plain-language series identifiers to the
    # denomination keywords we expect to see in a Greysheet collectible name.
    # Used by validate_match() to catch cross-series mismatches without AI.
    _SERIES_FAMILIES: List[tuple] = [
        # (series keyword in coin data,  must-appear in greysheet name,  must-NOT-appear)
        ("presidential",      "presidential",        ["morgan", "peace", "barber", "bust", "trade", "seated", "eisenhower"]),
        ("sacagawea",         "sacagawea",           ["morgan", "peace", "barber", "bust", "trade", "seated"]),
        ("native american",   "native american",     ["morgan", "peace", "barber"]),
        ("american innovation", "american innovation", ["morgan", "barber", "quarter", "dime"]),
        ("morgan",            "morgan",              ["peace", "barber", "presidential", "sacagawea"]),
        ("peace",             "peace",               ["morgan", "barber", "presidential"]),
        ("barber quarter",    "barber",              ["morgan", "peace", "presidential", "half dollar", "dime"]),
        ("barber dime",       "barber",              ["morgan", "peace", "presidential", "quarter", "half"]),
        ("barber half",       "barber",              ["morgan", "peace", "presidential", "quarter", "dime"]),
        ("kennedy",           "kennedy",             ["morgan", "peace", "barber", "walking liberty", "franklin"]),
        ("franklin",          "franklin",            ["morgan", "peace", "barber", "kennedy"]),
        ("walking liberty",   "walking liberty",     ["morgan", "peace", "barber", "kennedy", "franklin"]),
        ("standing liberty",  "standing liberty",    ["barber", "washington", "statehood"]),
        ("washington",        "washington",          ["standing liberty", "barber quarter"]),
        ("lincoln",           "lincoln",             ["indian cent", "flying eagle", "large cent"]),
        ("indian cent",       "indian",              ["lincoln", "flying eagle", "large cent"]),
        ("flying eagle",      "flying eagle",        ["lincoln", "indian"]),
        ("buffalo",           "buffalo",             ["jefferson", "liberty"]),
        ("jefferson",         "jefferson",           ["buffalo", "liberty"]),
        ("mercury",           "mercury",             ["barber", "roosevelt", "seated"]),
        ("roosevelt",         "roosevelt",           ["mercury", "barber", "seated"]),
        ("seated liberty",    "seated",              ["barber", "morgan", "peace"]),
        ("bust",              "bust",                ["barber", "morgan", "seated"]),
        ("trade dollar",      "trade",               ["morgan", "peace", "seated"]),
        ("commemorative",     "commemorative",       []),
        ("proof",             "proof",               []),
    ]

    @staticmethod
    def _year_in_name(name_lower: str, coin_year: str) -> bool:
        """Return True if coin_year is consistent with any year or range in name_lower."""
        import re as _re
        if not coin_year or not coin_year.isdigit():
            return True  # no year to check — allow
        yr = int(coin_year)
        # Explicit range e.g. "1892-1916"
        for m in _re.finditer(r'(\d{4})\s*[-\u2013]\s*(\d{4})', name_lower):
            if int(m.group(1)) <= yr <= int(m.group(2)):
                return True
        # Single year in name
        years_in_name = [int(y) for y in _re.findall(r'\b(\d{4})\b', name_lower)]
        if years_in_name:
            return yr in years_in_name
        return True  # no year present in name — allow

    def validate_match(
        self,
        greysheet_name: str,
        coin_data: Dict[str, Any],
        genai_client: Optional[Any] = None,
        primary_model: str = "gemini-3.5-flash",
    ) -> tuple:  # (is_valid: bool, reason: str)
        """
        Plain-language cross-check: does the Greysheet collectible name make sense
        for this coin?

        Returns (True, "ok") when the match is plausible.
        Returns (False, <reason>) when the match is clearly wrong.

        Checks (in order, no AI required for the first three):
          1. Year consistency
          2. Mint-mark consistency
          3. Series/denomination family cross-check via _SERIES_FAMILIES
          4. Gemini semantic check (optional, only when coin_data has a genai_client)
        """
        import re as _re

        if not greysheet_name:
            return False, "greysheet_name is empty"

        gs_lower = greysheet_name.lower()
        year = str(coin_data.get("Year") or coin_data.get("year") or "").strip()
        mint = str(coin_data.get("Mint Mark") or coin_data.get("mintMark") or
                   coin_data.get("MintMark") or "").strip().upper()
        series = str(coin_data.get("Program/Series") or coin_data.get("series") or
                     coin_data.get("ProgramSeries") or "").lower()
        denom = str(coin_data.get("Denomination") or coin_data.get("denomination") or "").lower()
        coin_desc = f"{series} {denom}".strip()

        # ── Check 1: Year ─────────────────────────────────────────────────────
        if not self._year_in_name(gs_lower, year):
            return False, (
                f"Year mismatch: coin is {year} but greysheet name "
                f"'{greysheet_name}' implies a different year."
            )

        # ── Check 2: Mint mark ────────────────────────────────────────────────
        # Only flag when the name contains a specific mint and it doesn't match.
        mint_kw_map = {"P": ["philadelphia", "-p "], "D": ["-d "], "S": ["-s "],
                       "O": ["-o "], "CC": ["carson city", "-cc"], "W": ["-w "]}
        if mint and mint in mint_kw_map:
            # Does the name assert a different mint?
            for other_mint, other_kws in mint_kw_map.items():
                if other_mint == mint:
                    continue
                if any(kw in gs_lower for kw in other_kws):
                    return False, (
                        f"Mint mismatch: coin is {mint} but greysheet name "
                        f"'{greysheet_name}' appears to be {other_mint}."
                    )

        # ── Check 3: Series family ─────────────────────────────────────────────
        for series_kw, gs_must_have, gs_must_not_have in self._SERIES_FAMILIES:
            if series_kw in coin_desc:
                if gs_must_have and gs_must_have not in gs_lower:
                    return False, (
                        f"Series mismatch: coin is '{series_kw}' but "
                        f"greysheet name '{greysheet_name}' does not contain '{gs_must_have}'."
                    )
                for bad_kw in gs_must_not_have:
                    if bad_kw in gs_lower:
                        return False, (
                            f"Series mismatch: coin is '{series_kw}' but "
                            f"greysheet name '{greysheet_name}' contains '{bad_kw}' — wrong series."
                        )
                break  # matched a family, no need to check further

        # ── Check 4: Gemini semantic check (optional) ─────────────────────────
        if genai_client:
            theme = str(coin_data.get("Theme/Subject") or "").strip()
            prompt = (
                f"You are a numismatic expert. Answer ONLY with JSON.\n\n"
                f"Does the Greysheet series name \"{greysheet_name}\" correctly "
                f"describe a coin with these attributes?\n"
                f"  Year: {year}\n"
                f"  Mint Mark: {mint}\n"
                f"  Denomination: {denom}\n"
                f"  Series/Program: {series}\n"
                f"  Theme/Subject: {theme}\n\n"
                f"Return: {{\"match\": true|false, \"reason\": \"<one sentence>\"}}"
            )
            try:
                resp = genai_client.models.generate_content(
                    model=primary_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json"),
                )
                res = json.loads(resp.text)
                if not res.get("match", True):
                    return False, f"Gemini: {res.get('reason', 'series mismatch')}"
            except Exception as e:
                logger.warning(f"[Greysheet] validate_match Gemini check failed: {e} — skipping AI check")

        return True, "ok"

    # ── GSID resolution ───────────────────────────────────────────────────────

    def resolve_gsid_hybrid(
        self,
        coin_data: Dict[str, Any],
        genai_client: Optional[Any] = None,
        primary_model: str = "gemini-3.5-flash",
    ) -> Optional[tuple]:  # (gsid: int, collectible_name: str) or None
        """
        Map a coin to a Greysheet GSID via plain-language matching.

        Returns (gsid, collectible_name) so callers always know *what* the GSID
        represents in human-readable form — not just an opaque integer.

        Priority order:
          1. Fast-path: if coin already has a stored greysheetName that passes
             validate_match(), trust the cached greysheetGsid and return early.
          2. PCGS number exact match.
          3. Gemini picks from denomination-filtered candidates.
          4. Text-score fallback.

        On success, the result is validated with validate_match() before returning.
        If validation fails the candidate is discarded and we return None, letting
        the caller decide whether to retry later.
        """
        # ── Guardrails ────────────────────────────────────────────────────────
        item_type = str(coin_data.get("item_type") or coin_data.get("Item Type") or
                        coin_data.get("Item_Type") or "").lower()
        if (item_type in ["paper_currency", "medal", "supply"] or
                "medal" in item_type or "paper" in item_type or "supply" in item_type):
            logger.info(f"[Greysheet] Guardrail: item_type='{item_type}' is non-coin. Skipping.")
            return None

        country = str(coin_data.get("Country") or coin_data.get("country") or "").lower().strip()
        if country and country not in ["us", "usa", "united states", "unknown"]:
            logger.info(f"[Greysheet] Guardrail: country='{country}' is non-U.S. Skipping.")
            return None

        # ── Extract coin attributes ───────────────────────────────────────────
        pcgs_number = (coin_data.get("PCGSNo") or coin_data.get("pcgs_number") or
                       coin_data.get("pcgsNo") or coin_data.get("PCGS Number"))
        year        = str(coin_data.get("Year") or coin_data.get("year") or "")
        mint_mark   = str(coin_data.get("MintMark") or coin_data.get("mintMark") or
                          coin_data.get("Mint Mark") or "").upper()
        denomination = str(coin_data.get("Denomination") or coin_data.get("denomination") or "")
        series      = str(coin_data.get("ProgramSeries") or coin_data.get("programSeries") or
                          coin_data.get("series") or coin_data.get("Program/Series") or "")
        variety     = str(coin_data.get("Variety") or coin_data.get("variety") or "")

        logger.info(
            f"[Greysheet] Resolving: Year={year}, Mint={mint_mark}, "
            f"Denomination={denomination}, Series={series}, PCGS={pcgs_number}"
        )

        # ── Fast-path: cached GSID with validated name ────────────────────────
        cached_gsid = coin_data.get("greysheetGsid")
        cached_name = coin_data.get("greysheetName")
        if cached_gsid and cached_name:
            valid, reason = self.validate_match(cached_name, coin_data, genai_client, primary_model)
            if valid:
                logger.info(
                    f"[Greysheet] Fast-path: cached GSID {cached_gsid} "
                    f"('{cached_name}') passed validation."
                )
                return (int(cached_gsid), cached_name)
            else:
                logger.warning(
                    f"[Greysheet] Fast-path rejected: cached GSID {cached_gsid} "
                    f"('{cached_name}') failed validation — {reason}. Re-resolving."
                )
                # Fall through to full resolution below.

        # ── Step 1: Find leaf nodes by denomination keyword ───────────────────
        leaf_nodes = self.crawl_all_us_leaf_nodes()
        denom_terms = self._normalise_denomination(denomination) if denomination else []

        matched_nodes = []
        denom_lower = denomination.lower()
        primary_kw = None

        if "double eagle" in denom_lower or "twenty" in denom_lower or "$20" in denom_lower:
            primary_kw = "$20"
        elif "half eagle" in denom_lower or "five dollar" in denom_lower or "five dollars" in denom_lower or "$5" in denom_lower:
            primary_kw = "$5"
        elif "quarter eagle" in denom_lower or "two and half" in denom_lower or "$2.5" in denom_lower or "$2.50" in denom_lower:
            primary_kw = "$2.50"
        elif "ten dollar" in denom_lower or "ten dollars" in denom_lower or "$10" in denom_lower:
            primary_kw = "$10"
        elif "three dollar" in denom_lower or "$3" in denom_lower:
            primary_kw = "$3"
        elif "quarter" in denom_lower:
            primary_kw = "quarter"
        elif "dime" in denom_lower:
            primary_kw = "dime"
        elif "nickel" in denom_lower or "five cents" in denom_lower or "5c" in denom_lower:
            primary_kw = "nickel"
        elif "cent" in denom_lower or "penny" in denom_lower or "1c" in denom_lower:
            primary_kw = "cent"
        elif "half dollar" in denom_lower or ("half" in denom_lower and "dollar" in denom_lower):
            primary_kw = "half dollar"
        elif "half cent" in denom_lower:
            primary_kw = "half cent"
        elif "half dime" in denom_lower:
            primary_kw = "half dime"
        elif "dollar" in denom_lower or "$1" in denom_lower or "1$" in denom_lower:
            primary_kw = "dollar"

        if primary_kw:
            for node in leaf_nodes:
                node_name_lower = node["Name"].lower()
                if primary_kw == "half dollar":
                    if "half dollar" in node_name_lower or "halves" in node_name_lower:
                        matched_nodes.append(node)
                elif primary_kw in node_name_lower:
                    matched_nodes.append(node)

        # Fuzzy fallback on series name
        if not matched_nodes:
            logger.info("[Greysheet] No primary keyword match. Trying series-name fuzzy fallback.")
            search_terms = []
            if series:
                search_terms.append(series.lower())
            search_terms.extend(denom_terms)
            for node in leaf_nodes:
                node_name_lower = node["Name"].lower()
                for term in search_terms:
                    if term in node_name_lower or node_name_lower in term:
                        matched_nodes.append(node)
                        break

        # ── Step 2: Fetch candidates under matched nodes ──────────────────────
        candidates = []
        for node in matched_nodes:
            node_id = node["Id"]
            logger.info(f"[Greysheet] Fetching collectibles for node: {node['Name']} (NodeId={node_id})")
            candidates.extend(self.get_collectible_by_node(node_id))

        if not candidates:
            logger.warning("[Greysheet] No candidate collectibles found.")
            return None

        # ── Step 3: PCGS number exact match ───────────────────────────────────
        if pcgs_number:
            pcgs_str = str(pcgs_number).strip()
            for cand in candidates:
                if str(cand.get("PcgsNumber", "")).strip() == pcgs_str:
                    name = cand["Name"]
                    gsid = cand["Gsid"]
                    valid, reason = self.validate_match(name, coin_data, genai_client, primary_model)
                    if valid:
                        logger.info(f"[Greysheet] PCGS match: '{name}' (GSID={gsid})")
                        return (int(gsid), name)
                    logger.warning(f"[Greysheet] PCGS match '{name}' failed validation: {reason}")

        # ── Step 4: Gemini picks from candidates ──────────────────────────────
        if genai_client:
            logger.info(f"[Greysheet] Invoking Gemini to select from {len(candidates)} candidates.")
            candidate_list_str = "".join(
                f"- GSID: {c['Gsid']} | Name: {c['Name']} | PCGS No: {c.get('PcgsNumber', 'N/A')}\n"
                for c in candidates
            )
            theme = str(coin_data.get("Theme/Subject") or "")
            prompt = f"""You are an expert numismatic data mapper. Select the single best Greysheet collectible for this coin.

COIN:
  Year: {year}
  Mint Mark: {mint_mark}
  Denomination: {denomination}
  Series/Program: {series}
  Theme/Subject: {theme}
  Variety: {variety}

CANDIDATES:
{candidate_list_str}

Return ONLY JSON: {{"gsid": <int or null>, "confidence": <0.0-1.0>, "explanation": "<one sentence>"}}
Set gsid to null if no candidate is a good match. Do not output markdown."""
            try:
                resp = genai_client.models.generate_content(
                    model=primary_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json"),
                )
                res_json = json.loads(resp.text)
                gsid = res_json.get("gsid")
                confidence = res_json.get("confidence", 0.0)
                logger.info(f"[Greysheet AI] Gemini response: {res_json}")
                if gsid and confidence >= 0.7:
                    # Find the collectible name for the chosen GSID
                    chosen = next((c for c in candidates if c["Gsid"] == gsid), None)
                    name = chosen["Name"] if chosen else f"GSID {gsid}"
                    valid, reason = self.validate_match(name, coin_data, genai_client, primary_model)
                    if valid:
                        logger.info(f"[Greysheet AI] Validated: '{name}' (GSID={gsid}, confidence={confidence})")
                        return (int(gsid), name)
                    logger.warning(
                        f"[Greysheet AI] Gemini chose GSID {gsid} ('{name}') "
                        f"but validation failed: {reason}. Discarding."
                    )
            except Exception as e:
                logger.error(f"[Greysheet AI] Gemini resolution failed: {e}")

        # ── Step 5: Text-score fallback ───────────────────────────────────────
        logger.info("[Greysheet] Falling back to text-score matching.")
        import re as _re
        name_val  = coin_data.get("Name") or coin_data.get("name")
        theme_val = coin_data.get("Theme/Subject") or coin_data.get("theme")
        descriptive_terms = []
        for src in [name_val, theme_val, variety]:
            if src:
                descriptive_terms.extend(str(src).lower().replace("&", " ").replace("-", " ").split())
        stop_words = {"&", "and", "or", "the", "a", "an", "of", "in", "on", "at", "to", "with", "couple", "compact"}
        descriptive_terms = [t for t in descriptive_terms if t not in stop_words and len(t) > 2]

        best_cand, best_score = None, 0
        for cand in candidates:
            cand_name = cand["Name"].lower()
            # Skip rolls/sets for individual coins
            cand_is_set = any(x in cand_name for x in ["roll", "set", "bag", "box", "case", "folder", "tribute"])
            coin_desc   = f"{name_val or ''} {variety or ''} {theme_val or ''} {series or ''} {denomination or ''}".lower()
            coin_is_set = any(x in coin_desc for x in ["roll", "set", "bag", "box", "case", "folder", "tribute"])
            if cand_is_set and not coin_is_set:
                continue
            # Year guardrail
            if year and year.isdigit():
                cand_years = [int(y) for y in _re.findall(r'\b\d{4}\b', cand_name)]
                if cand_years:
                    range_m = _re.search(r'(\d{4})\s*[-\u2013to\s]+\s*(\d{4})', cand_name)
                    if range_m:
                        if not (int(range_m.group(1)) <= int(year) <= int(range_m.group(2))):
                            continue
                    elif int(year) not in cand_years:
                        continue
            score = 0
            if year and year in cand_name:
                score += 10
            if mint_mark and f"-{mint_mark.lower()}" in cand_name:
                score += 5
            elif mint_mark and f" {mint_mark.lower()} " in cand_name:
                score += 3
            elif not mint_mark and ("no mint mark" in cand_name or "philadelphia" in cand_name):
                score += 2
            for term in descriptive_terms:
                if term in cand_name:
                    score += 15
            if score > best_score:
                best_score, best_cand = score, cand

        if best_cand and best_score >= 10:
            name = best_cand["Name"]
            gsid = best_cand["Gsid"]
            valid, reason = self.validate_match(name, coin_data, genai_client, primary_model)
            if valid:
                logger.info(f"[Greysheet] Text-score match: '{name}' (GSID={gsid}, score={best_score})")
                return (int(gsid), name)
            logger.warning(
                f"[Greysheet] Text-score match '{name}' (GSID={gsid}) "
                f"failed validation: {reason}. Discarding."
            )

        logger.warning("[Greysheet] Could not resolve a validated GSID.")
        return None

