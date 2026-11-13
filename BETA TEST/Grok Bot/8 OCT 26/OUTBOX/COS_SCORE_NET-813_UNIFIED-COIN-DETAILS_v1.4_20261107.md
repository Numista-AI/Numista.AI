# GB CoS score — NET-813 Unified Coin Details View v1.4

**86/100 — FAIL.** Pass requires 95+. Not ready for SAG pass, Eric YES or execution.
Reviewed 7 Nov 2026, approximately 7:25–7:35 PM EST (America/New_York). Baton `BATON_NET-813_GROKCOS_REVIEW_UNIFIED-COIN-DETAILS-VIEW_v1.4_20261107-1925.md` (file mtime 7:14:55 PM ET, stamped 7:25 PM ET). Writer: AG CoS v5 `cfe23a7a`, attempt **1/4** on this v5 revise (v1.3 was 76 FAIL). Next if revised: **v1.5 attempt 2/4**.

## Scope and evidence

Read the full 1,035-line plan `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.4.md` (**P** citations; 49,823 bytes, mtime 7:14:36 PM ET), the review baton (**B**), and prior `COS_SCORE_NET-813_UNIFIED-COIN-DETAILS_v1.3_20261107.md` (**76 FAIL**, 8 blocking must-fixes). Agent statements are evidence, never approval.

