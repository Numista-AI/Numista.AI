"""
Numismatic AI RAG, Deep Dive Essays, Morgan Chat Session Persistence,
Episodic Collector Memory, and Vector Domain Knowledge Routes
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field

from config import DEFAULT_CHAT_MODEL, FALLBACK_CHAT_MODEL
from routes.deps import genai_client, genai_types, db, get_current_user
from services.collector_profile_service import collector_profile_service

logger = logging.getLogger("numista_backend.ai_routes")

router = APIRouter(prefix="/api/ai", tags=["Numismatic AI Chat & Deep Dives"])

# ── Schemas ───────────────────────────────────────────────────────────────────

class ChatTurnRequest(BaseModel):
    session_id: Optional[str] = None
    message_id: Optional[str] = None
    query: str
    context_override: Optional[str] = None

class EssayRequest(BaseModel):
    topic: str
    denomination: Optional[str] = None
    year: Optional[int] = None

class CollectorProfileUpdateRequest(BaseModel):
    preferred_series: Optional[List[str]] = None
    target_grade_min: Optional[str] = None
    target_grade_max: Optional[str] = None
    preferred_services: Optional[List[str]] = None
    investment_goal: Optional[str] = None
    budget_tier: Optional[str] = None
    opt_in_chat_extraction: Optional[bool] = None

# ── Helper for Vision/Text Model Invocation with Resilient Fallback ───────────

def call_chat_model_with_fallback(system_prompt: str, user_query: str) -> str:
    """Invokes Gemini 3.6 Flash with automatic fallback to Gemini 3.5 Flash."""
    if not genai_client:
        return "I am currently unable to connect to Vertex AI services. Please try again shortly."

    models_to_try = [DEFAULT_CHAT_MODEL, FALLBACK_CHAT_MODEL]
    last_err = None

    for model_id in models_to_try:
        try:
            logger.info(f"Invoking chat model: {model_id}")
            resp = genai_client.models.generate_content(
                model=model_id,
                contents=[
                    genai_types.Part.from_text(text=f"{system_prompt}\n\nUser Question: {user_query}")
                ],
                config=genai_types.GenerateContentConfig(
                    temperature=0.3,
                ),
            )
            return resp.text.strip()
        except Exception as e:
            logger.warning(f"Chat model {model_id} failed: {e}")
            last_err = e

    raise HTTPException(status_code=500, detail=f"Morgan AI completion failed: {last_err}")


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/chat")
async def api_ai_chat(req: ChatTurnRequest, user: Dict[str, Any] = Depends(get_current_user)):
    """
    Morgan AI Chat completion endpoint with portfolio memory context,
    episodic collector preferences, vector RAG knowledge, & Firestore session persistence.
    """
    user_id = user.get("uid") or user.get("user_id") or "dev_guest_uid"
    user_name = user.get("name") or user.get("email") or "Collector"
    session_id = req.session_id or f"session_{int(datetime.now(timezone.utc).timestamp())}"
    msg_id = req.message_id or f"msg_{int(datetime.now(timezone.utc).timestamp())}"

    # 1. Base persona
    system_prompt = f"You are Morgan, an expert AI numismatic assistant for {user_name} on Numista.AI.\n"

    # 2. Inject Episodic Collector Memory
    try:
        profile_context = collector_profile_service.build_profile_prompt_context(user_id)
        if profile_context:
            system_prompt += profile_context + "\n"
    except Exception as pe:
        logger.warning(f"Failed to load collector profile context: {pe}")

    # 3. Inject Knowledge Base, Vector RAG, & Dynamic Feature Registry context
    try:
        from services.morgan_knowledge import get_morgan_system_knowledge_context
        system_prompt += get_morgan_system_knowledge_context(req.query) + "\n"
    except Exception as ke:
        logger.warning(f"Failed to load Morgan system knowledge context: {ke}")

    # 4. Inject Portfolio Summary Stats (<15ms latency)
    try:
        stats_doc = db.collection("users").document(user_id).collection("summary").document("stats").get()
        if stats_doc.exists:
            stats = stats_doc.to_dict() or {}
            system_prompt += (
                f"Portfolio Summary:\n"
                f"- Total Coins: {stats.get('total_coins', 0)}\n"
                f"- Portfolio Market Value: ${stats.get('portfolio_value', 0.0):,.2f}\n"
                f"- Unrealized P/L: ${stats.get('profit', 0.0):,.2f}\n"
                f"- Certified Slabs: {stats.get('grade_count', 0)}\n"
            )
    except Exception as e:
        logger.warning(f"Failed to fetch portfolio summary stats for context: {e}")

    if req.context_override:
        system_prompt += f"\nAdditional Context: {req.context_override}"

    # 5. Invoke Gemini AI completion with fallback
    assistant_reply = call_chat_model_with_fallback(system_prompt, req.query)

    # 6. Persist messages to Firestore: users/{userId}/ai_chat_sessions/{sessionId}/messages/{messageId}
    try:
        session_ref = db.collection("users").document(user_id).collection("ai_chat_sessions").document(session_id)
        
        # Ensure session parent doc exists
        session_ref.set({
            "session_id": session_id,
            "title": req.query[:40] if req.query else "New Conversation",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "is_deleted": False
        }, merge=True)

        messages_ref = session_ref.collection("messages")
        
        # Save user message
        messages_ref.document(f"{msg_id}_user").set({
            "message_id": f"{msg_id}_user",
            "role": "user",
            "content": req.query,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        # Save assistant message
        messages_ref.document(f"{msg_id}_assistant").set({
            "message_id": f"{msg_id}_assistant",
            "role": "assistant",
            "content": assistant_reply,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as se:
        logger.warning(f"Firestore session persistence error: {se}")

    return {
        "session_id": session_id,
        "message_id": f"{msg_id}_assistant",
        "reply": assistant_reply,
        "status": "success"
    }


# ── Collector Profile Endpoints ───────────────────────────────────────────────

@router.get("/profile")
async def api_get_collector_profile(user: Dict[str, Any] = Depends(get_current_user)):
    """Retrieve episodic collector preferences for current authenticated user."""
    user_id = user.get("uid") or user.get("user_id") or "dev_guest_uid"
    profile = collector_profile_service.get_collector_profile(user_id)
    return {"status": "success", "profile": profile}


@router.post("/profile")
@router.put("/profile")
async def api_update_collector_profile(
    req: CollectorProfileUpdateRequest,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Update collector preferences with strict snake_case validation."""
    user_id = user.get("uid") or user.get("user_id") or "dev_guest_uid"
    updates = req.model_dump(exclude_unset=True)
    res = collector_profile_service.update_collector_profile(user_id, updates)
    if res.get("status") == "error":
        raise HTTPException(status_code=400, detail=res.get("message", "Profile update failed"))
    return res


