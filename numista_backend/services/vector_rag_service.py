"""
Numismatic Semantic Vector RAG Service for MORGAN
Binds exclusively to gemini-embedding-2 on Vertex AI / Google GenAI SDK.
Provides semantic retrieval across official Red Book standards, PCGS Photograde,
and VAM variety reference chunks with fail-safe cold-start fallback.

Phase 4: Dual-path retrieval behind RAG_RETRIEVAL env flag.
  cosine_all  (default) — fetch all docs, in-memory cosine, no limit(50).
  find_nearest           — Firestore native KNN; requires 1536-dim Vector index READY.
"""

import os
import logging
import math
from typing import List, Dict, Any, Optional

import google.api_core.exceptions
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from google.genai import types as genai_types

from google import genai as _genai
from routes.deps import db

logger = logging.getLogger("numista_backend.vector_rag_service")

# Active 2026 Embedding Model Binding
ACTIVE_EMBEDDING_MODEL = "gemini-embedding-2"
RAG_EMBEDDING_DIM = 1536                        # Phase 4: MRL cut; Firestore cap is 2048
MAX_COSINE_DISTANCE_THRESHOLD = 0.45            # distance <= 0.45 (similarity >= 0.55); Phase 3 semantics unchanged
RAG_RETRIEVAL = os.environ.get("RAG_RETRIEVAL", "cosine_all")  # cosine_all | find_nearest
FIELDS_TO_EXCLUDE = {"embedding_vector", "cosine_distance"}    # never sent to Morgan's prompt

# gemini-embedding-2 requires location="global" on Vertex AI.
# The shared genai_client in deps.py uses location="us-central1" (correct for text generation)
# but that endpoint hangs on embed_content. Match the migrator exactly.
PROJECT_ID = "studio-9101802118-8c9a8"
try:
    _embed_client = _genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    print("[rag] Embedding client initialised (location=global)", flush=True)
