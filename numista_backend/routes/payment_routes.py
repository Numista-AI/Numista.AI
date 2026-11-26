"""
Stripe Billing, Checkout Sessions, Customer Portal, and Webhook Routes
"""

import os
import hmac
import json
import time
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Tuple
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.concurrency import run_in_threadpool
from firebase_admin import auth as firebase_auth
import stripe
from stripe_config import load_stripe_keys
from schemas.payment_schemas import StripeCheckoutRequest
from routes.deps import db, logger, get_current_user
import tier_gatekeeper as _tg      # _tg._run_txn: the single transaction seam (tests patch it)
from tier_gatekeeper import (
    get_user_profile,
    get_user_tier,
    get_user_allowance,
    get_coin_count,
    AuthFactsUnavailable,
    PURCHASABLE_TIERS,
    PURCHASE_MODE,
    LIFETIME_PRICE_CENTS,
    TIER_DISPLAY_NAMES,
    PRICE_CENTS,
    CHRISTMAS2026_START_UTC,
    CHRISTMAS2026_END_UTC,
    CHRISTMAS2026_DISCOUNT_CENTS,
    CHRISTMAS2026_COUPON_IDS,
    auth_beta_facts,
    load_entitlement_profile,
    effective_limit,
    enforce_entitlement,
    revoke_paid_tier,
    grant_lifetime_purchase,
    revoke_lifetime_purchase,
    LifetimeGrantRefused,
    has_lifetime_flag,
    lifetime_flag_set,
    estate_access,
    is_founding_beta,
    _fresh_email,
)

router = APIRouter(prefix="/api/stripe", tags=["Stripe Payments & Subscriptions"])

stripe_keys = load_stripe_keys()
if stripe_keys.get("secret_key"):
    stripe.api_key = stripe_keys["secret_key"]

def _create_lifetime_checkout(user_uid: str, user_email: str, tier: str):
    md = {
        "user_uid": user_uid,
        "user_email": user_email,
        "target_tier": tier,
        "purchase_kind": "lifetime",
    }
    return stripe.checkout.Session.create(
        mode="payment",
        customer_email=user_email,
        customer_creation="always",
        client_reference_id=user_uid,
        allow_promotion_codes=False,
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": f"Numista.AI {TIER_DISPLAY_NAMES[tier]}"},
                "unit_amount": LIFETIME_PRICE_CENTS[tier],
                "tax_behavior": "exclusive",
            },
            "quantity": 1,
        }],
        automatic_tax={"enabled": True},
        metadata=md,
        payment_intent_data={"metadata": md},
        success_url="https://numista.ai/#/settings?stripe=success",
        cancel_url="https://numista.ai/#/settings?stripe=cancel",
    )


def _resolve_subscription_coupon(
    tier: str,
    interval: str,
    raw_promo: str,
    user_email: str,
    now: Optional[float] = None,
) -> Tuple[Optional[str], str]:
    """Resolves an optional promo code to (stripe_coupon_id, metadata_promo_code)."""
    if not raw_promo:
        return None, ""
    ts = float(time.time() if now is None else now)
    if raw_promo == "CHRISTMAS2026":
        if not (CHRISTMAS2026_START_UTC <= ts < CHRISTMAS2026_END_UTC):
            raise HTTPException(status_code=400, detail={"error": "promo_not_active"})
        return CHRISTMAS2026_COUPON_IDS[tier][interval], "CHRISTMAS2026"

    expected_code = os.environ.get("STRIPE_TEST_PROMO_CODE", "").strip().upper()
    test_coupon_id = os.environ.get("STRIPE_TEST_COUPON_ID", "").strip()
    raw_allowlist = os.environ.get("STRIPE_TEST_BUYER_EMAILS", "")
    allowlist = {e.strip().lower() for e in raw_allowlist.split(",") if e.strip()}
    if (
        expected_code
        and test_coupon_id
        and allowlist
        and (user_email or "").strip().lower() in allowlist
        and hmac.compare_digest(raw_promo, expected_code)
    ):
        return test_coupon_id, "TEST100"

    raise HTTPException(status_code=400, detail={"error": "promo_invalid"})


