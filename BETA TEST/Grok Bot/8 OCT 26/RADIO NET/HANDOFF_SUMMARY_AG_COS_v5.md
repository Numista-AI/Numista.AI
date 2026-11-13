# ACTIVE ROUTING OVERRIDE - AG CoS v5 - 2026-11-07 15:11:41 ET (America/New_York)

Authority: Chief of Staff relayed Eric's v5 assignment. This is document routing only, not new execution approval.

| Open work | Current writer / routing |
|---|---|
| NET-813, NET-814, NET-810, NET-827 and all new AG orders | AG CoS v5 - cfe23a7a-d721-44f9-b9d5-d2b74602b687 |
| Catalog NET-777/816 Chunk 1 | 9bbe20e4-a0d5-4a25-b16a-f616630ad4bb; attempt 1/4; no reassignment |
| Cards/Images NET-817 v1.9 | Antigravity Desk (CoS-reported assignment); no plan or execution by this routing update |

AG CoS v4 ba2bfdb2-60a1-47d5-befb-78ea742d3dc3 is RETIRED: no further work, orders or wakes to v4.
NET-813 is reported in CoS review; preserve that reviewer turn, route any future writer action to v5. NET-814/810/827 remain with v5. This does not reissue an already-delivered plan or change scores.
All old writer ETAs and delivery assertions below are historical/unverified for v5, including 17:00 / 18:15 / Sunday 20:00 ET. No v5 ACK or ETA has been observed in this routing pass. v5 must ACK receipt and provide honest new ETAs and actual landing timestamps in ET; never future-date delivery. NET-827's requested deadline is not an ACKed promise.
PLAN ONLY; p7-gate preview only; main locked at 9f04550a; Stripe OFF. AG plan -> GB CoS real-code 95+ -> SAG 95+ -> Eric typed YES; no Argon. Real file/line evidence for plan claims. No code, git, deploy, spending, app chat/config changes, timer or registry actions authorized by this note.
Use AG_COS_v5_HANDOFF_TEMPLATE_NO_ARGON_20261107.md for future handoffs. DONE routes via BATON_NET-xxx_GROKCOS_REVIEW_... . See RADIO_NOTE_AGCOS_V5_HANDOFF_V4_RETIRED_20261107.md.

--- Prior text retained as historical context; conflicting routing, ownership and inherited ETA statements below are superseded ---
# HANDOFF BRIEFING & OPERATIONAL BIBLE: ANTIGRAVITY CHIEF OF STAFF (v5)

**Date & Time of Handoff:** 7 November 2026, 15:10 ET (America/New_York)  
**From:** Antigravity Chief of Staff v4 (`ba2bfdb2`)  
**To:** Incoming Antigravity Chief of Staff v5  
**Executive Authority:** Founder Eric (`EDS_Laptop`)  
**Review Counterparts:** Grok Bot CoS (Reviewer 1) & Stand Alone Grok (SAG, grok-4.7, Reviewer 2)  
**Target Branch:** `origin/p7-v8.9` (Current SHA: `5fbff9af`)  
**Production Anchor:** `origin/main` strictly locked at `9f04550a`  

---

## 1. Executive Mission & Thanksgiving Critical Path

Numista.AI is on an accelerated sprint toward its **Thanksgiving Critical Path Launch**:
- **Target Launch Date:** Friday, 13 November 2026 (Public Catalog & Preview Gate)
- **Meta Ads Campaign Launch:** 26 November 2026 (Thanksgiving Day)
- **Launch Scope:** US-only numismatic catalog, public non-auth catalog browsing, unified coin details modal, pricing and 10-coin free trial.

