# MERGED / SUPERSEDED by NET-556 CoS formal fold order
**When:** 26 Oct 2026 ~4:20 PM ET  
**Why:** Same 3 mandatory 4.1.x items. CoS LIVE NOW filed NET-556 + WAKE_AGCOS_NET556. Do not treat this as a second fold task.

--- ORIGINAL ---
# WAKE AG CoS â€” NET-554 (Fold Argon's 3 Surgical 4.1.x Items into Plan 4.1 Build)

**Time:** 2026-10-26 16:16 EDT  
**Ref:** `NET-552` (*"If Argon still files a review against Plan 4.0, fold any non-conflicting items into a 4.1.x patch"*), `NET-554`

Read `C:\Users\ericd\Documents\MyVertexProject\BETA TEST\Grok Bot\8 OCT 26\RADIO NET\NET-554_ARGON-to-GROKCOS-AGCOS_PLAN-V4-V41-STRUCTURED-REVIEW-41X-PATCH_OVER.md` and fold the 3 surgical 4.1.x items into your Plan 4.1 build:
1. **Edit Coin Dialog (`review_hub_screen.dart:825-830, 982-990`):** Render BOTH `Package/Roll: ${data['set_cost_label']}` (`$61.00 (25 @ $2.44)`) AND `Fee: \$${feeNum.toStringAsFixed(2)}` (`Fee: $0.00`) in `_showCoinEditDialog` (Plan 4.1 Â§4 Gate #4 & Â§6 Artifact #2 require both).
2. **Stop Illegal-Key Writes & Re-Injection (`main.py:7071-7146, 7602-7639, 8088-8095` + `review_hub_screen.dart:724-730`):** Remove `"Retailer/Website"`, `"Retailer Invoice #"`, `"Retailer Item No."`, and `"Allocated Fees"` from `normalize_and_validate_receipt`, `_execute_import_process_worker`, and `_link_receipts_to_coins` (`main.py:7127-7146`, which otherwise re-injects `"Retailer/Website"` and `"Retailer Invoice #"` via `.set(..., merge=True)`), and update `review_hub_screen.dart:724-730` text controllers to read `snake_case` keys first.
3. **Enforce `status == "pending"` Invariant (`review_hub_screen.dart:1271, 1320, 1396` & `main.py:7612, 8056`):** Tighten Hub actionable filter to `status == 'pending'`, set `doc["status"] = "pending"` in `main.py:7612`, and supersede prior docs with `status in ("pending", "pending_review", "staged")`.

