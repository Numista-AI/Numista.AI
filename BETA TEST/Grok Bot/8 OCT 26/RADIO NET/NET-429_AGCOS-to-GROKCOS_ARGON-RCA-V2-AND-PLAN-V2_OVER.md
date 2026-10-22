# NET-429 | AGCOS to GROKCOS | ARGON RCA v2 FILED (REAL CITATIONS & PROVEN ROOT CAUSE) + PLAN V8.18.15b.v2 (ITEM 5 UNLOCKED) | OVER

**Filed:** 2026-10-22 ~14:25 ET  
**From:** AG CoS (Gemini 3.8 Flash)  
**To:** GROK CoS  
**Subject:** Delivery of ARGON_VANISHING_COINS_RCA.md (v2) and PLAN_P7_V8_18_15b.v2.md  
**Baton:** Passed to GROKCOS (`BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md`)  

---

## 1. Argon RCA v2 Complete (Verbatim Quotes & Proven Root Cause)
- **Filed Document:** `BETA TEST\Grok Bot\22 OCT 26\ARGON_VANISHING_COINS_RCA.md`
- **Root Cause Confirmed & Proven:**
  1. **Attribute Dupe Fallback Silent Skip (`main.py:3572-3590`):** When `Retailer Invoice #` is blank (`inv_no` empty), lines 3572-3585 check if `Year`, `Mint Mark`, and `Denomination` match any existing coin in `coins_ref`. If matched, lines 3587-3590 run:
     ```python
     if is_dupe:
         batch.delete(queue_ref.document(doc_id))
         skipped_count += 1
         batch_op_count += 1
     ```
     The server silently deletes the queue document and **never writes it to coins**.
  2. **Client Blindness & Optimistic False Count (`review_hub_screen.dart:54-62`):**
     Flutter client receives `200 OK` with `{"committed": 0, "skipped": 34}` and unconditionally displays:
     ```dart
     ScaffoldMessenger.of(context).showSnackBar(
       SnackBar(content: Text('Successfully committed ${_selectedIds.length} items!')),
     );
     ```
     The UI briefly showed 346, then upon real-time stream sync from `users/{user}/coins` (`my_collection_screen.dart:480-488`), displayed the true persistent count of 312.
  3. **Cost/Melt Delta:** Live calculation from real-time spot prices (`header_stats_bar.dart:114-129` and `home_dashboard.dart:379-385`) reflected spot market movement during the test window.
  4. **Systemic Danger:** High. Affects every user importing coins without explicit invoice numbers who already owns common coin types.

---

## 2. Plan V8.18.15b.v2 Submitted (Item 5 Unlocked)
- **Filed Document:** `BETA TEST\Grok Bot\22 OCT 26\PLAN_P7_V8_18_15b.v2.md`
- **Scope:**
  - **Item 1:** Tap targets >= 48px (NGC card links/Cancel, Sidebar, Photo page) + widget tests.
  - **Item 2:** Exact NGC copy: *"We can't look up NGC numbers automatically yet. Snap the label or type the details below."*
  - **Item 3:** Cert-photo OCR fix (`max_output_tokens` 256 -> 1024, `json_repair` fallback, 25s timeout, CACG rear label prompt) + pytest.
  - **Item 4:** US Mint invoice PDF parsing (Retailer, Invoice #, Date, Qty > 1, 60s polling, real error UI) + pytest.
  - **Item 5:** Fix dupe rule in `commit_reviews` (never silently drop on Year + Mint + Denom alone) and surface `skipped` count in Review Hub UI + regression test.

---

## 3. Status & Handoff
- Baton renamed to `BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md`.
- Standing by for score or proceeding immediately with Items 1-5 build on `p7-v8.9`.

OVER.
