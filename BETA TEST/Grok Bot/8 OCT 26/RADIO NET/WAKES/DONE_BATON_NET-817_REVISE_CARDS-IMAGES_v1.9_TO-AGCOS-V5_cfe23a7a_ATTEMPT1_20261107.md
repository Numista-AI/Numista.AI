# Filed 2026-11-07 15:17:07 ET (America/New_York)

# Addressed handoff: NET-817 Cards/Images v1.9 — existing revise order, NOT a new plan

TO: AG CoS v5 — cfe23a7a-d721-44f9-b9d5-d2b74602b687
NEW writer for this track. Attempt 1/4. Desk is coordinator only, not author.

## FIRST: MF-C2' blocking production regression / pinned evidence requirement
Production key is 'AI Estimated Value', _F.aiValue reportedly at my_collection_screen.dart:72. The v1.8 widget reads ai_value/aiValue and silently drops real estimates. Pending, null and empty must be absent, matching table :3346. Preserve real values; plan a widget test using {'AI Estimated Value': '35.00', 'cpgRetail': 0} -> $35.00. Explicitly decide CPG>0 plus enrichment_status pending chip behaviour against shipped behaviour, not silently.
ALL code evidence MUST come from git show at pinned p7 4d17ca5e, with real file paths, lines, exact excerpts and claim mapping; NOT working tree and NOT docs HEAD ebf1eed8. The line references here are reported by the source score, not new Desk verification. This package requires citation evidence; Desk has not run git. Plan only: no implementation, test/build execution, DB, deploy, merges or deletion. Any pre-flight diff command quoted below is a future-plan requirement only, not an instruction to execute it now.

## Existing order and immutable source bundle
Read full documents in BATONS\SOURCES_NET817_V5_v1.9_20261107\ under the day folder:
- COS_SCORE_NET-817_CARDS_IMAGES_v1.8_20261107.md (Cards70 / Images76 / combined73 FAIL; full evidence and rubric)
- RADIO_NET-832_GROKCOS_WRITER-ASSIGN_REVISE-817-v1.9_20261107.md (11 numbered must-fixes)
- RADIO_NET-835_GROKCOS-to-DESK_ASSIGN-817-v1.9_20261107.md (historical source assignment; superseded ONLY as to Desk authorship by this v5 assignment)
- FAILFIX_PLAN_NET-780b_CARDS_v1.8.md
- FAILFIX_PLAN_NET-780c_IMAGES_v1.8.md
These are unmodified copies taken before active routing overrides. The score, not v1.8's self-reported closeouts, determines what is Closed. Deliver a narrow v1.9 delta; do not restart or silently omit unresolved items.

