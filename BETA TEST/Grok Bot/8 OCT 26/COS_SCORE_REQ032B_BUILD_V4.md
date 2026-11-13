# COS SCORE - T3b REQ_032B ALT SITE BUILD V4 (commit 39125bac on dev)
Scored by: Grok CoS, 13 Oct 2026 ~2:45 PM ET. Read numista_mobile/firestore.rules (deployed), firestore.rules.test.js, numista_backend/firestore.rules (NOT-DEPLOYED mirror). Cross-checked GEMINI38_REVIEW_T3B_V4_BUILD.md. Ran emulator myself.
PASS = code accepted on dev. DEPLOY needs Eric's typed YES. Nothing deployed.

## Verdict: PASS on dev. V3 required fix 1 is done on the deployed rules file. Emulator 38/38 green on my run.

## Emulator (run by Grok CoS, Java 21 Temurin)
`npx firebase emulators:exec --only firestore "npx jest firestore.rules.test.js --forceExit"` -> **Tests: 38 passed, 38 total.** Includes DENY writes + ALLOW reads for morgan_proposals, subaccounts, subscription, transferred_coins, transferred_currency.

## Checked in code (numista_mobile/firestore.rules)
1. Wildcard exclusions :109-116 include `'morgan_proposals', 'subaccounts', 'subscription', 'transferred_coins', 'transferred_currency'` (and prior coins/profile/settings/...).
2. Explicit server-only blocks :139-158 `allow read: if isOwner(email); allow write: if false;` for all five.
3. Tests in firestore.rules.test.js cover the five DENY writes and owner reads.

## Backend mirror (follow-up, not a deploy blocker)
numista_backend/firestore.rules has the five new server-only collections but still **omits `coins` and `profile` from the wildcard exclusion lists** and lacks the mobile coins is_demo block. Header correctly says NOT DEPLOYED. Re-sync from mobile or delete the mirror so nobody deploys the stale copy by mistake.

## Bundle
Ships under the same Eric YES as T1B (rules deploy from numista_mobile). Hold YES until T3 F1-F2 or Eric says otherwise.

Ball: see NET-029. No deploy.
