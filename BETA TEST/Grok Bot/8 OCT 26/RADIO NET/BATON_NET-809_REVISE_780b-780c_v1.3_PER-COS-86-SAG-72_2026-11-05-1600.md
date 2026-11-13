# BATON NET-809 - To: AG CoS v4 - PLAN ONLY: 780b Cards + 780c Images v1.3 (CoS 86 / SAG 72 FAIL on v1.2)
Source: GB CoS ~4:00 PM ET 5 Nov. Argon 98 PASS; CoS **86 FAIL**, SAG **72 FAIL**. Score files: `COS_SCORE_NET-805_780b-780c-v1.2_20261105.md`, `SAG_SCORE_NET-805_780b-780c-v1.2_20261105.md`. **Take after NET-808.**

Verified OK: cert/demo $ redaction; census 3,202 = CSV; allowlist (no denylist); anchored excludes in `.env.local`; to-be-created labels; `NAC1.*` keys; policy lines.

Fix:
1. **Rollback (both):** delete `git checkout 9f04550a -- my_collection_screen.dart / canonical_mint_asset_service.dart` (would wipe 12 p7 commits, +703/−18). Use `git revert <execute SHA>` / pre-execute p7-v8.9 pin (`a5eeb19b`).
2. **780b nickel regex:** `5¢` unanchored matches `15¢`; use `(?<!\d)5¢`. Test 3: fail `15¢`, `25c`; pass `5¢`, `5c`, `five cents`, `nickel`. Line 433 has a real `¢` — drop the "mojibake" claim.
3. **780c image order:** user photo → allowlisted own-origin URL → `CoinImageService` internal GCS reference → SVG placeholder (null must not jump straight to placeholder).
4. **780b chip:** show `cpgRetail` whenever `> 0`; chip only when `cpgRetail <= 0` (not on `aiValue=='pending'`).
5. Drop or label unverified the 8,836 / 109 / 8,945 archive counts.
6. `$0.00`: remove GCS mirror/copy phases from this YES or add a hard abort before any `gsutil`/storage call.
**Locks:** origin/main `9f04550a`, Stripe OFF, zero deploys, zero Firestore writes, no PII/AJ data. PLAN ONLY.
**Chain:** AG → Argon → GB CoS (95+) → SAG (95+) → Eric typed YES.
