# EXECUTE_DONE | NET-595 Live Cherry-Pick Deploy (Mint-pack + NET-585 UX to numista.ai)

- **DTG:** 2026-10-27 ~10:53 AM ET
- **Author:** AG CoS
- **Authority:** Eric typed explicit YES (`"YES live cherry-pick Mint-pack + UX NET-585 to numista.ai now"`) via Grok CoS Desk NET-595 / URGENT WAKE
- **Status:** **DEPLOY COMPLETE & VERIFIED LIVE**

---

## 1. Deploy Deliverables & IDs (Per BLUF Requirements)

| Item | Value / ID | Status |
|------|-----------|--------|
| **Live Hosting Release** | Site: `numista-vault`<br>Project: `studio-9101802118-8c9a8`<br>URL: `https://numista-vault.web.app`<br>Custom Domain: `https://numista.ai`<br>Release Date: `Tue, 27 Oct 2026 14:52:14 GMT`<br>ETag: `"c815127b48fa94c8c927b378317af9d30d50bb210555c70e9c4d6cf5e18a9c01"` | **RELEASED & LIVE** |
| **Cloud Run Revision** | `numista-backend-00494-rew` (100% live traffic)<br>Service: `numista-backend`<br>Region: `us-central1`<br>Project: `studio-9101802118-8c9a8`<br>URL: `https://numista-backend-qntvrqvxma-uc.a.run.app` | **SERVING 100% TRAFFIC** |
| **Commit on `main`** | **`449a9dcf`** (`Merge pull request #268 from Numista-AI/deploy/mintpack-ux-net595`)<br>Cherry-pick commit: `dfdbae38` (from FT-passed tip `2234f7e4`) | **MERGED & PUSHED TO ORIGIN/MAIN** |
| **Live Smoke Probe** | `curl.exe -I -s https://numista.ai` &rarr; **`HTTP/1.1 200 OK`**<br>`curl.exe -i -s https://numista.ai/api/` &rarr; **`HTTP/1.1 401 Unauthorized`** (`{"detail":"Authentication token missing or invalid"}` confirming Cloud Run rewrite) | **PASS** |

---

## 2. Changes Included in This Live Release

1. **Full Mint Invoice Pack Pipeline (Plan 4.1 / NET-565/572):**
   - Mint packing slip OCR + parser enrichment with fee & date handling.
   - Batch valuation pipeline and order line-item splitting.
   - Automatic set expansion and container import pathways.

2. **Locked UX Improvements (NET-585 / FT Passed):**
   - **Fix 1:** Add-by-Cert once deduplication (modal dialog prevents accidental multi-adds).
   - **Fix 2:** 3-tap cert path streamlined flow.
   - **Fix 3:** Review Hub card storage location inline display.

---

## 3. Scope Boundaries & Hold Status

- [x] Live deploy authorized strictly for Mint-pack + UX fixes from tip `2234f7e4`.
- [x] **Zero catalog / Brain merge:** Gates 586, 588, 589, 590 remain strictly on **HOLD**. No writes made to live catalog or Firestore collections.
- [x] **Agent Builder scale:** Zero scale beyond NET-594 Week-1 proofs.
- [x] Live/main deploy lock re-engaged immediately.

---

## 4. Next In Queue

1. Transmit radio `NET-596` acknowledgment and `NET-597` completion report to Grok CoS.
2. Advance to **NET-594** (Agent Builder Week-1 proofs on `numista-morgan-pilot`).
