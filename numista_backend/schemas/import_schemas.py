"""
Spreadsheet & Document Import DTO Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class SignedUrlRequest(BaseModel):
    filename: str
    content_type: str = "text/csv"

class ImportStartRequest(BaseModel):
    user_email: str
    file_id: str
    gcs_uri: Optional[str] = None
    column_mapping: Optional[Dict[str, str]] = {}

class ImportProcessRequest(BaseModel):
    user_email: str
    session_id: str

class CommitBatchRequest(BaseModel):
    import_session_id: str
    staging_ids: List[str]
    conflict_policy: str = "keep_existing"  # "keep_existing" | "overwrite" | "merge"

class StagingAreaItem(BaseModel):
    staging_id: str
    user_id: str
    import_batch_id: str
    source_type: str = "spreadsheet"
    source_file: str
    raw_row_data: Dict[str, Any] = {}
    normalized_coin: Dict[str, Any] = {}
    dedup_flag: str = "new_item"  # "exact_duplicate" | "potential_duplicate" | "new_item" | "intra_batch_duplicate"
    matching_coin_id: Optional[str] = None
    created_at: str
