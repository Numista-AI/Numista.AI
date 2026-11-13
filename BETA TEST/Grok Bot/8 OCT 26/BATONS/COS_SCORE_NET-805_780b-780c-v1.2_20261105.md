# GB CoS SCORE — NET-805 / FAILFIX_PLAN_NET-780b_CARDS_v1.2 + 780c_IMAGES_v1.2

- **Scorer:** Grok Bot Chief of Staff · 2026-11-05 ~3:55 PM ET
- **Targets:** `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.2.md`, `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.2.md`, `ARGON_REVIEW_NET-780_FAILFIX_v1.2.md` (Argon 98)
- **Repo checked:** p7-v8.9 @ a5eeb19b; origin/main 9f04550a
- **Mode:** SCORE ONLY.
- **CoS:** **86 / 100 FAIL** · **Argon:** 98 · **SAG (grok-4.7):** **72 / 100 FAIL**
- **Eric YES gate:** BLOCKED. Revise baton **NET-809** to AG CoS v4.

## 1. NET-805 baton must-fix closeout (verified in code)

| # | Must-fix | Result | Evidence |
|---|---|---|---|
| 1 | Nickel regex trailing `\b` | **PARTIAL** | Real line 433 has a real `¢` (plan's "mojibake" claim is false). New pattern matches `15¢` (unanchored `5¢`) |
| 2 | CPG retail only, gold chip, no AI fallback | **PARTIAL** | Real 3023 still falls back to `m[_F.aiValue]`; plan fix correct for valueText, but chip condition also fires on `aiValue=='pending'` even when `cpgRetail>0`, hiding a real price |
| 3 | Redact cert + demo $ | PASS | `[cert no. redacted]`; $95/$23.40 gone |
| 4 | Census = CSV | PASS | 2,354/639/181/1/27 = 3,202 matches CSV. But "8,836 after 109 PII-flagged" unverifiable |
| 5 | Own-origin allowlist | PASS (order wrong) | Allowlist ok; null → placeholder immediately, skips `CoinImageService` (SAG-83 MF-4) so nickel card stays blank |
| 6 | Anchored excludes, list in local config | PASS | `.env.local`, anchored folder regex |
| 7 | To-be-created labels, `NAC1.*` keys | PASS | |
| 8 | Rollback + policy lines | **FAIL (rollback)** | `git checkout 9f04550a -- my_collection_screen.dart / canonical_mint_asset_service.dart` would wipe 12 commits (+703/−18) of p7 work incl. existing chip and MF-1 regexes. Policy lines present |

**Breakdown:** PII/redaction (20)=20 · Locks & plan-only (20)=18 · Baton MF closeout (35)=27 · Census/no-invention (15)=12 · Launch fit (10)=9. **Total 86.**

## 2. Must-fixes (blocking)
1. **Rollback:** replace `git checkout 9f04550a -- <file>` with `git revert <execute SHA>` / pre-execute p7-v8.9 pin (a5eeb19b). Never use locked-main SHA as a file restore point.
2. **Nickel regex:** anchor `(?<!\d)5¢`; Test 3 must fail `15¢`, `25c`; pass `5¢`, `5c`, `five cents`, `nickel`. Correct the line-433 citation (real `¢`).
3. **Image order (780c):** user photo → allowlisted own-origin URL → `CoinImageService` internal GCS reference → SVG placeholder.
4. **Chip:** show formatted `cpgRetail` whenever `> 0`; chip only when `cpgRetail <= 0`.
5. Drop or label "unverified" the 8,836 / 109 / 8,945 archive counts.
6. `$0.00`: remove GCS mirror/copy phases from this YES, or add a hard abort before any `gsutil`/storage call.

## 3. PII
NONE. Personal folder prefixes kept in `.env.local`; cert redacted.
