"""
Collection, Set Review, and Dedup DTO Schemas
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class BulkUpdateRequest(BaseModel):
    user_email: str
    review_ids: List[str]
    updates: Dict[str, Any]

class ReviewCommitRequest(BaseModel):
    user_email: str
    items: List[Dict[str, Any]]

class SetActionRequest(BaseModel):
    user_email: str
    set_name: str
    items: List[Dict[str, Any]]
