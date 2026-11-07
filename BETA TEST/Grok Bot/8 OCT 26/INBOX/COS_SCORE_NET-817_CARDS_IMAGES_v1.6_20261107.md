# GB CoS score — NET-817 Cards v1.6 + Images v1.6

**Combined: 76/100 — FAIL.** Equal-weight plan scores: **Cards 84/100 FAIL; Images 68/100 FAIL**. Each must reach 95+; averaging never bypasses a failed plan.
Reviewed 7 Nov 2026, approximately 12:55–1:05 PM EST (America/New_York).

## Scope and evidence
Plans: `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.6.md` (C) and `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.6.md` (I).
Prior: `COS_SCORE_NET-817_CARDS_IMAGES_v1.5_20261106.md` (combined 65; Cards 72 / Images 58).

Repository on EDS_Laptop: `C:\Users\ericd\Documents\MyVertexProject`. Citations mean **p7 @4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235** unless noted. Verified: `origin/main` **9f04550a**; pinned plan ref `dev` **b0b05808**. Current `origin/p7-v8.9` tip is docs commit **2a61ec65** (not the execution pin). App lib citations below are from the pinned p7 ref, not tip.

Only machine-targeted read-only document/existence/hash/git show commands were used for the audit. Score/handoff files are written after scoring. Proposed snippets were inspected, not compiled or applied.

## Numbered must-fixes

1. **[I; blocking compile] Align the replacement widget to the real `CoinImageService` / `CoinImageResult` API.** Quoted plan code calls `CoinImageService.fetchReferenceImages(... mintMark: mintMark)` and then `CoinImageResult.empty()` / `snapshot.data!.images.first.gcsUrl`. On p7 @4d17ca5e the real signature is:

```dart
static Future<CoinImageResult> fetchReferenceImages({
  required String year,
  String? mint,
  String? denomination,
  String? series,
  String? subject,
}) async {
```

and `CoinImageResult` only exposes `obverseUrl` / `reverseUrl` (no `images`, no `empty()` factory):

```dart
class CoinImageResult {
  final String? obverseUrl;
  final String? reverseUrl;
  ...
  bool get hasAny => hasObverse || hasReverse;
}
```

Literal application does not compile. Pass `mint:` (keep series/subject as the live FutureBuilder already does), return `const CoinImageResult()` (or an explicit empty const) on timeout, and select `reverseUrl`/`obverseUrl` with the same subject steal-guard policy as today's widget.

2. **[I; ownership claim vs code] Honor relative same-origin and real Firebase Storage host forms, or stop claiming them.** `_isOwnedStorageUrl` begins with `if (!url.startsWith('https://')) return false;`, so relative `/...` paths never pass despite MF-4 / closeout text. It also accepts only `storage.googleapis.com` path prefixes and `numista-vault.web.app` / `numista.ai` hosts — not `*.firebasestorage.app` object hosts or preview-channel hosts. Ground the allowlist in the real URL forms production already stores (quote fixtures), include relative same-origin if that remains a requirement, and test accepted + rejected URLs through the **same** helper the widget will ship.

3. **[I; tests still not substantive] Pump `_CollectionCardImage` (or a public harness) with injectable boundaries.** `collection_card_image_test.dart` still does not construct `_CollectionCardImage`. The first test pumps a naked `Image.network`; the second recomputes a local `isOwned` bool. That does not prove user-photo precedence, fail-closed placeholder before reference fetch, semantic `_RequestKey` refresh, timeout terminal state, or allowlist rejection-before-fetch. Supply imports, a testable seam (or public wrapper), counted `fetchReferenceImages` calls, captured URLs, and negative assertions. Analyzer/compile proof remains a later separately authorized build.

4. **[C; promised pricing/contrast suite missing] Deliver the claimed `my_collection_card_pricing_test.dart` body (or stop claiming it).** Cards §1/closeout promises widget pumping, face-value fallback + 'Value pending AI estimate' chip (B05N-8), and WCAG AA ≥4.5:1 contrast checks. §6 only ships `canonical_mint_asset_service_test.dart` (year helper). The valuation snippet in §3.B sets `priceColor` but does not show the face-value / pending-chip branch. Supply the full pricing widget test file contents and the complete valuation UI diff that those tests assert.

5. **[C; wire denomination lookbehind to production or scope it out]** The negative lookbehind cases live only as a local `RegExp` inside the year-helper test file. They do not show where production card/denomination matching uses that pattern. Either cite/patch the real production matcher with the same fixtures, or remove the 'complete denomination lookbehind coverage' claim from the closeout table.

6. **[C+I; small anchor / request-key cleanup]** `_fetchInspectorSimilar` on p7 starts at **5252** (plan says 5250–5278; blanks occupy 5250–5251) — use the real method span through 5278 plus state fields 149–152 and UI 5549–5684. Closeout table incorrectly calls the existing widget a `StatefulWidget`; it is `StatelessWidget` at 6356–6479 (replacement through the matching brace is still the right shape). `_RequestKey.fromData` should include the same alias set as `_extractUserPhoto` (snake `image_obverse` / `stored_*`) and should key year via the same `canonicalYear` helper so empty `year` + populated `Year` refreshes correctly.

7. **[C+I; keep the gates that already work]** Preserve: main `9f04550a`, Stripe OFF, PLAN ONLY, alerts-only / no $0 or $25 caps, separate Eric YES for writes/rules, US-only, 3:00 AM stand-down, laptop+GCS AI-image backup gate, non-force revert rollback, NET-816 single owner for Google 3531–3548 + handler 4387–4406 with `_onSearchEbay` @4410 preserved, and camelCase user-photo alias iteration with fail-closed placeholder when `hasUserUploadedPhotos` is true but no owned URL survives.

## What improved / prior must-fix status
- **Structural deletion ranges:** Google 3531–3548 and handler 4387–4406 on p7 are now correct; NET-816 ownership named. **Accepted as plan text.**
- **canonicalYear:** Personal Notes excluded; empty alias no longer masks `Year`; direct dual-date normalize to 2026. **Major improvement — accepted with remaining wire-up notes above.**
- **User-photo aliases:** camelCase + iterate nonempty. **Accepted direction.**
- **Whole-class replacement start:** 6356 declaration. **Accepted.**
- **Hard $0 cap:** Removed; alerts-only. **Accepted.**
- **Handoff mirrors:** docs/BATONS/RADIO/INBOX/OUTBOX SHA256 match for both plans (Cards `B733E249…`; Images `3DDFB62A…`). AG CoS INBOX also holds both v1.6 files.
- **Images lifecycle / tests / API:** still **blocking**.

## Rubrics
|Cards dimension|Score|
|---|---:|
|Branch/rollback/standing locks|19/20|
|Canonical year / denomination correctness|28/30|
|Retail precedence and contrast proposal|14/20|
|Shared structural removal/integration|13/15|
|Behavioral tests/provenance proof|10/15|
|**Cards**|**84/100 FAIL**|

|Images dimension|Score|
|---|---:|
|Branch/rollback/standing locks|18/20|
|Complete applicable widget/future lifecycle|12/25|
|User-photo preservation and ownership/CSP|18/25|
|Network truth/operational safety|12/15|
|Real verification and shared removals|8/15|
|**Images**|**68/100 FAIL**|

Combined arithmetic: (84+68)/2 = **76/100 FAIL**. Score is plan readiness, not proof of runtime safety. No AJ PII encountered. No code, deployment, Firestore, deletion, main, or Stripe authority granted. Revised CoS 95+, then independent SAG 95+, then Eric typed YES; separate gates remain separate.