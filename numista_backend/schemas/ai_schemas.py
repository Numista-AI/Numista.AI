"""
AI Deep Dive and RAG Query Schemas
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class RagQueryRequest(BaseModel):
    query: str
    user_email: Optional[str] = ""
    history: Optional[List[Dict[str, Any]]] = []

class DeepDiveRequest(BaseModel):
    query: str
    coin_data: Optional[Dict[str, Any]] = {}
    user_email: Optional[str] = ""
