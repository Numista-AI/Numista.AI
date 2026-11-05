# BATON NET-807 - To: AG CoS v4 - PLAN ONLY: NET-801 Soft-404 / Public Catalog / Pricing v1.1 (CoS 78 / SAG 52 FAIL)
Source: GB CoS ~2:55 PM ET 5 Nov. Argon 96; CoS **78 FAIL**, SAG **52 FAIL**. Score file: `COS_SCORE_NET-801_SOFT404-PUBLIC-CATALOG-PRICING_20261105.md`. **Take after NET-804; align with catalog v1.4.**

Fix:
1. Live `/catalog` is **200** today (and `/catalog/foo`); 404 page is 3,379 B. Strike the 404 premise; rebase on `dev`'s existing catalog screen + `/catalog` rewrites (NET-747/768, NET-777) — no duplicate screen.
2. Replace `5,142` with cited 3,202 (or a cited newer count); remove "World"; reconcile the front-door badge.
3. Delete unsourced `99.4%`, "advisory board", "Sheldon grading", "100% Private & Secure", "Passport Protocol" unless cited.
4. Public card fields: CDN CPG retail only, no wholesale, no user value/ownership; AI images only in `ai_replica_images`; no hotlinks/outbound links.
5. Real anchor/`Link` widget for footer/Pricing; AuthGate must await auth restore.
6. Static per-route title/OG for non-JS crawlers on the ad landing `numista.ai`.
7. Rollback + preview channel + $0 cap; `test/route_test.dart`, `test/auth_gate_test.dart` are to-be-created.
8. All of Options A/B/C need Eric's typed YES (fix "standard plan cycle" on C).
**Plan A caps apply.** Locks unchanged: `origin/main` `9f04550a`, Stripe OFF, zero deploys, zero Firestore writes, no PII, no AJ data. PLAN ONLY — no execute/deploy/merge without Eric's separate YES.
**Chain:** AG files revision → Argon → GB CoS (95+) → SAG (95+) → Eric typed YES.
