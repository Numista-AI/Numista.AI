"""
sandbox_routes.py
ITEM 8 — Numista.AI Beta Sprint

POST /api/sandbox/clear
Soft-archives all demo coins for the authenticated user by setting
is_demo_cleared: true on each Firestore document where is_demo == true.

NON-NEGOTIABLE CONSTRAINTS:
- NEVER hard-deletes documents (no .delete() calls).
- NEVER changes document IDs.
- NEVER sets is_demo to false (that would make them look like real coins).
- Only sets is_demo_cleared: true — clients hide these in UI via query filter.
- is_demo_cleared is a SERVER-SIDE field; never trust the client to set it.
"""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Depends, Request
from routes.deps import db, logger, get_current_user

router = APIRouter(prefix="/api/sandbox", tags=["Sandbox"])


@router.post("/clear")
async def sandbox_clear(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    ITEM 8: Soft-archive all sandbox demo coins for the authenticated user.
    Sets is_demo_cleared: true on every coin where is_demo == true.
    Does NOT delete any documents. Does NOT mutate is_demo.
    Returns a count of documents archived.
    """
    uid = current_user.get("uid")
    email = current_user.get("email", "").strip()

    if not email:
        raise HTTPException(status_code=401, detail="User email not present in token.")

    try:
        # Query for all demo coins belonging to this user.
        # is_demo is always set server-side during seeding — never from client.
        coins_ref = db.collection("users").document(email).collection("coins")
        demo_query = coins_ref.where("is_demo", "==", True)
        demo_docs = demo_query.stream()

        # Batch update: set is_demo_cleared = true on each document.
        # Firestore batch limit is 500 writes per batch.
        batch = db.batch()
        count = 0
        for doc in demo_docs:
            batch.update(doc.reference, {"is_demo_cleared": True})
            count += 1
            if count % 500 == 0:
                # Commit and start a new batch when approaching the 500-write limit.
                batch.commit()
                batch = db.batch()

        if count % 500 != 0 or count == 0:
            batch.commit()

        logger.info(
            f"sandbox_clear: archived {count} demo coins for uid={uid} email={email}"
        )
        return {"status": "success", "archived": count}

    except Exception as e:
        logger.error(f"sandbox_clear failed for uid={uid}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to clear demo coins. Please try again.",
        )
