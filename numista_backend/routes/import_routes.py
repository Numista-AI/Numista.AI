"""
Spreadsheet & Document Bulk Ingestion, Pre-Signed Uploads, and Deduplication Routes
"""

import uuid
import json
import io
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Form, File, UploadFile, Depends, Request
import pandas as pd
from google.cloud import storage as gcs

from schemas.import_schemas import SignedUrlRequest, ImportProcessRequest, ImportStartRequest, CommitBatchRequest
from services.common import GOLDEN_SCHEMA_MAPPING, normalize_colloquial_header, safe_get_str, normalize_slang_term
from routes.deps import db, storage_client, logger, get_current_user, PROJECT_ID

router = APIRouter(prefix="/api", tags=["Spreadsheet & Document Bulk Ingestion"])

BUCKET_NAME = "studio-9101802118-8c9a8-uploads"

# ── Helper Functions ─────────────────────────────────────────────────────────

def _read_spreadsheet_bytes(contents: bytes, filename: str) -> pd.DataFrame:
    """Reads raw uploaded bytes into pandas DataFrame based on file extension."""
    fn = filename.lower()
    if fn.endswith('.csv'):
        return pd.read_csv(io.BytesIO(contents))
    elif fn.endswith(('.xls', '.xlsx')):
        return pd.read_excel(io.BytesIO(contents))
    else:
        return pd.read_csv(io.BytesIO(contents))

def _normalize_us_denomination(denom: str) -> str:
    """Pre-deduplication US Mint denomination normalization (fails open for non-US coins)."""
    d = denom.strip().lower()
    if d in ["penny", "lincoln cent", "1c", "1¢", "wheatie", "cent"]:
        return "Cent"
    elif d in ["nickel", "jefferson nickel", "5c", "5¢", "five cents"]:
        return "Five Cents"
    elif d in ["dime", "roosevelt dime", "10c", "10¢"]:
        return "Dime"
    elif d in ["quarter", "washington quarter", "25c", "25¢", "quarter dollar"]:
        return "Quarter Dollar"
    elif d in ["half dollar", "half", "50c", "50¢", "jfk half"]:
        return "Half Dollar"
    elif d in ["dollar", "dollar coin", "morgan", "peace", "$1"]:
        return "Dollar"
    return denom.strip()  # Fail open for non-US world coins

# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/v1/import/get_upload_url")
async def get_upload_url(req: SignedUrlRequest, user: Dict[str, Any] = Depends(get_current_user)):
    """Generate 15-minute V4 pre-signed GCS upload URL for large files (>5MB)."""
    user_id = user.get("uid") or user.get("user_id") or "dev_guest_uid"
    blob_name = f"imports/{user_id}/{uuid.uuid4().hex}_{req.filename}"
    
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(blob_name)
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=15),
            method="PUT",
            content_type=req.content_type,
        )
        return {
            "status": "success",
            "signed_url": signed_url,
            "gcs_uri": f"gs://{BUCKET_NAME}/{blob_name}",
            "expires_in_minutes": 15
        }
    except Exception as e:
        logger.warning(f"Signed URL generation fallback: {e}")
        return {
            "status": "fallback",
            "gcs_uri": f"gs://{BUCKET_NAME}/{blob_name}",
            "signed_url": None
        }


