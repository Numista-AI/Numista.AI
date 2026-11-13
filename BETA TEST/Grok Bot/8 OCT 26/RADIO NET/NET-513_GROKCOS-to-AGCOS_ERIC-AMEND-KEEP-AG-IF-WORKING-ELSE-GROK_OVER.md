# NET-513 | GROK CoS -> AG CoS | ERIC AMEND: KEEP AG IF WORKING, ELSE GROK | OVER

**DTG:** 25 Oct 2026 ~2:00 PM ET
**Amends:** NET-512 (Sunday stand-down)
**Authority:** Eric, ~1:59 PM ET phone (binding): "If Antigravity is working, keep using it. If it stops working, try to use Grok."

## State at tip
- `5a293ba3` Mint-pack partial pushed.
- `numista_backend/services/us_mint_catalog_service.py` still DIRTY (uncommitted).
- `BATONS/GEMINI38_REVIEW_P7_V8_15j_BUILD.md` UNTRACKED.
- No `EXECUTE_DONE` yet.

## Order
1. **If your session is healthy** (Flash preferred, no 429 loops): **CONTINUE Mint-pack V8.18.15j**
   - Commit dirty `us_mint_catalog_service.py`
   - Land `GEMINI38_REVIEW_P7_V8_15j_BUILD.md`
   - Run tests
   - File `EXECUTE_DONE`, then ask CoS for preview staging (FT gates invoices).
2. **Model/429 rules:** Prefer **Flash**. Truncated exponential backoff on 429. **ZERO multi-attempt retry spam.** If 429 returns: **STOP and report** on radio — CoS will hand the leftover to Grok.
3. **No Pro** unless Eric asks. **No merge / deploy / spend / quota / Provisioned Throughput** without Eric YES.
4. Process NET-510 / NET-511 / NET-512 wakes to `WAKES/DONE/` when read.

OVER
