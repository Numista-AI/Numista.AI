# Good Ideas Tracker — Part 2 (July 27, 2026 – August 4, 2026)

*Master Feature, Usability, and Architecture Tracker for Numista.AI Desktop Beta*  
*Period Covered: July 27, 2026 – August 4, 2026*  
*Total Items Tracked: 60*

---

## 📊 Summary Dashboard

```
========================================================================================
                 GOOD IDEAS TRACKER PART 2 (JULY 27 - AUGUST 4, 2026)
========================================================================================
 [████████████████████████████████████████████████████████████████████████] 100.0%
========================================================================================
 Total Items Tracked: 60
 🟢 Completed & Verified on Dev: 60 (100.0%)
 🟡 In Progress / Partial: 0 (0.0%)
 🔴 Open / Pending: 0 (0.0%)
========================================================================================
```

---

## 1. 💰 Greysheet Advanced Tier ($343/mo) & Wholesale Pricing Engine

| ID | Feature / Idea | Description | Origin | Status | Location / Details |
|:---|:---|:---|:---|:---:|:---|
| **GS-01** | **Advanced Tier Data Inventory** | Integrate full dataset unlocked in `apiLevel=advanced`: Wholesale Bid (`GreyVal`), Wholesale Ask (`GreyAskVal`), PCGS (`PcgsVal`), NGC (`NgcVal`), CPG Retail, and CAC verification flags (`IsCac`). | 30 JUL 2026 Prompt | 🟢 DONE | `numista_backend/services/greysheet_service.py` |
| **GS-02** | **Compliant Dual-Mode UI** | Surface high-recognition retail metrics (Red Book, PCGS, NGC, Blue Book, CAC) in public UI, while keeping Wholesale Bid/Ask in private backend for liquidation calculations per CDN §4.3. | 30 JUL 2026 Plan v2 | 🟢 DONE | `coin_detail_screen.dart`, `estate_report_generator.py` |
| **GS-03** | **Greysheet Market Hub Tab** | Dedicated "GreySheets Market Data" tab on Desktop Web Coin Card with multi-source comparison table, grade slider, and CAC premium indicator. | 30 JUL 2026 Plan v1 | 🟢 DONE | `coin_detail_screen.dart` |
| **GS-04** | **Atomic Quota Manager (50k Cap)** | Track monthly API calls atomically in Firestore (`greysheet_usage/YYYY-MM`) with 25k warning alert and 50k hard cap to lock variable cost to $287/mo max. | 30 JUL 2026 Plan v2 | 🟢 DONE | `numista_backend/services/greysheet_quota_service.py` |
| **GS-05** | **24h Cache TTL & Coalescing** | Cache pricing for 24 hours (aligned to CDN 3 PM PT refresh) and use single-flight request coalescing to prevent redundant API calls across Cloud Run instances. | 30 JUL 2026 Plan v2 | 🟢 DONE | `greysheet_quota_service.py` |
| **GS-06** | **Vertex AI Grounding Context** | Inject live Greysheet market ranges into Gemini prompt context for `/api/deep_dive` queries to eliminate pricing hallucinations in AI essays. | 30 JUL 2026 Plan v2 | 🟢 DONE | `numista_backend/main.py` (`POST /api/deep_dive`) |

---

## 2. 🎁 Wish List Sharing, EPN Affiliate Monetization & Gift Safety

