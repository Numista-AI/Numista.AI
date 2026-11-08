# GB CoS score: NET-810 Mint Product Fields, Detail View v1.0

**58/100 FAIL.** The pass bar is 95+. The plan is not ready for an SAG pass, an Eric YES or execution.
Reviewed 7 Nov 2026, about 12:23–12:45 AM EST (America/New_York).

## Scope and evidence

I read the 309-line plan (cited as **P**), the 24-line GROKCOS_REVIEW baton (**B**), `SCHEMA_DIFF_product_price_mint_schedule_20261105.json` (80 lines), `Plan.v1_catalog_Mint_product_fields_excerpt.md` (7 lines) and the NET-821 stall radio. The prior box score format was the template. Agent claims are not approval.

I ran read-only checks of EDS_Laptop git objects in `C:\Users\ericd\Documents\MyVertexProject`. Source citations refer to **origin/p7-v8.9 @ cd8d083b34bcfa2d81ce9e129542b2c7f6134c1f** (also local HEAD; commit 2026-11-06 11:52:21 PM EST, "docs(net-810): deliver mint product fields plan v1.0 and review baton"). The only commit since ef2b51e5 is that docs commit. Main is still **9f04550a45fa4da082ba8948c2d89a521a90fa45**. I did not fetch, so local remote-tracking refs were not refreshed. I also read the box catalog preview (`/workspace/catalog-preview/schema.json`, `entries.jsonl`).

I made no fetch, checkout, laptop write, build, test run, live HTTP or database request, push, deploy or message. Only this box report was written. This is a bounded document and source check, not a deep Code Reviewer audit and not runtime certification. Proposed files being absent is expected for a plan-only submission. False completion or coverage claims are defects.

**Verified correct:** `_DetailsTab` is declared at `coin_detail_screen.dart:1513`, and `build` opens `final fields = <(String, String)>[` at **1526**. The plan's copy of the existing 15 rows matches the real file exactly, and Notes sits at **1541**, so P199's citation and the placement before Notes are accurate. None of the four new fields exists in `coin_model.dart` today. The schema-diff types and descriptions for the 4 fields are carried over faithfully (P19–22 vs SCHEMA_DIFF 5–77). The label "U.S. Mint issue price" (R2), detail-only (R1), hiding null/<=0/UNKNOWN (R4), mint_schedule_status precedence (R5) and release-time pairing (R7) all match the excerpt. Dropping Argon from the review route (P297) correctly follows Eric's 5 Nov 6:07 PM ET order, even though the excerpt (line 6) still lists Argon.

## Numbered blocking must-fixes

1. **No source-of-truth or ingestion path: the fields can never reach the screen without forbidden writes.** The 4 fields are catalog properties: SCHEMA_DIFF `schema_path` is `/workspace/catalog-preview/schema.json`, which defines them at 544–575. But **0** records in box `entries.jsonl` carry any of them. Their sources (26XS list price $375, 26BM1 NOT_AVAILABLE) live only in proposal files (`NOV2026_RELEASES_*`, `entries_master_*`). `_DetailsTab` renders a user's **CoinModel**, which is loaded from the user coins collection (`coin_detail_screen.dart:485–488`, `AuthService.coinsPath`). The plan never says how a catalog record's Mint fields get joined onto a collection coin. It names no catalog ID/NAC/year/mint/product-code key, no read-only lookup service and no handling for ambiguous or missing matches. That leaves two outcomes: the fields never render, or someone writes catalog data into user coin documents, which breaks zero Firestore writes and catalog-as-source-of-truth. Specify a read-only catalog lookup (asset or public catalog JSON), the exact match key, fail-closed behavior on no match or multiple matches, the fact-checked source and version for each value, and a quarantine for proposal-status rows. No user-doc writes or seeding.

2. **`release_date` is invented.** P62, P103 and P128 add `releaseDate` to CoinModel. But `release_date` is **not** in SCHEMA_DIFF (4 fields only), is **not** a defined property in `catalog-preview/schema.json` (0 key occurrences; it appears only in the `release_time_et` description at 563), and is not in `coin_model.dart`. On the target branch it exists only in `services/upcoming_releases_service.dart:12,46,64`, with seeded values like `'Fall 2026'` (147), `'TBD'` (160) and `'Late 2026'` (199). Pairing those with `release_time_et` would print "TBD, noon ET", which breaks R4's ban on TBD and placeholders. Define `release_date` as an explicit schema addition with a format (ISO date plus display format), a source and fail-closed rules for vague or placeholder dates. Or tie it to an existing catalog field with a citation. Do not reuse the Upcoming Releases strings without validation.