Repository on EDS_Laptop `C:\Users\ericd\Documents\MyVertexProject`. All material citations checked via `git show 4d17ca5e:<path>` / `git ls-tree` (not the working tree, not plan quotes alone). Public-catalog binding also checked at `origin/dev`. Verified:
- `origin/main` **9f04550a45fa4da082ba8948c2d89a521a90fa45** (locked; `merge-base --is-ancestor` = 1).
- Pin `4d17ca5e` exists (`docs(cards-images): deliver NET-817 FAILFIX Plans 780b and 780c v1.5…`, 6 Nov 9:30:42 PM ET). `git diff --stat 4d17ca5e HEAD -- numista_mobile/` is **empty**.
- `c294fd3c` (plan's code pin; last `numista_mobile/` commit on p7) has **no mobile diff** vs `4d17ca5e`. Same app code.
- Plan delivery commit **`397f83ba`** (`docs(net-813): deliver Unified Coin Details View plan v1.4…`, 7:16:18 PM ET). Docs-only counterpart on `origin/dev` observed as **`48bb1427`** (7:17:06 PM ET).
- Local HEAD / `origin/p7-v8.9` at scoring time: **`ec27df45`** (later NET-814 docs delivery; mobile tree still unchanged). `origin/dev` tip **`6af2afb1`** (NET-817 v2.0 PASS docs; leave intact).
- Stripe OFF; PLAN ONLY; no Argon.

No checkout of main, no tests or builds executed, no app or database writes, no deploys, no Eric ping, no messages to SAG or anyone else. Score is plan readiness, not runtime certification.

## Prior CoS-76 must-fix closeout

| # | Prior must-fix | v1.4 verdict | Evidence |
|---|---|---|---|
| 1 | Rollback and flag operations | **Mostly closed** | Clone now uses `firebase hosting:clone numista-vault@<PRE_DEPLOY_VERSION_ID> numista-vault:live` (P780). Channel delete has `--site numista-vault` (P784). Version capture is Console / REST `sites.releases.list` at Gate 2, not the invalid `hosting:releases:list` CLI (P773–776). Smoke hits `https://numista.ai/`, `/catalog`, `https://numista.ai/catalog/US-1921-MORGAN`, and a hostile 404 (P786–790). SHA list artifact + `git revert --abort` on conflict (P792–803). Kill-switch honestly requires rebuild + live Hosting deploy and its own Eric YES (P806–807). Query override can only disable in `kReleaseMode` (P826–832). **Remaining:** `rootBundle.loadString('assets/config/features.json?v=${DateTime.now()…}')` (P815–816) is not valid Flutter asset loading — `rootBundle` keys are the declared asset path; the `?v=` suffix will miss `assets/config/features.json` and the `catch` fail-closes the flag forever. Per-SHA membership (`merge-base --is-ancestor <sha> HEAD` for each recorded execute SHA) is implied by `rev-list` but not spelled as a loop against `scratch/revert_shas_net813.txt`. |
| 2 | Parent identity / Previous-Next | **Mostly closed** | `_resolveParentForVirtualChild` passes `docs.indexWhere((r) => r.id == parentDoc.id)` or null (P240–253). `UnifiedCoinNavigationContext` is actually passed into `show()` (P174–196, P289–294). Signatures for `show()` / `showPublic()` are published (P174–211). Unified floating red SnackBar `'Parent set details unavailable'` at all five sites (P260–268, P277, P328, P375). Transition resolver dedupes consecutive virtual children of the same parent and banners a mid-nav cache miss (P401–434). **Remaining:** when the target parent is not in `filteredRows`, the resolver falls back to `targetIdx` (P430–431) — that is the child's index again, the same identity mismatch MF-2 asked to eliminate. Initial open correctly uses null for standalone; mid-nav must match. List-changes-while-open is only implicit (captured `filteredRows`). |
| 3 | Laws provenance / URL / timeout | **Mostly closed** | Web path uses `url_launcher` `Link` over a URI that already passed `isValidCongressUrl` (P596–616), never a raw interpolated string. Validator still matches real default URLs from `git show 4d17ca5e:numista_mobile/lib/screens/coin_detail_screen.dart` (`https://www.congress.gov/bill/110th-congress/house-bill/6184` and the other `_kDefaultLaws` house-bill URLs). Manifest location/schema/reviewer/unchecked badge are defined (P547–577). One precedence table covers Firestore success (verified vs unchecked), timeout/error → `_kDefaultLaws` labeled `"Historical Reference (Default)"` (not "checked"), and no-match/malformed → empty state (P631–637). The `_fallbackCheckedLaws` vs empty-state contradiction is gone. **Remaining:** the sample manifest marks Bland-Allison / Sherman / Pittman URLs `editorial_verified: true` and `reviewed_by: "Founder Eric & Numista Editorial"` (P553–573). Those URLs are not the real `_kDefaultLaws` entries and this review did not independently verify the bill numbers. Do not claim Founder verification of invented examples. |
| 4 | Morgan notes / rich content | **Mostly closed** | Theme-aware `strong`, `h3`, `listBullet`, and `code` are in the replacement styleSheet (P651–663), which does address real `:2792` `strong: … Colors.white` (`git show 4d17ca5e` `:2788–2800`: `p` and `listBullet` are already `_kText(context)`; `h1`/`h2`/`strong` are white). `sanitizeNotesText` is defined and strips HTML, pseudo-protocols, and Markdown links (P668–677). Notes have zero outbound links; Laws tab only. Amber `"AI Analysis (Unverified Reference)…"` banner is specified (P680–710). `isOwnedStorageUrl` is included here (not gated on NET-817) with Form A / Form B and a relative allowlist limited to `/assets/images/` and `/assets/icons/` (P713–746). AI images banned from primary/card/index; accepted user photos first (P749–754). **Remaining / regressions:** (a) §2.5's "verbatim" markdown block is not what `git show` returns — it assigns `Colors.white` to `p` at 2790 and `listBullet` at 2791; real 2790 is `h2` white and real 2793 `listBullet` uses `_kText`. (b) v1.3's `imageBuilder → SizedBox.shrink()` and `onTapLink` no-op were dropped; sanitizer is not a complete substitute if a call site forgets it (standard `![alt](url)` is only partially eaten by the link regex). (c) Extra Form B prefix `/studio-9101802118-8c9a8-uploads/` is not one of the 817-verified emitters (`us_mint_coin_images`, `numista-reference-library`, `numista-uploads-studio-9101802118-8c9a8`). (d) §8.1 cites `coin_detail_screen.dart:135–141` for the `#F4F4F2` + white header defect; `git show` `:135–141` is `ClipRRect` dialog chrome. Real defect: `_kDark` at `:59` (`#F4F4F2` in light mode), header `color: _kDark(context)` at `:892–893`, `Colors.white` title at `:918–921` (and `Colors.white60` subtitle `:925`). Contrast claim itself (1.10:1 vs proposed 17.x:1) remains correct. |
| 5 | Value/privacy matrix + public entry | **Partial** | **Closed:** public entry is now correctly bound to `origin/dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`. `git show origin/dev:…` confirms `_showItemDetailModal(Map<String, dynamic> item)` at **:810**, invoked from `:466`, with unknown-NAC snackbar at `:71–98`. `origin/dev:numista_mobile/lib/main.dart:133–134` and `:155–180` are `/catalog` and `/catalog/<nacCode>` with `?item=` fallback and the light theme the plan preserves. File is **absent** on `4d17ca5e` (`git cat-file -e` = 128), so the NET-816 drop-in / no-main-unlock dependency (P450–451) is the right contract. Owner/Guest × Field × Source matrix (P533–541) hides guest AI value, purchase, and storage; guests see positive CPG or `"Valuation Pending"`. `PublicCoinProjection` has nullable `weightG`/`diameterMm` and `"Not Recorded"` display rules (P461–462, P523–525). Guest notes/errors are catalog editorial only (P467–468, P540). **Open / blocking:** `toSyntheticCoinModel()` (P504–518) and the §10 tests construct a fictional `CoinModel`. `git show 4d17ca5e:numista_mobile/lib/models/coin_model.dart` has **no `name`**, `year` is a **String** (not `int`), `mintMark` not `mintmark`, `imageUrlObverse`/`imageUrlReverse` not `imageUrl`/`reverseImageUrl`, `personalNotes` not `notes`, `metalContent` not `composition`, and **no `weight` or `diameter` fields**. `storageLocation` and `cpgRetail` do exist. Implementation and tests written to this constructor will not compile. |
| 6 | Implementable offline test plan | **Partial** | Better than v1.3's comment-only stubs: 11 named tests have assertion text (P871–995) and a `UnifiedCoinDetailHarness` object exists (P854–869). **Not closed against the written MF-6 contract.** Harness has counters and `fakeLaunchUrl` but no injectable Firestore read, no law-loader fake clock, no URL/image capture wired into widgets. Test 2 constructs `CollectionRow` without required `data` (`git show` `:29–36` — `required this.data`). Tests 2/4/5/11 construct `CoinModel(...)` with invented fields (see MF-5). Test 6 calls `UnifiedCoinDetailScreen.showPublicWidget(...)` — that method is not in the published signatures (only `show` / `showPublic`). Test 5's name claims persistence across Next; the body never navigates. Test 7 checks null fields but never asserts `"Not Recorded"` display. Test 11 expects `harness.firestoreWriteCount == 0` without injecting the harness, so it cannot fail. Missing cases from the v1.3 MF-6 row remain: eBay absence, accepted-user-photo priority, Next/Previous identity (not just static `indexWhere`), owner vs guest on the same fixture, guest redaction of notes/filenames, timeout via fake clock, Markdown `strong` contrast. |
| 7 | Standing rules / operational gates | **Closed** | Dated 10–16 Nov checkpoints: 10 prep, 11 preview, 12 Field Tester, 13 Catalog live, 15 Founder review, 16 freeze (P1011–1017). Read-cost owner AG CoS v5; target <1 read/open, 0 on cache hit (P1019–1022). Laptop + GCS preservation precondition (P1024–1025). Gate 4 is live Hosting deploy from p7; Gate 5 is `main` merge — separated (P1002–1009). Gate 3 still requires Eric typed YES even though writes/rules are described as unused. |
| 8 | Handoff integrity | **Mostly closed** | Author line is AG CoS v5 `cfe23a7a` (P3, P1031). Baton section cites largely match real headers (§9, §3.1–3.4, §6.1–6.4, §7.1–7.5, §4–§5, §10, §11, §12). **Hygiene (not sole fail grounds):** plan/baton stamp 19:25 ET vs file mtimes 19:14:36 / 19:14:55 ET (~11 minutes ahead). Closeout table cites §3.5 for MF-4 (rich content) and §8 for MF-7 (ops); plan §3.5 is the navigation resolver and §8 is WCAG/accessibility. Baton omitted attempt N/4. |

## Numbered blocking must-fixes (v1.5)

1. **Map the projection and tests onto the real `CoinModel` / `CollectionRow`.** Use `git show 4d17ca5e:numista_mobile/lib/models/coin_model.dart` field names: `themeSubject` (no `name`), `year` as `String`, `mintMark`, `imageUrlObverse` / `imageUrlReverse`, `personalNotes`, `metalContent`, `cpgRetail`, `storageLocation`. Do not invent `weight`/`diameter` constructor args — keep those on `PublicCoinProjection` and render `"Not Recorded"` from the projection (or document an additive nullable extension). `CollectionRow` requires `data`. Delete `showPublicWidget`; pump `showPublic` or the real widget constructor.
2. **Finish the harness and make the assertions able to fail.** Inject Firestore read, law-loader fake clock, `url_launcher` capture, image-loader capture, and the write counter into the widget under test. Assert Next/Previous virtual-child identity (parent index, not child `targetIdx`), value persistence across Next, owner vs guest on one fixture, guest redaction, eBay absence, user-photo priority, timeout, and Markdown `strong` contrast. Test 11 must not be vacuously true.
3. **Fix mid-nav parent identity.** If `filteredRows.indexWhere((r) => r.id == targetDoc.id)` is `-1`, pass `null` (standalone) — never the child's `targetIdx`. State the list-changes-while-open rule (retain the loaded instance).
4. **Make the kill-switch loader real.** Load the declared asset key `assets/config/features.json` (no `?v=` on `rootBundle`). If cache-busting is required, explain that it happens via rebuild + live deploy (already stated) rather than a query string on an asset key. Keep the production-only-disable query rule.
5. **Correct the remaining verbatim cites and drop unverified claims.** Re-quote markdown from `git show 4d17ca5e` (`:2785–2805`). Move the contrast cite to `:59` / `:892–893` / `:918–921`. Restore `imageBuilder` + `onTapLink` defense in depth. Remove or clearly mark the sample legislation URLs as examples, not Founder-verified. Drop the extra `/studio-9101802118-8c9a8-uploads/` prefix unless `git show` proves an emitter uses it.
6. **Handoff hygiene.** Use a real wall-clock DTG that matches file mtime. Make the closeout table's section cites match the headers. State attempt N/4 on the baton.

## GEMINI38_REVIEW — real code from the pin (Tier-1 grounding)

**Call sites** — `git show 4d17ca5e:numista_mobile/lib/screens/my_collection_screen.dart` confirms the five pathways the plan names, with compressed-but-real quotes:
- Table cell `onTap` at **:2736** `_showCoinInspectorDialog(effectiveId, m)` (`row` at :2726, `crw` at :2729, `effectiveId` at :2734). Plan §2.1 line numbers are slightly collapsed (it labels `crw` as 2727; real 2727 is blank / 2728 comment) but the statements exist.
- Info-icon virtual-child / regular `CoinDetailScreen.show` at **:2754–2782** matches §2.2.
- Cards `itemBuilder` `:2991–2993` and tap `:3040–3045` match §2.3.
- Parent-set container `:3117–3124` matches §2.4.
- Inspector metrics `:3850` `data[_F.aiValue]`, eBay `:3861` `_onSearchEbay(data)`, storage `:3996` `data[_F.storageLocation]` — claims hold.

**Markdown sink** — real `:2785–2805`:
```
MarkdownBody(
  data: insight,
  styleSheet: MarkdownStyleSheet(
    p: TextStyle(fontSize: 14, color: _kText(context), height: 1.7),
    h1: TextStyle(..., color: Colors.white, ...),
    h2: TextStyle(..., color: Colors.white, ...),
    h3: TextStyle(..., color: _kText(context), ...),
    strong: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
    listBullet: TextStyle(fontSize: 14, color: _kText(context), height: 1.7),
    ...
    code: TextStyle(..., color: _kText(context)),
  ),
  onTapLink: (text, href, title) { if (href != null) launchUrl(...); },
)
```
`strong` at `:2792` is white — the styleSheet fix is still needed. Plan §2.5 is not a faithful verbatim quote.

**Header contrast** — `_kDark` `:59` is `#F4F4F2` in light mode; header container `:892–893` uses it; title `:918–921` is `Colors.white`. Plan's `:135–141` cite is wrong (dialog `ClipRRect`).

**Laws launch** — `:3152–3158` still unvalidated `launchUrl(Uri.parse(law!['congress_url']…))`. Real `_kDefaultLaws` congress_url values are house-bill URLs on `www.congress.gov` (HR 6184 / 2414 / 2764 / 1923) and pass the planned validator.

**CoinModel / CollectionRow** — as in the MF-5/MF-6 rows above. `pubspec.yaml:1` is `name: numista_ai` (plan tests import `package:numista_ai/...` — correct).

**Public entry** — absent on the pin; present on `origin/dev` at the exact path and lines the plan now cites. p7 `main.dart:119–148` has no `/catalog` and routes unknown paths to `NotFoundScreen` (`:142–148`).

**Hosting** — `numista_mobile/firebase.json:7–9` `"site": "numista-vault"`, `"public": "build/web"`, `"trailingSlash": false`.

## Rubric

| Dimension | v1.3 | v1.4 |
|---|---:|---:|
| Standing locks / read-only / approval boundaries | 18 | 19/20 |
| Branch, rollback and feature gate | 11 | 13/15 |
| Five-site resolution / navigation identity | 12 | 14/15 |
| Laws, notes and outbound safety | 11 | 13/15 |
| Guest privacy / CPG / image precedence | 11 | 12/15 |
| Accessibility / low-click UX | 9 | 9/10 |
| Offline verification / field-test readiness | 4 | 6/10 |
| **Total** | **76** | **86/100 FAIL** |

Locks, rollback commands, parent-index-on-open, web Laws `Link`, sanitizer/banner, public-entry path, matrix, dated gates, and v5 authorship all moved the right direction. The score stops short of 95 because the projection/tests still invent `CoinModel` fields, the harness cannot fail several of its own assertions, and a few "verbatim" cites plus the `rootBundle ?v=` loader remain untrue to `git show`.

No AJ PII was found in the reviewed plan or the selected code. No authority is granted. Sequence remains: revised CoS 95+, then independent SAG 95+, then Eric's typed YES, with separate code, preview, write, rules, live and deletion gates. No messages sent and no Eric ping.
