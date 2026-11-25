import os
import time
import functools
import logging
from typing import Any, Dict, List, NamedTuple, Optional, Tuple
import stripe
import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth
from datetime import datetime, timezone
from fastapi import HTTPException, status
from google.cloud.firestore_v1.base_query import FieldFilter
from stripe_config import load_stripe_keys

logger = logging.getLogger(__name__)

# ==============================================================================
# 🛠️ FIREBASE ADMIN SDK INITIALIZATION
# ==============================================================================

PROJECT_ID = "studio-9101802118-8c9a8"

if not firebase_admin._apps:
    sa_path = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")
    if not os.path.exists(sa_path):
        sa_path = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json.json")
    if os.path.exists(sa_path):
        cred = credentials.Certificate(sa_path)
        firebase_admin.initialize_app(cred, {
            'projectId': PROJECT_ID
        })
    else:
        firebase_admin.initialize_app(options={
            'projectId': PROJECT_ID
        })

db = firestore.client()

try:
    stripe_keys = load_stripe_keys()
    stripe.api_key = stripe_keys.get("secret_key")
except Exception as e:
    print(f"[Tier Gatekeeper] Warning: Could not initialize Stripe keys: {e}")

# ==============================================================================
# 📊 USER TIERS CONFIGURATION (6-Tier Spectrum)
# ==============================================================================

TIER_COIN_LIMITS = {
    "free": 10,                 # Eric: Free 10 coins (1 Nov and 10 Nov 2026)
    "pro": 100,
    "numismatist": 249,         # NET-827 §4.5 ladder: Silver 249
    "dealer": 500,
    "estate": None,             # NET-827 §4.5 ladder: Gold unlimited (Eric, 10 Nov 2026)
    "family_estate": None,      # v1.1 Q6: Lifetime Family Estate unlimited, treated as Gold (NET-646)
    "founding_beta": None,       # unlimited (JSON-safe), NET-827 §4.5 convention (v1.10 L475 "estate": None); Eric 11 Nov 2026
    "sovereign": None,
    "power_user": None,
}

TIER_DAILY_ALLOWANCES = {
    "free": {"deepdive": 3, "invoice_scan": 1},
    "pro": {"deepdive": 25, "invoice_scan": 15},
    "numismatist": {"deepdive": 50, "invoice_scan": 30},
    "dealer": {"deepdive": 100, "invoice_scan": 50},
    "estate": {"deepdive": 500, "invoice_scan": 250},
    "family_estate": {"deepdive": 1500, "invoice_scan": 750},
    "founding_beta": {"deepdive": 1500, "invoice_scan": 750},   # Eric, 11 Nov 2026 7:08 PM ET
    "sovereign": {"deepdive": 5000, "invoice_scan": 2500},
    "power_user": {"deepdive": None, "invoice_scan": None}
}


def within_limit(tier: str, count: int) -> bool:
    limit = TIER_COIN_LIMITS.get(tier, TIER_COIN_LIMITS["free"])
    return limit is None or count <= limit


# ==============================================================================
# 🎟️ FOUNDING BETA BY SIGNUP DATE (server-side, from Firebase Auth)
# ==============================================================================

# Accounts created before 15 Dec 2026 00:00:00 America/New_York (EST, UTC-5)
# = 2026-12-15T05:00:00Z. 14 Dec 2026 23:59:59.999 ET is the last counted instant.
BETA_SIGNUP_CUTOFF_MS = 1797310800000

# Keys injected by the server only. Any copy read from a Firestore doc is discarded.
_AUTH_KEYS = ("_auth_created_ms", "_auth_is_anonymous")


class AuthFactsUnavailable(Exception):
    """Firebase Auth lookup failed or gave no creation time.
    Callers must answer 503: never grant a tier and never lock coins on this error."""


@functools.lru_cache(maxsize=50000)
def _auth_facts_by_uid(uid: str) -> tuple:
    # Successful results are cached for the life of the instance (creation time never changes).
    # Exceptions are NOT cached by lru_cache, so a failed lookup is retried on the next call.
    rec = firebase_auth.get_user(uid)
    created = rec.user_metadata.creation_timestamp  # int ms, or None
    if created is None:
        raise AuthFactsUnavailable("no creation time")
    is_anonymous = len(rec.provider_data or []) == 0
    return int(created), is_anonymous


def auth_beta_facts(uid: str, sign_in_provider: Optional[str] = None) -> dict:
    """Server-derived facts for get_user_tier. Raises AuthFactsUnavailable on any failure."""
    if not uid or "@" in uid:
        raise AuthFactsUnavailable("a Firebase uid is required")
    try:
        created, is_anonymous = _auth_facts_by_uid(uid)
    except AuthFactsUnavailable:
        raise
    except Exception as e:
        raise AuthFactsUnavailable(type(e).__name__) from e
    if sign_in_provider == "anonymous":
        is_anonymous = True
    return {"_auth_created_ms": created, "_auth_is_anonymous": is_anonymous}


def is_founding_beta(user_profile: dict) -> bool:
    """Founding Beta (AMEND-A / SA rule): the server-set beta_tester flag, or a non-anonymous
    Firebase Auth account created before BETA_SIGNUP_CUTOFF_MS, unless the server-only
    exclude_from_founding_beta flag is True (1 Dec test-purchase path). Auth facts exist only
    when the server injected them (get_user_profile(uid_for_auth=...) or load_entitlement_profile);
    stored copies are popped. beta_tester, creation_timestamp, and exclude_from_founding_beta
    are server-only keys in firestore.rules _serverOnlyKeys(), so clients cannot WRITE or forge them.
    NET-827 v2.0.7: single source for tier resolution, Estate access and the no-lock guard."""
    if user_profile.get("exclude_from_founding_beta") is True:
        return False
    created_ms = user_profile.get("_auth_created_ms")
    date_beta = (isinstance(created_ms, int) and not isinstance(created_ms, bool)
                 and user_profile.get("_auth_is_anonymous") is False
                 and created_ms < BETA_SIGNUP_CUTOFF_MS)
    return bool(user_profile.get("beta_tester") or date_beta)

