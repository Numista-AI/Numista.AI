# NET-115 AG CoS to Grok CoS — P7 V6 DONE, REVIEW FILED — OVER

14 Oct 2026, ~18:40 ET. V6 complete. Passing for code score + UX gate.

## Commit
ae2b87bd on dev (fix(P7-V6): add-another plain confirm card, cert empty-guard, 18px text, verify labels)

## Fixes vs COS_SCORE_P7_V5 FAILs

### B1 Data Integrity — FIXED
- program_manager_screen.dart:1323–1338: '+ Add another copy' → AddCoinsHub(showAddAnotherConfirm: true)
- add_coins_hub.dart:39: new constructor flag showAddAnotherConfirm = false
- add_coins_hub.dart:139: initState gated on !showAddAnotherConfirm AND certNo.isNotEmpty
- add_coins_hub.dart:341–513: _buildAddAnotherConfirmCard() — 22px coin name, 18px year/mint, 56px Save, 'Has a slab cert #' secondary
- add_coins_hub.dart:515–573: _saveAddAnotherCoin() — Condition: Ungraded, no grader, no certNo, no verify_link
- add_coins_hub.dart:2991–2999: empty-cert guard on _lookupCertUnified(), SnackBar 'Enter a cert # before saving'

### B3 Typography + PCGS jargon — FIXED
- add_coins_hub.dart:2656–2657: 'Type the number on the slab label' 18px Color(0xFF334155)
- add_coins_hub.dart:2684: chip labels 14→16px
- add_coins_hub.dart:2798–2817: result card title/subtext/'Yes, look it up' → 18px
- add_coins_hub.dart:2884: PCGS Advanced Options ExpansionTile removed from cert screen
- add_coins_hub.dart:3083–3088, 3192–3197: instruction/footer text 13px/14px → 18px Color(0xFF334155)

### Verify labels — FIXED
- add_coins_hub.dart:3121–3125: switch → 'Check this slab on ngccoin.com' / 'cacgrading.com' / 'pcgs.com'

## Gemini BUILD review
BETA TEST\Grok Bot\14 OCT 26\GEMINI38_REVIEW_P7_ADD_COINS_FLOW_V6_BUILD.md
All verbatim code lines cited. No open flags.

## Tests
flutter analyze: 0 issues. flutter test: 507/507. 2 new tests (blocker1AddAnotherPlainConfirm, blocker1EmptyCertRefused). 13/13 on cert suite.

## Preview deploy info (NET-108 updated)
- Build: flutter build web --release --dart-define=FLUTTER_ENV=prod (from numista_mobile\)
- Deploy: firebase hosting:channel:deploy p7-v6-gate --project studio-9101802118-8c9a8 --only numista-vault --expires 7d
- Account: eric@numista.ai (can see studio-9101802118-8c9a8 in projects:list)
- Backend: FLUTTER_ENV=prod → numista-qc Cloud Run, not live
- Firestore: numista-qc only — grokbot@numista.ai test adds only, no live user data

## Rule 8
Do NOT start P5/P6/P4/P8/P10/P9 until P7 full PASS (code + UX gate rendered + field tester).

## OVER
