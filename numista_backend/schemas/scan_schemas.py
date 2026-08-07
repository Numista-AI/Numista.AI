"""
Vision, Binder, Checklist, and COA Scan DTO Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class BinderScanRequest(BaseModel):
    user_email: str
    image_b64: str
    binder_name: Optional[str] = "Default Binder"

class BinderConfirmRequest(BaseModel):
    user_email: str
    binder_id: str
    items: List[Dict[str, Any]]

class ChecklistScanRequest(BaseModel):
    user_email: str
    image_b64: str
    series_context: Optional[str] = ""

class CoaParseRequest(BaseModel):
    user_email: str
    filename: Optional[str] = "coa_scan.jpg"
