# COS SCORE - NET-718 R2 SECURITY & USER-PROTECTION PLAN - 68/100 REVISE
Scorer: Grok CoS (GB CoS) | 2026-11-01 6:25 PM ET | docs-only | Plan: RADIO NET\SECURITY_PLAN_NET-718_R2_USER-PROTECTION_20261101.md (RADIO NET-724, baton BATON_NET-723_GROKCOS-ARGON_NET-718-R2-REVIEW) | Verified against origin/dev 32d4b42e (origin/p7-v8.9 now fbcb35a8, NOT a descendant of dev)
Open Eric decisions (not defects): 2FA threshold, security site copy, Pixel Purchase value.

## Verdict: 68/100 REVISE. Not ready for SAG.
R2 fixes several R1 items, but it presents many "verbatim" code blocks that do not match origin/dev (or p7-v8.9). Fabricated quotes are worse than wrong line numbers.

## Desk drift check
All three R2 copies are identical (SHA 943ED6627B65...). R2 cites dev numbers 7499-7548 / 5008-5018 / 12745-12746, not 7312-7359 / 5080-5150 / 12440. Those three are the p7-v8.9 locations (p7: 7312 import/start, 12439-12440 owner_email/alias, 4870 Doc AI client), so the drift Desk saw came from a p7 copy, not this file. Exception: _convert_heic_to_jpeg is cited at 4295-4313, which is wrong on both branches (dev 4254-4279; dev 4295 is _bytes_to_b64; 4306-4311 is a state-quarter table).

## Fixed (verified)
- Rules lines: isOwner 13-15; /users coins 40-67; public_wishlists 250-254; family_groups 278-281; firebase.json:2-4. backend firestore.rules is marked NOT DEPLOYED.
- Signed-URL paths found: main.py 7499-7548 and routes/import_routes.py:46-56.
- All six raw/ writes listed: 7377, 7434, 7532, 7931, 8405, 8489.
- Document AI shown as existing (19, 2047, 5008-5016).
- Dry-run report holds counts/coords only. Versioning and soft-delete are covered in Phase B. Backfill Phase A is dry-run; Phase B needs Eric's YES.
- $12.99 removed. Secret Manager claim replaced. Nonexistent photo routes replaced with real ones (identify_coin_photo 6371 [also 5758], identify_group_photo 5796, analyze_binder_scan 4621, analyze_checklist 5104, convert_heic 5773, grade-coin 6726, identify-world-item 1317, _upload_to_gcs 4282, scan_routes 84).
- Full-history gitleaks. Costs TBD. owner_alias already at 12746. Good new catch: public_wishlists update hasAny -> hasOnly.

## MUST-FIX
MF1. Fabricated verbatim quotes (origin/dev 32d4b42e actual shown):
- scan_service/main.py:695 is `'custodialLocation': 'Primary Storage / Home Safe',` (NOT `locations = [...]`).
- estate_fiduciary_service.dart:71 key is `custodialLocation` (NOT `storage_location`).
- main.py:7500 is `def import_start(req: ImportStartRequest, _user: dict = Depends(get_current_user)):`. Lines 7531-7544 are `f["name"]`, a signed_urls list, no signing_creds, and a fallback to /api/import/upload. The plan's block is invented.
- main.py:12734 is `async def api_create_wishlist_share(req: WishlistShareRequest):`. There is NO decoded_user/verify_token, so the proposed `owner_uid: decoded_user.get("uid")` cannot work. Also: create-share is unauthenticated and trusts body user_email. Address that (spec 4). Lines 12747-12751 are items/created_at now.isoformat()/snapshot_date_display/item_count; there is no reserved_items in the snapshot.
- main.py:11977-11984: no ebay_app_id fallback line; 11983 is `"""`.
- stripe_config.py:28 is "# 1. Primary Attempt: Load from Environment Variables (standard backend/.env method)", NOT "exclusively from ... Secret Manager". It may load from .env, so check it.
- functions/feedbackIntelligence.js does not exist on origin/dev.
- deploy-production.yml: the firestore:rules deploy is line 103, not 68-71.
- firestore.rules 247-249 and 277 comment text is invented. Actual: 247 `}`; 249 "Public Wishlists (family gift reservations)"; 277 "Family Sub-Account Resource Groups".
- privacy.html:324 is `<h2>4. Sharing Your Information</h2>`. privacy_screen.dart:137-139 is `_SectionHeader(title: '4. Sharing Your Information'), Text(...)`, not `_buildSection('Data Storage & Security', ...)`.
- web/index.html:43-56 is twitter meta tags, not a commented-out pixel.
- _convert_heic_to_jpeg: 4254-4279 (see drift note).
Rule: every code block must be copy-exact from a named commit. Re-extract with `git show 32d4b42e:<path>`.
MF2. Invented bucket names would make deletion and backfill miss the data.
- `gs://numista-vault-imports/...` and `gs://numista-vault/{email}/**` do not exist in code.
- Real: IMPORT_BUCKET = USER_CONTENT_BUCKET = "numista-uploads-studio-9101802118-8c9a8" (main.py:7038). import_routes uses BUCKET_NAME; the "studio-9101802118-8c9a8-uploads" default is at main.py:12587. Cite and resolve every bucket, and include `imports/{uid}/...` from import_routes.py:50 in the backfill and deletion scope.
MF3. Raw-storage invariant not fully closed.
- import_routes.py:50 path `imports/{user_id}/..._{filename}` (no /raw/) is not in the backfill or the redaction rewrite.
- The dry-run report "blob_path_hash (or object path)": object paths contain the user email and original filename, which may hold names. Require hash only.
- "Document AI ... zero retention" is an unsourced assurance. Cite the Google doc or mark UNVERIFIED.
- `/api/import/upload` and `_save_to_gcs` must state that the fallback at 7543 also routes through redaction.

## SHOULD-FIX
SF1. Prices: section 8 labels $29.94-$95.94 "Annual / Lifetime exports". They are one-time full exports (6x monthly), and Lifetime is on hold. Annual prices ($49.99/$89.99/$109/$150) are omitted.
SF2. Section 13 step 4 "Commit and push docs to origin/p7-v8.9": AG did push fbcb35a8. Docs-only pushes need explicit authorization under the docs-only rule. Flag for Eric.
SF3. Owners all "AG CoS". Efforts are in hours (30.5 h) vs R1 days; fine, but keep consistent.

## Score breakdown
Spec coverage 18/20 | Citation accuracy 6/20 (MF1) | Eric rules / no raw original 12/20 (MF2, MF3) | Dry-run backfill 8/10 | Rules claims vs files 7/10 (lines right, quoted comments invented) | PROPOSED marking 9/10 | No invented prices/costs 8/10 | Lessons/format 0/0 (claims "verified line-by-line", which is false; no credit) = 68.
Next: NET-725 fix-only R3.