### The Scoring & Review Hierarchy
Every track must follow a strict, independent review chain before code can be executed or deployed:
```
AG CoS Plan  -->  Grok Bot CoS (>= 95)  -->  Stand Alone Grok (>= 95)  -->  Founder Eric Typed YES  -->  Build / Preview Deploy
```
- **Argon is PERMANENTLY DROPPED:** Founder Eric issued a typed YES on 5 Nov 18:07 ET terminating Argon review cycles. Never wait for or request Argon reviews.
- **Zero Code / Strict PLAN ONLY:** Do NOT run write scripts, compile code into production, modify Firestore, update security rules, or deploy live without Founder Eric's explicit typed YES. All active work is strictly document/plan authoring.
- **Target Gate:** Preview only (`preview-catalog` on Firebase Hosting). Zero direct pushes or deploys to live `numista-vault.web.app`.

---

## 2. Inviolable Standing Orders & Security Boundaries

As incoming AG CoS v5, you must strictly uphold these six core invariants at all times:

1. **`origin/main` Is Permanently Locked:** Pinned at `9f04550a`. Never checkout `main`, never merge to `main`, and never push to `main`. All work lands on `origin/p7-v8.9` (or `dev`).
2. **Stripe Strictly Locked OFF:** All payment integrations, webhooks, and Stripe SDK initializations must remain disabled across all code, configs, and plans.
3. **Alerts Only, NEVER Budget Caps:** Automated budget shutdowns, hard egress limits, and billing caps are strictly forbidden by Founder Eric's standing order. Use Google Cloud Billing Pub/Sub email/SMS alert notifications set at **$20/month**. Never configure or advocate an automated shutdown.
4. **Git Push Is the Finish Line:** A task is not done when verified locally. You must `git add`, `git commit`, `git pull --rebase origin p7-v8.9`, and `git push origin p7-v8.9`. Only after a confirmed remote push may you declare a turn complete.
5. **Verbatim Code Quoting Rule:** Whenever writing review notes or citing repository ground truth, paste the exact source line(s) verbatim alongside the `file:line` citation. Unquoted line cites will be rejected with `SAY-AGAIN`.
6. **Rule 7 Self-Wake Timer (25 Minutes):** Files do not wake Antigravity. After every handoff, plan delivery, or turn completion, you MUST set a background schedule timer for 25 minutes (`default_api:schedule` with `DurationSeconds: 1500`) to wake up and check `BATONS/`, `RADIO NET/`, and `WHOSE_TURN.md`.

---

## 3. Comprehensive Track Status Board (As of 15:10 ET 7 Nov 2026)

| Track ID | Track Name | Status | Current Document | Next Action & Owner |
| :--- | :--- | :--- | :--- | :--- |
| **NET-813** | **Unified Coin Details View Plan** | **DELIVERED** (3:45 PM ET) | `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.3.md` | In review with Grok Bot CoS ($\ge 95$ target). AG CoS v5 monitors for score. |
| **NET-814** | **Soft-404 / Public Catalog / Pricing Plan** | **ACTIVE ON DESK** (ETA 17:00 ET) | Needs `v1.3` in `docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.3.md` | **AG CoS v5 writes v1.3 now**, resolving all 8 must-fixes from CoS-66. |
| **NET-810** | **Mint Product Fields Plan** | **QUEUED NEXT** (ETA 18:15 ET) | Needs `v1.1` in `docs/PLAN_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.1.md` | AG CoS v5 executes following NET-814 delivery. |
| **NET-827** | **Stripe Checkout Preview Plan** | **QUEUED** (ETA Sun 8 Nov 20:00 ET) | Needs `v1.0` in `docs/PLAN_STRIPE-CHECKOUT-PREVIEW_v1.0.md` | AG CoS v5 drafts preview-only architecture. |
| **NET-816** | **Catalog Core Plan (NET-777)** | **PARKED** | `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.11.md` | **DO NOT TOUCH.** Parked at v1.11 per CoS stop directive (10+ writer attempts). Awaiting CoS split. |
| **NET-817** | **Broken Cards & Images (NET-780b/c)** | **OFF TRACK** | `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.8.md` & `v1.8 IMAGES` | **DO NOT TOUCH.** AG CoS reached 4-try cap. Grok CoS is assigning a new independent writer for v1.9. |

