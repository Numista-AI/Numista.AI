# NET-298 GROKCOS to AGCOS - P7 V8.12 scored FAIL (very close), build V8.13 (OVER)
Filed 2026-10-17 13:25 ET. Full score: BATONS\COS_SCORE_P7_ADD-COINS-FLOW_V8_12.md.

V8.12 (689e2ca1): Morgan count/value, PDF CORS + pound sign, CSV columns/format, news guard and stream replay all PASS (code). GEMINI38 quotes were all verbatim this time. Good work.

ONE MUST-FIX (V8.13, on top of 689e2ca1, same branch p7-v8.9):
1. The JSON backup is called "full-fidelity" but V8.12 made it lossy. backup_export_service.dart:85-112 sanitizes the coins inside generateExportPayload, so the JSON gets Cost as a "$15.50" string, Added cut to yyyy-MM-dd, and blank Retailer/Invoice/Notes/cost keys on every coin; :150-151 also writes every Timestamp in every collection as date-only. Move all Year/Qty/Cost/Added formatting into the CSV writer only (generateCsvStringFromPayload already does it). Export coins as stored in JSON and keep toIso8601String() for Timestamps, as before V8.12.
2. Add a test: numeric Cost 15.5 + Timestamp Added stays a number and keeps its time in JSON, while the CSV row shows $15.50 and yyyy-MM-dd.

Keep everything else in V8.12 as is. This touches 2 files or fewer, so per Rule 9.3 skip the GEMINI38 review. Gates: analyze 0, all tests pass, dev only, no live data writes, no deploys. Then pass the baton to GROKCOS for one preview on the fixed channel p7-gate + UX + FT re-gate.

FYI: the PDF fix needs scan_service redeployed before it can work on the preview. That is Grok CoS's job with Eric's YES. Don't deploy it.

Baton is yours: BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md. OVER