# Independent SAG review images22

Full plan submitted; packet chars 265542
Usage: {"prompt_tokens": 78869, "completion_tokens": 2365, "total_tokens": 120961, "prompt_tokens_details": {"text_tokens": 78869, "audio_tokens": 0, "image_tokens": 0, "cached_tokens": 1152}, "completion_tokens_details": {"reasoning_tokens": 39727, "audio_tokens": 0, "accepted_prediction_tokens": 0, "rejected_prediction_tokens": 0}, "num_sources_used": 0, "cost_in_usd_ticks": 4085620000}

## Score / verdict

| Item | Result |
|---|---|
| **Score** | **76 / 100** |
| **Verdict** | **FAIL** (PASS requires ≥ 95) |
| **Scope reviewed** | Plan readiness only. No tools, tests, or compiles were run. |
| **Pin used** | `4d17ca5e` git-show excerpts. `b0b05808` catalog (3202 rows) is not at this pin; the plan does not treat it as if it were. |
| **Execution** | **Do not apply.** Founder YES is not authorized by this review. |

Deductions: −8 −5 −4 −3 −2 −2 = −24.

---

## Must-fixes

### MF-1 — BLOCKER (−8): `isOwnedStorageUrl` does not compile
Proposed guard in §3.A:

```dart
if (trimmed.isEmpty || trimmed.contains(r'\')) return false;
```

In Dart, a raw string cannot end in a single backslash (`r'\'` is a compile-time error). The security function, and therefore `owned_storage_url_test.dart`, cannot be analyzed or run as written.

The §6.1 case `r'/\evil.com/coin.jpg'` is valid Dart and is not a substitute. Fix the implementation with a normal string (`'\\'`) or equivalent, and keep the reject-any-backslash behavior.

v2.2’s pre-parse `.` / `..` segment check is the right shape for the stated Dart `Uri` normalization issue. It is not landable until this parses.

### MF-2 — HIGH (−5): confirmed-user branch blanks cards the pin would still fill
Pin `hasUserUploadedPhotos` (`canonical_mint_asset_service.dart:27–50`) is true for `scan_source` of `microscope` / `hardware agent`, and for `stored_obv` / `stored_rev`, with no requirement that `image_url_*` be a displayable HTTPS URL.

Pin `_CollectionCardImage` (`my_collection_screen.dart:6369–6406`) then skips canonical (`resolveFromMap` returns null at `:156–157`) and, if `_cleanUrl` of `_F.imageObverse` / `_F.imageReverse` (`:76–77`, values `image_url_obverse` / `image_url_reverse`) is empty, **reference-fetches**.

§3.C `_select()` does not do that:

```dart
if (userUploaded) {
  final selected = rev.isNotEmpty ? rev : obv;
  if (selected.isNotEmpty && isOwnedStorageUrl(selected)) return _Selection.image(...);
  return const _Selection.placeholder('U|unowned'); // also when selected is empty
}
```

`extractUserPhoto` never reads `stored_obv` / `stored_rev`. Empty selection and a non-empty unowned selection share one placeholder path, so reference is suppressed.

That re-breaks images for microscope / `stored_*`-only / `gs://…/users/…` docs ( `gs://` is ignored by both `_cleanUrl` `:6363` and `extractUserPhoto`, but `isUserUrl` still matches `/users/`).

Required plan change:
- Non-empty selected URL that fails `isOwnedStorageUrl` → placeholder; do not render it; do not fall through to canonical (keep MF-SAG-I1).
- User-upload signal with **no** extractable HTTP(S) side → shipped reference step, not a hard placeholder.
- Either display owned `stored_obv` / `stored_rev`, or state that those fields are signals only and add tests for both.
- Add widget cases: `scan_source: microscope` with empty photo fields expects a reference fetch; `stored_obv` owned URL behavior must be asserted, not implied.

### MF-3 — HIGH (−4): rollback and preflight do not match the apply path
§4.D aborts on a dirty tree (`git diff --quiet && git diff --cached --quiet`). §7’s failure mode is `flutter test` **before** a commit. The revert script never runs, and there is no branch-only `git reset --hard <pre-apply SHA>` guarded by `HEAD == p7-v8.9` and never `main`.

§4.A also requires `git diff --quiet 4d17ca5e HEAD -- numista_mobile/`. §4.C Step 1 (Cards) edits `canonical_mint_asset_service.dart` and `my_collection_screen.dart`. After that commit, this Images preflight fails closed for the wrong reason. The Images diff anchor also assumes Cards already inserted `import '../widgets/collection_card_valuation_row.dart'`, which is **not** in the pin (`my_collection_screen.dart:43–45` ends at `denomination_canon.dart`).

