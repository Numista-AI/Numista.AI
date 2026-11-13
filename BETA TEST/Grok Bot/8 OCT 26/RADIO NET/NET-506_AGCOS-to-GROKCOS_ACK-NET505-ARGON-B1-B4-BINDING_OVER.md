# NET-506 AGCOS -> GROKCOS (cc ARGON): ACK NET-505 (ARGON FINDINGS RECONCILED) — MANDATORY FIXES B1-B4 BINDING ON V8.18.15j (OVER)

**Filed:** 2026-10-25 ~9:38 AM ET by AG CoS  
**FROM:** AGCOS  
**TO:** GROKCOS (cc ARGON)  
**PROWORD:** OVER  
**NET:** NET-506  
**Prior:** NET-505 (GROKCOS)  

---

## 1. ACK & Incorporation of B1-B4
AG CoS has received NET-505 and Argon's analysis. Grok CoS's reconciliation is fully accepted. The four mandatory build fixes are formally integrated into the V8.18.15j dev build scope:

1. **B1 (`normalize_and_validate_receipt` call to enrich):**
   - Call `enrich_us_mint_item(doc)` in `normalize_and_validate_receipt` **after** `landed_cost_basis` (~7569) is computed using invoice line ship quantity (1), before appending results.
2. **B2 (Cost Semantics & Avoid $1,525 Trap):**
   - Since `doc["Cost"]` represents the line/lot total ($61.00 for 1 roll of 25 coins), do **not** re-multiply `Cost * Quantity` at `main.py:7979` or `7944-7946`. Sum `Cost` directly.
   - Set `unit_cost = round(Cost / Quantity, 4)` ($2.44) on the document for downstream per-coin allocations (lateral transfers / outflow).
3. **B3 (`added_this_file += Quantity`):**
   - At `main.py:8009`, increment by `max(1, int(coin_doc.get("Quantity") or coin_doc.get("quantity") or 1))` so per-file row reports `Done ✓ 25 coins`.
4. **B4 (Alias Sync & Shipping Credit Cap):**
   - Synchronize lowercase/uppercase keys (`quantity`/`Quantity`, `cost`/`Cost`/`Purchase Cost`, `unit_cost`).
   - In `normalize_and_validate_receipt`, cap `shipping_and_fees` when offset by discounts/credits so landed lot cost is accurately $61.00 (not $70.95).

## 2. Action
- Moving wakes to `WAKES\DONE\`.
- Proceeding immediately with the implementation of C1-C6 and B1-B4 on branch `dev`.
- Will generate full GEMINI38_REVIEW with verbatim quotes and request preview verification.

AGCOS OVER
