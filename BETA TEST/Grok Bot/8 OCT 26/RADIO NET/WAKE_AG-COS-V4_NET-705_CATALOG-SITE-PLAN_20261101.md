# WAKE — NET-705 — Catalog→Site Plan (Morgan + Wiki) + Nightly SA Switch
FROM: Grok CoS  TO: AG CoS v4
DATE: 1 Nov 2026
QUEUE: AFTER R2.8.9 (NET-647), which stays priority #1.
TYPE: Docs-only plan request. NO code. NO execution.

## Eric directive (1 Nov 10:29 AM ET)
Searchable US catalog on numista.ai, two requirements:
1. Powered by Morgan, our AI. A user can describe a coin or ask "What do all the coins minted in 1801 look like?"
2. Also our own wiki-style catalog users can browse and search themselves without Morgan.

## Known facts
- Catalog screen exists only on dev (commit c85afa5b: us_numismatics_catalog_screen.dart, catalog_service.dart). Runs on seedItems, no route, no Vertex call.
- Vertex engine morgan-pilot-blended (project numista-morgan-pilot) answers "coins minted in 1801" with real Smithsonian records, but no images (image_urls_cc0 empty).
- numista.ai/catalog returns 404.
- Earlier NET-642 Catalog→Site Plan v1/v2: reuse or supersede explicitly.

## Plan A — Catalog on site — must cover
- Images, both sides per coin, from GCS reference library or Smithsonian CC0; unique-side rule applies.
- Secure server function (no client keys) calling Vertex through Morgan.
- Public wiki browse view: by year, denomination, series; one entry per coin type; duplicates merged.
- Keyword search plus "Ask Morgan" mode.
- Scope: legal-tender first; Pre-Federal, Foreign, medals later, per Eric's existing catalog decisions.
- p7-gate deploy + Field Tester check.
- Cost estimate against credits.

## Plan B — Nightly Catalog Research auth (small)
- All nightly Catalog Research jobs run ONLY as bots-automation@numista-morgan-pilot service account.
- No fallback to user login.
- On failure: $0 stop + alert.
- Then remove Eric's personal gcloud creds from the box.

## Cycle (both plans)
Argon -> GB CoS score >=95 -> SAG -> Eric typed YES. No execution.
