# ARGON VERIFY — NET-565 PREVIEW 3-CHECK (Eric 23RH Save / Fee / Hub Date)
**Date:** 26 Oct 2026 ~7:25 PM ET  
**Reviewer:** Argon (Grok Bot, non-author, read-only)  
**SHA checked:** `4eb93476447de343527aa78e73b177d3e05e0c34` (chore: auto-backup 2026-10-26 19:00 ET on origin/dev)  
**Parent of fix delta:** `ae41d948`  
**Files changed vs parent:** `numista_mobile/lib/screens/review_hub_screen.dart` (+49/−11), `numista_backend/main.py` (+5/−2)  
**Preview (baton):** https://numista-vault--p7-gate-8avtpz22.web.app · Hosting a628e317ea5b632a · Run 00494-rew tag p7gate · **0% live · main OFF**  
**Evidence context (not re-opened UI):** MY TESTING\26 OCT 2026\My Beta Test (SS 1–3 Fee $0, Save toast); invoice USM25343756 / 23RH. Prior dump: child `allocated_fees=0` / `shipping_fee=0`; `shipping_amount` missing on child; receipt top had `shipping_amount=9.95`.  
**Radio:** NET-574 (NET-566 was AG collision / superseded; CoS score NET-572; AG PREVIEW note NET-573).

## Overall VERDICT: **CONDITIONAL PASS**
| # | Item | Score |
|---|---|---|
| 1 | Save path | **PASS** |
| 2 | Fee / Mint S&H $9.95 | **PARTIAL** |
| 3 | Hub Date | **PASS** |

Independent of CoS NET-572 CONDITIONAL PASS. Soft plan OK. Do not score Package/Roll, Theme/Subject slash, Upload declutter, PDF→Morgan, catalog.

---

## 1) Save path — **PASS**

### What was throwing
Edit Coin **Save** and **Save & Commit** built a Firestore `update(Map)` by dumping controller keys as-is (`controllers.forEach((key, ctrl) { updates[key] = ctrl.text.trim(); })` on parent). One controller key is **`Retailer Item No.`** (trailing period). Firestore treats `.` in a map key as a **field-path separator**, so the update fails with `invalid-argument`. `NumistaErrorHelper._fromFirebase` default (`numista_error_helper.dart:51`, `:89-90`) returns **`An unexpected error occurred. Please try again.`** — exact Eric toast. Hypothesized by AG; not reproduced here against Eric data; code path is consistent with the symptom.

### Fix in 4eb93476
New helper maps dotted / display keys to snake_case before `update`:

```
review_hub_screen.dart:707-738  _buildReviewQueueUpdates
  'Purchase Date'        -> purchase_date
  'Retailer/Website'     -> retailer_website
  'Retailer Invoice #'   -> retailer_invoice_num
  'Retailer Item No.'    -> retailer_item_num   // <-- the period key
  'Storage Location'     -> storage_location
  'Fee'                  -> allocated_fees + shipping_fee (numeric)
```

Both handlers call it:
- **Save** `:1082` then `.update(updates)` at `:1103-1108`
- **Save & Commit** `:1141` → Firestore update `:1163-1168` → `HttpAuthClient.post(.../api/review/commit)` `:1171-1177`

Success toasts: `'Changes saved to Review Queue.'` (`:1112`); commit snackbar from response (`:1182-1187`). Catch still uses `toUserFriendly` (`:1117`, `:1197`) but the invalid dotted key is no longer written.

### Diff vs parent
Parent Save/Save&Commit used raw `controllers.forEach` → `updates[key]`. Replaced by `_buildReviewQueueUpdates` in both places. Matches PREVIEW_READY claim #1.

### Soft (not FAIL)
- Theme/Subject / Program/Series still pass through the else-branch with `/` (OUT OF SCOPE).
- No automated test. FT must canary Save + Save & Commit on 23RH.

---

## 2) Fee / Mint S&H $9.95 — **PARTIAL**

### Edit display + editability — PASS (code)
- Banner: `:868-874` always shows `Fee: $X.XX` when `feeNum >= 0.0` (always true for numeric path).
- Fee source for Edit: `:765-768`  
  `allocated_fees ?? Allocated Fees ?? shipping_fee ?? Fee ?? fee`
- New TextField: `:1045` `field('Fee', 'Fee / Shipping & Handling', ...)` with `TextInputType.numberWithOptions(decimal: true)`.
- `field()` (`:780-819`) is a normal `TextField` — **no `readOnly`**, not disabled. Editable.

### Hub card Fee — PASS (wiring)
- `:2046-2062` same key chain → `_buildMetaItem('Fee', feeStr, ...)`. After Edit save of 9.95 into `allocated_fees`/`shipping_fee`, Hub will show `$9.95`.

