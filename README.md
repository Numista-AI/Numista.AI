# Numista.AI — AI-Powered Numismatic Collection Manager

Welcome to **Numista.AI**, a comprehensive collection management and AI-powered valuation ecosystem for coin and banknote collectors. 

This repository contains the mobile app, admin portal, scraping scripts, and database operations that power the Numista.AI ecosystem.

---

## 📂 Repository Structure

The workspace is organized into the following main directories:

```
numista.ai/
├── numista_mobile/        # Flutter Web/Mobile Application (Frontend)
├── numista_admin/         # Next.js & TypeScript Admin Portal
├── numista_backend/       # Python backend (Scrapers, APIs, AI processing)
│   ├── scrapers/          # [NEW] Versioned JS scraping scripts
│   ├── data/              # [NEW] Raw data CSVs, checklists, and references
│   ├── database/          # SQLite database caches (numista_coins.db)
│   ├── services/          # Services for Greysheet, PCGS, and Smithsonian APIs
│   ├── _scripts/          # Maintenance, database audits, and ingestion utilities
│   └── main.py            # Primary Cloud Run entry point (Python API)
├── scratch/               # Local logs, test outputs, and temporary files (Git-ignored)
└── DEVELOPER_ONBOARDING.md # Developer guide for local setup and operations
```

---

## 🛠️ System Components

### 1. Frontend: Mobile & Web App (`numista_mobile/`)
* **Technology**: Flutter (Dart)
* **Hosting**: Firebase Hosting (`numista-vault.web.app`)
* **Key Features**: Personal collection visualization, valuation charts, AI guide ("Ask Morgan" chat), estate report generation, and wishlist eBay deal spotter.

### 2. Admin Portal (`numista_admin/`)
* **Technology**: Next.js (TypeScript), TailwindCSS
* **Key Features**: Moderation dashboard, user flags, manual grade verification queue, scraping scheduler, and system analytics.

### 3. Backend Services (`numista_backend/`)
* **Technology**: Python (FastAPI / Flask), Google Vertex AI (Gemini 2.5/3.5)
* **Hosting**: Google Cloud Run
* **Key Features**: Ingests collection invoices via Document AI, auto-categorizes coins, matches items to the Greysheet API for pricing, fetches reference images, and builds PDF estate reports.

---

## 💾 Database Architecture

* **Firestore**: The primary live database.
  - `users/{email}/coins`: User coin collections (including image URLs, costs, and valuations).
  - `users/{email}/currency`: User paper money collections.
  - `config/*`: Global config (API tokens, active proxy list, scraper locks).
* **SQLite (`numista_backend/database/numista_coins.db`)**: Local reference database containing standardized coin details, NGC/PCGS lookup mappings, and catalog details.

---

## 🚀 Key Workflows

### Running Locally
To run the components locally, consult [DEVELOPER_ONBOARDING.md](file:///C:/Users/ericd/Documents/MyVertexProject/DEVELOPER_ONBOARDING.md).

### Deploying changes
1. **Frontend**: Code changes must be pushed to `dev` first, verified via Firebase preview channels, and then merged to `main` for production deploy.
2. **Backend**: Deployed to Google Cloud Run via `gcloud run deploy`.

---

*See [DEVELOPER_ONBOARDING.md](file:///C:/Users/ericd/Documents/MyVertexProject/DEVELOPER_ONBOARDING.md) to get started as a developer.*