3. **The `toFirestore` change damages round-trip persistence and is the wrong place for the publish allow-list.** The real signature is `Map<String, dynamic> toFirestore()` with no arguments (`coin_model.dart:248`). It is used as the local round-trip source in `coin_detail_screen.dart:490–494` and `682–686` (`CoinModel.fromMap({..._coin.toFirestore(), ...})`), in `1054` (image resolution map) and in `1575` (`SetContentsPanel`), and it is written to Firestore through `wishlist_screen.dart:980` and `services/wishlist_service.dart:52,75`. With `includeMintProductFields=false` as the default, any coin carrying these fields would **silently lose them** on the first edit, CAC toggle or wishlist copy. P108–137 also confuses private user-document serialization with the **public catalog publish allow-list** (R8). The allow-list has to be enforced in the catalog export/publish pipeline: name the script/artifact, use an explicit allow-list (not a deny-by-flag), and default to dropping the fields. Add a test proving the published output omits all 4 until a recorded Eric YES. Keep `toFirestore()` behavior-neutral, or don't touch it at all if the fields are read-only catalog data (#1). Every call site must be listed if the signature changes.

4. **The proposed code doesn't compile against the real APIs, and fail-closed has gaps.** The real factory is `CoinModel.fromMap(Map<String, dynamic> data, String id)` with a **positional** `id` (`coin_model.dart:169`; callers at 490 and 682 pass `_coin.id` positionally). P83's `{required String id}` breaks every call site. P78–81 rewrites `fromFirestore` (real one at 141) without showing a diff. Other defects:
   - `parseNullableDouble` (P88) strips `-`, so `"-5"` parses as **5**, a positive price, which defeats the <=0 rule.
   - NaN and Infinity aren't rejected: `price <= 0` is false for NaN, so P185–191 would render "$NaN" or "$Infinity". Require `isFinite && > 0`.
   - The UNKNOWN check is case-sensitive in serialization (P120, P125) but case-insensitive in the helper (P153, P157). Make them consistent.
   - `MintProductHelper` (P149) has **no file path**. The tests import it from `screens/coin_detail_screen.dart` (P239) without saying it is defined there as a public class. Give an exact path (e.g. `lib/utils/mint_product_helper.dart`) and the imports.
   - P218–223 calls each helper twice per build. Compute once.

5. **UnifiedCoinDetailsModal integration is claimed but doesn't exist.** R1 (P32) requires rendering in "the Overview tab of `UnifiedCoinDetailsModal`". `git grep UnifiedCoinDetailsModal` on origin/p7-v8.9 matches **only the five NET-810 plan mirrors**, and on origin/dev it matches nothing. No snippet, file or dependency is given. The modal is the subject of NET-813, which scored 74 FAIL and is unapproved. Either limit v1 to `_DetailsTab`, or declare an explicit dependency on an approved NET-813 with the exact Overview integration and ordering. Also name every card, browse, search and table surface where the fields must stay absent, and test that.

6. **Zero-urgency, neutral styling and value separation aren't enforced.**
   - **Status wording:** "On Sale", "Coming Soon" and "Sold Out" (P165–168) are retail-promotion and scarcity language. "Sold Out" in particular implies scarcity and conflicts with R3 and Eric's zero-urgency rule. Use neutral factual labels with an as-of date, e.g. "Available from U.S. Mint (as of …)", "Scheduled by U.S. Mint", "No longer offered by U.S. Mint", "Not available". Eric's excerpt allows the enum values, not promotional display strings.
   - **Allow-list for statuses:** `_formatStatusLabel`'s `default: return raw.replaceAll('_',' ')` (P169) passes through **any** unvetted source string, which could include urgency copy. Map only enum values and hide anything else.
   - **Freshness:** status is time-sensitive, but there is no `as_of`/source field. A stale "On Sale" would misstate fact. Add an as-of date or suppress the status after a defined staleness window.
   - **Styling:** R6 calls for muted gray, but the snippet just adds tuples to the shared `fields` list, so the rows render like every other row. No per-row style hook is shown, and `_kSubtext(context)` is cited without a file location.
   - **Value separation:** add an explicit rule and test that `productPriceUsd` never feeds value, estimate, melt, portfolio totals, sorting or the "Value pending AI estimate" face-value fallback.

