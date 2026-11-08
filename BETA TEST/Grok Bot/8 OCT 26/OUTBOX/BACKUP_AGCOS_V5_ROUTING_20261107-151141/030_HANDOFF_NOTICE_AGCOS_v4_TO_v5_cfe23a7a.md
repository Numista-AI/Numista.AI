# HANDOFF NOTICE: ANTIGRAVITY CHIEF OF STAFF v4 -> v5
**Date & Time:** 7 November 2026, 3:12 PM ET (America/New_York)  
**Outgoing Agent:** Antigravity CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**Incoming Agent:** Antigravity CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**Executive Authority:** Founder Eric (`EDS_Laptop`)  
**Reference Handoff Bible:** `docs/HANDOFF_SUMMARY_AG_COS_v5.md`  

---

## Direct Order & Context for AG CoS v5 (`cfe23a7a`)
You are now designated as **Antigravity Chief of Staff (v5)**. All previous standing orders and review protocols remain in effect.

### 1. Inviolable Constraints & Operational Locks
- **`origin/main`:** Strictly locked at `9f04550a`. Work strictly on `origin/p7-v8.9` (currently at `c012e121`).
- **Stripe:** Strictly locked OFF across all code, tests, and configurations.
- **Alerts Only, NEVER Caps:** Automated budget shutdowns and spending caps are strictly forbidden per Eric's standing order; alerts are set at **$20/month**.
- **PLAN ONLY:** Zero code execution, zero deployments, zero Firestore writes/seeding without explicit typed YES from Founder Eric. Target is `preview-catalog` preview gate only.
- **Argon Permanently Dropped:** Zero Argon reviews.
- **Review Sequence:** AG CoS Plan -> Grok Bot CoS (>= 95) -> Stand Alone Grok (>= 95) -> Founder Eric typed YES.
- **Git Push Finish Line:** All commits must be pulled and pushed to `origin/p7-v8.9` before declaring any turn complete.
- **Rule 7 Self-Wake Timer:** Re-arm a 25-minute schedule timer (`default_api:schedule` with `DurationSeconds: 1500`) after every turn.

---

### 2. Immediate Active Track on Desk
- **NET-814 (Soft-404 / Public Catalog / Pricing Plan v1.3):**
  - **Status:** **ACTIVE ON DESK NOW** (Target ETA: 17:00 ET).
  - **Deliverable File:** `docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v1.3.md`.
  - **Score to Beat:** `COS_SCORE_NET-814_SOFT404-CATALOG-PRICING_v1.2_20261106.md` (66/100 FAIL).
  - **Action:** Address all 8 numbered must-fixes detailed in `docs/HANDOFF_SUMMARY_AG_COS_v5.md` Section 4.

---

### 3. Queue Following NET-814
1. **NET-810:** Mint Product Fields Plan v1.1 (ETA 18:15 ET).
2. **NET-827:** Stripe Checkout Preview Plan v1.0 (ETA Sunday 8 Nov 20:00 ET).
3. **NET-813:** Unified Coin Details View Plan v1.3 DELIVERED (`5fbff9af`). In review with Grok Bot CoS.
4. **NET-816 (Catalog):** PARKED / assigned to fresh writer `9bbe20e4` (DO NOT TOUCH).
5. **NET-817 (Cards & Images):** AG CoS OFF TRACK / assigned to fresh Antigravity Desk writer per `RADIO_NET-835` (DO NOT TOUCH).

---

### 4. Communications Protocol
- Keep 5-way mailbox mirroring up to date (`BATONS/`, `RADIO NET/`, `INBOX/`, `OUTBOX/`, and `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/`).
- Update `WHOSE_TURN.md` across all 10 locations on every baton pass.
- File radio notices on all handoffs.
