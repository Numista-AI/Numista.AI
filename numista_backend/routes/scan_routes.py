"""
Vision AI, Binder Scan, Checklist Ingestion, and Review Hub Provenance Routes
Numista.AI System of Record (Desktop Web 2026 Launch)
"""

import os
import json
import uuid
import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Depends, Request
from pydantic import BaseModel, Field
from google.cloud import firestore

from config import DEFAULT_VISION_MODEL, FALLBACK_VISION_MODEL
from config.ingestion_config import (
    CLASSIFIER_MODEL,
    EXTRACTION_MODEL,
    CLASSIFIER_CONFIDENCE_THRESHOLD,
    ACTIVE_IMPORT_STATUSES,
)
from routes.deps import db, genai_client, genai_types
from services.document_classifier_service import classify_document_bytes
from services.checklist_parser import extract_checklist_document

logger = logging.getLogger("numista_backend.scan_routes")

router = APIRouter(prefix="/api", tags=["Document Ingestion & Review Hub"])


# ── Pydantic Request Models ───────────────────────────────────────────────────

class AbortSessionRequest(BaseModel):
    uid: str
    import_session_id: str
    target_status: Optional[str] = "aborted"  # 'aborted' or 'superseded'

class ResumeSessionRequest(BaseModel):
    uid: str
    import_session_id: str

class CommitSessionRequest(BaseModel):
    uid: str
    import_session_id: str
    condition_override: Optional[str] = None
    storage_location_override: Optional[str] = None

class BulkConditionRequest(BaseModel):
    uid: str
    import_session_id: str
    condition: str
    scope: Optional[str] = "unspecified_only"  # 'unspecified_only' or 'all'


# ── Helper Functions ──────────────────────────────────────────────────────────

