# EXECUTE DONE NET-777: FAILFIX PLAN v1 for Live Public Catalog (NET-780)
- **Date/Time:** 2026-11-04 5:10 PM ET
- **Station:** AG CoS v4 Work (`ba2bfdb2`)
- **Authority:** `BATON_NET-777_FAILFIX_PLAN_CATALOG-LIVE-FT_v1_2026-11-04-1628.md` + `AMENDMENT A1` (4 Nov 2026 4:38 PM ET).
- **Assigned Radio Sequence:** NET-780
- **Status:** **PLAN ONLY COMPLETE** (100% finished, filed to INBOX, BATONS, RADIO NET).

---

## 1. Deliverable Summary
- **Primary Deliverable:** `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\FAILFIX_PLAN_NET-777_CATALOG_v1.md`
- **Copies Filed:**
  - `BETA TEST\Grok Bot\8 OCT 26\BATONS\FAILFIX_PLAN_NET-777_CATALOG_v1.md`
  - `BETA TEST\Grok Bot\8 OCT 26\RADIO NET\FAILFIX_PLAN_NET-777_CATALOG_v1.md`

## 2. All 6 Items Addressed in Strict Order
1. **Images (Amendment A1 Mirror Plan):**
   - 176 unique Wikimedia Commons images (166 `upload.wikimedia.org`, 10 `thumb.wikimedia.org`).
   - One-time mirror to GCS `numista-catalog-assets` served from on-domain / whitelisted GCS URL.
   - Retains and displays full attribution: `credit`, `license`, `source_url`.
   - Complete cost model included: 0.07 GB storage ($0.0014/mo at-rest, $0.00088 upload, $0.00–$2.40/mo egress; total < $2.50/mo).
   - Optional CSP bridge detailed for `firebase.json:284`.
2. **Deep Links:**
   - Real shareable URLs updating `window.history` to `/catalog/:nacCode` on modal open.
   - Cleanly reverts to `/catalog` on modal dismiss.
   - Preserves direct landing via `main.dart:154-178` and `catalog_browse_screen.dart:71-82`.
3. **Ask Morgan Signed-Out Behavior:**
   - Intercepts signed-out visitors with an informative modal detailing Morgan AI capabilities.
   - Action buttons: "Continue Browsing", "Sign In" (with redirect parameter), and "Create Free Account".
   - Seamlessly routes authenticated users into Morgan AI Chat.
4. **Era Filter State Persistence:**
   - Resets `_selectedEra = 'all'` in `_onTypeChanged(type)` on tab click (`catalog_browse_screen.dart:209-214`).
   - Prevents empty results when switching from Coins to Paper Money / Medals.
5. **Pre-Federal Filter Consistency:**
   - Aligns `_selectedEra == 'pre_federal'` condition strictly with C1 (`item['is_pre_federal'] == true || item['pre_federal'] == true`, 9 records).
   - Excludes Washington Indian Peace Medal (1789, `pre_federal: false`), eliminating badge discrepancy.
6. **First Load Performance Speed Fix:**
   - Minifies 5.5 MB JSON to 4.0 MB (130 KB gzipped).
   - Establishes two-tier payload architecture (`catalog_index_v1.json` at ~320 KB uncompressed / ~34 KB gzipped for instant grid render).
   - Adds immutable CDN cache-control headers.
   - Sets target first load time to **< 2.0s** (p95 < 2.5s), down from 7–9s.

## 3. Standing Locks Verified
- Zero code modifications executed.
- Zero deployments executed.
- `origin/main` strictly locked at `9f04550a`.
- Stripe strictly locked OFF.
- Zero Firestore writes / zero seeding.
- Image mirroring strictly locked pending Founder Eric's typed YES.
- Next step: Baton passed to Argon for review (`BATON_NET-780`).
