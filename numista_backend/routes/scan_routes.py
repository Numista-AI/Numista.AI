"""
Vision AI, Binder Scan, Checklist Ingestion, and COA Parsing Routes
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from scan_service.coa_parser_service import parse_coa_document

router = APIRouter(prefix="/api", tags=["Vision AI & Binder Scans"])

@router.post("/v1/coa/parse")
async def api_parse_coa(file: UploadFile = File(...)):
    """Parse scanned US Mint COA card and extract serial numbers and specs."""
    content = await file.read()
    result = parse_coa_document(content, filename=file.filename or "coa_scan.jpg")
    return result