except Exception as _e:
    print(f"[rag] Embedding client init FAILED: {_e}", flush=True)
    _embed_client = None


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculates cosine similarity between two equal-length float vectors."""
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
        self.client = client or _embed_client   # location="global" — required for gemini-embedding-2
        self.model_id = ACTIVE_EMBEDDING_MODEL

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generates 1536-dim float embedding using gemini-embedding-2 with MRL output_dimensionality.
        """
        if not self.client or not text or not text.strip():
            print("[rag] generate_embedding: no client or empty text", flush=True)
            return None

        try:
            resp = self.client.models.embed_content(
                model=self.model_id,
                contents=text.strip(),
                config=genai_types.EmbedContentConfig(output_dimensionality=RAG_EMBEDDING_DIM),
            )
            # Support both google-genai SDK response shapes
            if hasattr(resp, "embedding") and hasattr(resp.embedding, "values"):
                vec = list(resp.embedding.values)
            elif hasattr(resp, "embeddings") and len(resp.embeddings) > 0:
                vec = list(resp.embeddings[0].values)
            elif isinstance(resp, dict) and "embedding" in resp:
                vec = resp["embedding"].get("values", [])
            else:
                print("[rag] generate_embedding: unrecognised response shape", flush=True)
                return None
            print(f"[rag] generate_embedding: OK dim={len(vec)}", flush=True)
            return vec
        except Exception as e:
            print(f"[rag] generate_embedding ERROR: {e}", flush=True)
            logger.warning(f"Embedding generation error via {self.model_id}: {e}")
            return None

    def _cosine_all(self, query_vector: List[float], limit: int) -> List[Dict[str, Any]]:
        """
        Phase 4a default path: fetch all docs, in-memory cosine. No limit(50).
        Skips any doc whose embedding length != query length (SKIP_DIM).
        """
        docs = list(self.db.collection("numismatic_reference_chunks").stream())
        scored = []
        for doc in docs:
            data = doc.to_dict() or {}
            vec = data.get("embedding_vector", [])
            if isinstance(vec, Vector):
                vec = list(vec)
            if not vec:
                continue
            if len(vec) != len(query_vector):
                print(f"[rag] SKIP_DIM {doc.id}: vec={len(vec)}, query={len(query_vector)}", flush=True)
                continue
            sim = cosine_similarity(query_vector, vec)
            distance = 1.0 - sim
            if distance <= MAX_COSINE_DISTANCE_THRESHOLD:
                scored.append({
                    "chunk_id": doc.id,
                    "distance": round(distance, 4),
                    "similarity_score": round(sim, 4),
                    **{k: v for k, v in data.items() if k not in FIELDS_TO_EXCLUDE},
                })
        scored.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored[:limit]

    def _find_nearest(self, query_vector: List[float], limit: int) -> List[Dict[str, Any]]:
        """
        Phase 4b KNN path: Firestore native find_nearest.
        Requires index READY + all docs as Vector(1536).
        Falls back to cosine_all on any transient GCP error.
        """
        try:
            results = (
                self.db.collection("numismatic_reference_chunks")
                .find_nearest(
                    vector_field="embedding_vector",
                    query_vector=Vector(query_vector),
                    distance_measure=DistanceMeasure.COSINE,
                    limit=limit,
                    distance_result_field="cosine_distance",
                )
                .stream()
            )
            chunks = []
            for doc in results:
                data = doc.to_dict() or {}
                distance = data.get("cosine_distance", None)
                if distance is None:
                    # cosine_distance missing from snapshot — compute client-side
                    vec = data.get("embedding_vector", [])
                    if isinstance(vec, Vector):
                        vec = list(vec)
                    if vec and len(vec) == len(query_vector):
                        print(f"[rag] cosine_distance missing for {doc.id}; computing client-side", flush=True)
                        distance = 1.0 - cosine_similarity(query_vector, vec)
                    else:
                        print(
                            f"[rag] SKIP_DIM (fallback) {doc.id}: "
                            f"vec={len(vec) if vec else 0}, query={len(query_vector)}",
                            flush=True,
                        )
                        continue
                if distance <= MAX_COSINE_DISTANCE_THRESHOLD:
                    chunks.append({
                        "chunk_id": doc.id,
                        "distance": round(distance, 4),
                        "similarity_score": round(1.0 - distance, 4),
                        **{k: v for k, v in data.items() if k not in FIELDS_TO_EXCLUDE},
                    })
            return chunks   # already ordered by distance (server-side)
        except google.api_core.exceptions.GoogleAPIError as e:
            logger.warning(f"find_nearest failed ({e}); falling back to cosine_all")
            return self._cosine_all(query_vector, limit)

    def query_reference_chunks(
        self,
        query_text: str,
        limit: int = 3,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Queries indexed numismatic reference chunks.
        Routes to cosine_all or find_nearest based on RAG_RETRIEVAL env flag.
        """
        query_vector = self.generate_embedding(query_text)
        if not query_vector or not self.db:
            return []

        if RAG_RETRIEVAL == "find_nearest":
            results = self._find_nearest(query_vector, limit)
        else:
            results = self._cosine_all(query_vector, limit)

        # Retrieval log — chunk_id + distance + similarity_score visible in Cloud Run logs
        hit_summary = ", ".join(
            f"{r['chunk_id']}:d={r['distance']}:s={r['similarity_score']}"
            for r in results
        )
        logger.info(f"[rag] retrieval={RAG_RETRIEVAL} hits={len(results)} [{hit_summary}]")
        print(f"[rag] retrieval={RAG_RETRIEVAL} hits={len(results)} [{hit_summary}]", flush=True)

        return results

    def build_rag_prompt_context(self, query_text: str, limit: int = 3) -> str:
        """
        Constructs verified RAG citation text block for MORGAN system prompt.
        """
        print(f"[rag] build_rag_prompt_context called, query len={len(query_text)}", flush=True)
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