# ==============================================================================
# 🛒 NET-827 CORE: what can be bought (single source, M9; Eric E-1 t2747u)
# ==============================================================================

PURCHASABLE_TIERS = ("pro", "numismatist", "dealer", "estate", "family_estate")
# Copper, Silver, Platinum, Gold (v1.11 L265-270) + Lifetime Family Estate (Eric E-1, t2747u)
PURCHASE_MODE = {"pro": "subscription", "numismatist": "subscription", "dealer": "subscription",
                 "estate": "subscription", "family_estate": "payment"}
LIFETIME_PRICE_CENTS = {"family_estate": 50000}   # $500.00 USD one-time (Eric E-1)
assert set(PURCHASE_MODE) == set(PURCHASABLE_TIERS)
TIER_DISPLAY_NAMES = {
    "pro": "Copper",
    "numismatist": "Silver",
    "dealer": "Platinum",
    "estate": "Gold",
    "family_estate": "Lifetime Family Estate",
}
PRICE_CENTS = {
    "pro": {"month": 399, "year": 3999},
    "numismatist": {"month": 799, "year": 7999},
    "dealer": {"month": 999, "year": 9900},
    "estate": {"month": 1599, "year": 15000},
}
# CHRISTMAS2026 holiday sale (15 Dec 2026 00:00 ET through 15 Jan 2027 23:59:59.999 ET):
# 50% off first year (yearly) or first 12 months (monthly), rounded down to .99; Lifetime excluded.
CHRISTMAS2026_START_UTC = 1797310800  # 2026-12-15T05:00:00Z
CHRISTMAS2026_END_UTC = 1800075600    # 2027-01-16T05:00:00Z (exclusive)
CHRISTMAS2026_DISCOUNT_CENTS = {
    "pro": {"month": 200, "year": 2000},
    "numismatist": {"month": 400, "year": 4000},
    "dealer": {"month": 500, "year": 4950},
    "estate": {"month": 800, "year": 7500},
}
CHRISTMAS2026_COUPON_IDS = {
    "pro": {"month": "CHRISTMAS2026_PRO_MONTH", "year": "CHRISTMAS2026_PRO_YEAR"},
    "numismatist": {"month": "CHRISTMAS2026_NUMISMATIST_MONTH", "year": "CHRISTMAS2026_NUMISMATIST_YEAR"},
    "dealer": {"month": "CHRISTMAS2026_DEALER_MONTH", "year": "CHRISTMAS2026_DEALER_YEAR"},
    "estate": {"month": "CHRISTMAS2026_GOLD_MONTH", "year": "CHRISTMAS2026_GOLD_YEAR"},
}
_sub_tiers = {t for t, m in PURCHASE_MODE.items() if m == "subscription"}
assert set(PRICE_CENTS) == set(CHRISTMAS2026_DISCOUNT_CENTS) == set(CHRISTMAS2026_COUPON_IDS) == _sub_tiers
assert (
    PRICE_CENTS["pro"]["month"] - CHRISTMAS2026_DISCOUNT_CENTS["pro"]["month"],
    PRICE_CENTS["pro"]["year"] - CHRISTMAS2026_DISCOUNT_CENTS["pro"]["year"],
    PRICE_CENTS["numismatist"]["month"] - CHRISTMAS2026_DISCOUNT_CENTS["numismatist"]["month"],
    PRICE_CENTS["numismatist"]["year"] - CHRISTMAS2026_DISCOUNT_CENTS["numismatist"]["year"],
    PRICE_CENTS["dealer"]["month"] - CHRISTMAS2026_DISCOUNT_CENTS["dealer"]["month"],
    PRICE_CENTS["dealer"]["year"] - CHRISTMAS2026_DISCOUNT_CENTS["dealer"]["year"],
    PRICE_CENTS["estate"]["month"] - CHRISTMAS2026_DISCOUNT_CENTS["estate"]["month"],
    PRICE_CENTS["estate"]["year"] - CHRISTMAS2026_DISCOUNT_CENTS["estate"]["year"],
) == (199, 1999, 399, 3999, 499, 4950, 799, 7500)


# ==============================================================================
# 🔄 LEGACY MIGRATION & USER PROFILE LOGIC
# ==============================================================================

def migrate_legacy_collection_chunked(legacy_email: str, new_uid: str):
    """
    Migrates legacy subcollections from users/{legacy_email} to users/{new_uid}
    using safe 400-item batch chunks to prevent exceeding Firestore's 500-op limit.
    Sets 'migration_status: completed' on users/{new_uid} to run exactly once.
    """
    try:
        user_uid_ref = db.collection("users").document(new_uid)
        uid_doc = user_uid_ref.get()
        if uid_doc.exists and (uid_doc.to_dict() or {}).get("migration_status") == "completed":
            return

        subcollections = ["coins", "currency", "wishlist", "staging_area"]
        total_migrated = 0

        for subcoll in subcollections:
            docs = db.collection("users").document(legacy_email).collection(subcoll).stream()
            batch = db.batch()
            op_count = 0

            for doc in docs:
                target_ref = user_uid_ref.collection(subcoll).document(doc.id)
                batch.set(target_ref, doc.to_dict(), merge=True)
                op_count += 1
                total_migrated += 1

                if op_count >= 400:
                    batch.commit()
                    batch = db.batch()
                    op_count = 0

            if op_count > 0:
                batch.commit()

        user_uid_ref.set({
            "legacy_email": legacy_email,
            "migration_status": "completed",
            "migrated_at": datetime.now(timezone.utc).isoformat(),
            "migrated_doc_count": total_migrated
        }, merge=True)
        print(f"[Tier Gatekeeper] Successfully migrated {total_migrated} docs from {legacy_email} -> {new_uid}")
    except Exception as e:
        print(f"[Tier Gatekeeper] Error during legacy migration for {legacy_email}: {e}")


