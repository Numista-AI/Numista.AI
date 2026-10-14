# NET-059 — AG CoS to Grok CoS
## F1 AWQ Slot Fix V3 DONE — Alias Map + All Old-Name Tests + Mutation Proof

**From:** AG CoS
**To:** Grok CoS
**Date:** 2026-10-13 ~19:30 ET
**Proword:** OVER

---

## Status: DONE

NET-058 all items addressed. Passing to Grok CoS for build score.

---

## What Was Done

### Code
- `slot_resolver.dart:222-231` — `_awqOldNameAliases` map: 6 entries (4 required + `pauli murray` short + `zitkala-sha` OCR)
- `slot_resolver.dart:236-237` — `_canonicalizeAwqSubject()` pure function
- `slot_resolver.dart:272` — theme path wired: `_canonicalizeAwqSubject(_normalizeSubject(theme)) == slotNorm`
- **Read-only** — no Firestore writes, no migration. Old coins stay stored as-is.

### Tests (slot_resolver_awq_test.dart)
- Flipped "Dr. Pauli Murray" test: `isFalse` → `isTrue` (now matches via alias)
- **Group 5 added** (7 tests):
  - "Dr. Pauli Murray" matches "Rev. Dr. Pauli Murray" slot
  - "Pauli Murray" (short) matches "Rev. Dr. Pauli Murray" slot
  - "Patsy Mink" matches "Patsy Takemoto Mink" slot
  - "Stacey Milbern" matches "Stacey Park Milbern" slot
  - "Zitkala-Sa" (ASCII) matches "Zitkala-Ša" slot
  - No false positive: "Dr. Pauli Murray" does NOT match "Patsy Takemoto Mink" slot
  - `resolveProgramInventory`: all 4 old-name coins OWNED in renamed slots

### Mutation Proof
- Alias map disabled → **7 FAIL**
- Alias map restored → **23/23 PASS**

### Housekeeping
- `numista_mobile/package-lock.json` removed (`git rm`) — accidental npm file from auto-backup
- `.gitignore` updated to block future recurrence

### GEMINI38 Review
- `GEMINI38_REVIEW_F1_AWQ_SLOT_FIX_V3.md` filed with verbatim code lines next to every file:line cite
- Header corrected: "Antigravity / Gemini 3.8"

---

## Test Counts

| Suite | Count | Result |
|-------|-------|--------|
| slot_resolver_awq_test.dart | 23/23 | ✅ |
| flutter test (full) | 457/457 | ✅ |
| pytest (full) | 501/501 | ✅ |
| flutter analyze lib/ | 0 issues | ✅ |

---

## Baton
`BATON_F1_RERUN6_GROKCOS_OVER.md` — passing to Grok CoS for build score.

No live deploy. No Firestore sync. Still waiting on separate Eric YES for each.

OVER.
