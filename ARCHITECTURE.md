# Numista.AI — System Architecture

> **Version:** May 2026 | **Author:** Numista Deployer | **Status:** Beta MVP

---

## Table of Contents
1. [System Overview](#1-system-overview)
2. [Module Map](#2-module-map)
3. [Layer-by-Layer Architecture](#3-layer-by-layer-architecture)
4. [Data Flow Diagrams](#4-data-flow-diagrams)
5. [Firestore Data Schema](#5-firestore-data-schema)
6. [AI & Gemini Integration](#6-ai--gemini-integration)
7. [Authentication & Security Model](#7-authentication--security-model)
8. [External Integrations](#8-external-integrations)
9. [Deployment Architecture](#9-deployment-architecture)
10. [Known Limitations & Future Work](#10-known-limitations--future-work)

---

## 1. System Overview

Numista.AI is a **cross-platform coin collection management platform** powered by Google Gemini Vision AI. It allows numismatists to:

- **Digitize** collections via AI checklist scanning, PCGS import, manual entry, or USB microscope
- **Identify** coins using Gemini Vision (obverse + reverse photo analysis)
- **Track** collections with program-based progress, wish lists, and eBay live pricing
- **Research** coins via AI chat, numismatic reports, and PCGS CoinFacts data

The platform consists of **three primary modules** running across local hardware, Google Cloud, and end-user devices:

```
+----------------------------------------------------------+
|                    numista_mobile                        |
|           Flutter Web / Android / iOS App               |
|        (Primary user interface -- all features)         |
+------------------------+---------------------------------+
                         | Firebase SDK (Firestore, Auth)
                         | REST (Cloud Run endpoints)
+------------------------v---------------------------------+
|               Google Cloud Platform                     |
|  +----------------+  +--------------+  +-------------+  |
|  |   Firestore    |  |  Cloud Run   |  |  GCS Bucket |  |
|  |  (primary DB)  |  | (AI services)|  |  (images)   |  |
|  +----------------+  +--------------+  +-------------+  |
|  +------------------------------------------------------+|
|  |      Gemini Vision AI  (gemini-3-flash-preview)      ||
|  +------------------------------------------------------+|
+----------------------------------------------------------+
                         | Firestore real-time listener
+------------------------v---------------------------------+
|               numista_hardware                          |
|     Windows Desktop Agent (Python + OpenCV)             |
|     USB Microscope -> Coin ID -> GCS -> Firestore       |
+----------------------------------------------------------+
```

---

## 2. Module Map

| Module | Language | Runtime | Purpose |
|--------|----------|---------|---------|
| `numista_mobile` | Dart / Flutter | Web, Android, iOS | Primary user application |
| `numista_backend` | Python | Cloud Run (GCP) | AI scan service, admin tools, data pipelines |
| `numista_hardware` | Python | Windows Desktop | USB microscope agent, local coin ID |
| `numista_ai` | *(reserved)* | -- | Future dedicated AI model workspace |

**GCP Project:** `studio-9101802118-8c9a8`
**GCS Bucket:** `studio-9101802118-8c9a8-uploads`
**Cloud Run Region:** `us-central1`
**Firestore Location:** `(default)` multi-region

---

## 3. Layer-by-Layer Architecture

### 3.1 Frontend -- `numista_mobile` (Flutter)

**Entry Point:** `lib/main.dart`
- Initializes Firebase via `firebase_options.dart`
- Auth gate: `StreamBuilder<User?>` on `FirebaseAuth.instance.authStateChanges()`
- Signed out -> `LoginScreen`; Signed in -> `BaseLayout`

#### 3.1.1 Screen Inventory

| Screen | File | Purpose |
|--------|------|---------|
| `LoginScreen` | `login_screen.dart` | Firebase Auth (email/password + Google Sign-in) |
| `BaseLayout` | `base_layout.dart` | Shell with sidebar nav, responsive layout engine |
| `HomeDashboard` | `home_dashboard.dart` | Program browser, news feed, portfolio summary |
| `MyCollectionScreen` | `my_collection_screen.dart` | Full collection grid/table, inspector panel |
| `AddCoinsHub` | `add_coins_hub.dart` | Multi-tab coin entry (Manual, PCGS, Checklist, Roll, CSV) |
| `WishlistScreen` | `wishlist_screen.dart` | Wish list with eBay live pricing + "I Found It!" flow |
| `ProgramManagerScreen` | `program_manager_screen.dart` | Browse/search US Mint programs |
| `MicroscopeScanScreen` | `microscope_scan_screen.dart` | Hardware agent control + live status polling |
| `AIChatScreen` | `ai_chat_screen.dart` | Gemini-powered numismatic AI assistant |
| `ReviewHubScreen` | `review_hub_screen.dart` | Checklist scan upload + multi-page processing |
| `SettingsScreen` | `settings_screen.dart` | User profile, PCGS token, preferences |
| `CustomerServiceScreen` | `customer_service_screen.dart` | Support chat, FAQs |
| `OurTeamScreen` | `our_team_screen.dart` | Team info page |
| `HumanAITrainerScreen` | `human_ai_trainer_screen.dart` | (Future) human-in-the-loop AI training |

#### 3.1.2 Service Layer

```
lib/services/
+-- auth_service.dart               Firebase Auth wrapper; exposes userEmail, coinsPath
+-- numista_service.dart            General Firestore helpers (coin CRUD)
+-- reference_service.dart          Stream of global_programs from Firestore
+-- reference_library_service.dart  Reference image URL resolution from GCS
+-- reference_seed_service.dart     One-time admin migration to cloud
+-- coin_programs_data.dart         Local fallback copy of US coin program catalog
+-- wishlist_service.dart           Wishlist CRUD + StreamBuilder support
+-- checklist_generator_service.dart  PDF checklist generation (dart:ui canvas)
+-- checklist_scan_service.dart     HTTP client -> scan_service Cloud Run endpoint
+-- pcgs_import_service.dart        PCGS Public API + cert# batch import + CSV parse
+-- pcgs_service.dart               PCGS token fetch helper
+-- epn_service.dart                eBay Partner Network live listing fetcher
+-- hardware_service.dart           HTTP polling client for numista_hardware agent
+-- mint_history_service.dart       Historical US mint mark data by year/denomination
+-- wizard_service.dart             Roll Entry wizard state + Firestore batch write
+-- guest_seed_service.dart         Demo collection seeding for guest mode
```

#### 3.1.3 Widget Library

```
lib/widgets/
+-- add_coin_manual_form.dart        Manual coin entry form fields
+-- coin_set_viewer.dart             Flip-card coin set viewer (for gift sets)
+-- roll_entry_dialog.dart           3-step roll wizard (Identical/Sequential/Lot)
+-- scan_result_dialog.dart          AI scan result confirmation dialog
+-- extraction_success_dialog.dart   Checklist scan success summary
+-- wizard_overlay.dart              Guided onboarding wizard
+-- common/ref_image_widget.dart     Reference coin image loader from GCS
```

---

### 3.2 Cloud Backend -- `numista_backend`

#### 3.2.1 Scan Service (Cloud Run)

**Path:** `numista_backend/scan_service/`
**URL:** `https://scan-service-568985927038.us-central1.run.app`
**Runtime:** Python 3.9, Flask, `google-genai` SDK

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `POST /scan_checklist` | multipart/form-data | Accepts checklist image + program_id + user_id; calls Gemini Vision; writes results to Firestore |
| `GET /health` | -- | Health check, returns model name + SDK version |

**Scan Pipeline:**
1. Receive image bytes + `program_id` + `user_id` + page metadata
2. Load program coin list from `global_programs/{program_id}` in Firestore
3. Chunk coin list by page number (reduces output tokens ~65%)
4. Call `gemini-3-flash-preview` with system prompt + image + structured coin list
5. Parse JSON response (with truncation-recovery logic)
6. Batch-write to `users/{uid}/checklist_entries` (owned) and `users/{uid}/wishlist` (unowned)
7. Return summary JSON

#### 3.2.2 Sync Worker (Cloud Run)

**Path:** `numista_backend/sync_worker/`
Handles background data synchronization between local processing results and Firestore.

#### 3.2.3 Main Backend App (`app.py` + `main.py`)

A Streamlit + FastAPI hybrid (193 KB) used for admin data management, bulk ingestion, reference library management, and manual coin ID testing.

#### 3.2.4 Data Pipeline Scripts

| Category | Scripts | Purpose |
|----------|---------|---------|
| Schema patching | `patch_*.py` (20+) | One-time Firestore data fixes per program |
| Phase 2 ingestion | `run_phase2_*.py` (30+) | Wikipedia/Smithsonian image scraping + enrichment |
| Auditing | `audit_*.py` | Validate Firestore data integrity per program |
| Image management | `build_image_index.py`, `sync_local_images_to_gcs.py` | Build and sync reference image library to GCS |
| PCGS proxy | Inside `main.py` | `/api/pcgs/cert/{certNo}` server-side Cloudflare bypass |
| Contribution ingestion | `ingest_contributions.py` | Process user-submitted coin photos |
| Coin set ingestion | `ingest_coin_set.py` | Push coin set manifests to `coin_set_index` |

---

### 3.3 Hardware Agent -- `numista_hardware`

**Entry Point:** `auto_capture.py`
**Runtime:** Python, Windows desktop
**Dependencies:** OpenCV (`cv2`), Flask, Google Cloud SDK, `google-genai`

#### 3.3.1 File Structure

```
numista_hardware/
+-- auto_capture.py       Main agent: camera loop, vision pipeline, Flask server
+-- identify_coin.py      Gemini Vision coin identification (obverse + reverse)
+-- pcgs_service.py       Local PCGS enrichment (silver detection, melt value)
+-- coin_engine.py        Coin data normalization helpers
+-- tray_agent.py         Windows system tray icon (minimize to tray)
+-- scan_coin.py          Standalone single-scan utility
+-- index.html            Local web UI for the agent
+-- install_agent.ps1     Windows startup auto-install script
+-- NumistaAgent.spec     PyInstaller spec for .exe packaging
```

#### 3.3.2 Capture Pipeline

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
Auto-capture -> crop_coin() -> JPEG saved
    |  [OBVERSE complete]
    v
"FLIP COIN" prompt (8-second lockout)
    |  [REVERSE complete]
    v
run_numista_report(obv_path, rev_path)
    |
    v
Gemini Vision -> coin identification JSON
    {year, denomination, mint_mark, grade, program_series,
     ai_estimated_value, verification_confidence, report}
    |
    v
PCGS enrichment (silver flag, melt value, PCGS#)
    |
    v
GCS upload -> microscope/{email}/{slug}_{side}_{ts}.jpg
    |
    v
Firestore: users/{email}/coins/{uuid}
```

#### 3.3.3 Remote Trigger Architecture (Firestore Command Bus)

The hardware agent is triggered via Firestore, not HTTP, to avoid HTTPS mixed-content restrictions:

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
capture_worker thread -> [pipeline above]
    |
    v
commands/{email}/results/{coin_id}  {status: "saved", gcs_urls: ...}
```

Flutter polls `GET http://localhost:5000/get-status` every 500ms for live sharpness, motion, and countdown.

---

### 3.4 Data Infrastructure (Google Cloud)

#### 3.4.1 Firestore Collections

| Collection | Content | Access |
|------------|---------|--------|
| `users/{email}/coins` | Full coin documents | Per-user isolated |
| `users/{email}/wishlist` | Wishlist items (individual or program) | Per-user |
| `users/{email}/checklist_entries` | Scanned checklist results | Per-user |
| `global_programs/{program_id}` | Program definition with coin + variety tree | Read-only for users |
| `config/pcgs` | Platform PCGS bearer token | Admin write, user read |
| `commands/{email}/pending` | Hardware agent command queue | Agent listens |
| `commands/{email}/results` | Hardware scan confirmation | Flutter reads |
| `coin_set_index/{set_id}` | Coin set manifests | Read-only |

#### 3.4.2 GCS Bucket Structure

```
studio-9101802118-8c9a8-uploads/
+-- microscope/{email}/{slug}_Obverse_{timestamp}.jpg   <- Hardware captures
+-- microscope/{email}/{slug}_Reverse_{timestamp}.jpg
+-- reference/{program_id}/{coin_id}_obverse.jpg        <- Reference library
+-- reference/{program_id}/{coin_id}_reverse.jpg
+-- checklists/{program_id}/page_{n}.pdf                <- Generated PDFs
```

---

## 4. Data Flow Diagrams

### 4.1 Checklist Scan Pipeline

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
         owned=true  -> checklist_entries/{program}__{coin}
         owned=false -> checklist_entries + wishlist (merge)
    |
    v
Flutter: ExtractionSuccessDialog
    {X coins owned, Y added to wishlist, confidence: Z%}
```

### 4.2 Hardware Microscope Pipeline

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
    on_command_snapshot() -> capture_worker thread
    |
    v
[OpenCV loop: sharpness -> stability -> countdown -> capture]
    Obverse JPEG saved -> captures/obverse_peak.jpg
    "FLIP COIN" prompt (8-sec lockout)
    Reverse JPEG saved -> captures/reverse_peak.jpg
    |
    v
identify_coin.py -> Gemini Vision
    Returns: year, denomination, mint_mark, grade, series,
             value estimate, confidence, numismatic report
    |
    v
pcgs_service.py -> PCGS enrichment
    Returns: is_silver, metal_content, melt_value, pcgs_number
    |
    v
upload_to_gcs_local() -> GCS bucket
    microscope/{email}/{slug}_{side}_{ts}.jpg
    |
    v
Firestore write: users/{email}/coins/{uuid}  (full coin doc)
Firestore write: commands/{email}/results/{uuid}  (confirmation)
    |
    v
Flutter polls localhost:5000/get-status every 500ms
    -> Live sharpness bar, countdown ring, final result card
```

### 4.3 PCGS Import Pipeline

```
User enters cert numbers or uploads PCGS CSV
    |
    v
AddCoinsHub -> PCGS Import Tab
    |
    v
pcgs_import_service.dart
    parseCertNumbersFromCsv() [if CSV input]
    |
    v  for each cert number:
    Firestore: check for duplicate (Certification Number field)
    |
    v
    GET https://scan-service-*.run.app/api/pcgs/cert/{certNo}
    (server-side proxy bypasses Cloudflare browser restriction)
    |
    v
    mapToFirestoreSchema()  PCGS fields -> Numista schema
    |
    v
    Firestore: users/{email}/coins.add(firestoreData)
    |
    v
PcgsImportResult: {successCount, failedCount, duplicateCount}
    -> UI shows import summary card
```

---

## 5. Firestore Data Schema

### Coin Document (`users/{email}/coins/{docId}`)

```json
{
  "Year":                      "1921",
  "Country":                   "United States",
  "Denomination":              "Dollar",
  "Mint Mark":                 "D",
  "Condition":                 "MS-63",
  "Program/Series":            "Morgan Dollar",
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
  "source":                    "pcgs_api | hardware_agent | manual | checklist_scan | roll_wizard",
  "scan_source":               "microscope",
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

### Global Program Document (`global_programs/{program_id}`)

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

---

## 6. AI & Gemini Integration

### 6.1 Models in Use

| Service | Model | SDK | Purpose |
|---------|-------|-----|---------|
| Scan Service (Cloud Run) | `gemini-3-flash-preview` | `google-genai` | Checklist OCR + checkbox detection |
| Hardware Agent | `gemini-3-flash-preview` | `google-genai` | Coin ID from microscope photos |
| AI Chat (Flutter) | Gemini via Vertex AI | Firebase AI Logic | Numismatic Q&A assistant |

> **IMPORTANT:** The old `vertexai` Python SDK is deprecated (shutdown Jun 2026).
> All backend services now use `google-genai` SDK:
> `client = genai.Client(vertexai=True, project=..., location="global")`

### 6.2 Prompt Engineering

**Checklist Scanner:** Two-part prompt -- strict system instruction (checkbox rules + JSON-only output) + per-request prompt listing every expected coin ID. Coin list is chunked by page to stay within token limits.

**Coin Identifier:** Structured prompt requesting year, denomination, mint mark, grade, series, theme, estimated value, and numismatic report. Uses reference images from GCS for comparison.

**AI Chat:** Conversational assistant with numismatic expertise covering US coinage, grading standards, and collection management.

### 6.3 JSON Recovery Logic

The scan service handles truncated Gemini responses: if the JSON is cut off mid-token (hit output token limit), it finds the last complete `}}` pair, closes the JSON object, and continues rather than failing the entire scan.

---

## 7. Authentication & Security Model

### 7.1 Firebase Authentication
- **Primary:** Email/password
- **Secondary:** Google Sign-In
- **Auth state:** `FirebaseAuth.instance.authStateChanges()` stream drives the auth gate in `main.dart`

### 7.2 User Data Isolation

All Firestore paths are user-scoped:
```dart
// auth_service.dart
static String get coinsPath => 'users/$userEmail/coins';
```

> **CAUTION:** The hardware agent has `USER_EMAIL` hardcoded as `eric@numista.ai`.
> This must be replaced with dynamic auth before multi-user hardware deployment.

### 7.3 PCGS Token Management
- **Platform token:** `config/pcgs.bearerToken` (admin-write only via Firestore rules)
- **User token:** `users/{email}.pcgsToken` (user self-managed fallback)
- **Priority:** platform -> user personal -> error
- Tokens are never logged or exposed in Flutter client code

### 7.4 GCS Access
- Reference images: public CDN (`cache-control: public, max-age=31536000`)
- User microscope uploads: authenticated via service account key file

---

## 8. External Integrations

| Service | Purpose | Auth Method |
|---------|---------|-------------|
| **PCGS Public API** | Coin facts by cert# or PCGS#; auction prices | Bearer token (Firestore-managed) |
| **eBay Partner Network (EPN)** | Live listing prices on wishlist items | API key stored in Firestore `config/epn` |
| **NewsAPI** | Numismatic news feed on home dashboard | API key stored in Firestore |
| **Google Cloud Storage** | Reference coin images; microscope captures | Service account / ADC |
| **Cloud Firestore** | Primary database, real-time listeners | Firebase SDK (authenticated) |
| **Firebase Auth** | User authentication, session management | Firebase SDK |

---

## 9. Deployment Architecture

### 9.1 Cloud Run Services

| Service | Source Directory | Trigger |
|---------|-----------------|---------|
| `scan-service` | `numista_backend/scan_service/` | HTTPS POST from Flutter web |
| `sync-worker` | `numista_backend/sync_worker/` | Background / Cloud Scheduler |
| `main-app` | `numista_backend/` (app.py) | Internal admin use |

Build pipeline: `cloudbuild.yaml`
Registry: Google Artifact Registry (project-scoped)

### 9.2 Flutter Web Hosting

Flutter web build deployed to **Firebase Hosting** (`firebase.json` + `.firebaserc`).

### 9.3 Hardware Agent Distribution

- Packaged as a Windows `.exe` via PyInstaller (`NumistaAgent.spec`)
- Auto-starts with Windows via Task Scheduler (`install_agent.ps1`)
- System tray integration via `tray_agent.py`

### 9.4 Daily Automated Backup

- **Script:** `numista_auto_backup.ps1` (project root)
- **Schedule:** Windows Task Scheduler -- daily at 7:00 PM
- **Target:** `github.com/Numista-AI/Numista.AI` (main branch)
- **Behavior:** Stages all changes, commits with timestamp, pushes to GitHub
- **Fallback:** `StartWhenAvailable` ensures backup runs if machine was off at 7 PM
- **Log:** `numista_backup.log`

---

## 10. Known Limitations & Future Work

### Current Limitations

| Area | Limitation |
|------|-----------|
| Hardware agent | `USER_EMAIL` hardcoded -- single-user only today |
| PCGS proxy | Cert# lookup routes through Cloud Run; fragile if service is down |
| Checklist scan | Multi-page scans processed sequentially, not in parallel |
| AI Chat | No persistent conversation history across sessions |
| Mobile (iOS) | Full distribution requires physical Apple hardware + developer account |
| Reference images | ~4.5M row GCS index; image coverage is partial for rare coins |

### Planned Improvements

- [ ] Multi-user hardware agent (dynamic user ID from Firebase Auth)
- [ ] Parallel multi-page checklist scanning
- [ ] AI Chat session persistence (Firestore-backed conversation history)
- [ ] Deep Dive AI reports (Gemini Pro for detailed numismatic analysis)
- [ ] Human-AI Trainer screen (collect corrections to improve scan accuracy)
- [ ] eBay snipe/alert integration for wishlist items
- [ ] iOS App Store distribution
- [ ] Real-time shared collections (multi-user collaboration)
