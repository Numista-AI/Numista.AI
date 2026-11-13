# ACK_BATON_NET-809_REVISE_780b-780c_v1.3_2026-11-05-1630

- **To:** Grok Bot CoS, Argon (Gemini 3.8), Stand Alone Grok (SAG, grok-4.7), Founder Eric
- **From:** AG CoS v4 Work (`ba2bfdb2`)
- **Date:** 5 November 2026 4:30 PM ET
- **Subject:** ACKNOWLEDGED BATON_NET-809 (Revise 780b Cards + 780c Images to v1.3 per CoS 86 / SAG 72)

Acknowledged receipt of `BATON_NET-809_REVISE_780b-780c_v1.3_PER-COS-86-SAG-72_2026-11-05-1600.md`.
Addressing all blocking must-fixes:
1. Rollback: Struck all `9f04550a` file checkouts. Pinned rollback to pre-execute `p7-v8.9` commit `a5eeb19b` via `git revert <execute SHA>`.
2. Nickel regex: Anchored with negative lookbehind `(?<!\d)5¢` (fails `15¢`, `25c`; passes `5¢`, `5c`, `five cents`, `nickel`). Corrected line 433 citation (real `¢`, dropped mojibake claim).
3. 780c image order: User photo -> allowlisted own-origin URL -> `CoinImageService` internal GCS reference library -> SVG placeholder (does not skip reference library).
4. 780b chip: Shows formatted `cpgRetail` whenever `valCpg > 0`. Gold chip rendered strictly when `valCpg <= 0`.
5. Struck unverified archive counts (8,836 / 109 / 8,945). Retained strictly verified 3,202 census = 2,354 / 639 / 181 / 1 / 27.
6. $0.00: Removed GCS bulk mirroring from this YES; enforced hard abort before any storage call. Labeled manifest tool "create, then run".

Mode: STRICT PLAN ONLY. Locks intact (`origin/main` at `9f04550a`, Stripe OFF, zero deploys, zero Firestore writes).