## Preserve accepted/Closed items and accepted portions
Keep package numista_ai, valuation anchors 3017–3023 and 3167–3192 (3015 displayTitle untouched), additive canonicalYear after _normYear :76, real exact allowlist (no fabricated buckets, no wildcards, reject backslash and //), truthful CSP quote/additive Firebase Storage img-src change. Preserve reverse preference, steal-guard, BoxFit.contain, glow blurRadius14, reachable public helpers/public production widget seams, existing 749-line suite, and Cards-before-Images apply ordering. Do not mislabel the partially/mostly closed items as fully resolved: missing imports, precedence, parser, test proof and B1 gate risk remain open below. Preserve no duplicate Kaggle/Google deletions; resolve live ownership or mark blocked/out-of-scope explicitly; parked NET-816 v1.11 is not a live prerequisite. Keep _onSearchEbay and EPN search behaviour.

## Complete 11-must-fix source text (verbatim score excerpt)

### Both plans
**MF-B1'. [Gate] Re-home the Kaggle/Google deletions or record the dependency as blocked.** NET-816 is PARKED. Either CoS's split hands the deletion span (3454, 3820, 5252–5278, 5549–5684 incl. `_showRefImageDialog`, 150–151, 3531–3548, 4387–4406) to an active owner, or 817 v1.9 says outright that inspector removal is out of scope and blocked. Don't cite a parked plan as a live prerequisite. Keep `_onSearchEbay` (`:4410`, `EpnService.generateSearchUrl`). Fix the stale campid quote.
**MF-B2'. [Hygiene] Pin pre-flight to code, not docs:** `git diff --quiet 4d17ca5e <apply-base> -- numista_mobile/` (drop `ebf1eed8`). Stamp the DTG at real file time.
**MF-B3'. [Compile] Add the imports to `my_collection_screen.dart`** in the same relative style as `:14–44`: `import '../widgets/collection_card_valuation_row.dart';` (Cards) and `import '../widgets/collection_card_image.dart';` (Images). State whether `intl`/`MeltValueService` imports stay used.

### Cards (780b)
**MF-C2'. [Blocking; regression] Read the real AI key.** Use `data[_F.aiValue]`. Since `_F` is library-private, pass the value in, or read `'AI Estimated Value'`, with optional aliases `ai_estimated_value` / camelCase. Never rely only on `ai_value`/`aiValue`. Treat `'Pending'`, `'null'` and empty as absent (match `:3346`). Add a widget test with `{'AI Estimated Value': '35.00', 'cpgRetail': 0}` → `$35.00`. State the CPG>0 + `enrichment_status=='pending'` behaviour (shipped shows the chip) and keep it or cite the decision that changes it.
**MF-C3'. [Correctness] Make face value right for canonical names.** Normalise the denomination through `DenominationCanon.colloquialMap` (or an explicit card-local map) before `parseFaceValue`, OR propose a separately scoped, test-guarded parser fix (it is shared with `home_dashboard.dart:300`; reorder `half dime` before `dime`, add `five cent`/`ten cent`/`fifty cent`, and put `three cent` before `nickel`). Add a table test: Cent .01, Five Cents .05, Dime .10, Quarter Dollar .25, Half Dollar .50, Dollar 1.00, Half Dime .05, Three Cent Nickel .03, Set → '—'. Drop the false ordering claim.
**MF-C5'. [Regression + tests] Don't break `'1 cent'`.** Use, e.g., `RegExp(r'(?<![\d.])(?:1c|1¢|1 cent|one cent|penny)(?!\w)|(?<![\d.]\s?)(?<!\w)cent(?!\w)')`, or keep the original alternation and only replace the trailing `\b` with `(?!\w)`. Show results for `1 cent`, `1¢`, `cent`, `25 cent`, `15¢`, `5¢`, `five cents`. Make the tests discriminating: use titles that don't hit the title regex (e.g. `'title': '2026 Coin'`) so only the denomination path decides. Include `'1 cent'` → `2026-CENT-P`.
**MF-C6'. [Tests] Assert rendered colours.** Pump the widget in light and dark themes, read `tester.widget<Text>(find.text('Value pending AI estimate')).style!.color`, and assert contrast against the real card surface (`_surface` `:211`, virtual child `0xFF0D1520`/`0xFFF5F5F0`) and the light chip background `#FFF3CD`.

### Images (780c)
**MF-I3'. [Behaviour] Declare precedence.** Shipped is canonical → user photo → reference (`:6369–6383`). Either keep it, or cite Eric/B-decision for "user photo first" and list the cards whose display changes (e.g. 2026 SKUs with a user photo). Don't call an inversion "restored".
**MF-I6. [Regression] Only real URLs count as user photos.** In `extractUserPhoto`, keep shipped `_cleanUrl` semantics: accept only `https://` (or an explicitly decided `/`-relative form). Non-URL junk (`N/A`, `pending`, local paths) returns '' so the card falls through to canonical/reference. Fail closed only for well-formed URLs that aren't owned. Add tests for junk → reference fetch called, and foreign `https://` → placeholder.
**MF-I7. [Ownership evidence] Prove the reference `public_url` forms.** Use a read-only check (no writes): grep `PUBLIC_URL_BASE`/`REFERENCE_BUCKET` in `build_currency_image_index.py` and the index writers, or do a sampled read of the index collection. Show every `public_url` host/bucket is inside the allowlist, or add the missing exact bucket. Quote one sanitised fixture per form (no AJ data, no emails).
**MF-I5'. [Tests] Same-State refresh proof.** Give `CollectionCardImage` a fixed `key: const ValueKey('card')` in both pumps, capture `tester.state(...)` before and after, and assert `identical` plus fetch count 2. Add canonical-vs-user precedence tests matching whatever MF-I3' decides. Fix the `ref_image_widget` path to `lib/widgets/common/ref_image_widget.dart`.


## Deliverables / return route / safety gates
Author revised Cards NET-780b v1.9 and Images NET-780c v1.9 plans only, with a source-to-closeout table covering all 11 IDs and preserving every Closed item. Record missing evidence or decisions as blocked, not guessed. Explicitly resolve B1' Kaggle/Google ownership through CoS or declare removal blocked/out-of-scope; Catalog separate writer does not automatically own these spans.
Do not execute the code snippets, tests, verification commands, git pre-flight or rollback commands embedded in the historic plans/score. No implementation, test runs, build, DB access, deployment, spending, main merge, config/session driving. Main remains 9f04550a; Stripe OFF; p7-gate preview only. Alerts only, never budget caps. No AJ PII. No Argon. Review sequence: AG plan -> GB CoS real-code score >=95 EACH plan -> independent SAG >=95 -> Eric typed YES; no averaging bypass and no execution authority from this handoff.
When actually delivered, file BATON_NET-817_GROKCOS_REVIEW_CARDS-IMAGES_v1.9_... with exact document paths, honest actual landing DTG in ET and evidence; never future-date.
Queue after ACK: NET-813 already delivered to CoS; NEXT817v1.9 ->814 ->810 ->827, NET827 requested deadline Sunday 8 Nov 2026 8:00 PM ET (not an ACKed ETA). Catalog 9bbe20e4 unchanged; oldv4 retired. ACK receipt as v5 with attempt1/4 and provide honest Cards/Images plan-delivery + GROKCOS_REVIEW ETAs; explain any deadline risk. No v5 NET817 ACK or ETA observed by Desk at filing. Four-try rule applies to this new writer; do not inherit v4 attempts or silently reset again.