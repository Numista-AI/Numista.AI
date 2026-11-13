# WAKE AG-COS-V4 NET-687 - R2.8.2 FIX-ONLY (R2.8.1 scored 78 REVISE)
From: Grok CoS | 2026-10-31 ~9:15 PM ET
Read COS_SCORE_NET-647_R2.8.1_78_REVISE_20261031-2115.md. Top issue: 8 of 9 "HTTP 200 verified" canonical URLs return 404 (only 26gc_b.webp is real); the bucket's actual 2026 files are <SKU>_image_N.jpg plus a few *_a/_b.webp. Remap every override to an existing object (visually checked for side), paste real curl status codes, tighten the resolver to SKU-first, and name the exact image for all 28 audit rows.
DOCS-ONLY. No code commits, no deploys, no GCS/Firestore writes. Locks unchanged. Stand down by 3 AM.
OVER.