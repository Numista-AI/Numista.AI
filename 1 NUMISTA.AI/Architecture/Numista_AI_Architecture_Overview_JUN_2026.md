# Numista.AI — System Architecture Overview

> **Version:** June 2026 | **Author:** Eric D. / Antigravity | **Status:** Production MVP (v3.5.0)
> **Replaces:** Numista.AI Architecture Overview 26 FEB 26.docx

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Module Map](#2-module-map)
3. [Layer-by-Layer Architecture](#3-layer-by-layer-architecture)
4. [Full API Endpoint Inventory](#4-full-api-endpoint-inventory)
5. [Data Flow Diagrams](#5-data-flow-diagrams)
6. [Firestore Data Schema](#6-firestore-data-schema)
7. [AI & Gemini Integration](#7-ai--gemini-integration)
8. [Subscription & Billing System](#8-subscription--billing-system)
9. [Authentication & Security Model](#9-authentication--security-model)
10. [External Integrations](#10-external-integrations)
11. [Deployment Architecture](#11-deployment-architecture)
12. [Known Limitations & Future Work](#12-known-limitations--future-work)

---

## 1. System Overview

Numista.AI is a **cross-platform coin collection management platform** powered by Google Gemini Vision AI. It allows numismatists to:

- **Digitize** collections via AI checklist scanning, binder scanning, PCGS import, manual entry, USB microscope, or spreadsheet upload
- **Identify** coins and world items using Gemini Vision (obverse + reverse photo analysis)
- **Track** collections with program-based progress, wish lists, eBay live pricing, and melt value tracking
- **Research** coins via AI chat (Morgan), numismatic deep-dive reports, and PCGS CoinFacts data
- **Estate Planning** — generate state-specific legal estate reports with attorney portal access
- **Monetize** via tiered Stripe subscriptions (Free → Sovereign) with feature gatekeeping

The platform consists of **four primary modules** running across local hardware, Google Cloud, and end-user devices:

```
+----------------------------------------------------------+
|                    numista_mobile                        |
|           Flutter Web / Android / iOS / Windows         |
|        (Primary user interface — all features)          |
|            v3.5.0  •  Dart SDK ^3.11.3                  |
+------------------------+---------------------------------+
                         | Firebase SDK (Firestore, Auth)
                         | REST (Cloud Run endpoints)
+------------------------v---------------------------------+
|               Google Cloud Platform                      |
|  GCP Project: studio-9101802118-8c9a8                   |
|  +------------------+  +--------------------+  +-------+ |
|  |   Firestore      |  |  Cloud Run          |  | GCS   | |
|  |  (primary DB)    |  |  numista-backend    |  | CDN   | |
|  |  Multi-region    |  |  numista-scan-svc   |  |Bucket | |
|  +------------------+  +--------------------+  +-------+ |
|  +------------------------------------------------------+ |
|  |  Gemini Vision AI  (gemini-3.5-flash / 3.1-pro)     | |
|  |  Vertex AI Search  (coin reference library 1.9k docs)| |
|  |  Document AI       (invoice parsing)                 | |
|  +------------------------------------------------------+ |
|  +------------------------------------------------------+ |
|  |  Firebase Auth + Firebase Hosting (Flutter web)      | |
|  +------------------------------------------------------+ |
+----------------------------------------------------------+
                         | Firestore real-time listener
+------------------------v---------------------------------+
|               numista_hardware                           |
|     Windows Desktop Agent (Python + OpenCV)             |
|     USB Microscope → Coin ID → GCS → Firestore          |
+----------------------------------------------------------+
```

---

## 2. Module Map

| Module | Language | Version / Runtime | Purpose |
|--------|----------|-------------------|---------|
| `numista_mobile` | Dart / Flutter | v3.5.0+35, SDK ^3.11.3 | Primary user application (Web, Android, iOS, Windows) |
| `numista_backend` | Python | 3.11-slim, FastAPI + uvicorn, Cloud Run | Main API — all Flutter calls route here |
| `numista_backend/scan_service` | Python | 3.11-slim, Flask, Cloud Run | Estate PDF generation + checklist scanning |
| `numista_hardware` | Python | Windows desktop, OpenCV | USB microscope agent, local coin ID |
| `numista_ai` | *(reserved)* | — | Future dedicated AI model workspace |

### GCP Configuration

| Setting | Value |
|---------|-------|
| **GCP Project** | `studio-9101802118-8c9a8` |
| **GCS Bucket (uploads)** | `numista-uploads-studio-9101802118-8c9a8` |
| **Cloud Run Region** | `us-central1` |
| **Gemini Location** | `global` (required for Gemini 3.x preview models) |
| **Firestore Location** | `(default)` multi-region |
| **Firebase Hosting** | `numista.ai` + `www.numista.ai` |

---

## 3. Layer-by-Layer Architecture

### 3.1 Frontend — `numista_mobile` (Flutter)

**Entry Point:** `lib/main.dart`
- Initializes Firebase via `firebase_options.dart`
- Auth gate: `StreamBuilder<User?>` on `FirebaseAuth.instance.authStateChanges()`
- Signed out → `LoginScreen` / `WelcomeScreen`; Signed in → `BaseLayout`

#### 3.1.1 Screen Inventory (25 screens as of June 2026)

| Screen | File | Purpose |
|--------|------|---------|
| `LoginScreen` | `login_screen.dart` | Firebase Auth (email/password + Google Sign-in) |
| `WelcomeScreen` | `welcome_screen.dart` | Onboarding splash / landing |
| `BaseLayout` | `base_layout.dart` | Shell with sidebar nav, responsive layout engine |
| `HomeDashboard` | `home_dashboard.dart` | Program browser, news feed, portfolio summary, spot prices |
| `MyCollectionScreen` | `my_collection_screen.dart` | Full collection grid/table, inspector panel, bulk actions |
| `AddCoinsHub` | `add_coins_hub.dart` | Multi-tab coin entry (Manual, PCGS, Checklist, Roll, CSV, Binder Scan) |
| `AddWorldItemScreen` | `add_world_item_screen.dart` | International / world coin entry + Gemini ID |
| `WishlistScreen` | `wishlist_screen.dart` | Wish list with eBay live pricing + "I Found It!" flow |
| `ProgramManagerScreen` | `program_manager_screen.dart` | Browse/search US Mint programs |
| `CoinDetailScreen` | `coin_detail_screen.dart` | Full coin inspector with Deep Dive AI, PCGS data, images |
| `CoinSearchScreen` | `coin_search_screen.dart` | Vertex AI Search across reference library (1,900+ coins) |
| `MicroscopeScanScreen` | `microscope_scan_screen.dart` | Hardware agent control + live status polling |
| `ReviewHubScreen` | `review_hub_screen.dart` | Binder scan upload + checklist multi-page processing |
| `AIChatScreen` | `ai_chat_screen.dart` | "Morgan" — Gemini-powered numismatic AI assistant |
| `EstatePlanningScreen` | `estate_planning_screen.dart` | Estate report builder (7 states), PDF generation |
| `AttorneyPortalScreen` | `attorney_portal_screen.dart` | Token-based read-only estate report access for attorneys |
| `HumanAITrainerScreen` | `human_ai_trainer_screen.dart` | Human-in-the-loop AI correction / training feedback |
| `AdminGradeFlagsScreen` | `admin_grade_flags_screen.dart` | Admin tool: grade dispute queue management |
| `SettingsScreen` | `settings_screen.dart` | User profile, PCGS token, preferences, subscription |
| `CustomerServiceScreen` | `customer_service_screen.dart` | Support chat, FAQs |
| `DesktopAgentDownloadScreen` | `desktop_agent_download_screen.dart` | Download / setup guide for hardware agent |
| `OurTeamScreen` | `our_team_screen.dart` | Team info page |
| `SuppliesScreen` | `supplies_screen.dart` | Numismatic supplies & affiliate links |
| `PrivacyScreen` | `privacy_screen.dart` | Privacy policy |
| `TermsScreen` | `terms_screen.dart` | Terms of service |

#### 3.1.2 Service Layer (30 services as of June 2026)

```
lib/services/
+-- auth_service.dart                 Firebase Auth wrapper; exposes userEmail, coinsPath
+-- numista_service.dart              General Firestore helpers (coin CRUD)
+-- reference_service.dart            Stream of global_programs from Firestore
+-- reference_library_service.dart    Reference image URL resolution from GCS
+-- reference_seed_service.dart       One-time admin migration to cloud
+-- coin_programs_data.dart           Local fallback copy of US coin program catalog
+-- wishlist_service.dart             Wishlist CRUD + StreamBuilder support
+-- checklist_generator_service.dart  PDF checklist generation (dart:ui canvas)
+-- checklist_scan_service.dart       HTTP client → scan_service Cloud Run endpoint
+-- pcgs_import_service.dart          PCGS Public API + cert# batch import + CSV parse
+-- pcgs_service.dart                 PCGS token fetch helper
+-- epn_service.dart                  eBay Partner Network live listing fetcher
+-- hardware_service.dart             HTTP polling client for numista_hardware agent
+-- mint_history_service.dart         Historical US mint mark data by year/denomination
+-- wizard_service.dart               Roll Entry wizard state + Firestore batch write
+-- guest_seed_service.dart           Demo collection seeding for guest mode
+-- coin_image_service.dart           Reference image URL lookup + GCS CDN resolver
+-- coin_normalizer_service.dart      Coin field normalization (series names, grade strings)
+-- coin_search_service.dart          Vertex AI Search REST client
+-- batch_valuation_service.dart      Bulk melt value + AI estimate calculations
+-- melt_value_service.dart           Silver/gold melt value from spot prices
+-- estate_data_service.dart          Estate report data aggregation
+-- estate_profile_service.dart       Attorney + estate profile management
+-- estate_report_service.dart        Estate report PDF trigger (platform dispatcher)
+-- estate_report_service_web.dart    Web-specific estate PDF download
+-- estate_report_service_mobile.dart Mobile-specific estate PDF save
+-- morgan_chat_context.dart          Morgan AI chat context builder + coin knowledge RAG
+-- morgan_prefs.dart                 Morgan chat user preference persistence
+-- portfolio_snapshot_service.dart   Portfolio value snapshots (daily/weekly tracking)
+-- world_item_service.dart           World/international coin CRUD + Gemini ID calls
```

#### 3.1.3 Widget Library

```
lib/widgets/
+-- add_coin_manual_form.dart         Manual coin entry form fields
+-- coin_set_viewer.dart              Flip-card coin set viewer (for gift sets)
+-- roll_entry_dialog.dart            3-step roll wizard (Identical/Sequential/Lot)
+-- scan_result_dialog.dart           AI scan result confirmation dialog
+-- extraction_success_dialog.dart    Checklist scan success summary
+-- wizard_overlay.dart               Guided onboarding wizard
+-- common/ref_image_widget.dart      Reference coin image loader from GCS
```

**Key Flutter Dependencies (pubspec.yaml):**
- `firebase_core` ^4.6.0, `cloud_firestore` ^6.2.0, `firebase_auth` ^6.3.0, `firebase_storage` ^13.2.0
- `firebase_ai` ^3.10.0 (Gemini via Firebase AI Logic for Morgan chat)
- `fl_chart` ^0.70.2 (portfolio charts)
- `pdf` ^3.12.0 + `printing` ^5.14.3 (checklist PDF generation)
- `cached_network_image` ^3.4.1 (GCS reference image caching)
- `file_picker` ^11.0.2, `image_picker` ^1.1.2 (scan upload)
- `two_dimensional_scrollables` ^0.4.2 (collection table)

---

### 3.2 Cloud Backend — `numista_backend` (Primary Cloud Run Service)

**URL:** `https://numista-backend-568985927038.us-central1.run.app`
**Runtime:** Python 3.11-slim, FastAPI + uvicorn
**Size:** `main.py` is ~5,565 lines covering all endpoints
**Memory:** 2Gi, min-instances=1 (no cold start), max=10, concurrency=20

#### 3.2.1 AI Configuration (as of June 2026)

```python
# Per official Gemini deprecation schedule Jun 11, 2026
PRIMARY_MODEL = "gemini-3.5-flash"      # Released May 19, 2026 — NO shutdown announced
PRO_MODEL     = "gemini-3.1-pro-preview" # Released Feb 19, 2026 — NO shutdown announced

# google-genai SDK (replaces deprecated vertexai SDK — shutdown Jun 24 2026)
genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
```

> **IMPORTANT:** `gemini-3-pro-preview` was SHUT DOWN March 9, 2026. Do NOT use.
> All Gemini 3.x models require `location='global'` on Vertex AI.

#### 3.2.2 Backend Directory Structure

```
numista_backend/
  main.py               ← Production FastAPI app (~5,565 lines, all endpoints)
  tier_gatekeeper.py    ← Subscription tier enforcement + Stripe integration
  stripe_config.py      ← Stripe key loader from Streamlit secrets
  morgan_knowledge.py   ← RAG knowledge base for Morgan AI chat
  Dockerfile            ← python:3.11-slim base
  requirements.txt      ← Full pinned dependency list
  cloudbuild.yaml       ← Build config (used with gcloud builds submit)
  .gcloudignore         ← Excludes _archive/, _scripts/, binaries from Docker
  firestore.rules       ← Firestore security rules (deployed to Firebase)
  storage.rules         ← GCS security rules
  firestore.indexes.json← Composite index definitions
  vertex_search/        ← Vertex AI Search module (coin reference library)
  scan_service/         ← Separate Cloud Run service (estate PDF + checklist scan)
  sync_worker/          ← Monthly Cloud Run Job (Wikipedia → Firestore sync)
  functions/            ← Firebase Cloud Functions (Node.js)
  database/             ← Local admin DB assets
  _archive/             ← Legacy files (app.py — old Streamlit frontend)
  _scripts/             ← 181 one-time data ingestion/migration scripts
```

---

### 3.3 Scan Service — `numista_backend/scan_service` (Secondary Cloud Run Service)

**URL:** Separate Cloud Run service (`numista-scan-service`)
**Runtime:** Python 3.11-slim, Flask
**Memory:** 1Gi
**Model:** `gemini-3.5-flash` via `google-genai` SDK

#### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `POST /scan_checklist` | multipart/form-data | Accepts checklist image + program_id + user_id; calls Gemini Vision; writes results to Firestore |
| `POST /generate_estate_report` | application/json | Generates state-specific estate report PDF (7 states) |
| `GET /health` | — | Health check, returns model name + SDK version |

---

### 3.4 Hardware Agent — `numista_hardware`

**Entry Point:** `auto_capture.py`
**Runtime:** Python, Windows desktop
**Dependencies:** OpenCV (`cv2`), Flask, Google Cloud SDK, `google-genai`
**Distribution:** PyInstaller `.exe` → Windows Task Scheduler auto-start

#### 3.4.1 File Structure

```
numista_hardware/
+-- auto_capture.py       Main agent: camera loop, vision pipeline, Flask server
+-- identify_coin.py      Gemini Vision coin identification (obverse + reverse)
+-- pcgs_service.py       Local PCGS enrichment (silver detection, melt value)
+-- coin_engine.py        Coin data normalization helpers
+-- tray_agent.py         Windows system tray icon (minimize to tray)
+-- scan_coin.py          Standalone single-scan utility
+-- agent_config.py       Agent configuration + environment loader
+-- agent_setup.py        Hardware agent installer / setup wizard
+-- index.html            Local web UI for the agent
+-- install_agent.ps1     Windows startup auto-install script
+-- NumistaAgent.spec     PyInstaller spec for .exe packaging
+-- NumistaAgentSetup.nsi NSIS installer script
```

#### 3.4.2 Capture Pipeline

```
Camera (USB Microscope or Webcam)
    |
    v
OpenCV frame capture (1920x1080)
    |
    v
Sharpness analysis (Laplacian variance)
Motion detection (Gaussian blur diff)
Coin detection (contour area threshold > 10,000px)
    |
    v
Pre-capture countdown (3-second hold-still timer)
    |
    v
Auto-capture → crop_coin() → JPEG saved
    |  [OBVERSE complete]
    v
"FLIP COIN" prompt (8-second lockout)
    |  [REVERSE complete]
    v
run_numista_report(obv_path, rev_path)
    |
    v
Gemini Vision → coin identification JSON
    {year, denomination, mint_mark, grade, program_series,
     ai_estimated_value, verification_confidence, report}
    |
    v
PCGS enrichment (silver flag, melt value, PCGS#)
    |
    v
GCS upload → microscope/{email}/{slug}_{side}_{ts}.jpg
    |
    v
Firestore: users/{email}/coins/{uuid}
```

#### 3.4.3 Remote Trigger Architecture (Firestore Command Bus)

```
Flutter App (MicroscopeScanScreen)
    |
    v  writes
commands/{email}/pending/{docId}  {command: "start_scan"}
    |
    v  real-time listener (on_snapshot)
Hardware Agent (on_command_snapshot)
    |
    v  deletes doc (acknowledge)
capture_worker thread → [pipeline above]
    |
    v
commands/{email}/results/{coin_id}  {status: "saved", gcs_urls: ...}
```

Flutter polls `GET http://localhost:5000/get-status` every 500ms for live sharpness, motion, countdown.

---

### 3.5 Data Infrastructure (Google Cloud)

#### 3.5.1 Firestore Collections

| Collection | Content | Access |
|------------|---------|--------|
| `users/{email}/coins` | Full coin documents | Per-user isolated (isOwner rule) |
| `users/{email}/wishlist` | Wishlist items (individual or program) | Per-user |
| `users/{email}/checklist_entries` | Scanned checklist results | Per-user |
| `users/{email}/estate_reports` | Estate report metadata + PDF links | Owner read; token-based attorney `get` |
| `global_programs/{program_id}` | Program definition with coin + variety tree | Public read, backend-write only |
| `config/pcgs` | Platform PCGS bearer token | Auth read, backend-write only |
| `config/epn` | eBay Partner Network API key | Auth read, backend-write only |
| `commands/{email}/pending` | Hardware agent command queue | Agent listens |
| `commands/{email}/results` | Hardware scan confirmation | Flutter reads |
| `coin_set_index/{set_id}` | Coin set manifests | Read-only |
| `coin_image_index/{...}` | GCS reference image index (4.5M rows) | Auth read, backend-write only |
| `admin_grade_flags/{...}` | AI grade dispute queue | Backend only |
| `supplies_log/{...}` | Supplies affiliate tracking | Backend only |
| `pending_items/{...}` | Backend processing queue | Backend only |

#### 3.5.2 GCS Bucket Structure

```
numista-uploads-studio-9101802118-8c9a8/
+-- microscope/{email}/{slug}_Obverse_{timestamp}.jpg   ← Hardware captures
+-- microscope/{email}/{slug}_Reverse_{timestamp}.jpg
+-- reference/{program_id}/{coin_id}_obverse.jpg        ← Reference library (public CDN)
+-- reference/{program_id}/{coin_id}_reverse.jpg
+-- checklists/{program_id}/page_{n}.pdf                ← Generated PDFs
+-- binder_scans/{email}/{binder_id}/                   ← Binder scan uploads
+-- invoices/{email}/{uuid}/                            ← Invoice scan uploads
+-- estate_reports/{email}/{report_id}.pdf              ← Estate report PDFs
```

---

## 4. Full API Endpoint Inventory

All endpoints served from `numista-backend` Cloud Run service at `https://numista-backend-568985927038.us-central1.run.app`.

### Core / Utility

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/` | Health check / API root |
| `GET` | `/api/spot_prices` | Live silver/gold spot prices (yfinance) |
| `GET` | `/api/template` | Download NumisMate collection CSV template |
| `GET` | `/api/collection/count` | Get coin count for a user |
| `POST` | `/api/collection/clear` | Admin: clear a user's collection |

### Coin Identification & Valuation

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/identify_coin_photo` | Gemini Vision coin ID from uploaded photo |
| `POST` | `/api/identify-world-item` | Gemini Vision world/international item ID |
| `POST` | `/api/estimate_value_text` | AI text-based value estimate (no photo) |
| `GET` | `/api/coin_crop` | GCS image URL → crop coin from binder scan tile |
| `GET` | `/api/coin_search` | Vertex AI Search — coin reference library (registered by `vertex_search` module) |

### Import & Normalization

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/import_spreadsheet` | Parse + import user spreadsheet (CSV/Excel/PCGS CSV) |
| `POST` | `/api/normalize_backfill` | Normalize colloquial coin names in existing collection |
| `POST` | `/api/import/start` | Start async bulk import session |
| `GET` | `/api/import/status/{session_id}` | Poll async import session status |
| `POST` | `/api/import/process` | Process next batch in import session |

### PCGS

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/pcgs/cert/{cert_no}` | Server-side PCGS cert lookup (Cloudflare bypass proxy) |

### Checklist & Binder Scanning

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/analyze_binder_scan` | Gemini Vision binder page analysis → coin grid |
| `POST` | `/api/confirm_binder_scan` | Commit confirmed binder scan results to Firestore |
| `GET` | `/api/binder_scans/{user_email}` | List user's binder scan sessions |
| `GET` | `/api/binder_scans/{user_email}/{binder_id}` | Get binder scan detail |
| `POST` | `/api/analyze_checklist` | Gemini Vision checklist scan (alternative endpoint) |

### Review Hub

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/review/commit` | Commit reviewed checklist/scan results |
| `POST` | `/api/review/break_up_set` | Break a coin set into individual coins |
| `POST` | `/api/review/keep_set_as_is` | Keep a scanned set as a single set record |
| `POST` | `/api/review/bulk_update` | Bulk field update on multiple coins |

### De-duplication

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/dedup_sweep` | Scan collection for duplicate coins |
| `POST` | `/api/dedup_sweep/auto_clean` | Auto-remove confirmed duplicates |

### AI Deep Dive & Chat

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/deep_dive` | Gemini Pro deep-dive numismatic report for a coin |

### Nicknames (Community)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/nicknames/submit` | Submit a new coin nickname |
| `GET` | `/api/nicknames` | List community coin nicknames |
| `POST` | `/api/nicknames/{doc_id}/vote` | Vote on a nickname |
| `GET` | `/api/nicknames/stats` | Nickname usage statistics |

### Grade Review (Human-AI Trainer)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/grade_review/queue` | Get AI grading dispute queue |
| `POST` | `/api/grade_review/submit` | Submit human grade correction |
| `GET` | `/api/grade_review/stats` | Grade review statistics |

### Admin

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/admin/grade_flags` | List unresolved admin grade flags |
| `POST` | `/api/admin/grade_flags/{flag_id}/resolve` | Resolve a grade flag |

### News

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/mint_news` | US Mint + numismatic news feed (NewsAPI + feedparser) |
| `POST` | `/api/dismiss_news` | Dismiss a news item for user |
| `GET` | `/api/dismissed_news/{user_email}` | Get user's dismissed news list |

### Invoice / Receipts

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/process_invoice` | Document AI invoice parsing (dealer receipts) |
| `GET` | `/api/receipts/{user_email}` | List user's stored receipts |
| `GET` | `/api/receipts/{user_email}/{receipt_id}/view_url` | Get signed GCS URL for receipt |

### Scan Service (Separate Cloud Run)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/scan_checklist` | Checklist image → Gemini Vision → Firestore write |
| `POST` | `/generate_estate_report` | Generate state-specific estate PDF |
| `GET` | `/health` | Health check |

---

## 5. Data Flow Diagrams

### 5.1 Checklist Scan Pipeline

```
User photographs printed checklist (mobile camera)
    |
    v
ReviewHubScreen: select program + upload image(s)
    |
    v
checklist_scan_service.dart
    POST /scan_checklist  (multipart/form-data)
    {image, program_id, user_id, page_number, total_pages}
    |
    v
scan_service (Cloud Run)
    1. Firestore: GET global_programs/{program_id}
    2. chunk_coin_list()  -- page-aware coin subset
    3. Gemini Vision: system_prompt + image + coin_list
    4. parse_json() with truncation recovery
    5. write_to_firestore():
         owned=true  → checklist_entries/{program}__{coin}
         owned=false → checklist_entries + wishlist (merge)
    |
    v
Flutter: ExtractionSuccessDialog
    {X coins owned, Y added to wishlist, confidence: Z%}
```

### 5.2 Binder Scan Pipeline (New June 2026)

```
User photographs coin binder page
    |
    v
ReviewHubScreen: "Scan Binder" tab
    |
    v
POST /api/analyze_binder_scan
    Gemini Vision: binder grid → coin tile positions + identifications
    GCS upload: binder_scans/{email}/{binder_id}/
    |
    v
Flutter: Review each coin tile (accept / reject / edit)
    |
    v
POST /api/confirm_binder_scan
    Batch-write confirmed coins → users/{email}/coins
```

### 5.3 Hardware Microscope Pipeline

```
User taps "Start Scan" in MicroscopeScanScreen
    |
    v
hardware_service.dart
    Firestore write: commands/{email}/pending
    {command: "start_scan"}
    |
    v
numista_hardware auto_capture.py (always-on daemon)
    on_command_snapshot() → capture_worker thread
    |
    v
[OpenCV loop: sharpness → stability → countdown → capture]
    Obverse JPEG → captures/obverse_peak.jpg
    "FLIP COIN" prompt (8-sec lockout)
    Reverse JPEG → captures/reverse_peak.jpg
    |
    v
identify_coin.py → Gemini Vision
    Returns: year, denomination, mint_mark, grade, series,
             value estimate, confidence, numismatic report
    |
    v
pcgs_service.py → PCGS enrichment
    Returns: is_silver, metal_content, melt_value, pcgs_number
    |
    v
upload_to_gcs_local() → GCS bucket
    microscope/{email}/{slug}_{side}_{ts}.jpg
    |
    v
Firestore write: users/{email}/coins/{uuid}  (full coin doc)
Firestore write: commands/{email}/results/{uuid}  (confirmation)
    |
    v
Flutter polls localhost:5000/get-status every 500ms
    → Live sharpness bar, countdown ring, final result card
```

### 5.4 PCGS Import Pipeline

```
User enters cert numbers or uploads PCGS CSV
    |
    v
AddCoinsHub → PCGS Import Tab
    |
    v
pcgs_import_service.dart
    parseCertNumbersFromCsv() [if CSV input]
    |
    v  for each cert number:
    Firestore: check for duplicate (Certification Number field)
    |
    v
    GET /api/pcgs/cert/{certNo}
    (server-side proxy bypasses Cloudflare browser restriction)
    |
    v
    mapToFirestoreSchema()  PCGS fields → Numista schema
    |
    v
    Firestore: users/{email}/coins.add(firestoreData)
    |
    v
PcgsImportResult: {successCount, failedCount, duplicateCount}
    → UI shows import summary card
```

### 5.5 Estate Report Pipeline (New 2026)

```
User: EstatePlanningScreen → selects state + report mode
    {living_inventory | estate_settlement}
    |
    v
estate_data_service.dart
    Aggregates: user coins + valuations + melt values
    |
    v
POST /generate_estate_report (scan_service Cloud Run)
    {uid, mode, state, owner_name, attorney_info, ...}
    |
    v
estate_report_generator.py
    1. Fetch all coins from Firestore: users/{uid}/coins
    2. Apply state_rules.py (state-specific legal language)
    3. estate_pdf_builder.py → ReportLab PDF generation
    4. GCS upload: estate_reports/{uid}/{report_id}.pdf
    5. Firestore: users/{uid}/estate_reports/{report_id}
       {token: uuid, attorney_email, gcs_url, state, mode}
    |
    v
Flutter: share PDF link / email attorney
    Attorney accesses: AttorneyPortalScreen
    Token-based Firestore read (no auth required for attorney)
```

---

## 6. Firestore Data Schema

### 6.1 Coin Document (`users/{email}/coins/{docId}`)

```json
{
  "Year":                      "1921",
  "Country":                   "United States",
  "Denomination":              "Dollar",
  "Mint Mark":                 "D",
  "Condition":                 "MS-63",
  "Program/Series":            "Morgan Silver Dollar",
  "Theme/Subject":             "Liberty Head / Eagle",
  "AI Estimated Value":        "$95.00",
  "Melt Value":                "$22.14",
  "Metal Content":             "90% Silver, 10% Copper",
  "Is Silver":                 true,
  "PCGS Number":               "7294",
  "Certification Number":      "12345678",
  "Grading Service":           "PCGS",
  "Holder Type":               "PCGS Slab",
  "Variety":                   "VAM-2",
  "Die Variety":               "VAM-2",
  "Cost":                      "$85.00",
  "Purchase Date":             "2026-04-15",
  "Storage Location":          "Morgan Binder",
  "Personal Notes":            "Gorgeous luster",
  "Numismatic Report":         "Full AI analysis text...",
  "Quantity":                  1,
  "Population":                "1,250",
  "Is NFC Secure":             false,
  "image_url_obverse":         "https://storage.googleapis.com/.../obverse.jpg",
  "image_url_reverse":         "https://storage.googleapis.com/.../reverse.jpg",
  "source":                    "pcgs_api | hardware_agent | manual | checklist_scan | roll_wizard | binder_scan | csv_import | world_item",
  "scan_source":               "microscope | binder | checklist",
  "scan_date":                 "20260415_1432",
  "deep_dive_status":          "PENDING | COMPLETE",
  "roll_id":                   "roll_quarter_1746123456789",
  "roll_type":                 "identical | sequential | lot",
  "verification_confidence":   "HIGH",
  "reference_images_used":     4,
  "added_at":                  "<Firestore Timestamp>",
  "created_at":                "<Firestore Timestamp>"
}
```

### 6.2 World Item Document (`users/{email}/coins/{docId}`)

World/international items share the same collection but include additional fields:
```json
{
  "Country":         "Germany",
  "item_type":       "coin | medal | token | banknote",
  "world_item":      true,
  "source":          "world_item"
}
```

### 6.3 Global Program Document (`global_programs/{program_id}`)

```json
{
  "id":          "morgan_dollar",
  "name":        "Morgan Dollar",
  "category":    "Dollars",
  "years":       "1878-1904, 1921",
  "description": "...",
  "coins": [
    {
      "id":      "1878_p",
      "name":    "1878",
      "year":    1878,
      "varieties": [
        {"id": "8TF",   "name": "8 Tail Feathers",   "mint_marks": ["P"]},
        {"id": "7TF",   "name": "7 Tail Feathers",   "mint_marks": ["P"]},
        {"id": "7/8TF", "name": "7/8 Tail Feathers", "mint_marks": ["P"]}
      ]
    }
  ]
}
```

### 6.4 User Profile Document (`users/{email}`)

```json
{
  "stripe_tier":          "free | hobbyist | collector | numismatist | sovereign",
  "tier":                 "free",
  "power_user":           false,
  "pcgsToken":            "user_personal_token_if_set",
  "last_usage_date":      "2026-06-19",
  "deepdive_count":       3,
  "invoice_scan_count":   1,
  "dismissed_news":       ["article_id_1", "article_id_2"],
  "morgan_prefs":         { "tone": "casual", "expertise": "intermediate" }
}
```

### 6.5 Estate Report Document (`users/{email}/estate_reports/{reportId}`)

```json
{
  "token":          "uuid-serves-as-access-token",
  "state":          "NY",
  "mode":           "living_inventory | estate_settlement",
  "owner_name":     "John Smith",
  "attorney_email": "attorney@lawfirm.com",
  "gcs_url":        "https://storage.googleapis.com/.../report.pdf",
  "created_at":     "<Firestore Timestamp>"
}
```

---

## 7. AI & Gemini Integration

### 7.1 Models in Use (June 2026)

| Service | Model | SDK | Purpose |
|---------|-------|-----|---------|
| Main Backend (Cloud Run) | `gemini-3.5-flash` | `google-genai` ≥1.71.0 | Coin ID photos, binder scan, world item ID, deep dive, text valuation |
| Main Backend (Pro features) | `gemini-3.1-pro-preview` | `google-genai` | Deep Dive reports, complex analysis |
| Scan Service (Cloud Run) | `gemini-3.5-flash` | `google-genai` | Checklist OCR + checkbox detection; estate report narrative |
| Hardware Agent | `gemini-3.5-flash` | `google-genai` | Coin ID from microscope photos |
| Morgan AI Chat (Flutter) | Gemini via `firebase_ai` SDK | Firebase AI Logic | Numismatic Q&A conversational assistant |
| Vertex AI Search | `numista-coin-library` | `google-cloud-discoveryengine` | Reference library search (1,913 coin documents, Enterprise + LLM tier) |
| Document AI | Processor (invoice type) | `google-cloud-documentai` | Dealer invoice / receipt parsing |

### 7.2 Prompt Engineering

**Checklist Scanner:** Two-part prompt — strict system instruction (checkbox rules + JSON-only output) + per-request prompt listing every expected coin ID. Coin list is chunked by page to stay within token limits.

**Binder Scanner:** Structured prompt requesting coin position grid, identification, and confidence for each tile in the binder page photo.

**Coin Identifier (Hardware + Photo Upload):** Structured prompt requesting year, denomination, mint mark, grade, series, theme, estimated value, and numismatic report. Uses GCS reference images for comparison.

**World Item Identifier:** Prompt adapted for international coins and non-US items — country detection, foreign denomination, and era identification.

**Deep Dive:** Uses `gemini-3.1-pro-preview` for extended numismatic analysis covering population data, variety details, historical context, and market analysis.

**Morgan Chat:** Conversational assistant with `morgan_knowledge.py` RAG context. Covers US coinage, grading standards, collection management, and market trends. Persona is friendly expert named "Morgan."

### 7.3 JSON Recovery Logic

The scan service handles truncated Gemini responses: if JSON is cut off mid-token (hit output token limit), it finds the last complete `}}` pair, closes the JSON object, and continues rather than failing the entire scan.

---

## 8. Subscription & Billing System

### 8.1 Tier Definitions

| Tier | Coin Limit | Deep Dive/day | Invoice Scans/day | Notes |
|------|-----------|--------------|-------------------|-------|
| `free` | 20 | 3 | 1 | Default for new users |
| `hobbyist` | 100 | 10 | 5 | Entry paid tier |
| `collector` | 199 | 25 | 15 | Mid tier |
| `numismatist` | 500 | 100 | 50 | Power tier |
| `sovereign` | Unlimited | 500 | 250 | Top tier |
| `power_user` | Unlimited | Unlimited | Unlimited | Internal beta bypass |

### 8.2 Tier Gatekeeper (`tier_gatekeeper.py`)

Located at `numista_backend/tier_gatekeeper.py`. Provides:

- `get_user_profile(email)` — reads `users/{email}` from Firestore
- `get_user_tier(profile)` — resolves from `stripe_tier` → `tier` → `"free"`
- `get_coin_count(email)` — Firestore `.count()` aggregation (no document reads)
- `check_and_enforce_coin_limit(email, ...)` — blocks add if over tier limit; shows Stripe upgrade button
- `check_and_increment_daily_usage(email, feature_type)` — token bucket per feature per day; auto-resets daily

### 8.3 Stripe Integration

| Config | Location |
|--------|----------|
| Secret Key | `.streamlit/secrets.toml` → `STRIPE_SECRET_KEY` |
| Publishable Key | `.streamlit/secrets.toml` → `STRIPE_PUBLISHABLE_KEY` |
| Price IDs | `.streamlit/secrets.toml` → `STRIPE_PRICE_{TIER}` |
| Key loader | `stripe_config.py` (`load_stripe_keys()`) |

- **Checkout:** `stripe.checkout.Session.create(mode="subscription", allow_promotion_codes=True)`
- **Portal:** `stripe.billing_portal.Session.create(customer_id, return_url)`
- **Coupon Support:** Beta testers can enter promo codes at checkout

---

## 9. Authentication & Security Model

### 9.1 Firebase Authentication

- **Primary:** Email/password
- **Secondary:** Google Sign-In
- **Auth state:** `FirebaseAuth.instance.authStateChanges()` stream drives the auth gate in `main.dart`

### 9.2 User Data Isolation

All Firestore paths are user-scoped:
```dart
// auth_service.dart
static String get coinsPath => 'users/$userEmail/coins';
```

Firestore security rules (`firestore.rules`):
- `users/{email}/{document=**}` — `isOwner(email)` only
- `users/{email}/estate_reports/{reportId}` — owner full access; `get` (not list) permitted for any caller (attorney token-based access)
- `global_programs/{...}` — public read, backend-write only
- `config/{...}` — authenticated read, backend-write only
- `coin_image_index/{...}` — authenticated read, backend-write only
- All other collections — deny

### 9.3 PCGS Token Management

- **Platform token:** `config/pcgs.bearerToken` (admin-write only via Firestore rules)
- **User token:** `users/{email}.pcgsToken` (user self-managed fallback)
- **Priority:** platform → user personal → error
- Tokens are never logged or exposed in Flutter client code

### 9.4 GCS Access

- Reference images: public CDN (`cache-control: public, max-age=31536000`)
- User microscope uploads: authenticated via service account key file
- Estate reports: signed URL access

> **CAUTION:** The hardware agent has `USER_EMAIL` hardcoded as `eric@numista.ai`.
> This must be replaced with dynamic auth before multi-user hardware deployment.

---

## 10. External Integrations

| Service | Purpose | Auth Method |
|---------|---------|-------------|
| **PCGS Public API** | Coin facts by cert# or PCGS#; auction prices | Bearer token (Firestore-managed) |
| **eBay Partner Network (EPN)** | Live listing prices on wishlist items | API key stored in Firestore `config/epn` |
| **NewsAPI** | Numismatic news feed on home dashboard | API key stored in Firestore |
| **yfinance** | Live silver/gold spot prices | Public (no auth) |
| **Stripe** | Subscription billing, checkout, customer portal | Secret key in `.streamlit/secrets.toml` |
| **Google Cloud Storage** | Reference coin images; microscope captures; estate PDFs | Service account / ADC |
| **Cloud Firestore** | Primary database, real-time listeners | Firebase SDK (authenticated) |
| **Firebase Auth** | User authentication, session management | Firebase SDK |
| **Vertex AI Search** | Semantic coin reference library search | ADC (service account) |
| **Google Document AI** | Dealer invoice/receipt parsing | ADC (service account) |

---

## 11. Deployment Architecture

### 11.1 Cloud Run Services

> Last verified: **June 16–19, 2026**

| Service | Source Directory | Memory | Config | Purpose |
|---------|-----------------|--------|--------|---------|
| `numista-backend` | `numista_backend/` | 2Gi | min-instances=1, max=10, concurrency=20 | **Primary API** — all Flutter app calls route here |
| `numista-scan-service` | `numista_backend/scan_service/` | 1Gi | — | Estate PDF generation + binder checklist scanning |

> **Note:** 5 legacy services deleted June 16, 2026: `annotate-gcs`, `annotate-http`, `coin-app`, `numista-ai-prod`, `scan-service`.

**Flutter app backend URL** — defined in a single constant:
```dart
// numista_mobile/lib/constants.dart
const String kApiBaseUrl =
    'https://numista-backend-568985927038.us-central1.run.app';
```

### 11.2 Python Backend Tech Stack

```
Base image:     python:3.11-slim
Framework:      FastAPI + uvicorn
AI SDK:         google-genai >= 1.71.0 (unified SDK — NOT legacy vertexai or google-generativeai)
Key packages:   Pillow, pandas, yfinance, feedparser, stripe, firebase-admin,
                google-cloud-documentai, google-cloud-discoveryengine,
                google-cloud-firestore, google-cloud-storage, opencv-python
Version:        Python 3.11 (upgraded from 3.9 on June 16, 2026)
```

### 11.3 Backend Deploy Command

```powershell
# From numista_backend/
gcloud builds submit . --tag gcr.io/studio-9101802118-8c9a8/numista-backend:latest --project studio-9101802118-8c9a8
gcloud run deploy numista-backend --image gcr.io/studio-9101802118-8c9a8/numista-backend:latest --region us-central1 --project studio-9101802118-8c9a8 --quiet
```

### 11.4 Flutter Web Hosting

Flutter web build deployed to **Firebase Hosting** (`firebase.json` + `.firebaserc`).
Deploy via: `.\deploy_production.ps1` from project root.
Live URL: `https://numista.ai`

### 11.5 CI/CD Pipeline (GitHub Actions)

Two workflows in `.github/workflows/`:

| File | Purpose |
|------|---------|
| `deploy-production.yml` | Automated deployment on push to `main`: Job 1 → Backend (Cloud Build → Cloud Run); Job 2 → Flutter (build web → Firebase Hosting) |
| `numista-ai-tests.yml` | Automated test suite |

- **Auth:** Workload Identity Federation (no service account key files in GitHub)
- **Secrets required:** `WIF_PROVIDER` and `WIF_SERVICE_ACCOUNT` as GitHub repository secrets

### 11.6 Hardware Agent Distribution

- Packaged as a Windows `.exe` via PyInstaller (`NumistaAgent.spec`)
- Installer built with NSIS (`NumistaAgentSetup.nsi`)
- Auto-starts with Windows via Task Scheduler (`install_agent.ps1`)
- System tray integration via `tray_agent.py`

### 11.7 Daily Automated Backup

- **Script:** `numista_auto_backup.ps1` (project root)
- **Schedule:** Windows Task Scheduler — daily at 7:00 PM
- **Target:** `github.com/Numista-AI/Numista.AI` (main branch)
- **Behavior:** Stages all changes, commits with timestamp, pushes to GitHub
- **Fallback:** `StartWhenAvailable` ensures backup runs if machine was off at 7 PM

---

## 12. Known Limitations & Future Work

### Current Limitations

| Area | Limitation |
|------|-----------  |
| Hardware agent | `USER_EMAIL` hardcoded — single-user only today |
| PCGS proxy | Cert# lookup routes through Cloud Run; fragile if service is down |
| Checklist scan | Multi-page scans processed sequentially, not in parallel |
| AI Chat (Morgan) | No persistent conversation history across sessions |
| Mobile (iOS) | Full distribution requires physical Apple hardware + developer account |
| Reference images | ~4.5M row GCS index; image coverage is partial for rare coins |
| Tier gatekeeper | Uses Streamlit `st.secrets` — needs migration to FastAPI env vars for Cloud Run deployment |
| Stripe webhooks | No webhook handler for subscription lifecycle events (upgrades, cancellations not auto-synced to Firestore) |

### Planned Improvements

- [ ] Stripe webhook handler → auto-sync subscription status to Firestore `stripe_tier`
- [ ] Multi-user hardware agent (dynamic user ID from Firebase Auth)
- [ ] Parallel multi-page checklist scanning
- [ ] Morgan chat session persistence (Firestore-backed conversation history)
- [ ] Deep Dive AI reports available in Flutter UI (currently backend-only)
- [ ] Human-AI Trainer feedback loop integration with model training
- [ ] eBay snipe/alert integration for wishlist items
- [ ] iOS App Store distribution
- [ ] Real-time shared collections (multi-user collaboration)
- [ ] Offline mode with local SQLite sync
- [ ] NFC tag writing for coin holders (`Is NFC Secure` field primed)

---

*Document generated June 19, 2026. Reflects production state as of Flutter v3.5.0+35, backend revision 00061-lbh.*
