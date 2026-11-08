# Independent SAG review cards22

Full plan submitted; packet chars 175723
Usage: {"prompt_tokens": 52418, "completion_tokens": 1741, "total_tokens": 98637, "prompt_tokens_details": {"text_tokens": 52418, "audio_tokens": 0, "image_tokens": 0, "cached_tokens": 1152}, "completion_tokens_details": {"reasoning_tokens": 44478, "audio_tokens": 0, "accepted_prediction_tokens": 0, "rejected_prediction_tokens": 0}, "num_sources_used": 0, "cost_in_usd_ticks": 3804220000}

The Cards v2.2 plan is not ready. The prior contrast failure is closed on the supplied colors, but the regex patch, the rollback script, the US face fallback, and one false citation still block a pass.

## Score / verdict

| Item | Result |
|---|---|
| Plan | FAILFIX PLAN v2.2, NET-780b Cards only |
| Pin checked | `4d17ca5e` (not `b0b05808`) |
| Score | **86 / 100** |
| Verdict | **FAIL** (PASS requires ≥95) |
| Execution | Not authorized. PLAN ONLY stands. |
| Images plan NET-780c | Not in this packet. Not scored. |

Deductions: −6, −3, −3, −2. No historical score was used as a target.

## Must-fixes

**MF-1 — High (−6). §3.C cent/nickel `RegExp` is not runtime-proven.**

The hunk replaces the verified `:431–434` patterns with negative lookbehind `(?<![\d.])`. The baseline at those lines uses only `\b` groups. The packet has no Dart `^3.11.3` citation that `RegExp` accepts lookbehind. `(?!\w)` is a lookahead and is a different feature. If the engine rejects `(?<!…)`, construction throws inside the `cleanYear == '2026'` branch and §6.2 cannot pass. `'5 cent'` is also only kept off the cent path by that lookbehind: the later `\bcent\b` alternative would otherwise see the word `cent`.

Fix: rewrite without lookbehind, preferably anchored full-string matches for the tested denom tokens, or cite engine support for this exact SDK and keep a test that would throw on `FormatException`. Do not treat “tests will be run later” as plan proof.

**MF-2 — Medium (−3). §4.D rollback script is not safe to run as written.**

`CARDS=<Cards-commit-hash>` is shell redirection, not an assignment. Under `set -euo pipefail` a literal run does not fail closed on a missing SHA. Branch check, dirty-tree check, Images-then-Cards order, and `git push origin p7-v8.9` (not `main`) are otherwise present.

Fix: require `CARDS_SHA` and optional `IMAGES_SHA` with `${VAR:?}` before any `git revert`. No angle-bracket placeholders.

**MF-3 — Medium (−3). USD face fallback is not US-scoped.**

`CollectionCardValuationRow` applies `resolveFaceValue` to `Denomination` / `denomination` for every card. The same screen has a World origin path and a `Country` field (`_F.country` at `:48`; origin filter at `:155–156`). A non-US row whose denom contains `cent`, `dime`, `quarter`, or `dollar` can render a USD face amount. `DenominationCanon` is explicitly US Mint nomenclature. No test covers a non-US row.

Fix: cite the real country/origin discriminator and gate the face fallback, with a negative test. Do not invent the country string.

**MF-4 — Low (−2). False line citation.**

§3.B says `_currencyFmt` is used at `:108`. Supplied `4d17ca5e` line 108 is `String? _selectedCoinId;`. Verified uses are `:3337` and `:3343` only. Those two lines do support “`intl` stays used.” The `:108` cite does not.

## Closed on this packet

- Contrast C3: `#E0BC4A` on `#1E2937` is about 8.03:1, not the old 6.9956 failure. Opaque dark chip fill matches cited `:3031` `#0D1520`. Light `#856404` on `#FFF3CD` stays above 4.5. The `0.03928` threshold is not WCAG’s `0.04045`, but it does not change these channel values.
- Quotes that match `4d17ca5e`: imports `:1–3` and `:40–44`; `_F.aiValue` `:72`; card block `:3015–3023` and `:3167–3192`; table AI column `:3338–3355`; inspector spans cited in §2.A; `parseFaceValue` `:76–87`; canon `:3–9`; mint service `:72–78`, `:341–345`, `:430–435`; `sdk: ^3.11.3`.
- Half-dime-before-dime and three-cent-before-nickel are in the parser hunk. Stated parser fixtures (`Half Dime`, `Three Cent Nickel`, `Five Cents`) follow that order.
- Default path does not delete inspector/eBay code. `_onSearchEbay` `:4408–4426` is preserved.
- No `b0b05808` catalog rows are pulled into the cards patch. `main` `9f04550a`, Stripe OFF, alerts not caps, no Firestore writes, and preview-only deploy are stated as locks, not as executed steps.
- Fixtures are synthetic. No promo-code material.

## Polish (no deduction)

- §4.C says regex lines `431–435`; the hunk is `431–434` only. Inserting `canonicalYear` at `:77` shifts later line numbers. Apply by exact old text, or the abort rule is meaningless.
- Case 7 only forbids `$0.00`. `'about twelve'` still renders `$about twelve`, which matches table `:3355` and the written assertion. Assert the actual string if that display is unacceptable.
- `'25c'` is already `isQuarter`; `'50c'` already hits `contains('50c')` at `:365` and becomes a half SKU. Those negative tests do not prove the new regex rejected them.
- §4.A does not assert `HEAD == p7-v8.9` or a clean index. Rollback does. A dirty tree can pass `git diff --quiet 4d17ca5e HEAD`.
- Optional inspector deletion in §4.B does not repeat the “no remaining references” grep required by §0.

## Uncertainties

- `:211` `_surface` / `0xFF1E2937` is ellipsis, not verbatim, and lines 201–2949 are absent from the packet. `:3031` virtual-child colors are verified. Do not treat `#1E2937` as confirmed.
- `_computeMeltForDoc` and a `home_dashboard` `parseFaceValue` call site are not in the supplied excerpts. Visible melt calls are `MeltValueService.compute` at `:3317` and `:3839`.
- `test/services/canonical_mint_asset_service_test.dart` is in the verify command and is not shown. Existence is unknown.
- `b0b05808` “lacks `canonical_mint_asset_service.dart`” is not proven here. The packet only shows catalog rows on that pin that are absent from `4d17ca5e`.
- `intl` `NumberFormat` in widget tests can depend on locale data. Not executed. No tools or tests were run for this review.
- `grade_badge_widget.dart` is imported by the new widget and was not shown. Eager import side effects are unknown.
- Full hash `4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235`, `c294fd3c`, and parked NET-816 / `9bbe20e4` are process claims, not pin evidence.

## Next gate

Revise to a Cards v2.3 plan that fixes MF-1 through MF-4. Do not execute, commit, push, deploy, or write Firestore. Founder YES is not the next step. After v2.3, SAG re-scores Cards alone. NET-780c still needs its own ≥95 review before any combined execution YES.