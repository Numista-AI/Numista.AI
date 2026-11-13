# NET-427 | AGCOS to GROKCOS | ARGON RCA FILED + PLAN_P7_V8_18_15b.v1 SUBMITTED FOR SCORING | OVER

**Filed:** 2026-10-22 ~12:55 ET  
**From:** AG CoS (Gemini 3.8 Flash resumed after Gemini 4 Argon RCA)  
**To:** GROK CoS  
**Subject:** Delivery of ARGON_VANISHING_COINS_RCA.md and PLAN_P7_V8_18_15b.v1.md  
**Baton:** Passed to GROKCOS (`BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md`)  

---

## 1. Argon RCA Complete (Read-Only)
- **Filed Document:** `BETA TEST\Grok Bot\22 OCT 26\ARGON_VANISHING_COINS_RCA.md`
- **Findings Summary:**
  1. No server-side deletion or schedule purge occurred (confirmed 0 backend DELETE calls, 0 scheduler triggers).
  2. Document IDs generated via `uuid.uuid4()` are unique; no overwrite of existing coin documents occurred.
  3. **Dual-Counting & Listener Cache Reversion:** US Mint invoice sets/lots are categorized separately in authoritative inventory calculation (`collection_inventory.py:217-248` `is_physical_coin`). The client briefly showed raw local count (346), then on listener re-sync/cache fallback reverted to displaying physical coin count (312).
  4. **Systemic Risk:** Low for coin document deletion, but invoices with `Invoice # N/A` can collide under attribute-key deduplication (`main.py:3882-4060`) if auto-clean runs. A synthetic invoice ID fallback is planned.

---

## 2. Plan V8.18.15b.v1 Submitted
- **Filed Document:** `BETA TEST\Grok Bot\22 OCT 26\PLAN_P7_V8_18_15b.v1.md`
- Incorporates:
  - **Item 1:** Tap targets < 48px fixed across NGC card, sidebar, and photo page.
  - **Item 2:** Exact NGC card copy: *"We can't look up NGC numbers automatically yet. Snap the label or type the details below."*
  - **Item 3:** Cert-photo OCR fix (`max_output_tokens` 256 -> 1024, `json_repair` fallback, 25s timeout, CACG reverse label prompt).
  - **Item 4:** US Mint invoice PDF parsing (Retailer, Date, Invoice #, Quantity preservation, polling timeout >60s, real error text).
  - **Item 5:** Synthetic invoice ID to guard against deduplication sweeps.

---

## 3. Status & Handoff
- Model switched back to **Gemini 3.8 Flash** per Founder Instructions.
- Awaiting Grok CoS plan score before build execution.
- Baton passed to GROKCOS.

OVER.
