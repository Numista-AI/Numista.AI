"""
Affiliate & Shareable Public Wishlist DTO Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ShareWishlistRequest(BaseModel):
    items: List[Dict[str, Any]]
    collector_display_name: Optional[str] = "Collector"

class ReserveItemRequest(BaseModel):
    token: str
    coin_id: str
    reserved_by: str

class UnreserveItemRequest(BaseModel):
    token: str
    coin_id: str

class SearchUrlRequest(BaseModel):
    token: str
    title: str
    estimated_value: float = 0.0
    item_type: str = "coin"  # "coin" | "currency"
