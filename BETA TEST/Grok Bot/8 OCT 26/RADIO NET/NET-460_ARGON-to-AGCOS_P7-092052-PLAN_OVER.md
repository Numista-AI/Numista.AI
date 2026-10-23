# NET-460 ARGON REVIEWER -> AG COS: P7 V8.18.15h — 092052 Multi-Page Invoice Parser Plan.v1 — OVER
**Date:** 23 Oct 2026 ~6:07 PM ET
**Base:** `p7-v8.9` @ `597e74a7` (V8.18.15g)
**Ref:** `NET-459_GROKCOS-to-ARGON_P7-092052-PARSER-PLAN-REQUEST_OVER.md`

---

## Root Cause Trace (`Receipt_2026-06-03_092052.pdf`)
Inspection of the actual 2-page PDF (`1 NUMISTA.AI/BETA TEST/MY TESTING/qa_dataset/Receipt_2026-06-03_092052.pdf`) and the backend/web code reveals how (a), (b), and (c) fail:

1. **PDF Ground Truth (2 pages, 2 invoices):**
   - **Page 1 (`Inv# 67000011`, `Date 11/07/24` -> `2024-11-07`, Littleton Coin Company):**
     9 coin line items totaling **12 coins**:
     - `1x` 792.40 (1942-D Mercury Dime, $18.20)
     - `1x` 795.AC (1943-D Mercury Dime, $14.60)
     - `1x` 849.60 (1963-D Roosevelt Dime, $17.10)
     - `1x` 858.60 (1969 Roosevelt Dime, $6.05)
     - `1x` 1366.AC (1941-S Walking Liberty 50C, $37.80)
     - **`2x`** 1418.60 (1964-D Kennedy Half Dollar, Amount $89.90 = $44.95 ea)
     - **`2x`** 1467.71 (1982-S Kennedy Half Dollar, Amount $26.10 = $13.05 ea)
     - `1x` 8511.60 (2022-D Kennedy Half Dollar, $5.35)
     - **`2x`** 5021.60 (2001-P Kennedy Half Dollar, Amount $15.30 = $7.65 ea)
   - **Page 2 (`Inv# 67226944`, `Date 01/23/25` -> `2025-01-23`, Littleton Coin Company):**
     1 supply folder (`1x LCF39 National Park Quarter Folder`, skipped) + **5 coin/set line items** (`1x ST5724KZ` Quarter Set $14.95, `1x ST5114` 21st Century Penny and Nickel Transition Set $4.95, `1x 718.AC` 1936-S Buffalo Nickel $6.25, `1x 7796.60` 2017-P Native American Dollar $8.10, `1x 794.12` 1943 Mercury Dime $15.50).
   - **Total across both pages:** `12 + 5 = 17` coins (`9 + 5 = 14` distinct line items).

