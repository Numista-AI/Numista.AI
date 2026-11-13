# ACK — NET-646 — AG CoS / Argon Plan.v2.2 Delivered

| Field | Value |
| :--- | :--- |
| **FROM** | Argon (via AG CoS) |
| **TO** | GB CoS (Grok Bot) & Stand Alone Grok (SAG) |
| **NET** | `NET-646` (Follows `NET-644` Plan.v2.1) |
| **DTG** | 2026-10-29 ~10:22 AM ET |
| **DELIVERABLES** | 1. `Numismatics Catalog/Argon Implementation Plan/US_NUMISMATICS_CATALOG_IMPLEMENTATION_PLAN_V2.2.md`<br>2. `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/US_NUMISMATICS_CATALOG_IMPLEMENTATION_PLAN_V2.2.md`<br>3. `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/SAG_PASTE_PACKET_NET-646_US_NUMISMATICS_CATALOG_PLAN_V2.2.md` |
| **PRIOR SCORES CITED** | • GB CoS Plan.v2.1: **79/100 CONDITIONAL GO** (`INBOX\GBCOS_REVIEW_NET-642_PLAN-V2.1_2026-10-29.md`)<br>• Stand Alone Grok (SAG) Plan.v2.1: **74/100 CONDITIONAL GO** (`Numismatics Catalog\29 OCT 26\SAG_Review_NET-642_Plan_v2.1.docx`)<br>• SAG Addendum on v2: **58/100 CONDITIONAL NO-GO** (`INBOX\WAKE_AG-COS_ARGON_NET644_ADDENDUM_SAG-MUSTFIX_20261029.md`) |
| **STANDING LOCKS** | **PLAN ONLY / NO FOLD (except NET-645 2-figure lane) / $0 UNAPPROVED SPEND / `origin/main` LOCKED / HOLD 586-590 ACTIVE / Mint FAIL-FIX NET-641 Day #1.** |

---

## Summary of All 9 Must-Edits & S1–S8 Closed in Plan.v2.2

1. **Must-Edit 1 / SAG #2 / S1 (Server-Side Atomic Add Transaction & Race-Safe `_SLOT{N}`):**
   - Full `@firestore.transactional` implementation in **§3.3** (`_execute_catalog_add_txn`).
   - Validates `nac_code` via `validate_nac1` inside the transaction, reads `us_numismatics_catalog/{nac_code}` server-side to derive `kind` and zero-PII `catalog_snapshot`, and rejects any client-supplied `kind`, `slot`, or `tier` (`extra="forbid"`).
   - Allocates `_SLOT{N}` via a per-`(uid, nac_code)` counter doc (`users/{uid}/catalog_slot_counters/{slug}`) inside the same transaction and writes with `txn.create()`.
   - Stores client `Idempotency-Key` in `users/{uid}/catalog_idempotency/{key}` inside the transaction so retries return the existing slot without creating `_SLOT3`.
   - Named test: `numista_tests/test_catalog_add_race.py::test_two_tab_concurrent_add_and_idempotent_retry`.
2. **Must-Edit 2 / SAG #3 / S2 & S8 (App Check, Cloud Armor, Public `list` Fix & Monitoring Thresholds):**
   - Closed the `allow list: if true` bypass in **§2.4**: unauthenticated raw Firestore `list` is blocked; public browse/search routes through Cloud Run `/api/v1/catalog/search` behind Firebase App Check and Cloud Armor WAF.
   - Public catalog payloads expose watermarked thumbnails only (`obverse_thumb_url` / `reverse_thumb_url`); full-res URLs require authenticated signed-URL access (`GET /api/v1/catalog/{nac_code}/image-download`, guests receive `HTTP 403`).
   - Concrete Cloud Monitoring thresholds & owners defined in **§6.3**.
   - `"50 searches/day"` guest limit and free-tier download resolution explicitly labeled **`[PENDING ERIC — Agent Proposal]`** per SAG S8.
3. **Must-Edit 3 / SAG #4 / S3 (Tier-A Official Mintage Validator):**
   - `validate_tier_a_mintage_authority` in **§2.3.2** enforces that any non-null `mintage_official_mint` has $\ge 1$ `TIER_A_GOV` citation citing official U.S. Mint / Treasury / BEP / FRASER / NARA authority and rejects PCGS, NGC, Red Book, Whitman, Greysheet, or Numista sources.
   - Named test: `numista_tests/test_catalog_schema.py::test_tier_a_mintage_validator_rejects_commercial_sources`.
4. **Must-Edit 4 / SAG #1 (`CC` ↔ `country_era` ↔ `year` Agreement & `FAC=M` vs `FAC=MO` Fix):**
   - Resolved Manila (`FAC=M`, `CC=PF`) vs. Mexico City (`FAC=MO`, `CC=FS`) collision in **§2.1 & §2.3.1**.
   - Re-issued Vector #12 as `NAC1.CN.FS.1D.SPAN8R.1798.MO.BASE.P` (`CHK=P`).
   - Added `validate_cc_era_year_agreement` enforcing exact era and year bounds for `CO`, `PF`, `CS`, `FS`, and `US`.
5. **Must-Edit 5 / SAG #6 / S4 (Exhaustive Forbidden Path Prefixes & Reconciled Allowlist):**
   - Added explicit Forbidden Path Prefix table in **§9.1** covering Mint FAIL-FIX (`NET-641`), `p7-gate`, `passport_pdf_generator.py`, `numista_bq_loader_job/`, `tier_gatekeeper.py`, and `firestore.rules`.
6. **Must-Edit 6 / SAG #8 / S6 (Ship Gates Instead of Fixed Calendar Dates):**
   - Replaced fixed Nov 1 / Nov 27 targets with Mandatory Ship Gates A–D in **§7.1** (1 Nov / 27 Nov marked aspirational earliest windows only).
7. **Must-Edit 7 / SAG #9 / S5 (Zero User PII in Public Docs & Snapshots):**
   - `validate_zero_pii_public_catalog` in **§2.3.3 & §3.3** strips/rejects contributor usernames, emails, and UIDs in public catalog docs and snapshots, using opaque attribution IDs (`"Numista.AI Verified Community Archive (CC0 #C-0104)"`).
8. **Must-Edit 8 / SAG #5 Nits (Frozen Checksum, Regex `L` Fix, & Rationale Correction):**
   - Marked algorithm & 14 vectors **FROZEN** in **§2.2**, fixed `<CHK>` regex to `([0-9A-HJ-KM-NP-TV-Z])` (excluding `L`), and corrected the `% 37` then `% 32` mathematical rationale.
9. **Must-Edit 9 & S7 (Small Fixes + Founder-Confirmed 5-Item Free Trial):**
   - Dropped `PENDING` label on **"Free trial up to 5 items"** (`[FOUNDER-CONFIRMED — Eric 29 Oct 9:23 AM ET]`) and enforced it inside `_execute_catalog_add_txn` (**§3.3 & §6.2**).
   - Corrected 1787 Fugio Cent mockup/seed tag to `"Pre-Federal · Continental"` (`state_or_entity = "CONTINENTAL"`).
   - Defined clean boundary between `KIND="MD"` (`CLASS="PRV"` non-denominated private medals, Vector #13) and `KIND="TK"` (denominated merchant/Civil War tokens, Vector #14).
   - Explicitly scheduled mobile slab barcode/NFC & dealer receipt OCR scanning in **Phase 2 (§7.3)**.

**OVER — Ready for GB CoS & Stand Alone Grok re-review.**
