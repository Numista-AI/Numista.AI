# GB CoS score — NET-813 Unified Coin Details View v1.3

**76/100 — FAIL.** Pass requires 95+. Not ready for SAG pass, Eric YES or execution.
Reviewed 7 Nov 2026, approximately 3:17–3:25 PM EST (America/New_York).

## Scope and evidence

Read the full 743-line plan `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.3.md` (**P** citations), the 71-line review baton `BATONS/BATON_NET-813_GROKCOS_REVIEW_UNIFIED-COIN-DETAILS-VIEW_v1.3_20261107-1545.md` (**B**), delivery `RADIO NET/RADIO_NET-833_AGCOS-to-GROKCOS_DELIVERY-NET-813-v1.3_20261107.md`, and prior `BATONS/COS_SCORE_NET-813_UNIFIED-COIN-DETAILS_v1.2_20261106.md` (**74**). Agent statements are evidence, never approval.

Read-only checks on EDS_Laptop in `C:\Users\ericd\Documents\MyVertexProject` after `git fetch --all`:
- origin/main **9f04550a45fa4da082ba8948c2d89a521a90fa45** (locked; not an ancestor of p7, `merge-base --is-ancestor` = 1).
- origin/p7-v8.9 tip **f7e8369a40a4563865ae6c80e5a80b3d1c12d250** (docs-only; also local HEAD). Plan delivery commit **5fbff9af** (docs only).
- origin/dev tip **afbbbd45950c459c04a1e82b437dd346c522c3da**.
- Last code commit on p7 touching `numista_mobile/lib`, `test` or `firebase.json`: **c294fd3c** (4 Nov 16:35 EST). `git diff --stat 03da3195..origin/p7-v8.9` over `numista_mobile/lib`, `test`, `assets`, `firebase.json`, `firestore.rules` and `pubspec.yaml` is **empty**. So the code baseline is unchanged from the v1.2 score. All source citations below are from **c294fd3c** (same app code as 03da3195 and tip).

No checkout, no laptop writes, no tests or builds, no app or database requests, no deploys, no push, no messages. Only this report was written, on the box. This is a bounded document and source check. It is not a runtime certification.

## Prior CoS-74 must-fix closeout

