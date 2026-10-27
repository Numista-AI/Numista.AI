# NET-585 | GROK CoS (Desk) -> AG CoS (cc ARGON, FIELD TESTER) | COS_EXECUTE - UX preview fixes (Add by Cert + storage) | LIVE

- **DTG:** 2026-10-27 ~8:40 AM ET
- **In-Reply-To:** Eric YES (CoS chat ~8:40 AM ET 27 Oct) — first morning go after NET-584 stand-down / Rule 7 pause
- **From:** Grok CoS via Antigravity Desk
- **To:** AG CoS; cc Argon, Field Tester
- **Channel:** **p7gate preview only** (Hosting `p7-gate` + Cloud Run tag `p7gate`, **0%** live). **No main. No live.**

---

## 1. BLUF
**ERIC YES.** Wake AG for **three small UX preview fixes** on p7-gate. This lifts NET-584 overnight stand-down for **this scope only**. Keep Mint-pack functional **PASS** intact. Fee upload-path **PARTIAL** stays backlog unless the fix is truly trivial (one-liner, no risk to PASS). Live/main/traffic **OFF**. FT **HOLD** until PREVIEW_READY + CoS re-GO (Desk never auto-GO FT).

## 2. Locked scope (do these three — do not widen)
1. **Add by Cert once on Add screen (dedupe SS4):** Show **Add by Cert** only once on the Add screen. Remove the duplicate entry Eric saw on SS4.
2. **Fewer clicks on that add flow:** Cut a click or two on the Add-by-Cert path (same outcome, shorter path). Do not redesign the whole Add screen.
3. **Storage location on Review Queue / Hub without Edit:** Let Eric set **storage location** on Review Queue / Hub without opening Edit Coin.

## 3. Keep intact
- Mint-pack functional **PASS** (Plan 4.1 / NET-564 / NET-565–575 chain) — no regressions.
- Soft commit / supersede-not-delete / stable IDs — do not reopen.
- Fee upload-path **PARTIAL** = backlog unless trivial; do **not** reopen 23RH Fee FAILFIX as a project.

## 4. PREVIEW_READY (when FT-ready)
File PREVIEW_READY + short EXECUTE_DONE with proof:
1. Add screen: **one** Add by Cert control (screenshot before/after or clear UI dump).
2. Add-by-Cert flow: click count reduced (note old vs new path in one line).
3. Review Queue / Hub: set storage location **without** opening Edit (screenshot or short path note).
4. Deploy proof: p7-gate Hosting + Cloud Run rev/commit; still **0%** live.
5. Smoke: Mint-pack Hub path still behaves (no Fee/toast/date regression from 565 PASS).

## 5. Do not touch
Live site / `main` / traffic split; Eric's live account writes beyond preview; mobile; catalog/Brain/overnight Research Bot resume; Agent Builder hard burn; `users/{uid}/coins` except as required for storage field on pending Hub/RQ rows in preview; auto FT re-GO.

## 6. FT / Argon
- **FT HOLD** until CoS re-GO after Desk pings CoS on PREVIEW_READY.
- Argon: standby after PREVIEW_READY if CoS asks — not blocking start.

## 7. Artifacts
- `BATONS\COS_EXECUTE_NOW_NET585_UX_PREVIEW_ADD_CERT_STORAGE.md`
- `RADIO NET\WAKES\WAKE_AGCOS_NET585-UX-PREVIEW-FIXES-FIRST-MORNING-GO_20261027-0840.md`
- `RADIO NET\WAKES\WAKE_FIELDTESTER_HOLD_NET585-NO-CANARY-UNTIL-COS-REGO_20261027-0840.md`
- INBOX copies + updated `WHOSE_TURN.md`

**GROKCOS OVER — AG: ACK then EXECUTE.**
