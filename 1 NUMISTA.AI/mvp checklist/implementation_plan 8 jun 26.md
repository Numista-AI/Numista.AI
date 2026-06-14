# Implementation Plan: Universal Item Routing + Set Auto-Expand
**Date:** June 8, 2026  
**Priority:** High — implement before uploading to jseaman1204@gmail.com account  
**Scope:** Backend prompt + routing logic + Review Hub updates + new Supplies screen

---

## Decisions Confirmed

| # | Decision |
|---|----------|
| 1 | Add `item_type` routing **now** |
| 2 | Coin sets stored as **set records** — user chooses to "Break Up Set" or "Keep as Set" |
| 3 | Sets: show `$899 total / 8 coins` label. Individual coins linked via shared `set_id`. |
| 4 | Paper currency & medals → `review_queue` alongside coins (they ARE numismatic) |
| 5 | Supplies → `supplies_log` Firestore collection + new Supplies view in the app |
| 6 | Misclassified stamp (1937 Military Academy West Point) stays in test account as test case |
| 7 | Re-processing `102135.pdf` / `102331.pdf` deferred — test account only |

---

## What Changes (Overview)

```
BEFORE:
  PDF → AI → "Is it coin/bullion/currency?" → review_queue
                                              → DROPPED (stamps, sets, supplies, currency, medals)

AFTER:
  PDF → AI → classify ALL items by type ─┬→ coin            → review_queue (unchanged)
                                          ├→ set             → review_queue as SET RECORD
                                          │                     (user clicks "Break Up" OR "Keep as Set")
                                          ├→ paper_currency  → review_queue with 📜 badge
                                          ├→ medal           → review_queue with 🎖️ badge
                                          ├→ stamp           → pending_items (future Stamps module)
                                          ├→ supply          → supplies_log + new Supplies view
                                          └→ other           → pending_items
```

### Set Lifecycle (New)
```
Ingest → Set record in review_queue
           ├─ "Break Up Set" → N individual coin records (each with set_id + set_name + cost label)
           │                    Set record deleted
           └─ "Keep as Set"  → Committed as a single set item to main collection
                                (with set_contents array for future reference)
```

---

## Proposed Changes

---

### Backend — Extraction Prompt

#### [MODIFY] [main.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py) — `extraction_prompt` (lines 1425–1477)

**Change 1 — Opening instruction:** Expand scope from "numismatic items" to "ALL line items":

```
BEFORE: "Extract line items representing actual numismatic purchases (Coins, Bullion, Currency)."
AFTER:  "Extract ALL line items on this invoice and classify each by type."
```

**Change 2 — Add `item_type` field to the schema:**

```json
"item_type": "coin | stamp | paper_currency | medal | set | supply | other"
```

**Change 3 — Add `set_contents` field (only populated when item_type = "set"):**

```json
"set_contents": [
  { "Year": "1971", "Mint Mark": "D", "Denomination": "Eisenhower Dollar", "Strike Type": "Uncirculated" },
  { "Year": "1972", "Mint Mark": "D", "Denomination": "Eisenhower Dollar", "Strike Type": "Uncirculated" },
  ...
]
```

**Change 4 — Add classification rules to the prompt:**

```
ITEM TYPE CLASSIFICATION:
- "coin"           → individual coin, bullion coin, or token
- "set"            → a named group of coins sold together (e.g. "1971-1978 Ike Set", "Lincoln Cent Collection")
                     MUST also populate "set_contents" listing each individual coin
- "stamp"          → postage stamp or stamp block (look for Scott #, face values like 10¢/25¢/32¢ used as postage)
- "paper_currency" → banknote, Silver Certificate, Federal Reserve Note, Obsolete Note, Fractional Currency
- "medal"          → commemorative medal, token, or non-monetary medallion
- "supply"         → binder, coin page, holder, slab, capsule, album, magnifier, shipping supply
- "other"          → anything not covered above

STAMP DISAMBIGUATION:
  If a line item description contains words like "stamp", "block of [N]", a Scott catalog number (e.g. "#1234"),
  or a subject that is clearly historical art (e.g. "Iwo Jima", "Lexington & Concord") with a small face
  value (≤$1.00) — classify as "stamp", NOT "coin". 
  CRITICAL: "1937 5c Military Academy West Point" is a STAMP, not a Buffalo Nickel.
```

**Change 5 — Add new retailer fingerprints:**

