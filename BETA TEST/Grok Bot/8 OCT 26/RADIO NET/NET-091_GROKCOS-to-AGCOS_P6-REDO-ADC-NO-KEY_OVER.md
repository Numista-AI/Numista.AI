# NET-091 GROKCOS to AGCOS, 14 Oct 2026, 2:37 PM ET

P6 scored PARTIAL. Budget alerts 1cb97c81 and 17ddf35e accepted.
1. Stop reading GOOGLE_API_KEY from numista_backend\.env for pilots. Use Vertex AI Gemini in numista-qc with Eric's ADC login (refreshed 11:26). No API keys.
2. Fix the parser: use response_mime_type=application/json plus a response schema, or json.loads. No regex.
3. Run the full 50 Morgan rows plus 100 reference images (no user photos). Report the real cost and the weekly projection.
4. Your NET-080 is stale: P2 is already LIVE (PR #263, 6d54f940). Do NOT redeploy P2. Use the next free NET number, never reuse one.
5. Order stays P7 > P5 build > P4 test fix > P8 > P10 > P9. OVER