| ID | Feature / Idea | Description | Origin | Status | Location / Details |
|:---|:---|:---|:---|:---:|:---|
| **WL-01** | **Shareable Gift List (`/wishlist/{token}`)** | Read-only public gift list view allowing family members to view missing program coins and custom wishlist items without logging in. | eBay 30 JUL 2026 | 🟢 DONE | `public_wishlist_view_screen.dart` |
| **WL-02** | **EPN Affiliate Monetization** | Embed **[ Buy on eBay ]** buttons with Numista.AI affiliate tracking (`campid=5339148752`) on every missing wishlist item (1–4% commission). | eBay 30 JUL 2026 | 🟢 DONE | `epn_service.dart` |
| **WL-03** | **Key-Date $200+ Safety Filter** | Automatically append `PCGS NGC CAC` to eBay search queries for missing coins estimated at $\ge \$200$ to protect non-collector relatives from altered/raw coins. | eBay 30 JUL 2026 Plan v2 | 🟢 DONE | `epn_service.dart` |
| **WL-04** | **"I Bought This" Gift Reservation** | Interactive reservation toggle on public wishlist with optional buyer name dialog and disabled EPN button once reserved. | eBay 30 JUL 2026 Plan v2 | 🟢 DONE | `public_wishlist_view_screen.dart` |
| **WL-05** | **Buyer Safety Box Guidance** | Display non-collector buyer safety tips (seller feedback $\ge 99\%$, avoid stock photos, prefer certified slabs) on the public gift list page. | eBay 30 JUL 2026 Plan v2 | 🟢 DONE | `public_wishlist_view_screen.dart` |
| **WL-06** | **Automatic Wishlist In-Progress Pre-fill** | Automatically display missing coins from active tracked Coin Programs (e.g. 28 missing Presidential Dollars) on Wish List screen even if manual wishlist is empty. | 30 JUL 2026 Test | 🟢 DONE | `wishlist_screen.dart` |

---

## 3. 🎯 Custom Set Completion Goals & 33 Mint Mark Checklists

| ID | Feature / Idea | Description | Origin | Status | Location / Details |
|:---|:---|:---|:---|:---:|:---|
| **CG-01** | **Custom Set Completion Goals** | Allow collectors to select completion criteria per program: `Circulation Only (P & D)`, `Standard Set`, `Full Master Set`, or `Manual Override`. | eBay 30 JUL 2026 | 🟢 DONE | `program_manager_screen.dart`, `users/{email}/settings/program_preferences` |
| **CG-02** | **Progress Bar Recalculation** | Automatically recalculate program completion percentages based on chosen goal (e.g. 100% complete for business strike set without requiring proof coins). | eBay 30 JUL 2026 | 🟢 DONE | `program_manager_screen.dart` |
| **CG-03** | **Complete Mint Mark Checklists** | Expand all 33 U.S. Coin Programs to break down every mint mark (P, D, S, W, O, CC) and finish variety (Uncirculated, Clad Proof, Silver Proof, Satin, Reverse Proof). | eBay 30 JUL 2026 | 🟢 DONE | `coin_programs_data.dart`, `master_coin_programs.json` |
| **CG-04** | **5-by-5 Staged Mint Mark Audit** | Audit and seed all 33 coin programs in batches of 5 against Littleton reference checklists to prevent Firestore schema corruption. | eBay 30 JUL 2026 Plan v2 | 🟢 DONE | `_scripts/seed_global_programs.py` |
| **CG-05** | **Custom Goal Met Badge (✓)** | Render visual "Custom Goal Met ✓" badge when collector achieves 100% of their selected completion goal. | eBay 30 JUL 2026 | 🟢 DONE | `program_manager_screen.dart` |
| **CG-06** | **America250 Semiquincentennial Checklist** | Complete 2026 250th Anniversary Special Program checklist (5 circulating quarter designs, gold & silver medals). | Sprint 4 Plan | 🟢 DONE | `checklist_2026_service.dart` |

---

## 4. 📄 Ingestion, CSV Templates, Theme/Location Metadata & Export

| ID | Feature / Idea | Description | Origin | Status | Location / Details |
|:---|:---|:---|:---|:---:|:---|
| **IN-01** | **Downloadable Pre-Formatted CSV Template** | Provide downloadable CSV template matching Golden Schema in "Upload Files" tab so users can easily input and upload data. | 30 JUL 2026 Test | 🟢 DONE | `add_coins_hub.dart` |
| **IN-02** | **CSV Test Row Warning / AI Skip** | Add explicit warning to delete test rows in downloadable CSV, and instruct backend AI parser to auto-ignore test columns/rows. | 30 JUL 2026 Test | 🟢 DONE | `numista_backend/main.py` |
| **IN-03** | **CSV `Theme / Subject` Column** | Add `Theme / Subject` metadata field (e.g. "Harrison", "Tyler") to distinguish coins in series like Presidential Dollars during CSV export/import. | 30 JUL 2026 Test | 🟢 DONE | `coin_model.dart`, `numista_backend/main.py` |
| **IN-04** | **CSV `Storage Location` Column** | Add `Storage Location` metadata field (e.g. "Safe Box 2", "Album 1") to CSV schema and coin details. | 30 JUL 2026 Test | 🟢 DONE | `coin_model.dart`, `add_coins_hub.dart` |
| **IN-05** | **Sub-2-Second 25-Coin CSV Pipeline** | Fix 6-minute CSV processing bottleneck using local rapidfuzz header mapping, single-call Gemini fallback, `asyncio.to_thread`, and `db.batch()` writes. | 31 JUL 2026 Feedback | 🟢 DONE | `numista_backend/main.py` |
| **IN-06** | **JSON/CSV Collection Backup Exporter** | One-click export of user collection data with `schemaVersion: 1`, metal spot price baselines, and ISO-8601 timestamps. | Sprint 4 Plan | 🟢 DONE | `backup_export_service.dart`, `settings_screen.dart` |

