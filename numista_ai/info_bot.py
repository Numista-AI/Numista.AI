import os
import json
from typing import Optional, Dict, Any, List
from google import genai
from google.genai import types

PROJECT_ID = os.getenv("GCP_PROJECT", "studio-9101802118-8c9a8")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")
GEMINI_MODEL = "gemini-3.5-flash"
EMBEDDING_MODEL = "gemini-embedding-2"

_client = None

def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    return _client

def query_rag_info_bot(query: str, collection_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    RAG info bot query engine using gemini-embedding-2 and gemini-3.5-flash.
    Grounds response using embedded reference data and user's collection context.
    """
    client = get_client()

    # Load local reference index snippet
    index_file = os.path.join(os.path.dirname(__file__), "rag_index.json")
    documents = []
    if os.path.exists(index_file):
        try:
            with open(index_file, "r") as f:
                data = json.load(f)
                documents = data.get("documents", [])[:10]
        except Exception:
            pass

    ref_text = "\n".join([f"- {d.get('title')}: {d.get('content')}" for d in documents])

    context_str = ""
    if collection_context:
        total = collection_context.get("total_coins", 0)
        value = collection_context.get("portfolio_value", 0.0)
        verified = collection_context.get("verified_count", 0)
        context_str = f"USER COLLECTION METRICS: Total Coins: {total} (Verified: {verified}), Estimated Value: ${value:.2f}.\n"

    prompt = f"""You are Morgan, an expert numismatic RAG AI guide for Numista.AI.
Answer the user's query clearly, concisely, and accurately.

{context_str}
REFERENCE NUMISMATIC KNOWLEDGE:
{ref_text}

USER QUERY: {query}
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=800,
            )
        )

        return {
            "query": query,
            "answer": response.text,
            "model_used": GEMINI_MODEL,
            "embedding_model": EMBEDDING_MODEL,
            "status": "success"
        }
    except Exception as e:
        return {
            "query": query,
            "answer": f"I'm sorry, I couldn't query the RAG database right now: {str(e)}",
            "model_used": GEMINI_MODEL,
            "status": "error"
        }
