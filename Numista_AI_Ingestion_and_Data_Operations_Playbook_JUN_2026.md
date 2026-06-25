# Numista.AI — Ingestion & Data Operations Playbook
> **Version:** June 2026 | **Author:** Numista Operations Team | **Status:** Reference Document for Standalone AI Advisor

This operations playbook details the data ingestion, validation, and database synchronization pipelines within the Numista.AI ecosystem. It is intended for upload into standalone AI advisors to align their understanding of how data flows through the application's backend.

---

## 1. Spreadsheet Ingestion & Normalization

The ingestion engine in `numista_backend/main.py` normalizes custom user spreadsheets (CSV and Excel format) into the Golden Schema before saving to Firestore.

### 1.1 Column Header Normalization Rules
Spreadsheet headers are parsed case-insensitively and mapped to canonical fields:

| Colloquial Input Header | Canonical Database Field | Data Type |
|-------------------------|--------------------------|-----------|
| `Price Paid`, `Cost/Price`, `Purchase Cost`, `Cost` | `Cost` | String (formatted e.g. `"$12.50"`) |
| `My Notes`, `Notes`, `Personal Notes I` | `Personal Notes` | String |
| `Grading Cert #`, `Certification #` | `Certification Number` | String |
| `Personal Ref #`, `Ref #` | `Personal Reference #` | String |

### 1.2 KeyError Prevention
All row parsers in the backend utilize safe `.get()` calls (e.g. `row.get("Cost", "$0.00")`) instead of direct dictionary lookups (`row["Cost"]`). This allows the system to process files containing missing or incomplete columns without throwing runtime exceptions.

---

## 2. Ingestion Routing & Set Lifecycles

When an invoice or document PDF is processed via `POST /api/process_invoice`, the backend leverages Gemini Vision to classify all listed items:

```
                          [Processed PDF Invoice]
                                     │
                                     ▼
                        [Gemini Item Classifier]
                                     │
         ┌───────────┬───────────────┼─────────────┬───────────┐
         ▼           ▼               ▼             ▼           ▼
      [coin]       [set]     [paper_currency]   [medal]    [supply]
         │           │               │             │           │
         ▼           ▼               ▼             ▼           ▼
   [review_queue] [staging]    [review_queue] [review_queue] [supplies_log]
                     │         (w/ 📜 Badge)  (w/ 🎖️ Badge)
         ┌───────────┴───────────┐
         ▼                       ▼
  ["Break Up Set"]        ["Keep as Set"]
         │                       │
         ▼                       ▼
    [Splits to N            [Committed as
   Individual Coins]       Single Set Record]
```

### 2.1 Item Type Routing Definitions
- **`coin`**: Renders inside the standard Review Queue.
- **`set`**: Staged as a unified Set Record. Users can click "Break Up Set" (creating individual coins linked via a shared `set_id`) or "Keep as Set" (committing a single cataloged set document).
- **`paper_currency`**: Routed to the Review Queue flagged with a banknote icon badge.
- **`medal`**: Routed to the Review Queue flagged with a medallion icon badge.
- **`stamp`**: Sent to `pending_items` (reserved for a future stamps workspace).
- **`supply`**: Directly parsed and committed to the `supplies_log` subcollection (rendered inside the app's Inventory panel).

### 2.2 Presidential Coin Name Standardization
Ingestion validation routines compare incoming Presidential $1 coin titles against official US Mint nomenclature, standardizing name strings before saving (e.g. "Grant" or "Ulysses Grant" $\rightarrow$ "Ulysses S. Grant").

---

## 3. RAG Chat & Session Persistence

The AI Chat interface integrates Vertex AI Search and a local context script (`morgan_knowledge.py`).

- **Persistence Storage**: Chat histories are stored under `users/{user_email}/ai_chat_sessions/{session_id}`.
- **Auto-Restoration**: When the user opens the chat panel, the client polls this endpoint to list and reconstruct active sessions. Clicking "New Chat" clears the local state and allocates a new session ID in Firestore.

---

## 4. Heir Division Engine

The Division Engine performs lot allocation calculations using a greedy **Longest Processing Time (LPT)** partitioning algorithm:

1. Coins are sorted in descending order based on their value (combining premium value and live silver melt value).
2. The engine iterates through the coins, assigning the most valuable available coin to the beneficiary who currently has the lowest total allocated lot value.
3. If cash offsets are requested, the engine computes cash payments required from beneficiaries with higher-value lots to achieve equal division.
4. **Locks**: Collectors can "lock" specific coins to specific heirs via `MyCollectionScreen`. Locked items are pre-allocated to their designated heirs, and the LPT algorithm processes the remaining inventory around those locks.

---

## 5. Testing & Verification Runbook

All changes to the ingestion and parsing pipelines are verified against automated E2E and unit tests.

### 5.1 Playwright Frontend Verification
Routinely run Playwright specs to ensure navigation, auth, and upload dialogs do not break:
`npm test` (executed from `numista_tests/` folder).

### 5.2 Python Backend Verification
Run verification checks targeting latency, nickname endpoints, and condition normalizations (e.g. mapping `BU` $\rightarrow$ `MS-63`, `PR69` $\rightarrow$ `PF-69`):
`python run_overnight_tests.py` (executed from the project root).

---

## 6. Infrastructure Deployment SOP

Deployment utilizes a primary automated script:

### 6.1 Frontend Deploy (Firebase Hosting)
From the project root:
```powershell
.\deploy_production.ps1
```
*(This script builds the Flutter web app with `--release --base-href "/"` and pushes it to Firebase Hosting).*

> 🔴 **Verification Rule**: Cache settings on Firebase Hosting are aggressive. Always verify deployment updates using a fresh **Incognito Window** to prevent stale service worker caching.

### 6.2 Backend Deploy (Cloud Run)
From the `numista_backend/` directory:
```powershell
gcloud run deploy numista-backend --source . --project studio-9101802118-8c9a8 --region us-central1
```

### 6.3 Daily Scheduled Backups
- **Script**: `numista_auto_backup.ps1`
- **Configuration**: Scheduled daily at 7:00 PM in Windows Task Scheduler.
- **Behavior**: Stages changed files, commits them with a current timestamp, and pushes them to the GitHub main branch.
