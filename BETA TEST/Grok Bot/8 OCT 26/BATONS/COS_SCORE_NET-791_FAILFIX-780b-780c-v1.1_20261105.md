# GB CoS SCORE — NET-791 / FAILFIX_PLAN_NET-780b_CARDS_v1.1 + FAILFIX_PLAN_NET-780c_IMAGES_v1.1

- **Scorer:** Grok Bot Chief of Staff (GB CoS scorer executor)
- **Date / Time:** 2026-11-05 ~2:45 PM ET (America/New_York)
- **Targets:** `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.1.md`, `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.1.md`, `RADIO NET/ARGON_REVIEW_NET-780_FAILFIX_v1.1.md`
- **Mode:** SCORE ONLY — read-only repo checks, no deploy/merge/Firestore, no messages
- **Argon Score (prior):** 96 / 96 PASS
- **CoS Score:** **82 / 100 (`FAIL`)** — 780b 88, 780c 76
- **SAG Score (grok-4.7 via xAI API, key never printed):** **67 / 100 (`FAIL`)** — 780b 72, 780c 61
- **Eric YES gate:** **BLOCKED.** Revise baton **NET-805** filed to AG CoS v4.

---

## 1. Verified against the repo (p7-v8.9 working tree, read-only)

**780b holds up well on citations:** `canonical_mint_asset_service.dart` lines 27 (`hasUserUploadedPhotos`), 54 (`_mintBase = '$_base/us_mint_official'` — internal, not a hotlink), 72 (`_normYear`), 156, 433 (mojibake regex); `my_collection_screen.dart` 3017 `final valCpg = _parseNumber(m['cpgRetail']);`, 3170, 3178 `'Valuation Pending'`, 6377; `add_coins_hub.dart:117` `kFallbackUsMintSkus`; `test/services/canonical_mint_asset_service_test.dart` exists. MF-B1 and MF-B3 closed.

**Problems found:**

| # | Plan | Quote | Reality | Severity |
|---|---|---|---|---|
| 1 | 780b §4.B | `RegExp(r'\b(5c|5¢|five cents?|nickel)\b')` | `¢` is a non-word char, so the trailing `\b` never matches bare "5¢"; Test 3 would fail | must-fix |
| 2 | 780b §4.C | `final finalVal = valCpg > 0 ? valCpg : valAi;` | Unlabeled AI-value fallback on the card. Eric 5 Nov 10:36 AM: CDN CPG retail; don't prefer AI over CDN. Show chip when CPG missing, or label AI explicitly | must-fix |
| 3 | 780b §3.A | `"Certification Number": "[cert no. redacted]"`, `"AI Estimated Value": "$95.00"` | Real-looking NGC cert number quoted in a pushed doc; demo-record provenance not stated → redact | must-fix |
| 4 | 780c §3.2 | "Catalog Master Index 3,202 … 1,420 / 1,180 / 602 … 0 unmapped" | `docs/MISSING_IMAGES.csv`: all 3,202 rows MISSING / EXTERNAL_MIRROR_PENDING; tiers 2,354 / 666 / 181 / 1 | must-fix (invented census) |
| 5 | 780c §3.5 | `(?i)(aj|invoice|receipt|packing|microscope|user_upload|eric)` | Unanchored: `eric` hits "Am**eric**an" — 578 of 8,945 paths in `inventory_20261031.csv`; `aj` hits Ajax/Majestic | must-fix |
| 6 | 780c §4 | `if (url.startsWith('https://upload.wikimedia.org') || url.startsWith('https://numismatics.org'))` | Denylist; any other external host still fetched/hotlinked. Needs own-origin allowlist | must-fix |
| 7 | 780c §5 | "Run `python tools/verify_catalog_manifest_pii.py`"; `assets/catalog_image_manifest.json` | Neither file exists — say "create" | must-fix |
| 8 | 780c §3.4 | `"nac_code": "USA-1C-1909-S-VDB"` | Master/CSV format is `NAC1.BN.US....` | must-fix |
| 9 | both | — | No rollback section in either plan | must-fix |
| 10 | 780c §3.5 | lists [named personal/AJ folders] | Exclusion list in a repo doc names AJ/Eric folders; move to a local prefix config (SAG) | advisory |

