# NET-497 FT-to-GROKCOS: P7 V8.18.15i QTY gate — PASS (with caveat) — OUT
Field Tester, 24 Oct 2026 ~6:25 PM ET. grokbot only. Preview only (not live). Argon PASS NET-494. Label still v8.18.15h (NET-492 lock OK). Backend confirmed p7gate---numista-backend (00487-hub path).

BLUF: OVERALL PASS for gate criteria. QTY=2 one-row fix works. Live YES still held separately. Caveat: importer showed red "Invalid char in element with leading alpha: Retailer/Website" after Done — rows still landed.

| Check | Result | Evidence |
|---|---|---|
| Backend = p7gate not live | PASS | upload/process/status all to p7gate---numista-backend |
| 092052 no 60s timeout | PASS | ~2.5 min, Done ✓ 14 coins |
| ~14 rows / 17 coins | PASS | Hub 114→128 (+14) |
| 1964-D / 1982-S / 2001-P QTY=2 single row | PASS | each one row Quantity 2 |
| Per-page inv # / date | PASS | p1 67000011 / 2024-11-07; p2 67226944 / 2025-01-23 |
| Review Hub commit | PASS | 1936-S Buffalo "Added 1 coin.", 316→317 |
| Manual duplicate | PASS | "flagged as possible duplicate", 317→318 |

Caveat: importer error banner after success (Invalid char… Retailer/Website). Did not retry.
Counts: START 316 / Hub 114; END 318 / Hub 127. Added: 1936-S Buffalo, 2026-D FT-TEST 15i dup. 13 invoice rows uncommitted. No deletions.
Shots: NET-497_shots\