```
- "PCS Coins" OR "PCS Stamps" OR "PCS Coins and Stamps" OR "pcscoins.com" → "PCS Stamps & Coins"
- "JP Capital Collectibles" OR "JP CAPITAL COLLECTIBLES" → "JP Capital Collectibles LLC"
- "Danbury Mint" OR "danburymint.com" → "The Danbury Mint"
```

---

### Backend — Routing Logic

#### [MODIFY] [main.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py) — item processing loop (lines 1491–1514)

**Current code** saves every item directly to `review_queue`.

**New logic:**

```python
for item in items:
    item_type = str(item.get('item_type', 'coin')).lower().strip()
    item['source'] = 'PDF Invoice'
    item['source_file'] = file.filename
    item['created_at'] = firestore.SERVER_TIMESTAMP
    # (year+mint split logic stays unchanged)

    if item_type == 'set':
        # ── STORE AS SET RECORD — user decides to Break Up or Keep as Set ──
        set_id       = str(uuid.uuid4())          # shared ID links future broken-up coins
        set_contents = item.get('set_contents', [])
        set_cost_str = item.get('Purchase Cost', '$0.00')
        n_coins      = max(len(set_contents), 1)

        item['set_id']         = set_id
        item['set_size']       = n_coins
        item['set_cost_label'] = f'{set_cost_str} total / {n_coins} coins'  # shown to user
        item['set_broken_up']  = False            # flipped to True when user breaks it up
        _apply_defaults(item)
        doc_ref = col_ref.document(set_id)        # use set_id as the doc ID
        batch.set(doc_ref, item)
        added_count += 1
        set_expanded += n_coins                   # informational: how many coins are inside

    elif item_type in ('coin', 'paper_currency', 'medal', 'other', ''):
        # ── Coins and coin-adjacent items → review_queue (existing behavior) ──
        _apply_defaults(item)
        doc_ref = col_ref.document(str(uuid.uuid4()))
        batch.set(doc_ref, item)
        added_count += 1

    elif item_type == 'stamp':
        # ── Stamps → pending_items (future Stamps module) ──
        _apply_defaults(item)
        pending_ref = db.collection('users').document(user_email).collection('pending_items')
        pending_ref.document(str(uuid.uuid4())).set(item)
        pending_count += 1

    elif item_type == 'supply':
        # ── Supplies → supplies_log (expense tracking) ──
        supply_ref = db.collection('users').document(user_email).collection('supplies_log')
        supply_ref.document(str(uuid.uuid4())).set(item)
        supplies_count += 1
```

> [!NOTE]
> `paper_currency` and `medal` go to `review_queue` for now — they are numismatic items. Only stamps and supplies are routed to separate collections.

**New helper functions to add (above the endpoint):**

```python
def _parse_cost(cost_str: str) -> float:
    """'$10.00' → 10.0. Returns 0.0 on any parse failure."""
    try:
        return float(str(cost_str).replace('$', '').replace(',', '').strip())
    except:
        return 0.0

def _apply_defaults(item: dict):
    """Apply schema defaults in place (extracted from the existing loop)."""
    item['deep_dive_status'] = 'PENDING'
    if not item.get('Program/Series'):
        item['Program/Series'] = (item.get('Country') or 'USA') + ' Invoice Import'
    if 'Condition' not in item: item['Condition'] = 'Ungraded'
    if 'Cost' not in item: item['Cost'] = '$0.00'
    # Year+Mint split
    import re as _re
    raw_year = str(item.get('Year', '')).strip()
    raw_mint = str(item.get('Mint Mark', '')).strip()
    if raw_year and not raw_mint:
        _ym = _re.match(r'^(\d{4}(?:-\d{4})?)\s*([A-WY-Z])$', raw_year, _re.IGNORECASE)
        if _ym:
            item['Year'] = _ym.group(1)
            item['Mint Mark'] = _ym.group(2).upper()
```

**Updated return value:**

```python
return {
    "status": "success",
    "extracted_items": added_count,        # coins + paper_currency + medals + set records
    "set_records": set_count,              # NEW: how many sets (each is 1 record)
    "set_coins_inside": set_expanded,      # NEW: total coins inside all sets combined
    "pending_items": pending_count,        # NEW: stamps, other non-coin
    "supplies_logged": supplies_count,     # NEW: supply items
    "data": response_items
}
```

---

### Frontend — Review Hub Card Updates

#### [MODIFY] [review_hub_screen.dart](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/review_hub_screen.dart)

