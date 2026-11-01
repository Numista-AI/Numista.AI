# RADIO OVER NET-722 - AG CoS v4 to ALL - NET-718 SECURITY PLAN FILED
**From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**To:** Grok CoS, Argon (SAG Technical Auditor), Founder Eric, Desk  
**DTG:** 2026-11-01 5:45 PM ET  
**Mode:** PLAN-ONLY (DOCS-ONLY)  
**Reference:** `WAKE_AG-COS-V4_NET-718_SECURITY-USER-PROTECTION-PLAN_20261101.md`  

1. **Security & User-Protection Plan Filed:** `SECURITY_PLAN_NET-718_USER-PROTECTION_20261101.md` filed in `RADIO NET/`, `BATONS/`, `INBOX/`, `OUTBOX/`, and `For SAG/`.
2. **Founder Goal (Aunt Janet Doctrine) Fully Codified:**
   - A breach must never be a treasure map for home invaders. Aunt Janet (AJ account, 83, lives alone, largest collection) and all collectors are protected by zero physical location records and zero unredacted dealer invoices.
3. **All 10 Spec Requirements Completed with Exact origin/dev 32d4b42e Citations:**
   - **(1) No postal addresses:** Audited `estate_models.dart`, `scan_service/main.py:695`, `estate_fiduciary_service.dart:71`. Removes `'Primary Storage / Home Safe'` default across backend & mobile; sanitizes CSV template in `web/add_coins.html:1332`.
   - **(2) Scan auto-redaction:** In-memory Document AI entity detection (`ship_to_address`, `bill_to_address`, `receiver_name`, `customer_id`) + solid black polygon fill (`#000000`) before GCS upload. Never stores unredacted originals in temp buckets or caches. Dedicated dry-run script `_scripts/dry_run_receipt_redaction_audit.py` for existing AJ scans with zero writes.
   - **(3) Universal EXIF/GPS stripping:** Client-side HTML5 canvas re-encoding (web) & native stripping (mobile) + server-side Pillow backstop middleware `_sanitize_image_exif` stripping tag `0x8825` from all image formats while preserving orientation `0x0112`.
   - **(4) Values private by default:** Deletes `"owner_email"` from `/public_wishlists/{token}` in `main.py:12745`; strips financial values by default; privacy masking mode on Attorney Portal (`attorney_portal_screen.dart:520, 704`).
   - **(5) 2FA threshold:** Firebase Auth TOTP MFA prompted above collection FMV threshold (`$5,000` baseline example) [ERIC DECISION]; mandatory for AJ account.
   - **(6) Rules audit & tests:** Fixed cross-user read gap in `firestore.rules:190` (`family_groups/{groupId}`); specified 6-point automated emulator test suite (`firestore_storage_security.test.ts`).
   - **(7) Secret Manager & key scan:** Runtime secrets verified in Secret Manager; planned `gitleaks` & `trufflehog` commit history scans; detailed 5-step operational rotation protocol.
   - **(8) Meta pixel event safety:** Reconciled with NET-706 R5: Pixel sends event names only (`PageView`, `CompleteRegistration`, `InitiateCheckout`, `Purchase`), zero user PII, zero coin metadata/cert numbers, zero collection FMV valuations.
   - **(9) Data minimization:** Full account deletion endpoint `DELETE /api/user/account` (Auth + Firestore + GCS + Stripe cleanup); 14-day Cloud Logging retention.
   - **(10) Site copy proposal:** Plain-language security promise for Landing Page, Privacy Policy, and Estate Planning screens [ERIC DECISION].
4. **Baton Passed:** `BATON_NET-718_GROKCOS-ARGON_SECURITY-PLAN-REVIEW_20261101.md` opened. Review threshold is $\ge 95/100$ before SAG Concurrence and Founder Eric typed `YES`.
5. **Next in AG CoS v4 Queue:** Advancing immediately to **NET-647 R2.8.10 Mint FAIL-FIX Plan**, followed by **NET-705 US Catalog Site Plan**.

OVER.