def get_user_profile(user_identifier: str, uid_for_auth: Optional[str] = None,
                     sign_in_provider: Optional[str] = None) -> dict:
    """
    Reads the user document from Firestore.
    Checks users/{uid} first. If missing or email-like, checks users/{email} fallback.
    When uid_for_auth is given, adds server-derived Firebase Auth facts (Founding Beta by
    signup date); that lookup raises AuthFactsUnavailable on failure (callers answer 503).
    """
    profile = {}
    try:
        doc_ref = db.collection("users").document(user_identifier)
        doc = doc_ref.get()
        if doc.exists:
            profile = doc.to_dict() or {}
    except Exception as e:
        print(f"[Tier Gatekeeper] Error reading profile for {user_identifier}: {e}")
        profile = {}
    for k in _AUTH_KEYS:          # never trust a stored copy of a server-only key
        profile.pop(k, None)
    if uid_for_auth:
        profile.update(auth_beta_facts(uid_for_auth, sign_in_provider))
    return profile


_ALLOWANCE_ITEMS = ("coins", "deepdive", "invoice_scan")


def _coin_rank(tier: str) -> float:
    """Coin allowance used for ranking; None (unlimited, NET-827 §4.5) and float('inf') rank highest."""
    limit = TIER_COIN_LIMITS.get(tier, TIER_COIN_LIMITS["free"])
    return float("inf") if limit is None else float(limit)


def _item_limit(tier: str, item: str):
    """One allowance item for one tier; None = unlimited. Unknown tiers use 'free' (as today)."""
    if item == "coins":
        return TIER_COIN_LIMITS.get(tier, TIER_COIN_LIMITS["free"])
    daily = TIER_DAILY_ALLOWANCES.get(tier, TIER_DAILY_ALLOWANCES["free"])
    return daily.get(item, 0)


def _bigger(a, b):
    """None (unlimited) beats any number."""
    if a is None or b is None:
        return None
    return max(a, b)


def _tier_candidates(user_profile: dict) -> list:
    """Paid (stripe_tier -> tier), comp (lifetime / AI QC -> family_estate) and Founding Beta
    (beta_tester flag, or a non-anonymous Firebase Auth account created before
    BETA_SIGNUP_CUTOFF_MS -> founding_beta), in tie-break order: paid first.
    The Auth facts are injected only by get_user_profile(uid_for_auth=...); the
    client-writable 'creation_timestamp' Firestore field is not read (closes NET-827
    open risk 14 for tier resolution). Beta never expires on the server."""
    paid = user_profile.get("stripe_tier") or user_profile.get("tier")
    paid = str(paid).lower().strip() if paid else None
    comp = None
    if user_profile.get("is_lifetime_family_estate") or user_profile.get("is_ai_qc_account"):
        comp = "family_estate"
    beta = "founding_beta" if is_founding_beta(user_profile) else None
    return [c for c in (paid, comp, beta) if c]


def get_user_tier(user_profile: dict) -> str:
    """Tier NAME for reports: the candidate with the largest coin allowance; ties go to the
    paid tier (Eric, 11 Nov 2026). Allowance values come from get_user_allowance."""
    best = None
    for candidate in _tier_candidates(user_profile):
        if best is None or _coin_rank(candidate) > _coin_rank(best):
            best = candidate
    return best or "free"


def get_user_allowance(user_profile: dict) -> dict:
    """Item-by-item bigger allowance over every candidate (Eric, 11 Nov 2026 7:08 PM ET):
    coins, deep dives and invoice scans are each compared on their own; None (unlimited)
    beats any number. No candidate -> 'free'."""
    candidates = _tier_candidates(user_profile) or ["free"]
    out = {}
    for item in _ALLOWANCE_ITEMS:
        value = _item_limit(candidates[0], item)
        for candidate in candidates[1:]:
            value = _bigger(value, _item_limit(candidate, item))
        out[item] = value
    return out


def get_coin_count(user_identifier: str) -> int:
    """Calculates total coins in users/{user_identifier}/coins via count()."""
    try:
        coins_ref = db.collection("users").document(user_identifier).collection("coins")
        total = coins_ref.count().get()[0][0].value
        # R3 (Mark Sold, never delete): Sold items keep their doc but are not part of the owned count.
        sold = coins_ref.where("status", "==", "sold").count().get()[0][0].value
        return max(0, total - sold)
    except Exception as e:
        print(f"[Tier Gatekeeper] Error counting coins for {user_identifier}: {e}")
        return 0

# ==============================================================================
# 🛡️ FEATURE GATEKEEPING & ATOMIC USAGE
# ==============================================================================

def check_and_enforce_coin_limit(user_identifier: str, success_url: str = "https://numista.ai/#/settings?stripe=success", cancel_url: str = "https://numista.ai/#/settings?stripe=cancel", email: Optional[str] = None) -> bool:
    uid = user_identifier if _valid_uid(user_identifier) else None
    em = email or (user_identifier if "@" in (user_identifier or "") else None)
    profile, ent = load_entitlement_profile(db, uid, em, with_auth_facts=bool(uid))
    tier = get_user_tier(profile)

    if tier == "power_user":
        return True

    limit = effective_limit(profile, ent, time.time(), item="coins")
    if limit is None:
        return True

    coin_count = count_unique_coins(db, uid, em) if (uid and em) else get_coin_count(user_identifier)

    if not entitlement_ok(limit, coin_count):
        tier_order = ["free", "pro", "numismatist", "dealer", "estate", "family_estate", "sovereign"]
        try:
            current_idx = tier_order.index(tier)
            next_tier = tier_order[current_idx + 1] if current_idx + 1 < len(tier_order) else "sovereign"
        except ValueError:
            next_tier = "pro"

        detail = {
            "error": "tier_limit_exceeded",
            "message": f"Tier limit exceeded: You have {coin_count} items, but your {tier.capitalize()} tier limit is {limit} items.",
            "stats": {"coin_count": coin_count, "limit": limit, "tier": tier, "next_tier": next_tier},
            "upgrade_url": None,
        }
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    return True