Required: record pre-apply SHA; on test failure reset only `p7-v8.9` to that SHA if uncommitted, or `git revert` the Images commit if committed; push only `p7-v8.9`; assert `origin/main` stays `9f04550a`. State the preflight as “mobile tree equals `4d17ca5e` plus the already-reviewed Cards commit” once Cards has landed.

### MF-4 — MEDIUM (−3): `canonicalYear` is not on the pin
Every `CollectionCardImage` calls `CanonicalMintAssetService.canonicalYear(data)` from `initState` → `fromData`, including paths that never fetch.

At `4d17ca5e`, line 77 is `static String extractSku`, and the year helper is private `_normYear` at `:72–76`. This plan does not quote a Cards signature. Against the pin, the widget and §6.2 do not compile. Quote the exact static signature Cards must land, or inline the pinned `_normYear` behavior in this plan so Images is not an unquoted external symbol.

### MF-5 — MEDIUM (−2): `package:numista_ai/` is uncited
New widget, utils, and both tests import `package:numista_ai/...`. No supplied `4d17ca5e` file uses that package; existing libraries use relative imports. `pubspec.yaml` `name:` is not quoted. Quote it from the pin or use relative imports. This is an unverified compile path, not a proven wrong name.

### MF-6 — MEDIUM (−2): preview deploy is in the YES scope with no safe command
`firebase.json:7` hosting site is `numista-vault`; `:2–4` also points at Firestore rules. Header YES includes preview-channel deploy and excludes Firestore writes, production `numista-vault.web.app` / `numista.ai`, and rules changes. §4 never gives a command.

Required in-plan: one preview-only hosting channel command for `preview-catalog`, cwd `numista_mobile`, and an explicit forbid of `firebase deploy`, `--only firestore`, rules/index deploys, and production hosting. Firestore writes/seeding remain a separate Founder YES.

---

## Verified against `4d17ca5e` (do not churn)

These plan quotes match the supplied pin excerpts: `_CollectionCardImage` `:6356–6420` (no timeout at `:6399–6406`); `_F.imageObverse` / `_F.imageReverse` `:76–77`; `hasUserUploadedPhotos` `:31–50`; `coin_image_service.dart` `_collection` `:17` and `public_url` reads `:567` and `:583`; `ref_image_widget.dart:55–57`; CSP `firebase.json:276` (img-src lacks `firebasestorage.googleapis.com`; `*.googleapis.com` is not an img-src fallback); `build_image_index.py` `SCAN_TARGETS` `:53–103` and `public_url` `:301–303` (space → `%20` only); `build_currency_image_index.py:38–42` and `:267`; `promote_user_photos.py:34–37` and `:130` with dest shape `reference/{program_slug}/{year}_{program_slug}_{side}.jpg`.

Allowlist roots for those three emitters are the right prefixes. v2.2 in-root `a/../x.jpg`, `./x.jpg`, and cross-root `../numista-reference-library/` checks match the tests. Balabaskar fixture matches `:84`. Stripe OFF, alerts-not-caps, no promo-code material, US image scope, and anon fixtures (no collector emails) are stated correctly. `b0b05808` is not used as the code pin.

---

## Polish (not scored)

- §7 `flutter test test/utils/...` only works with cwd `numista_mobile`.
- Preflight prose locks `origin/main` at `9f04550a` but the script never `rev-parse`s it.
- Relative `/assets/...` accepted by the guard will not load through `Image.network` (absolute URL required). Dead allow, not a third-party bypass.
- No widget test for unowned reverse + owned obverse → placeholder (the stated “ignore the other side” rule).

## Uncertainties (not scored; not run)

- `firebase_options.dart:55` and screen `:5015` / `:5489` are cited but not in the supplied excerpts. Form A bucket string is unverified here. Project id `studio-9101802118-8c9a8` is in `firebase.json`.
- `c294fd3c` vs `4d17ca5e` is two different hashes; their relationship is not in the packet.
- `studio-9101802118-8c9a8-uploads` is only a substring in `hasUserUploadedPhotos:37`, not an emitter. Ownership of that GCS root is not shown.
- FutureBuilder cases use one `pump()`; completion timing was not executed.
- Cards denomination edits at pin `:431–435` could move Case 8; not in this packet.
- A download-token substring `%2e` would be over-rejected. Normal `getDownloadURL` tokens are not shown to contain that.

---

## Next gate

Revise to a plan-only v2.3 that closes MF-1–MF-6 with paste-ready snippets and tests. Re-submit for a fresh SAG score. **No code, tests, commits, hosting deploy, or Firestore writes until a later SAG ≥ 95 and a separate Founder typed YES.** That YES still does not authorize Firestore writes, rules, seeding, or production deploy. `origin/main` stays `9f04550a`. Stripe stays OFF. Alerts only, no spend caps.