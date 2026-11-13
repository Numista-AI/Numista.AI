# ACK_BATON_NET-798_PLAN_UNIFIED-COIN-DETAILS-VIEW_2026-11-04

**From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**To:** Grok CoS (`GB CoS`), Argon, Stand Alone Grok (`SAG`), Founder Eric  
**Date:** 4 Nov 2026 7:42 PM ET  
**Reference:** `BATON_NET-798_PLAN_UNIFIED-COIN-DETAILS-VIEW_2026-11-04-1933.md`

---

### 1. Acknowledgment & Baton Intake
AG CoS v4 acknowledges receipt of **`BATON_NET-798`** (PLAN ONLY: Unified Coin Details View for the 10–16 Nov build).

* **Founder Eric's Typed Plan Authorization (7:32 PM ET):** YES to PLAN it. Execution requires its own typed YES.
* **Design Spec Verified:** `1 NUMISTA.AI\UI UX DESIGN\2026-11-04\Unified Coin Details\Spec_Unified_Coin_Details_2026-11-04.md` audited and incorporated.
* **Supersession & Integration:** Cards and Table will open the exact same unified details view. Supersedes `NET-794` item 3. `NET-794` items 1 & 2 (photo asset resolution and header contrast) will be folded in.
* **Binding Decisions Logged:**
  1. "Show values" toggle stays ON across Next/Previous navigation until the modal is Closed.
  2. Congress.gov laws not yet checked by Numista.Ai will be displayed with the exact label `"From Congress.gov, not yet checked by us"`. Catalog legislation field always wins when present.
  3. Legislation field fallback handled gracefully when missing/empty (`"Morgan hasn't found the law for this coin yet"` + research request action).
  4. Privacy Rule enforced: Storage location and dollar values are strictly mutually exclusive (revealing values conceals storage location; location requires PIN re-authentication).
* **Execution Queue:** Queued immediately after `BATON_NET-788` and `BATON_NET-791`.
* **Cycle:** Argon review -> GB CoS 95+ -> SAG concurrence -> Founder Eric typed YES.
* **Standing Locks:** `origin/main` locked at `9f04550a`, Stripe strictly OFF, zero Firestore writes/seeding, zero code deploys, zero PII.
