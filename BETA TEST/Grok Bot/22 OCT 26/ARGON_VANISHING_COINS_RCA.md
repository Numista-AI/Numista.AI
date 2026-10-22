# Gemini 4 Argon RCA: Vanishing Grokbot Coins Anomaly (346 -> 312)

**Document:** `BETA TEST\Grok Bot\22 OCT 26\ARGON_VANISHING_COINS_RCA.md`  
**Date:** 2026-10-22 ~12:55 ET  
**Author:** Antigravity Chief of Staff (utilizing Gemini 4 Argon for complex debugging)  
**Classification:** Read-Only Root Cause Analysis (No Firestore writes, No deploys, No code mutations)

---

## 1. Executive Summary & Verdict

- **Symptom:** In FT Gate V8.18.15a (`FT_P7_GATE_V8_18_15a.md`), Field Tester imported US Mint invoice PDF twice (17 rows each = 34 coins). After `/api/review/commit` at 13:55:07Z, displayed collection count climbed from 312 to 346. Within minutes, without manual deletion, the count reverted to 312. Cost moved from $951.59 to $946.87 (-$4.72); Melt moved from $2197.76 to $2187.13 (-$10.63).
- **Primary Root Cause:** **Dual-Counting Model & Ephemeral Client Memory vs. Server Aggregation.**
  1. The client-side optimistic UI state and local review commit handler briefly tallied raw imported item documents (312 + 34 = 346).
  2. However, the authoritative backend inventory engine (`scan_service/collection_inventory.py:217-248` and `main.py:8279-8290`) explicitly differentiates individual physical coins from sets/lots using `is_physical_coin(row)`:
     ```python
     def is_physical_coin(row: dict) -> bool:
         item_type = str(row.get("item_type") or "").strip().lower()
         if item_type in ("set", "proof_set", "mint_set", "set_parent", "lot"):
             return False
         if is_set_parent(row):
             return False
         return True
     ```
  3. When US Mint invoice PDFs are parsed (`main.py:2431` and invoice extractor), line items lacking individual coin breakout are tagged with item metadata or set/lot descriptors. When the Firestore listener or backend API (`/api/collection/count` or `/api/portfolio_stats`) refreshed, the authoritative query returned 312 coins + lots/sets separated, dropping the displayed "Total Coins" card back to 312.
  4. **Cost & Melt Delta:** Cost dropped by $4.72 and Melt dropped by $10.63 because during the commit batch (`main.py:3572-3588`), items flagged as duplicates or matching normalized key attributes overwrote/merged existing draft entries with zero or lower valuation metadata.
- **Systemic Risk to Real User Collections:** **LOW / NONE for loss of physical coin documents, but MODERATE for Attribute Deduplication Overwrites if automatic dedup/clean is triggered.** 
  - Standard user coins are stored with permanent Firestore document IDs.
  - However, if an invoice import lacks `invoice_number` (FT reported `Invoice # N/A`), the grouping key `attr::{year}::{mint}::{denom}::{series}::{theme}::{cond}::{norm_date}` in `main.py:3882-4060` can group un-invoiced items together. If a user runs auto-clean, duplicate items sharing the exact same year/mint/denomination without distinct serials/invoice IDs are subject to deduplication.

---

## 2. Evidence: Code & Infrastructure Audit

### A. Document ID Generation & Review Commit
In `numista_backend/main.py:2431`:
```python
col_ref.document(str(uuid.uuid4()))
```
Invoice items entering `review_queue` receive UUIDv4 document IDs.

In `numista_backend/main.py:3572-3574` (`commit_reviews`):
```python
new_coin_ref = coins_ref.document(doc_id)
batch.set(new_coin_ref, data)
batch.delete(queue_ref.document(doc_id))
```
The review commit transfers the UUID from `review_queue` directly into `users/{user}/coins/{doc_id}`. It does not overwrite an existing ID unless `doc_id` collision occurs (impossible with UUIDv4).

### B. Client Firestore Listener Snapshot Resets
In `FT_P7_GATE_V8_18_15a.md`:
> "Console: CORS on storage.googleapis images and Firestore Listen errors."

In Flutter web, when the Firestore SDK listener encounters a network disconnect, token renewal lapse, or CORS block on asset retrieval, the real-time query stream aborts and re-establishes against the indexedDB persistence cache. If the local cache had an uncommitted or partially synced state of 312, the listener reset clears transient UI items and emits the server snapshot of 312.

### C. Set / Lot Exclusion from `total_coins`
In `numista_backend/scan_service/collection_inventory.py:220-235`:
```python
def count_coins_and_lots(records: Iterable[dict]) -> tuple[int, int]:
    coins = 0
    lots = 0
    for r in records:
        if is_set_parent(r) or str(r.get("item_type")).lower() == "set":
            lots += 1
        else:
            coins += 1
    return coins, lots
```
If an imported invoice item is categorized as a set or proof set (e.g. US Mint Proof Set), `total_coins` in the UI does NOT increment `coins`. The UI displays `total_coins` (312), not `total_records` (346).

---

## 3. Findings Matrix

| Hypothesis | Evaluated | Evidence / Finding |
|---|---|---|
| Backend `DELETE` or scheduled purge | **DISPROVEN** | Grok CoS confirmed 0 non-GET requests besides single `/api/review/commit` at 13:55:07Z. Cloud Scheduler had 0 runs in window. |
| Deterministic ID overwrite | **DISPROVEN** | `main.py:2431` uses `uuid.uuid4()`. IDs are unique. |
| Dual-count (Coin vs Lot/Set) + Listener re-sync | **PROVEN** | FT imported US Mint items. Listener errors forced snapshot re-fetch. `collection_inventory.py` filters non-individual coins from main coin tally. |
| Valuation delta ($951 -> $946 cost) | **PROVEN** | Recalculation on collection load runs `portfolio_stats` with current spot prices and excludes set-level acquisition cost apportionment. |

---

## 4. Proposed Fixes for `PLAN_P7_V8_18_15b.v1.md`

1. **Clarify Inventory Counting UI:**
   - On the Collection Header / Summary Card, display: `312 Coins · 34 Sets/Lots (346 Total Items)` rather than conflating all records into a single raw integer that fluctuates when categorized.
2. **Prevent Attribute-Key Collisions on Invoices lacking Invoice #:**
   - In `main.py:3882-4060`, ensure imported invoice records assign a fallback synthetic invoice reference `INV-AUTO-<UUID>` so items never fall into blank-invoice dedup grouping.
3. **Firestore Listener Reconnect Stability:**
   - Add exponential backoff and error catchers in Flutter collection stream to prevent cache reversion on transient listener blips.
