# BATON — NET-827 — PLAN ONLY — v1.9.2 (from SAG 83 REVISE)
From: Grok CoS · 10 Nov 2026 8:16 PM ET · To: Code Writing (8309c0e0) · Track attempt 6/10, writer try 3/4
Input: v1.9.1 SHA ec9c50b49c4d19d45a4a545b3171b98bb8aeb26761036070c9cadabbde0bfddb
CoS score 100 PASS (record 4d824a91…3797) — CoS missed the three SAG findings below; CoS 100 is not a gate pass on its own.
SAG (API, grok-4.7, resp 4765de99…) 83 REVISE: /workspace/net827-sag-v191/sag-result/SAG_REVIEW_NET-827_v1.9.1_20261110.md SHA 6f45d255…fdfc1 — read it in full.

Fix exactly these; keep everything else byte-identical where possible:
S1 Beta Special must never grant a permanent tier. Add server-set purchase_kind (never from client metadata). Beta grant writes only Beta fields in entitlements + ledger + unlock; never stripe_tier. Ignore/reject client tier on Beta checkouts. Tests: free user sends tier=estate + beta_special -> no stripe_tier; after expiry and after refund -> no paid tier.
S2 Full refund / cancel / lost dispute must null the tier on BOTH users/{uid} and users/{email} (today's webhook writes email doc when no uid, payment_routes.py:206-238). Test that merged profile shows no paid tier afterward.
S3 Import-graph test: main.py:10624 imports scripts/refresh_vertex_data_store.py (prod bucket at line 12). Allowlist or guard it, add it to the file list; test must pass as written.
E1 Eric 7:57 PM ET t2560u "Definitely fix the 'Free Limits' bug": RX is REQUIRED before go-live (not optional). Mark it so; its deploy still needs Eric's own scoped YES under hold 41b8bd5f.
A1 (advisory) Fix wording: checkout_pending cannot hold a Stripe session id before the session exists — state the real write order. Optionally note added_at has no timezone.

Plan only. Return file name, byte size, SHA-256, and a diff summary vs v1.9.1.
