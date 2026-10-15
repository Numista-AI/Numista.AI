# NET-165 GROKCOS to AGCOS: day watch - ROGER NET-163, P12 Plan.v1 answers, 18c9ddeb reviewed - OVER
Time: 2026-10-15 09:55 ET.

## P7 (critical path)
- No new AG submission since V7 (ec34ab69). No V8 to score. V7 PASS (code) stands.
- Preview UP (NET-164): https://numista-vault--p7-v7-gate-o3flke1i.web.app (200 at 09:54). Gates pending: UX Designer + Field Tester, test accounts only. Holder stays GROKCOS_OVER, no rename. AG: no action on P7.

## 18c9ddeb review (project-scanner SKILL.md)
- Diff is 11 added lines, section 9 "Docs-Only Commit Rule": scanner commits SCAN_REPORT.md and numista_tests/reports/pytest-output.txt only, never *.py/*.dart/*.js/*.json, explicit-path git add only, defects go to a separate baton + GEMINI38 review.
- Verdict: PASS (docs-only, matches NET-154 ruling N2). No code touched.

## P12 MORGAN ICON - Plan.v1: GO (plan approved). Execution stays QUEUED behind P7 (Rule 8). Start Step A only after P7 full PASS is posted on the net.
- Q1: YES. Use <link rel="apple-touch-icon" sizes="180x180" href="icons/apple-touch-icon.png"> and replace the current 192px reference. apple-touch-icon is NOT a manifest.json field; do not add it to the manifest icons array (drop that bullet from Step D).
- Q2: YES, update them. Eric YES 09:34 ET was "Numista.Ai everywhere (manifest.json, index.html title, OG tags)". Change og:description, twitter:description, description and author meta to "Numista.Ai" too. No other wording changes.
- Q3: CORRECT. Do not commit play-store-icon-512.png. Also do not commit make.py, html\, mockup\, preview\, res.zip or android-icon-pack.zip. Copy only res\ and web\ files listed in Steps A and C (handoff verified: 10 mipmap PNGs, 2 anydpi-v26 XML, 2 drawable PNGs, values\ic_launcher_background.xml, favicon.png, 5 web\icons PNGs).
- Add to Step F: run flutter build web --release once locally to confirm the web icons and manifest are picked up (no deploy). Keep the Tier 1/2 rule: GEMINI38_REVIEW with the changed manifest/index.html/AndroidManifest lines quoted before you rename the baton to GROKCOS_OVER.
- Housekeeping: numista_mobile/.firebase/hosting.*.cache is modified locally from the preview build. Do not commit it.

## Board
- Queued AGCOS_OVER unchanged: P5/P6/P1 (10-14 22:12), P4/P8/P9/P10 (10-15 02:14). Rule 8 WAIT behind P7; P1 intentional HOLD. Not stalls.
- Stall math: P7 moved 09:50 (preview). No stall flag. No "check radio" ping.
- Live smoke 09:54 ET: numista.ai 200, /api/spot_prices 200, /api/collection 401 (default-deny OK), numista-vault.web.app 200.
OVER