---

## 5. 🧙‍♂️ Morgan AI Avatar, Floating Draggable Window & Conversation State

| ID | Feature / Idea | Description | Origin | Status | Location / Details |
|:---|:---|:---|:---|:---:|:---|
| **MG-01** | **Draggable & Resizable Pop-Out Window** | Make "Ask Morgan" AI chat a floating pop-out window that can be dragged and resized anywhere across desktop viewports. | 30 JUL 2026 Test / PR #65 | 🟢 DONE | `morgan_guide_flow.dart`, `base_layout.dart` |
| **MG-02** | **Collection-Aware Prompt Context** | Inject live user collection metrics (item count, total cost, market value, key dates, missing gaps) into Morgan's prompt context (1,200 token budget). | Sprint 4 Plan | 🟢 DONE | `morgan_chat_context.dart`, `ai_chat_screen.dart` |
| **MG-03** | **Cross-Platform TTS Voice Engine** | Hands-free TTS voice synthesis via `flutter_tts` with browser Web Speech API fallback, "Tap to Listen" per message, and auto-play setting. | Sprint 4 Plan | 🟢 DONE | `tts_voice_service.dart`, `ai_chat_screen.dart` |
| **MG-04** | **Conversation State Hardening** | Preserve turn state and format short answers like "D" as clarification responses to previous questions without context loss. | Dad Feedback #1 | 🟢 DONE | `ai_chat_screen.dart`, `main.py` |
| **MG-05** | **Prompt Tone & Verbiage Simplification** | Streamline Morgan's response verbiage to be concise, direct, and beginner-friendly for non-tech-savvy users. | Dad Feedback #1 | 🟢 DONE | `morgan_chat_context.dart` |
| **MG-06** | **"Start Collection With This Coin" Prompt** | When user asks about a coin not in collection, Morgan proactively prompts: *"Would you like to start your collection with this coin?"* | Dad Feedback #1 | 🟢 DONE | `ai_chat_screen.dart` |

---

## 6. 🔐 Auth, Onboarding, PIN Terminology & Email Deliverability (Dad's Audit)

| ID | Feature / Idea | Description | Origin | Status | Location / Details |
|:---|:---|:---|:---|:---:|:---|
| **AU-01** | **"Try It Free" Button Handler Fix** | Fix issue where clicking "Try It Free" on landing page did nothing; wire to instant demo session or registration modal. | Dad Feedback #1 | 🟢 DONE | `base_layout.dart`, `welcome_screen.dart` |
| **AU-02** | **Onboarding Sign-Up Flow Clarity** | Redesign sign-up screen to make "Create Account" instantly recognizable and reduce competing button clutter. | Dad Feedback #1 | 🟢 DONE | `login_screen.dart` |
| **AU-03** | **"Reset 6-Digit PIN" UI Terminology** | Update all UI text and dialogs from "Reset Password" to "Reset 6-Digit PIN" to match Numista's PIN authentication model. | Dad Feedback #1 | 🟢 DONE | `login_screen.dart` |
| **AU-04** | **Email Deliverability & DKIM/SPF Alignment** | Audit reset email delivery headers to prevent password/PIN reset emails landing in Spam/Trash folders. | Dad Feedback #1 | 🟢 DONE | Firebase Console / SendGrid DNS TXT setup |
| **AU-05** | **Account Creation Status Indicator** | Fix delay/messaging when user signs up so system doesn't falsely indicate "account already exists" during PIN reset flow. | Dad Feedback #1 | 🟢 DONE | `auth_service.dart` |
| **AU-06** | **Anonymous Guest Demo Isolation** | Pre-seeded 100-coin demo session with 30-day isolated Firestore path (`users/{uid}/coins`) and top conversion banner. | Sprint 5 / Base Layout | 🟢 DONE | `guest_seed_service.dart`, `base_layout.dart` |

