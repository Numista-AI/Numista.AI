# NET-559 Artifact #3 — Firestore dump summary

**When:** 26 Oct 2026 ~16:50 ET (America/New_York)  
**Project:** `studio-9101802118-8c9a8`  
**Account:** `grokbot@numista.ai` only (uid `eIGZgYb49eeCR4Bsa5ABtHr94L63`)  
**Invoice / item:** USM24086141 / 26SQRP  
**Committed:** N (still pending in Review Hub)  
**Session:** `sess_1793047548494_7uoqtd`  
**Dump file:** `/workspace/p7gate/net559/ARTIFACT3_firestore_dump.json`  
**Read-only:** Y (no deletes/updates)

## Doc paths

| Role | Path |
|---|---|
| **Child (pending Hub coin)** | `users/grokbot@numista.ai/review_queue/7a32932ebc4e94a586534e7180cd1c4372c4f17d` |
| **Parent (receipt / paper trail)** | `users/grokbot@numista.ai/receipts/rec_Receipt_Semiquincentennial_President_D_Coin_Roll` |

No separate `is_set_parent` / package parent doc exists under `review_queue`. Parent for Artifact 3 is the receipt doc (linked via `receipt_id` / `linked_coin_ids`).

## Core figures (child)

- invoice #: **USM24086141**
- item #: **26SQRP**
- qty: **25**
- cost / Purchase Cost: **61.0**
- unit_cost: **2.44**
- status: **pending**
- retailer: United States Mint
- source_file: Receipt_Semiquincentennial_President_D_Coin_Roll.pdf

## Required six fields

| Field | Child (`review_queue/...7a32932e…`) | Parent receipt (top-level) | Parent receipt `line_items[0]` |
|---|---|---|---|
| `from_set` | **present** = `true` | **MISSING** | **present** = `true` |
| `set_name` (full) | **present** = `2026 Semiquincentennial Presidential $1 Coin 25-Coin Roll` | **MISSING** | **present** (same) |
| `set_cost_label` | **present** = `$61.00 (25 @ $2.44)` | **MISSING** | **present** (same) |
| `allocated_fees` | **present** = `0.0` | **MISSING** | **present** = `0.0` |
| `shipping_fee` | **present** = `0.0` | **present** = `9.95` | **present** = `0.0` |
| `shipping_amount` | **MISSING** | **present** = `9.95` | **MISSING** |

### Plain-English takeaway
- Child has 5/6 required fields; only **`shipping_amount` missing** on the coin doc (fee shown as allocated `shipping_fee=0` / `allocated_fees=0`).
- Receipt parent holds invoice-level **`shipping_amount=9.95`** and **`shipping_fee=9.95`**, but does **not** carry `from_set` / `set_name` / `set_cost_label` / `allocated_fees` at top level (those live on `line_items[0]`, mirroring the child).
- Fee economics on the pending Hub coin are `$0` allocated (lot stayed $61), matching UI Fee $0.00; raw Mint shipping $9.95 remains on the receipt parent only.

## Illegal `/` in keys

Child and receipt line_item still contain slash keys:
- `Theme/Subject`
- `Program/Series`

No `Retailer/Website` key on the **pending** child (uses `retailer_website` snake_case). Aborted leftovers from earlier runs may still carry `Retailer/Website`.

## Other USM24086141 leftovers (not the canary)

Four **aborted** `review_queue` docs remain (prior NET fails); dump JSON lists them. Only the pending child above is the NET-559 canary.

## Blockers

None for read. ADC at `/home/box/.config/gcloud/application_default_credentials.json` worked against project `studio-9101802118-8c9a8`.
