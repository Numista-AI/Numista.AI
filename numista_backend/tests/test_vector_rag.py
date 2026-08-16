"""
Unit tests for Numismatic Vector RAG Service (gemini-embedding-2 binding & fallback)
"""

import pytest
from services.vector_rag_service import VectorRAGService, cosine_similarity, ACTIVE_EMBEDDING_MODEL


class DummyEmbeddingModel:
    def embed_content(self, model, contents):
        class Resp:
            def __init__(self, values):
                self.embedding = type("Emb", (), {"values": values})()
        # Mock deterministic embedding response
        if "1893-S" in contents:
            return Resp([1.0, 0.0, 0.0])
        return Resp([0.0, 1.0, 0.0])


class DummyGenAIClient:
    def __init__(self):
        self.models = DummyEmbeddingModel()


class DummyChunkDoc:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data
    def to_dict(self):
        return self._data


class DummyChunkCollection:
    def __init__(self, docs):
        self.docs = docs
    def limit(self, n):
        return self
    def where(self, *args, **kwargs):
        return self
    def stream(self):
        return self.docs


class DummyRAGFirestore:
    def __init__(self, docs):
        self.docs = docs
    def collection(self, name):
        return DummyChunkCollection(self.docs)


def test_vector_model_binding_constant():
    assert ACTIVE_EMBEDDING_MODEL == "gemini-embedding-2"


def test_cosine_similarity():
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    vec3 = [0.0, 1.0, 0.0]
    assert pytest.approx(cosine_similarity(vec1, vec2), 0.001) == 1.0
    assert pytest.approx(cosine_similarity(vec1, vec3), 0.001) == 0.0


def test_vector_rag_query_and_prompt_formatting():
    mock_docs = [
        DummyChunkDoc("c1", {
            "title": "1893-S Key Date Rarity",
            "source_document": "PCGS Photograde",
            "content_text": "Mintage of 100,000 coins only.",
            "embedding_vector": [1.0, 0.0, 0.0]
        }),
        DummyChunkDoc("c2", {
            "title": "Lincoln Memorial Cents",
            "source_document": "Red Book 2026",
            "content_text": "Common circulation series.",
            "embedding_vector": [0.0, 1.0, 0.0]
        })
    ]

    service = VectorRAGService(
        db_client=DummyRAGFirestore(mock_docs),
        client=DummyGenAIClient()
    )

    results = service.query_reference_chunks("Tell me about 1893-S Morgan", limit=2)
    assert len(results) >= 1
    assert results[0]["title"] == "1893-S Key Date Rarity"
    assert results[0]["similarity_score"] == 1.0

    prompt_context = service.build_rag_prompt_context("1893-S Morgan")
    assert "[Source: PCGS Photograde - 1893-S Key Date Rarity]" in prompt_context
    assert "Mintage of 100,000 coins only." in prompt_context
