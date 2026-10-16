# BATON P4 TIGHTEN 21 ROUTES LACKING OWNERSHIP CHECKS (priority 4 of 5)
Holder: AG CoS. Ref: NET-070, NET-067 Category-2 residual, T4.

## Task
Add per-route ownership (caller uid == resource owner, or admin) to the 21 Category-2 routes from the T4 audit.
- List all 21 with file:line in the EXECUTE_DONE. Add an IDOR test per route (pytest -s). Re-run full pytest + flutter test.
- Check related routes systemically (same handler patterns). Keep CORS behavior on 401s in mind (outer default-deny middleware).
- Dev only. Deploy later only on Eric's typed YES via cherry-pick from main.
## HARD LIMITS (all tracks)
- Dev only. No deploy without Eric's own typed YES. Deploys = cherry-pick approved commits onto a branch from main. Never a full dev merge.
- Eric is adding new coin purchases to his collection TODAY. NOTHING writes to his collections or any user collection. No sync_canon. No Firestore writes.
- Never fake data. U.S. Mint/Treasury figures beat PCGS/NGC. No PII or collection values in prompts or files.
- Treat every error as systemic and check related features.
- Rule 7: keep your 25-min wake timer running. git mv the baton (one file per track).
## Log
- 2026-10-14 09:40 ET GROKCOS: issued. Passed to AGCOS. OVER.
- 2026-10-14 12:40 ET GROKCOS: SCORED FAIL. Full pytest 15 failed (receipts/identify routes) caused by P4; clean P4 commit needed; check attorney links. See COS_SCORE_P4_ROUTE_OWNERSHIP.md, NET-088. Passed to AGCOS. OVER.

- 2026-10-14 14:40 ET GROKCOS WATCH: STALL FLAG. Unmoved since NET-088 FAIL handback (~12:40 ET, ~2h). Critical-path AG idle; Eric pinged once (check radio). See NET-092. OVER.

- 2026-10-14 15:57 ET GROKCOS WATCH: hourly re-flag. Still unmoved since the 12:40 FAIL (~3h15m). AG says subagent quota is exhausted; queued after P7/P6/P5. AG critical path active (15:49/15:52), so no Eric ping. See NET-100. OVER.
- 2026-10-14 17:40 ET GROKCOS WATCH: hourly re-flag. Still unmoved since 12:40 FAIL (~5h). Queued after P7. AG critical path active on P7 V5 (NET-109). No Eric ping. See NET-110. OVER.

- 2026-10-14 19:41 ET GROKCOS WATCH: hourly re-flag. Still unmoved since 12:40 FAIL (~7h). Queued after P7 (Rule 8). AG critical path active on P7 V7 (NET-116 ~19:15). No Eric ping. See NET-117. OVER.

- 2026-10-14 20:41 ET GROKCOS WATCH: hourly re-flag. Queued behind LIVE-AUTH V2 (NET-121) + P7 preview hold. AG critical path on LIVE-AUTH. No Eric ping (overnight). See NET-122. OVER.
- 2026-10-14 21:35 ET GROKCOS WATCH: still queued behind P7/LIVE-AUTH (Rule 8). No hourly re-flag (NET-122 <1h). See NET-125. OVER.

- 2026-10-14 22:08 ET GROKCOS WATCH: hourly re-flag. Queued behind LIVE-AUTH (ERIC) + P7 preview hold (Rule 8). No Eric ping (overnight). See NET-126. OVER.
- 2026-10-14 23:15 ET GROKCOS WATCH: hourly re-flag. Queued behind P7 preview hold (Rule 8); NET-129 also queued. No Eric ping (overnight). See NET-130. OVER.
- 2026-10-14 23:42 ET GROKCOS WATCH: still queued behind P7 preview hold (Rule 8); NET-129 Plan.v1 GO filed (code WAIT). No hourly re-flag (Grok NET-130 watch <1h). No Eric ping (overnight). See NET-131. OVER.

- 2026-10-15 02:12 ET GROKCOS WATCH: still queued AGCOS_OVER behind P7 (Rule 8). Hourly re-flag NET-136. Not a stall. Overnight quiet. OVER.


- 2026-10-15 19:45 ET GROKCOS WATCH: hourly re-flag. Still AGCOS_OVER queued behind P7 V8.7 (Rule 8). Not a stall. Overnight quiet. See NET-230. OVER.

- 2026-10-15 21:12 ET GROKCOS WATCH: hourly re-flag. Still AGCOS_OVER queued behind P7 V8.8 (Rule 8). Not a stall. Overnight quiet. See NET-234. OVER.


- 2026-10-15 22:15 ET GROKCOS WATCH: hourly re-flag. Still AGCOS_OVER queued behind P7 (V8.8 PASS code, awaiting AM preview + UX/FT; Rule 8). Not a stall. Overnight quiet. See NET-238. OVER.
