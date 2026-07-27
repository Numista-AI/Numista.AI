"""
Numista.AI Family Sub-Account API Routes
Handles parent-managed sub-accounts, profile switching, and access permissions.
Tier limits: Pro = 5 sub-accounts max, Estate = Unlimited.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, Field
from typing import List, Optional
import time
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/family", tags=["family_subaccounts"])

class SubAccountCreateRequest(BaseModel):
    parent_email: str
    child_alias: str
    relationship: str  # e.g., "Daughter", "Son", "Heir", "Trustee"
    permission_level: str = Field(default="VIEW_ONLY", description="VIEW_ONLY, CONTRIBUTOR, FULL_ACCESS")
    bequest_percentage: float = Field(default=0.0, ge=0.0, le=100.0)

class SubAccountResponse(BaseModel):
    child_id: str
    parent_email: str
    child_alias: str
    relationship: str
    permission_level: str
    bequest_percentage: float
    created_at: float

# In-memory / Firestore fallback store for sub-accounts
SUB_ACCOUNT_DB = {}

@router.post("/subaccounts", response_model=SubAccountResponse)
def create_subaccount(req: SubAccountCreateRequest, user_tier: Optional[str] = Header(default="Pro")):
    """
    Create a new family sub-account under a parent master email.
    Enforces tier limits: Pro tier max 5 sub-accounts, Estate tier unlimited.
    """
    parent_accounts = [acc for acc in SUB_ACCOUNT_DB.values() if acc["parent_email"] == req.parent_email]
    
    # Enforce Pro tier limit (max 5)
    if user_tier.lower() == "pro" and len(parent_accounts) >= 5:
        raise HTTPException(
            status_code=403,
            detail="Pro tier is limited to 5 sub-accounts. Upgrade to Estate Tier for unlimited family sub-accounts."
        )

    child_id = f"sub_{int(time.time() * 1000)}"
    sub_account = {
        "child_id": child_id,
        "parent_email": req.parent_email,
        "child_alias": req.child_alias,
        "relationship": req.relationship,
        "permission_level": req.permission_level,
        "bequest_percentage": req.bequest_percentage,
        "created_at": time.time()
    }
    
    SUB_ACCOUNT_DB[child_id] = sub_account
    logger.info(f"Created sub-account '{req.child_alias}' ({child_id}) under parent '{req.parent_email}'")
    return SubAccountResponse(**sub_account)

@router.get("/subaccounts", response_model=List[SubAccountResponse])
def get_subaccounts(parent_email: str):
    """
    List all family sub-accounts for a parent email.
    """
    results = [acc for acc in SUB_ACCOUNT_DB.values() if acc["parent_email"] == parent_email]
    return [SubAccountResponse(**acc) for acc in results]

@router.delete("/subaccounts/{child_id}")
def delete_subaccount(child_id: str, parent_email: str):
    """
    Delete a sub-account by child_id.
    """
    if child_id not in SUB_ACCOUNT_DB:
        raise HTTPException(status_code=404, detail="Sub-account not found.")
    
    if SUB_ACCOUNT_DB[child_id]["parent_email"] != parent_email:
        raise HTTPException(status_code=403, detail="Unauthorized to delete this sub-account.")
        
    del SUB_ACCOUNT_DB[child_id]
    return {"status": "success", "message": f"Sub-account {child_id} deleted successfully."}
