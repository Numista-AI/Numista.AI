# ACK: BATON NET-752 — AG CoS v4 (NET-747 CATALOG BROWSE PLAN v2)

- **To:** Grok CoS Desk / Argon / SAG / Founder Eric
- **From:** AG CoS v4 / Gemini 3.8 Code Reviewer (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3` | `eric@numista.ai`)
- **Timestamp:** `2026-11-03T13:25:00-05:00` (ET)
- **Authorizing Baton:** `BATON_NET-752_AG_NET-747-PLAN-v2_20261103-1315.md`
- **Subject:** Acknowledgment and Delivery of `AG_PLAN_NET-747_CATALOG-BROWSE_v2.md`

---

### Verification Against All 7 Must-Fixes & Catalog Builder Addendum Directives:

1. **`MF-747-1` (Soft-404 Reuse & Accurate Hosting Routing):**
   - Verified. Dropped second `CatalogSoft404Screen`. Strictly reuses existing `NotFoundScreen` (`numista_mobile/lib/screens/not_found_screen.dart:18-23`), adding catalog-aware copy (*"We don't have that one yet."*), search box, "Ask Morgan" button, intake link, and `<meta name="robots" content="noindex">` injection. Corrected Firebase Hosting rewrite explanation (SPA rewrite returns 200, `noindex` blocks indexing). Updated `main.dart:119-140` (`isKnownPath`) and `firebase.json` specifications.
2. **`MF-747-2` (Exact UX Badge Hex Colors & SVG Icons):**
   - Verified. Matched verbatim to `ux/badges_concept.html:5-6, 12-14`: Pre-Federal pill locked to `2px solid #1F5FAD` outline on `#FFFFFF` with `#0B2545` bold text (15.39:1 AAA text, 6.37:1 outline); `"Needs source"` locked to `2px solid #6B6B6B` with circled `"i"` SVG and `#333333` text (12.63:1 text); `"Details coming"` locked to `2px solid #6B6B6B` with dotted-circle SVG (`stroke-dasharray="3 2.5"`) and `#333333` text. Top block styled verbatim to `ux/catalog_top_concept.html:10-24`.
3. **`MF-747-3` (Page Section Order, Newest Entries, Image+Source First):**
   - Verified. Layout order matches `Plan.v1_catalog.md:155` exactly: Top Block -> In-Progress Notice -> 1. Browse -> 2. Newest Entries -> 3. Coverage by Year -> 4. Missing Something? Browse lists default-sort **image + source first** (`Plan.v1_catalog.md:160`). "Newest Entries" strictly excludes seed records.
4. **`MF-747-4` (`schema.json` NAC Code Pattern Fix):**
   - Verified. Added prerequisite schema fix updating `nac_code` regex pattern to support multi-segment seed codes (including `.BEP.BASE.2` and related suffixes) across all entries, with unit test asserting 0 validation errors.
5. **`MF-747-5` (Image Ranking, SHA-256 Check, Attribution, Type Image Label):**
   - Verified. Verification of SHA-256 checksums for all 171 manifest images in `images_MANIFEST.csv`. Multi-image ranking order enforced: `1. Museum -> 2. Public domain -> 3. Verified collector uploads`. Every image displays `credit` and `license`. `primary_image` denotes exact coin match; `type_image` displays `"date may differ"`.
6. **`MF-747-6` (4 Shaky X-Post Claims & Manual Read Gate):**
   - Verified. Explicitly strips/blocks the 4 known shaky claims (`Fugio source file`, `Chain cent grounding`, `1793 half-cent "first" claim`, and `1795 $10 placeholder link`) from `social_posts`. Mandates manual read gate for notes. Unit test asserts 0 occurrences.
7. **`MF-747-7` & Addendum (Allow-List Mapping, 3,202 Master Records, Virtualization):**
   - Verified. Sized for **3,202 records** (`entries_master_20261103.jsonl`), read through small read-only adapter (NEVER runs `build.py` or `finalize.py`). Varieties handled as structured objects (`name`, `attribution`, `status`). 951 placeholders marked `"Details coming"` with neutral coin outline. Virtualized using Flutter Web `CustomScrollView` + `SliverGrid` / `SliverList` (`SliverChildBuilderDelegate`) for smooth 60fps rendering.

---

### Deliverables Filed:
- `AG_PLAN_NET-747_CATALOG-BROWSE_v2.md` filed across `INBOX`, `BATONS`, `RADIO NET`, and `For SAG`.
- Turn returned to Review Swarm: Argon review from RADIO NET -> CoS score 95+ -> SAG concurrence -> Founder Eric's typed YES -> Execute.
- Locks unchanged: `origin/main` locked at `9f04550a`, live site untouched, Stripe OFF.
