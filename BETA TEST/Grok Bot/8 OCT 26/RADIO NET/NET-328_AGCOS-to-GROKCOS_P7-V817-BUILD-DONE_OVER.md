# NET-328 | AGCOS to GROKCOS | P7 V8.17 Build Done — Ready for Score
Filed 2026-10-18 19:53 ET.

## Commit
- **SHA:** `dbda922f7ae5c9b34e7ed60df10893b9d88fbd2b` (short: `dbda922f`)
- **Branch:** `p7-v8.9` → pushed to `origin/p7-v8.9`
- **Built on:** `7c5179cd` (V8.16)
- **Files touched:** 2 only (Rule 9.3: no GEMINI38 review)

## Changes
| File | Lines | Change |
|------|-------|--------|
| `numista_mobile/web/add_coins.html` | 527–552, 1157–1173 | Extracted `resolveApiBase(origin, search, liveUrl)` pure fn; new pinned `ALLOWED_HOST_RE` at line 541; `getApiBaseUrl()` delegates to it; self-tests (12 total: 4 accept + 8 reject) now call `resolveApiBase()` directly |
| `numista_mobile/web/scraper_dashboard.html` | 522–547, 907–923 | Same pattern; scan-service LIVE_URL; new pinned `ALLOWED_HOST_RE` at line 536; 12 self-tests |

## Pinned Regex (both files)
```
/^(?:[a-z0-9-]+---)?numista-(?:backend|scan-service)-(?:568985927038\.us-central1\.run\.app|qntvrqvxma-uc\.a\.run\.app)$/
```

## Old Broad Regex
Confirmed **completely gone** — `git grep` finds zero matches. Only the pinned regex remains.

## Self-Test Coverage (per file: 12 total)
- **Accept:** a1 (preview origin, no ?api=→live), a2 (us-central1 form accepted), a3 (uc.a form accepted), a4 (localhost→empty)
- **Reject:** r1 (prod origin), r2 (evil path), r3 (foreign run.app), r4 (http not https), r5 (prod firebase no preview prefix), r6 (wrong project number), r7 (wrong region), r8 (wrong uc.a hash)

## EXECUTE_DONE
- `BATONS\EXECUTE_DONE_P7_V8_17.md` ✅
- No GEMINI38 (Rule 9.3: ≤2 files) ✅
- No flutter/pytest run needed (HTML-only) ✅

Note: Eric's 8:30 PM ET stop tonight — finished at 7:53 PM, within window.
Handing baton. Ready for Grok CoS score.
OVER
