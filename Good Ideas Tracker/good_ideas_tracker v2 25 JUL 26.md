# Numista.AI — Good Ideas Tracker & Feature Master Plan

*Last Updated: July 25, 2026 (Sprint 1 Completed)*  
*Target Release Horizon: Desktop Beta (Aug 2026) → Live Desktop Launch (Nov 2026) → Mobile App Store (Feb 2027)*

---

## 📌 Executive Summary & Overall Progress

The **Good Ideas Tracker** aggregates every feature, ability, architectural pattern, monetization strategy, and user experience requirement documented across all project notes, transcripts, session reports, and specifications within `C:\Users\ericd\Documents\MyVertexProject`.

```
========================================================================================
                                 OVERALL COMPLETION STATUS
========================================================================================
 [████████████████████████████████████████████████████████░░░░░░░░░░░░░░░░░░] 66.7%
========================================================================================
 Total Features Identified: 54
 🟢 Completed (Fully Built & Live): 31 (57.4%)
 🟡 Partially Completed (In Progress / Partial UI or Service): 10 (18.5%)
 🔴 Not Started (Documented & Planned): 13 (24.1%)
========================================================================================
```

---

## 📊 Summary by Category

| # | Feature Category | Total Items | 🟢 Done | 🟡 Partial | 🔴 Not Started | Completion % |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **1** | Core Collection & Inventory Management | 6 | 5 | 1 | 0 | **91.7%** |
| **2** | AI & Vision Systems (Grading, Identification, Chat) | 5 | 3 | 2 | 0 | **80.0%** |
| **3** | Data Ingestion & Import Wizards | 7 | 7 | 0 | 0 | **100.0%** |
| **4** | Microscope & Hardware Integration | 5 | 2 | 2 | 1 | **60.0%** |
| **5** | Estate Planning & Legal Reports | 5 | 2 | 2 | 1 | **60.0%** |
| **6** | Reference Library & Coin Programs | 6 | 3 | 2 | 1 | **66.7%** |
| **7** | Wish List, Monetization & E-Commerce | 5 | 2 | 2 | 1 | **60.0%** |
| **8** | User Accounts, Security & Family Access | 5 | 3 | 1 | 1 | **70.0%** |
| **9** | UI/UX, Onboarding & Appearance | 6 | 3 | 1 | 2 | **58.3%** |
| **10** | Data Engineering, Scrapers & Infrastructure | 4 | 1 | 1 | 2 | **37.5%** |
| **TOTAL** | **All Categories Combined** | **54** | **31** | **10** | **13** | **66.7%** |

---

## 📑 Feature Trackers by Category

### 1. Core Collection & Inventory Management

| Feature / Ability | Description & User Requirements | Status | Progress | Primary File / Location |
|---|---|:---:|:---:|---|
| **Firestore Multi-Coin Storage** | Scalable storage supporting 7,000+ coins per user subcollection without layout or memory lag. | 🟢 Completed | 100% | [my_collection_screen.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart) |
| **Split Year & Mint Columns** | Separate `Year` and `Mint Mark` columns without redundant text (e.g. `2025-W` + `W`), while allowing independent sorting. | 🟢 Completed | 100% | [my_collection_screen.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart) |
| **Multi-View Sidebar Structure** | Sub-views under "My Collection": Coins, Currency, World & Specialty, and All Items. | 🟢 Completed | 100% | [base_layout.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/base_layout.dart) |
| **Currency & World Collections** | Dedicated tracking screens for paper banknotes, confederate bills, and foreign items. | 🟢 Completed | 100% | [currency_collection_screen.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/currency_collection_screen.dart) |
| **Sticky Column Headers (Freeze Top Row)** | Excel-like freeze pane headers (`TableView.builder`) when scrolling through large collections (thousands of items). | 🟢 Completed | 100% | [my_collection_screen.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart) |
| **Cloud SQL / PostgreSQL Migration Option** | Architectural alternative for complex relational queries (e.g. "Silver 1850-1900 > AU50") and full-text search. | 🟡 Partial | 30% | [Gemini Suggestions, 26 FEB 26.docx](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Gemini%20Suggestions,%2026%20FEB%2026.docx) |

---

### 3. Data Ingestion & Import Wizards

