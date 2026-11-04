# ACK BATON NET-772: EXECUTE NET-748 v5 (p7-gate Preview Only)
- **Date/Time:** 2026-11-04 4:10 PM ET
- **Station:** AG CoS v4 Work (`ba2bfdb2`)
- **Authority:** Founder Eric typed YES (3:33 PM ET, 4 Nov 2026: *"YES, execute NET-748 v5 to p7-gate preview only"*).
- **Target Plan:** `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/NET-748_v5_PLAN.md` (Attempt 12; SAG 96, Argon 96, 0 must-fixes).
- **Status:** ACKNOWLEDGED & COMMENCED.

## Execution Checklist & Boundary Discipline
1. Fold Argon's 4 implementer notes (`ARGON_REVIEW_NET-748_v5.md`):
   - Note 1 (Test 20 title tokens): Pass matching title tokens in Test 20 (`'Peace Dollar Reverse Proof'`, `'2026 Semiquincentennial President Donald J. Trump $1 Coin 25-Coin Roll'`, `'Silver Proof Set'`).
   - Note 2 (Line 182 / Line 193 placement): Insert `extractSku` fallback after line 193 (after `cleanMint` is computed).
   - Note 3 (SKU names & strings): Match exact strings from `canonical_mint_asset_service.dart:106-123` and `main.py:2197-2200`.
   - Note 4 (Pinned deploy command): Deploy preview using exact pinned command:
     `firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8`
2. Run local Firestore rules emulator test (`firestore.rules.test.js`). If emulator test fails, STOP and file BLOCKED.
3. Strict Locks Confirmed:
   - ZERO Firestore rules deploy (gated on Eric's separate YES naming folder, project, SHA-256, rollback).
   - ZERO Firestore writes.
   - `origin/main` strictly locked at `9f04550a`.
   - Stripe locked OFF.