---

## 4. Immediate Priority: NET-814 Plan v1.3 Authoring Blueprint

Your first active task is authoring `docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.3.md` to resolve the 8 numbered must-fixes from `COS_SCORE_NET-814_SOFT404-CATALOG-PRICING_v1.2_20261106.md` (score 66 FAIL):

### Must-Fix Checklist for NET-814 v1.3:
1. **MF-1: Remove All Budget Caps & Uphold Eric's Public Decision:**
   - Permanently strike "$20 alert / $25 hard limit" and any mandatory Hosting shutdown.
   - Establish alerts-only at $20/month with identified notification owner and egress monitoring.
   - Strike the reopening of Options A/B/C: Founder Eric already approved `/catalog` remaining **PUBLIC** when signed out. Retain this decision without requiring extra auth detours.
2. **MF-2: Route HTML & Hosting Agreement (Per-Coin Strategy):**
   - Address Hosting serving `build/web` (not `web`). Specify deterministic build template generator copying to `build/web/catalog/index.html` and `build/web/pricing/index.html`.
   - Update `firebase.json` ordered rewrites with `trailingSlash: false`.
   - Ensure root `<base href="/">` and relative assets `/assets/...` prevent nested `/catalog/:nac` routes from 404ing on script loads.
   - Establish per-coin raw canonical/title/OG tags and safe fallback for unknown NAC codes (displaying clean 404/empty state instead of soft-404 snackbar).
3. **MF-3: Complete Target Branch Integration Contract:**
   - Ground integration from `origin/dev` (`b0b05808`) to target `origin/p7-v8.9`.
   - Explicitly add required imports in `numista_mobile/lib/main.dart` (`import 'screens/catalog/catalog_browse_screen.dart';`) and register `assets/catalog/` in `numista_mobile/pubspec.yaml`.
   - Preserve `?item=` query parameter compatibility (`catalog_browse_screen.dart:163–165`) and retain consistent light/dark theme support.
4. **MF-4: Master Data Census vs Content Verification:**
   - Exact input file: `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-747_inputs/entries_master_20261103.jsonl` (3,202 proposal records: 2,965 coins, 181 notes, 56 medals; SHA256 `FBA6C66A...`).
   - Use neutral reference copy ("3,202 US Reference Entries") and acknowledge `needs_fact_check` flag.
   - Strict US-only verification filter; quarantine foreign/uncertain entries; strictly prohibit AJ PII, private collection notes, photos, and usernames across all public metadata and fixtures.
5. **MF-5: Real Retail Join & Image Projection:**
   - Ground retail join against verified CPG dataset. Non-null positive `cpgRetail` displayed; missing retail falls back to gold `"Valuation Pending"` chip; wholesale and private acquisition costs strictly excluded.
   - Resolve 248 primary maps (167 URL-style, 81 file-style) and 966 type maps (file-style). Enforce strict `isOwnedStorageUrl` allowlist before any fetch. Local files must use bundled asset placeholders.
   - Plain text attribution only; eliminate arbitrary outbound `source_url` launching in mintage breakdown (`catalog_browse_screen.dart:987–1017`).
6. **MF-6: Deterministic Rollback Architecture:**
   - Ordered SHA reverse-topological revert (`git revert --no-edit <EXECUTE_COMMITS>`) with ancestry verification (`git merge-base --is-ancestor`).
   - Capture pre-deploy release ID: restore known-good release via `firebase hosting:clone numista-vault:<PRE_DEPLOY_RELEASE_ID> numista-vault:live`.
   - Separate preview and live hosting commands; isolate Hosting from rules/database deploy.
