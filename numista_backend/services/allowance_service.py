"""
allowance_service.py — claim-time FIFO overflow lock (PLAN v1.2 section 4.5, G2).

A Free recipient's claim ALWAYS succeeds. After the claim commits, this module keeps the
oldest `limit` eligible items open and locks the newest ones (`locked_pending_upgrade`).

Eligible = not is_demo, not is_demo_cleared, and status != "sold" (Mark Sold, never delete).
Each doc is judged ONCE, in one pass, so a doc matching several exclusions is never
double-counted, and Sold is keyed on `status` (never `transferStatus`).

Self-contained on purpose: it does not call tier_gatekeeper.lock_overflow_coins, whose
signature changes in the unmerged NET-827 build (bed5c255). It only needs
get_user_profile / get_user_allowance, whose names are stable on both sides.
Only the `coins` subcollection is counted and locked, exactly like today's limit.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

logger = logging.getLogger("numista_backend.allowance_service")

LOCKED_CLAIM_MESSAGE = (
    "Added to your collection. Your free plan keeps your oldest 10 items open. "
    "This one is locked until you upgrade. Nothing is lost."
)

_BATCH_LIMIT = 400


def is_eligible_item(data: Dict[str, Any]) -> bool:
    """True when an item counts toward the Free item limit and can be locked."""
    if data.get("is_demo") is True or data.get("is_demo_cleared") is True:
        return False
    if data.get("status") == "sold":
        return False
    return True


def _created_sort_key(data: Dict[str, Any], doc_id: str) -> Tuple[float, str]:
    created = data.get("created_at")
    epoch = float("inf")  # unresolved / missing timestamps sort as the newest
    if isinstance(created, datetime):
        dt = created if created.tzinfo else created.replace(tzinfo=timezone.utc)
        epoch = dt.timestamp()
    elif isinstance(created, bool):
        epoch = float("inf")
    elif isinstance(created, (int, float)):
        epoch = float(created)
    elif isinstance(created, str):
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            dt = dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            epoch = dt.timestamp()
        except ValueError:
            epoch = float("inf")
    return (epoch, doc_id)


def compute_lock_flags(docs: Iterable[Tuple[str, Dict[str, Any]]], limit: Optional[int]) -> Dict[str, bool]:
    """One pass. Returns {doc_id: should_be_locked} for EVERY doc.

    Ineligible docs (demo, cleared demo, Sold) are always False. Eligible docs are sorted
    by (created_at, id); the first `limit` stay open, the rest are locked. limit None = no lock.
    """
    flags: Dict[str, bool] = {}
    eligible: List[Tuple[str, Dict[str, Any]]] = []
    for doc_id, data in docs:
        if is_eligible_item(data):
            eligible.append((doc_id, data))
        else:
            flags[doc_id] = False
    eligible.sort(key=lambda pair: _created_sort_key(pair[1], pair[0]))
    for idx, (doc_id, _data) in enumerate(eligible):
        flags[doc_id] = (limit is not None) and (idx >= limit)
    return flags


def resolve_coin_limit(
    *,
    uid: Optional[str],
    email: Optional[str],
    sign_in_provider: Optional[str] = None,
) -> Optional[int]:
    """Coin allowance via the server entitlement path. None = unlimited.

    Never gates on stripe_tier alone: uses get_user_profile(uid_for_auth=...) so the
    date-based Founding Beta fact is injected (fixes F8), then get_user_allowance.
    """
    from tier_gatekeeper import get_user_profile, get_user_allowance  # lazy: heavy import

    profile = get_user_profile(email or uid or "", uid_for_auth=uid, sign_in_provider=sign_in_provider)
    return get_user_allowance(profile).get("coins")


def apply_free_overflow_lock(
    db: Any,
    *,
    user_key: str,
    uid: Optional[str],
    email: Optional[str] = None,
    sign_in_provider: Optional[str] = None,
    limit_resolver: Optional[Callable[[], Optional[int]]] = None,
) -> Dict[str, Any]:
    """Apply the FIFO lock for one user. Idempotent. Never raises on entitlement lookup errors."""
    try:
        if limit_resolver is not None:
            limit = limit_resolver()
        else:
            limit = resolve_coin_limit(uid=uid, email=email or user_key, sign_in_provider=sign_in_provider)
    except Exception as exc:  # AuthFactsUnavailable or any lookup failure: never lock on error
        logger.warning("overflow lock skipped: entitlement lookup failed (%s)", type(exc).__name__)
        return {"skipped": "entitlement_unavailable", "limit": None, "locked_ids": [], "unlocked_ids": []}

    coins_col = db.collection("users").document(user_key).collection("coins")
    snaps = list(coins_col.stream())
    docs = [(s.id, s.to_dict() or {}) for s in snaps]
    flags = compute_lock_flags(docs, limit)

    updates: List[Tuple[str, bool]] = []
    for doc_id, data in docs:
        want = flags.get(doc_id, False)
        have = data.get("locked_pending_upgrade") is True
        if want != have:
            updates.append((doc_id, want))

    for start in range(0, len(updates), _BATCH_LIMIT):
        chunk = updates[start:start + _BATCH_LIMIT]
        if hasattr(db, "batch"):
            batch = db.batch()
            for doc_id, want in chunk:
                batch.update(coins_col.document(doc_id), {"locked_pending_upgrade": want})
            batch.commit()
        else:
            for doc_id, want in chunk:
                coins_col.document(doc_id).update({"locked_pending_upgrade": want})

    eligible_count = sum(1 for _id, d in docs if is_eligible_item(d))
    return {
        "limit": limit,
        "eligible_count": eligible_count,
        "locked_ids": sorted(i for i, f in flags.items() if f),
        "unlocked_ids": sorted(i for i, w in updates if not w),
    }