def enforce_review_queue_fifo_cap(uid: str, max_items: int = 500) -> int:
    """
    Enforces a strict 500-item FIFO cap on users/{uid}/review_queue
    to protect Firestore read/write quotas and Tier Gatekeeper budgets.
    """
    if not db or not uid:
        return 0
    try:
        col_ref = db.collection("users").document(uid).collection("review_queue")
        docs = list(col_ref.order_by("created_at", direction=firestore.Query.ASCENDING).stream())
        overflow = len(docs) - max_items
        if overflow > 0:
            logger.info(f"Review queue overflow for user {uid}: removing {overflow} oldest items (FIFO).")
            batch = db.batch()
            for doc in docs[:overflow]:
                batch.delete(doc.reference)
            batch.commit()
            return overflow
    except Exception as e:
        logger.warning(f"Failed to enforce review queue FIFO cap: {e}")
    return 0


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/upload_document")
async def upload_document(
    uid: str = Form(...),
    user_email: Optional[str] = Form(""),
    file: UploadFile = File(...),
    import_session_id: Optional[str] = Form(""),
    force_reprocess: Optional[bool] = Form(False),
):
    """
    Canonical Multi-Modal Document Upload Gateway.
    Classifies document, enforces SHA-256 deduplication, and routes to specialized
    Checklist vs. Invoice extractors.
    """
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty document payload")

    filename = file.filename or "uploaded_doc.pdf"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    mime_map = {"pdf": "application/pdf", "png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}
    mime_type = file.content_type or mime_map.get(ext, "application/pdf")
    if mime_type in ("application/octet-stream", "binary/octet-stream", ""):
        mime_type = "application/pdf" if contents[:4] == b"%PDF" else "image/jpeg"

    doc_hash = hashlib.sha256(contents).hexdigest()
    session_id = import_session_id or f"sess_{uuid.uuid4().hex[:12]}"

    # Step 1: Content Hash Deduplication Check
    if not force_reprocess:
        try:
            existing_docs = list(
                db.collection("users").document(uid)
                .collection("review_queue")
                .where("doc_hash", "==", doc_hash)
                .where("status", "in", ACTIVE_IMPORT_STATUSES)
                .limit(5)
                .stream()
            )
            if existing_docs:
                existing_session_id = existing_docs[0].to_dict().get("import_session_id", "")
                logger.info(f"Duplicate document detected (hash={doc_hash[:8]}, session={existing_session_id})")
                return {
                    "status": "duplicate_detected",
                    "doc_hash": doc_hash,
                    "existing_session_id": existing_session_id,
                    "existing_items_count": len(existing_docs),
                    "message": "An active review session already exists for this document."
                }
        except Exception as dup_err:
            logger.warning(f"Deduplication check error: {dup_err}")

    # Step 2: Multi-Modal Document Classification
    classification = classify_document_bytes(
        file_bytes=contents,
        mime_type=mime_type,
        genai_client=genai_client
    )

    doc_type = classification.get("document_type", "checklist")
    conf = classification.get("confidence", 1.0)
    requires_conf = classification.get("requires_confirmation", False)

    # Step 3: Route to Checklist Extraction Engine
    if doc_type == "checklist" or "check" in doc_type:
        extraction_result = extract_checklist_document(
            file_bytes=contents,
            mime_type=mime_type,
            filename=filename,
            genai_client=genai_client,
            uid=uid,
            import_session_id=session_id
        )

        items = extraction_result.get("items", [])
        # Stage extracted items in users/{uid}/review_queue
        batch = db.batch()
        col_ref = db.collection("users").document(uid).collection("review_queue")
        
        staged_items = []
        is_quarantined = conf < 0.85 or requires_conf
        for item in items:
            doc_id = str(uuid.uuid4())
            item["staging_id"] = doc_id
            item["uid"] = uid
            item["user_email"] = user_email
            item["confidence_score"] = conf
            item["created_at"] = datetime.now(timezone.utc).isoformat()
            if is_quarantined:
                item["status"] = "quarantined"
                item["review_needed"] = True
                item["priority_score"] = round(1.0 - conf, 2)
            else:
                item["status"] = "staged"
                item["review_needed"] = False
                item["priority_score"] = 0.0

            doc_ref = col_ref.document(doc_id)
            batch.set(doc_ref, item)
            staged_items.append(item)

        batch.commit()
        enforce_review_queue_fifo_cap(uid, max_items=500)
        logger.info(f"Successfully staged {len(staged_items)} items for user {uid} (session={session_id}, quarantined={is_quarantined})")

        return {
            "status": "success",
            "document_type": "checklist",
            "classifier_confidence": conf,
            "requires_confirmation": is_quarantined,
            "is_quarantined": is_quarantined,
            "import_session_id": session_id,
            "doc_hash": doc_hash,
            "storage_location": extraction_result.get("storage_location", ""),
            "snapshot_id": extraction_result.get("snapshot_id", ""),
            "extracted_count": len(staged_items),
            "data": staged_items,
        }

    # Step 4: Fallback to General / Invoice Scraper if classified as invoice
    return {
        "status": "classified_invoice",
        "document_type": "invoice",
        "classifier_confidence": conf,
        "import_session_id": session_id,
        "doc_hash": doc_hash,
        "message": "Document routed to invoice processing pipeline.",
    }


@router.post("/review/resume_session")
async def resume_session(request: ResumeSessionRequest):
    """
    Resumes an existing review session by retrieving already-staged documents.
    Performs ZERO re-extraction or AI calls.
    """
    try:
        docs = db.collection("users").document(request.uid)\
                 .collection("review_queue")\
                 .where("import_session_id", "==", request.import_session_id)\
                 .where("status", "in", ACTIVE_IMPORT_STATUSES)\
                 .stream()

        items = [d.to_dict() for d in docs]
        return {
            "status": "success",
            "import_session_id": request.import_session_id,
            "items_count": len(items),
            "data": items,
        }
    except Exception as e:
        logger.exception(f"Failed to resume session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review/abort_session")
async def abort_session(request: AbortSessionRequest):
    """
    Soft-deletes review queue items without physical document deletion.
    Sets status: 'aborted' or 'superseded' to preserve legal SoR auditability.
    """
    try:
        docs = list(
            db.collection("users").document(request.uid)
            .collection("review_queue")
            .where("import_session_id", "==", request.import_session_id)
            .stream()
        )

        batch = db.batch()
        for doc in docs:
            batch.set(doc.reference, {
                "status": request.target_status or "aborted",
                "aborted_at": firestore.SERVER_TIMESTAMP,
                "aborted_by": request.uid
            }, merge=True)

        batch.commit()
        return {
            "status": "success",
            "archived_count": len(docs),
            "target_status": request.target_status or "aborted"
        }
    except Exception as e:
        logger.exception(f"Failed to abort session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review/commit_session")
async def commit_session(request: CommitSessionRequest):
    """
    Atomically commits staged review items to canonical users/{uid}/coins collection
    and writes an immutable audit record to users/{uid}/audit_log/{log_id}.
    """
    try:
        staged_docs = list(
            db.collection("users").document(request.uid)
            .collection("review_queue")
            .where("import_session_id", "==", request.import_session_id)
            .where("status", "in", ACTIVE_IMPORT_STATUSES)
            .stream()
        )

        if not staged_docs:
            return {"status": "no_items", "message": "No active staged items found for session"}

        coins_col = db.collection("users").document(request.uid).collection("coins")
        audit_col = db.collection("users").document(request.uid).collection("audit_log")
        queue_col = db.collection("users").document(request.uid).collection("review_queue")

        batch = db.batch()
        committed_coin_ids = []

        for doc in staged_docs:
            data = doc.to_dict()
            coin_id = str(uuid.uuid4())
            committed_coin_ids.append(coin_id)

            # Apply any optional bulk overrides
            if request.condition_override:
                data["condition"] = request.condition_override
                data["Condition"] = request.condition_override
            if request.storage_location_override:
                data["storage_location"] = request.storage_location_override
                data["Storage Location"] = request.storage_location_override

            data["id"] = coin_id
            data["status"] = "committed"
            data["committed_at"] = firestore.SERVER_TIMESTAMP

            # Atomic write to canonical vault collection
            coin_ref = coins_col.document(coin_id)
            batch.set(coin_ref, data, merge=True)

            # Mark staged doc as committed (soft state transition)
            batch.set(doc.reference, {"status": "committed", "committed_coin_id": coin_id}, merge=True)

        # Write Canonical Audit Log Entry
        log_id = f"aud_{request.import_session_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        audit_entry = {
            "log_id": log_id,
            "uid": request.uid,
            "action": "session_commit",
            "import_session_id": request.import_session_id,
            "source": "review_hub",
            "timestamp": firestore.SERVER_TIMESTAMP,
            "before": {
                "staged_count": len(staged_docs),
                "condition": "Unspecified / Raw",
            },
            "after": {
                "committed_count": len(committed_coin_ids),
                "condition": request.condition_override or "Unspecified / Raw",
            },
            "affected_coin_ids": committed_coin_ids,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        audit_ref = audit_col.document(log_id)
        batch.set(audit_ref, audit_entry)

        batch.commit()
        logger.info(f"Committed {len(committed_coin_ids)} coins to vault for user {request.uid}")

        return {
            "status": "success",
            "committed_count": len(committed_coin_ids),
            "audit_log_id": log_id,
            "coin_ids": committed_coin_ids,
        }
    except Exception as e:
        logger.exception(f"Failed to commit session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review/bulk_condition")
async def bulk_condition(request: BulkConditionRequest):
    """
    Applies a bulk condition update across active staged items in a review session
    and logs an immutable record to users/{uid}/audit_log/{log_id}.
    """
    try:
        staged_docs = list(
            db.collection("users").document(request.uid)
            .collection("review_queue")
            .where("import_session_id", "==", request.import_session_id)
            .where("status", "in", ACTIVE_IMPORT_STATUSES)
            .stream()
        )

        if not staged_docs:
            return {"status": "no_items", "message": "No active staged items found for session"}

        batch = db.batch()
        updated_ids = []
        for doc in staged_docs:
            data = doc.to_dict()
            current_cond = data.get("condition") or data.get("Condition") or "Unspecified / Raw"
            if request.scope == "unspecified_only" and "Unspecified" not in current_cond:
                continue

            batch.set(doc.reference, {
                "condition": request.condition,
                "Condition": request.condition,
                "updated_at": firestore.SERVER_TIMESTAMP
            }, merge=True)
            updated_ids.append(doc.id)

        if updated_ids:
            # Write canonical audit log entry
            log_id = f"aud_{request.import_session_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            audit_entry = {
                "log_id": log_id,
                "uid": request.uid,
                "action": "bulk_condition_update",
                "import_session_id": request.import_session_id,
                "source": "review_hub",
                "timestamp": firestore.SERVER_TIMESTAMP,
                "before": {"condition": "Unspecified / Raw", "scope": request.scope},
                "after": {"condition": request.condition, "applied_to_count": len(updated_ids)},
                "affected_coin_ids": updated_ids,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            audit_ref = db.collection("users").document(request.uid).collection("audit_log").document(log_id)
            batch.set(audit_ref, audit_entry)

        batch.commit()
        return {
            "status": "success",
            "updated_count": len(updated_ids),
            "condition": request.condition,
            "affected_coin_ids": updated_ids,
        }
    except Exception as e:
        logger.exception(f"Failed to apply bulk condition: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Review Hub: Delete Items ─────────────────────────────────────────────────

class DeleteReviewItemsRequest(BaseModel):
    user_email: str = Field(..., description="Owner email — used as Firestore doc ID")
    review_ids: List[str] = Field(..., min_length=1, description="List of review_queue document IDs to delete")
    reason: str = Field(default="user_deleted", description="Reason code written to audit log")


@router.post("/review/delete_items")
async def delete_review_items(request: DeleteReviewItemsRequest):
    """
    Permanently delete one or more review_queue documents for a user.
    Each deletion is recorded in the users/{uid}/audit_log collection.
    Called by Review Hub Delete Selected and Delete Single buttons.
    """
    try:
        uid = request.user_email.lower().strip()
        user_ref = db.collection("users").document(uid)
        queue_col = user_ref.collection("review_queue")
        audit_col = user_ref.collection("audit_log")

        deleted_ids: List[str] = []
        batch = db.batch()

        for review_id in request.review_ids:
            doc_ref = queue_col.document(review_id)
            doc = doc_ref.get()
            if not doc.exists:
                logger.warning(f"delete_review_items: doc {review_id} not found for {uid}, skipping")
                continue

            # Capture data for audit before deleting
            data = doc.to_dict() or {}
            batch.delete(doc_ref)

            # Audit log entry
            log_id = f"DEL-{review_id[:8]}-{uuid.uuid4().hex[:6]}"
            audit_ref = audit_col.document(log_id)
            batch.set(audit_ref, {
                "log_id": log_id,
                "action": "review_queue_delete",
                "reason": request.reason,
                "review_id": review_id,
                "subject": data.get("theme_subject") or data.get("Theme/Subject") or data.get("title") or "unknown",
                "source_type": data.get("source_type", "unknown"),
                "deleted_by": uid,
                "deleted_at": datetime.now(timezone.utc).isoformat(),
            })
            deleted_ids.append(review_id)

        batch.commit()
        logger.info(f"delete_review_items: deleted {len(deleted_ids)} items for {uid} (reason={request.reason})")
        return {
            "status": "success",
            "deleted_count": len(deleted_ids),
            "deleted_ids": deleted_ids,
        }
    except Exception as e:
        logger.exception(f"Failed to delete review items: {e}")
        raise HTTPException(status_code=500, detail=str(e))
