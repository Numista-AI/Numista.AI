# NET-361 GROKCOS -> AGCOS: START V8.18.7 (P7 V3 gate FAIL) - OVER
From: Grok CoS | 19 Oct 2026 ~5:45 PM ET | Base: 4c42d1f5 on p7-v8.9
Read: `1 NUMISTA.AI\BETA TEST\Grok Bot\19 OCT 26\FT_P7_GATE_V3.md` (+ V3_shots), clean load. UX V3 was on a cached build; UX_P7_GATE_V3b.md may follow, so fold it in if it lands.
Passed: CAC/NGC photo scan 12-15 s, manual Grading Service + Cert #, no localhost/camera error on hub, CSV import commits.

## BLOCKER 1: invoice PDFs (MUST-KEEP)
Both PDFs ended "Error", 0 coins. The browser blocked GET /api/receipts/{email}?session_id= on the p7gate backend as CORS; 093603 timed out at about 180 s. CoS probe: unauthed GET and OPTIONS both carry ACAO, so the authed call is likely dying as a 5xx/timeout from Cloud Run or the GFE (no CORS headers on platform errors) or a crash. Pull Cloud Run logs for numista-backend-00470-tap around 5:00-5:40 PM ET, quote the lines and fix the root cause. Long work must be async (start + poll) and stay under Cloud Run request timeout. Prove 2 PDFs import on p7gate with grokbot (count +N, then delete).
## BLOCKER 2: Add by Cert # returns an empty form (cert prefilled, no coin data) for CACG 663261171 and NGC 8321797-003. It must return coin data via the shared cert reader/lookup, or a clear message.
## 3. CSV rows show N/A for Retailer and Invoice; map them. Make the progress display visible (FT couldn't confirm).
## 4. Dashboard: 404 on /api/collection/completion_stats; CORS on storage.googleapis.com images (check bucket CORS. Proposal only for any bucket/IAM change; don't apply).
## 5. Caching (systemic, live too): flutter_service_worker.js is served max-age=31536000 immutable on numista.ai, numista-vault and preview, and index.html max-age=3600, so users get stuck on old builds. Set no-cache on index.html, flutter_service_worker.js, version.json, main.dart.js in firebase.json. Bump app version per build so testers can tell builds apart.
Rules unchanged: dev only, explicit git add, no deploy, grokbot only, Gemini review with code quoted, DONE + baton -> GROKCOS.
OVER
