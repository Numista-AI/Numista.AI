# SAG SCORE NET-805 / FAILFIX_PLAN_NET-780b_CARDS_v1.2 + 780c_IMAGES_v1.2 (xAI API, grok-4.7, 2026-11-05 ~3:55 PM ET)

Inputs: plan text + GB CoS repo evidence (read-only, p7-v8.9 a5eeb19b / origin/dev / origin/main 9f04550a).

## SAG_SCORE: 72/100 FAIL

## MUST_FIX
1. Rollback still restores `9f04550a` onto the two Dart files (`git checkout 9f04550a --` in both plans). That SHA is 12 commits and +703/−18 behind `p7-v8.9` on those files and would wipe existing p7 work, including the Valuation Pending chip and the cent/nickel regexes. Restore only with `git revert <execute SHA>` or the pre-execute `p7-v8.9` pin (`a5eeb19b`). Do not use the locked main SHA as a file restore point.
2. Nickel pattern is still wrong, and the live citation is wrong. Repo line 433 is `RegExp(r'\b(5c|5¢|five cents?|nickel)\b')` with a real `¢`, not mojibake. The proposed `5¢` alternative is unanchored: it matches `15¢`. Anchor it (`(?<!\d)5¢` or equivalent). Test 3 must fail `15¢` and `25c`, and must pass `5¢`, `5c`, `five cents`, and `nickel`.
3. 780c still sends a null allowlist result straight to the SVG placeholder. Card 2 (nickel) stays broken unless `CoinImageService` (internal GCS reference library) runs after the allowlist miss and before the placeholder. 780b §4.B mentions that fallback; 780c §3.1 and §4 step 1 do not. Required order: user photo, then allowlisted own-origin URL, then `CoinImageService`, then SVG.
4. Valuation chip still hides a real CDN price. `isValuationPending` is true when `aiValue` or `enrichment_status` is pending even if `cpgRetail > 0`. Show formatted `cpgRetail` whenever it is `> 0`. Chip only when `cpgRetail <= 0`. No AI, melt, issue, or cost figure in the primary slot.
5. Unverifiable counts are still stated as verified. `8,836` generic files after `109` PII-flagged paths (and the `8,945` split) cannot be checked from the repo. Drop them or mark them unverified. Keep only the CSV-matched census: 3,202 = 2,354 / 639 / 181 / 1 / 27.
6. `$0.00` is stated with no stop-on-exceed, while 780c §3.3 and §4 still describe GCS mirror/copy phases. Storage for mirrored images is not literally $0, and the Thanksgiving cut already says bulk mirror of 3,202 images is not authorized by this YES. Remove those mirror steps from this YES, or add a hard abort before any `gsutil`/storage call.

## NON_BLOCKING
- GCS rollback is copy-only plus manifest deactivation. No object-generation restore is named. Acceptable only if deactivated manifest keys are never served; say that in one line.
- Allowlist hosts `numista.ai` and `numista-vault.web.app` are own origins and are fine.
- Laws tab is untouched; no new outbound links. If a later edit adds any, Congress.gov only.
- 780c §5 still says “Execute” a script marked to-be-created. The label is present; keep “create, then run” so an executor does not treat the tool as already in the tree.

## PII_FINDINGS
NONE. Cert number is redacted, demo dollar figures are gone, and personal directory prefixes are kept in `.env.local` only. No personal names beyond Eric.

## 2_SENTENCE_PLAIN_ENGLISH
This draft does fix the raw “Pending” price, the 3,202 image count, and the privacy folder filter, but it is not safe to approve. The nickel matcher still treats 15¢ as a nickel, the undo command would erase the current p7 work, and a blocked picture still skips the internal photo library and jumps straight to an empty placeholder.

## RATIONALE
Repo evidence closes redaction, the 3,202 census, the allowlist (not a denylist), anchored folder exclusions, to-be-created labels, and `NAC1.*` keys. It does not close the unanchored `5¢` false positive, the false mojibake citation, the destructive checkout of `9f04550a`, or the placeholder-before-reference-library order required to fix card 2. The chip condition can hide a positive CDN retail value, and unverifiable archive counts plus an unenforced `$0` mirror path still violate “nothing invented” and the spend lock.

## REPO EVIDENCE SENT
REPO EVIDENCE (GB CoS, read-only, 5 Nov 2026 ~3:50 PM ET). p7-v8.9 HEAD a5eeb19b; origin/main 9f04550a.
1. canonical_mint_asset_service.dart:433 real = RegExp(r'\b(5c|5¢|five cents?|nickel)\b') (the ¢ is a real ¢, not mojibake as plan states). Plan fix RegExp(r'(?:\b5c\b|5¢|\bfive cents?\b|\bnickel\b)', caseSensitive:false). Python test: '5¢' T, '5c' T, 'five cents' T, 'nickel' T, '25c' F, '15¢' TRUE (false positive - 5¢ unanchored; needs (?<!\d)5¢ or \b5¢), '$5 coin' F. Lines 74, 118-121 quoted correctly.
2. my_collection_screen.dart:3017-3023 real: valCpg=_parseNumber(m['cpgRetail']); finalVal=valCpg; valueText = finalVal>0 ? fmt.format(finalVal) : (m[_F.aiValue]?.toString() ?? '—'). So live code still shows raw AI value / 'Pending' string when cpgRetail is 0. Plan fix sets valueText = valCpg>0 ? fmt : '—' and gold 'Valuation Pending' chip when valCpg<=0 -> CORRECT and closes MF-2.
3. Cert number redacted to [cert no. redacted]; $95 / $23.40 demo figures removed -> closed.
4. 780c census = 3202: 2354/639/181/1/27 -> matches CSV (CSV verified). 1,420/1,180/602 removed -> closed. "8,836 generic files after 109 PII-flagged" not verifiable from repo.
5. 780c allowlist guard sanitizeAndAllowlistUrl: allowlist (no denylist) -> closed. BUT on null it "immediately displays SVG placeholder" - prior SAG-83 MF-4 required CoinImageService (internal GCS reference library) to run BEFORE placeholder so card 2 (nickel) is actually fixed; 780b §4.B mentions CoinImageService fallback but 780c guard order doesn't state it. Allowlist also admits numista.ai and numista-vault.web.app hosts (own origins, OK).
6. Anchored folder regex; personal prefixes kept in .env.local, not pushed -> closed.
7. tools/verify_catalog_manifest_pii.py and assets/catalog_image_manifest.json marked to-be-created; NAC1.* keys -> closed.
8. Rollback: both plans use "git checkout 9f04550a -- my_collection_screen.dart / canonical_mint_asset_service.dart". FACT: 12 commits and +703/-18 lines on p7-v8.9 since 9f04550a in those two files; this checkout would wipe all p7 work (incl. existing Valuation Pending chip, MF-1 cent/nickel regexes), not just this fix. Correct: git revert <execute SHA> or pin to the pre-execute p7-v8.9 SHA (currently a5eeb19b). GCS rollback = copy-only + manifest deactivation; no object-generation restore named.
9. $0.00 cap stated in both; no stop-on-exceed mechanism (GCS storage for mirrored images is not literally $0). Policy lines (ai_replica_images only, US-only, no wholesale, numista.ai Thanksgiving cut) present.
