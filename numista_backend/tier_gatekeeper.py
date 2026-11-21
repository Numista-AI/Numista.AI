import os
import functools
from typing import Optional
import stripe
import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth
from datetime import datetime, timezone
from fastapi import HTTPException, status
from stripe_config import load_stripe_keys

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
    "numismatist": 250,
    "dealer": 500,
    "estate": 1000,
    "family_estate": 2500,
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
    created_ms = user_profile.get("_auth_created_ms")
    date_beta = (isinstance(created_ms, int) and not isinstance(created_ms, bool)
                 and user_profile.get("_auth_is_anonymous") is False
                 and created_ms < BETA_SIGNUP_CUTOFF_MS)
    beta = "founding_beta" if (user_profile.get("beta_tester") or date_beta) else None
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
        results = coins_ref.count().get()
        return results[0][0].value
    except Exception as e:
        print(f"[Tier Gatekeeper] Error counting coins for {user_identifier}: {e}")
        return 0

# ==============================================================================
# 💳 STRIPE CHECKOUT & PORTAL SESSIONS
# ==============================================================================

def create_upgrade_checkout_session(user_id: str, email: str, target_tier: str, success_url: str, cancel_url: str) -> str:
    sec_key = os.getenv("STRIPE_SECRET_KEY")
    if not sec_key:
        raise ValueError("STRIPE_SECRET_KEY is not set in environment.")
    stripe.api_key = sec_key

    price_map = {
        "pro": os.getenv("STRIPE_PRICE_PRO", "price_1ProMockID"),
        "numismatist": os.getenv("STRIPE_PRICE_NUMISMATIST", "price_1NumismatistMockID"),
        "dealer": os.getenv("STRIPE_PRICE_DEALER", "price_1DealerMockID"),
        "estate": os.getenv("STRIPE_PRICE_ESTATE", "price_1EstateMockID"),
        "family_estate": os.getenv("STRIPE_PRICE_FAMILY_ESTATE", "price_1FamilyEstateMockID"),
        "sovereign": os.getenv("STRIPE_PRICE_SOVEREIGN", "price_1SovereignMockID"),
    }

    price_id = price_map.get(target_tier.lower(), price_map["pro"])

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        customer_email=email,
        client_reference_id=user_id,
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        allow_promotion_codes=True,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"user_uid": user_id, "user_email": email, "target_tier": target_tier}
    )
    return session.url


def create_customer_portal_session(user_id: str, email: str, return_url: str) -> str:
    sec_key = os.getenv("STRIPE_SECRET_KEY")
    if not sec_key:
        raise ValueError("STRIPE_SECRET_KEY is not set in environment.")
    stripe.api_key = sec_key

    user_doc_ref = db.collection("users").document(user_id)
    user_doc = user_doc_ref.get()
    customer_id = (user_doc.to_dict() or {}).get("stripe_customer_id") if user_doc.exists else None

    if not customer_id and stripe.api_key:
        existing = stripe.Customer.list(email=email, limit=1)
        if existing.data:
            customer_id = existing.data[0].id
        else:
            cust = stripe.Customer.create(email=email, metadata={"uid": user_id})
            customer_id = cust.id
        user_doc_ref.set({"stripe_customer_id": customer_id}, merge=True)

    if not customer_id:
        customer_id = f"cus_mock_{hash(user_id) & 0xffffffff}"

    session = stripe.billing_portal.Session.create(customer=customer_id, return_url=return_url)
    return session.url

# ==============================================================================
# 🛡️ FEATURE GATEKEEPING & ATOMIC USAGE
# ==============================================================================

