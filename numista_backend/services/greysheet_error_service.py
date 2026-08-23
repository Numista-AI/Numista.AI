"""
services/greysheet_error_service.py
-------------------------------------
Greysheet Known Errors feature — Phase 1 backend service.

Responsibilities:
  1. Reads denomination → node_id mapping from Firestore cache (greysheet_cache/node_map).
     Falls back to a live crawl on first run, with single-flight coalescing to prevent
     concurrent cold-start races wasting quota.
  2. Fetches collectibles for those nodes via GreysheetService (24h Firestore cache).
  3. Applies two-layer classification:
       Layer 1 — keyword candidate scan (keyword set from config/greysheet_error_keywords)
       Layer 2 — GSID allow-list overlay (config/greysheet_error_gsid_allowlist)
  4. Returns a structured list of GsErrorEntry objects with NO prices.
     Pricing is fetched lazily on the separate /known-errors/{gsid}/price route.

What this service does NOT do:
  - It does not write to users/{uid}/coins.
  - It does not write to mint_errors.
  - It does not modify any existing GreysheetService method.
  - It does not call get_pricing() on the list path.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from google.cloud import firestore

from services.greysheet_service import GreysheetService
from services.greysheet_quota_service import GreysheetQuotaService

logger = logging.getLogger("greysheet_error_service")

# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------
_NODE_MAP_COLLECTION = "greysheet_cache"
_NODE_MAP_DOC        = "node_map"
_KEYWORDS_DOC        = "greysheet_error_keywords"
_ALLOWLIST_DOC       = "greysheet_error_gsid_allowlist"
_ERRORS_CACHE_PREFIX = "errors_"        # greysheet_cache/errors_{denom}_{year}
_NODE_MAP_STALE_DAYS = 7               # Refresh node map if older than 7 days
_ERRORS_TTL_HOURS    = 24
_ERROR_PRICING_CAP   = 5_000           # Max lazy price calls/month for this feature

# Fallback keyword set — overridden by Firestore config if present.
_DEFAULT_KEYWORDS: List[str] = [
    "clip", "clipped", "curved clip", "straight clip", "ragged clip",
    "doubled die", "double die", "ddo", "ddr",
    "broadstrike", "broad strike",
    "off-center", "off center",
    "off-metal", "wrong planchet",
    "planchet crack", "lamination",
    "rotated die", "rotated reverse",
    "brockage",
    "capped die",
    "missing mintmark", "omitted mintmark",
    "repunched mintmark", "rpm",
    "overdate",
]

# Terms explicitly excluded regardless of keyword match.
_EXCLUDED_TERMS: List[str] = [
    "vam", "variety", "die variety",
    "proof", "cameo", "deep cameo",
]

# Attribution label constant (confirmed by owner 23 Aug 2026).
CPG_ATTRIBUTION_LABEL = "CPG® Data"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass
class GsErrorEntry:
    gsid: int
    name: str
    classification_source: str   # "allowlist" | "keyword_candidate"
    is_confirmed: bool
    category_hint: Optional[str] = None


# ---------------------------------------------------------------------------
# Service class
# ---------------------------------------------------------------------------
class GreysheetErrorService:
    """
    Surfaces Greysheet error/variety collectibles for the Known Errors tab.
    Uses GreysheetService (unchanged) and GreysheetQuotaService (unchanged) internally.
    """

    def __init__(self, db: firestore.Client):
        self._db = db
        self._gs = GreysheetService(db=db)
        self._quota = GreysheetQuotaService(db=db)
        # Single-flight dict reuses the same pattern as GreysheetQuotaService._single_flight_in_flight.
        # Key "node_map_seed" coalesces concurrent first-run crawls so only one live call fires.
        self._in_flight: Dict[str, asyncio.Future] = {}

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------
    async def get_error_entries(
        self,
        denomination_norm: str,
        year: int,
    ) -> List[GsErrorEntry]:
        """
        Returns a list of GsErrorEntry for the given denomination + year.
        No prices. Safe to call on every Known Errors tab open.
        """
        if self._quota.is_hard_cap_engaged():
            logger.warning("[GreysheetErrorService] Hard cap engaged — serving from cache or []")
            return await self._serve_from_cache(denomination_norm, year)

        # Check Firestore cache first
        cached = await self._read_errors_cache(denomination_norm, year)
        if cached is not None:
            return cached

        # Cache miss — fetch from Greysheet
        return await self._fetch_and_cache(denomination_norm, year)

    async def get_lazy_price(self, gsid: int) -> Optional[Dict[str, Any]]:
        """
        Fetches pricing for a single GSID. Called only when a user expands a row.
        Returns None if quota is exhausted or the call fails.
        Schema: { bid_low: float, ask_high: float, grade_count: int, attribution: str }
        """
        # Check error pricing sub-cap
        if not await self._error_pricing_budget_available():
            logger.info(f"[GreysheetErrorService] Error pricing cap reached; returning null for gsid={gsid}")
            return None

        if self._quota.is_hard_cap_engaged():
            return None

        try:
            pricing_data = self._gs.get_pricing(gsid)
            if not pricing_data:
                return None
            return self._collapse_grade_pricing(pricing_data)
        except Exception as e:
            logger.error(f"[GreysheetErrorService] get_lazy_price error for gsid={gsid}: {e}")
            return None

    # -----------------------------------------------------------------------
    # Node-map helpers (single-flight on first run)
    # -----------------------------------------------------------------------
    async def _get_node_ids_for_denomination(self, denomination_norm: str) -> List[int]:
        """
        Reads greysheet_cache/node_map from Firestore.
        If missing or stale (>7 days), triggers a crawl — with single-flight coalescing
        so concurrent cold-start requests share one future.
        """
        node_map_doc = (
            self._db.collection(_NODE_MAP_COLLECTION)
            .document(_NODE_MAP_DOC)
            .get()
        )

        if node_map_doc.exists:
            data = node_map_doc.to_dict() or {}
            updated_at = data.get("updated_at")
            is_stale = self._is_node_map_stale(updated_at)
            if not is_stale:
                return data.get(denomination_norm, [])
            # Stale: trigger async refresh (non-blocking), return current data
            asyncio.create_task(self._refresh_node_map())
            return data.get(denomination_norm, [])

        # Missing: single-flight crawl
        return await self._single_flight_seed_node_map(denomination_norm)

    def _is_node_map_stale(self, updated_at: Any) -> bool:
        if not updated_at:
            return True
        if isinstance(updated_at, datetime):
            ts = updated_at if updated_at.tzinfo else updated_at.replace(tzinfo=timezone.utc)
        else:
            return True
        return (datetime.now(timezone.utc) - ts) > timedelta(days=_NODE_MAP_STALE_DAYS)

    async def _single_flight_seed_node_map(self, denomination_norm: str) -> List[int]:
        """
        Coalesces concurrent first-run crawls. Only one crawl fires per Cloud Run instance.
        """
        key = "node_map_seed"
        if key in self._in_flight:
            try:
                node_map = await self._in_flight[key]
            except Exception:
                node_map = {}
            return node_map.get(denomination_norm, [])

        loop = asyncio.get_event_loop()
        future: asyncio.Future = loop.create_future()
        self._in_flight[key] = future
        try:
            node_map = await self._refresh_node_map()
            future.set_result(node_map)
            return node_map.get(denomination_norm, [])
        except Exception as e:
            future.set_exception(e)
            return []
        finally:
            self._in_flight.pop(key, None)

    async def _refresh_node_map(self) -> Dict[str, List[int]]:
        """
        Calls crawl_all_us_leaf_nodes(), writes result to greysheet_cache/node_map.
        This is the ONLY place in this service that calls the crawler.
        Admin seed endpoint also calls this method.
        """
        logger.info("[GreysheetErrorService] Refreshing node map via crawl_all_us_leaf_nodes()")
        try:
            raw = self._gs.crawl_all_us_leaf_nodes()
            # raw is a dict: { denomination_norm: [node_id, ...], ... }
            node_map = {k: v for k, v in raw.items() if isinstance(v, list)}
            node_map["updated_at"] = datetime.now(timezone.utc)
            self._db.collection(_NODE_MAP_COLLECTION).document(_NODE_MAP_DOC).set(
                node_map, merge=False
            )
            logger.info(f"[GreysheetErrorService] Node map written: {len(node_map)-1} denominations")
            return node_map
        except Exception as e:
            logger.error(f"[GreysheetErrorService] Node map refresh failed: {e}")
            return {}

    # -----------------------------------------------------------------------
    # Classification helpers
    # -----------------------------------------------------------------------
    def _load_keywords(self) -> List[str]:
        """Reads keyword set from Firestore config. Falls back to hardcoded list."""
        try:
            doc = self._db.collection("config").document(_KEYWORDS_DOC).get()
            if doc.exists:
                data = doc.to_dict() or {}
                kws = data.get("keywords", [])
                if isinstance(kws, list) and kws:
                    return [k.lower() for k in kws]
        except Exception as e:
            logger.warning(f"[GreysheetErrorService] Could not read keyword config: {e}")
        return _DEFAULT_KEYWORDS

    def _load_allowlist(self) -> Dict[int, Dict[str, Any]]:
        """Reads GSID allow-list from Firestore config. Returns empty dict on error."""
        try:
            doc = self._db.collection("config").document(_ALLOWLIST_DOC).get()
            if doc.exists:
                data = doc.to_dict() or {}
                # Expected shape: { "12345": { error_type_code, category, is_confirmed }, ... }
                return {int(k): v for k, v in data.items() if k.isdigit()}
        except Exception as e:
            logger.warning(f"[GreysheetErrorService] Could not read allowlist config: {e}")
        return {}

    def _is_error_candidate(self, name: str, keywords: List[str]) -> bool:
        """Layer 1: keyword scan. True if name matches any keyword and no excluded term."""
        name_lower = name.lower()
        for excluded in _EXCLUDED_TERMS:
            if excluded in name_lower:
                return False
        return any(kw in name_lower for kw in keywords)

    def _classify_entries(
        self,
        collectibles: List[Dict[str, Any]],
        keywords: List[str],
        allowlist: Dict[int, Dict[str, Any]],
    ) -> List[GsErrorEntry]:
        """
        Applies two-layer classification to a list of Greysheet collectible dicts.
        Layer 1: keyword candidate scan.
        Layer 2: GSID allow-list overlay (allow-list wins over keyword exclusion).
        """
        seen_gsids: set = set()
        entries: List[GsErrorEntry] = []

        for item in collectibles:
            gsid = item.get("Id") or item.get("gsid") or item.get("GSID")
            name = item.get("Name") or item.get("name") or ""
            if not gsid or not name:
                continue
            try:
                gsid = int(gsid)
            except (ValueError, TypeError):
                continue
            if gsid in seen_gsids:
                continue
            seen_gsids.add(gsid)

            in_allowlist = gsid in allowlist
            is_keyword_match = self._is_error_candidate(name, keywords)

            if in_allowlist:
                al = allowlist[gsid]
                entries.append(GsErrorEntry(
                    gsid=gsid,
                    name=name,
                    classification_source="allowlist",
                    is_confirmed=True,
                    category_hint=al.get("category"),
                ))
            elif is_keyword_match:
                entries.append(GsErrorEntry(
                    gsid=gsid,
                    name=name,
                    classification_source="keyword_candidate",
                    is_confirmed=False,
                    category_hint=None,
                ))

        return entries

    # -----------------------------------------------------------------------
    # Fetch + cache helpers
    # -----------------------------------------------------------------------
    async def _fetch_and_cache(
        self, denomination_norm: str, year: int
    ) -> List[GsErrorEntry]:
        node_ids = await self._get_node_ids_for_denomination(denomination_norm)
        if not node_ids:
            self._write_errors_cache(denomination_norm, year, [])
            return []

        keywords = self._load_keywords()
        allowlist = self._load_allowlist()

        all_collectibles: List[Dict[str, Any]] = []
        for node_id in node_ids:
            try:
                items = self._gs.get_collectible_by_node(node_id)
                if isinstance(items, list):
                    all_collectibles.extend(items)
            except Exception as e:
                logger.warning(f"[GreysheetErrorService] get_collectible_by_node({node_id}) failed: {e}")

        entries = self._classify_entries(all_collectibles, keywords, allowlist)
        self._write_errors_cache(denomination_norm, year, entries)
        return entries

    async def _serve_from_cache(
        self, denomination_norm: str, year: int
    ) -> List[GsErrorEntry]:
        cached = await self._read_errors_cache(denomination_norm, year)
        return cached if cached is not None else []

    async def _read_errors_cache(
        self, denomination_norm: str, year: int
    ) -> Optional[List[GsErrorEntry]]:
        cache_key = f"{_ERRORS_CACHE_PREFIX}{denomination_norm}_{year}"
        try:
            doc = self._db.collection(_NODE_MAP_COLLECTION).document(cache_key).get()
            if not doc.exists:
                return None
            data = doc.to_dict() or {}
            updated_at = data.get("updated_at")
            if not self._quota.is_cache_valid(updated_at, ttl_hours=_ERRORS_TTL_HOURS):
                return None
            raw_entries = data.get("entries", [])
            return [
                GsErrorEntry(
                    gsid=e["gsid"],
                    name=e["name"],
                    classification_source=e["classification_source"],
                    is_confirmed=e["is_confirmed"],
                    category_hint=e.get("category_hint"),
                )
                for e in raw_entries
                if isinstance(e, dict) and "gsid" in e
            ]
        except Exception as e:
            logger.warning(f"[GreysheetErrorService] Cache read error for {cache_key}: {e}")
            return None

    def _write_errors_cache(
        self, denomination_norm: str, year: int, entries: List[GsErrorEntry]
    ) -> None:
        cache_key = f"{_ERRORS_CACHE_PREFIX}{denomination_norm}_{year}"
        try:
            self._db.collection(_NODE_MAP_COLLECTION).document(cache_key).set({
                "denomination_norm": denomination_norm,
                "year": year,
                "entries": [
                    {
                        "gsid": e.gsid,
                        "name": e.name,
                        "classification_source": e.classification_source,
                        "is_confirmed": e.is_confirmed,
                        "category_hint": e.category_hint,
                    }
                    for e in entries
                ],
                "updated_at": datetime.now(timezone.utc),
            }, merge=False)
        except Exception as e:
            logger.warning(f"[GreysheetErrorService] Cache write error for {cache_key}: {e}")

    # -----------------------------------------------------------------------
    # Pricing helpers
    # -----------------------------------------------------------------------
    async def _error_pricing_budget_available(self) -> bool:
        month_key = self._quota._get_current_month_key()
        try:
            doc = self._db.collection("greysheet_usage").document(month_key).get()
            if doc.exists:
                data = doc.to_dict() or {}
                return data.get("error_pricing_calls", 0) < _ERROR_PRICING_CAP
        except Exception as e:
            logger.warning(f"[GreysheetErrorService] Could not read error_pricing_calls: {e}")
        return True  # Fail open: allow call if counter unreadable

    def _increment_error_pricing_counter(self) -> None:
        month_key = self._quota._get_current_month_key()
        try:
            self._db.collection("greysheet_usage").document(month_key).set(
                {"error_pricing_calls": firestore.Increment(1)}, merge=True
            )
        except Exception as e:
            logger.warning(f"[GreysheetErrorService] error_pricing_calls increment failed: {e}")

    def _collapse_grade_pricing(self, pricing_data: Any) -> Optional[Dict[str, Any]]:
        """
        Collapses multiple grade rows for a GSID into a single bid/ask range.
        Returns { bid_low, ask_high, grade_count, attribution }.
        """
        if not pricing_data:
            return None
        rows = pricing_data if isinstance(pricing_data, list) else [pricing_data]
        bids = []
        asks = []
        for row in rows:
            if isinstance(row, dict):
                bid = row.get("bid") or row.get("Bid") or row.get("bid_price")
                ask = row.get("ask") or row.get("Ask") or row.get("ask_price")
                if bid is not None:
                    try:
                        bids.append(float(bid))
                    except (ValueError, TypeError):
                        pass
                if ask is not None:
                    try:
                        asks.append(float(ask))
                    except (ValueError, TypeError):
                        pass
        if not bids and not asks:
            return None
        self._increment_error_pricing_counter()
        return {
            "bid_low": min(bids) if bids else None,
            "ask_high": max(asks) if asks else None,
            "grade_count": len(rows),
            "attribution": CPG_ATTRIBUTION_LABEL,
        }

    # -----------------------------------------------------------------------
    # Admin helpers (called from greysheet_admin_routes.py)
    # -----------------------------------------------------------------------
    async def admin_seed_node_map(self) -> Dict[str, Any]:
        """Admin-triggered node map seeding. Returns summary."""
        node_map = await self._refresh_node_map()
        denom_count = len([k for k in node_map if k != "updated_at"])
        return {"status": "ok", "denominations_indexed": denom_count}

    def admin_promote_to_allowlist(
        self, gsid: int, error_type_code: str, category: str
    ) -> None:
        """Adds a GSID to the allow-list. Called from the admin promote endpoint."""
        doc_ref = self._db.collection("config").document(_ALLOWLIST_DOC)
        doc_ref.set(
            {
                str(gsid): {
                    "error_type_code": error_type_code,
                    "category": category,
                    "is_confirmed": True,
                    "promoted_at": datetime.now(timezone.utc).isoformat(),
                }
            },
            merge=True,
        )
        logger.info(f"[GreysheetErrorService] GSID {gsid} promoted to allowlist (category={category})")
