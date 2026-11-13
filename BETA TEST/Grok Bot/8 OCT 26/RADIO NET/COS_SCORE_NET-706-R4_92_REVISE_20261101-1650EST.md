# COS SCORE - NET-706 R4 META-AD PRE-LAUNCH PLAN - 92/100 REVISE
Scorer: Grok CoS | Mode: docs-only, read-only verification | Plan: RADIO NET\PRELAUNCH_PLAN_NET-706_R4_META-AD_20261101.md (baton NET-716, radio NET-717) | 2026-11-01 4:46 PM ET

## Verdict: 92/100 REVISE (two must-fixes, both in Section 7 privacy text). Argon's 99 PASS is not accepted.
The SF-D route fix and the settled decisions are good. But the Section 7 AFTER text, if pasted verbatim, would break the Dart build and would create a new contradiction on the web privacy page.

## What I verified (origin/dev 32d4b42e, origin/main 9f04550a)
- [ERIC DECISION] markers: 0 left. Cutoff 2026-11-26T05:00:00Z and Free export $95.94 stated as settled. All 13 v3.2 prices still correct.
- Live HEAD: /us-coins 404; /zzz-unknown?utm_source=meta 404; /?utm_source=meta&fbclid=abc 200; /pricing?utm_source=meta&fbclid=abc 200, no redirect.
- Pixel block: not changed since R3 (byte-identical per R3 check; no edits outside Sections 4.2, 5.1 and 7).

## MUST-FIX
MF-B. Dart string escaping (privacy_screen.dart:139).
- The file is a single-quoted Dart string. The real line 139 reads `...using Google Cloud\'s Gemini...` (escaped apostrophe). The plan's BEFORE drops the backslash, so it is not a byte-exact quote.
- The plan's AFTER contains two unescaped apostrophes, in `collection's` and `Google Cloud's`. Pasted verbatim, this ends the string early and fails to compile.
- Fix: BEFORE must match line 139 byte-for-byte, including `\'`. AFTER must escape every apostrophe as `\'` (`collection\'s`, `Cloud\'s`).

MF-C. New contradiction in web/privacy.html:325 AFTER.
- The AFTER opens with "We do not sell, rent, trade, or share your personal data or coin collection details with third parties." It then says Meta Pixel data is used for ad measurement and that data is shared with third-party service providers. A blanket "do not share with third parties" contradicts both sentences that follow it.
- Fix: drop "or share" from that clause so it matches the Dart text and Eric's approved line: "We do not sell, rent, or trade your personal data or coin collection details to third parties." Keep the rest (no home addresses, Meta Pixel/cookies sentence, "Beyond this campaign measurement..." and the service-provider lead-in).

## SHOULD-FIX
SF-E. Section 4.2 line numbers are 2 low throughout. Actual "source" lines in origin/dev firebase.json: /privacy 66, /terms 70, /about 74, /pricing 78, /features 82, /faq 86, /login 90, /reset-password 94, /signup 98, /demo 102, / 106, /index.html 110, /wishlist 114, /wishlist/** 118, /attorney_portal 122, /claim 126, /claim/** 130. Redirects: /app 23 and /blog 28, and the redirect block also holds /signin 33, /forgot 38 and /reset 43. Either use these numbers or cite only the block range. (Note: the "source": "**" at line 248 is in the headers block, not a rewrite; the no-catch-all-rewrite invariant holds.)

## Score breakdown
Accuracy/no invention 30/30 | Pixel and 404/UTM 20/20 | Pricing and tiers 15/15 | Privacy integration 9/15 (MF-B, MF-C) | Line citations 8/10 (SF-E) | Test plan 10/10 = 92.
Not ready for SAG. Next: NET-719 fix-only R5 (Section 7 strings plus Section 4.2 numbers only).
