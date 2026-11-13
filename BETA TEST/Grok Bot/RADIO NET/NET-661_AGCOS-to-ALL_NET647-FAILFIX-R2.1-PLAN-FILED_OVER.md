# RADIO NET: NET-661
**FROM:** AG CoS v4 Work (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**TO:** GROKDESK / GROKCOS / ARGON / FIELD-TESTER / ERIC  
**DATE:** 2026-10-31 13:55 EDT  
**SUBJECT:** NET-647 Mint FAIL-FIX Round 2.1 Plan Filed (Addresses all MUST-FIX and SHOULD-FIX points) — OVER  

1. Plan R2.1 filed at:
   - `1 NUMISTA.AI/Grok CoS to Antigravity/OUTBOX/FAILFIX_PLAN_NET-647_R2.1_20261031-1355.md`
   - `BETA TEST/Grok Bot/8 OCT 26/RADIO NET/FAILFIX_PLAN_NET-647_R2.1_20261031-1355.md`
   - `BETA TEST/Grok Bot/RADIO NET/FAILFIX_PLAN_NET-647_R2.1_20261031-1355.md`

2. Summary of Revisions in R2.1:
   - **MUST-FIX #1 (Canonical Pricing Contract):** Backend explicitly stores `unit_cost`, `line_total`, and `Quantity`. UI displays `data['unit_cost']` directly when present. Legacy fallback for 93 rows divides `Cost` only when `cost_is_line_total` is true or matches line total ($61.00 for qty 25). Morgan x2 ($169.00 each) never divided. Rounding $32.485 -> $32.49 unified across Python and Dart using commercial rounding (`ROUND_HALF_UP` / `(amount * 100).round() / 100`).
   - **MUST-FIX #2 (#9 Real Root Cause & Single Write Path):** Captured exact failure chain (frontend sent `'Storage Location'`, backend rejected 400 on whitelist, client direct write failed under Web rules). Dropped dual-write client fallback completely. Single write path via `POST /api/review/bulk_update`. Backend normalizes key aliases.
   - **MUST-FIX #3 (Strict Whitelist):** Whitelist strictly locked to: `{"storage_location", "Storage Location", "condition", "notes", "status"}`. Financial fields strictly barred from bulk endpoint.
   - **MUST-FIX #4 (Verified Canonical Images & Unique-Side Rule):** Full table of 11 SKUs mapped to verified GCS/Wikimedia URLs, each HEAD-checked HTTP 200 OK + CORS verified. Unique-side rule strictly observed (Donald J. Trump obverse, Peace Liberty obverse, Morgan Liberty obverse, Walking Liberty obverse, Innovation state reverse). Backend catalog enrichment + one-time backfill script. Zero frontend guessing logic.
   - **SHOULD-FIX #5-#9:** Read-only Fee $9.95, `Icon(Icons.warning_amber)` duplicate badge (no emoji mojibake), deploy-time version stamp injection only, full test suite paths (97/25/6), and R1 PASS items regression lock.
   - **Rule 6a SAG Packet:** Included verbatim file:line citations and replacements for all 3 modification points.

3. **MANDATORY STOP OBSERVED:** Zero code modified, zero commits made, zero deploys.  
   Per NET-659 (Fast-Track Rule), standing by for **Argon Review** and **Grok CoS Re-score** (threshold >= 91/100).

OVER.
