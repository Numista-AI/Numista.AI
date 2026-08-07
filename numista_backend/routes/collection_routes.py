"""
User Coin Collection, Review Queue, Bulk Updates, and Dedup Routes
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Coin Collection & Review Queue Management"])