@router.post("/create-checkout-session")
async def api_stripe_checkout(
    req: StripeCheckoutRequest,
    _user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Creates a Stripe Checkout Session for Copper/Silver/Platinum/Gold subscriptions
    or Lifetime Family Estate ($500 one-time).
    """
    if not stripe.api_key:
        logger.error("Stripe checkout rejected: secret key is not configured")
        raise HTTPException(status_code=502, detail="Stripe is not configured")

    user_uid = _user.get("uid") or _user.get("user_id") or ""
    user_email = (_user.get("email") or "").strip().lower()
    provider = (_user.get("firebase") or {}).get("sign_in_provider")
    if provider == "anonymous" or not user_email or not _valid_uid(user_uid):
        raise HTTPException(status_code=403, detail={"error": "sign_in_required"})

    tier = (req.tier or "").strip().lower()
    if tier not in PURCHASABLE_TIERS:
        raise HTTPException(status_code=400, detail={"error": "tier_not_purchasable"})

    raw_promo = (req.promo_code or "").strip().upper()

    try:
        if PURCHASE_MODE[tier] == "payment":
            if has_lifetime_flag(db, user_uid, user_email):
                raise HTTPException(status_code=409, detail={"error": "already_lifetime"})
            if raw_promo == "CHRISTMAS2026":
                raise HTTPException(status_code=400, detail={"error": "promo_not_applicable_to_lifetime"})
            if raw_promo:
                raise HTTPException(status_code=400, detail={"error": "promo_invalid"})
            session = _create_lifetime_checkout(user_uid, user_email, tier)
            return {"checkout_url": session.url, "session_id": session.id}

        ent_snap = db.collection("entitlements").document(user_uid).get()
        ent_d = (ent_snap.to_dict() or {}) if ent_snap.exists else {}
        if ent_d.get("stripe_subscription_id"):
            profile, _ = load_entitlement_profile(db, user_uid, user_email, with_auth_facts=False)
            if profile.get("subscription_status") in ("active", "trialing", "past_due"):
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error": "already_subscribed",
                        "message": "You already have a plan. To change it, cancel in Manage Billing; you can choose a new plan when the current period ends.",
                    },
                )

        interval = (req.interval or "").strip().lower()
        if interval not in ("month", "year"):
            raise HTTPException(status_code=400, detail={"error": "interval_invalid"})

        coupon_id, promo_meta = _resolve_subscription_coupon(tier, interval, raw_promo, user_email)

        md = {
            "user_uid": user_uid,
            "user_email": user_email,
            "target_tier": tier,
            "purchase_kind": "subscription",
            "interval": interval,
        }
        if promo_meta:
            md["promo_code"] = promo_meta

        session_kwargs: Dict[str, Any] = {
            "mode": "subscription",
            "customer_email": user_email,
            "client_reference_id": user_uid,
            "payment_method_types": ["card"],
            "line_items": [{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": f"Numista.AI {TIER_DISPLAY_NAMES[tier]}"},
                    "unit_amount": PRICE_CENTS[tier][interval],
                    "tax_behavior": "exclusive",
                    "recurring": {"interval": interval},
                },
                "quantity": 1,
            }],
            "automatic_tax": {"enabled": True},
            "metadata": md,
            "subscription_data": {"metadata": md},
            "success_url": "https://numista.ai/#/settings?stripe=success",
            "cancel_url": "https://numista.ai/#/settings?stripe=cancel",
        }
        if coupon_id:
            session_kwargs["discounts"] = [{"coupon": coupon_id}]
        else:
            session_kwargs["allow_promotion_codes"] = False

        session = stripe.checkout.Session.create(**session_kwargs)
        return {"checkout_url": session.url, "session_id": session.id}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Stripe checkout session creation failed")
        raise HTTPException(status_code=502, detail="Unable to create Stripe checkout session")

@router.post("/create-customer-portal")
async def api_stripe_customer_portal(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Generates a self-serve Stripe Customer Portal session link for plan management.
    """
    if not stripe.api_key:
        logger.error("Stripe customer portal rejected: secret key is not configured")
        raise HTTPException(status_code=502, detail="Stripe is not configured")

    uid = current_user.get("uid") or current_user.get("user_id") or ""
    if not _valid_uid(uid):
        raise HTTPException(status_code=404, detail={"error": "no_billing_account"})

    try:
        ent_snap = db.collection("entitlements").document(uid).get()
        cid = (ent_snap.to_dict() or {}).get("stripe_customer_id") if ent_snap.exists else None
        if not _is_id(cid, "cus_"):
            raise HTTPException(status_code=404, detail={"error": "no_billing_account"})

        cust_snap = db.collection("stripe_customers").document(cid).get()
        if not cust_snap.exists:
            raise HTTPException(status_code=404, detail={"error": "no_billing_account"})
        if (cust_snap.to_dict() or {}).get("uid") != uid:
            raise HTTPException(status_code=403, detail={"error": "billing_account_mismatch"})

        portal_session = stripe.billing_portal.Session.create(
            customer=cid,
            return_url="https://numista.ai/#/settings"
        )
        return {"portal_url": portal_session.url}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to generate Stripe Customer Portal session")
        raise HTTPException(status_code=502, detail="Unable to create Stripe customer portal session")

def _own_status(uid: str, caller_uid: str, caller_email: str, sign_in_provider: Optional[str]) -> Dict[str, Any]:
    profile, ent = load_entitlement_profile(
        db,
        caller_uid,
        caller_email or None,
        sign_in_provider=sign_in_provider,
        with_auth_facts=True,
    )
    tier = get_user_tier(profile)
    allowance = get_user_allowance(profile)
    now_ts = time.time()
    coin_limit = effective_limit(profile, ent, now_ts, item="coins")
    ai_allowance = {"deepdive": allowance["deepdive"], "invoice_scan": allowance["invoice_scan"]}
    coin_count = get_coin_count(uid)
    return {
        "uid": uid,
        "stripe_tier": tier,
        "subscription_status": profile.get("subscription_status", "active"),
        "grace_period_until": profile.get("grace_period_until"),
        "coin_count": coin_count,
        "coin_limit": coin_limit,
        "unlimited": coin_limit is None,
        "founding_beta": bool(is_founding_beta(profile)),
        "daily_ai_allowance": ai_allowance,
        "deepdive_count": profile.get("deepdive_count", 0),
        "invoice_scan_count": profile.get("invoice_scan_count", 0),
        "lifetime_family_estate": lifetime_flag_set(profile),
        "estate_access": estate_access(profile, caller_email),     # NET-827 v2.0.6
    }


@router.get("/subscription-status")
async def api_subscription_status(
    uid: str,
    _user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Queries current subscription tier, coin usage, daily AI tokens, and grace period status.
    """
    caller_uid = _user.get("uid") or _user.get("user_id") or ""
    caller_email = (_user.get("email") or "").strip().lower()
    is_dev_guest = os.environ.get("ALLOW_UNAUTHENTICATED") == "1" and caller_email == "dev_guest@numista.ai"
    if not _user.get("admin") and not is_dev_guest:
        if uid.strip() != caller_uid and uid.strip().lower() != caller_email:
            raise HTTPException(status_code=403, detail="Forbidden")
    try:
        is_own = uid.strip() == caller_uid or uid.strip().lower() == caller_email
        sign_in_provider = (_user.get("firebase") or {}).get("sign_in_provider") if is_own else None
        if is_own and _valid_uid(caller_uid):
            try:
                return await run_in_threadpool(_own_status, uid, caller_uid, caller_email, sign_in_provider)
            except AuthFactsUnavailable:
                raise HTTPException(status_code=503, detail="Account check unavailable, try again")

        auth_uid = caller_uid if is_own else (uid.strip() if "@" not in uid else None)
        try:
            profile = get_user_profile(uid, uid_for_auth=auth_uid, sign_in_provider=sign_in_provider)
        except AuthFactsUnavailable:
            raise HTTPException(status_code=503, detail="Account check unavailable, try again")
        tier = get_user_tier(profile)
        allowance = get_user_allowance(profile)
        coin_count = get_coin_count(uid)
        coin_limit = allowance["coins"]
        ai_allowance = {"deepdive": allowance["deepdive"], "invoice_scan": allowance["invoice_scan"]}

        return {
            "uid": uid,
            "stripe_tier": tier,
            "subscription_status": profile.get("subscription_status", "active"),
            "grace_period_until": profile.get("grace_period_until"),
            "coin_count": coin_count,
            "coin_limit": coin_limit,
            "unlimited": coin_limit is None,
            "founding_beta": bool(is_founding_beta(profile)),
            "daily_ai_allowance": ai_allowance,
            "deepdive_count": profile.get("deepdive_count", 0),
            "invoice_scan_count": profile.get("invoice_scan_count", 0),
            "lifetime_family_estate": lifetime_flag_set(profile),
            "estate_access": estate_access(profile, caller_email if is_own else None),   # NET-827 v2.0.6
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting subscription status")
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# NET-827 CORE webhook (plan v1.1.1 §5): dict normalisation, claim/lease, grant,
# renewal, payment-failed, cancellation, refund, dispute, ledger, P1 seam.
# ==============================================================================

LEASE_SECONDS = 60


def claim_event(snap_dict, now):
    """Pure decision: 'claim', 'skip_done' or 'lease_active'."""
    if snap_dict is None:
        return "claim"
    status = snap_dict.get("status")
    if status is None and snap_dict.get("processed_at"):   # NEW: doc written by today's :240
        return "skip_done"
    if status == "done":
        return "skip_done"
    if status == "processing" and now - float(snap_dict.get("ts", 0)) < LEASE_SECONDS:
        return "lease_active"
    return "claim"          # stale lease, retry or failed


def claim_event_txn(transaction, ref, now, event_type=""):
    snap = ref.get(transaction=transaction)
    decision = claim_event(snap.to_dict() if snap.exists else None, now)
    if decision == "claim":
        transaction.set(ref, {"status": "processing", "ts": now, "type": event_type}, merge=True)
    return decision


def _finish(ref, status, **fields):
    ref.set({"status": status, "ts": time.time(), "processed_at": datetime.now(timezone.utc).isoformat(),
             **fields}, merge=True)


def _relock_hook(db, handler_uid, revoked_owner_keys, swept_customer_ids, now):
    """P1 seam (NET-827-P1 §4.2 step 4). Core body: no lock (fail-safe under-lock).
    P1 replaces this body with: return relock_after_revoke(db, handler_uid,
    revoked_owner_keys, swept_customer_ids, now)."""
    return {"accounts_reconciled": [], "review_required": False, "review_reasons": []}


def _is_id(value, prefix):
    return isinstance(value, str) and value.startswith(prefix)


def _valid_uid(uid):
    return bool(uid and isinstance(uid, str) and "@" not in uid)


def _iso(now):
    return datetime.fromtimestamp(float(now), timezone.utc).isoformat()


def _done(**fields):
    return {"status": "done", **fields}


def _failed(reason, **fields):
    logger.warning("[Stripe Webhook] failed: %s", reason)
    return {"status": "failed", "reason": reason, "review_required": True, **fields}


def _add_review(out, reasons, required=True):
    if not reasons:
        return out
    out["review_reasons"] = list(out.get("review_reasons") or []) + list(reasons)
    if required:
        out["review_required"] = True
    return out


def _merge_relock(out, rel):
    if rel and rel.get("review_required"):
        out["review_required"] = True
        out["review_reasons"] = list(out.get("review_reasons") or []) + list(rel.get("review_reasons") or [])
    return out


def _resolve_uid(db, customer, metadata):
    """§5.5: stripe_customers/{customer}.uid, else metadata.user_uid, else None."""
    if _is_id(customer, "cus_"):
        snap = db.collection("stripe_customers").document(customer).get()
        if snap.exists:
            mapped = (snap.to_dict() or {}).get("uid")
            if _valid_uid(mapped):
                return mapped
    from_md = (metadata or {}).get("user_uid")
    return from_md if _valid_uid(from_md) else None


def _post_grant_email(db, uid):
    """F3: (current Auth email lower-cased, previous entitlements.email). Auth error raises."""
    email = _fresh_email(db, uid)
    snap = db.collection("entitlements").document(uid).get()
    old = ((snap.to_dict() or {}).get("email") if snap.exists else None) or None
    return email, old


def _email_patch(t, db, uid, email, old, out):
    """Writes entitlements.email in the event's transaction when it differs (F3)."""
    if email and email != old:
        t.set(db.collection("entitlements").document(uid), {"email": email}, merge=True)
        if old:
            logger.info("email_changed uid=%s", uid)
            _add_review(out, ["email_changed"])


def _user_refs(db, uid, email):
    refs = [db.collection("users").document(uid)]
    if email and email != uid:
        refs.append(db.collection("users").document(email))
    return refs


def _ledger_row(db, pi):
    if not _is_id(pi, "pi_"):
        return None
    snap = db.collection("stripe_payments").document(pi).get()
    return (snap.to_dict() or {}) if snap.exists else None


def _invoice_payment_intents(obj):
    """§5.7: legacy payment_intent; else payments.data[i].payment.payment_intent; else
    InvoicePayment.list (Stripe error raises -> retry)."""
    pi = obj.get("payment_intent")
    if _is_id(pi, "pi_"):
        return [pi]

    def _from(items):
        out = []
        for item in items or []:
            p = ((item or {}).get("payment") or {}).get("payment_intent")
            if _is_id(p, "pi_") and p not in out:
                out.append(p)
        return out

    found = _from((obj.get("payments") or {}).get("data"))
    if found:
        return found
    inv_id = obj.get("id")
    if not _is_id(inv_id, "in_"):
        return []
    listed = stripe.InvoicePayment.list(invoice=inv_id, limit=10).to_dict()
    return _from(listed.get("data"))


def _session_amounts(obj):
    total_details = obj.get("total_details") or {}
    return {
        "amount_subtotal": obj.get("amount_subtotal"),
        "amount_discount": total_details.get("amount_discount") or 0,
        "amount_tax": total_details.get("amount_tax") or 0,
        "amount_total": obj.get("amount_total"),
        "currency": (obj.get("currency") or "").lower(),
    }


def _grant_subscription(db, obj, md, uid, now):
    """§5.4 steps 2-8 (subscription kind) + v2.0.7 CHRISTMAS2026 / TEST100 discount verification."""
    if md.get("purchase_kind") != "subscription":
        return _failed("purchase_kind_unsupported")
    if obj.get("mode") != "subscription":
        return _failed("mode_mismatch")
    tier = (md.get("target_tier") or "").lower()
    if tier not in PURCHASABLE_TIERS:
        return _failed("tier_not_purchasable")
    if PURCHASE_MODE[tier] != "subscription":
        return _failed("tier_mode_mismatch")
    interval = md.get("interval")
    exp = PRICE_CENTS.get(tier, {}).get(interval)
    if exp is None or obj.get("amount_subtotal") != exp or (obj.get("currency") or "").lower() != "usd":
        return _failed("amount_mismatch")

    amounts = _session_amounts(obj)
    promo = (md.get("promo_code") or "").strip().upper()
    if promo == "CHRISTMAS2026":
        if obj.get("payment_status") != "paid":
            return _failed("not_paid")
        expected_disc = CHRISTMAS2026_DISCOUNT_CENTS.get(tier, {}).get(interval)
        if expected_disc is None or amounts["amount_discount"] != expected_disc:
            return _failed("discount_mismatch")
    elif promo == "TEST100":
        test_cid = os.environ.get("STRIPE_TEST_COUPON_ID", "").strip()
        if (
            not test_cid
            or obj.get("payment_status") not in ("paid", "no_payment_required")
            or amounts["amount_discount"] != exp
            or obj.get("amount_total") != 0
        ):
            return _failed("discount_mismatch")
    elif promo == "":
        if obj.get("payment_status") != "paid":
            return _failed("not_paid")
        if amounts["amount_discount"] != 0:
            return _failed("discount_mismatch")
    else:
        return _failed("discount_mismatch")

    sub_id, cid = obj.get("subscription"), obj.get("customer")
    if not (_is_id(sub_id, "sub_") and _is_id(cid, "cus_")):
        return _failed("grant_ids_missing")
    try:
        facts = auth_beta_facts(uid, None)                  # AuthFactsUnavailable -> retry
    except AuthFactsUnavailable as e:
        if isinstance(e.__cause__, firebase_auth.UserNotFoundError):
            return _failed("grant_uid_unknown")
        raise
    if facts["_auth_is_anonymous"]:
        return _failed("grant_anonymous_uid")
    email = (md.get("user_email") or obj.get("customer_email") or "").strip().lower() or None
    iso_now = _iso(now)
    pi = obj.get("payment_intent")

    def _txn(t):
        cust_ref = db.collection("stripe_customers").document(cid)
        cust = cust_ref.get(transaction=t)
        if cust.exists:
            owner = (cust.to_dict() or {}).get("uid")
            if owner and owner != uid:
                return "customer_uid_conflict"
        payload = {"stripe_tier": tier, "subscription_status": "active", "grace_period_until": None,
                   "stripe_customer_id": cid, "updated_at": iso_now}
        for ref in _user_refs(db, uid, email):
            t.set(ref, payload, merge=True)
        ent = {"stripe_subscription_id": sub_id, "stripe_customer_id": cid, "updated_at": iso_now}
        if email:
            ent["email"] = email
        t.set(db.collection("entitlements").document(uid), ent, merge=True)
        t.set(cust_ref, {"uid": uid}, merge=True)
        if _is_id(pi, "pi_"):
            ledger_row = {
                "uid": uid, "kind": "subscription", "tier": tier, "subscription_id": sub_id,
                "invoice_id": None, **amounts, "granted": True, "created_at": iso_now,
            }
            if promo:
                ledger_row["promo_code"] = promo
            t.set(db.collection("stripe_payments").document(pi), ledger_row, merge=True)
        return "ok"

    if _tg._run_txn(db, _txn) == "customer_uid_conflict":
        return _failed("customer_uid_conflict")
    enforce_entitlement(db, uid, email, now)                # unlock on upgrade
    out = _done()
    if email is None:
        out.update(review_required=True, reason="grant_email_missing")
    return out


def _grant_lifetime(db, obj, md, uid, now):
    """§5.8.1 (Eric E-1): one-time $500 Lifetime Family Estate."""
    if obj.get("mode") != "payment":
        return _failed("mode_mismatch")
    if obj.get("payment_status") != "paid":
        return _failed("not_paid")
    tier = (md.get("target_tier") or "").lower()
    if PURCHASE_MODE.get(tier) != "payment":
        return _failed("tier_not_purchasable")
    if obj.get("amount_subtotal") != LIFETIME_PRICE_CENTS[tier] or (obj.get("currency") or "").lower() != "usd":
        return _failed("amount_mismatch")
    amounts = _session_amounts(obj)
    if amounts["amount_discount"] != 0:
        return _failed("discount_mismatch")
    pi = obj.get("payment_intent")
    cid = obj.get("customer")
    if not _is_id(pi, "pi_") or not (cid is None or _is_id(cid, "cus_")):
        return _failed("grant_ids_missing")
    try:
        facts = auth_beta_facts(uid, None)                  # AuthFactsUnavailable -> retry
    except AuthFactsUnavailable as e:
        if isinstance(e.__cause__, firebase_auth.UserNotFoundError):
            return _failed("grant_uid_unknown")
        raise
    if facts["_auth_is_anonymous"]:
        return _failed("grant_anonymous_uid")
    email = (md.get("user_email") or obj.get("customer_email") or "").strip().lower() or None
    try:
        result = grant_lifetime_purchase(db, uid, email, pi, cid, tier, now, amounts)
    except LifetimeGrantRefused as e:
        return _failed(e.reason)
    out = _done()
    if email is None:
        out.update(review_required=True, reason="grant_email_missing")
    if result == "duplicate":
        out.update(review_required=True, reason="lifetime_duplicate_purchase")
    enforce_entitlement(db, uid, email, now)                # unlock up to the new allowance
    # Q7: overlap with an active subscription -> audit + informational review reason only.
    profile, ent = load_entitlement_profile(db, uid, email, with_auth_facts=False)
    paid = (profile.get("stripe_tier") or "").lower()
    if profile.get("subscription_status") in ("active", "trialing") and PURCHASE_MODE.get(paid) == "subscription":
        db.collection("entitlements").document(uid).set(
            {"lifetime": {"overlap_subscription": {"tier": paid, "subscription_id": ent.get("stripe_subscription_id"),
                                                   "at": now}}}, merge=True)
        _add_review(out, ["lifetime_with_active_subscription"], required=False)
    return out


def _handle_checkout_completed(db, obj, now):
    md = obj.get("metadata") or {}
    uid = obj.get("client_reference_id") or md.get("user_uid")
    if not _valid_uid(uid):
        return _failed("grant_uid_missing")                 # no email fallback
    if md.get("purchase_kind") == "lifetime":
        return _grant_lifetime(db, obj, md, uid, now)
    return _grant_subscription(db, obj, md, uid, now)


def _handle_invoice_paid(db, obj, now):
    sd = ((obj.get("parent") or {}).get("subscription_details") or {})
    sub_id = obj.get("subscription") or sd.get("subscription")
    if not _is_id(sub_id, "sub_"):
        return _done(reason="invoice_no_subscription")
    uid = _resolve_uid(db, obj.get("customer"), sd.get("metadata"))
    if uid is None:
        return _failed("renewal_uid_unknown")
    ent_snap = db.collection("entitlements").document(uid).get()
    ent_now = (ent_snap.to_dict() or {}) if ent_snap.exists else {}
    known_sub = ent_now.get("stripe_subscription_id")
    if known_sub and known_sub != sub_id:
        logger.info("renewal_other_sub uid=%s", uid)
        return _done(reason="renewal_other_sub")
    email, old = _post_grant_email(db, uid)
    pis = _invoice_payment_intents(obj)
    out = _done()
    if not pis:
        logger.info("ledger_pi_missing invoice=%s", obj.get("id"))
        out["reason"] = "ledger_pi_missing"
    profile, ent = load_entitlement_profile(db, uid, email, with_auth_facts=False)
    last = (ent.get("last_revoke") or {}).get("subscription") or {}
    created = obj.get("created")
    after_revoke = isinstance(created, (int, float)) and created > float(last.get("at") or 0)
    status_ok = last.get("subscription_id") != sub_id or after_revoke
    reaffirm_tier = None
    if not profile.get("stripe_tier"):                      # (i) merged view has no paid tier
        refused = None
        sub = None
        if not _is_id(sub_id, "sub_"):
            refused = "ii"
        else:
            sub = stripe.Subscription.retrieve(sub_id).to_dict()   # Stripe error -> retry
            if sub.get("status") not in ("active", "trialing"):
                refused = "ii"
        if refused is None:
            for pi in pis:
                row = _ledger_row(db, pi)
                if row and row.get("revoked"):
                    refused = "iii"
                    break
        if refused is None and last.get("subscription_id") == sub_id and not after_revoke:
            refused = "iv"
        if refused is None:
            tier = ((sub.get("metadata") or {}).get("target_tier") or "").lower()
            if PURCHASE_MODE.get(tier) == "subscription":
                reaffirm_tier = tier
            else:
                refused = "v"
        if refused:
            logger.info("reaffirm_refused:%s uid=%s", refused, uid)
            _add_review(out, [f"reaffirm_refused:{refused}"])
    iso_now = _iso(now)
    tier_after = reaffirm_tier or profile.get("stripe_tier")

    def _txn(t):
        for pi in pis:
            t.set(db.collection("stripe_payments").document(pi),
                  {"uid": uid, "kind": "subscription", "tier": tier_after, "subscription_id": sub_id,
                   "invoice_id": obj.get("id"), "granted": True, "created_at": iso_now}, merge=True)
        fields = {}
        if status_ok:
            fields.update({"subscription_status": "active", "grace_period_until": None, "updated_at": iso_now})
        if reaffirm_tier:
            fields["stripe_tier"] = reaffirm_tier
        if fields:
            for ref in _user_refs(db, uid, email):
                t.set(ref, fields, merge=True)
        _email_patch(t, db, uid, email, old, out)
        return True

    _tg._run_txn(db, _txn)
    enforce_entitlement(db, uid, email, now)
    return out


def _handle_payment_failed(db, obj, now):
    sd = ((obj.get("parent") or {}).get("subscription_details") or {})
    uid = _resolve_uid(db, obj.get("customer"), sd.get("metadata"))
    if uid is None:
        return _failed("renewal_uid_unknown")
    email, old = _post_grant_email(db, uid)
    out = _done()
    lines = ((obj.get("lines") or {}).get("data") or [])
    if lines:
        price = (lines[0].get("price") or lines[0].get("plan") or {})
        unit_amount = price.get("unit_amount")
        interval = (price.get("recurring") or {}).get("interval")
        meta_tier = ((obj.get("metadata") or {}).get("target_tier") or "").lower()
        if meta_tier in PRICE_CENTS and unit_amount != PRICE_CENTS.get(meta_tier, {}).get(interval):
            _add_review(out, ["price_tier_mismatch"])
    grace = datetime.fromtimestamp(float(now), timezone.utc) + timedelta(days=3)

    def _txn(t):
        for ref in _user_refs(db, uid, email):
            t.set(ref, {"subscription_status": "past_due", "grace_period_until": grace.isoformat()}, merge=True)
        _email_patch(t, db, uid, email, old, out)
        return True

    _tg._run_txn(db, _txn)
    return out


def _handle_subscription_updated(db, obj, now):
    status = obj.get("status")
    if status in ("canceled", "unpaid"):
        return _handle_cancellation(db, obj, now)
    if status not in ("active", "trialing"):
        logger.info("subscription_updated_status_%s", status)
        return _done(reason=f"status_{status}")
    uid = _resolve_uid(db, obj.get("customer"), obj.get("metadata"))
    if uid is None:
        return _failed("renewal_uid_unknown")
    ent_snap = db.collection("entitlements").document(uid).get()
    ent = (ent_snap.to_dict() or {}) if ent_snap.exists else {}
    last = (ent.get("last_revoke") or {}).get("subscription") or {}
    if last.get("subscription_id") == obj.get("id"):
        logger.info("stale_after_revoke uid=%s", uid)
        return _done(reason="stale_after_revoke")
    email, old = _post_grant_email(db, uid)
    out = _done()
    items = ((obj.get("items") or {}).get("data") or [])
    if items:
        price = (items[0].get("price") or {})
        unit_amount = price.get("unit_amount")
        interval = (price.get("recurring") or {}).get("interval")
        meta_tier = ((obj.get("metadata") or {}).get("target_tier") or "").lower()
        if meta_tier in PRICE_CENTS and unit_amount != PRICE_CENTS.get(meta_tier, {}).get(interval):
            _add_review(out, ["price_tier_mismatch"])

    def _txn(t):
        for ref in _user_refs(db, uid, email):              # status fields only; never stripe_tier
            t.set(ref, {"subscription_status": status, "grace_period_until": None}, merge=True)
        _email_patch(t, db, uid, email, old, out)
        return True

    _tg._run_txn(db, _txn)
    return out


def _handle_cancellation(db, obj, now):
    """§5.6 steps 1-7 (customer.subscription.deleted, or .updated to canceled/unpaid)."""
    md = obj.get("metadata") or {}
    if md.get("purchase_kind") and md.get("purchase_kind") != "subscription":
        return _failed("purchase_kind_unsupported")
    customer = obj.get("customer")
    handler_uid = _resolve_uid(db, customer, md)
    email = _fresh_email(db, handler_uid) if handler_uid else None   # F3
    res = revoke_paid_tier(db, handler_uid, email, customer_id=customer, revoked_subscription_id=obj.get("id"))
    swept_customer_ids = [customer] if _is_id(customer, "cus_") else []
    if not res.revoked_owner_keys and not res.guard_skipped:
        return _failed("nothing_to_revoke")
    rel = _relock_hook(db, handler_uid, res.revoked_owner_keys, swept_customer_ids, now)
    if handler_uid:
        db.collection("entitlements").document(handler_uid).set(
            {"last_revoke": {"subscription": {"subscription_id": obj.get("id"), "payment_intent": None,
                                              "at": now, "reason": "canceled"}}}, merge=True)
    out = _merge_relock(_done(), rel)
    if res.guard_skipped:
        _add_review(out, ["revoke_skip_other_sub"])
    return out


def _revoke_from_ledger(db, row, pi, customer, reason, now):
    """Full refund / lost dispute with a ledger row (§5.6, §5.8.2)."""
    if not row.get("granted"):
        return _done(reason="not_granted")
    kind, uid = row.get("kind"), row.get("uid")
    swept = [customer] if _is_id(customer, "cus_") else []
    if kind == "lifetime":
        res = revoke_lifetime_purchase(db, uid, pi, reason, now)
        rel = _relock_hook(db, uid, res.revoked_owner_keys, [], now)
        return _merge_relock(_done(), rel)
    if kind == "subscription":
        email = _fresh_email(db, uid) if _valid_uid(uid) else None    # F3
        res = revoke_paid_tier(db, uid, email, customer_id=customer,
                               revoked_subscription_id=row.get("subscription_id"))
        if not res.revoked_owner_keys and not res.guard_skipped:
            return _failed("nothing_to_revoke")
        rel = _relock_hook(db, uid, res.revoked_owner_keys, swept, now)
        db.collection("stripe_payments").document(pi).set({"revoked": {"at": now, "reason": reason}}, merge=True)
        if _valid_uid(uid):
            db.collection("entitlements").document(uid).set(
                {"last_revoke": {"subscription": {"subscription_id": row.get("subscription_id"),
                                                  "payment_intent": pi, "at": now, "reason": reason}}}, merge=True)
        out = _merge_relock(_done(), rel)
        if res.guard_skipped:
            _add_review(out, ["revoke_skip_other_sub"])
        return out
    if kind == "beta":
        db.collection("entitlements").document(uid).set(
            {"beta_special_until": datetime.fromtimestamp(float(now), timezone.utc)}, merge=True)
        rel = _relock_hook(db, uid, [uid], swept, now)
        return _merge_relock(_done(), rel)
    return _failed("ledger_kind_unknown")


def _handle_refund(db, obj, now):
    if obj.get("refunded") is not True:
        logger.info("partial_refund charge=%s", obj.get("id"))
        return _done(reason="partial_refund")
    pi = obj.get("payment_intent")
    row = _ledger_row(db, pi)
    if row is None:
        return _failed("no_ledger_entry")                   # flag-only (Eric decision 5)
    return _revoke_from_ledger(db, row, pi, obj.get("customer"), "refunded", now)


def _handle_dispute_created(db, obj, now):
    row = _ledger_row(db, obj.get("payment_intent"))
    if row is None:
        return _failed("no_ledger_entry")
    uid = row.get("uid")
    if not uid:
        logger.warning("charge.dispute.created ledger row missing uid pi=%s", obj.get("payment_intent"))
        return _done(reason="dispute_uid_missing")
    db.collection("entitlements").document(uid).set({"dispute_review": True}, merge=True)
    return _done()


def _handle_dispute_closed(db, obj, now):
    status = obj.get("status")
    if status != "lost":
        return _done(reason=f"dispute_{status}")
    pi = obj.get("payment_intent")
    row = _ledger_row(db, pi)
    if row is None:
        return _failed("no_ledger_entry")
    if row.get("kind") == "lifetime":
        return _revoke_from_ledger(db, row, pi, None, "dispute_lost", now)
    charge = obj.get("charge")
    if isinstance(charge, str):
        customer = (stripe.Charge.retrieve(charge).to_dict() or {}).get("customer")   # no .get on SDK objects
    elif isinstance(charge, dict):
        customer = charge.get("customer")
    else:
        customer = None
    return _revoke_from_ledger(db, row, pi, customer, "dispute_lost", now)


_HANDLERS = {
    "checkout.session.completed": _handle_checkout_completed,
    "invoice.paid": _handle_invoice_paid,
    "invoice.payment_failed": _handle_payment_failed,
    "customer.subscription.updated": _handle_subscription_updated,
    "customer.subscription.deleted": _handle_cancellation,
    "charge.refunded": _handle_refund,
    "charge.dispute.created": _handle_dispute_created,
    "charge.dispute.closed": _handle_dispute_closed,
}


@router.post("/webhook")
async def api_stripe_webhook(request: Request):
    """
    Handles Stripe webhooks with signature verification, a Firestore claim/lease per event
    (done / retry / failed), and the NET-827 core grant / renewal / revoke rules.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
    is_prod = os.environ.get("K_SERVICE") or os.environ.get("ENVIRONMENT") == "production"
    
    event = None
    if webhook_secret:
        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing signature header")
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
            event = event.to_dict()      # stripe 15.2.1 StripeObject has no .get (M10)
        except Exception as e:
            logger.error(f"Stripe webhook signature verification failed: {e}")
            raise HTTPException(status_code=400, detail="Invalid signature")
    else:
        if is_prod:
            logger.error("[CRITICAL] Stripe webhook rejected: STRIPE_WEBHOOK_SECRET is not configured in production!")
            raise HTTPException(status_code=400, detail="Stripe webhook secret is missing")
        logger.warning("[DEV MODE] STRIPE_WEBHOOK_SECRET not set; parsing unverified JSON payload.")
        try:
            event = json.loads(payload.decode('utf-8'))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_id = event.get("id") if isinstance(event, dict) else None
    if not _is_id(event_id, "evt_"):
        raise HTTPException(status_code=400, detail="Invalid event")
    event_type = event.get("type") or ""
    obj = (event.get("data") or {}).get("object") or {}
    now = time.time()

    # 1. Claim / lease in Firestore (stripe_events/{event_id})
    event_ref = db.collection("stripe_events").document(event_id)
    try:
        decision = _tg._run_txn(db, lambda t: claim_event_txn(t, event_ref, now, event_type))
    except Exception:
        logger.exception(f"[Stripe Webhook] claim failed for {event_id}")
        raise HTTPException(status_code=500, detail="Event claim failed")
    if decision == "skip_done":
        logger.info(f"[Stripe Webhook] Duplicate event {event_id} skipped.")
        return {"status": "skipped_duplicate", "event_id": event_id}
    if decision == "lease_active":
        raise HTTPException(status_code=500, detail="Event is being processed")

    # 2. Dispatch; any exception -> retry / 500 (Stripe redelivers)
    try:
        handler = _HANDLERS.get(event_type)
        if handler is None:
            logger.info(f"[Stripe Webhook] ignored_event_type {event_type}")
            outcome = _done(reason="ignored_event_type")
        else:
            outcome = handler(db, obj, now)
    except Exception:
        logger.exception(f"[Stripe Webhook] processing failed for {event_id}; marked retry")
        try:
            _finish(event_ref, "retry", type=event_type)
        except Exception:
            logger.exception(f"[Stripe Webhook] could not write retry for {event_id}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

    status = outcome.pop("status")
    _finish(event_ref, status, type=event_type, **outcome)
    return {"status": status, "event_type": event_type, "event_id": event_id}
