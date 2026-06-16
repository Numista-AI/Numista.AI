# numista_ai/

> **Status:** Reserved — not yet active.

This directory is reserved for a future dedicated AI model workspace for Numista.AI.

## Planned Purpose
- Custom fine-tuned model training data and configuration
- Vertex AI model evaluation pipelines
- Dataset management for coin identification training

## Current AI Integration
All current AI functionality lives in:
- **`numista_backend/main.py`** — Gemini Vision API calls (FastAPI endpoints)
- **`numista_backend/morgan_knowledge.py`** — RAG knowledge base for AI chat
- **`numista_backend/vertex_search/`** — Vertex AI Search (coin reference library)
