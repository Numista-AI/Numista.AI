# NET-335 GROKCOS -> AGCOS: V8.18 ADDENDUM (with NET-334) - OVER

From: Grok CoS  |  19 Oct 2026 ~9:42 AM ET  |  Source: FT full report `1 NUMISTA.AI\BETA TEST\Grok Bot\19 OCT 26\FT_P7_GATE.md` (+ FT_P7_GATE_shots\)
P7 gate on dbda922f = FAIL. Read the FT report before starting.

## Must fix in V8.18
1. NET-334 brace fix + systemic `node --check` of all web/*.html scripts + test step.
2. PDF INVOICE PATH (MUST-KEEP capability per Eric): "Run High-Speed Parallel Batch" does nothing, and the only PDF path is the dead add_coins.html. After the brace fix, confirm an invoice PDF imports end-to-end on p7gate with grokbot. Note: Document AI checklist processor versions were undeployed today; invoice scanning must not depend on them. Confirm which path invoices use.
3. CAC slab photo ID hang (1952 nickel): find the cause; add a timeout with a plain-English message.

## Investigate + report (fix if small)
4. Backup count: export holds 314 records, the app shows 312 for grokbot. Explain the 2 (soft-deleted? duplicates?). Do not delete anything.
5. Backup JSON says app_version 4.339; it should match the current build version.
6. Manual entry has no Grading Service / Cert # fields (NGC, PCGS, CAC, CACG). Eric wants NGC + CAC certs recorded. Give a scope estimate; build only after CoS score.

## Rules unchanged
Dev only, explicit git add paths, no deploy, grokbot only, no writes to Eric's collections. DONE + baton back to GROKCOS.
OVER
