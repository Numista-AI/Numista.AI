"""
catalog_service.py
------------------
Catalog read helpers, guest anti-scraping guards, personal photo toggle, and the
transactional collection-add contract (Plan.v2.1 3.1-3.3).

`add_catalog_item_in_txn` and `toggle_personal_photo_in_txn` are deliberately written
against a minimal transaction/db interface (`tx.get`, `tx.create`, `tx.update`,
`db.collection(...)`), so the exact same logic is unit-tested with an in-memory fake
and executed in production under `google.cloud.firestore.transactional`.
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from catalog_models import build_catalog_snapshot
from catalog_nac1 import KIND_TO_COLLECTION, validate_nac1

CATALOG_COLLECTION = "us_numismatics_catalog"
USER_COLLECTIONS = ("coins", "currency", "world_items")
_FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "data", "catalog_dev_fixture.json")

# In-memory guest search sliding-window rate limiter (Founder Q4: rate-limited guest search)
_guest_search_buckets: Dict[str, List[float]] = {}
GUEST_SEARCH_LIMIT_PER_MIN = 30


class CatalogError(Exception):
    """Business-rule failure carrying an HTTP status + machine-readable code."""

    def __init__(self, status_code: int, code: str, extra: Optional[dict] = None):
        super().__init__(code)
        self.status_code = status_code
        self.code = code
        self.extra = extra or {}


def reset_guest_rate_limits() -> None:
    """Clear guest rate-limit buckets (used by unit tests)."""
    _guest_search_buckets.clear()


def check_guest_search_rate_limit(
    client_id: str,
    limit: int = GUEST_SEARCH_LIMIT_PER_MIN,
    window_sec: float = 60.0,
    now_ts: Optional[float] = None,
) -> None:
    """Enforce guest search rate limit (Founder Q4: Guest search rate-limited)."""
    now = now_ts if now_ts is not None else time.time()
    key = (client_id or "anonymous").strip() or "anonymous"
    bucket = [t for t in _guest_search_buckets.get(key, []) if now - t < window_sec]
    if len(bucket) >= limit:
        _guest_search_buckets[key] = bucket
        raise CatalogError(429, "GUEST_SEARCH_RATE_LIMIT_EXCEEDED", {"limit_per_min": limit})
    bucket.append(now)
    _guest_search_buckets[key] = bucket


def verify_image_download_allowed(user: Optional[dict], nac_code: str) -> Dict[str, Any]:
    """
    Founder Q4 policy: Unauthenticated guests can browse and view the catalog,
    but NO image download is permitted without a registered account.
    """
    if not validate_nac1(nac_code):
        raise CatalogError(400, "INVALID_NAC1_CHECKSUM")
    if not user or not user.get("uid"):
        raise CatalogError(403, "IMAGE_DOWNLOAD_REQUIRES_ACCOUNT")
    return {"allowed": True, "nac_code": nac_code, "uid": user["uid"]}


# ── Reads ─────────────────────────────────────────────────────────────────────

_cache: Dict[str, Any] = {"at": 0.0, "items": []}
_CACHE_TTL = 300


def _load_fixture() -> List[dict]:
    with open(_FIXTURE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_catalog(db=None, force: bool = False) -> List[dict]:
    """All catalog docs, sorted by year. Dev fixture is used ONLY when CATALOG_DEV_FIXTURE=1."""
    if os.environ.get("CATALOG_DEV_FIXTURE") == "1":
        return sorted(_load_fixture(), key=lambda d: (d["year"], d["nac_code"]))
    now = time.time()
    if not force and _cache["items"] and now - _cache["at"] < _CACHE_TTL:
        return _cache["items"]
    items = [d.to_dict() for d in db.collection(CATALOG_COLLECTION).stream()]
    items.sort(key=lambda d: (d.get("year", 0), d.get("nac_code", "")))
    _cache.update(at=now, items=items)
    return items


def filter_catalog(
    items: List[dict],
    kind: Optional[str] = None,
    era: Optional[str] = None,
    facility: Optional[str] = None,
    state: Optional[str] = None,
    max_year: Optional[int] = None,
    q: Optional[str] = None,
    cc: Optional[str] = None,
) -> List[dict]:
    out = []
    ql = (q or "").lower().strip()
    for it in items:
        if kind and it.get("kind") != kind:
            continue
        if cc and it.get("cc") != cc:
            continue
        if era and it.get("country_era") != era:
            continue
        if facility and it.get("facility_code") != facility:
            continue
        if state and it.get("state_or_entity") != state:
            continue
        if max_year and it.get("year", 0) > max_year:
            continue
        if ql:
            hay = " ".join(
                str(it.get(k, ""))
                for k in ("title", "subtitle", "nac_code", "year_display", "series", "denomination_class")
            )
            if ql not in hay.lower():
                continue
        out.append(it)
    return out


def find_by_slug(items: List[dict], slug: str) -> Optional[dict]:
    slug = "/" + slug.strip("/")
    for it in items:
        if "/" + it.get("seo_slug", "").strip("/") == slug:
            return it
    return None


# ── Transactional collection add & personal photo toggle ─────────────────────

def add_catalog_item_in_txn(
    tx,
    db,
    uid: str,
    nac_code: str,
    tier_limit: float,
    count_fn: Callable[[Any, str], int],
    new_specimen: bool = False,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Returns {"created": bool, "doc_id": str, "collection": str, "doc": dict}.
    Raises CatalogError(400 INVALID_NAC1_CHECKSUM | 404 CATALOG_ITEM_NOT_FOUND | 403 QUOTA_EXCEEDED).
    All reads happen before the single tx.create(); no merge writes ever.
    """
    if not validate_nac1(nac_code):
        raise CatalogError(400, "INVALID_NAC1_CHECKSUM")

    catalog_snap = tx.get(db.collection(CATALOG_COLLECTION).document(nac_code))
    if not catalog_snap.exists:
        raise CatalogError(404, "CATALOG_ITEM_NOT_FOUND")
    item = catalog_snap.to_dict()

    target_col = KIND_TO_COLLECTION[item["kind"]]  # BN/MD/TK/ST can never resolve to "coins"
    col_ref = db.collection("users").document(uid).collection(target_col)

    slot = 1
    ref = col_ref.document(f"{nac_code}_SLOT1")
    existing = tx.get(ref)
    if existing.exists and not new_specimen:
        return {"created": False, "doc_id": ref.id, "collection": target_col, "doc": existing.to_dict()}
    while existing.exists:  # explicit additional specimen -> next free slot
        slot += 1
        ref = col_ref.document(f"{nac_code}_SLOT{slot}")
        existing = tx.get(ref)

    total = sum(count_fn(tx, c) for c in USER_COLLECTIONS)
    if total >= tier_limit:
        raise CatalogError(403, "QUOTA_EXCEEDED", {"count": total, "limit": tier_limit})

    now = now or datetime.now(timezone.utc)
    doc = {
        "nac_code": nac_code,
        "kind": item["kind"],
        "cc": item.get("cc", "US"),
        "slot": slot,
        "source": "us_catalog",
        "quantity": 1,
        "title": item.get("title"),
        "year": item.get("year"),
        "mint_mark": item.get("mint_mark"),
        "denomination_class": item.get("denomination_class"),
        "series": item.get("series"),
        "use_personal_photo": False,
        "custom_obverse_image_url": None,
        "custom_reverse_image_url": None,
        "catalog_snapshot": build_catalog_snapshot(item),
        "added_at": now.isoformat(),
    }
    tx.create(ref, doc)
    audit_ref = db.collection("users").document(uid).collection("collection_audit_log").document()
    tx.create(
        audit_ref,
        {
            "action": "ADD",
            "nac_code": nac_code,
            "collection": target_col,
            "doc_id": ref.id,
            "at": now.isoformat(),
        },
    )
    return {"created": True, "doc_id": ref.id, "collection": target_col, "doc": doc}