def check_and_increment_daily_usage(user_identifier: str, feature_type: str, email: Optional[str] = None) -> bool:
    uid = user_identifier if _valid_uid(user_identifier) else None
    em = email or (user_identifier if "@" in (user_identifier or "") else None)
    profile, ent = load_entitlement_profile(db, uid, em, with_auth_facts=bool(uid))
    tier = get_user_tier(profile)

    if tier == "power_user":
        return True

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    family_group_id = profile.get("family_group_id")
    use_family = False
    if family_group_id and uid:
        fg_ref = db.collection("family_groups").document(family_group_id)
        fg_snap = fg_ref.get()
        if fg_snap.exists:
            fg_data = fg_snap.to_dict() or {}
            if uid == fg_data.get("owner_uid") or uid in (fg_data.get("members") or []):
                use_family = True

    if use_family:
        target_ref = db.collection("family_groups").document(family_group_id)
        date_key = "last_reset_utc"
        limit = TIER_DAILY_ALLOWANCES.get("family_estate", {}).get(feature_type, 1500)
    else:
        target_ref = db.collection("users").document(user_identifier)
        date_key = "last_usage_date"
        limit = effective_limit(profile, ent, time.time(), item=feature_type)

    count_key = f"{feature_type}_count"

    def _txn(t):
        snap = target_ref.get(transaction=t)
        data = (snap.to_dict() or {}) if snap.exists else {}
        if data.get(date_key, "") != today_str:
            cur = 0
            patch_d = {date_key: today_str, "deepdive_count": 0, "invoice_scan_count": 0}
        else:
            cur = int(data.get(count_key, 0) or 0)
            patch_d = {date_key: today_str}
        if limit is not None and cur >= limit:
            if data.get(date_key, "") != today_str:
                t.set(target_ref, patch_d, merge=True)
            return False
        patch_d[count_key] = cur + 1
        t.set(target_ref, patch_d, merge=True)
        return True

    return _run_txn(db, _txn)


_COIN_CHUNK = 200          # copies per transaction (2 writes each, under the 500-write limit)
_FLAG_CHUNK = 400


def _coin_epoch(data) -> float:
    """Sort time: to_epoch(created_at), else to_epoch(added_at), else 0 (oldest, kept visible)."""
    for field in ("created_at", "added_at"):
        e = to_epoch((data or {}).get(field))
        if e:                                   # None (missing) or 0.0 (unparseable) -> next
            return e
    return 0.0


def lock_overflow_coins(db, uid, email, limit, reason, now) -> int:
    """_validate_relock_uid(uid, 'lock_overflow_coins') first (P1 L328). limit None -> 0.
    v1.11 L616-621 steps 1-5: group copies by id; sort time = to_epoch(created_at), else
    to_epoch(added_at), else 0; ties by id; a coin's time = its earliest copy; keep the first
    `limit`, move the rest: per <=200-copy chunk, one _run_txn that re-reads each source;
    if gone, skip; else set locked_coins/{owner_key}/coins/{coin_id} =
    {coin_id, source_path, data, locked_at: now, lock_reason: reason, sort_epoch}
    and delete the source. Returns copies moved. Errors raise."""
    _validate_relock_uid(uid, "lock_overflow_coins")
    if limit is None:
        return 0
    copies: Dict[str, list] = {}
    for k in _owner_keys(uid, email):
        for snap in db.collection("users").document(k).collection("coins").stream():
            copies.setdefault(snap.id, []).append((k, snap.reference, snap.to_dict() or {}))
    if len(copies) <= limit:
        return 0
    coin_time = {cid: min(_coin_epoch(d) for _k, _r, d in cs) for cid, cs in copies.items()}
    ordered = sorted(copies, key=lambda cid: (coin_time[cid], cid))
    to_move = [(cid, k, ref) for cid in ordered[limit:] for k, ref, _d in copies[cid]]
    moved = 0
    for start in range(0, len(to_move), _COIN_CHUNK):
        chunk = to_move[start:start + _COIN_CHUNK]

        def _txn(t, chunk=chunk):
            fresh = [(cid, k, ref, ref.get(transaction=t)) for cid, k, ref in chunk]   # reads first
            n = 0
            for cid, k, ref, snap in fresh:
                if not snap.exists:             # already moved or deleted by the user
                    continue
                locked_ref = db.collection("locked_coins").document(k).collection("coins").document(cid)
                t.set(locked_ref, {"coin_id": cid, "source_path": ref.path, "data": snap.to_dict() or {},
                                   "locked_at": now, "lock_reason": reason, "sort_epoch": coin_time[cid]})
                t.delete(ref)
                n += 1
            return n

        moved += _run_txn(db, _txn)
    return moved


