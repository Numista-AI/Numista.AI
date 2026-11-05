# SAG SCORE NET-748 v5 (xAI API, grok-4.7, 2026-11-04 ET)

v4 MF-1 and MF-2 are closed. Quoted lines 101–103, 183, and 186 already lowercase `prog` / `theme` / `title`, `cleanTitle`, and `cleanDenom`; 3.2 lowercases `cond`; 185 uppercases `rawMint` and quoted 187–193 map that to `cleanMint` before `'D'`/`'P'` checks. Test 21, including mint `"d"`, is the right guard. Step 1b pins `--project studio-9101802118-8c9a8`, cwd, SHA-256 of the diffed `firestore.rules`, an emulator STOP before the LIVE YES, and one rollback that deploys the snapshot from that same pin. No new execute-fail or unbound-live defect.

MUST-FIXES:
None

ADVISORIES:
1. Test 20’s “canonical 106–123” cite is still an unquoted summary. Quote the match conditions, or narrow the titles to what those lines actually return, before execute. The STOP is safe, but a miss kills the attempt.
2. Section 3.5 says both “replace line 182” and “after `cleanMint`” (193). Insert the fallback after 193 so it does not use `cleanTitle` / `cleanDenom` / `cleanMint` before they exist.
3. Section 8’s re-read list omits edit sites 73–80, 100, 154, and 182. Section 9 still says to grep `item_type`, which 4.2 already resolved to `'coin'`/`'set'`. Section 4.1 still paraphrases 26XH/26XF/26GC/26RG/26RH/23RG/23RH; copy those strings, do not use the table.
4. Pin `--project` and cwd on `firebase hosting:channel:deploy p7-gate` the same way as 1b. The YES cwd string is `numista_mobile/`; the must-hold pin is the absolute path.

SAG SCORE: 96/100 - PASS
