# NET-083 GROKCOS -> AGCOS: New P8 (Morgan photo upload) + P6 auth note
14 Oct 2026 12:25 PM ET. Baton: `BATONS\BATON_P8_MORGAN-PHOTO-UPLOAD_AGCOS_OVER.md`. Order: P7 first, then P8.

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
## P6 NOTE (2026-10-14 12:25 ET GROKCOS): Use Vertex AI Gemini via numista-qc with the ADC login Eric refreshed at 11:26 ET. NO API key; never ask Eric for a key in chat.

OVER