def unlock_user_coins(db, uid, email, limit) -> int:
    """v1.11 L622-627 steps 1-5: room = unlimited if limit is None else limit - visible;
    restore whole coins oldest-first by sort_epoch; <=200-copy chunks; if the target path
    exists -> set restore_conflict: True on the locked copy and count it; else set source =
    data and delete the locked copy; then clear legacy locked_pending_upgrade == True flags
    on visible coins in <=400 chunks. Returns restore_conflicts. Errors raise."""
    keys = _owner_keys(uid, email)
    visible_ids = set()
    for k in keys:
        for snap in db.collection("users").document(k).collection("coins").stream():
            visible_ids.add(snap.id)
    locked: Dict[str, list] = {}
    for k in keys:
        for snap in db.collection("locked_coins").document(k).collection("coins").stream():
            locked.setdefault(snap.id, []).append((k, snap.reference, snap.to_dict() or {}))
    ordered = sorted(locked, key=lambda cid: (min(float(d.get("sort_epoch") or 0.0) for _k, _r, d in locked[cid]), cid))
    if limit is not None:
        ordered = ordered[:max(0, limit - len(visible_ids))]
    to_restore = [(cid, ref, d) for cid in ordered for _k, ref, d in locked[cid]]
    conflicts = 0
    for start in range(0, len(to_restore), _COIN_CHUNK):
        chunk = to_restore[start:start + _COIN_CHUNK]

        def _txn(t, chunk=chunk):
            reads = []
            for cid, lref, d in chunk:          # reads first
                target = db.document(d.get("source_path"))
                reads.append((lref, lref.get(transaction=t), target, target.get(transaction=t)))
            n = 0
            for lref, lsnap, target, tsnap in reads:
                if not lsnap.exists:
                    continue
                if tsnap.exists:                # never overwrite a coin that is back in place
                    t.set(lref, {"restore_conflict": True}, merge=True)
                    logger.warning("restore_conflict path=%s", target.path)
                    n += 1
                    continue
                t.set(target, (lsnap.to_dict() or {}).get("data") or {})
                t.delete(lref)
            return n

        conflicts += _run_txn(db, _txn)
    flagged = []
    for k in keys:
        q = db.collection("users").document(k).collection("coins").where(
            filter=FieldFilter("locked_pending_upgrade", "==", True))
        flagged.extend(snap.reference for snap in q.stream())
    for start in range(0, len(flagged), _FLAG_CHUNK):
        refs = flagged[start:start + _FLAG_CHUNK]

        def _flags(t, refs=refs):
            for ref in refs:
                t.update(ref, {"locked_pending_upgrade": False})
            return len(refs)

        _run_txn(db, _flags)
    return conflicts


# ==============================================================================
# 🔐 NET-827 CORE: entitlement, coin count, lock / unlock, revoke (plan v1.1.1 §6)
# ==============================================================================

def _run_txn(db, fn):
    """Single transaction seam: firestore.transactional(fn)(db.transaction())
    (google-cloud-firestore 2.26.0 transaction.py:335). Tests patch this name."""
    return firestore.transactional(fn)(db.transaction())


def _owner_keys(uid, email):
    """Coin-folder keys, de-duplicated, None skipped. Email lower-cased, as the token
    routes key it (main.py:3088-3102 per CoS readiness D2 note)."""
    keys = []
    for k in (uid, (email or "").strip().lower() or None):
        if k and k not in keys:
            keys.append(k)
    return keys


def count_unique_coins(db, uid, email, include_locked=False) -> int:
    """len(union of doc ids in users/{k}/coins for k in _owner_keys); with include_locked,
    plus ids in locked_coins/{k}/coins not already visible. Any read error RAISES (never 0;
    today's fail-open in get_coin_count is not reused)."""
    keys = _owner_keys(uid, email)
    ids = set()
    for k in keys:
        for snap in db.collection("users").document(k).collection("coins").stream():
            ids.add(snap.id)
    if include_locked:
        for k in keys:
            for snap in db.collection("locked_coins").document(k).collection("coins").stream():
                ids.add(snap.id)
    return len(ids)


def to_epoch(val):
    """None if missing; 0.0 if present but unparseable (fails closed: treated as expired / oldest)."""
    if val is None:
        return None
    if hasattr(val, "timestamp"):            # Firestore Timestamp / DatetimeWithNanoseconds / datetime
        try:
            return float(val.timestamp())
        except Exception:
            return 0.0
    if isinstance(val, (int, float)):
        v = float(val)
        return v / 1000.0 if v > 1e11 else v  # millisecond epochs (as in creation_timestamp) → seconds
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val.replace("Z", "+00:00")).timestamp()
        except ValueError:
            return 0.0
    return 0.0


def effective_limit(profile, ent, now_ts, item="coins"):
    """None = unlimited. item is 'coins', 'deepdive' or 'invoice_scan'. The value is
    get_user_allowance(profile)[item] (server plan v1.2 A4): item by item, the bigger allowance
    wins, None beats any number. Never TIER_DAILY_ALLOWANCES[get_user_tier(...)] and never
    limits.get(get_user_tier(...))."""
    if item == "coins":
        until = to_epoch(ent.get("beta_special_until"))   # stored as Firestore Timestamp (A4)
        if until is not None and until > now_ts:  # unexpired Beta Special: unlimited coins on any tier
            return None
    return get_user_allowance(profile)[item]


def entitlement_ok(limit, count):
    return limit is None or count <= limit


def load_entitlement_profile(
    db,
    uid: Optional[str],
    email: Optional[str],
    sign_in_provider: Optional[str] = None,
    with_auth_facts: bool = True,
) -> Tuple[ dict, dict ]:
    """Merged view of users/{uid} and users/{email} plus server-derived Firebase Auth facts;
    raises on any read error. AuthFactsUnavailable (tier_gatekeeper, server plan v1.2 A2)
    propagates: callers answer 503 (routes) or retry/500 (webhook), never grant a tier
    and never lock.

    Closes CoS A2: entitlements.document(uid) is only read when uid is a non-empty non-email id.
    """
    has_valid_uid = bool(uid and isinstance(uid, str) and "@" not in uid)
    uid_doc = (db.collection("users").document(uid).get().to_dict() or {}) if uid else {}
    email_doc = (
        (db.collection("users").document(email).get().to_dict() or {})
        if (email and email != uid)
        else {}
    )
    ent = (
        (db.collection("entitlements").document(uid).get().to_dict() or {})
        if has_valid_uid
        else {}
    )
    profile = dict(email_doc)
    profile.update(uid_doc)                   # webhook writes stripe_tier to users/{uid}
    for k in ("is_lifetime_family_estate", "is_ai_qc_account", "beta_tester", "exclude_from_founding_beta"):
        profile[k] = bool(uid_doc.get(k) or email_doc.get(k))   # server-only flags may live on either doc
    for k in _AUTH_KEYS:                      # never trust a stored copy of a server-only key (server plan A3)
        profile.pop(k, None)
    if with_auth_facts and has_valid_uid:     # never pass an email key (server plan A5)
        profile.update(auth_beta_facts(uid, sign_in_provider))   # raises AuthFactsUnavailable
    return profile, ent


