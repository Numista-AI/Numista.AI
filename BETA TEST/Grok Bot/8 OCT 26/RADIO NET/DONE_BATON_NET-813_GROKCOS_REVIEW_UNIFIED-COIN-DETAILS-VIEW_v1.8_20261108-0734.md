# BATON NET-813 — GROKCOS REVIEW — UNIFIED-COIN-DETAILS-VIEW v1.8

- **Writer:** GB CoS fresh writer (writer-cap rule; AG CoS v5 `cfe23a7a` exhausted 4/4). Eric GO Sun 8 Nov 07:27 ET.
- **Plan:** `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.8.md` — 78716 bytes, SHA-256 `76c94e725475fcc0f0a08b5cbbe5c3f77a5698333bd062c6dcd45c2363566655`
- **Filed:** Sun 8 Nov 2026 07:34 ET
- **Mode:** PLAN ONLY. No code edits, no Firestore, no deploy, no push to main (locked `9f04550a`). Stripe OFF. Alerts only, never caps. No PII.
- **Writer self-score (not independent; needs GB CoS scorer pass, then SAG, then Eric typed YES):** 95/100

## Changes (only the CoS remaining defects)
D1 A4.1 labels 464–467 / 77–82 (origin/dev bde8b402); D2 Test 11 uses setDoc + reset, widget _loadCurrentDoc reads via getDoc, asserts readCount>=1 & writeCount==0; D3 fromCoinModel/Test 12 use real CoinModel fields (personalRef NAC-only, metalContent), no storageLocation on guest, redaction assertions can fail; D4 §6.5 loader reads harness.clock via 250ms watchdog, Test 13 uses non-manifest key and asserts 'Founding legislation details pending verification.'; D5 public UnifiedCoinDetailNavState with @visibleForTesting getter. See plan top table. Residual (not in must-fix list): fromCatalogMap reads m['primary_image_url'] while catalog key is primary_image (object) — flag for scorer.
