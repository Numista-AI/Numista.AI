"""
Spreadsheet & Document Ingestion and Column Mapping Routes
"""

import uuid
import json
import io
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Form, File, UploadFile
import pandas as pd
from schemas.import_schemas import ImportProcessRequest, ImportStartRequest
from services.common import GOLDEN_SCHEMA_MAPPING, normalize_colloquial_header, safe_get_str, normalize_slang_term
from routes.deps import db, logger

router = APIRouter(prefix="/api", tags=["Spreadsheet & Document Bulk Ingestion"])

def _read_spreadsheet_bytes(contents: bytes, filename: str) -> pd.DataFrame:
    """Reads raw uploaded bytes into pandas DataFrame based on file extension."""
    fn = filename.lower()
    if fn.endswith('.csv'):
        return pd.read_csv(io.BytesIO(contents))
    elif fn.endswith(('.xls', '.xlsx')):
        return pd.read_excel(io.BytesIO(contents))
    else:
        # Fallback to CSV
        return pd.read_csv(io.BytesIO(contents))

def _fast_map_spreadsheet_headers(headers: List[str], is_currency: bool = False) -> Dict[str, str]:
    """Map headers to Golden Schema column names."""
    mapping = {}
    for h in headers:
        normalized = normalize_colloquial_header(h)
        mapping[h] = normalized
    return mapping

@router.post("/import_spreadsheet")
async def import_spreadsheet(
    user_email:        str = Form(...),
    file:              UploadFile = File(...),
    import_name:       str = Form(''),
    import_session_id: str = Form(''),
    item_type:         str = Form(None),
):
    """
    Ingests an Excel/CSV file into the user's review_queue.
    """
    contents = await file.read()
    try:
        df = _read_spreadsheet_bytes(contents, str(file.filename))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")

    fname = str(file.filename).lower()
    is_currency = False
    if item_type == "paper_currency" or "currency" in fname or "banknote" in fname or "bill" in fname:
        is_currency = True

    headers = list(df.columns)
    mapping = _fast_map_spreadsheet_headers(headers, is_currency)

    col_ref = db.collection("users").document(user_email).collection("review_queue")
    batch = db.batch()
    count = 0
    added_coin_ids = []

    for _, row in df.iterrows():
        doc = {}
        for orig_col, target_col in mapping.items():
            val = row[orig_col]
            if pd.notna(val):
                clean_val = str(val).strip()
                doc[target_col] = clean_val
                slang_info = normalize_slang_term(clean_val)
                if slang_info:
                    if "series" in slang_info and "Series" not in doc:
                        doc["Series"] = slang_info["series"]
                    if "denomination" in slang_info and "Denomination" not in doc:
                        doc["Denomination"] = slang_info["denomination"]
                    if "mapped_grade" in slang_info and "Grade" not in doc:
                        doc["Grade"] = slang_info["mapped_grade"]
                    if "mapped_mint_mark" in slang_info and "Mint Mark" not in doc:
                        doc["Mint Mark"] = slang_info["mapped_mint_mark"]

        if not doc:
            continue

        doc["import_session_id"] = import_session_id or f"imp_{uuid.uuid4().hex[:8]}"
        doc["import_name"] = import_name or file.filename
        doc["status"] = "pending_review"

        doc_ref = col_ref.document(str(uuid.uuid4()))
        batch.set(doc_ref, doc)
        added_coin_ids.append(doc_ref.id)
        count += 1

        if count % 490 == 0:
            batch.commit()
            batch = db.batch()

    if count % 490 != 0:
        batch.commit()

    return {
        "status": "ok",
        "imported_count": count,
        "import_session_id": import_session_id or f"imp_{uuid.uuid4().hex[:8]}",
        "added_ids": added_coin_ids,
    }
