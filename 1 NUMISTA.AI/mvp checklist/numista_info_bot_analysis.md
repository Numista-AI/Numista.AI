# Numista.AI — Info Bot Architecture Analysis

> Scan completed: June 9, 2026 | Scope: Full workspace audit

---

## Executive Summary

**Yes — your current architecture strongly supports a RAG-based Info Bot**, and you already have most of the
raw ingredients in place. The project is not starting from zero; it is one focused module away from having
a working knowledge retrieval pipeline.

---

## 1. Does Your Architecture Support a RAG Info Bot?

### ✅ YES — Here's Why

#### You Already Have the Data Layer
Your `training_output/` folder is now a structured JSON knowledge base:

| File | Entries | Purpose |
|---|---|---|
| `washington_quarter_1993_1998.json` | 1 | Pre-program standard design |
| `50_state_quarters.json` | 56 | Full state/territory program |
| `generation_summary.json` | Large | Bulk training metadata |

Plus 25+ checklist PDF folders covering nearly every major US coin program
(Lincoln, Morgan, Peace, Eisenhower, Kennedy, Barber, Roosevelt, etc.).

#### You Already Have the AI Infrastructure
Your backend is already wired to Gemini via **Vertex AI** (`gemini-2.5-flash` in `app.py`)
and **google-genai SDK** in the scan service. A RAG bot would use this same pipeline —
no new AI accounts or credentials needed.

#### You Have a Local SQLite Coin Database
`numista_backend/database/numista_coins.db` (906 KB) — this is a pre-built structured
coin reference database. This is a **prime RAG source** right now, today.

#### You Have a `master_coin_programs.json` (515 KB)
This file in `numista_backend/` is a large, rich structured dataset covering all US Mint
programs. This alone could be the backbone of the Info Bot's knowledge.

#### The Architecture Has a Clear Slot for It
Your `ARCHITECTURE.md` explicitly reserves:
```
numista_ai  *(reserved)* -- Future dedicated AI model workspace
```
The Info Bot fits perfectly into this reserved module.

#### Your `AI Chat` Screen Already Exists (Flutter)
`AIChatScreen` (`ai_chat_screen.dart`) is a live, deployed screen for Gemini-powered Q&A.
The Info Bot could be a **second tab or mode** within this existing screen — or a
dedicated new screen — without touching any core collection logic.

---

## 2. Files You Must NOT Overwrite

### 🔴 CRITICAL — Core App Logic (Do Not Touch)

| File | Why It's Critical |
|---|---|
| [`numista_backend/app.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/app.py) | **193 KB, 3,882 lines** — the entire Streamlit admin app. One wrong edit here breaks the admin dashboard. |
| [`numista_backend/main.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py) | **161 KB** — second major backend file, contains PCGS proxy + data pipeline logic. |
| [`numista_backend/scan_service/main.py`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/scan_service/main.py) | Live Cloud Run endpoint. Overwriting this breaks the checklist scanner for all users. |
| [`numista_backend/firestore.rules`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/firestore.rules) | Security rules. Overwriting could expose user data. |
| [`numista_backend/storage.rules`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/storage.rules) | GCS security rules — same risk. |
| [`numista_backend/firebase.json`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/firebase.json) | Firebase hosting + rewrite config. Overwriting breaks production routing. |
| [`numista_backend/master_coin_programs.json`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/master_coin_programs.json) | **515 KB** structured program catalog — took months to build. Read-only for the bot. |
| [`numista_backend/database/numista_coins.db`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/database/numista_coins.db) | SQLite coin reference DB. Read-only for the bot — never write to this from Info Bot code. |
| [`numista_backend/.env`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/.env) | API keys and secrets. Never overwrite or commit. |
| [`numista_backend/serviceAccountKey.json.json`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/serviceAccountKey.json.json) | GCP service account key. Treat as a secret. |
| [`numista_backend/cloudbuild.yaml`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/cloudbuild.yaml) | CI/CD build pipeline. Changes here affect all Cloud Run deployments. |

### 🟡 CAUTION — Shared Infrastructure (Edit Carefully)