| # | Prior must-fix | v1.3 verdict | Evidence |
|---|---|---|---|
| 1 | Rollback and flag operations | **Partial** | The broad-range revert is gone. P597–606 adds an ordered list of exact SHAs and P601 adds an ancestry check. P614–622 points the restore the right way (known-good → live). **But the commands won't run:** `firebase hosting:releases:list` (P616) is not a Firebase CLI command. `hosting:clone numista-vault:$ID numista-vault:live` (P621) is missing the `@` version form (`numista-vault@VERSION_ID` / `site:@VERSION_ID`), so it reads the ID as a channel. `.version.name` returns the full `sites/…/versions/…` path, not a bare ID. P611 `channel:delete` has no `--site numista-vault`. P625's smoke test hits `numista-vault.web.app/` only, not `numista.ai` `/` and `/catalog`. The ancestry check only proves PRE_EXEC is an ancestor of HEAD. It doesn't prove each execute SHA belongs to the range, and it doesn't record the SHA list or cover merge/conflict handling. Kill-switch P583–585: `assets/config/features.json` is a bundled asset (absent on the pin), so flipping it means a rebuild plus a **live deploy**, which is neither remote nor instant. There's no loader, cache or precedence spec against the non-const P580 global. The `?unified_details=` override needs a rule that it can only disable, never enable, in production. |
| 2 | Parent identity / Previous-Next | **Partial (substantial progress)** | Closed: fail-closed on a missing parent with no `m` fallback (P208–217, P250–254, P318–327). Out-of-filter parent opens standalone with `currentIndex: null` (P370–375). The `...` stubs are replaced with full callbacks (P218–383), and they match real 2761–2782. **Open:** at every virtual-child branch the plan passes the **child's** index while showing the **parent** (`currentIndex: row` P222/P272, `currentIndex: index` P332). Real `docs[row]` is the child (`my_collection_screen.dart:2729`, `2992`), so `coinList[currentIndex]` ≠ the displayed coin, which is the same identity mismatch as before. `UnifiedCoinNavigationContext` (P175–187) is defined but **never passed**: every `show` call uses loose `coinList`/`currentIndex`, so `canNavigate`/`bannerNotice` aren't wired. There's still no `show()` signature and no transition resolver for stepping onto a virtual child (parent lookup, dedupe, cache miss mid-navigation, list changes). Missing-parent UX differs by site: snackbar at sites 1/4, silent `return` at 2/3 (P252). |
| 3 | Laws provenance / URL / timeout | **Partial (substantial progress)** | Closed: `isValidCongressUrl` (P493–505) is correct for the real data (`_kDefaultLaws` URLs are all `https://www.congress.gov/bill/...`). It covers HTTPS, userinfo, port, exact host and path prefix. Mobile uses the validator with `LaunchMode.externalApplication` (P511). The 4s timeout and `mounted` check are named (P517–518). Icon removed (P512). **Open:** the web anchor (P510) interpolates raw `${law['congress_url']}` **without** calling the validator, so web bypasses the check. Flutter web also can't emit a raw `<a>` from Dart strings: specify `url_launcher` `Link` (or equivalent) wrapping a validated `Uri`. `_kCheckedLegislationManifest` (P487) is named but never defined (contents, version, reviewer, location). `is_editorial_verified` doesn't exist anywhere on the pin, which is fine as long as absent means unchecked, but say so. The timeout's `onTimeout: () => _fallbackCheckedLaws(lawKey)` (P517) conflicts with P519–520, which shows the empty state on timeout, and the name implies static defaults are "checked". Precedence for timeout, error, malformed data and static fallback needs to be one table. The non-timeout `catch` path is unspecified. |
| 4 | Morgan notes / rich content | **Partial** | Closed: Markdown uses the real `flutter_markdown_plus` API (pubspec `^1.0.4`, which has `imageBuilder` and `onTapLink`). Images are blocked with `SizedBox.shrink()` (P548). Theme-aware h1/h2/p replace real white headings (`coin_detail_screen.dart:2789–2790`). **Open:** real `strong: … Colors.white` (2792) isn't in the replacement styleSheet, so it still inherits white-on-light. `sanitizeNotesText` (P540) is undefined. P543–545 allows Congress links from **AI text**, which contradicts §7's "Zero outbound links" for Morgan's notes (P531); pick one. The "AI Analysis (Unverified Reference)" label only appears as a table cell (P531) and has no rendering spec. Notes have no source binding or failure mapping (prior CoS #3). `isOwnedStorageUrl` / `lib/utils/owned_storage_url.dart` (P397) **don't exist on p7 or dev**: they're a NET-817 deliverable that is still failing (v1.8 73/100). Name the dependency and its pass gate, or include the guard. P403 admits any relative `/` path. The v1.2 commitment of no AI images in primary/card/index slots and accepted-user-photo priority is **missing** from v1.3. |
| 5 | Value/privacy matrix + public entry | **Partial / entry not closed** | Closed: the `cpgRetail` contract is grounded (`coin_model.dart:54` `final double cpgRetail;`, `:130` default `0.0`, `:225` parse `cpg_retail ?? cpgRetail`). Positive/finite vs Valuation Pending is defined (P456–457). Owner default-hidden with Show values, storage never shown alongside values, session reset (P407–415). **Open:** P462 binds to `numista_mobile/lib/screens/catalog_browse_screen.dart`, which is **absent on p7 and dev**. The real screen is `origin/dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` (18a8b8e5, blob 3a0d3109), and it opens `_showItemDetailModal(Map<String, dynamic> item)` (line 810) from line 466. p7 has no `/catalog` route. Dev routes `/catalog` and `/catalog/<nacCode>` (`main.dart:133–178`), not `/catalog?item=<id>` (P470). Name the dev→p7 integration dependency or move the public binding to the NET-816 owner without a main unlock. `PublicCoinProjection.fromCatalogItem` is undefined. `weightG`/`diameterMm` are non-nullable with no missing-data rule. §7 marks Morgan's notes, History and Known errors as **Full** for guests (P531–534), but the projection has no fields for notes or errors, and real `_AiInsightsTab.insight` is free text from a private-session AI call. Contradictions remain: P476 "all valuation figures derive strictly from cpgRetail" vs owner purchase/melt (P411) and guest `aiValue` sub-caption (P459). Decide whether guests see an AI estimate at all. Test 6 (P677) says "or null" for a non-nullable field. |
| 6 | Implementable offline test plan | **Not closed** | P634–705 has the right 11 test names, and imports `package:numista_ai` (correct; pubspec `name: numista_ai`). But **every test body is a comment only**. `UnifiedCoinDetailHarness` is named (P632) but never defined. There are no fakes for Firestore, `url_launcher` (URL capture), the image loader or the law loader. No write counter, no injected clock for the 4s timeout, no contrast helper. Test 1's comment is garbled ("details when false for 2, 3"). Missing cases: eBay absence, accepted-user-photo priority, hostile image URLs, virtual-child Next/Previous identity, value reset on Next to a new coin (P414 says it persists, so assert that), owner vs guest on the same fixture, guest absence of notes/semantics/filenames, unnecessary-read counting, and the `strong` contrast. The baton's test list (B49–59) is in a different order and content from the plan (e.g. B "Test 9 projection redaction" isn't in P). This is still a prose checklist with `testWidgets` wrappers. |
| 7 | Standing rules / operational gates | **Mostly closed (Partial)** | Closed: separate Eric YES gates for code, preview, Firestore writes, rules, and production (P713–720). US-only, sourced only, AJ/user PII, alerts never caps ($20), zero deletions, Catalog 13 Nov, build 10–16 Nov, Meta 26 Nov (P723–731). **Open:** no dated preview, field-test or Founder checkpoints inside 10–16 Nov. No read-cost measurement or owner. No laptop+GCS preservation precondition if NET-816/817 image cleanup ever touches this view. Gate 5 conflates "production go-live" with `origin/main`: the Thanksgiving build ships from p7 Hosting, so state that a live Hosting deploy from p7 also needs its own YES, and that toggling the kill-switch asset is a live deploy. |

## Numbered blocking must-fixes (v1.4)

1. **Make rollback commands real.** Replace `hosting:releases:list` with a supported method: record the version ID from the console release history, or from the Hosting REST `sites.releases.list` read under Eric's credentials at Gate 2. Use `firebase hosting:clone numista-vault@<VERSION_ID> numista-vault:live`, store the **bare** version ID, and add `--site numista-vault` to channel commands. Smoke-test `https://numista.ai/`, `/catalog` and a known coin path. Record the execute SHA list as an artifact, verify each SHA with `git merge-base --is-ancestor <sha> HEAD` and `git rev-list $PRE_EXEC_SHA..HEAD`, and say what to do on conflicts or merges. Restate the kill-switch honestly: a bundled asset needs a rebuild plus a live deploy under its own Eric YES. Specify the loader, cache-busting and precedence. The query override may only disable.
2. **Fix virtual-child navigation identity.** Wherever the displayed coin is the parent, pass the **parent's** filtered index (`docs.indexWhere((r) => r.id == parentDoc.id)`, or null for standalone), not the child's `row`/`index`. Actually pass `UnifiedCoinNavigationContext` into `show()` and publish the full `show()` / `showPublic()` signatures. Define the transition resolver: Next/Previous onto a virtual child → its parent (deduped, so consecutive children of one parent aren't repeated), a parent cache miss mid-navigation → fail closed with a banner, and the list changing while open. Use one missing-parent UX at all five sites.
3. **Close the web Laws bypass and fallback precedence.** Render the web link with `url_launcher` `Link` (or equivalent) over a URI that has **passed `isValidCongressUrl`**, never a raw interpolated string. Define `_kCheckedLegislationManifest` (location, schema, version, who reviewed it), and state that absent or unknown means "From Congress.gov, not yet checked by us". Write one table covering Firestore success, timeout, error, malformed data and no key, with the static fallback, its label (never "checked" unless manifest-backed) and the empty state. Remove the `_fallbackCheckedLaws` vs empty-state contradiction.
4. **Finish the rich-content boundary.** Add `strong`, h3, listBullet and code to the theme-aware styleSheet (real 2792 `Colors.white`). Define `sanitizeNotesText`. Decide on Congress links inside AI notes (recommended: none in notes, Laws tab only) and make §5, §7 and §7.3 agree. Spec how the "AI Analysis (Unverified Reference)" label renders. Either name NET-817's `isOwnedStorageUrl` as a hard dependency with its own pass gate, or include the guard here (exact HTTPS hosts and bucket paths, and no relative `/` unless it's a same-origin asset allowlist). Restore the rules for no AI images in primary/card/index slots and accepted-user-photo priority.
5. **Bind the real public entry.** Cite `origin/dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` and `_showItemDetailModal(Map<String, dynamic>)` (line 810), and the real `/catalog` and `/catalog/<nacCode>` routes. Name how that code reaches p7 (the NET-816 dependency, with no file transplant and no main unlock), or explicitly defer `showPublic` to NET-816 with a stub contract. Define `PublicCoinProjection.fromCatalogItem(Map<String, dynamic>)` field by field, with missing-data rules (nullable weight and diameter), and the guest source for Morgan's notes, History and Known errors. Catalog-sourced editorial text is fine; private-session AI insight is not. Resolve the `aiValue` and "CPG sole authority" contradictions with one owner/guest × field × source matrix.
6. **Author the tests for real.** Provide the `UnifiedCoinDetailHarness` code (injectable Firestore read, law loader with a fake clock, `url_launcher` capture, image loader capture, write counter), plus at least the assertion bodies for all 11 tests and the missing cases in the MF-6 row above. Make the baton's list match the plan's. Executing the tests still waits for Gate 1.
7. **Finish the ops gates.** Add dated checkpoints inside 10–16 Nov: preview, Field Tester verification with evidence, and the Founder review. Add a read-cost owner and measurement. Add the laptop+GCS preservation precondition. Separate "live Hosting deploy from p7" from "main merge" in the gate table.
8. **Fix handoff integrity.** Correct DTGs and baton section references (see below), and address the revise to the current AG CoS v5 (`cfe23a7a`). The plan's "From" line is v4 `ba2bfdb2`, which was relieved at 15:09 per p7 commit c8c4dbdd.

## GEMINI38_REVIEW (Tier 1/2 — real code from origin/p7-v8.9 @c294fd3c)

**Virtual child row identity:** the plan passes this index while showing the parent:
```dart
// my_collection_screen.dart:2726–2736
              final row = vicinity.row;
            final crw = docs[row];
            final m   = crw.data;
            final effectiveId = crw.isVirtualChild ? (crw.parentDocId ?? crw.id) : crw.id;
            void onTap() => _showCoinInspectorDialog(effectiveId, m);
```
```dart
// my_collection_screen.dart:2991–2993, 3041–3044
      itemBuilder: (context, index) {
        final crw = docs[index];
        final m = crw.data;
          child: InkWell(
            onTap: () {
              setState(() => _selectedCoinId = effectiveId);
              _showCoinInspectorDialog(effectiveId, m);
```
`docs` is `List<CollectionRow>` (`_buildDataTable(List<CollectionRow> docs…)` :2557, `_buildCardGrid` :2982). `CollectionRow` documents that virtual child IDs are synthetic (`{parentId}__set_coin_{idx}`) and must never be used as Firestore paths (`models/collection_row.dart:5–8`).

**Info-icon fail-closed precedent** (plan matches):
```dart
// my_collection_screen.dart:2754–2760
                          if (crw.isVirtualChild) {
                            final parentDoc = _cachedCoinsDocs
                                .where((d) => d.id == crw.parentDocId)
                                .firstOrNull;
                            if (parentDoc == null) return; // parent missing — skip
                            final parentData = (parentDoc.data() as Map<String, dynamic>?) ?? {};
                            final coin = CoinModel.fromMap(parentData, parentDoc.id);
```
`_cachedCoinsDocs` is `List<QueryDocumentSnapshot<Map<String, dynamic>>>` (:131), so the plan's `as Map<String, dynamic>?` cast is redundant but harmless.

**Laws loader:** no timeout today; static fallback precedence:
```dart
// coin_detail_screen.dart:2956–2970
  Future<void> _fetch() async {
    try {
      final snap = await FirebaseFirestore.instance
          .collection('metadata')
          .doc('coin_legislation')
          .get();
      if (mounted) {
        setState(() {
          _laws = snap.data()?['laws'] as Map<String, dynamic>?;
          _loading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _loading = false);
```
```dart
// coin_detail_screen.dart:3082–3088
    final lawKey = _matchLawKey();
    Map<String, dynamic>? law;
    if (lawKey != null) {
      if (_laws != null && _laws![lawKey] != null) {
        law = _laws![lawKey] as Map<String, dynamic>?;
      }
      law ??= _kDefaultLaws[lawKey];
```
**Unvalidated launch** (replaced on mobile in P511; web P510 still raw):
```dart
// coin_detail_screen.dart:3152–3158
                if ((law['congress_url'] ?? '').toString().isNotEmpty) ...[
                  SizedBox(height: 16),
                  OutlinedButton.icon(
                    onPressed: () => launchUrl(
                      Uri.parse(law!['congress_url'].toString()),
                      mode: LaunchMode.externalApplication,
```
Real static URLs, e.g. `'congress_url': 'https://www.congress.gov/bill/110th-congress/house-bill/6184'`, all pass P493–505.

**Markdown sink:** `strong` is still white and missing from the plan's replacement:
```dart
// coin_detail_screen.dart:2785–2805
                MarkdownBody(
                  data: insight,
                  styleSheet: MarkdownStyleSheet(
                    h1: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white, height: 2.0),
                    h2: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white, height: 2.0),
                    strong: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
                  onTapLink: (text, href, title) {
                    if (href != null) {
                      launchUrl(Uri.parse(href), mode: LaunchMode.externalApplication);
```
Import `package:flutter_markdown_plus/flutter_markdown_plus.dart` (:24). The package has `MarkdownImageBuilder imageBuilder`, so P548 compiles.

**Header contrast:**
```dart
// coin_detail_screen.dart:59, 892–893, 918–921
Color _kDark(BuildContext c) => _isDarkCtx(c) ? const Color(0xFF0B1120) : const Color(0xFFF4F4F2);
    return Container(
      color: _kDark(context),
                  Text(title,
                    style: const TextStyle(
                      color: Colors.white, fontSize: 18,
```
Measured on the box: white on #F4F4F2 = **1.10:1**, which confirms the plan's P36 claim. The proposed #0B1A2E on #FFFFFF = **17.48:1** and #F8FAFC on #0F172A = **17.06:1** (the plan says 16.2:1, which is conservative and still AAA). The subtitle at :925 (`Colors.white60`) needs the same fix.

**cpgRetail contract:**
```dart
// coin_model.dart:54, 130, 225
  final double cpgRetail;
    this.cpgRetail = 0.0,
      cpgRetail: _parseDouble(data['cpg_retail'] ?? data['cpgRetail']),
```
The card grid already prefers positive CPG and falls back to `aiValue` (`my_collection_screen.dart:3017–3023`). The guest policy must decide whether that `aiValue` fallback is allowed in public.

**Public entry reality:** `git cat-file -e` returns 128 for `numista_mobile/lib/screens/catalog_browse_screen.dart`, `lib/utils/owned_storage_url.dart`, `lib/config/feature_flags.dart`, `assets/config/features.json`, `lib/screens/unified_coin_detail_screen.dart` and `test/screens/unified_coin_detail_screen_test.dart` on **both** p7 and dev. Present only on dev: `lib/screens/catalog/catalog_browse_screen.dart` (`void _showItemDetailModal(Map<String, dynamic> item)` :810), with routing in `main.dart:133–178` (`normalizedPath == '/catalog' || path.startsWith('/catalog/')` → `CatalogBrowseScreen(initialNacCode: …)`). p7 `numista_mobile/lib` has no `/catalog` route.

**Hosting:** `numista_mobile/firebase.json` has `"site": "numista-vault"`, `"public": "build/web"`, and `.firebaserc` default project `studio-9101802118-8c9a8`. So `channel:delete` without `--site` targets the project default site, not necessarily numista-vault.

## Handoff integrity

- **Mirrors: hash-match.** The plan's SHA256 is **65899CDD3923DA0189BBB62B287FCF6A44EB53F39DAAA8DC7892A6F79CFE2C62** (39,507 bytes) in `docs/`, `BETA TEST/…/BATONS/`, `BETA TEST/…/RADIO NET/`, and in `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/` and `/OUTBOX/` (those two are untracked by git). There's no copy in `BETA TEST/…/INBOX` or `OUTBOX`, so the claim holds only if "INBOX/OUTBOX" means the `1 NUMISTA.AI` mailboxes. This fixes the v1.2 mirror defect. The review baton's SHA256 is **3EC4C919331206B0C95448A21E2ED34F18843A11B2E6DEA729EC626C2A648215** and matches across all 4 locations.
- **The DTG is in the future.** The plan, baton and RADIO_NET-833 all say 15:45 ET. Actual file mtimes are 14:46:00 (plan), 14:47:41 (baton) and 14:48:30 (radio) EST, and the commit 5fbff9af is at 14:49:27 EST. Stamps run about 1 hour ahead, the same pattern as the NET-816/817 batons.
- **The baton doesn't match the plan.** It cites §2.5 (rollback), §6.4/§6.5 (rich content), §5.1, §9.4 and §10.1/§10.2, none of which exist. Rich content is §7.3, ops is §11. The baton says `imageDirectory: null` and `colorScheme.onSurface`, but the plan uses `imageBuilder` and `textTheme.titleMedium`. The test lists differ. The baton must describe the plan as delivered.
- The author line is AG CoS v4 `ba2bfdb2`, which was relieved at 15:09 EST (p7 c8c4dbdd/c012e121). The revise goes to AG CoS v5 `cfe23a7a`. NET-813 writer-cap count is now 4 scored versions (v1.0–v1.3; CoS 86 / SAG 58 / CoS 74 / CoS 76).

## Rubric

| Dimension | v1.2 | v1.3 |
|---|---:|---:|
| Standing locks / read-only / approval boundaries | 17 | 18/20 |
| Branch, rollback and feature gate | 10 | 11/15 |
| Five-site resolution / navigation identity | 11 | 12/15 |
| Laws, notes and outbound safety | 10 | 11/15 |
| Guest privacy / CPG / image precedence | 12 | 11/15 |
| Accessibility / low-click UX | 9 | 9/10 |
| Offline verification / field-test readiness | 5 | 4/10 |
| **Total** | **74** | **76/100 FAIL** |

Guest privacy dropped because the public binding names a file and route that don't exist, and the image-precedence rules regressed. Offline verification dropped because the "complete authored suite" claim (P27, B48) is contradicted by empty test bodies.

No AJ PII was found in the reviewed plan or the selected code. No authority is granted. The sequence is still: revised CoS 95+, then independent SAG 95+, then Eric's typed YES, with separate code, preview, write, rules, live and deletion gates. No messages sent and no Eric ping.
