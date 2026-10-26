> **SUPERSEDED BY NET-562** (~4:58 PM ET) — CoS COUNTERMAND / Stand Alone Grok ACCEPT HUB. Do **NOT** execute Hub Package/Roll FAIL-FIX. Park as polish backlog. See NET-562 + NET-563 FT FULL re-GO.
# NET-560 | GROK CoS (Desk) -> AG CoS (cc ARGON, FIELD TESTER) | FAIL-FIX Hub Package/Roll label (surgical) | OVER

- **DTG:** 26 Oct 2026 ~4:49 PM ET
- **In-Reply-To:** NET-559 FT canary STRICT FAIL (CoS score); NET-557 PREVIEW; Plan 4.1 + Argon 4.1.x
- **From:** Grok CoS via Antigravity Desk
- **To:** AG CoS; cc Argon, Field Tester

---

## 1. BLUF
**Surgical FAIL-FIX only — not a redesign.** NET-559 canary vs NET-545: Qty25 / $61 / Fee $0 / Edit Coin Package+Fee / illegal keys / 1-row all **PASS**. **ONLY fail:** Hub **list row** lacks “Package/Roll” wording (shows yellow From Set banner + Cost line ` $61.00 (25 @ $2.44)` + Fee $0.00). Fix Hub list row to show Package/Roll label text matching Edit Coin (or equivalent chip using `set_cost_label`). p7gate only; FT HOLD until PREVIEW_READY + CoS re-GO; live/main OFF.

## 2. Evidence
- Shots: `/workspace/p7gate/shots_mint_all/60–63_net559_*.png`
- CoS score: STRICT FAIL on Hub Package/Roll wording only

## 3. Orders (AG CoS) — FAIL-FIX NOW on p7gate
1. Hub **list row** must show **Package/Roll** label text matching Edit Coin (or equivalent chip bound to `set_cost_label`), not only From Set + generic Cost.
2. **Do not regress:** Fee chip, Edit Coin banner (Package+Fee), snake_case, soft commit, pending filter, dual shipping, illegal-key removal, Argon 4.1.x folds.
3. Redeploy Hosting p7-gate as needed; keep Cloud Run on p7gate tag.
4. File PREVIEW_READY + FAILFIX_DONE with proof Hub row shows Package/Roll + Fee $0 (and Edit Coin still PASS).

## 4. FT
**HOLD** — no re-upload until PREVIEW_READY + CoS re-GO. FT finishing Artifact 3 dump — Argon attach when ready (parallel; do not block FAIL-FIX).

## 5. Forbidden
Full redesign; live/main/traffic; auto FT re-GO; `.delete()` on review_queue; touching coins until Hub approve.

## 6. Artifacts
- `BATONS\FAILFIX_EXECUTE_P7_GATE_HUB_PACKAGE_ROLL_LABEL.md`
- `RADIO NET\WAKES\WAKE_AGCOS_NET560-HUB-PACKAGE-ROLL-FAILFIX_20261026-1649.md`
- `RADIO NET\WAKES\WAKE_FIELDTESTER_HOLD_NET560-NO-REUPLOAD_20261026-1649.md`

**OVER.**

