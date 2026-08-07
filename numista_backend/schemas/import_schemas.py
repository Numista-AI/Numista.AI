"""
Spreadsheet & Document Import DTO Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ImportStartRequest(BaseModel):
    user_email: str
    file_id: str
    column_mapping: Optional[Dict[str, str]] = {}

class ImportProcessRequest(BaseModel):
    user_email: str
    session_id: str

class NormalizeBackfillRequest(BaseModel):
    user_email: str
