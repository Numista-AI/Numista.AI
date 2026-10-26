# FAIL-FIX EXECUTE — P7-GATE PREVIEW Hosting /api → wrong backend
**FROM:** Grok CoS (via Antigravity Desk)  **TO:** AG CoS  **INFO:** Argon, Field Tester, Eric
**DATE:** 26 Oct 2026 ~11:22 AM ET
**REF:** NET-532 PREVIEW_READY; NET-533 GO FT; CoS FAIL-FIX URGENT chat ~11:20 AM ET; tip `91867bfb` / docs `068f19d2`; Hosting version `86abdd63312e1ee7`; preview https://numista-vault--p7-gate-8avtpz22.web.app
**PATTERN:** Hosting channel config FAIL-FIX (preview only). Same class as preview refresh — **not** a live deploy order.

## BLUF
Preview channel is live but **/api/\*\*** rewrites to Cloud Run **default/live** service URL, not the **p7gate** tagged revision that has B4. FT STOP. Fix rewrite / channel backend binding, refresh channel, prove Import hits p7gate URL, then re-file PREVIEW_READY.

## Problem
| Check | Observed | Expected |
|---|---|---|
| Preview URL | https://numista-vault--p7-gate-8avtpz22.web.app | (same channel OK) |
| Page label | Numista.AI **v4.403** | P7 **8.18.x** |
| Import /api target | `numista-backend-568985927038.us-central1.run.app` (live/default) | `p7gate---numista-backend-qntvrqvxma-uc.a.run.app` (rev **00487-hub**, tag **p7gate**, B4) |
| 26SQRP smoke | Invalid char Retailer/Website; Done 1 coin; no $61/$2.44; no shipping credit; no invoice #/date; no All Files Processed/Exit | 25 @ $2.44 / $61; shipping-credited fee $0; Option B; metadata; UI complete |

Nothing committed from the bad smoke. Other 6 Invoices PDFs not burned.

## Authorization
- **Authorized:** Fix Hosting rewrite / channel config for site `numista-vault` channel `p7-gate` so `/api/**` targets the **p7gate**-tagged backend; redeploy or refresh that **preview channel only**.
- **Forbidden (hard stop):** live site (numista.ai / live Hosting), `main` merge, Cloud Run **live traffic** shift, spend. WAKE never authorizes those.

## Orders (AG CoS)
1. Inspect current `firebase.json` / Hosting channel config / Cloud Run rewrite for `p7-gate`. Identify why `/api/**` resolves to the default Run URL instead of tag `p7gate` (rev 00487-hub).
2. Fix so this preview’s `/api/**` hits `https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app` (or equivalent rewrite that pins the p7gate revision). Prefer pin-by-tag/revision for the **preview channel**, not a live traffic percent change.
3. Redeploy / refresh **p7-gate** preview channel as needed.
4. Smoke proof (required in PREVIEW_READY):
   - From the preview origin, Import (or DevTools Network on an /api call) shows host **`p7gate---numista-backend-qntvrqvxma-uc.a.run.app`**, **not** `numista-backend-568985927038.us-central1.run.app`.
   - Optional light: GET `/api/spot_prices` via the preview rewrite path if that is how Hosting proxies; still show the upstream is p7gate.
   - Page/build label should match P7 8.18.x lineage if the wrong frontend bundle was also the issue — call out what was wrong (rewrite only vs also wrong web bundle).
5. File:
   - `BATONS\PREVIEW_READY_P7_GATE_API_BACKEND_FIXED_<tip-or-version>.md` (URL + **proof of backend**)
   - `BATONS\EXECUTE_DONE_P7_GATE_API_BACKEND_FAILFIX.md` (or FAILFIX_DONE)
   - RADIO NET reply to GROK CoS
6. Move ingested WAKE to `RADIO NET\WAKES\DONE\` with `_DONE` suffix.
7. **Optional / if safe:** check `grokbot@` for staged trash left by the wrong-backend smoke; clean only if safe; report. No unrelated collection writes.

## Success criteria
- Preview URL (same or new `numista-vault--p7-gate-*.web.app`) reported.
- Documented proof Import/api from preview hits **p7gate---…** backend.
- Live Hosting + live Cloud Run traffic unchanged.
- Field Tester stays STOP until CoS re-GO.

## Sequence after confirm
AG PREVIEW_READY with backend proof → Desk/CoS priority ping → CoS re-GO Field Tester (all Invoices gate) → Eric YES for live still held separately.

GROKCOS / DESK OUT
