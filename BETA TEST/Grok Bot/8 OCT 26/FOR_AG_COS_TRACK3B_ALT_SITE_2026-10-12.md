# FOR AG COS - TRACK 3b: ALTERNATE "SIMPLE" SITE (Eric approved YES 12 Oct 2026 12:24 PM ET)

Model: Claude Sonnet 4.6 (Thinking). Reviewer: Gemini 3.8 Flash. Deliverable: PLAN_V1_REQ032B_ALT_SITE.md in this folder.

## Design (Eric's decision)
- ONE database. Two front ends (Classic = current, Simple = iPhone-style from REQ_032 mockups fix1-fix5) read/write the SAME records via the SAME backend APIs. No data copies, no separate DB.
- Both front ends must hit identical backend auth + safety checks (REQ_031 lockdown, confirms, no values in AI prompts). No new backend routes that bypass these.

## Rollout (feature flag, server-side)
1. Phase A: Simple version visible ONLY to eric.seaman@yahoo.com and eric@numista.ai, on their live data.
2. Phase B: beta testers (after Eric's YES).
3. Phase C: all users, with a Classic/Simple toggle in Settings (after Eric's YES).
Flag is server-set; users cannot grant themselves access.

## Plan must cover
- Hosting/URL (e.g. beta.numista.ai or in-app toggle) with pros/cons.
- How the flag is stored and checked (file:line).
- Proof both UIs share the same API calls (list them).
- Tests: flag off = no access; both UIs show the same coin after an edit.

## Order of work
REQ_031 hotfix ships FIRST. Track 3b builds on dev only. No deploy without Eric's typed YES.
Update WHOSE_TURN.md: add row "Track 3b ALT SITE - AG CoS (plan)". When plan + Gemini review land, set to "Grok CoS: score it".
