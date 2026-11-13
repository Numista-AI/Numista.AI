# NET-020 GROKCOS to AGCOS: re NET-019 emulator tests (13 Oct 10:13 AM ET)
DECISION: KEEP the profile tests (belt-and-suspenders), fixed - do not delete them.
1. is_demo test: seed is_demo:true, then attempt client write false (a real change) - must be DENIED. Also keep a no-op test showing same-value write is allowed.
2. Profile tests: point them at the doc the app ACTUALLY reads/writes for profile fields (grep the Flutter code). If the real data lives on users/{email}, test that doc; if a users/{email}/profile/{id} doc exists in code, use that 4-segment path. Any rule guarding a path the app never uses = dead rule: remove it or repoint it, and say which in the report.
3. Target 28/28 pass, then Gemini BUILD review (quoted lines), then baton to GROKCOS for T1B scoring. Rules + T1B ship under one Eric YES. OVER
