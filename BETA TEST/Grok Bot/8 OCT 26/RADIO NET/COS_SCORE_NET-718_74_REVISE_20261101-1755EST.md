# COS SCORE - NET-718 SECURITY & USER-PROTECTION PLAN - 74/100 REVISE
Scorer: Grok CoS (GB CoS) | 2026-11-01 5:55 PM ET | docs-only | Plan: RADIO NET\SECURITY_PLAN_NET-718_USER-PROTECTION_20261101.md (RADIO NET-722, baton BATON_NET-718_GROKCOS-ARGON_SECURITY-PLAN-REVIEW) | origin/dev 32d4b42e
Two [ERIC DECISION] items (2FA threshold; Purchase value vs no-value / site copy approval) treated as open questions, not defects.

## Verdict: 74/100 REVISE. Not ready for SAG.
All 10 spec items addressed with per-item state/gap/fix/test/owner/effort/risk + Lessons section, backfill Phase A is dry-run-only, new items mostly marked PROPOSED. But the rules audit cites wrong lines, the redaction design leaves existing raw-original write paths open (violates Eric's no-unredacted-original rule), and there are invented/unverifiable facts.

## Verified correct
scan_service/main.py:695 and estate_fiduciary_service.dart:71 'Primary Storage / Home Safe'; estate_models.dart:215/262/288; estate_planning_screen.dart:608-610, 4076, 4196; add_coins.html:1315 maskPII, 1331-1332 "Safe Box A"; auth_service.dart:7-23 PIN; login_screen.dart:127/154; main.py:7396 /api/import/upload, 7499 /api/import/start, 8899 view_url, 4254-4279 HEIC GPS strip; main.py:12733-12750 public wishlist writes owner_email (12745); attorney_portal_screen.dart:520/704; wishlist_screen.dart:134/186; image_picker imports; storage.rules:9-12 owner-only; camera_capture_service_web.dart exists. family_groups open read is a REAL gap (good catch) - but at the wrong line.

## MUST-FIX
MF1. Firestore rules citations do not match firestore.rules (spec item 6 check fails):
- isOwner is lines 13-15 (17-21 is the estate-report token comment).
- /public_wishlists is lines 250-254 (182 is /config). Also note `allow create: if request.auth != null` (any signed-in user can create a public doc) - assess it.
- /family_groups open read is lines 278-279 (190 is /coin_image_index, which is intentionally auth-read).
- "per firebase.json:134-136" is the headers block; the firestore rules reference is numista_mobile/firebase.json:2-4. Note a second numista_backend/firestore.rules + firebase.json exists - state which is deployed.
- Verify and cite the real line range for /users/{email}/coins (40-70 unverified as stated).
MF2. Redaction design does not meet "no unredacted original anywhere, incl. temp":
- /api/import/start (7499-7548) issues GCS SIGNED UPLOAD URLs - the client writes raw files straight to GCS, bypassing in-memory redaction. Raw paths also written at main.py:7377, 7434, 7931, 8405, 8489 (`{email}/imports/{session_id}/raw/...`). Plan must cover every path: remove/redirect the signed-URL route, eliminate the raw/ prefix, and state how in-flight bytes never touch GCS, logs, or Document AI request logging.
- Document AI is ALREADY used (main.py:19, 2047, 5008-5014 us-documentai). Cite and extend the existing client, do not describe it as new.
- Backfill must include existing imports/*/raw/* objects, GCS object versioning/soft-delete retention, and the dry-run report must contain counts/coordinates only - NO extracted name/address text.
MF3. Invented / unverifiable facts:
- `$12.99` (section 8, twice) is not a v3.2 price and does not appear in NET-706 R5. Use v3.2 prices or "server-verified amount".
- "main.py:60-120 retrieves credentials ... Secret Manager (projects/numista-qc/secrets/*)": line 60-62 is CORS; no Secret Manager/projects path found. Cite real evidence (e.g. main.py:11978 EBAY_CERT_ID comment) or mark UNVERIFIED.
- Routes `/api/coins/{id}/photo` and `/api/chat/photo` do not exist on origin/dev - cite real photo-ingest routes.
- Section 10.1 quotes privacy.html:325 / privacy_screen.dart:139 with NET-706 R5 proposed text; origin/dev:325 still reads "...or share your personal data with third-party advertisers or marketers". Label as "after NET-706 R5".
- Section 8 cites "NET-706 lines 161-168" as JS `fbq(...)`; R5 lines 161-164 are Dart js.context.callMethod. Quote correctly.

## SHOULD-FIX
SF1. Section 7 test `gitleaks detect --no-git` does not scan history, and `trufflehog --since-commit 9f04550a` limits history; use full-history `gitleaks git` (all branches) as the pass criterion.
SF2. Costs: "based on published standard tiers" with no figure/source - mark Document AI and Identity Platform costs TBD (with source to be cited).
SF3. EXIF sanitizer: signature mismatch (doc says 2 params, code 1); pops only 3 tags while claiming "all PII EXIF"; img.save with exif for PNG/WEBP; test must cover JPEG/PNG/WEBP and the HEIC path.
SF4. Section 4.3 "replace owner_email with owner_alias" - owner_alias already exists at 12746; just drop owner_email (and audit existing /public_wishlists docs for stored emails - dry-run).
SF5. Mark mfa_security_modal.dart, test_rules/*.test.ts, dry_run_receipt_redaction_audit.py, DELETE /api/user/account consistently as [PROPOSED] (some are).

## Score breakdown
Spec coverage 10 items 18/20 | Repo citation accuracy 12/20 (MF1, MF3) | Eric rules (no address / no unredacted original) 10/20 (MF2) | Dry-run backfill 8/10 | Rules claims vs files 4/10 | PROPOSED marking 8/10 | No invented costs/prices 6/10 | Lessons/format 8/10 = 74 (rounded from component judgment).
Next: NET-723 fix-only R2.
