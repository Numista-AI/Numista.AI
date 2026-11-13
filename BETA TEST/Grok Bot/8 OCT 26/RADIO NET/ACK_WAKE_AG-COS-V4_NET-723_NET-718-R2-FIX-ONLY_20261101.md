# ACK - WAKE AG CoS v4 - NET-723 - NET-718 SECURITY PLAN R2 FIX-ONLY
**From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3` | `eric@numista.ai` | PAYG `numista-qc`)  
**To:** Grok CoS (GB CoS), Argon (SAG Technical Auditor), Founder Eric  
**Date:** 2026-11-01 18:25 EST  
**Subject:** ACK WAKE NET-723 & NET-718 R2 Fix-Only Plan Filed  

### 1. Acknowledgment & Actions Taken
1. **MF1 (Rules Citations Verified Byte-for-Byte against origin/dev:numista_mobile/firestore.rules):**
   * Verified `isOwner` helper is at lines 13-15.
   * Verified `/public_wishlists/{token}` is at lines 250-254 (assessed `allow create: if request.auth != null;` and hardened to Cloud Run server-only write).
   * Verified `/family_groups/{familyGroupId}` open read gap is at lines 278-281 (hardened to restrict read to primary owner UID or member emails).
   * Verified rules reference in `numista_mobile/firebase.json:2-4`.
   * Verified deployment target in `.github/workflows/deploy-production.yml:68-71` runs `working-directory: numista_mobile` deploying `numista_mobile/firestore.rules`.
   * Verified `/users/{email}/coins/{coinId}` range is lines 40-67.
2. **MF2 (In-Memory Redaction & Zero Raw Storage Invariant):**
   * Direct GCS signed URL route `/api/import/start` (`main.py:7312-7359`) is deprecated/redirected to in-memory `/api/import/upload`.
   * Completely eliminated `/raw/` GCS storage prefix.
   * In-flight bytes held purely in memory buffer; blackout redaction applied in memory before write to `{email}/imports/{session_id}/redacted/{safe_name}`. Zero unredacted files touch GCS or temp disk.
   * Cited and extended ALREADY imported/existing Document AI client (`main.py:19`, `main.py:5080-5150`).
   * Dry-run backfill script covers historical `imports/*/raw/*` and GCS versioning/soft-delete retention.
   * Dry-run report logs item counts, file sizes, and coordinate bounding boxes ONLY (zero customer names or PII strings).
3. **MF3 (Invented Facts & Phantom Routes Expunged):**
   * Removed all references to `$12.99`; cited server-verified amount and real v3.2 prices ($4.99/mo, $29.99/yr, $95.94).
   * Replaced inaccurate `main.py:60-120` Secret Manager claim with container environment variable injection (`os.environ`), citing `feedbackIntelligence.js:21` for direct SecretManagerServiceClient.
   * Replaced nonexistent photo routes with real routes (`/api/identify_coin_photo`, `/api/identify_group_photo`, `/api/coin_crop`, `/api/analyze_binder_scan`, `/api/analyze/grade-coin`, `/api/scan/upload_document`, `/api/ai/chat`, `/api/import/upload`).
   * Labeled Section 10.1 Privacy Policy text accurately as current origin/dev text vs `[PROPOSED after NET-706 R5 Meta Pixel Enablement]`.
   * Quoted NET-706 R5 lines 160-166 Purchase event correctly (`js.context.callMethod('fbq', ...)` with `amountUsd`).
4. **SF1-SF5 Addressed:**
   * SF1: Full-history `gitleaks git --verbose` across all branches required.
   * SF2: Document AI and Identity Platform costs marked `[TBD]`.
   * SF3: Universal EXIF sanitizer specified with correct 1-parameter HEIC baseline and universal image format support (JPEG/PNG/WebP/HEIC).
   * SF4: Dropped `owner_email` from public wishlist snapshot (`owner_alias` already exists at line 12440).
   * SF5: Consistently labeled all proposed artifacts (`mfa_security_modal.dart`, `DELETE /api/user/account`, etc.) as `[PROPOSED]`.
5. **Open Eric Decisions:**
   * Kept [ERIC DECISION 1] (2FA valuation threshold) and [ERIC DECISION 2] (Purchase value in Pixel & site copy approval) open.

### 2. Deliverable
* `SECURITY_PLAN_NET-718_R2_USER-PROTECTION_20261101.md` filed across all 5 standard folders.
* Review baton passed to Grok CoS and Argon: `BATON_NET-723_GROKCOS-ARGON_NET-718-R2-REVIEW_20261101.md`.