| File | Risk |
|---|---|
| [`numista_backend/requirements.txt`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/requirements.txt) | Adding RAG packages here is fine, but version conflicts can break Cloud Run deploys. Pin versions explicitly. |
| [`numista_backend/coin-schema.json`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/coin-schema.json) | Shared schema definition — append only, never remove fields. |

### 🟢 SAFE — Your Training Data (Own This Space)

| File/Folder | Status |
|---|---|
| `training_output/` (entire folder) | Safe — nothing in the live app reads from here yet. This is your Info Bot's source of truth. |
| `numista_ai/` (currently empty) | Safe — reserved for AI work, use freely. |

---

## 3. Safest Integration Strategy

### Recommended Approach: Isolated Module + Read-Only Data Access

```
training_output/                    ← Knowledge Base (JSON files, your new structured data)
    50_state_quarters.json
    washington_quarter_1993_1998.json
    [future coin program JSON files]
        |
        | read-only
        v
numista_ai/                         ← NEW: Info Bot Module (safe isolated folder)
    info_bot.py                     ← RAG logic: load JSON → chunk → embed → retrieve → answer
    knowledge_index.py              ← Vector index builder (runs once, or on new file added)
    bot_api.py                      ← Optional: Flask/FastAPI endpoint if you want it callable from Flutter
        |
        | Gemini API call (same credentials already in .env)
        v
    Gemini 2.5 Flash (already wired)
        |
        v
    Answer returned to user
```

### Phase 1 — Local Bot (Safe, No Risk to Production)
1. Create `numista_ai/info_bot.py`
2. Load `training_output/*.json` files at startup
3. Build a simple keyword or embedding search over the loaded data
4. Pass retrieved context + user question to Gemini via the existing Vertex AI credentials
5. Test entirely locally — zero changes to `numista_backend/`

### Phase 2 — Expose as an API Endpoint (Low Risk)
1. Add `bot_api.py` to `numista_ai/` — a small Flask endpoint: `POST /ask`
2. Deploy as a **new, separate Cloud Run service** (not touching the existing `scan-service`)
3. Flutter calls this new endpoint from `AIChatScreen` — or a new `InfoBotScreen`

### Phase 3 — Grow the Knowledge Base
Add new JSON files to `training_output/` using the schema we established:
- One file per coin series (e.g., `morgan_dollar.json`, `kennedy_half.json`)
- Use `master_coin_programs.json` and `numista_coins.db` as source data
- The bot re-indexes automatically when new files appear

---

## 4. RAG Packages to Add

When ready, add to `requirements.txt` (pin versions to avoid breaking existing deps):

```
# Info Bot / RAG
sentence-transformers==3.0.1    # Local embeddings (no API cost)
faiss-cpu==1.8.0                # Vector similarity search
langchain-core==0.2.0           # Optional: orchestration layer
```

> **Note:** `google-cloud-aiplatform` (already installed at `1.148.0`) also supports
> Vertex AI Vector Search, which is a cloud-native alternative to FAISS if you prefer
> to keep everything on GCP.

---

## 5. Key Insight: You Already Have a Head Start

Your `master_coin_programs.json` (515 KB) + `numista_coins.db` (906 KB) +
`training_output/` JSON files = **~1.5 MB of structured numismatic knowledge**
that doesn't exist in most general-purpose AI models.

That's exactly the retrieval corpus a RAG bot needs. The Info Bot's job is simply
to **surface the right piece of that data** in response to a user's question —
Gemini handles the natural language understanding and response formatting.

---

## Summary Table

| Question | Answer |
|---|---|
| Does current architecture support RAG Info Bot? | ✅ Yes — strongly |
| Key existing assets to leverage | `numista_coins.db`, `master_coin_programs.json`, `training_output/` JSON |
| Safest build location | `numista_ai/` (reserved, currently empty) |
| Risk to existing app? | Zero, if built in `numista_ai/` with read-only data access |
| Files never to touch | `app.py`, `main.py`, `scan_service/main.py`, `.env`, `firestore.rules`, `firebase.json` |
| Recommended first step | Build `numista_ai/info_bot.py` locally — no cloud changes needed yet |
