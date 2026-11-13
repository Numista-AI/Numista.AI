# DONE BATON — NET-816 Catalog Chunk 1 Fail-Fix Round 2 — PLAN ONLY
From: AG Chief of Staff v5  
To: Grok Bot CoS (Designated CoS Gate)  
Date: 10 Nov 2026 ~7:20 PM ET  
Delivered Plan: `1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\PLAN_NET-816_FAILFIX-R2_v1_AGCOS-V5_20261110.md`  
Plan Size: 17,156 bytes (258 lines)  
SHA-256: `72d2ecbd85a6d75ddb6445961f9b979dc0ba29dadcd04d99d91d19282cb73b6e`  

---

## Closure of F1–F5 and Technical Notes

| Defect / Item | Status | Resolution in Plan v1.0 |
|---|---|---|
| **F1 Hash Routing (`#/catalog` & `#/catalog/<id>`)** | **CLOSED** | Root cause identified: `main.dart` inspected only `uri.path` (`'/'` under hash URLs) and ignored `uri.fragment`. Fix: inspect `uri.fragment`; if `/catalog` or `/catalog/...`, route directly to `CatalogBrowseScreen` without authentication. (§1) |
| **F2 Catalog Images & CSP** | **CLOSED** | Root cause identified: `firebase.json` CSP headers omitted Wikimedia domains from `img-src` and `connect-src`. Fix: add `https://upload.wikimedia.org`, `https://commons.wikimedia.org`, `https://*.wikimedia.org` to both directives. Documented image gap (1,213 with photos, 1,752 without). Outlined Chunk 2 plan to fill gaps from `gs://numista-reference-library` and Eric's collection photos before placeholders per Eric's 31 Oct rule. (§1) |
| **F3 Multi-Coin Sets Face Value** | **CLOSED** | Root cause identified: `MeltValueService.parseFaceValue` matched `"Dollar"` in `"Dollar (two-coin set)"` returning $1.00. Fix: parse set multipliers (`two-coin set` -> 2x, etc.). Morgan/Peace 2-coin set computes $1.00 * 2 = $2.00 face value. Indeterminate sets display `No face value` chip. (§1) |
| **F4 Stamping `git_commit` in `version.json`** | **CLOSED** | Root cause identified: `flutter build web` generates `version.json` without git metadata. Fix: build script executes `git rev-parse HEAD` and stamps `"git_commit": "<SHA>"` into `build/web/version.json` prior to deployment so Field Tester can deterministically verify commit pin. (§1) |
| **F5 90% Silver Half Dime Melt Verification** | **CLOSED** | Root cause identified: Grokbot test account lacked half dime and catalog detail lacked melt display. Specifications detailed: ASW 0.03617 oz @ current silver spot ($51.51/oz) = $1.86 (rejecting legacy $1.09 estimate). Verification plan: automated unit test in `melt_value_service_test.dart` + calculated bullion melt value displayed on catalog detail dialog + pre-seeded grokbot test coin option requiring Eric's separate YES. (§1) |
| **Note 1: Search Queries Returning 0** | **ANALYZED** | `"1816"`: verified that `catalog_public_v1.json` contains exactly 0 records dated 1816 (historical coinage hiatus after 1816 Mint fire). `"Morgan dollar 1881"`: search filter evaluated as un-tokenized substring; series name `"Morgan Dollar"` does not contain `"1881"`. Tokenized search recommendation documented for Chunk 2. (§2) |
| **Note 2: Coin Search "Server error 500"** | **ANALYZED** | Traced to `CoinSearchScreen` calling `CoinSearchService.search` -> `GET /api/reference/search` (`main.py:9509`). Exception inside `_get_user_owned_doc_ids` or SQLite `definitive_reference` query triggers line 9597 `raise HTTPException(500, detail=str(e))`, rendered by client as `Server error 500`. Traced and documented. (§2) |

---

## Authority & Compliance
- STRICTLY PLAN ONLY: Zero code execution, zero commits of source code, zero deploys, zero Firestore/Stripe writes.
- Branch `p7-v8.9` pinned at `49e77cf7`; `main` strictly pinned at `9f04550a`.
- HOLDs `74611e05` and `41b8bd5f` remain in full effect.
- Passed to Grok Bot CoS for designated CoS gate scoring.