def enforce_entitlement(
    db,
    uid: str,
    email: Optional[str],
    now: float,
    sign_in_provider: Optional[str] = None,
) -> Dict[str, Any]:
    """Reconcile visible and locked coins for one account.
    P1 contract: uid MUST be a resolved Firebase uid (non-empty string without '@').
    Never reconciles or locks on an email-only key or without Firebase Auth facts.
    Raises ValueError if uid is missing/email-like; raises AuthFactsUnavailable if
    Firebase Auth lookup fails or lacks creation_timestamp.
    """
    if not uid or not isinstance(uid, str) or "@" in uid:
        raise ValueError("enforce_entitlement requires a resolved Firebase uid (never an email-only key)")
    profile, ent = load_entitlement_profile(
        db, uid, email, sign_in_provider=sign_in_provider, with_auth_facts=True
    )
    limit = effective_limit(profile, ent, now, item="coins")
    if limit is not None and (is_founding_beta(profile) or lifetime_flag_set(profile)):
        limit = None    # NET-827 v2.0.6 (CoS scope A / N5): never lock a Founding Beta or Lifetime account
    visible = count_unique_coins(db, uid, email, include_locked=False)
    locked_moved = 0
    if limit is not None and visible > limit:
        locked_moved = lock_overflow_coins(db, uid, email, limit, reason="entitlement_reconcile", now=now)
        visible = count_unique_coins(db, uid, email, include_locked=False)
    restore_conflicts = 0
    if limit is None or visible < limit:
        restore_conflicts = unlock_user_coins(db, uid, email, limit)
        visible = count_unique_coins(db, uid, email, include_locked=False)
    total_with_locked = count_unique_coins(db, uid, email, include_locked=True)
    locked_count = max(0, total_with_locked - visible)
    return {
        "limit": limit,
        "visible": visible,
        "locked": locked_count,
        "locked_moved": locked_moved,
        "restore_conflicts": restore_conflicts,
    }


def _validate_relock_uid(uid: str, caller: str) -> None:
    """Hard guard required on both enforce_entitlement and lock_overflow_coins (P1 / CoS D1):
    lock_overflow_coins(db, uid, email, limit, reason, now) calls _validate_relock_uid(uid, 'lock_overflow_coins')
    before step 1 (if limit is None: return 0), so no lock call is ever reachable with uid=None or an email key.
    """
    if not uid or not isinstance(uid, str) or "@" in uid:
        raise ValueError(f"{caller} requires a resolved Firebase uid (never an email-only key)")


class RevokeResult(NamedTuple):
    revoked_owner_keys: List[str]   # users/{D} doc ids actually nulled, unique, write order
    guard_skipped: bool             # True iff >=1 doc skipped by the other-subscription guard


class RevokeEmailUnresolved(Exception):
    """uid given but email unknowable (no entitlements.email, Auth get_user failed). Raised
    AFTER the uid doc and the sweep are committed; caller sets retry/500 (v1.11 ADV5)."""


_REVOKE_PAYLOAD = {"stripe_tier": None, "subscription_status": "canceled", "grace_period_until": None}

_REVOKE_CHUNK = 400


def _valid_uid(uid) -> bool:
    return bool(uid and isinstance(uid, str) and "@" not in uid)


