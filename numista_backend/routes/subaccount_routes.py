"""
Numista.AI Family Sub-Account API Routes
Handles parent-managed sub-accounts, profile switching, and access permissions.
Tier limits: Pro = 5 sub-accounts max, Estate/Sovereign/Power User = Unlimited.
Persists data to Firestore: /users/{parent_email}/subaccounts/{child_id}
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
import time
import logging
from google.cloud import firestore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/family", tags=["family_subaccounts"])

# Lazy-initialized Firestore client
_db = None

def get_db():
    global _db
    if _db is None:
        _db = firestore.Client(project="studio-9101802118-8c9a8")
    return _db

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


def _get_parent_tier(db: firestore.Client, parent_email: str) -> str:
    """Fetch the parent's actual subscription tier from Firestore."""
    doc = db.collection("users").document(parent_email).get()
    if not doc.exists:
        return "free"
    data = doc.to_dict() or {}
    tier = data.get("stripe_tier") or data.get("tier") or "free"
    return str(tier).lower().strip()


@router.post("/subaccounts", response_model=SubAccountResponse)
def create_subaccount(req: SubAccountCreateRequest):
    """
    Create a new family sub-account under a parent master email in Firestore.
    Enforces tier limits: Pro tier max 5 sub-accounts, Estate/Sovereign tier unlimited.
    """
    db = get_db()
    sub_col = db.collection("users").document(req.parent_email).collection("subaccounts")
    existing_docs = list(sub_col.stream())
    
    tier = _get_parent_tier(db, req.parent_email)
    
    # Enforce tier limits server-side (Pro max 5; Free max 0 or 1)
    if tier == "free" and len(existing_docs) >= 1:
        raise HTTPException(
            status_code=403,
            detail="Free tier allows 1 family sub-account. Upgrade to Pro or Estate Tier for additional sub-accounts."
        )
    elif tier == "pro" and len(existing_docs) >= 5:
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
    
    sub_col.document(child_id).set(sub_account)
    logger.info(f"Created sub-account '{req.child_alias}' ({child_id}) under parent '{req.parent_email}' in Firestore.")
    return SubAccountResponse(**sub_account)


@router.get("/subaccounts", response_model=List[SubAccountResponse])
def get_subaccounts(parent_email: str):
    """
    List all family sub-accounts for a parent email from Firestore.
    """
    db = get_db()
    sub_col = db.collection("users").document(parent_email).collection("subaccounts")
    docs = list(sub_col.stream())
    results = [d.to_dict() for d in docs if d.exists]
    return [SubAccountResponse(**acc) for acc in results]


@router.delete("/subaccounts/{child_id}")
def delete_subaccount(child_id: str, parent_email: str):
    """
    Delete a sub-account by child_id from Firestore.
    """
    db = get_db()
    doc_ref = db.collection("users").document(parent_email).collection("subaccounts").document(child_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Sub-account not found.")
        
    doc_ref.delete()
    logger.info(f"Deleted sub-account {child_id} for parent {parent_email}.")
    return {"status": "success", "message": f"Sub-account {child_id} deleted successfully."}
