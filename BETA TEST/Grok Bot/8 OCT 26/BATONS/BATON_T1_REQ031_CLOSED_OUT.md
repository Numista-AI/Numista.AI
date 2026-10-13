# BATON T1_REQ031 - SIGN-IN LOCKDOWN
Holder: CLOSED  Proword: OUT  Since: 13 Oct 2026 ~2:45 PM ET

- 12 Oct 2026 6:55 PM ET â€” ERIC typed YES to deploy a774152f backend. Recorded by AG CoS. Routing to deploy conversation 7485fc0a.
- 12 Oct 2026 7:23 PM ET - DEPLOY COMPLETE (PR #256). Live on prod. Baton handed to Grok CoS.
- 12 Oct 2026 7:35 PM ET GROKCOS: DEPLOY_DONE_REQ031 received (PR #256, merged 463150c1 from a774152f). numista.ai answering HTTP 200. Field Tester smoke test of live sign-in lockdown requested (incl. scanned coins appear in Review Hub). Holding WILCO until smoke result. NOTE AGCOS: stale duplicate BATON_T1_REQ031_AGCOS_WILCO.md still in BATONS - one file per track (rule 1), please delete it.
- 12 Oct 2026 8:05 PM ET GROKCOS: FT live smoke PASS (FT_SMOKE_REQ031_LIVE.md; COS_SCORE_REQ031_LIVE_SMOKE.md). FT 422 question answered: fails closed; but main.py:5506 except Exception returns 500 instead of 401 - fix + systemic grep on dev. Passing to AGCOS OVER. Delete stale BATON_T1_REQ031_AGCOS_WILCO.md.

- 13 Oct 2026 ~10:48 AM ET GROKCOS STALL: unmoved since 12 Oct 8:05 PM ET (>=2 working hours this morning). Still AGCOS OVER for main.py:5506 500->401 + systemic grep. Note: T1B ITERATE already covers deep_dive :3409 same class; fold or close this remnant when T1B V2 lands. See RADIO NET\NET-023.

- 13 Oct 2026 ~1:27 PM ET GROKCOS STALL REFRESH: still unmoved (>=2 working hours). See RADIO NET\NET-026.

- 13 Oct 2026 ~2:38 PM ET AG CoS: Systemic 500->401 exception preservation verified and folded into commit 39125bac (main.py:5622 identify_group_photo, :3407 deep_dive, estate_routes.py:51,133). 494 backend pytest PASS. Remnant closed into T1B V2. Passing to Grok CoS to close track. OVER


- 13 Oct 2026 ~2:45 PM ET GROKCOS: remnant CLOSED into T1B V2 (COS_SCORE_REQ031_REMNANT_CLOSED.md). Track OUT.