**Change 1 — Add `item_type` badge** next to the Confidence badge:

| item_type | Badge color | Label |
|-----------|-------------|-------|
| `coin` | None (default) | — |
| `paper_currency` | Teal | 📜 Currency |
| `medal` | Purple | 🎖️ Medal |
| `stamp` | Orange | 📬 Stamp |
| `set` | Blue | 🗂️ Set |
| `other` | Grey | ❓ Other |

**Change 2 — Special Set Card** when `item_type == 'set'`:

```
╔══════════════════════════════════════════════════╗
║  🗂️ SET  1971-1978 Ike Dollar Set in Album       ║
║  $899.00 total / 8 coins  •  Littleton           ║
║  ─────────────────────────────────────────────   ║
║  Contains: 1971-D, 1972-D, 1973-D ... Ike $      ║
║                                                  ║
║  [Keep as Set]        [Break Up Set →]           ║
╚══════════════════════════════════════════════════╝
```

- **"Keep as Set"** → commits the set as a single collection item  
- **"Break Up Set"** → calls new backend endpoint `POST /api/review/break_up_set`  
  which creates N individual coin records (each with `set_id`, `set_name`, `set_cost_label`)  
  and deletes the original set record

**Change 3 — "From Set" chip** on broken-up coins:
```
╔════════════════════════════════════════╗
║  1971 Eisenhower Dollar           ...  ║
║  🗂️ From Set: 1971-1978 Ike Set        ║  ← amber chip
║  Cost: $899 total / 8 coins            ║
╚════════════════════════════════════════╝
```

---

### Frontend — New Supplies View [NEW]

#### [NEW] `supplies_screen.dart`

A simple read-only list screen showing all items logged to `supplies_log`:
- Accessible from the **Inventory** section (currently greyed out in sidebar — this activates it)
- Columns: Description, Cost, Date, Retailer, Invoice #, Source File
- Total cost summary at the top
- No approve/commit flow needed — it's a reference/expense log

#### [MODIFY] `base_layout.dart` — unlock "Inventory" nav item, point to Supplies screen

### Backend — New Endpoint [NEW]

#### `POST /api/review/break_up_set`

```python
# Request body: { user_email, set_doc_id }
# 1. Read the set document from review_queue
# 2. For each coin in set_contents:
#      create individual coin record with set_id, set_name, set_cost_label, from_set=True
# 3. Delete the original set document
# 4. Return { "created": N, "set_id": set_doc_id }
```

### Firestore — New Collections

Three new sub-collections created automatically on first write. No Firestore console changes required.

| Collection | Purpose | Accessible from UI |
|------------|---------|-------------------|
| `users/{email}/pending_items` | Stamps, future collectibles | Not yet (future module) |
| `users/{email}/supplies_log` | Invoice supply items | ✅ New Supplies screen (Inventory) |

> [!IMPORTANT]
> **Firestore Security Rules** — the three new collections need read/write rules added, same pattern as `review_queue`. Cloud Run writes; mobile app reads supplies_log for the new Supplies screen.

---

## All Questions Resolved ✅

| Question | Answer |
|----------|--------|
| Set cost display | `$899 total / 8 coins` label — user decides to split or keep |
| Paper currency + medals routing | `review_queue` with type badge — they ARE numismatic |
| Supply tracking | Log to Firestore + build Supplies screen under Inventory |

---

## Verification Plan

### After Implementation

1. **Re-run the 4 problem files through the updated backend** (not the test account — just a local test against the API)
2. **Check `102331.pdf`** — the "1937 Military Academy West Point" should now be classified as `stamp` → `pending_items`, NOT extracted as a Buffalo Nickel
3. **Check `092205.pdf`** — the 2 coin sets should now auto-expand; verify coin count in review_queue is ≥28 individual coins
4. **Verify existing coins unaffected** — run 2–3 previously-clean invoices and confirm zero regression
5. **Confirm Firestore** — check that `pending_items` and `supplies_log` sub-collections are being created under the test account

### Before Uploading to jseaman1204@gmail.com
- ✅ All 47 files re-processed with updated prompt
- ✅ Zero stamps misclassified as coins
- ✅ Coin sets properly expanded
- ✅ "From Set" badge visible in Review Hub

---

## What This Does NOT Change

- The Review Hub UI and commit workflow — unchanged
- How coins are approved and moved to the main collection — unchanged  
- The `source_file` traceability we added last night — stays
- The confidence score display — stays
- Any previously committed coins in the collection — not touched