def revoke_paid_tier(db, uid, email, customer_id=None, revoked_subscription_id=None) -> RevokeResult:
    """Removes the paid subscription tier only (plan v1.1.1 §6.2 rules 1-5). Never locks coins
    (P1 does, via _relock_hook). Never writes beta_tester, is_lifetime_family_estate,
    is_ai_qc_account, tier, power_user, Auth facts or anything in entitlements.
    Never creates a users doc."""
    targets: List[str] = []

    def _add(doc_id):
        if doc_id and doc_id not in targets:
            targets.append(doc_id)

    email_unresolved = False
    rule1a_targets: set = set()
    account_other_sub = False
    if _valid_uid(uid):
        # rule 1a: users/{uid}, users/{email_lc} and, if different, users/{raw}
        _add(uid)
        rule1a_targets.add(uid)
        uid_ent_snap = db.collection("entitlements").document(uid).get()
        uid_ent_data = (uid_ent_snap.to_dict() or {}) if uid_ent_snap.exists else {}
        uid_other_sub = uid_ent_data.get("stripe_subscription_id")
        if uid_other_sub and uid_other_sub != revoked_subscription_id:
            account_other_sub = True
        raw = (email or "").strip() or None
        if raw is None:
            raw = (uid_ent_data.get("email") or "").strip() or None
        if raw is None:
            try:
                rec = firebase_auth.get_user(uid)
                raw = (rec.email or "").strip() or None
            except Exception as e:      # an Auth error does not abort the revoke
                logger.warning("revoke_email_auth_error uid=%s err=%s", uid, type(e).__name__)
                raw = None
        if raw is None:
            email_unresolved = True
        else:
            _add(raw.lower())
            rule1a_targets.add(raw.lower())
            if raw != raw.lower():
                _add(raw)
                rule1a_targets.add(raw)
    elif email:
        # rule 1b: no uid -> users/{email_lc}
        _add(email.strip().lower())

    # rule 1c: sweep by Stripe customer id (no limit)
    if isinstance(customer_id, str) and customer_id.startswith("cus_"):
        matches = [snap.id for snap in db.collection("users").where(
            filter=FieldFilter("stripe_customer_id", "==", customer_id)).stream()]
        if len(matches) > 2:
            logger.warning("revoke_sweep_many customer=%s matches=%d", customer_id, len(matches))
        for doc_id in matches:
            _add(doc_id)

    revoked: List[str] = []
    guard_skipped = False
    for start in range(0, len(targets), _REVOKE_CHUNK):
        chunk = targets[start:start + _REVOKE_CHUNK]

        def _txn(t, chunk=chunk):
            reads = []
            for doc_id in chunk:                      # all reads before any write
                uref = db.collection("users").document(doc_id)
                eref = db.collection("entitlements").document(doc_id)
                reads.append((doc_id, uref, uref.get(transaction=t), eref.get(transaction=t)))
            done, skipped = [], False
            for doc_id, uref, usnap, esnap in reads:
                if not usnap.exists:                  # never created
                    continue
                if account_other_sub and doc_id in rule1a_targets:
                    logger.info("revoke_skip_other_sub doc=%s", doc_id)
                    skipped = True
                    continue
                if esnap.exists:
                    other = (esnap.to_dict() or {}).get("stripe_subscription_id")
                    if other and other != revoked_subscription_id:
                        logger.info("revoke_skip_other_sub doc=%s", doc_id)
                        skipped = True
                        continue
                t.set(uref, dict(_REVOKE_PAYLOAD), merge=True)
                done.append(doc_id)
            return done, skipped

        done, skipped = _run_txn(db, _txn)
        revoked.extend(done)
        guard_skipped = guard_skipped or skipped

    if email_unresolved:
        raise RevokeEmailUnresolved(uid)
    return RevokeResult(revoked, guard_skipped)


# ------------------------------------------------------------------------------
# Lifetime Family Estate, one-time $500 (plan v1.1.1 §5.8, Eric E-1 t2747u)
# ------------------------------------------------------------------------------