---

## 7. 🖥️ Desktop UX, Upload Files Layout & Danger Zone Isolation

| ID | Feature / Idea | Description | Origin | Status | Location / Details |
|:---|:---|:---|:---|:---:|:---|
| **UI-01** | **Upload Files CTA Relocation** | Move "Open Bulk Import →" CTA button from bottom of `Upload Files` tab up into the top hero section next to "Folder-Drop Bulk Import". | 31 JUL 2026 Feedback | 🟢 DONE | `add_coins_hub.dart` |
| **UI-02** | **Danger Zone Complete Removal from HTML** | Delete `<div class="danger-zone">` and clear collection JS handlers from `add_coins.html`, and PIN-gate `/api/collection/clear` backend route. | 31 JUL 2026 Feedback | 🟢 DONE | `numista_backend/public/add_coins.html`, `main.py` |
| **UI-03** | **Settings Danger Zone Safeguards** | Consolidate Danger Zone strictly inside `Settings` with two-step type-to-confirm "DELETE" modal safeguards. | 31 JUL 2026 Feedback | 🟢 DONE | `settings_screen.dart` |
| **UI-04** | **Ultra-Wide Multi-Pane Desktop Layout** | Multi-pane responsive renderer for screens $> 1600\text{px}$ displaying spot ticker, collection grid, and Morgan chat side-by-side. | Sprint 5 Plan | 🟢 DONE | `secondary_display_layout.dart`, `base_layout.dart` |
| **UI-05** | **Desktop 1920x1080 Viewport Mandate** | Optimize all Flutter web screens, checklists, and microscope triggers for 1080p/4K desktop viewports for Nov 1 Launch. | OPORD Week 1 | 🟢 DONE | `numista_mobile/lib/` |
| **UI-06** | **Floating Beta Feedback Overlay** | Pinned `💬 Feedback` FAB with 1-5 star ratings (Ease, Fun, Utility), route context capture, GCS screenshot upload, and Admin Dashboard. | 27 JUL 2026 Checklist | 🟢 DONE | `beta_feedback_widget.dart`, `admin_feedback_screen.dart` |

---

## 8. 🔄 Version Control, Release Notes Automation & System Observability

| ID | Feature / Idea | Description | Origin | Status | Location / Details |
|:---|:---|:---|:---|:---:|:---|
| **VO-01** | **Automated `RELEASE_NOTES.md` Script** | Create `add_release_note.py` script to automatically log version updates and sync release notes across the system. | 30 JUL 2026 Test | 🟢 DONE | `add_release_note.py`, `RELEASE_NOTES.md` |
| **VO-02** | **Version Number Alignment (v4.1)** | Standardize version display across app header, dashboard badge, and backend APIs to `v4.1` (eliminating v3.9 / v4.0 mismatch). | 30 JUL 2026 Test | 🟢 DONE | `home_dashboard.dart`, `RELEASE_NOTES.md` |
| **VO-03** | **Rule 7 Git Workflow Enforcement** | Commit all agent work on `dev` branch with `--rebase` pushes; main branch merges remain exclusively under owner authority. | Workspace Rules | 🟢 DONE | `.agents/AGENTS.md` |
| **VO-04** | **Model Policy Deprecation Audit (Rule 6)** | Audit and enforce active 2026 Gemini model bindings (`gemini-3.6-flash`, `gemini-3.1-pro-preview`, `gemini-3.5-flash-lite`, `gemini-3.1-flash-image`). | Rule 6 Policy | 🟢 DONE | `numista_backend/config.py`, `SCAN_REPORT.md` |
| **VO-05** | **Proactive Scraper Failure Isolation** | Route auction/market scraper results to `scraped_price_staging` table with outlier detection before updating master price data. | Sprint 4 Plan | 🟢 DONE | `proactive_scraper.py` |
| **VO-06** | **System Audit & Scan Suite (`SCAN_REPORT.md`)** | Automated diagnostic scanner verifying Pytest unit suite, Playwright E2E suite, Gemini health, and GCP proxy probes. | 4 AUG 2026 Scan | 🟢 DONE | `SCAN_REPORT.md` |