7. **Tests are unit-only, even though the baton claims a widget suite, and the path doesn't exist.** B23 promises a "Unit and widget test suite", but P237–290 contains only five helper unit tests and no `testWidgets`. P234's `numista_tests/` directory does not exist; the real tests live in `numista_mobile/test/` (e.g. `coin_quantity_test.dart`, `auth_gate_navigation_test.dart`). Mark the suite **to be authored** at a real path. Add:
   - a `_DetailsTab` widget test for the exact label, order and hidden rows
   - card/browse absence tests
   - a check that rows have no InkWell or url_launcher (zero buy links)
   - neutral style and status allow-list mapping tests
   - negative, NaN, string and "TBD" inputs
   - round-trip preservation through 490/682
   - an export allow-list drop-by-default test
   - a check that the catalog lookup makes zero writes, using a fake writer

8. **Acceptance criteria, file manifest and rollback are missing.** There is no exact file manifest, no ordered execution steps, and no rollback for model and UI changes (record a baseline SHA and revert only the feature commits; main stays locked). There is no fit to the ~13 Nov catalog-live date. Plan-only, Stripe OFF, main lock, zero writes, AJ/PII exclusion (no collection identifiers in fixtures or logs) and the Eric-YES publish gate must be acceptance criteria, not just header text (P8, P304–309).

Note (non-blocking): the box `schema.json` `x-privacy` line says "No … price … fields exist in this schema by design", which now contradicts `product_price_usd`. Reword it to "no collector/owner price" when the schema is next revised.

## Prior must-fix closeout

N/A. This is v1.0 with no prior CoS or SAG score for NET-810.

## Handoff integrity

B6 says the plan is at `docs/`, and the plan is mirrored to docs/BATONS/RADIO NET/INBOX/OUTBOX. I checked this myself: the working-tree SHA256 is **2F0D694C1CB3920E67AF085E1DA7BF21DAECED1ACBFAC8EC7A046AA147C03038** (13,303 bytes, 11:50:57 PM EST 6 Nov) in all five places: `docs/`, `BETA TEST/Grok Bot/8 OCT 26/BATONS/`, `RADIO NET/`, `INBOX/` and **`OUTBOX/`**. The git blob is be7cbd33… in all five at cd8d083b, and the hash matches the box review copy. The GROKCOS_REVIEW baton (`BATON_NET-810_GROKCOS_REVIEW_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1_20261106-2355.md`, SHA256 78EBE90A03666D46…) is identical in BATONS/INBOX/RADIO NET/OUTBOX and matches the box copy. DONE_BATON (E0C9DE32…) is also in all four. The mirror claim **matches**, and **OUTBOX is not lagging** for NET-810 (an earlier listing that showed no NET-810 files in OUTBOX was out of date). One small asymmetry: OUTBOX has no copy of the 5 Nov FOLLOW-ON baton (BATONS/INBOX/RADIO NET do), but it does have the DESK_NOTE. Baton DTG 23:55 is about 4 minutes after the file mtimes (23:51) and the commit (23:52). I wrote nothing to the laptop.

## Rubric

| Dimension | Score |
|---|---:|
| Schema fidelity / source of truth / ingestion | 9/20 |
| Display rules / zero-urgency / value separation | 14/20 |
| Code correctness against real APIs / line citations | 11/20 |
| Allow-list gate / persistence safety / operational locks | 11/20 |
| Tests / verification / handoff integrity | 13/20 |
| **Total** | **58/100 FAIL** |

No AJ identifying values are reproduced here. These source checks do not certify a full PII or fact audit. No approval granted. The route is a revised plan scoring CoS 95+, then an independent SAG 95+, then Eric's typed YES. Separate gates for Firestore writes, publishing, rules and deploys remain. No messages or pings sent.
