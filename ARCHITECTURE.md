# Numista.AI — System Architecture Overview

> **Version:** August 2026 | **Author:** Numista Engineering & Architecture Team | **Status:** Production / Live Beta MVP

---

## Table of Contents
1. [System Overview](#1-system-overview)
2. [Module Inventory & Repository Structure](#2-module-inventory--repository-structure)
3. [Layer-by-Layer Architecture](#3-layer-by-layer-architecture)
   - [3.1 Frontend — `numista_mobile` (Flutter)](#31-frontend--numista_mobile-flutter)
   - [3.2 Cloud Backend — `numista_backend` (FastAPI)](#32-cloud-backend--numista_backend-fastapi)
   - [3.3 Desktop Hardware Agent — `numista_hardware` (Python)](#33-desktop-hardware-agent--numista_hardware-python)
   - [3.4 Data Warehouse & Analytics — `numista_bq_loader_job`](#34-data-warehouse--analytics--numista_bq_loader_job)
4. [Data Architecture & Schemas](#4-data-architecture--schemas)
   - [4.1 Firestore NoSQL Collections](#41-firestore-nosql-collections)
   - [4.2 Relational & Reference Catalog (`numista_coins.db`)](#42-relational--reference-catalog-numista_coinsdb)
   - [4.3 BigQuery Data Warehouse](#43-bigquery-data-warehouse)
   - [4.4 Cloud Storage (GCS Bucket)](#44-cloud-storage-gcs-bucket)
5. [Core Functional Pipelines & Data Flows](#5-core-functional-pipelines--data-flows)
   - [5.1 Multimodal Gemini AI Photo Identification](#51-multimodal-gemini-ai-photo-identification)
   - [5.2 USB Microscope Auto-Capture & Pair Loop](#52-usb-microscope-auto-capture--pair-loop)
   - [5.3 Valuations: Greysheet, PCGS Proxy, and Spot Metals](#53-valuations-greysheet-pcgs-proxy-and-spot-metals)
   - [5.4 Estate Planning & Attorney Portal Division Solver](#54-estate-planning--attorney-portal-division-solver)
   - [5.5 Document AI PDF Invoice & Checklist Processing](#55-document-ai-pdf-invoice--checklist-processing)
   - [5.6 Human-in-the-Loop (HITL) AI Training & Feedback Loop](#56-human-in-the-loop-hitl-ai-training--feedback-loop)
6. [AI Infrastructure & Prompt Recovery](#6-ai-infrastructure--prompt-recovery)
7. [Security & Authentication Model](#7-security--authentication-model)
8. [External System Integrations](#8-external-system-integrations)
9. [Deployment & CI/CD Pipelines](#9-deployment--cicd-pipelines)
10. [August 2026 Architecture Evolution & Future Roadmap](#10-august-2026-architecture-evolution--future-roadmap)

---

## 1. System Overview

**Numista.AI** is a comprehensive, cross-platform numismatic management, collection tracking, and AI-assisted coin authentication ecosystem. The system bridges mobile devices, web browsers, specialized local desktop hardware (USB microscope stations), and Google Cloud Platform services.

### Key Capabilities
- **Multimodal AI Coin Identification**: Obverse and reverse high-resolution image analysis using Google Gemini 3.5 / Gemini Vision AI to identify coin series, year, mint mark, variety, and grade estimation.
- **Universal Ingestion Hub**: Seamless onboarding via bulk Excel/CSV import, PCGS cert search, PDF invoice parsing (Google Document AI), manual wizard forms, and high-resolution USB microscope capture.
- **Hybrid Real-Time Valuation Engine**: Multi-tiered pricing combining live bullion spot prices (yfinance), Greysheet CPG wholesale/retail catalog cache, PCGS certification proxy, and eBay sold listing analytics.
- **Estate Planning & Attorney Portal**: Algorithmic estate division (greedy LPT partition solver with valuation offset compensation), executor inheritance access management, and automated export of legal-grade Numismatic Passports (PDF).
- **USB Microscope Hardware Integration**: Local background Windows desktop agent (`numista_hardware`) featuring stability detection, automated auto-capture, local GCS upload, and instant Firestore pairing.
- **Human-in-the-Loop (HITL) AI Trainer**: Interactive grading dispute resolution and AI visual dataset annotation interface.

### High-Level System Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                  numista_mobile                                   |
|                          Flutter Web / Android / iOS App                          |
|             (User Portal, Collection Grid, AI Chat, Estate Manager)               |
+-----------------------------------------+-----------------------------------------+
                                          | Firebase Auth & Firestore SDK
                                          | REST API Requests (Bearer Token)
+-----------------------------------------v-----------------------------------------+
|                              Google Cloud Platform                                |
|  +---------------------+  +--------------------------+  +----------------------+  |
|  | Cloud Firestore     |  | Cloud Run (FastAPI)      |  | Cloud Storage (GCS)  |  |
|  | (Primary NoSQL DB)  |  | - modular APIRouters     |  | (Images & Invoices)  |  |
|  | - users/{uid}/coins |  | - PCGS & Greysheet Proxy |  | studio-9101802118-   |  |
|  | - staging_area      |  | - PDF / Document AI      |  | 8c9a8-uploads        |  |
|  +---------------------+  +--------------------------+  +----------------------+  |
|  +-----------------------------------------------------------------------------+  |
|  | Gemini 3.5 Vision AI / Vertex AI (Image ID, Chat, Grade Audit)               |  |
|  +-----------------------------------------------------------------------------+  |
|  +-----------------------------------------------------------------------------+  |
|  | BigQuery Data Warehouse (Nightly ETL, Market Analytics & Trends)             |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------+-----------------------------------------+
                                          | Firestore Listener / Local HTTPS API
+-----------------------------------------v-----------------------------------------+
|                                 numista_hardware                                  |
|                 Windows Tray Desktop Agent (Python / Flask / OpenCV)              |
|        USB Microscope -> Stability Capture -> GCS Upload -> Firestore Sync        |
+-----------------------------------------------------------------------------------+
```

---

## 2. Module Inventory & Repository Structure

| Module Directory | Core Tech Stack | Runtime Platform | Role / Responsibilities |
|------------------|-----------------|------------------|-------------------------|
| `numista_mobile` | Dart, Flutter 3.x, Firebase SDK | Web, Android, iOS | Primary user-facing application frontend |
| `numista_backend` | Python 3.11, FastAPI, Pydantic | GCP Cloud Run | Core REST API, AI pipelines, PCGS/Greysheet proxy, Document AI invoice parser |
| `numista_hardware` | Python 3.11, OpenCV, Flask, PyInstaller | Windows Desktop | USB microscope capture agent, motion stability engine, local pairing agent |
| `numista_bq_loader_job` | Python, BigQuery Client | Cloud Run Jobs / Cron | ETL pipeline serializing Firestore records into BigQuery analytical tables |
| `numista_admin` & `numista_qa_runner` | Node.js, Playwright, Pytest | CI/CD & Local | Automated E2E test runner, Playwright smoke tests, nightly audit reporter |

### GCP Production Environment Details
- **GCP Project ID**: `studio-9101802118-8c9a8`
- **Primary GCS Bucket**: `studio-9101802118-8c9a8-uploads`
- **Cloud Run Primary Region**: `us-central1`
- **Production API Gateway**: `https://numista-backend-568985927038.us-central1.run.app`
- **Checklist Scan Service**: `https://scan-service-568985927038.us-central1.run.app`
- **Live Web Frontend**: `https://numista-vault.web.app` / `https://numista.ai`

---

## 3. Layer-by-Layer Architecture

### 3.1 Frontend — `numista_mobile` (Flutter)

The frontend is built using Flutter for cross-platform deployment across Web, Android, and iOS.

#### Screen Inventory & Functionality

```
lib/screens/
├── add_coins_hub.dart               # Multi-tab ingestion wizard (Manual, AI Photo ID, PCGS Cert, Spreadsheet)
├── add_world_item_screen.dart       # World coinage & ancient coin entry interface
├── admin_feedback_screen.dart       # Admin dashboard for user feedback review
├── admin_grade_flags_screen.dart    # Flagged AI grade audit review panel
├── ai_chat_screen.dart              # Interactive Gemini numismatic chat assistant
├── attorney_portal_screen.dart      # Attorney & estate executor read-only audit & inheritance portal
├── base_layout.dart                 # Responsive shell with sidebar, topbar, and drawer navigation
├── coa_inspector_screen.dart        # Certificate of Authenticity (COA) visual inspection tool
├── coin_detail_screen.dart          # Deep coin view: photos, Greysheet pricing, grade history, notes
├── coin_search_screen.dart          # High-performance search across full catalog & personal collection
├── currency_collection_screen.dart  # Banknotes, paper money, CSA notes, & obsolete currency collection
├── customer_service_screen.dart     # Support ticketing, knowledge base, & FAQ
├── deals_screen.dart                # Live Deal Spotter (arbitrage opportunities vs Greysheet/metal prices)
├── desktop_agent_download_screen.dart# USB Microscope desktop installer download & status pairing widget
├── estate_planning_screen.dart      # Estate allocation simulator (LPT partition) & PDF Passport generator
├── family_settings_screen.dart      # Sub-account management & family sharing controls
├── glossary_academy_screen.dart     # Interactive numismatic glossary & grading guide academy
├── home_dashboard.dart              # Portfolio overview, spot prices ticker, quick AI prompt shortcuts
├── human_ai_trainer_screen.dart     # Human-in-the-loop AI model fine-tuning & annotation tool
├── lateral_transfer_screen.dart     # Inter-user/family coin transfer initiator
├── login_screen.dart                # Firebase Auth (Email/Password + Google Sign-In)
├── microscope_scan_screen.dart      # Live microscope feed, trigger capture, real-time pairing status
├── mint_error_detail_screen.dart    # Detailed error coin breakdown (doubled die, off-center, clipped)
├── mint_error_library_screen.dart   # US Mint rare error coin catalog & diagnostic guide
├── my_collection_screen.dart        # Main collection table/grid with filters, sorting, bulk actions
├── program_manager_screen.dart      # US Mint coin program progress checklist browser
├── public_wishlist_view_screen.dart # Shareable public wish list view for gift-givers/traders
├── review_hub_screen.dart           # Staging area audit queue for batch PDF/CSV/Microscope scans
├── settings_screen.dart             # Profile, PCGS token setup, default grading service preferences
├── supplies_screen.dart             # Recommended numismatic storage flips, capsules, and tools
└── wishlist_screen.dart             # Personal wish list with live eBay affiliate price integration
```

### 3.2 Cloud Backend — `numista_backend` (FastAPI)

The backend is modularized into FastAPI `APIRouter` modules located in `numista_backend/routes/`:

```
numista_backend/
├── main.py                          # FastAPI app entry point, middleware, CORS, lifecycle setup
├── config.py                        # Environment variables, GCP settings, credential validation
├── routes/
│   ├── ai_routes.py                 # Gemini Vision coin ID, chat completion, AI report generation
│   ├── collection_routes.py         # Collection CRUD, bulk status updates, image assignment
│   ├── grade_review_routes.py       # AI grade verification, human-in-the-loop dispute logging
│   ├── import_routes.py             # CSV/Excel parsing, staging batch commits
│   ├── news_routes.py               # Numismatic news feed aggregator & US Mint updates
│   ├── payment_routes.py            # Stripe checkout, subscription tier entitlement gatekeeper
│   ├── pcgs_routes.py               # PCGS API cert lookup, price guide proxy, rate limiter
│   ├── scan_routes.py               # Document AI invoice scanning & checklist OCR
│   ├── subaccount_routes.py         # Family sub-account delegation & authorization
│   └── valuation_routes.py          # Greysheet CPG wholesale lookup, yfinance metal spot calculation
├── services/
│   ├── canon_sync_service.py        # SQLite catalog to Firestore reference synchronizer
│   ├── deal_spotter_service.py      # Market arbitrage & deal spotter scoring algorithm
│   ├── greysheet_service.py         # Greysheet pricing API client, caching, and fallback logic
│   ├── greysheet_quota_service.py   # Daily Greysheet API quota tracking & throttling
│   ├── mint_nomenclature_service.py # Standardized coin title & denomination normalizer
│   ├── passport_pdf_generator.py    # ReportLab PDF generator for legal Numismatic Passports
│   ├── transfer_service.py          # Inter-account coin transfer state machine
│   └── variety_detector.py          # Visual variety & die error detection heuristic engine
└── scrapers/                        # Automated scrapers for catalog enrichment & price updates
```

### 3.3 Desktop Hardware Agent — `numista_hardware` (Python)

The desktop agent provides zero-click USB microscope integration for collectors:

- **Stability & Motion Detection Engine (`auto_capture.py`)**: Uses OpenCV (`cv2.absdiff`) to detect when a coin is placed under the microscope lens and held stationary for 1.2 seconds.
- **Auto-Capture & Crop**: Automatically crops bounding boxes, balances color temperature, and generates high-resolution PNG uploads.
- **Cloud Direct Ingestion**: Uploads obverse/reverse captures directly to GCS (`studio-9101802118-8c9a8-uploads`) and posts record updates to Firestore `staging_area`.
- **Local HTTPS Server & Tray Agent (`tray_agent.py`)**: Runs a lightweight Flask HTTPS listener on `localhost:8443` secured with local SSL certificates (`localhost.crt`) for direct browser-to-hardware communication.
- **Executable Distribution**: Packaged via PyInstaller into `NumistaAgent.exe` and delivered with an NSIS installer (`NumistaAgentSetup.exe`).

---

## 4. Data Architecture & Schemas

### 4.1 Firestore NoSQL Collections

```
Firestore Root
├── users/{userId}/
│   ├── coins/{coinId}              # User coin items (Golden Coin Schema)
│   ├── wishlist/{itemId}           # User wish list items
│   ├── subaccounts/{subId}         # Delegated family/executor accounts
│   ├── estate_plans/{planId}       # Saved estate division configurations
│   └── notifications/{notifId}     # System alerts & transfer inbox
├── staging_area/{stagingId}        # Staged scans awaiting user audit/commit
├── program_checklists/{programId}  # Canonical US Mint program definitions & slots
├── reference_catalog/{numistaId}   # Synchronized canonical catalog items
└── scraped_coins/{scrapeId}        # Raw scraper market listings & deal spotter candidates
```

#### Firestore Golden Coin Schema (`coin-schema.json`)

```json
{
  "coin_id": "string (UUID v4)",
  "title": "string (e.g. '1921 Morgan Silver Dollar')",
  "country": "string (e.g. 'United States')",
  "denomination": "string (e.g. '$1')",
  "year": "integer (e.g. 1921)",
  "mint_mark": "string (e.g. 'S', 'D', 'P', or '')",
  "series": "string (e.g. 'Morgan Dollar')",
  "variety": "string (e.g. 'VAM-1A')",
  "grade": "string (e.g. 'MS-65')",
  "grading_service": "string (e.g. 'PCGS', 'NGC', 'Raw')",
  "cert_number": "string",
  "purchase_price": "number",
  "estimated_value": "number",
  "greysheet_value": "number",
  "melt_value": "number",
  "obverse_image_url": "string (GCS URL)",
  "reverse_image_url": "string (GCS URL)",
  "is_silver": "boolean",
  "is_gold": "boolean",
  "weight_grams": "number",
  "purity": "number",
  "review_status": "string ('pending' | 'approved' | 'rejected')",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### 4.2 Relational & Reference Catalog (`numista_coins.db`)

A local SQLite database (`numista_coins.db`) serves as the offline reference authority for:
- 150+ US Mint programs (State Quarters, Presidential Dollars, Morgan Dollars, American Silver Eagles, etc.)
- Mintage figures, metal compositions, diameter, weight, and standard PCGS CoinFacts mapping.
- Synced automatically to Firestore `reference_catalog` via `canon_sync_service.py`.

### 4.3 BigQuery Data Warehouse

The `numista_bq_loader_job` runs automated ETL routines loading Firestore collections into BigQuery dataset `numista_analytics`:
- **`fact_collection_snapshot`**: Nightly user collection valuations, composition metrics, and growth trends.
- **`dim_coin_catalog`**: Master coin reference dimensions.
- **`fact_market_prices`**: Historical Greysheet and metal spot prices.

---

## 5. Core Functional Pipelines & Data Flows

### 5.1 Multimodal Gemini AI Photo Identification

```
[User App / Microscope]
        | (Upload Obverse & Reverse Photos)
        v
 [Google Cloud Storage] ---> GCS Public / Signed URLs
        |
        v
 [numista_backend: ai_routes.py]
        |
        +---> Construct Multimodal Prompt (System rules + JSON schema enforce)
        |
        v
 [Gemini 3.5 Vision API]
        |
        +---> Raw Text / JSON Response
        |
        v
 [JSON Recovery & Sanitizer Engine] ---> Enforces numeric years, standard grade strings
        |
        v
 [Firestore Staging / Collection]
```

### 5.2 USB Microscope Auto-Capture & Pair Loop

```
1. User opens numista_mobile -> Microscope Scan Screen.
2. App queries Desktop Agent local HTTPS server at https://localhost:8443/status.
3. User places coin under USB Microscope.
4. Agent auto_capture.py detects image stability (OpenCV frame diff threshold < 0.02 for 1.2s).
5. Agent crops image, uploads obverse_image.png to GCS.
6. User flips coin -> Agent captures reverse_image.png to GCS.
7. Agent posts payload to Cloud Run /api/v1/scan/microscope-commit.
8. Real-time Firestore listener updates Flutter UI instantly.
```

### 5.3 Valuations: Greysheet, PCGS Proxy, and Spot Metals

```
                  +-----------------------------------+
                  |  Valuation Request for Coin Item  |
                  +-----------------+-----------------+
                                    |
            +-----------------------+-----------------------+
            |                       |                       |
            v                       v                       v
   [Is Certified PCGS?]    [Has Greysheet Match?]    [Is Precious Metal?]
            |                       |                       |
            v                       v                       v
   [pcgs_routes.py Proxy]   [greysheet_service.py]   [yfinance Spot API]
   (PCGS Bearer Token)     (Wholesale CPG Cache)   (Gold/Silver $/oz)
            |                       |                       |
            +-----------------------+-----------------------+
                                    |
                                    v
                    [Combined Valuation Hierarchy]
                1. Cert Exact Match (PCGS/NGC Guide)
                2. Greysheet CPG Wholesale/Retail
                3. Calculated Bullion Melt Value
                4. User Manual Estimate
```

### 5.4 Estate Planning & Attorney Portal Division Solver

```
1. Collection loaded into memory as valuation matrix.
2. Executor inputs N Heirs & Target Percentage splits.
3. Greedy LPT (Longest Processing Time First) Partitioning Algorithm distributes coins.
4. Valuation offset compensations calculated for exact dollar parity.
5. ReportLab engine in passport_pdf_generator.py builds downloadable legal PDF ("Numismatic Passport").
6. Attorney Portal link generated with time-bound read-only view permission.
```

---

## 6. AI Infrastructure & Prompt Recovery

- **Primary Models**: `gemini-3.5-flash` (fast visual ID & chat), `gemini-3.5-pro` (complex variety analysis & audit reports).
- **SDK**: `google-genai` Python SDK (v1.71+).
- **JSON Recovery Architecture**: If Gemini returns invalid JSON or markdown-fenced text, backend `ai_routes.py` executes a multi-pass regex extractor and schema fallback normalizer to prevent downstream crashes.

---

## 7. Security & Authentication Model

- **User Authentication**: Firebase Authentication (Email/Password, Google OAuth). JWT ID tokens validated on every FastAPI request via `deps.py`.
- **Database Rules**: Firestore security rules restrict write operations strictly to authenticated document owners (`request.auth.uid == userId`).
- **GCS Storage Rules**: Public read access restricted to user images; invoice PDFs locked to user authorization tokens.
- **PCGS Token Security**: `PCGS_BEARER_TOKEN` stored securely in GCP Secret Manager / Environment variables, accessed exclusively by backend proxy routes.
- **Hardware Local Agent Security**: Local HTTPS listener uses TLS certificates to prevent browser mixed-content blocks during local pairing.

---

## 8. External System Integrations

| External System | Purpose / Functionality | Integration Endpoint / Protocol |
|-----------------|-------------------------|---------------------------------|
| **Google Gemini API** | Multimodal coin ID, visual grading, AI chat | Vertex AI / GenAI SDK (`google-genai`) |
| **PCGS API** | Cert lookup, population report, price guide | REST HTTPS (Bearer Token Auth Header) |
| **Greysheet API** | CPG wholesale & retail coin pricing catalog | REST API with quota monitoring service |
| **yfinance** | Real-time Gold, Silver, Platinum, Palladium spot prices | Python `yfinance` market data stream |
| **Google Document AI** | PDF invoice & tabular checklist OCR extraction | GCP Document AI REST / Client SDK |
| **eBay Partner Network** | Live market listings & affiliate link generation | eBay Finding & Shopping APIs |
| **Stripe** | Subscription billing & tier entitlement gating | Stripe Webhooks & SDK (`stripe_config.py`) |

---

## 9. Deployment & CI/CD Pipelines

### GitHub Actions Workflow Overview

```
[Git Push to 'dev' or 'main']
             |
             v
+-------------------------------------------------------------+
| GitHub Actions Workflows                                    |
|  - CI — Dev Branch (Pytest + Flutter Build)                 |
|  - Numista.AI Automated Tests (Playwright E2E Test Suite)   |
|  - CodeQL Security Analyzer                                 |
|  - Deploy to numista.ai (Triggered on 'main' push)          |
+------------------------------+------------------------------+
                               |
            +------------------+------------------+
            |                                     |
            v                                     v
 [Firebase Web Hosting]                 [GCP Cloud Run]
 (numista-vault.web.app)                (numista-backend container)
```

### Git Branch & Push Rules
- **`dev` branch**: Primary development branch. CI/CD runs automated test suites on PR open/update.
- **`main` branch**: Production deployment branch. Pushing to `main` deploys live to `numista-vault.web.app` and Cloud Run.
- **Strict Protection Rule**: Pushing directly to `main` requires explicit user authorization (refer to workspace `AGENTS.md` Rule 7).

---

## 10. August 2026 Architecture Evolution & Future Roadmap

### Recent August 2026 Milestone Upgrades
1. **FastAPI Route Modularization**: Refactored monolithic `main.py` into dedicated APIRouter domain modules (`pcgs`, `news`, `payment`, `grade_review`, `import`, `valuation`, `scan`, `ai`, `collection`, `subaccount`).
2. **Currency & Banknotes Expansion**: Native data schemas, UI screens (`currency_collection_screen.dart`), and specialized catalog mappings for US paper money, obsolete banknotes, and CSA notes.
3. **Estate Division & Legal Attorney Portal**: Complete inheritance solver engine with ReportLab legal PDF passport output.
4. **Greysheet & PCGS Resilient Valuation Tier**: Tiered fallback valuation engine with daily quota tracking and automated fallback to bullion spot prices.
5. **Human-in-the-Loop AI Trainer**: Integrated visual feedback loop for human audit of AI identification anomalies.

### Future Architectural Roadmap
- **Edge AI Mobile Scanning**: On-device TensorFlow Lite / CoreML model inference for offline coin identification.
- **Full BigQuery Predictive Analytics**: Advanced machine learning price forecasting using BigQuery ML on historical Greysheet trends.
- **3D Coin Topography Scanner**: Support for specialized 3D depth-sensing hardware stations.
