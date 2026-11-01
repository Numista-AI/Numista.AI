# BATON NET-723 - Grok CoS & Argon - NET-718 SECURITY PLAN R2 REVIEW
**STATUS: OPEN 2026-11-01 6:25 PM ET** - holders: Grok CoS (GB CoS), Argon (SAG Technical Auditor).  
**Target File:** `RADIO NET/SECURITY_PLAN_NET-718_R2_USER-PROTECTION_20261101.md`  
**Passed By:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**Mode:** PLAN-ONLY (DOCS-ONLY). Zero code edits, zero builds, zero deploys, zero GCS/Firestore writes.  
**Review Threshold:** $\ge 95/100$ before SAG Concurrence $\rightarrow$ Founder Eric typed `YES`.  

### R2 Fixes Applied:
1. **MF1 (Rules Citations Verified):** Cites exact verified lines in `numista_mobile/firestore.rules` on `origin/dev 32d4b42e`: `isOwner` lines 13-15; `/public_wishlists` lines 250-254 (assessed and hardened to Cloud Run server-only); `/family_groups` lines 278-281 (restricted to primary owner / members); active deployment target `numista_mobile/firebase.json:2-4` via `.github/workflows/deploy-production.yml:68-71`; `/users/{email}/coins/{coinId}` lines 40-67.
2. **MF2 (In-Memory Redaction & Zero Raw Storage Invariant):** Deprecated direct signed-URL ingress in `/api/import/start` (`main.py:7312-7359`); eliminated `/raw/` GCS storage prefix across all routes; enforced in-memory blackout before persistence to `{email}/imports/{session_id}/redacted/{safe_name}`; extended ALREADY existing Document AI client (`main.py:19`, `main.py:5080-5150`); backfill covers GCS object versioning and soft delete; dry-run report outputs counts/coordinates ONLY (zero extracted text strings).
3. **MF3 (Invented Facts & Phantom Routes Expunged):** Expunged `$12.99`; cited server-verified amount and real v3.2 prices ($4.99/mo, $29.99/yr, $95.94); accurately cited container environment variable secret injection (`os.environ`) and `feedbackIntelligence.js:21`; cited real photo routes (`/api/identify_coin_photo`, `/api/identify_group_photo`, `/api/coin_crop`, `/api/analyze_binder_scan`, `/api/analyze/grade-coin`, `/api/scan/upload_document`, `/api/ai/chat`, `/api/import/upload`); labeled Privacy Policy text accurately as current origin/dev text vs `[PROPOSED after NET-706 R5 Meta Pixel Enablement]`; quoted NET-706 R5 lines 160-166 Purchase event correctly.
4. **SF1-SF5 Addressed:** Full-history `gitleaks git --verbose` pass criterion; Document AI & Identity Platform costs marked `[TBD]`; universal EXIF sanitizer with correct baseline; dropped `owner_email` from public wishlists (`owner_alias` already exists at line 12440); consistently labeled all proposed artifacts with `[PROPOSED]`.
5. **Open Eric Decisions:** Kept [ERIC DECISION 1] (2FA threshold) and [ERIC DECISION 2] (Purchase value in Pixel & site copy approval) open.

### Queue Continuity:
- Grok CoS & Argon: Score NET-718 R2 Security Plan.
- AG CoS v4: Advances to **NET-647 R2.8.10 Mint FAIL-FIX Plan**, followed by **NET-705 US Catalog Site Plan**.
