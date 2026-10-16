# BATON P8 MORGAN PHOTO UPLOAD (after P7)
Holder: AG CoS. Ref: NET-083.

## Problem
Eric's phone (home-screen PWA) attached a 4.2 MB JPEG of an NGC slab in Ask Morgan chat -> generic 'Something went wrong'. A smaller photo worked yesterday. Likely an upload size limit (client, backend body limit, Cloud Run 32 MB request cap, or Gemini inline-image limit - find which).

## Fix (dev only)
- Client-side downscale before upload: longest side ~1600 px, JPEG re-encode, under 1 MB. Keep EXIF orientation correct; strip GPS/EXIF metadata.
- Backend: raise or properly handle the limit; return a clear 413-style error code.
- UI: show a clear message ("Photo too large - we tried to shrink it; please retry or pick a smaller photo") instead of the generic error.
- SYSTEMIC: check EVERY photo upload path - Ask Morgan, scanner/Microscope Scanner, AI Photo ID, Add (incl. new Add by Cert #), Review Hub, bulk folder-drop. Use one shared resize helper. List each path + status in EXECUTE_DONE.
- Tests: a 4-5 MB JPEG (and a large HEIC/PNG if supported) passes on every path; an oversize backend payload gets the clear error. Full flutter test + pytest.

## Gate
Gemini build review -> Field Tester on the grokbot test account (phone-size viewport/PWA) -> GROKCOS score -> Eric typed YES -> cherry-pick onto a branch from main.

## Limits
Dev only. Cherry-pick only. No collection writes (test account only). No deploy without Eric's YES. **Keep P8 behind P7.**
## Log
- 2026-10-14 12:25 ET GROKCOS: issued. Queue behind P7. OVER.
- 2026-10-14 14:30 ET GROKCOS WATCH: STALL FLAG. Unmoved ~2h since issue (~12:30 ET). Correctly queued behind P7 (TOP PRIORITY). No Eric ping - critical AG work (P7/P4/P5/P6) last moved 12:40 ET (~110m, under 2h). See NET-090. OVER.

- 2026-10-14 15:57 ET GROKCOS WATCH: hourly re-flag. Unmoved since issue ~12:30 (~3h25m). Correctly queued behind P7. AG critical path active (15:49/15:52), so no Eric ping. See NET-100. OVER.
- 2026-10-14 17:40 ET GROKCOS WATCH: hourly re-flag. Unmoved since issue ~12:30 (~5h10m). Correctly queued behind P7. AG on P7 V5. No Eric ping. See NET-110. OVER.

- 2026-10-14 19:41 ET GROKCOS WATCH: hourly re-flag. Unmoved since issue ~12:30 (~7h10m). Correctly queued behind P7. AG on P7 V7 (NET-116). No Eric ping. See NET-117. OVER.

- 2026-10-14 20:41 ET GROKCOS WATCH: hourly re-flag. Queued behind LIVE-AUTH V2 (NET-121) + P7 preview hold. AG critical path on LIVE-AUTH. No Eric ping (overnight). See NET-122. OVER.
- 2026-10-14 21:35 ET GROKCOS WATCH: still queued behind P7/LIVE-AUTH (Rule 8). No hourly re-flag (NET-122 <1h). See NET-125. OVER.

- 2026-10-14 22:08 ET GROKCOS WATCH: hourly re-flag. Queued behind LIVE-AUTH (ERIC) + P7 preview hold (Rule 8). No Eric ping (overnight). See NET-126. OVER.
- 2026-10-14 23:15 ET GROKCOS WATCH: hourly re-flag. Queued behind P7 preview hold (Rule 8); NET-129 also queued. No Eric ping (overnight). See NET-130. OVER.

- 2026-10-15 02:12 ET GROKCOS WATCH: still queued AGCOS_OVER behind P7 (Rule 8). Hourly re-flag NET-136. Not a stall. Overnight quiet. OVER.


- 2026-10-15 19:45 ET GROKCOS WATCH: hourly re-flag. Still AGCOS_OVER queued behind P7 V8.7 (Rule 8). Not a stall. Overnight quiet. See NET-230. OVER.

- 2026-10-15 21:12 ET GROKCOS WATCH: hourly re-flag. Still AGCOS_OVER queued behind P7 V8.8 (Rule 8). Not a stall. Overnight quiet. See NET-234. OVER.

