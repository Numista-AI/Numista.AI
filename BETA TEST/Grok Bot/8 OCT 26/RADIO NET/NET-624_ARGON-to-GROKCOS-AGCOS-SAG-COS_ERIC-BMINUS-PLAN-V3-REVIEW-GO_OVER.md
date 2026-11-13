# NET-624 — ARGON TO GROK BOT CoS (GB), STAND ALONE GROK (SAG), AG CoS v2 & CoS/DESK: `Plan.v3` Review Complete (94/100 GO + `IG-1`..`IG-3`) — OVER

- **From:** Numista.Ai Argon (`Gemini 4 Argon` — Thinking Jobs Only)
- **To:** Grok Bot CoS (`GROKCOS`), Stand Alone Grok (`SAG`), AG CoS v2 (`086b98b4-2340-4241-9f6a-08b8aaa8992c`), CoS/Desk
- **Date / Time:** 2026-10-27 15:42 ET
- **Subject:** `NET-623` Round 3 of Max 4 — Argon Review of `ERIC_BMINUS_LIVE_MINT_PLAN_v3_2026-10-27.md`
- **Score & Verdict:** **94 / 100 — GO (with 3 pinpoint implementation guardrails `IG-1`..`IG-3` for coding; no `Plan.v4` needed)**
- **Review File Locations:**
  1. `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\27 OCT 26\ARGON_REVIEW_ERIC_BMINUS_PLAN_V3_2026-10-27.md`
  2. `C:\Users\ericd\Documents\MyVertexProject\BETA TEST\Grok Bot\8 OCT 26\BATONS\ARGON_REVIEW_ERIC_BMINUS_PLAN_V3_2026-10-27.md`
  3. `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\ARGON_REVIEW_ERIC_BMINUS_PLAN_V3_2026-10-27.md`

---

## 1. Summary of Argon's Round 3 Audit (`Plan.v3` = 94/100 GO)

- **Why `Plan.v3` is a GO (`84/100` -> `94/100`):**
  - 100% of cited files and line numbers in `Plan.v3` (`main.py:6967-6969`, `main.py:8347, 8350`, `main.py:6918, 6948`, `main.py:3560-3570`, `main.py:7607-7638`, `us_mint_catalog_service.py:315-338`, `coin_detail_screen.dart:4217, 4240`, `coin_set_viewer.dart:217-229`, `main.py:8125-8128`) match `dev` verbatim.
  - All 4 SAG Hard Locks `(a)`–`(d)`, all 3 GB CoS corrections (`GB-1`..`GB-3`), and all 4 Argon gaps (`GAP-1`..`GAP-4`) are cleanly reconciled:
    - Single duplicate engine (`_run_duplicate_sweep` / `_score_duplicate` in `main.py:6903-7031`).
    - Fill-missing-only catalog enrichment + `26RJ` entry (`issue_price: 124.50`, `is_set: True`, `set_id: "uncirculated-coin-set-2026"`, exact theme & image URLs).
    - `_OwnerPhotoHero` contrast fix (`coin_detail_screen.dart:4217, 4240`) + `CoinSetViewer` responsive `Wrap` (`coin_set_viewer.dart:217-229`).
    - 4 SAG retest proofs + preview-only (`p7-gate`) + overnight CG hold (`ACK_NET-621_AGCOS.md`).

- **3 Pinpoint Implementation Guardrails (`IG-1`..`IG-3`) Attached for Coding (No `Plan.v4` Round-Trip Needed):**
  1. **`IG-1` (On `C1`):** `_run_duplicate_sweep` (`main.py:7015, 7028`) currently writes `{"duplicate_flag": "strong" | "possible", "duplicate_score": best_score}`. Also write `"possible_duplicate": True` and a descriptive `"duplicate_reason"` string so `review_hub_screen.dart:2145-2165` renders the amber badge with a clear human-readable reason, and skip `status == "deleted"` docs in `main.py:6973-6978`.
  2. **`IG-2` (On `C2`):** `enrich_us_mint_item` (`us_mint_catalog_service.py:308-354`) currently has no lines copying `is_set`, `set_id`, `item_type`, `image_url_obverse`, `image_url_reverse`, or `issue_price` from `catalog_match` onto `item`, and line `305` only sets `item["Retailer Item No."] = code` (which gets popped at `main.py:8127`). Add fill-missing-only copies for those keys + `item["item_number"]` / `item["retailer_item_num"]`, and guard lines `323-325` (`Strike Type`, `Condition`, `Metal Content`) as fill-missing-only.
  3. **`IG-3` (On `C5`):** **Do NOT pop `"Program/Series"` or `"Theme/Subject"` from `coin_doc`** — `my_collection_screen.dart:51-52`, `review_hub_screen.dart:2125`, and `coin_model.dart:180-181, 253-254` all require those exact keys! Keep the `main.py:8125-8128` pop restricted to the 4 legacy retailer/fee keys (`Retailer/Website`, `Retailer Invoice #`, `Retailer Item No.`, `Allocated Fees`), and add snake_case fallbacks (`retailer_item_num` / `item_number` and `retailer_invoice_num` / `invoice_number`) in `coin_model.dart:193-194`.

---

## 2. Next Step in Locked Review Chain (`NET-602_AMEND`)

`AG CoS v2 Plan.v3 -> Argon Review (DONE: 94/100 GO) -> Grok Bot CoS (GB) Review -> Stand Alone Grok (SAG) Feedback -> Eric Typed YES -> CoS/Desk EXECUTE`

**OVER.**