def toggle_personal_photo_in_txn(
    tx,
    db,
    uid: str,
    collection: str,
    doc_id: str,
    use_personal_photo: bool,
) -> Dict[str, Any]:
    """
    Founder Q3: Toggle between the user's personal specimen photo and the stock
    catalog image without mutating the public catalog or overwriting custom photo URLs.
    """
    if collection not in USER_COLLECTIONS:
        raise CatalogError(400, "INVALID_COLLECTION")
    ref = db.collection("users").document(uid).collection(collection).document(doc_id)
    snap = tx.get(ref)
    if not snap.exists:
        raise CatalogError(404, "COLLECTION_ITEM_NOT_FOUND")
    doc = snap.to_dict()
    if hasattr(tx, "update"):
        tx.update(ref, {"use_personal_photo": use_personal_photo})
    doc["use_personal_photo"] = use_personal_photo

    snapshot = doc.get("catalog_snapshot") or {}
    stock_obv = snapshot.get("obverse_image_url_at_acquire")
    stock_rev = snapshot.get("reverse_image_url_at_acquire")
    custom_obv = doc.get("custom_obverse_image_url")
    custom_rev = doc.get("custom_reverse_image_url")

    active_obv = custom_obv if (use_personal_photo and custom_obv) else stock_obv
    active_rev = custom_rev if (use_personal_photo and custom_rev) else stock_rev
    return {
        "collection": collection,
        "doc_id": doc_id,
        "use_personal_photo": use_personal_photo,
        "active_obverse_image_url": active_obv,
        "active_reverse_image_url": active_rev,
    }
