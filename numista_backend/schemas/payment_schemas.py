"""
Stripe and Payment DTO Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional

class StripeCheckoutRequest(BaseModel):
    user_email: Optional[str] = None
    tier: str  # 'pro', 'numismatist', 'dealer', 'estate', or 'family_estate'
    interval: Optional[str] = "month"
    promo_code: Optional[str] = None
