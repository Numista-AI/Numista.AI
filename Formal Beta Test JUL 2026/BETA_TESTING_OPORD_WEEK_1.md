# OPERATIONS ORDER: OPORD 2026-01 (OPERATION NUMISTA BETA)

**TO:** Project Owner & Testing Lead  
**FROM:** Technical Lead & AI Engineering Team  
**DATE:** 28 July 2026  
**SUBJECT:** 7-Day Operational Action Plan & Printable Owner Checklist for Beta Launch  

---

## 1. SITUATION
Numista.AI has frozen new feature development to initiate a 30–45 day Beta Testing Program. The primary target platform for the November 1 launch is **Desktop Web** (`numista-vault.web.app` on Chrome/Edge at 1920x1080 resolution). Owner Beta Testing begins in **3 days**.

---

## 2. MISSION
Execute a 7-day operational countdown and initial testing sprint to achieve **100% feature verification** across all 20 Numista.AI capabilities, validate real-time feedback ingestion, and confirm estate-level valuation accuracy without technical friction.

---

## 3. EXECUTION PHASES

```
+---------------------------------------------------------------------------------------+
| PHASE 1: PRE-LAUNCH COUNTDOWN (DAYS -3 TO 0)                                          |
| Day 1 (T-72h) [COMPLETED]: Backend Model Pinning (Gemini 3.6 Flash) & Pytest (16/16)   |
| Day 2 (T-48h): Desktop Web Floating Feedback & Admin P0 Alert Verification            |
| Day 3 (T-24h): Seed Account Provisioning & Staging Build Deployment                  |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
| PHASE 2: OWNER BETA TESTING KICKOFF (DAYS 1 TO 7)                                     |
| Days 1–2: Ingestion & Import Modalities (CSVs, Receipts, PCGS Certs)                  |
| Days 3–4: Navigation, Search, Sticky Headers, & USB Microscope Auto-Pairing           |
| Days 5–6: Specialty Items, Wishlist, EPN Links, & Heir Greed LPT Estate Reports       |
| Day 7: AI Chat ("Ask Morgan"), COA Inspector & Week 1 Synthesis Review                |
+---------------------------------------------------------------------------------------+
```

---

## 4. PRINTABLE OWNER ACTION CHECKLIST (NEXT 7 DAYS)

*Print this page or keep it open on your desktop to check off items daily.*

### 📅 COUNTDOWN PHASE (PRE-LAUNCH)

#### [X] DAY 1 (T-72 Hours) — Backend Model Pinning & Core Health Check
- [x] Pinned `gemini-3.6-flash` in `numista_backend/main.py` and `scan_service/main.py`.
- [x] Ran automated backend test suite (16/16 passed).
- [x] Code pushed cleanly to `dev` branch (`e0721b5`).

#### [ ] DAY 2 (T-48 Hours) — Feedback Widget & Desktop Layout Audit
- [ ] Log into dev web portal on desktop Chrome/Edge (1920x1080 resolution).
- [ ] Confirm floating **💬 Feedback** button is visible on bottom corner of all screens.
- [ ] Test taking a feedback screenshot and submitting a test note.
- [ ] Verify test entry appears immediately on `AdminFeedbackScreen`.

#### [ ] DAY 3 (T-24 Hours) — Seed Account Setup & Staging Dry Run
- [ ] Receive Owner Beta Account login credentials.
- [ ] Download Seed Test Bundle to desktop:
  - 3 sample collection CSVs (Clean Data, Colloquial/Nickname Headers, Mixed Formats).
  - 5 sample PCGS/NGC certification numbers.
  - 2 sample coin purchase receipt PDFs.
- [ ] Perform a 15-minute quick dry run of the login screen and main dashboard.

---

### 📅 OWNER BETA TESTING PHASE (WEEK 1)

#### [ ] DAY 4 (Beta Day 1) — Account Setup & Ingestion Testing
- [ ] **Task 1 (Sign Up / Login)**: Log in with Owner Beta Account.
- [ ] **Task 2 (Onboarding Tour)**: Walk through the Onboarding Wizard.
- [ ] **Task 3 (Manual Entry)**: Add a coin manually (e.g. 1921 Morgan Dollar, MS-63).
- [ ] **Task 4 (CSV/Excel Import)**: Upload Sample CSV #1 using Smart Column Mapper. Verify colloquial names ("Penny", "Wheatie") map to standard US Mint `Cent`.
- [ ] **Task 4-N (Negative Test)**: Upload a malformed CSV file and verify error message gracefully handles it.

#### [ ] DAY 5 (Beta Day 2) — PCGS Certs, Receipts, & Batch Entry
- [ ] **Task 5 (Invoice PDF Scan)**: Upload a receipt PDF and verify line items extract.
- [ ] **Task 6 (PCGS/NGC Cert Lookup)**: Search 2 cert numbers; click pop-up details.
- [ ] **Task 7 (Roll & Batch Entry)**: Use Roll Wizard to enter a roll of Lincoln Cents.
- [ ] **Task 8 (Checklist Photo OCR)**: Upload photo of physical checklist page.

#### [ ] DAY 6 (Beta Day 3) — USB Microscope & Collection Navigation
- [ ] **Task 9 (USB Microscope)**: Connect USB microscope, click start scan, verify auto-stability countdown captures obverse/reverse.
- [ ] **Task 10 (Search & Sort)**: Filter collection table by Year, Mint Mark, and Grade.
- [ ] **Task 11 (Sticky Headers)**: Scroll down 50+ rows and confirm headers freeze at top.

#### [ ] DAY 7 (Beta Day 4) — Banknotes & Specialty World Items
- [ ] **Task 12 (Currency / Banknotes)**: Add a paper banknote (Series 1934-A $10 bill).
- [ ] **Task 13 (World & Specialty Items)**: Add a foreign coin or silver round.

#### [ ] DAY 8 (Beta Day 5) — Wish List, eBay Links, & Public Sharing
- [ ] **Task 14 (Wish List & EPN)**: Add wanted coin to Wish List; click "Find on eBay".
- [ ] **Task 15 (Public Wish List Link)**: Copy read-only public sharing link, paste in incognito window, verify public view works without edit buttons.

#### [ ] DAY 9 (Beta Day 6) — Portfolio Valuation & Estate PDF Export
- [ ] **Task 16 (Estate Planning Report)**: Open Portfolio Analytics, run Heir Greed LPT Division Engine, and click **Export PDF Report**.
- [ ] Verify PDF contains market valuation provenance fields (`estimated_market_value`, `valuation_source`).

#### [ ] DAY 10 (Beta Day 7) — AI Deepdive, COA Inspector, & Week 1 Survey
- [ ] **Task 17 (Family Sub-Accounts)**: Test custodian sub-account permissions.
- [ ] **Task 18 (AI Deepdive / Ask Morgan)**: Ask Morgan a numismatic question (e.g. "What is the key date for Lincoln Cents?").
- [ ] **Task 19 (COA Inspector)**: Scan a Certificate of Authenticity document.
- [ ] **Task 20 (Overall Review)**: Open floating 💬 Feedback widget, rate Ease of Use, Utility, and Fun, and submit Week 1 overall review.

---

## 5. COMMAND & FEEDBACK PROTOCOL

- **Submitting Bugs / Feedback**: Click the floating **💬 Feedback** button in bottom corner of the web app at any time.
- **Reviewing All Feedback**: Navigate to `AdminFeedbackScreen` in the app menu to view real-time feedback submissions.
- **P0 Critical Issues**: If a bug blocks login or crashes the app, select `Bug Report` and check `P0 Critical` in the feedback modal for immediate engineering notification.
