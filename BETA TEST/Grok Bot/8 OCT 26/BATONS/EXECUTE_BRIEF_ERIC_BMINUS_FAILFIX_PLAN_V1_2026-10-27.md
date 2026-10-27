# EXECUTE BRIEF — Eric B− FAIL-FIX Plan.v1 (NET-629 → EXECUTE)

**Authorization:** Eric typed YES 2026-10-27 ~5:45 PM ET  
**Target:** preview `p7-gate` ONLY. origin/main LOCKED. No live/main without a later typed YES.  
**Chain scores:** Argon 71 CONDITIONAL GO | GB 91 PASS WITH EDITS | SAG 90 CONDITIONAL GO  
**Plan:** `ERIC_BMINUS_FAILFIX_PLAN_v1_2026-10-27.md` + this brief’s mandatory folds

## MUST fold before / while writing code (Argon Must-Fix 1–5 + GB FF-1..3)

### Fee (I-04b)
1. Patch **`main.py:7589–7590`** blanket `allocated_fee = 0` for 26SQRP invoices **and** the confirmed **`main.py:7718–7719`** `pack_expanded` zero. Fixing only one leaves USM24086141 at Fee $0.
2. Parent Hub roll lot carries invoice S&H ($9.95); do **not** multiply full S&H onto every pack-expanded child. Preserve working **26RJ Fee $9.95**. Dual-write/read `allocated_fees` / `shipping_fee` / `Allocated Fees` consistently.

### Commit valuation + images (I-07 / PM-01)
3. Wire **real** FastAPI `BackgroundTasks` / async enrich kick on `commit_reviews` (name the function; it must run). Sets/rolls: verify baseline intact; **skip Greysheet overwrite**.
4. On **Commit** path (FT path): dual-write PascalCase **`AI Estimated Value`** and `ai_estimated_value` plus existing snake_case; fill-missing-only baseline from catalog `issue_price` / cost when value blank/zero; set `enrichment_status = "enriched"` when baseline lands. Mirror same into `keep_set_as_is` (second path).
5. Prove 26RJ catalog image URLs copy onto vault (`image_url_obverse` / `image_url_reverse` → also `primary_image_url` / `photo_urls` as needed). Catalog URLs exist (`us_mint_catalog_service.py:200-202`); wiring must stick. Frontend dual-read for value + image keys per Plan.v1 §B.
6. **FF-3:** Baseline is fill-missing-only (never overwrite non-blank collector/Greysheet). Log enrich errors — no bare `except: pass`.

### Also from Plan.v1
- Do not regress: smoke, Invoice #, I-04c, I-05, I-06, I-08/SAG1 dup amber, 26RJ Fee $9.95, SAG3 contrast, SAG4 20-coin wrap.
- Zero daytime Check Grounding; NET-610 Option B overnight separate.

## Gates after PREVIEW_READY
1. Field Tester runs FT_RETEST_CHECKLIST — FIXED/FAIL each item.
2. Proofs: (a) Commit 26RJ → image + non-zero val (b) 26SQRP Hub Fee $9.95 (c) prior PASS green + Firestore dumps of committed 26RJ vault doc and 26SQRP Hub row.
3. Only after FT PASS → prompt Eric founder retest.
4. Live/main: **hold** until Eric types YES again after retest.

## Out of scope
- NET-610 Option B · catalog merge HOLD stack · Plan.v2 rewrite · Claude/3.8 fallback (only if next FT still misses a P0)

## Radio
EXECUTE preview FAIL-FIX. Report PREVIEW_READY with Hosting URL + Run ID + commit SHA. AG CoS codes; Desk mirrors/wakes only (not coding).
