# REVISE NET-817 Cards (NET-780b) v2.2 → v2.3 (SAG 86 FAIL) — verified fix list
Verifier: GB CoS executor, 8 Nov 2026 ~11:52 AM ET. Tally: REAL 3 · FALSE 1 · UNCLEAR 0

## Must-fixes (priority order)
1. **[REAL MF-3] US-scope the face fallback.** The pin has `_F.country = 'Country'` (my_collection_screen.dart:48) and origin filter `_coinOriginFilter` 'All'/'U.S.'/'World' (:155–156). The plan has no country gate. Gate `resolveFaceValue` on the existing US discriminator (reuse the exact predicate the origin filter uses; quote it, don't invent a string). Add a negative test with a non-US row whose denom contains "cent".
2. **[REAL MF-2] Rollback vars.** Line 753 `CARDS=<Cards-commit-hash>` is a redirection under bash. Use `CARDS_SHA="${CARDS_SHA:?set CARDS_SHA}"` and an optional `IMAGES_SHA`. No angle brackets. **git revert only. No `reset --hard`.**
3. **[REAL MF-4] False citation.** Plan line 573 says `_currencyFmt` is at `:108`. Pin :108 is `String? _selectedCoinId;`, and the declaration is `:248` (`static final _currencyFmt =`). Uses are :3337 and :3343. Cite `:248, :3337, :3343`.

## Rejected (FALSE)
- **[FALSE MF-1] Lookbehind "not runtime-proven".** Dart `RegExp` uses ECMAScript semantics, and the Dart VM and web (JS) both support `(?<!…)` lookbehind. I ran the exact patterns from lines 664/666 under the ECMAScript engine (node). `1c/1¢/penny/cent/one cent/Lincoln cent` → cent. `5 cent/5c/nickel/Five Cents` → nickel. `15¢/25c/25 cent/15c/2.5c` → neither. "Three Cent Nickel" matches both, which the stated three-cent-first ordering handles. Optional hardening (no rewrite needed): add a test that constructs both RegExps, so a `FormatException` would fail loudly.

## Polish (from SAG; cheap)
Hunk is 431–434, not 431–435. Apply by exact old text, since inserting `canonicalYear` shifts lines. §4.A should assert HEAD == p7-v8.9 and a clean index. Case 7 should assert the actual string. `'25c'`/`'50c'` negatives don't prove the new regex (earlier branches catch them), so add a token that reaches the new regex.