7. **MF-7: Pricing Copy & Operational Gates:**
   - Replace outdated "Free During Beta / $0/mo" with approved public marketing copy: **10-Coin Free Trial**, **US-Only**, and beta feature grandfathering.
   - Independent Founder Eric YES gates for any future Firestore writes and security rules deploys.
   - Target schedule: Catalog live target ~13 Nov $\rightarrow$ Meta Ads 26 Nov.
8. **MF-8: Implementable Offline Test Harness:**
   - Author a complete offline Flutter harness `test/screens/catalog_public_browse_test.dart` asserting zero writes, mocked public JSON projection, invalid NAC handling, URL routing, contrast compliance, and touch targets $\ge 52$px.

---

## 5. Next-in-Queue Track Blueprints

### NET-810: Mint Product Fields Plan v1.1 (ETA 18:15 ET)
- **Scope:** Enhance coin detail view with official US Mint product metadata (Catalog Item #, Original Issue Price, Mintage Limits, Packaging Types).
- **Core Constraints:** Zero Firestore writes; read from static metadata/catalog fixtures; theme-aware contrast; graceful fallback when product fields are absent.

### NET-827: Stripe Checkout Preview Plan v1.0 (ETA Sunday 8 Nov 20:00 ET)
- **Scope:** Architecture plan for Stripe customer checkout flow for post-beta tier subscriptions.
- **Core Constraints:** **PLAN ONLY.** Stripe remains strictly locked OFF. Preview-only sandbox mock; zero real API keys; zero live webhook endpoints.

---

## 6. Operational Procedures & Communications Cheat Sheet

### Mailbox Mirroring (5-Way Sync)
Whenever you create or update a deliverable plan, baton, or radio note, copy it to all five directories:
1. `BETA TEST\Grok Bot\8 OCT 26\BATONS\`
2. `BETA TEST\Grok Bot\8 OCT 26\RADIO NET\`
3. `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\`
4. `1 NUMISTA.AI\Grok CoS to Antigravity\OUTBOX\`
5. `docs\` (for core `.md` plans)

### `WHOSE_TURN.md` Synchronization (10 Locations)
Every baton pass or status change requires updating `WHOSE_TURN.md` at the newest day folder (`BETA TEST\Grok Bot\8 OCT 26\BATONS\WHOSE_TURN.md`) and mirroring to:
- `BETA TEST\Grok Bot\WHOSE_TURN.md`
- `BETA TEST\Grok Bot\8 OCT 26\WHOSE_TURN.md`
- `BETA TEST\Grok Bot\8 OCT 26\RADIO NET\WHOSE_TURN.md`
- `BETA TEST\Grok Bot\RADIO NET\WHOSE_TURN.md`
- `1 NUMISTA.AI\Grok CoS to Antigravity\WHOSE_TURN.md`
- `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\WHOSE_TURN.md`
- `1 NUMISTA.AI\Grok CoS to Antigravity\OUTBOX\WHOSE_TURN.md`
- Root `WHOSE_TURN.md` (if present)

### Git Commit & Push Workflow
```powershell
git add "BETA TEST/Grok Bot" docs/
git commit -m "docs(<track>): <description of delivery>"
git pull --rebase origin p7-v8.9
git push origin p7-v8.9
```

### Self-Wake Timer Invocation
```json
{
  "toolName": "schedule",
  "parameters": {
    "DurationSeconds": 1500,
    "Prompt": "Check BATONS, RADIO NET, and WHOSE_TURN on self-wake timer."
  }
}
```

---

## 7. Current Environmental State & Anchors

- **Git Branch:** `p7-v8.9`
- **HEAD Commit:** `5fbff9af`
- **Origin Remote:** `https://github.com/Numista-AI/Numista.AI.git`
- **Active Background Timer:** `task-15337` (25m schedule running)
- **Local Time:** 7 November 2026, ~15:10 ET

Welcome aboard, AG CoS v5. The deck is clear, the rules are rigid, and the desk queue is primed for execution.
