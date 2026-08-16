"""
Numismatic Semantic Vector RAG Service for MORGAN
Binds exclusively to gemini-embedding-2 on Vertex AI / Google GenAI SDK.
Provides semantic retrieval across official Red Book standards, PCGS Photograde,
and VAM variety reference chunks with fail-safe cold-start fallback.
"""

import os
import logging
import math
from typing import List, Dict, Any, Optional

from routes.deps import genai_client, db

logger = logging.getLogger("numista_backend.vector_rag_service")

# Active 2026 Embedding Model Binding
ACTIVE_EMBEDDING_MODEL = "gemini-embedding-2"
MAX_COSINE_DISTANCE_THRESHOLD = 0.45  # Distance > 0.45 rejected as low-relevance


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculates cosine similarity between two float vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)


class VectorRAGService:
    """
    Manages vector embedding generation and semantic similarity search
    over numismatic knowledge chunks.
    """

    def __init__(self, db_client=None, client=None):
        self.db = db_client or db
        self.client = client or genai_client
        self.model_id = ACTIVE_EMBEDDING_MODEL

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generates 768-dim float embedding using gemini-embedding-2.
        """
        if not self.client or not text or not text.strip():
            return None

        try:
            resp = self.client.models.embed_content(
                model=self.model_id,
                contents=text.strip(),
            )
            # Support both google-genai SDK response shapes
            if hasattr(resp, "embedding") and hasattr(resp.embedding, "values"):
                return list(resp.embedding.values)
            elif hasattr(resp, "embeddings") and len(resp.embeddings) > 0:
                return list(resp.embeddings[0].values)
            elif isinstance(resp, dict) and "embedding" in resp:
                return resp["embedding"].get("values", [])
            return None
        except Exception as e:
            logger.warning(f"Embedding generation error via {self.model_id}: {e}")
            return None

    def query_reference_chunks(
        self,
        query_text: str,
        limit: int = 3,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Queries indexed numismatic reference chunks.
        Performs in-memory / Firestore vector distance matching with fallback.
        """
        query_vector = self.generate_embedding(query_text)
        if not query_vector or not self.db:
            return []

        scored_results: List[Dict[str, Any]] = []

        try:
            chunks_ref = self.db.collection("numismatic_reference_chunks")
            if category:
                query = chunks_ref.where("category", "==", category).limit(50)
            else:
                query = chunks_ref.limit(50)

            docs = list(query.stream())
            for doc in docs:
                chunk_data = doc.to_dict() or {}
                chunk_vec = chunk_data.get("embedding_vector")
                if chunk_vec and isinstance(chunk_vec, list):
                    sim = cosine_similarity(query_vector, chunk_vec)
                    distance = 1.0 - sim
                    if distance <= MAX_COSINE_DISTANCE_THRESHOLD:
                        scored_results.append({
                            "chunk_id": doc.id,
                            "title": chunk_data.get("title", ""),
                            "source_document": chunk_data.get("source_document", "Official Numismatic Canon"),
                            "content_text": chunk_data.get("content_text", ""),
                            "similarity_score": round(sim, 4),
                            "distance": round(distance, 4),
                        })

            # Sort by highest similarity
            scored_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        except Exception as qe:
            logger.warning(f"Vector search retrieval error: {qe}")

        return scored_results[:limit]

    def build_rag_prompt_context(self, query_text: str, limit: int = 3) -> str:
        """
        Constructs verified RAG citation text block for MORGAN system prompt.
        """
        results = self.query_reference_chunks(query_text, limit=limit)
        if not results:
            return ""

        context_lines = [
            "### NUMISMATIC REFERENCE CITATIONS (Verified Domain RAG):",
        ]
        for res in results:
            title = res.get("title", "Reference Standard")
            source = res.get("source_document", "Numista Canon")
            content = res.get("content_text", "")
            context_lines.append(f"\n[Source: {source} - {title}]")
            context_lines.append(content)

        context_lines.append(
            "\nCite these references explicitly when addressing grading, mintage rarity, or variety attributions."
        )
        return "\n".join(context_lines)


# Global Singleton
vector_rag_service = VectorRAGService()
