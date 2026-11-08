# REVISE NET-814 v1.9 → v2.0 (SAG 64 FAIL) — verified fix list
Verifier: GB CoS executor, 8 Nov 2026 ~11:52 AM ET. Tally: REAL 7 · FALSE 1 · UNCLEAR 1

## Must-fixes (priority order)
1. **[REAL MF-3] Fail-closed pricing.** Plan lines 910 (`$30 / 6 months`) and 913 (world coverage "2027") are still specified. The pin's established copy (public_info_screens.dart:362/396/407/412) is free beta. Generator + in-app copy must emit ONLY those four strings until a separate Founder YES. Add negative asserts that the proposed price and world-coverage sentences are absent. US-only stays. No promo codes.
2. **[REAL MF-1, corrected] One firebase.json edit per branch.** The hunk header `@@ -115,6` (line 362) is wrong: pin `/claim/**` is at :130. Correction to SAG: the pin has no catch-all rewrite before `/claim/**`, so appending works ON THE PIN. The "never runs" problem applies only to origin/dev, where `/catalog/**` already exists. Write two explicit edits. Pin: insert both rules once after `/claim/**`. origin/dev (now `cc815522`, not `bde8b402`): change only the existing `/catalog/**` destination.
3. **[REAL MF-2] Tests match real strings.** Test at line 1050 expects `'Reference Catalog'`, but the b0b05808 screen shows `'Public Catalog'` (:270) and `'U.S. Numismatics Catalog'` (:335). Add a fixture/asset override + Image.network mock before `pumpAndSettle`. Replace the hardcoded `PREVIEW_URL …-xyz.web.app` (936) with the URL captured from `hosting:channel:deploy` (810). Run widget tests BEFORE the preview deploy.
4. **[REAL MF-4] Image guard placement.** `isApprovedCatalogImageUrl(String)` (731) must receive `primary_image['url']` / `type_image['url']`. Insert it before the `Image.network` call sites (b0b05808 :918, :1106). Fall back to the existing placeholder. Put the guard in a named production file in §7.5. Add call-site asserts.
5. **[REAL MF-5] No invented mintage source.** Line 781 reads `mintage?['source_name'] ?? 'US Mint Records'`, but `_buildMintageRow` uses only `value`, `label` and `source_url`. Drop `source_name` and the default. Render plain text with no `launchUrl`.
6. **[REAL MF-6] Per-coin HTML from build output.** The sample (444, `<base href="/">`) is not the template. Rule: clone `build/web/index.html` after `flutter build web`, keep the bootstrap payload, and replace only title/description/canonical/OG/Twitter. Emit `og:image` only from a guarded non-null `primary_image['url']`.
7. **[REAL MF-9] Negative OG test.** Assert the 1921-P Morgan page has no `og:image` / `twitter:image`. The row exists on b0b05808, but its field values were not re-checked here.
8. **[UNCLEAR → just fix] MF-7 manifest.** Line 29 references `lib/routing/public_catalog_route.dart`, and 1132 references `test/services/catalog_image_guard_test.dart`. I didn't confirm whether §7.5 lists them. Make sure §7.5 lists both, plus the guard production file.
9. Rollback: **git revert only, no `reset --hard`**. Drop `tac`. Push `p7-v8.9`/dev only with its own YES. Main stays `9f04550a`.

## Rejected (FALSE)
- **[FALSE MF-8]** "`5,142 Reference Coins` is ungrounded": it exists at `numista_mobile/lib/screens/login_screen.dart:338` and `:466`, on both pin `4d17ca5e` and origin/dev. Keep the instruction (line 628) but cite those two lines. The replacement figure must come from the verified 3,202-row count (b0b05808). Don't round it up.

## Polish
Fix the v1.9/v1.8 title drift; fix the header label 135–234 → 135–280; remove the dead second `main` check; try/catch the double `Uri.decodeComponent`; whitelist `/catalog_unknown.html` in `isKnownPath` or note it.
