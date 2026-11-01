# COS SCORE (independent re-verification) - NET-706 R4 - 92/100 REVISE
Scorer: Grok CoS | 2026-11-01 4:55 PM ET | docs-only | origin/dev 32d4b42e
This confirms COS_SCORE_NET-706-R4_92_REVISE_20261101-1650EST.md, re-verified from scratch. Argon's 99 PASS is not accepted.

## Fixed
- MF-A (structure): the change rewrites the existing privacy_screen.dart:139 and privacy.html:325 in place, with no new section. The duplicate standalone non-sale pledge is gone. The privacy.html Section 3 list item is an extension, which is OK.
- [ERIC DECISION] markers: 0 left. NET-714A is settled: no home addresses; cutoff 2026-11-26T05:00Z; Free export $95.94.
- Pixel snippet: byte-identical to the spec. All 13 v3.2 prices are correct. No invented items. /app and /blog are correctly cited as redirects.
- Live HEAD: /us-coins 404; /zzz-unknown?utm_source=meta 404; the UTM routes return 200.

## MUST-FIX (still open)
- MF-B: Plan line 302 (BEFORE) omits the \' that is in real line 139. In the AFTER (plan line 307), collection's and Cloud's are unescaped inside a single-quoted Dart string, so the build would fail. Escape them as \'.
- MF-C: Plan line 320 (privacy.html AFTER) says "do not ... share ... with third parties" and then describes sharing with Meta and service providers, which contradicts itself. Use "We do not sell, rent, or trade your personal data or coin collection details to third parties."

## SHOULD-FIX
- SF-E: The firebase.json lines in Section 4.2 are 2 low. Real: /privacy 66, /terms 70, /about 74 ... /claim 126, /claim/** 130. Redirects: /app 23, /blog 28 (plan says 24-33).

Score 92: Privacy 9/15, Line citations 8/10, all else full. Next: the existing NET-719 R5 fix-only (no new NET number).
