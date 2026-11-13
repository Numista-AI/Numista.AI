"""
Atomic Image Model Router (Nano Banana Pro -> Nano Banana 2 Monthly Cap).

Routes the first 100 image generations per UTC month to Nano Banana Pro
(gemini-3-pro-image) for maximum coin typography accuracy, then automatically
routes remaining generations to Nano Banana 2 (gemini-3.1-flash-image).

Uses an atomic Firestore transaction on `system_metrics/image_gen_quota_{YYYY-MM}`
prior to generation to prevent concurrency races, and a compensating decrement
transaction if the Pro API call fails before falling back to Flash Image.
Logs zero PII (operational month_key, model, count, and cap only).
"""

from datetime import datetime, timezone
import logging
from typing import Any, Callable, Optional, Tuple

from google.api_core.exceptions import GoogleAPIError
from google.cloud import firestore
from google.cloud.exceptions import GoogleCloudError

_FIRESTORE_TRANSIENT_ERRORS = (
    GoogleAPIError,
    GoogleCloudError,
    ConnectionError,
    TimeoutError,
)

from config import (
    GEMINI_IMAGE_MODEL,
    GEMINI_IMAGE_PRO_MODEL,
    GEMINI_IMAGE_PRO_MONTHLY_CAP,
)

logger = logging.getLogger(__name__)


def current_month_key(now: Optional[datetime] = None) -> str:
    """Return the UTC YYYY-MM key used for the monthly image quota document."""
    dt = now or datetime.now(timezone.utc)
    return dt.strftime("%Y-%m")


def _quota_doc_ref(db: firestore.Client, month_key: str) -> firestore.DocumentReference:
    return db.collection("system_metrics").document(f"image_gen_quota_{month_key}")


@firestore.transactional
def _reserve_pro_slot_tx(
    transaction: firestore.Transaction,
    doc_ref: firestore.DocumentReference,
    cap: int,
) -> Tuple[bool, int]:
    """Atomically reserve a Pro image slot if pro_count < cap."""
    snapshot = doc_ref.get(transaction=transaction)
    current_count = 0
    if snapshot.exists:
        data = snapshot.to_dict() or {}
        current_count = int(data.get("pro_count", 0) or 0)

    if current_count < cap:
        new_count = current_count + 1
        transaction.set(
            doc_ref,
            {
                "pro_count": new_count,
                "updated_at": firestore.SERVER_TIMESTAMP,
            },
            merge=True,
        )
        return True, new_count

    return False, current_count


@firestore.transactional
def _release_pro_slot_tx(
    transaction: firestore.Transaction,
    doc_ref: firestore.DocumentReference,
) -> int:
    """Compensating decrement when a reserved Pro API call fails."""
    snapshot = doc_ref.get(transaction=transaction)
    if not snapshot.exists:
        return 0
    data = snapshot.to_dict() or {}
    current_count = int(data.get("pro_count", 0) or 0)
    new_count = max(0, current_count - 1)
    transaction.set(
        doc_ref,
        {
            "pro_count": new_count,
            "updated_at": firestore.SERVER_TIMESTAMP,
        },
        merge=True,
    )
    return new_count


def reserve_image_model(
    db: Optional[firestore.Client],
    month_key: Optional[str] = None,
    cap: Optional[int] = None,
) -> Tuple[str, int, bool, str]:
    """
    Select the image generation model for this request.

    Returns:
        (selected_model, monthly_pro_count, reserved_pro, month_key)
    """
    mkey = month_key or current_month_key()
    effective_cap = GEMINI_IMAGE_PRO_MONTHLY_CAP if cap is None else cap

    if db is None:
        logger.warning(
            "image_model_router: Firestore client unavailable; defaulting to fallback",
            extra={
                "month_key": mkey,
                "selected_model": GEMINI_IMAGE_MODEL,
                "monthly_pro_count": -1,
                "cap": effective_cap,
                "fallback_triggered": True,
            },
        )
        return GEMINI_IMAGE_MODEL, 0, False, mkey

    try:
        doc_ref = _quota_doc_ref(db, mkey)
        transaction = db.transaction()
        reserved_pro, count = _reserve_pro_slot_tx(transaction, doc_ref, effective_cap)
    except _FIRESTORE_TRANSIENT_ERRORS as exc:
        logger.warning(
            "image_model_router: Firestore reservation failed (%s: %s); falling back to %s",
            type(exc).__name__,
            exc,
            GEMINI_IMAGE_MODEL,
            extra={
                "month_key": mkey,
                "selected_model": GEMINI_IMAGE_MODEL,
                "monthly_pro_count": -1,
                "cap": effective_cap,
                "fallback_triggered": True,
            },
        )
        return GEMINI_IMAGE_MODEL, 0, False, mkey

    selected_model = GEMINI_IMAGE_PRO_MODEL if reserved_pro else GEMINI_IMAGE_MODEL

    logger.info(
        "image_model_router: month=%s model=%s pro_count=%d/%d fallback=%s",
        mkey,
        selected_model,
        count,
        effective_cap,
        not reserved_pro,
    )
    return selected_model, count, reserved_pro, mkey


def release_pro_image_reservation(
    db: Optional[firestore.Client],
    month_key: str,
) -> int:
    """Run compensating decrement if a reserved Pro generation failed."""
    if db is None:
        return 0
    try:
        doc_ref = _quota_doc_ref(db, month_key)
        transaction = db.transaction()
        new_count = _release_pro_slot_tx(transaction, doc_ref)
        logger.warning(
            "image_model_router: released pro reservation month=%s new_pro_count=%d",
            month_key,
            new_count,
        )
        return new_count
    except _FIRESTORE_TRANSIENT_ERRORS as exc:
        logger.warning(
            "image_model_router: failed to release pro reservation month=%s (%s: %s)",
            month_key,
            type(exc).__name__,
            exc,
        )
        return 0


def execute_with_image_routing(
    db: Optional[firestore.Client],
    call_fn: Callable[[str], Any],
    month_key: Optional[str] = None,
    cap: Optional[int] = None,
) -> Tuple[Any, str]:
    """
    Execute an image generation callable with monthly Pro cap and error fallback.

    `call_fn(model_id)` is invoked with the selected model ID. If Pro was reserved
    and raises an exception, the slot is released via compensating transaction and
    `call_fn` is retried once with `GEMINI_IMAGE_MODEL` (Nano Banana 2).
    """
    selected_model, _count, reserved_pro, mkey = reserve_image_model(
        db=db, month_key=month_key, cap=cap
    )
    try:
        return call_fn(selected_model), selected_model
    except Exception as exc:
        if not reserved_pro:
            raise
        logger.warning(
            "image_model_router: Pro generation failed (%s); falling back to %s",
            type(exc).__name__,
            GEMINI_IMAGE_MODEL,
        )
        release_pro_image_reservation(db=db, month_key=mkey)
        return call_fn(GEMINI_IMAGE_MODEL), GEMINI_IMAGE_MODEL
