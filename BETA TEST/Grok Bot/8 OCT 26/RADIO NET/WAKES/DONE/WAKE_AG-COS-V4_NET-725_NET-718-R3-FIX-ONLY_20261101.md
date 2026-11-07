**STATUS: SUPERSEDED 2026-11-01 6:40 PM ET — Eric directed GB CoS to author R3 ("Take advantage of the Ultra plan and you do it.", 6:25 PM ET). AG: do NOT work this; move on to NET-647 R2.8.10.**

# WAKE - AG CoS v4 - NET-725 - NET-718 SECURITY PLAN R3 FIX-ONLY
From: Grok CoS | 2026-11-01 6:25 PM ET | DOCS-ONLY. No code edits, commits, pushes, deploys, GCS/Firestore writes.
R2 scored 68 REVISE (RADIO NET\COS_SCORE_NET-718-R2_68_REVISE_20261101-1825EST.md). File SECURITY_PLAN_NET-718_R3_USER-PROTECTION_20261101.md (INBOX + RADIO NET) fixing ONLY:
1. MF1: Re-extract EVERY code block with `git show 32d4b42e:<path>`, and label each with that commit. Fix: scan_service/main.py:695, estate_fiduciary_service.dart:71 (custodialLocation), main.py:7500 and 7528-7544, 12734 and 12743-12755 (no auth dependency; unauthenticated create-share must be addressed), 11977-11984, stripe_config.py:28 (.env fallback), drop functions/feedbackIntelligence.js (absent), deploy-production.yml:103, firestore.rules comment lines 247-249/277, privacy.html:324 and privacy_screen.dart:137-139 (actual "4. Sharing Your Information"), drop the index.html:43-56 pixel claim, and use _convert_heic_to_jpeg at 4254-4279.
2. MF2: Replace the invented buckets numista-vault / numista-vault-imports with the real ones: USER_CONTENT_BUCKET "numista-uploads-studio-9101802118-8c9a8" (IMPORT_BUCKET, main.py:7038); import_routes BUCKET_NAME; main.py:12587 default. Apply them in redaction, backfill and deletion.
3. MF3: Add import_routes.py:50 `imports/{uid}/...` to redaction and backfill. The dry-run report holds the path HASH only. Cite the source for the Document AI retention claim or mark it UNVERIFIED. The 7543 fallback also goes through redaction.
4. SF1: Correct the export/annual price labels per v3.2 (Lifetime on hold). SF2: remove the "push to p7-v8.9" step (docs-only).
Keep the 3 Eric decisions open. Change nothing else. File the plan, a RADIO_OVER, and BATON_NET-725 review baton for Grok CoS/Argon.

