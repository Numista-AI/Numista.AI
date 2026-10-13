# NET-039 GROKCOS -> AGCOS: HOTFIX after PR #258 live smoke (URGENT, ahead of F1)
13 Oct 2026, from Grok CoS. Source: FT_SMOKE_UNIFIED_BUNDLE_LIVE.md (CONDITIONAL).

P0 - CORS on /api/spot_prices: the live browser console shows no Access-Control-Allow-Origin header. Likely cause: the default-deny middleware returns 401 on the OPTIONS preflight, or runs before CORSMiddleware. Fix: let OPTIONS pass, and make sure CORS headers are added to every response, including 401s. Check whether spot_prices should be on the public allowlist. Add tests for an OPTIONS preflight on a protected route and for CORS headers on a 401.
P1 - Frontend: live reports v4.403, both the old and the new nav show, and the text is small. Check whether the Flutter web build from PR #258 was built and deployed to Hosting. Report what is actually live.
P2 - Morgan Undo is not offered after a confirmed save (only Undo All and View Binder).
P2 - Repeated Firestore onSnapshot failures plus main.dart.js:4427 errors. These may come from the new server-only rules; check that the app isn't listening to collections it can no longer read.
P3 - The home page renders blank in the FT screenshot. Recheck.

Process: dev only, Gemini BUILD review with the code quoted, then baton T1C_HOTFIX to GROKCOS. Deploy only by cherry-pick, with Eric's YES. F1 (NET-038) goes after this.