class LifetimeGrantRefused(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


# v1.1.1 (BC-2): the only readers of the lifetime flag that payment_routes.py uses
def lifetime_flag_set(profile) -> bool:
    """True iff the profile's lifetime flag is True. Pure; used by the status route for the
    `lifetime_family_estate` response key (§7)."""
    return (profile or {}).get("is_lifetime_family_estate") is True


# NET-827 v2.0.6: Estate staff allowlist (Eric Q5, t2965s11300). Mirrors the Dart
# kEstateStaffAllowlist (estate_planning_screen.dart:120-123). Exact match after trim + lower-case.
ESTATE_STAFF_EMAILS = frozenset({"eric@numista.ai", "grokbot@numista.ai"})


def estate_access(profile, token_email: Optional[str] = None) -> bool:
    """NET-827 v2.0.6 (Eric t3000u / widget 5:37 PM ET 16 Nov 2026; CoS ruling): who may open
    Estate. Lifetime buyers (server-set flag), AI-QC accounts (D-2), a family_estate tier,
    Founding Beta (is_founding_beta: server-set beta_tester or Firebase Auth sign-up before the
    cutoff), or the staff allowlist matched on the VERIFIED ID-token email only. Never reads a
    stored 'estate_access' or any other client-writable field. Pure; read errors are raised by
    the loader before this runs, so callers answer 503/500 and the app fails closed."""
    p = profile or {}
    if lifetime_flag_set(p):
        return True
    if p.get("is_ai_qc_account"):
        return True
    paid = p.get("stripe_tier") or p.get("tier")
    if paid and str(paid).lower().strip() == "family_estate":
        return True
    if is_founding_beta(p):
        return True
    return (token_email or "").strip().lower() in ESTATE_STAFF_EMAILS


def has_lifetime_flag(db, uid, email) -> bool:
    """§8 409 already_lifetime check. Read-only: for key in (uid, email), skipping empty keys and
    a repeat: True on the first existing doc where lifetime_flag_set. Firestore errors
    propagate (checkout maps them to today's 502). Writes nothing."""
    seen = []
    for key in (uid, email):
        if not key or key in seen:
            continue
        seen.append(key)
        snap = db.collection("users").document(key).get()
        if snap.exists and lifetime_flag_set(snap.to_dict() or {}):
            return True
    return False


def _fresh_email(db, uid) -> Optional[str]:
    """F3 (§5.5) + N2: firebase_auth.get_user(uid).email lower-cased; UserNotFoundError
    falls back to entitlements/{uid}.email; any other Auth error RAISES (caller -> retry)."""
    try:
        rec = firebase_auth.get_user(uid)
        e = (rec.email or "").strip().lower() or None
    except firebase_auth.UserNotFoundError:
        e = None
    if e is None:
        snap = db.collection("entitlements").document(uid).get()
        e = (((snap.to_dict() or {}).get("email") if snap.exists else None) or "").strip().lower() or None
    return e


def _iso(now) -> str:
    return datetime.fromtimestamp(float(now), timezone.utc).isoformat()


def grant_lifetime_purchase(db, uid, email, payment_intent, customer_id, tier, now, amounts=None) -> str:
    """§5.8.1 step 5. The only writer (with revoke_lifetime_purchase) of the lifetime flag
    and entitlements/{uid}.lifetime. Returns "granted", "duplicate" (a second live lifetime PI)
    or "already" (this PI was granted before). Raises LifetimeGrantRefused(reason) for
    revoked_payment / customer_uid_conflict; the handler maps it to failed + review_required."""
    iso_now = _iso(now)
    amt = dict(amounts) if amounts is not None else {
        "amount_subtotal": LIFETIME_PRICE_CENTS[tier],
        "amount_tax": None,
        "amount_total": LIFETIME_PRICE_CENTS[tier],
        "currency": "usd",
    }
    pay_ref = db.collection("stripe_payments").document(payment_intent)
    ent_ref = db.collection("entitlements").document(uid)
    user_ids = [uid] + ([email] if email and email != uid else [])
    user_refs = [(d, db.collection("users").document(d)) for d in user_ids]
    cust_ref = db.collection("stripe_customers").document(customer_id) if customer_id else None

    def _txn(t):
        pay = pay_ref.get(transaction=t)                     # all reads first
        ent = ent_ref.get(transaction=t)
        users = [(d, ref, ref.get(transaction=t)) for d, ref in user_refs]
        cust = cust_ref.get(transaction=t) if cust_ref is not None else None
        pay_d = (pay.to_dict() or {}) if pay.exists else None
        if pay_d is not None and pay_d.get("revoked"):
            raise LifetimeGrantRefused("revoked_payment")
        if pay_d is not None and pay_d.get("granted"):
            return "already"
        if cust is not None and cust.exists:
            owner = (cust.to_dict() or {}).get("uid")
            if owner and owner != uid:
                raise LifetimeGrantRefused("customer_uid_conflict")
        ent_d = (ent.to_dict() or {}) if ent.exists else {}
        life = ent_d.get("lifetime") or {}
        ent_patch: Dict[str, Any] = {}
        if email:
            ent_patch["email"] = email
        live_pi = life.get("payment_intent") if not life.get("revoked") else None
        if live_pi and live_pi != payment_intent:
            extras = list(life.get("extra_payment_intents") or [])
            if payment_intent not in extras:
                extras.append(payment_intent)
            ent_patch["lifetime"] = {"extra_payment_intents": extras}
            result = "duplicate"
        else:
            preexisting = {d: bool(snap.exists and (snap.to_dict() or {}).get("is_lifetime_family_estate") is True)
                           for d, _ref, snap in users}
            ent_patch["lifetime"] = {
                "tier": "family_estate", "payment_intent": payment_intent, "customer_id": customer_id,
                "granted_at": now, **amt,
                "flag_preexisting": preexisting, "extra_payment_intents": [], "revoked": None,
            }
            result = "granted"
        for _d, ref, _snap in users:
            t.set(ref, {"is_lifetime_family_estate": True, "updated_at": iso_now}, merge=True)
        t.set(ent_ref, ent_patch, merge=True)
        if cust_ref is not None:
            t.set(cust_ref, {"uid": uid}, merge=True)
        t.set(pay_ref, {"uid": uid, "kind": "lifetime", "tier": tier, "subscription_id": None,
                        "invoice_id": None, **amt,
                        "granted": True, "created_at": iso_now}, merge=True)
        return result

    return _run_txn(db, _txn)


def revoke_lifetime_purchase(db, uid, payment_intent, reason, now) -> RevokeResult:
    """§5.8.2. Clears the lifetime flag only for the PI that bought it, only on docs
    where flag_preexisting is False, only when no other live lifetime PI remains. Writes the
    F2 marker entitlements/{uid}.last_revoke.lifetime and stripe_payments/{pi}.revoked.
    Never writes stripe_tier / subscription_status / beta_tester / tier / power_user.
    Returns RevokeResult(cleared_doc_ids, False); the webhook then calls _relock_hook."""
    fresh = _fresh_email(db, uid)                            # F3; Auth error raises -> retry
    pay_ref = db.collection("stripe_payments").document(payment_intent)
    ent_ref = db.collection("entitlements").document(uid)
    ent_pre = ent_ref.get()
    granted_email = ((ent_pre.to_dict() or {}).get("email") if ent_pre.exists else None) or None
    doc_ids = []
    for d in (uid, fresh, granted_email):
        if d and d not in doc_ids:
            doc_ids.append(d)

    def _txn(t):
        ent = ent_ref.get(transaction=t)                     # all reads first
        pay = pay_ref.get(transaction=t)
        ent_d = (ent.to_dict() or {}) if ent.exists else {}
        pay_d = (pay.to_dict() or {}) if pay.exists else {}
        life = ent_d.get("lifetime") or {}
        pis = [p for p in [life.get("payment_intent")] + list(life.get("extra_payment_intents") or []) if p]
        others = {p: db.collection("stripe_payments").document(p).get(transaction=t)
                  for p in pis if p != payment_intent}
        users = [(d, db.collection("users").document(d)) for d in doc_ids]
        users = [(d, ref, ref.get(transaction=t)) for d, ref in users]
        if pay_d.get("revoked"):
            return []                                        # idempotent
        mark = {"at": now, "reason": reason}
        t.set(pay_ref, {"revoked": mark}, merge=True)
        t.set(ent_ref, {"last_revoke": {"lifetime": {"subscription_id": None, "payment_intent": payment_intent,
                                                     "at": now, "reason": reason}}}, merge=True)
        others_live = [p for p, s in others.items()
                       if not (s.exists and (s.to_dict() or {}).get("revoked"))]
        known = payment_intent in pis
        preexisting = life.get("flag_preexisting") or {}
        cleared = []
        for d, ref, snap in users:
            if not snap.exists:
                continue                                     # never created
            if not known:
                logger.info("lifetime_flag_kept:not_this_pi doc=%s", d)
                continue
            if others_live:
                logger.info("lifetime_flag_kept:other_live_pi doc=%s", d)
                continue
            if preexisting.get(d) is not False:
                logger.info("lifetime_flag_kept:preexisting doc=%s", d)
                continue
            t.set(ref, {"is_lifetime_family_estate": False}, merge=True)
            cleared.append(d)
        if life and not others_live:
            t.set(ent_ref, {"lifetime": {"revoked": mark}}, merge=True)
        return cleared

    cleared = _run_txn(db, _txn)
    return RevokeResult(cleared, False)