@router.post("/import_spreadsheet")
async def import_spreadsheet(
    user_email: str = Form(...),
    file: Optional[UploadFile] = File(None),
    gcs_uri: Optional[str] = Form(None),
    import_name: str = Form(''),
    import_session_id: str = Form(''),
    user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Ingests an Excel/CSV file or GCS URI into users/{userId}/staging_area with intra-batch and 3-tier deduplication.
    """
    user_id = user.get("uid") or user.get("user_id") or "dev_guest_uid"
    session_id = import_session_id or f"imp_{uuid.uuid4().hex[:8]}"

    # 1. Obtain bytes from GCS or Direct Upload
    if gcs_uri and gcs_uri.startswith("gs://"):
        parts = gcs_uri.replace("gs://", "").split("/", 1)
        bucket = storage_client.bucket(parts[0])
        blob = bucket.blob(parts[1])
        contents = blob.download_as_bytes()
        filename = parts[1].split("/")[-1]
    elif file:
        contents = await file.read()
        filename = file.filename or "upload.csv"
    else:
        raise HTTPException(status_code=400, detail="Must provide direct file upload or gcs_uri")

    try:
        df = _read_spreadsheet_bytes(contents, filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {e}")

    headers = list(df.columns)
    mapping = {h: normalize_colloquial_header(h) for h in headers}

    # 2. Fetch existing user collection for 3-tier deduplication
    existing_certs = set()
    existing_combos = set()
    try:
        existing_docs = db.collection("users").document(user_id).collection("coins").get()
        for d in existing_docs:
            data = d.to_dict() or {}
            cert = data.get("cert_number") or data.get("Cert Number")
            if cert:
                existing_certs.add(str(cert).strip().lower())
            
            y = str(data.get("year") or data.get("Year") or "").strip()
            mm = str(data.get("mint_mark") or data.get("Mint Mark") or "").strip().upper()
            den = _normalize_us_denomination(str(data.get("denomination") or data.get("Denomination") or ""))
            if y and den:
                existing_combos.add(f"{y}_{mm}_{den.lower()}")
    except Exception as e:
        logger.warning(f"Deduplication index fetch warning: {e}")

    # 3. Process rows with intra-batch + 3-tier deduplication
    batch_certs = set()
    batch_combos = set()
    staged_items = []
    
    staging_ref = db.collection("users").document(user_id).collection("staging_area")
    batch = db.batch()
    count = 0

    for _, row in df.iterrows():
        raw_row = {}
        norm_coin = {}
        for orig_col, target_col in mapping.items():
            val = row[orig_col]
            if pd.notna(val):
                clean_val = str(val).strip()
                raw_row[orig_col] = clean_val
                norm_coin[target_col.lower()] = clean_val

        if not norm_coin:
            continue

        # Denomination Pre-Normalization
        raw_denom = norm_coin.get("denomination") or norm_coin.get("denom") or ""
        canon_denom = _normalize_us_denomination(raw_denom) if raw_denom else ""
        if canon_denom:
            norm_coin["denomination"] = canon_denom

        cert = str(norm_coin.get("cert_number") or norm_coin.get("cert") or "").strip().lower()
        year = str(norm_coin.get("year") or "").strip()
        mint = str(norm_coin.get("mint_mark") or norm_coin.get("mint") or "").strip().upper()

        # Deduplication matching
        dedup_flag = "new_item"
        matching_id = None

        if cert and cert in existing_certs:
            dedup_flag = "exact_duplicate"
        elif cert and cert in batch_certs:
            dedup_flag = "intra_batch_duplicate"
        else:
            combo_key = f"{year}_{mint}_{canon_denom.lower()}"
            if year and canon_denom and combo_key in existing_combos:
                dedup_flag = "potential_duplicate"
            elif year and canon_denom and combo_key in batch_combos:
                dedup_flag = "intra_batch_duplicate"

        if cert:
            batch_certs.add(cert)
        if year and canon_denom:
            batch_combos.add(f"{year}_{mint}_{canon_denom.lower()}")

        staging_id = str(uuid.uuid4())
        stage_doc = {
            "staging_id": staging_id,
            "user_id": user_id,
            "import_batch_id": session_id,
            "source_type": "spreadsheet",
            "source_file": import_name or filename,
            "raw_row_data": raw_row,
            "normalized_coin": norm_coin,
            "dedup_flag": dedup_flag,
            "matching_coin_id": matching_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        doc_ref = staging_ref.document(staging_id)
        batch.set(doc_ref, stage_doc)
        staged_items.append(stage_doc)
        count += 1

        if count % 400 == 0:
            batch.commit()
            batch = db.batch()

    if count % 400 != 0 and count > 0:
        batch.commit()

    return {
        "status": "success",
        "import_session_id": session_id,
        "rows_parsed": count,
        "new_items": sum(1 for i in staged_items if i["dedup_flag"] == "new_item"),
        "exact_duplicates": sum(1 for i in staged_items if i["dedup_flag"] == "exact_duplicate"),
        "potential_duplicates": sum(1 for i in staged_items if i["dedup_flag"] == "potential_duplicate"),
        "intra_batch_duplicates": sum(1 for i in staged_items if i["dedup_flag"] == "intra_batch_duplicate"),
    }


@router.post("/v1/import/commit_batch")
async def commit_batch(req: CommitBatchRequest, user: Dict[str, Any] = Depends(get_current_user)):
    """
    Executes non-blocking partial batch commits from staging to users/{userId}/coins.
    """
    user_id = user.get("uid") or user.get("user_id") or "dev_guest_uid"
    coins_ref = db.collection("users").document(user_id).collection("coins")
    staging_ref = db.collection("users").document(user_id).collection("staging_area")

    committed = 0
    skipped = 0
    conflicts = 0

    batch = db.batch()

    for sid in req.staging_ids:
        try:
            sdoc = staging_ref.document(sid).get()
            if not sdoc.exists:
                skipped += 1
                continue
            
            data = sdoc.to_dict() or {}
            coin_data = data.get("normalized_coin") or {}
            dedup = data.get("dedup_flag")

            if dedup == "exact_duplicate" and req.conflict_policy == "keep_existing":
                skipped += 1
                conflicts += 1
                continue

            coin_id = str(uuid.uuid4())
            coin_data["id"] = coin_id
            coin_data["imported_at"] = datetime.now(timezone.utc).isoformat()
            coin_data["import_session_id"] = req.import_session_id

            # Write to collection
            batch.set(coins_ref.document(coin_id), coin_data)
            # Delete from staging
            batch.delete(staging_ref.document(sid))
            committed += 1

            if committed % 400 == 0:
                batch.commit()
                batch = db.batch()
        except Exception as e:
            logger.warning(f"Error committing staging item {sid}: {e}")
            skipped += 1

    if committed % 400 != 0 and committed > 0:
        batch.commit()

    return {
        "status": "success",
        "import_session_id": req.import_session_id,
        "committed": committed,
        "skipped": skipped,
        "conflicts": conflicts
    }
