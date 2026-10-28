# NET-640 EXECUTE_DONE — Phase I afternoon (Catalog Research)

**Filed:** 2026-10-28 12:49 ET (America/New_York)  
**Status:** **EXECUTE_DONE**  
**Project:** `numista-morgan-pilot`  
**Window:** 12:30–4:00 PM ET · resumed after ADC re-auth (same YES; not a second burn)

## BLUF
Phase I WP0–WP6 complete inside ceiling. **ESTIMATE $0** list Discovery spend (inline ~22.5 KiB text under 10 GiB free index band; engine attach-only; 7 Enterprise Search smokes). **No Layout Parser. No Check Grounding. No fold. Adv Answers OFF.** FinOps please confirm App Builder promo actuals.

## Dollars vs $60
| Item | Amount |
|---|---|
| Ceiling | ≤ **$60** Phase I / $60 day |
| 80% abort line | ~$48 |
| **ESTIMATE spent** | **$0.00** (not billing actual) |
| Layout Parser | $0 (not used) |
| Check Grounding | $0 (forbidden this YES) |
| Remaining headroom | ~$60 |

## SKUs touched (ESTIMATE)
1. Vertex AI Search / Discovery — unstructured document index (inline import)
2. Vertex AI Search — Enterprise Search queries (smoke only)
3. Discovery Engine — create engine `morgan-pilot-blended` (existing stores attach; no re-ingest)

## WP results
| WP | Result |
|---|---|
| WP0 | ADC_OK; stores morgan-docs / morgan-factcheck / smithsonian-nnc / usmint-site; engines listed |
| WP1 | 8 prep JSONL → morgan-docs inline (FG-590-16/17/19, FG-589-15) |
| WP2 | 3 prep JSONL → morgan-docs (FG-588-06, FG-588-10) |
| WP3 | 7 prep JSONL → morgan-docs (FG-586-01/02/03/05, FG-588-09, FG-590-18); skip FG-586-04 |
| WP4 | 4 prep JSONL → morgan-docs (FG-589-11..14) |
| WP5 | Single-store engines cannot add stores; **created** `morgan-pilot-blended` = morgan-docs + smithsonian-nnc (attach only). Preexisting `morgan-factcheck-blended` already had NNC. Observability set OFF on new engine. |
| WP6 | 3 primary smokes (+ Franklin check) — **all phase1_hit=True** on morgan-pilot-search and blended |

## Doc / engine counts
- **morgan-docs:** 114 → **136** listed (+22 Phase I excerpts)
- **Engines:** morgan-pilot-search [morgan-docs]; morgan-factcheck-search [morgan-factcheck]; morgan-factcheck-blended [morgan-factcheck, smithsonian-nnc]; **morgan-pilot-blended [morgan-docs, smithsonian-nnc]** (new)

## FAIL rows now searchable (Enterprise Search; not CG-gated)
- FG-586-01
- FG-586-02
- FG-586-03
- FG-586-05
- FG-588-06
- FG-588-09
- FG-588-10
- FG-589-11
- FG-589-12
- FG-589-13
- FG-589-14
- FG-589-15
- FG-590-16
- FG-590-17
- FG-590-18
- FG-590-19

**Attach-path (smithsonian-nnc via blended):** FG-588-07 Porthole, FG-588-08 Chief — searchable on blended engines; not re-ingested.  
**Skipped:** FG-586-04 (already SUPPORT); FG-590-20 optional Tier B.

## Smoke hits (top)
- Fugio/NNP → `wp3-fg-586-05-device-specs`, `wp3-fg-586-01-…`, `wp3-fg-586-03-abel-buell` (+ NNC Fugio on blended)
- Mint AR 548,000 → `wp1-fg-590-16-ar1922-cy1921-sf-half`
- Franklin 2,876,381 → `wp1-fg-590-17-ar1956-table15-phil-half`
- BEP/FR → `wp2-fg-588-06-…watermelon`, `wp2-fg-588-10-…frbn-vs-frn`

## Artifacts (box)
- `/workspace/catalog-research/ingest/INGEST_MANIFEST_EXECUTE_NET640_2026-10-28.json`
- `/workspace/catalog-research/ingest/logs/SMOKE_QUERY_LOG.md`
- `/workspace/catalog-research/ingest/logs/IMPORT_WP1-4_RESULT.json`
- `/workspace/catalog-research/ingest/NET640_BLOCKED_THEN_RESUME_AUTH_20261028.md`

## Ask next (NOT this YES)
Separate Eric YES for **Phase I-C Check Grounding Option A ≤ $0.50** (19 FAIL re-gate; Adv Answers OFF; fold still HOLD).

---
Catalog Research · NET-640 · EXECUTE_DONE · afternoon 28 Oct 2026
