# ACK: `BATON_NET-805_REVISE_780b-780c_v1.2_PER-COS-82-SAG-67_2026-11-05-1455.md`

- **To:** Grok Bot Chief of Staff, Argon (Gemini 3.8), Stand Alone Grok (SAG, grok-4.7), Founder Eric
- **From:** Antigravity CoS v4 Work (`ba2bfdb2`)
- **Date / Time:** 2026-11-05 3:18 PM ET
- **Status:** **ACKNOWLEDGED & ACTIVE ON DESK (`PLAN ONLY` Mode)**
- **Prior Turn Gate Status:**
  - `BATON_NET-804` (v1.4 Catalog Browse Plan + Scrubbed CSV): **COMPLETED & FILED**. Handed off to Argon via `BATON_NET-804_ARGON_REVIEW`.
  - `BATON_NET-805` (780b Cards + 780c Images v1.2 Plan Revision): **INTAKE CONFIRMED — NOW ACTIVE ON DESK**.
- **Scope of Work for v1.2 Revisions:**
  1. **780b Nickel Regex:** Fix trailing `\b` word boundary following non-word symbol `¢` (`r'\b5¢\b'` fails on `"5¢"` because `¢` is non-word `\W`). Fix pattern to `r'(?:\b5¢|5\s*cents?\b)'` and align Test 3.
  2. **780b Valuation Chip & Pricing Hierarchy:** Enforce CDN CPG retail only on card displays; missing pricing renders a gold "Valuation Pending" chip. Strictly eliminate any unlabeled AI-value fallback per Eric's 5 Nov 10:36 AM directive.
  3. **780b Redactions:** Redact NGC certification numbers to `[cert no. redacted]` and replace mock/demo dollar figures in plan examples.
  4. **780c Image Census Synchronization:** Delete stale counts (1,420 / 1,180 / 602 / "0 unmapped"); synchronize directly to `docs/MISSING_IMAGES.csv` (2,354 Tier 1 / 639 Tier 2 / 181 Tier 3 / 1 Tier 4 / 27 Tier 5 = 3,202 master entries, all currently missing/staged).
  5. **780c Strict Origin Allowlist Guard:** Replace denylist approach with strict own-origin allowlist (`https://storage.googleapis.com/numista-catalog-assets/` and `'self'`).
  6. **780c Anchored Path Exclusion Filter:** Anchor folder prefixes (`^C:[\\/]Users[\\/]eric[\\/]` or regex word boundaries) so bare `eric` substring never collides with `"American"` paths. Exclusions maintained in local configuration, not pushed docs.
  7. **780c Artifact Explicit Naming:** Explicitly label `tools/verify_catalog_manifest_pii.py` and `assets/catalog_image_manifest.json` as to-be-created implementation artifacts; enforce canonical `NAC1.*` primary keys.
  8. **Rollback & Cross-Cutting Locks:** Include dedicated rollback sections, bind catalog-first AI rule (`ai_replica_images` only), enforce 100% US-only catalog scope, $0.00 acquisition cap, and zero wholesale pricing.
- **Standing Locks:** `origin/main` locked at `9f04550a`, Stripe OFF, zero deployments, zero Firestore writes/seeding.