def check_and_enforce_coin_limit(user_identifier: str, success_url: str = "https://numista.ai/#/settings?stripe=success", cancel_url: str = "https://numista.ai/#/settings?stripe=cancel") -> bool:
    user_profile = get_user_profile(user_identifier)
    tier = get_user_tier(user_profile)

    if tier == "power_user":
        return True

    coin_count = get_coin_count(user_identifier)
    limit = TIER_COIN_LIMITS.get(tier, TIER_COIN_LIMITS["free"])

    if not within_limit(tier, coin_count):
        tier_order = ["free", "pro", "numismatist", "dealer", "estate", "family_estate", "sovereign"]
        try:
            current_idx = tier_order.index(tier)
            next_tier = tier_order[current_idx + 1] if current_idx + 1 < len(tier_order) else "sovereign"
        except ValueError:
            next_tier = "pro"

        email = user_profile.get("email") or user_identifier
        try:
            checkout_link = create_upgrade_checkout_session(user_identifier, email, next_tier, success_url, cancel_url)
        except Exception as ex:
            checkout_link = None

        detail = {
            "error": "tier_limit_exceeded",
            "message": f"Tier limit exceeded: You have {coin_count} items, but your {tier.capitalize()} tier limit is {limit} items.",
            "stats": {"coin_count": coin_count, "limit": limit, "tier": tier, "next_tier": next_tier},
            "upgrade_url": checkout_link
        }
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    return True


def check_and_increment_daily_usage(user_identifier: str, feature_type: str) -> bool:
    user_profile = get_user_profile(user_identifier)
    tier = get_user_tier(user_profile)

    if tier == "power_user":
        return True

    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    family_group_id = user_profile.get("family_group_id")

    if family_group_id:
        target_ref = db.collection("family_groups").document(family_group_id)
        target_doc = target_ref.get()
        data = target_doc.to_dict() or {} if target_doc.exists else {}

        last_date = data.get("last_reset_utc", "")
        if last_date != today_str:
            target_ref.set({"last_reset_utc": today_str, "deepdive_count": 0, "invoice_scan_count": 0}, merge=True)
            data["deepdive_count"] = 0
            data["invoice_scan_count"] = 0

        allowance = TIER_DAILY_ALLOWANCES.get("family_estate")
        limit = allowance.get(feature_type, 1500)
        current_count = data.get(f"{feature_type}_count", 0)

        if current_count >= limit:
            return False

        target_ref.update({
            f"{feature_type}_count": firestore.Increment(1),
            "last_reset_utc": today_str
        })
        return True

    target_ref = db.collection("users").document(user_identifier)
    last_date = user_profile.get("last_usage_date", "")

    if last_date != today_str:
        target_ref.set({"last_usage_date": today_str, "deepdive_count": 0, "invoice_scan_count": 0}, merge=True)
        user_profile["deepdive_count"] = 0
        user_profile["invoice_scan_count"] = 0

    allowance = TIER_DAILY_ALLOWANCES.get(tier, TIER_DAILY_ALLOWANCES["free"])
    limit = allowance.get(feature_type, 0)
    current_count = user_profile.get(f"{feature_type}_count", 0)

    if limit is not None and current_count >= limit:
        return False

    target_ref.update({
        f"{feature_type}_count": firestore.Increment(1),
        "last_usage_date": today_str
    })
    return True


def lock_overflow_coins(user_id: str, limit: int):
    try:
        coins_ref = db.collection("users").document(user_id).collection("coins").order_by("created_at")
        docs = list(coins_ref.stream())
        if len(docs) <= limit:
            return
        batch = db.batch()
        for idx, doc in enumerate(docs):
            is_locked = idx >= limit
            batch.update(doc.reference, {"locked_pending_upgrade": is_locked})
        batch.commit()
    except Exception as e:
        print(f"[Tier Gatekeeper] Error locking overflow coins for {user_id}: {e}")


def unlock_user_coins(user_id: str):
    try:
        coins_ref = db.collection("users").document(user_id).collection("coins").where("locked_pending_upgrade", "==", True)
        docs = list(coins_ref.stream())
        if not docs:
            return
        batch = db.batch()
        for doc in docs:
            batch.update(doc.reference, {"locked_pending_upgrade": False})
        batch.commit()
    except Exception as e:
        print(f"[Tier Gatekeeper] Error unlocking coins for {user_id}: {e}")
