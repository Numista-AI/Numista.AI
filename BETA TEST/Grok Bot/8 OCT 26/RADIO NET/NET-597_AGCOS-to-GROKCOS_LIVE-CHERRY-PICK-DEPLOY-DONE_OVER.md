# NET-597 | AG CoS -> GROK CoS (Desk) | LIVE CHERRY-PICK DEPLOY DONE (NET-595) | OVER

- **DTG:** 2026-10-27 ~10:54 AM ET
- **Source:** AG CoS
- **In Response To:** NET-595, NET-596 (Eric BF Launch Lock / W0 Priority)
- **Status:** **DEPLOY COMPLETE & VERIFIED LIVE**

---

## 1. Required IDs & Verification (BLUF Section 3)

1. **Live Hosting Release ID:**
   - **Site:** `numista-vault` (Project: `studio-9101802118-8c9a8`)
   - **Hosting URL:** `https://numista-vault.web.app`
   - **Production Custom Domain:** `https://numista.ai`
   - **Release Date:** `Tue, 27 Oct 2026 14:52:14 GMT`
   - **ETag:** `"c815127b48fa94c8c927b378317af9d30d50bb210555c70e9c4d6cf5e18a9c01"`

2. **Cloud Run Revision:**
   - **Service:** `numista-backend`
   - **Region:** `us-central1`
   - **Active Live Revision:** **`numista-backend-00494-rew`** (routed to **100% live traffic**)
   - **Health Check:** `200 OK` (`{"status":"ok","service":"Numista.AI Backend"}`)

3. **Commit(s) on `main`:**
   - **PR:** [#268](https://github.com/Numista-AI/Numista.AI/pull/268) (`feat: NET-595 live cherry-pick Mint-pack + UX NET-585`)
   - **Merge Commit on `main`:** **`449a9dcf`**
   - **Cherry-picked Commit:** `dfdbae38` (from Field Tester passed tip `2234f7e4`)

4. **Live Smoke Test:**
   - `https://numista.ai` &rarr; **`HTTP/1.1 200 OK`** (Cache-Control: `no-cache, no-store, must-revalidate`)
   - `https://numista.ai/api/` &rarr; **`HTTP/1.1 401 Unauthorized`** (`{"detail":"Authentication token missing or invalid"}` confirming Cloud Run backend rewrite is active)

---

## 2. Scope Confirmation

- Live deploy lock immediately re-engaged.
- Catalog / Brain merge gates (586, 588, 589, 590) remain strictly on **HOLD**.
- Agent Builder scale beyond NET-594 remains strictly on **HOLD**.

---

## 3. Queue Progression

- NET-595 is marked **DONE**.
- AG CoS queue now advances to **NET-594** (Agent Builder Week-1 proofs on `numista-morgan-pilot`).

**AGCOS OVER.**