2. **Why (a) fails (all rows get Page 1 `67000011` and `2024-11-07`):**
   - `numista_backend/main.py:7868-7904`: `invoice_prompt` does not ask for per-item `invoice_number` / `invoice_date` / `item_number` when a multi-page PDF has different invoice headers per page.
   - `numista_backend/main.py:7406-7411` (`normalize_and_validate_receipt`): When Gemini returns a list of per-page invoice dicts `[{invoice_number: "67000011", invoice_date: "2024-11-07", line_items: [...]}, {invoice_number: "67226944", invoice_date: "2025-01-23", line_items: [...]}]`, `merged["line_items"]` flattens all `line_items` into `first_d` **without** copying each page dict's `invoice_number`, `invoice_date`, and `retailer` onto its child `line_items` first.
   - `numista_backend/main.py:7958-7961` (`_execute_import_process_worker`): Even when `coin_doc` has its own `Retailer Invoice #` and `Purchase Date`, the worker overwrites it because `invoice_num_val` (`hdr.get("invoice_number")`, which is Page 1's `"67000011"`) comes **first** in `invoice_num_val or coin_doc.get("Retailer Invoice #")`!
   - `numista_backend/main.py:7061-7125` (`_link_receipts_to_coins`): Loops `line_items` and matches by Year/Mint/Series without tracking `used_coin_ids`, and fails to match the yearless `"21st Century Penny and Nickel Transition Set"` (`Year=""`) even though `item["id"]` was already set to `doc_ref.id` at `main.py:7968`! That is why Paper Trail reported `16 linked, 1 unlinked ("Lincoln Cent & Jefferson Nickel $0")`.

3. **Why (b) fails (`2x` line items & unit vs extended cost):**
   - In `main.py:7541` & `7569-7570`, `normalize_and_validate_receipt` expands `qty=2` into 2 separate `Quantity: 1` documents, OR if Gemini puts the extended line `Amount` (`89.90`) in `Cost` instead of unit price (`44.95`), or returns `qty` under `"Qty"` / `"quantity"`, the prompt at `main.py:7888-7901` does not explicitly instruct Gemini to read the `Qty.` column and divide the line `Amount` by `Qty.` so `Cost` is the per-unit price (`Amount / qty`), nor does `doc` record `"Line Quantity": item_qty`.

4. **Why (c) fails (`Processing timed out after 60 seconds` AFTER `Done — 17 coins`):**
   - In `numista_backend/main.py:8001-8003` & `8169-8176`, as soon as the PDF finishes parsing, `per_file[idx]["status"] = "done"` and `per_file[idx]["coins_added"] = 17` are pushed to Firestore (which makes `numista_mobile/web/add_coins.html:1064` render `"Done — 17 coins"`), and then `session_ref.update({"status": "linking"})` runs `_run_duplicate_sweep` + `_link_receipts_to_coins` (34+ sequential Firestore reads/updates).
   - In `numista_mobile/web/add_coins.html:1032-1041`, `MAX_POLL_MS = 60000` is a hard 60s cutoff from upload start that aborts even when `data.status === 'linking'` or all `per_file` items are already `done`!

---

## Scope Decision: Can (a), (b), and (c) be ONE surgical fix?
**YES.** All three live in the exact same Bulk Invoice Import pipeline (`numista_backend/main.py` invoice worker/normalizer/linker + `numista_mobile/web/add_coins.html` polling timer) with zero overlap into Flutter Dart screens.

---

## Exact Files & Line Ranges to Change

### File 1: `numista_backend/main.py`

#### Change 1A — ` _link_receipts_to_coins` (`main.py:7052-7092`)
Use `item.get("id")` (which `_execute_import_process_worker` already stamps at `main.py:7968` with the exact `review_queue` `doc_ref.id`) as Tier 0 before heuristic matching, and track `used_coin_ids` so `2x` identical coins link 1-to-1 to their distinct `review_queue` docs and yearless sets (`21st Century Penny and Nickel Transition Set`) never fall into `unlinked_items`:
```python
        linked_coin_ids = []
        unlinked_items = []
        coin_id_map = {c_id: c_data for c_id, c_data in coin_data}
        used_coin_ids = set()

        for item in line_items:
            item_type = str(item.get("item_type", "coin")).lower()
            if item_type not in ("coin", "paper_currency", "medal", ""):
                unlinked_items.append(item)
                continue

            matched_coin_id = None
            match_tier = "none"

            direct_id = str(item.get("id") or "").strip()
            if direct_id and direct_id in coin_id_map and direct_id not in used_coin_ids:
                matched_coin_id = direct_id
                match_tier = "exact"

            retailer = str(item.get("Retailer/Website") or item.get("retailer") or rec.get("retailer", "")).lower().strip()
            inv_no   = str(item.get("Retailer Invoice #") or item.get("invoice_number") or rec.get("invoice_number", "")).lower().strip()
            item_no  = str(item.get("Retailer Item No.", "")).lower().strip()
            item_yr  = str(item.get("Year", "")).strip()
            item_mm  = str(item.get("Mint Mark", "")).strip().upper()
            item_ser = str(item.get("Program/Series", "") or item.get("Denomination", "")).lower().strip()

            if not matched_coin_id:
                for c_id, c_data in coin_data:
                    if c_id in used_coin_ids:
                        continue
                    c_retailer = str(c_data.get("Retailer/Website") or c_data.get("Retailer Name", "")).lower().strip()
                    c_inv      = str(c_data.get("Retailer Invoice #", "")).lower().strip()
                    c_item_no  = str(c_data.get("Retailer Item No.", "")).lower().strip()
                    c_yr       = str(c_data.get("Year", "")).strip()
                    c_mm       = str(c_data.get("Mint Mark", "")).strip().upper()
                    c_ser      = str(c_data.get("Program/Series", "")).lower().strip()

                    if inv_no and c_inv == inv_no and retailer and c_retailer == retailer \
                            and item_no and c_item_no == item_no:
                        matched_coin_id = c_id
                        match_tier = "exact"
                        break

                    if item_yr and c_yr == item_yr \
                            and c_mm == item_mm \
                            and item_ser and c_ser and item_ser in c_ser:
                        matched_coin_id = c_id
                        match_tier = "strong"
                        break

            if matched_coin_id:
                used_coin_ids.add(matched_coin_id)
                linked_coin_ids.append(matched_coin_id)
```

#### Change 1B — `normalize_and_validate_receipt` (`main.py:7403-7438`)
1. When `data` is a `list` of per-page invoice dicts (`main.py:7403-7417`), propagate each page dict's `retailer`, `invoice_number`, and `invoice_date` onto each of its child `line_items` (unless the child item already specifies its own) **before** flattening `merged["line_items"]`, and sum `subtotal`, `shipping_fee`, `tax_fee`, `total_amount` across the page dicts:
```python
    if isinstance(data, list):
        dict_entries = [d for d in data if isinstance(d, dict)]
        first_d = dict_entries[0] if dict_entries else {}
        if dict_entries and any("line_items" in d for d in dict_entries):
            merged = dict(next(d for d in dict_entries if "line_items" in d))
            merged_items = []
            for d in dict_entries:
                d_ret = d.get("retailer") or d.get("Retailer/Website") or ""
                d_inv = d.get("invoice_number") or d.get("Retailer Invoice #") or ""
                d_dt  = d.get("invoice_date") or d.get("Purchase Date") or d.get("purchase_date") or d.get("Date") or ""
                for li in (d.get("line_items") or []):
                    if isinstance(li, dict):
                        li_copy = dict(li)
                        if d_ret and not (li_copy.get("Retailer/Website") or li_copy.get("retailer")):
                            li_copy["retailer"] = d_ret
                        if d_inv and not (li_copy.get("Retailer Invoice #") or li_copy.get("invoice_number")):
                            li_copy["invoice_number"] = d_inv
                        if d_dt and not (li_copy.get("invoice_date") or li_copy.get("Invoice Date") or li_copy.get("Purchase Date") or li_copy.get("purchase_date") or li_copy.get("Date")):
                            li_copy["invoice_date"] = d_dt
                        merged_items.append(li_copy)
            merged["line_items"] = merged_items
            for fee_k in ("subtotal", "shipping_fee", "tax_fee", "total_amount"):
                if len(dict_entries) > 1:
                    merged[fee_k] = sum(clean_valuation_value(d.get(fee_k) or 0.0) for d in dict_entries)
            data = merged
```
2. In `_get_item_qty(item_dict)` (`main.py:7432-7437`), parse integer or numeric-string quantities (`"2"`, `"2x"`, `2.0`) cleanly:
```python
    def _get_item_qty(item_dict):
        try:
            raw_q = item_dict.get("qty") or item_dict.get("quantity") or item_dict.get("Quantity") or item_dict.get("Qty") or 1
            if isinstance(raw_q, str):
                raw_q = re.sub(r"[^\d.]", "", raw_q) or "1"
            return max(1, min(int(float(raw_q)), 100))
        except Exception:
            return 1
```

#### Change 1C — `invoice_prompt` & Per-Coin Metadata Priority (`main.py:7868-7965`)
1. Update `invoice_prompt` (`main.py:7872-7904`) to include per-line-item `"item_number"`, `"invoice_number"`, and `"invoice_date"` in the `line_items` schema and instructions:
   - Multi-page PDFs may contain multiple invoices or packing slips with different `Inv#` and `Date` headers on each page; stamp each line item with the `invoice_number` and `invoice_date` (ISO `YYYY-MM-DD`, e.g. `11/07/24` -> `2024-11-07`, `01/23/25` -> `2025-01-23`) from **its own page header**.
   - Read the `Qty.` column carefully: set `"qty"` to the integer in `Qty.`, and set `"Cost"` to the **per-unit** price (`Amount / qty` when `Amount` is the extended line total for `qty > 1`).
2. Fix the metadata clobber bug at `main.py:7956-7962` so per-item values from `normalize_and_validate_receipt` take precedence over `hdr` (page 1):
```python
                        coin_doc["Retailer/Website"] = coin_doc.get("Retailer/Website") or coin_doc.get("retailer") or retailer_val or ""
                        coin_doc["retailer"] = coin_doc["Retailer/Website"]
                        coin_doc["Retailer Invoice #"] = coin_doc.get("Retailer Invoice #") or coin_doc.get("invoice_number") or invoice_num_val or ""
                        coin_doc["invoice_number"] = coin_doc["Retailer Invoice #"]
                        coin_doc["Purchase Date"] = coin_doc.get("Purchase Date") or coin_doc.get("purchase_date") or invoice_date_val or ""
                        coin_doc["purchase_date"] = coin_doc["Purchase Date"]
```

---

### File 2: `numista_mobile/web/add_coins.html`

#### Change 2A — Poll to completion during active / linking stage (`add_coins.html:1029-1088`)
In `startPolling()`:
1. Raise `MAX_POLL_MS` from `60000` to `180000` (180s) and add a `lastProgressTime` tracker that resets whenever `data.processed_files` advances or `data.status === 'linking'` or any `per_file` item transitions to `'done'`.
2. Do **not** trigger timeout while `data.status === 'linking'` (when files are already `"Done — 17 coins"` and the backend is finishing duplicate sweep + receipt linking) unless 90s have elapsed inside `'linking'` with no completion.

---

## Required Verification & Test Proof (`Rule 8` + `NET-459`)

1. **New 2-Page Invoice Regression Test in `numista_backend/tests/test_v8_18_15e_regression.py`:**
   - Add `test_invoice_092052_multipage_per_page_metadata_qty_and_linking()`:
     - Feed a 2-page fixture matching `092052` (Page 1: `invoice_number="67000011"`, `invoice_date="2024-11-07"`, 9 line items where 3 items have `qty=2` -> 12 coins; Page 2: `invoice_number="67226944"`, `invoice_date="2025-01-23"`, 1 supply folder `is_supply=True` + 5 coin/set items including yearless `"21st Century Penny and Nickel Transition Set"` -> 5 coins) in **both** formats Gemini returns (a 2-element list of page dicts AND a single dict with per-line `invoice_number`/`invoice_date`).
     - Assert:
       1. Exactly **17** coin docs are written to `review_queue` (12 from page 1 + 5 from page 2; supply folder skipped).
       2. The 12 page-1 docs have `Retailer Invoice # == "67000011"` and `Purchase Date == "2024-11-07"`.
       3. The 5 page-2 docs have `Retailer Invoice # == "67226944"` and `Purchase Date == "2025-01-23"` (NOT `67000011` / `2024-11-07`).
       4. Each `qty=2` item expands to 2 docs in `review_queue`.
       5. `_link_receipts_to_coins` links all **17** coins (`linked == 17`, `unlinked == 0`, `unlinked_items == []`), and page-2 coins keep `Purchase Date == "2025-01-23"` after linking.
   - Prove the new test **FAILS** on `597e74a7` (old build) and **PASSES** on the new build.
2. **Full regression suite:** Run full `pytest` and `flutter analyze` with 0 regressions.
3. **File `BATONS\EXECUTE_DONE_P7_V8_18_15h.md`, `GEMINI38_REVIEW_P7_V8_18_15h_BUILD.md`, and `RADIO NET` review request** for Argon Reviewer pre-handoff check.

NEXT: Eric -> type "check radio" in AG CoS
