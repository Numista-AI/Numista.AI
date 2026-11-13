# GB CoS independent score — NET-810 Mint Product Fields v1.5

**89/100 — FAIL. PASS requires 95+. Not ready for SAG approval, Eric YES or execution.**

Reviewed Sunday 8 November 2026, morning ET (America/New_York). Fresh-writer attempt 1; writer self-score disregarded. This is a full-plan static/document review, not a build/test result. No code was edited or executed, no Firestore touched, no deployment, push, or outside send.

## Artifact and actual refs
- Plan: `docs/PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.5.md`, 62,418 bytes.
- SHA-256: `64278a01d525e2f3db26ce01811ef43034fee03512840e6b91c632c48e67908e`; matches review baton.
- Actual `git rev-parse 4d17ca5e`: **4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235**.
- Actual `origin/dev`: **bde8b402d34675a39f2b3b4e872cb46f71a5b32a**.
- `origin/main` remains **9f04550a45fa4da082ba8948c2d89a521a90fa45**.
- Prior evidence read in full: RADIO_NET-856 and COS_SCORE v1.4 (93 FAIL).

## Prior residual closeout
- R1: Header/version/author now v1.5; obsolete duplicate v1.2-to-v1.3 rows removed. Historical v1.4 matrix remains expressly historical, not current API authority.
- R2: Unused Firestore field/parameter/import and unavailable fake_cloud_firestore import removed from proposed service. Positive improvement; new no-initialize test is narrower than a complete zero-writes proof (MF-3 below).
- R3: The main grounding headings now correctly use initState 182–193 and TabBarView 770–786; the latter explicitly truncates at 786.
- R4: Privacy test now uses testWidgets + tester.runAsync + rootBundle, not File/CWD. **Asset registration dependency is properly specified**, not a new defect: pin pubspec 92–96 lacks assets/catalog/, §4.4 adds it, and dev bde8b402 already has it at 97. Test must run against the implemented/dev asset bundle, not the unmodified pin.

## Remaining must-fixes

### MF-1 — Nonexistent full baseline SHA; unsafe rollback range
Plan lines 10, 69 and rollback lines 1306–1311 use `4d17ca5e0bc75f14e7aeb29a39f60d626c04f982`. That is NOT the object resolved by 4d17ca5e. `git cat-file -t` on the claimed full SHA failed: could not get object info. The real full SHA is recorded above.

The rollback also reverts `$PRE_EXEC_SHA..HEAD`, which would include unrelated commits added after the baseline rather than only NET-810 implementation commits. Replace every incorrect full SHA and specify an exact, recorded NET-810 execution-commit list (newest first, ancestry/conflict checks). Do not hard-code the source pin as a substitute for a captured pre-execution head. A rollback plan with an invalid object is not operationally usable. No rollback was run.

### MF-2 — The promised strict public/quarantine join is bypassed
- Plan 407–412 promises eligible only when `is_placeholder == false` and an exact four-field composite join.
- Proposed implementation 697–702 returns the overlay entry immediately for a matching personalRef, without looking up the catalog row or applying any placeholder gate.
- Composite implementation 715–737 rejects only `is_placeholder == true`; missing/null values are accepted. Missing facility and missing series on catalog rows also pass the comparisons. Blank mint mark maps to empty at 754–763, whereas §5.2 promises blank = Philadelphia.
- Concrete counterexample from the proposed API: supply `entries['NAC1.TEST']` and `rawEntries` containing the same NAC with `is_placeholder: true`, then a coin with personalRef `NAC1.TEST`. The primary path returns metadata at 701, rather than null.

Apply the eligibility requirement to BOTH joins; require explicit false; make incomplete/mismatched composite keys fail closed; reconcile blank-mint behavior. Add negative tests for a primary NAC pointing at a placeholder/missing row and missing facility/series/flag. Current placeholder test uses no primary overlay match, so it cannot catch this bypass.

### MF-3 — Zero-writes test does not cover asset initialization and swallowed failures
The no-Firebase initialization sentinel at 1171–1217 exercises a pre-seeded forTesting lookup and a passive DetailsTab; it never invokes ensureInitialized or the screen initState callback. The real asset-loading path at 663–690 catches every exception and returns empty metadata. Consequently a regression accessing FirebaseFirestore.instance inside that try could throw and be swallowed without this test failing. The test's claim that ANY such access fails is too broad.

Keep the useful no-initialize test, but specify observable initialization coverage and a non-vacuous datastore-boundary check/mutation criterion for the full lookup/render path. AC-R2 only scans two files for literal names; it excludes the modified screen and indirect calls. On this laptop `rg` is not installed (command-not-recognized during read-only citation lookup), so declare/install that prerequisite later with approval or specify a native PowerShell equivalent. This review did not install anything.

### MF-4 — Official-looking Mint values lack an acquired source
The real catalog identity and fields are verified, but the overlay's issue price, release date/time and as-of are not fields in that catalog. §4.3 explicitly says the government input is TO-BE-ACQUIRED. §5.5 nevertheless presents concrete overlay values beside a verified real record without clearly labeling those Mint values synthetic/unverified fixtures. Mark example overlay values as test-only and prohibit production emission until the named official input and provenance support each field. Do not promote a schema example into an accepted Mint fact.

## Citation audit (git show, not the dirty worktree)
- `coin_model.dart` 1–28, fields/defaults 81–125, and toFirestore 248–297 checked. Core quoted code matches; §3.1's class excerpt labelled 1–25 actually continues through country at 28.
- `coin_detail_screen.dart` 182–193; 490–494; 682–686; 770–787; 1513–1571; 3268–3309 checked. InitState, tab call and tile quotes match. The 490–494 quote includes the preceding comment at 489, so either extend the range or omit that comment. Proposed diff hunk labels 1551/1571 are not the quoted tile/class-end positions: actual return _DetailTile is 1561 and 1571 is a SizedBox, not the class closing brace. Distinguish illustrative snippets from apply-ready diffs.
- pubspec name is `numista_ai` at 1; catalog asset is missing at pin and present at dev 97; no fake_cloud_firestore dependency at pin. Pin has firebase_core 39 and cloud_firestore 40.
- Dev catalog is 5,895,259 bytes, 3,202 rows: 2,965 coins / 181 notes / 56 medals, 2,251 explicit non-placeholders / 951 placeholders. Both named 1921-D Morgan and 2024-W Eagle records exist and their quoted public fields match. Catalog is not present in the pinned mobile tree; dev is the expressly named source.

## Rubric
| Dimension | Score |
|---|---:|
| Schema/source/ingestion | 18/20 |
| Display/neutrality/value separation | 19/20 |
| Real APIs and citation correctness | 17/20 |
| Allow-list/persistence/operational safety | 17/20 |
| Tests and handoff integrity | 18/20 |
| **Total** | **89/100 FAIL** |

No identifying collector/AJ values or promo codes reproduced. PLAN ONLY, main locked, US-only, Stripe sandbox/OFF, alerts only (never caps). No approval inferred from a baton or agent. Any Firestore write or deploy requires its own Eric YES. Full-plan SAG review remains a separate gate after CoS 95+. DONE-renaming the review baton means review completed, NOT plan approved. No revision wake or outside message sent.