---

## 9. 🏛️ Estate Planning, Provenance Audit & High-Value Appraisal

| ID | Feature / Idea | Description | Origin | Status | Location / Details |
|:---|:---|:---|:---|:---:|:---|
| **EP-01** | **Twin Portfolio Valuation Split** | Display side-by-side **Liquidation Cash Value** (Greysheet Wholesale Bid) vs **Replacement Value** (Red Book Retail) for estate executors. | 30 JUL 2026 Plan v1 | 🟢 DONE | `home_dashboard.dart`, `estate_planning_screen.dart` |
| **EP-02** | **IRS Form 8283 & USPAP Legal Disclaimer** | Explicit legal notice on PDF reports stating valuations are property accountability tools, not formal IRS Form 8283 qualified appraisals. | 27 JUL 2026 Review | 🟢 DONE | `estate_report_service.dart`, `estate_report_generator.py` |
| **EP-03** | **Institutional Appraisal Tier ($250K+ / 5K+ Coins)** | Institutional appraisal PDF report package with USPAP compliance statement, liquidation risk matrix, and certificate page. | Sprint 5 Plan | 🟢 DONE | `estate_report_generator.py` |
| **EP-04** | **Heir Division Engine (LPT Algorithm)** | Greedy Longest Processing Time algorithm partitioning collection items equitably among heirs while respecting locked family heirlooms. | Sprint 3 / 5 | 🟢 DONE | `numista_backend/scan_service/` |
| **EP-05** | **COA (Certificate of Authenticity) Inspector** | OCR document scanner tab extracting serial numbers, production limits, and mintage signatures from US Mint COA cards via Gemini Vision. | Sprint 5 Plan | 🟢 DONE | `coa_inspector_screen.dart`, `coa_parser_service.py` |
| **EP-06** | **5-State Probate Rule Engine** | Tailored probate rules and legal report templates for CA, TX, FL, NY, and NC jurisdictions. | Sprint 3 / 28 JUL | 🟢 DONE | `estate_planning_screen.dart` |

---

## 10. 🛡️ GCP Infrastructure, Secret Manager & Hardware Bus Resilience

| ID | Feature / Idea | Description | Origin | Status | Location / Details |
|:---|:---|:---|:---|:---:|:---|
| **HW-01** | **Firestore Command Bus (CORS Fix)** | Eliminate browser Mixed Content (HTTPS -> HTTP) CORS blocks by routing USB microscope triggers via Firestore stream (`commands/{email}/pending`). | OPORD Week 1 | 🟢 DONE | `numista_hardware/auto_capture.py`, `microscope_scan_screen.dart` |
| **HW-02** | **Headless Hardware Mock Flag** | Add `--mock-hardware` CLI flag to `auto_capture.py` to bypass physical camera checks during automated CI test suite execution. | 27 JUL 2026 Test | 🟢 DONE | `numista_hardware/auto_capture.py` |
| **HW-03** | **GCP Secret Manager Integration** | Mount `GREYSHEET_API_KEY`, `GREYSHEET_API_TOKEN`, and `STRIPE_SECRET_KEY` via GCP Secret Manager into Cloud Run containers. | 4 AUG 2026 Audit | 🟢 DONE | GCP Secret Manager / `config.py` |
| **HW-04** | **Cloud Run Auto-Scaling & Timeout Tuning** | Configure `numista-backend` to autoscale (1 to 10 instances) with 300s timeout for bulk imports and 1 warm instance for PDF scan service. | OPORD Week 1 | 🟢 DONE | GCP Cloud Run Console |
| **HW-05** | **Automated Firestore GCS Backup** | Daily automated Firestore exports to GCS bucket (`gs://studio-9101802118-8c9a8-uploads/backups/`) via GCP Cloud Scheduler. | OPORD Week 1 | 🟢 DONE | GCP Cloud Scheduler |
| **HW-06** | **20-Point Interactive Hybrid Beta Checklist** | In-app drawer widget tracking 20 core testing tasks with auto-detection, manual checkmarks, "N/A / Skip" toggles, and celebratory completion badge. | 27 JUL 2026 Plan | 🟢 DONE | `beta_checklist_widget.dart`, `beta_checklist_service.dart` |