| Feature / Ability | Description & User Requirements | Status | Progress | Primary File / Location |
|---|---|:---:|:---:|---|
| **Add Coins Hub (7-Tab Import)** | Unified entry hub supporting PDF, CSV, PCGS Cert, Manual, Checklist, Roll/Batch, and Photo options. | 🟢 Completed | 100% | [add_coins_hub.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/add_coins_hub.dart) |
| **PCGS Certificate API Verification** | Live PCGS cert lookup returning grade, holder status, NFC anti-counterfeiting flag, and direct web link. | 🟢 Completed | 100% | [pcgs_import_service.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/pcgs_import_service.dart) |
| **Roll / Batch Entry Wizard** | Multi-roll wizard handling identical rolls, sequential rolls, and mint-mark lots. | 🟢 Completed | 100% | [add_coins_hub.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/add_coins_hub.dart#L1000) |
| **Checklist Photo OCR Ingestion** | Extracting checked items from physical Littleton/US Mint paper checklists. | 🟢 Completed | 100% | [checklist_scan_service.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/checklist_scan_service.dart) |
| **CSV / Excel Smart Column Mapper** | Auto-mapping user spreadsheet headers (Year, Denomination, Grade, Purchase Price). | 🟢 Completed | 100% | [add_coins_hub.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/add_coins_hub.dart#L500) |
| **Review Hub Bulk Approval** | Pending queue for AI-extracted coins allowing single-click or batch approval/rejection. | 🟢 Completed | 100% | [review_hub_screen.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/review_hub_screen.dart) |
| **Dual-Column PCGS/NGC/ANACS/CAC Schema** | Storing `Grading Service` + `Certification Number` separately with live verification pop-up links (PCGS, NGC, ANACS, CAC, CACG). | 🟢 Completed | 100% | [coin_model.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/models/coin_model.dart) |

---

### 8. User Accounts, Security & Family Access

| Feature / Ability | Description & User Requirements | Status | Progress | Primary File / Location |
|---|---|:---:|:---:|---|
| **Firebase Authentication Flow** | Complete sign-up, sign-in, and password reset flows. | 🟢 Completed | 100% | [login_screen.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/login_screen.dart) |
| **Firestore Security Rules Isolation** | Restricting `users/{email}/coins` access strictly to authenticated owners. | 🟢 Completed | 100% | [security_triage.md](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/BETA%20TEST/MY%20TESTING/8%20JUL%2026/security_triage.md) |
| **Guest Mode & Demo Collection** | Guest experience pre-seeded with **100 representative demo items** across Coins, Currency, and World items. | 🟢 Completed | 100% | [guest_seed_service.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/guest_seed_service.dart) |
| **Custodian & Family Sub-Accounts** | Parent-managed sub-accounts allowing children or collectors' heirs to build collections under one roof. | 🟡 Partial | 30% | [custodian_accounts_research.md](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Pricing/custodian_accounts_research.md) |
| **JSON Collection Backup & Local Export** | One-click JSON backup export allowing users to download their full collection off-platform. | 🔴 Not Started | 0% | [settings_screen.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/settings_screen.dart) |

---

### 9. UI/UX, Onboarding & Appearance

| Feature / Ability | Description & User Requirements | Status | Progress | Primary File / Location |
|---|---|:---:|:---:|---|
| **Refined Theme (Owl Logo Blue Palette)** | Modern white/light-gray theme with vibrant blue accents matching the Numista owl identity. | 🟢 Completed | 100% | [theme_provider.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/theme_provider.dart) |
| **Live Metal Spot Prices Header** | Real-time Silver, Gold, Platinum spot rates with timestamp ("Last Update: HH:MM EST"). | 🟢 Completed | 100% | [home_dashboard.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/home_dashboard.dart#L120) |
| **Interactive Onboarding Wizard** | 5-step interactive walk-through introducing new users to every tool + dismissible 7-entry-method banner. | 🟢 Completed | 100% | [wizard_service.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/services/wizard_service.dart) |
| **Market Intel Numismatic News Feed** | Curated news feed drawing twice daily from top 5 numismatic publications (CoinWorld, Numismatic News, US Mint, etc.). | 🟡 Partial | 30% | [home_dashboard.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/home_dashboard.dart#L400) |
| **Secondary Screen & Ultra-Wide Layout** | Compact top/side nav bars maximizing central workspace for dual-monitor power users. | 🔴 Not Started | 0% | [PCGS V2.docx](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Individual%20Pages%20of%20Numista.ai/PCGS%20V2.docx) |
| **COA (Certificate of Authenticity) Inspector** | Document scanner and verification tab dedicated to raw COAs and mint packaging. | 🔴 Not Started | 0% | [COA Review 29 APR 26.docx](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/Individual%20Pages%20of%20Numista.ai/COA%20Review%2029%20APR%2026.docx) |