# ── Session & Research Endpoints ──────────────────────────────────────────────

@router.get("/sessions")
async def api_list_sessions(user: Dict[str, Any] = Depends(get_current_user)):
    """List active Morgan AI chat sessions for current user."""
    user_id = user.get("uid") or user.get("user_id") or "dev_guest_uid"
    sessions = []
    try:
        query = db.collection("users").document(user_id).collection("ai_chat_sessions").where("is_deleted", "!=", True).get()
        for doc in query:
            sessions.append(doc.to_dict())
    except Exception as e:
        logger.warning(f"Failed to query AI chat sessions: {e}")

    return {"sessions": sessions}


@router.get("/sessions/{session_id}")
async def api_get_session_messages(session_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    """Get full message history for a specific chat session (capped at last 50 turns)."""
    user_id = user.get("uid") or user.get("user_id") or "dev_guest_uid"
    messages = []
    try:
        msgs = db.collection("users").document(user_id).collection("ai_chat_sessions").document(session_id).collection("messages").order_by("timestamp").limit(50).get()
        for doc in msgs:
            messages.append(doc.to_dict())
    except Exception as e:
        logger.warning(f"Failed to query messages for session {session_id}: {e}")

    return {"session_id": session_id, "messages": messages}


@router.delete("/sessions/{session_id}")
async def api_delete_session(session_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    """Soft-delete a Morgan AI chat session."""
    user_id = user.get("uid") or user.get("user_id") or "dev_guest_uid"
    try:
        db.collection("users").document(user_id).collection("ai_chat_sessions").document(session_id).set({
            "is_deleted": True,
            "deleted_at": datetime.now(timezone.utc).isoformat()
        }, merge=True)
        return {"status": "success", "session_id": session_id, "message": "Session soft-deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {e}")


@router.post("/essay")
async def api_generate_essay(req: EssayRequest, user: Dict[str, Any] = Depends(get_current_user)):
    """Generate in-depth numismatic research essay or heritage summary."""
    prompt = f"Write a detailed, high-level numismatic research essay on: {req.topic}."
    if req.denomination or req.year:
        prompt += f" Focus on {req.year or ''} {req.denomination or ''} series history, mintage figures, and key varieties."

    essay_text = call_chat_model_with_fallback(
        "You are Morgan, senior numismatic researcher for Numista.AI.",
        prompt
    )
    return {"topic": req.topic, "essay": essay_text}
