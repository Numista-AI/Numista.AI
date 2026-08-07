"""
Stripe and Payment DTO Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional

class StripeCheckoutRequest(BaseModel):
    user_email: str
    tier: str  # 'pro' or 'estate'