### Edit save of Fee — PASS (code)
- `_buildReviewQueueUpdates` Fee branch (`:723-728`) parses currency and writes both `allocated_fees` and `shipping_fee`. Setting $9.95 on an **existing** 23RH-class review_queue doc should persist and display.

### Import path shipping → allocated_fees — PARTIAL
**Parent (broken for Mint):**  
`doc["allocated_fees"] = 0.0 if (is_us_mint_order or doc.get("pack_expanded")) else allocated_fee`  
→ every US Mint child (including 23RH) got **$0**.

**4eb93476 (`main.py:7652-7654`):**  
`doc["allocated_fees"] = 0.0 if doc.get("pack_expanded") else allocated_fee`  
(same for `shipping_fee`)  
→ only pack/roll expansions waive fee; regular Mint items (23RH) carry allocated S&H. Matches PREVIEW_READY claim #2.

**Residuals (why PARTIAL, not PASS):**
1. **Existing 23RH docs** still have `allocated_fees=0` / `shipping_fee=0` until user sets Fee in Edit **or** re-imports. Baton says this; code agrees. Preview will not magically show $9.95 on old queue rows without that step.
2. **`main.py:7526-7527`** still zeroes `allocated_fee` for **every** line if the order contains any 26SQRP / "26sqrp" note — including a sibling 23RH. Baton called this out; unchanged in this commit.
3. **`shipping_amount` → allocated_fees gap:** allocation uses `data.get("shipping_fee")` (`:7493`) and/or `grand_total - subtotal` (`:7502-7505`). Receipt write sets both `shipping_fee` and `shipping_amount` from `shipping_val` (`:8149-8150`), but normalize does **not** fall back to `shipping_amount` if only that key is present on the AI parse. Prior dump having receipt `shipping_amount=9.95` with child fees at 0 is explained primarily by the old `is_us_mint_order` blanket zero; re-import of a clean 23RH-only invoice should allocate if `shipping_fee` or grand_total>subtotal is present. **Re-import → $9.95 not tested** (baton). Soft plan OK.

### Score rationale
Editable Fee + Hub/banner wiring + Save of 9.95 on existing item: **code PASS**. Import fix for non-`pack_expanded` Mint: **present**. Product "Fee must appear as $9.95" on Eric's current 23RH without Edit/re-import: **not guaranteed**. Combined → **PARTIAL**.

---

## 3) Hub Date — **PASS**

### Bug
Import writes `purchase_date` (`main.py:8123`). Edit controller already preferred it (`:757` `purchase_date ?? Purchase Date`). Hub on parent only read **`Purchase Date`** → **N/A** when only snake_case was set (Eric SS 1).

### Fix
`review_hub_screen.dart:2065`:  
`_buildMetaItem('Date', (data['purchase_date'] ?? data['Purchase Date'] ?? 'N/A').toString(), ...)`

Save also maps `'Purchase Date' → purchase_date` (`:714`), so future Edit saves stay consistent.

Matches PREVIEW_READY claim #3. Diff vs parent is exactly this fallback.

---

## Non-author sanity (PREVIEW_READY vs code)
| Baton claim | Present at 4eb93476? |
|---|---|
| `_buildReviewQueueUpdates` snake_case for retailer/invoice/item/date/storage | **Yes** `:707-738` |
| Fee field → allocated_fees + shipping_fee | **Yes** `:723-728`, `:768`, `:1045` |
| Backend: only pack_expanded zeroes fee | **Yes** `:7652-7654` |
| Hub Date reads purchase_date first | **Yes** `:2065` |
| Not reproduced vs Eric data | Honest |
| Existing child still $0; re-import untested | Honest |
| `:7526` 26SQRP fee-zero unchanged | Honest (`:7526` still present) |

Claims match. Caveats match. Not oversold.

---

## Hygiene
- `git fetch`; temp worktree `%TEMP%\cr_wt_n565` at 4eb93476; removed after.
- No git writes, deploys, live POSTs, `--execute`/`--apply`, Eric/AJ collection touches, secrets, or setting changes.
- Live/main **OFF** (baton; not promoted by this review).

## Deliverables
- Radio: `BETA TEST\Grok Bot\8 OCT 26\RADIO NET\NET-574_ARGON-to-GROKCOS-AGCOS-FT_NET565-PREVIEW-3CHECK-VERDICT_OVER.md`
- This review: `1 NUMISTA.AI\BETA TEST\Grok Bot\26 OCT 26\ARGON_VERIFY_NET565_23RH_4eb93476.md` (+ mirror under `BETA TEST\Grok Bot\26 OCT 26\`)