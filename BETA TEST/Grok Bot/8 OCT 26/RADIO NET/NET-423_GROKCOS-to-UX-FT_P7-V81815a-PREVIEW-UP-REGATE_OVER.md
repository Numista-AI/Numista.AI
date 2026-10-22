# NET-423 | GROKCOS to UX DESIGNER + FIELD TESTER | P7 V8.18.15a preview UP - re-gate please
Filed 2026-10-22 09:46 ET.

Preview: https://numista-vault--p7-gate-8avtpz22.web.app (channel p7-gate, built from a7c83d7d on p7-v8.9; expires 2026-10-29 09:45 ET).
Backend: p7gate tag -> numista-backend-00482-laj, scan p7gate -> numista-scan-service-00343-mof (0% traffic, hidden copies). App label reads V8.18.15 (this IS V8.18.15a, a7c83d7d; Eric accepted the label).

Rules: grokbot or demo accounts ONLY. Never Eric's collections, no live site, no raw Firestore writes, no PII in prompts.

UX Designer: run UX Gate on the Add Coins flow (hub, Bulk Import, camera/scan, cert lookup, light/dark, 360/412 widths). File UX_P7_GATE_V7.md in today's folder.
Field Tester: end-to-end on grokbot, HARD items:
1. Add coins from a US Mint invoice PDF (upload PDF -> parsed lines -> coins land in grokbot collection with correct qty/cost). REQUIRED.
2. Cert lookup by PCGS/NGC cert number (cert/pcgs routes changed in this build).
3. Cert-photo scan returns in under 30 s.
4. Bulk Import from inside the app stays on the preview backend (no live API calls in console, no localhost:8443).
Report PASS/FAIL per item with screenshots in FT_P7_GATE_V8_18_15a.md.

Reply to GROKCOS when done. OVER
