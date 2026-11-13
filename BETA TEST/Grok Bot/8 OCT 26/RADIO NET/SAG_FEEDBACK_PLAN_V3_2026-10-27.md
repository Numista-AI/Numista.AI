# SAG Feedback — Eric B− Live Mint Plan.v3 (Round 3 of max 4)

- **Reviewer:** Stand Alone Grok (SAG)
- **DTG:** 2026-10-27 ~3:52 PM ET (America/New_York)
- **Inputs:** Plan.v3 + Argon 94 GO (IG-1..3) + GB CoS 93 READY FOR SAG
- **Chain:** AG Plan.v3 → Argon 94 → GB 93 → **SAG (this)** → Eric typed YES → EXECUTE

---

## BLUF

**92 / 100 — GO**

No Plan.v4. Plan.v3 + Argon IG-1..IG-3 as **mandatory coding guardrails** is ready. Ship after Eric typed YES.

---

## Score and verdict

Plan correctly folds prior locks (single sweep, fill-missing-only, 26RJ catalog add, contrast, 20-coin wrap, four proofs, preview-only + Eric YES). Residual first-try risks are exactly the three wiring gaps Argon flagged. Locking those IGs into the EXECUTE/coding brief closes them without another plan round.

Deductions only for residual process risk (history of “verified in code” without live proofs) and IGs not yet in the coding brief — not plan defects.

---

## IG-1..IG-3 — mandatory coding folds (confirm, no amendments)

1. **IG-1:** Dual-write `possible_duplicate=True` + `duplicate_reason` alongside existing `duplicate_flag`/`duplicate_score`. Skip `status=="deleted"` candidates. Without this the Hub amber badge stays dark even when the counter works.
2. **IG-2:** `enrich_us_mint_item` fill-missing-only copy `is_set`/`set_id`/`item_type`/`image_url_*`/`issue_price` and populate `item_number`/`retailer_item_num` when blank. Guard Strike/Condition/Metal the same way. Treat LLM “Uncirculated Coin Set” as placeholder/alias. Without this the 26RJ enrichment proof fails.
3. **IG-3:** Do **not** pop `Program/Series` or `Theme/Subject`. Pop only the four legacy retailer/fee keys after snake_case copies. Add CoinModel snake_case fallbacks for SKU/invoice. Popping series/theme keys would blank them app-wide.

These three are not polish. They go in the EXECUTE packet / AG coding brief **before any code is written**.

---

## Four retest proofs + FT-before-founder loop (unchanged, still required)

- Second-invoice 26RJ → Duplicates Flagged ≥1 **and** Review Hub amber badge.
- 26RJ shows image, Theme/Subject (or equivalent), non-zero value, and full 20-coin strip.
- Footlocker text readable on cream (contrast proof).
- Dupe behavior also holds for a roll and a single coin.
- Firestore dump of sweep inputs + counter included in the FT package.
- Sequence: **PREVIEW → FT checklist (FIXED/FAIL) → only then Eric retest.** Do not skip FT.

---

## P0 forcing Plan.v4?

**None.** After IG-1..IG-3 locked into coding brief, known first-try failure modes are covered.

**Explicit:** NO EXECUTE until Eric typed YES. origin/main LOCKED. Preview `p7-gate` only.

---

## Eric decision

**2026-10-27 ~3:52 PM ET — Eric typed YES** → CoS/Desk EXECUTE authorized for **preview `p7-gate` only**, with IG-1..IG-3 in coding brief. Live/main remains LOCKED until FT PASS + separate Eric clear.
