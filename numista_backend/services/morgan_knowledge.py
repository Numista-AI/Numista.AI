"""
Morgan AI Knowledge Base & RAG Index Module
Combines numismatic knowledge domain with the dynamic Feature Registry and
semantic Vector RAG reference retrieval (gemini-embedding-2).
"""

import logging
from typing import List, Dict, Any
from services.feature_registry import registry

logger = logging.getLogger("numista_backend.morgan_knowledge")


def get_morgan_system_knowledge_context(user_query: str = "") -> str:
    """
    Builds system prompt knowledge context for Morgan AI.
    Includes dynamic Feature Registry context, explicit rules preventing negative answers,
    and semantic vector RAG context from numismatic reference chunks.
    """
    prompt = (
        "CRITICAL INSTRUCTIONS & NEGATIVE ANSWER OVERRIDES:\n"
        "1. Lateral Transfers / Account-to-Account Transfers ARE FULLY SUPPORTED in Numista.AI via the 'Passport Protocol'.\n"
        "   NEVER state that users cannot transfer coins between accounts. ALWAYS explain how to use Lateral Transfer.\n"
        "2. If asked about transferring coins, moving coins to another login/account, or sharing items:\n"
        "   - Confirm that Lateral Transfer allows account-to-account property transfer with full legal provenance.\n"
        "   - Explain the 3 steps: 1) Initiate transfer in Lateral Transfer screen -> 2) Share 6-digit Claim PIN & Passport Certificate (or send via recipient email) -> 3) Recipient logs in and claims transfer.\n"
        "3. Provide helpful, precise, and enthusiastic assistance on numismatics, grading, market values, and Numista.AI capabilities.\n"
    )

    # Append dynamic features from FeatureRegistry
    try:
        feature_context = registry.build_morgan_prompt_context()
        if feature_context:
            prompt += f"\n{feature_context}\n"
    except Exception as fe:
        logger.warning(f"Feature registry context load error: {fe}")

    # Append semantic Vector RAG reference chunks if query text is provided
    if user_query and user_query.strip():
        try:
            from services.vector_rag_service import vector_rag_service
            rag_context = vector_rag_service.build_rag_prompt_context(user_query)
            if rag_context:
                prompt += f"\n{rag_context}\n"
        except Exception as ve:
            print(f"[rag] Vector RAG error: {ve}", flush=True)
            logger.warning(f"Vector RAG context retrieval error: {ve}")

    return prompt
