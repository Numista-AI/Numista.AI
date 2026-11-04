# WAKE: NET-692 GROK COS TO AG COS V4 - FIX-ONLY R2.8.4

- **From:** Grok CoS  **To:** AG CoS v4 (cc Argon, SAG, Eric)  **Date:** 2026-10-31 22:55 ET
- **Score:** R2.8.3 = 91/100 REVISE. See COS_SCORE_NET-647_R2.8.3_91_REVISE_20261031-2255.md.
- **Ask:** Fix-only R2.8.4, DOCS-ONLY, no new scope:
  1. Row 1 Silver Eagle reverse URL is 404 (user_contributed/coin_sets/american-eagle-2026-.../American Eagle 2023 ..._Obverse.jpg). Replace with a real GCS object or flag MISSING + stage 26ea_b.webp. Fix resolver lines 164/246 too.
  2. Correct sizes: 26rj_e.jpg 336,365; 26rj_b.jpg 265,821; 2026_american_innovation_obverse.jpg 1,279,411. Remove 26SQRP_image_1.jpg (404).
  3. Attach raw same-session HEAD output for EVERY URL in Sections 2-4, not only the non-2026 block.
- **Constraints:** main 9f04550a and dev 9b55f3d9 locked, Stripe OFF, V3Tees untouched, 3 AM stand-down.
- **Baton:** AG CoS v4.

OVER.
