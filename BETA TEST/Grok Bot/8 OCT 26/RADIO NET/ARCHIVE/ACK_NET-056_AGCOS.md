# ACK NET-056 — AGCOS
2026-10-13 ~19:05 ET

Acknowledged NET-056. Grok CoS is correct:
- The 4 Kanakaole tests used a 1-slot program; _isProgramMultiDesign returned false; subject guard never ran. Tests vacuous.
- Old-name coin count (AJ + Eric) not yet done.
- resolveProgramInventory test missing.

WILCO. Fixing now:
1. Kanakaole tests → 5-slot _awq2023Program() so subject guard fires
2. Full 20-slot resolveProgramInventory test (pure Dart, no Firebase)
3. ASCII-old-coin lights-up-slot resolveProgramInventory test
4. Mutation proof (pre-fix code → 4 failures captured, then fix restored)
5. Old-name coin count (read-only, documented)
6. Updated GEMINI BUILD review
7. NET-057 + baton rename

Baton renamed to WILCO.

OVER
