# BATON NET-817 — To: AG CoS v4 — QUEUED AFTER NET-816: 780b Cards + 780c Images v1.5 (CoS 67 / SAG 64 FAIL on v1.4)

Source: GB CoS, 5 Nov ~8:05 PM ET. QUEUE: NET-816 Catalog v1.8 first; then NET-817. Deliver `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.5.md` and `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.5.md`. PLAN ONLY; Eric YES blocked. No Argon.

Scores: `COS_SCORE_NET-812_780b-780c-v1.4_20261105.md`, `SAG_SCORE_NET-812_780b-780c-v1.4_20261105.md`.

## Verified correct — preserve

1. Real valuation defect is at lines 3017–3023 and 3170. Proposed positive `cpgRetail` > 0 always wins over `enrichment_status == pending`; missing/zero uses pending and no AI fallback. Preserve this logic, subject to accessibility below.
2. Cent/nickel negative-lookbehind proposal is valid Dart. Local isolated Dart 3.11.3 check of the exact nickel expression produced `5¢=true`, `15¢=false`, `25c=false`, `5c=true`, `Jefferson Nickel=true`. SAG's SDK objection is explicitly corrected in the filed SAG note; do not remove the correct regex based on that false claim.
3. Real async API is `CoinImageService.fetchReferenceImages`; nonexistent `resolveReferenceAsset` is correctly removed. Real CSP is firebase.json:276; docs/MISSING_IMAGES.csv has 3,202 data rows. Bulk writes/mirroring stay out of scope.

## Blocking must-fixes for v1.5

1. **Use actual execution HEAD for rollback.** Current p7 is a07cf9f231daff6fa1066978c3ad03d5bfe08529, not 4c97c7f0 (11 docs commits behind). Record HEAD at execution and revert only execute commits, preserving intervening docs. Remove or narrowly scope old-SHA file-checkout language. Execute only p7: dev b0b05808 lacks `canonical_mint_asset_service.dart`.
2. **Supply a complete compiling widget.** Proposed `_CollectionCardImage` calls `_buildCoinImage` without defining it. Preserve real method at 6443–6478 or include it; ensure every returned image kind uses the correct renderer. Do not pass data/blob/local assets to `Image.network`; use https-only if that is the actual policy. Cache the async future instead of recreating it in every `build`.
3. **Propagate normalized year everywhere.** `extractSku` fallback does not update `resolveFromMap` line 172 or reference lookup dualRead. Use one canonical helper across extract/resolve/reference inputs. Test public `resolveFromMap` missing-year 26EA obverse/reverse, `1776-2026` preferring 2026, 2023 nickel not becoming 2026 commemorative, and year-gated designs.
4. **Never displace user photos.** Real helper detects `/microscope/`, `/users/`, `/user_uploads/`, `user_upload`, camelCase image fields and uploads. Proposed sanitizer accepts fewer paths and then can fall through to reference art. Define verified accepted first-party user paths, preserve the actual image, or show placeholder when user-owned data exists—never substitute unrelated reference art. Test every precedence step and external-host rejection before fetch.
5. **Correct the no-network claim and verification.** Reference lookup reads Firestore and then loads GCS images. Define permitted read-only network behavior, no writes/mutations, timeout/error terminal states and mocks. Correct canonical test path to `test/services/canonical_mint_asset_service_test.dart`; supply real new pricing/image test files, fixtures and assertions rather than nonexistent `-n` names.
6. **Cover related tracker regressions.** B27-8 Google Images/Kaggle paths remain and neither plan removes them; coordinate with NET-816 so only one implementation owns the change. B27-11 white-on-white detail remains; new pending gold is only ~2.06–2.24:1 and 13px positive price ~2.55:1 on light surfaces. Use theme-aware dark text >=4.5:1 plus automated and Eric field tests. B05N-7 upload preservation and B05N-8 valuation are partial; explicitly cover or bound the separate Cert Add financial/image flows.

Locks: main 9f04550a; Stripe OFF; zero code execution/deploy/Firestore writes/rules during review; no external messages; no AJ PII. Chain: NET-816 -> NET-817 AG CoS v4 -> GB CoS 95+ -> SAG 95+ -> Eric typed YES. No Argon.