Checklist: plan-only PASS; `origin/main` 9f04550a PASS; Stripe OFF PASS; Firestore separate YES PASS (stated "zero Firestore writes"); no-hotlink **PARTIAL** (denylist); AI-never-primary **NOT STATED** (add fence for `numista-uploads-studio` AI test renders); CPG-only **FAIL** (#2); US-only not stated; $ cap $0 implied, not stated; tests PARTIAL; Thanksgiving fit: card pending chip + closed CSP fallback are launch-useful, bulk mirror is not a launch blocker.

**CoS breakdown:** 780b (citations 25/25, fixes 20/25, values rule 13/20, PII 15/15 −2 cert, rollback/tests 10/15 → 88 after −2 cert); 780c (citations 14/25, PII gate 14/20, no-hotlink 14/20, license/manifest 16/20, rollback/tests 8/15 → 76). Combined ≈ **82 FAIL**.

---

## 2. Must-fixes for v1.2 (CoS + SAG merged)

1. 780b: fix nickel regex (e.g. `(?:\b5c\b|5¢|\bfive cents?\b|\bnickel\b)`) and Test 3.
2. 780b: CPG retail only on cards; missing/≤0 → gold "Valuation Pending" chip; no unlabeled AI / melt / issue / purchase value as "value".
3. 780b: redact cert `[cert no. redacted]` and demo $ figures from the plan.
4. 780c: replace the census with numbers that match `docs/MISSING_IMAGES.csv` (2,354 / 666 / 181 / 1) or cite a real match report.
5. 780c: own-origin **allowlist** guard (`'self'`, `storage.googleapis.com/numista-catalog-assets`, data:, blob:) — everything else → placeholder, no fetch.
6. 780c: anchored folder-prefix excludes (no bare `eric`/`aj` substrings); keep the list in a local config, not a pushed doc.
7. 780c: mark `tools/verify_catalog_manifest_pii.py` and `assets/catalog_image_manifest.json` as to-be-created; use `NAC1.…` keys.
8. Both: rollback section (branch revert; GCS copy-only, manifest-reversible; preview channel before live).
9. Both: one line each — AI images only in `ai_replica_images`, never primary/card/index; US-only intake; $0 spend cap; no wholesale.

---

## 3. SAG Result (independent; grok-4.7)

```
## SAG_SCORE: 67/100 FAIL
## MUST_FIX (ordered, blocking before Eric YES; or 'NONE blocking')
1. 780c census is false against the file it cites (fact 12). Delete Tier1 1,420 / Tier2 1,180 / Tier3 602 and “0 unmapped.” `docs/MISSING_IMAGES.csv` is 3,202 rows, all obverse MISSING or EXTERNAL_MIRROR_PENDING, tiers 2,354 / 666 / 181 / 1 (NET-803 v1.3). Collection 284/28/41 and “0 missing” is not CoS-verified and contradicts the broken-card audit — remove it or cite row evidence.
2. 780c image guard is a denylist, not an allowlist (fact 13). It misses `thumb.wikimedia.org` and every other external host, so `Image.network` still hotlinks and can still throw CSP errors. Allow only own origins already in CSP (`storage.googleapis.com` catalog-assets, `'self'`, data, blob). Blank every other URL in memory before fetch. No Firestore image-field writes under this YES.
3. 780c PII regex is unsafe (fact 11). Unanchored `eric` matches `American` (578 of 8,945 paths); `aj` matches Ajax/Majestic. Use exact folder-prefix excludes only. `tools/verify_catalog_manifest_pii.py` and `assets/catalog_image_manifest.json` do not exist (fact 10) — say “create,” do not “run” them as if present.
4. 780b valuation breaks the 5 Nov rule (fact 6). Display CDN `cpgRetail` only. If it is missing or ≤ 0, show the gold “Valuation Pending” chip only. Do not fall back to AI value, melt, issue price, or purchase price, and do not leave an unlabeled AI number on the card.
5. 780b nickel regex will fail its own test (fact 5). `\b` after `¢` does not match bare `5¢`. Fix the pattern and Test 3. Do not map a 2023 nickel to 2026 Semiquincentennial art. Cite a real internal asset path; do not invent a filename.
6. Neither plan has rollback (facts 8, 15). Add branch-only revert: no `origin/main` move off `9f04550a`, Stripe stays OFF, no Firestore rules/writes without a separate YES, GCS is copy-only and reversible by manifest, no deletes.
7. 780c example id `USA-1C-1909-S-VDB` is not the master format (fact 14). Keys and manifest must use `NAC1.BN.US....` or catalog joins fail.
8. Redact PII from both plan texts before any further push: NGC cert `[cert no. redacted]`, `$95.00`, melt `$23.40` (fact 7, provenance unstated), and the AJ / Eric folder names and name tokens in 780c. Keep excludes on a local prefix list, not spelled into a repo doc.
9. State the catalog-first fence: AI test renders and user uploads stay in labeled `ai_replica_images` only, never primary, card, or index. Do not ingest `numista-uploads-studio` into `gs://numista-catalog-assets` on this YES. Intake is US-only (current and former states, territories, possessions), coins/notes/currency, hard spend cap $0.
10. Name the 26 Nov 2026 cut for landing `numista.ai` (US-only Meta ads): card pending-chip + closed-CSP fallback only. Bulk mirror of 3,202 images is not authorized by this YES and is not a launch blocker.
## NON_BLOCKING
- CSP citation `firebase.json:275-276` and inventory row counts (8,945 and 11,069) match facts 9 and 16. Closing the Wikimedia CSP bridge is the right call. `storage.googleapis.com` is already allowed; do not depend on the unverified `numista-vault.web.app` rewrite.
- `3936ba5f` docs-backup story is not in the CoS fact file. If it stays docs-only, it does not move `origin/main`.
- Year-from-text can grab the wrong year when several years appear; prefer an explicit Year field, then one unambiguous match.
- License `source_url` may be stored for compliance. UI credit must be plain text, not a clickable outbound link.
- Owner “Cost:” subtitle must never appear on catalog, social, or ad surfaces, and must never be labeled as value.
## PII_FINDINGS
- 780b quotes a real-looking NGC certification number `[cert no. redacted]` plus `$95.00` and melt `$23.40` from `guest_demo_coins.json`. CoS fact 7: provenance not stated. Treat as a possible ownership id until proven synthetic. Remove from the plan.
- 780c writes user/founder identifiers into the plan and the filter: `[personal folder]`, `[personal folder]`, `[personal folder]`, `[personal folder]`, and regex tokens `aj` and `eric`. That violates no-AJ / no-name. The same regex also false-hits ordinary “American” paths (578) and names like Ajax/Majestic (fact 11).
- No street address is in either plan. Collection value would still hit the card if the AI-value fallback ships (fact 6). Microscope, receipt, and invoice paths (109) are correctly out of scope, but the filter as written does not prove a real 0-hit.
## 3_SENTENCE_PLAIN_ENGLISH (for founder Eric, plain words)
Do not type YES yet. The card plan would still show an AI price when the CDN retail price is missing, and the nickel image check is written so it fails. The image plan uses counts that do not match the missing-images file, a privacy filter that would drop hundreds of normal “American” pictures, and a block-list that still lets other outside picture links through.
## RATIONALE (brief)
Sub-scores: 780b cards 72/100 FAIL; 780c images 61/100 FAIL. Combined 67 because one YES covers both, and 780b’s card images depend on 780c’s URL guard. CoS facts override the plans and Argon’s 96: facts 5, 6, 8, 11, 12, 13, 14, and 15 are unmet, so this is not a ≥95 gate. Locks that do hold: plan-only wording, `origin/main` @ `9f04550a`, Stripe OFF, CSP left closed, bucket pinned to `gs://numista-catalog-assets`, no invented $95 issue price. Those do not offset a false census, a broken PII gate, hotlink leakage, a CDN-CPG violation, or missing rollback.
```

---

## 4. Three-Sentence Plain English (CoS, for Eric)

The card fix is mostly right and its code quotes check out, but its nickel check is written so it can't match "5¢", and it would quietly show an AI price on a card when the CDN retail price is missing. The image plan's coverage numbers don't match our missing-images list, its privacy filter would throw out every picture with "American" in the name, and it only blocks two outside image sites instead of allowing just our own storage. I sent both back to AG for a v1.2 — nothing for you to approve yet.

## 5. Next Actions (no execute)

1. **AG CoS v4:** take **BATON_NET-805** → v1.2 of 780b and 780c clearing §2. Then Argon → GB CoS → SAG → Eric.
2. Priority: after NET-804 (catalog v1.4, Thanksgiving critical path).
3. Locks unchanged: `origin/main @ 9f04550a`, Stripe OFF, zero deploys, zero Firestore writes.
