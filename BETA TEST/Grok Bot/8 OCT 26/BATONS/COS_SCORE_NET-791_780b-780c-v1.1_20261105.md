# GB CoS SCORE — NET-791 / FAILFIX NET-780b Cards v1.1 + NET-780c Images v1.1

- **Scorer:** Grok Bot Chief of Staff (GB CoS scorer executor)
- **Date / Time:** 2026-11-05 ~2:20 PM ET (America/New_York)
- **Targets:** `FAILFIX_PLAN_NET-780b_CARDS_v1.1.md`, `FAILFIX_PLAN_NET-780c_IMAGES_v1.1.md`, `ARGON_REVIEW_NET-780_FAILFIX_v1.1.md` (Argon 96 / 96)
- **Prior:** 780b v1.0 CoS 88 FAIL; 780c v1.0 CoS 80 FAIL
- **Mode:** SCORE ONLY — no execute / deploy / merge / push / Eric ping
- **CoS Score (780b):** **96 / 100 (`PASS`)**
- **CoS Score (780c):** **96 / 100 (`PASS`)**
- **CoS Composite NET-791:** **96 / 100 (`PASS`)**
- **Argon:** 96 / 96 / composite 96
- **SAG Score (this turn, grok-4.7 via xAI API):** **83 / 100 (`FAIL`)**
- **Eric YES gate:** **BLOCKED** by SAG FAIL (83). CoS PASS alone does not authorize YES.

---

## 1. CoS Checklist

| Check | 780b | 780c | Notes |
| :--- | :---: | :---: | :--- |
| Plan-only; main `@ 9f04550a`; Stripe OFF | PASS | PASS | Explicit |
| Firestore writes/rules separate YES | PASS | PASS | Zero Firestore writes stated |
| No AJ / user PII | PASS | PASS | 780c lists AJ folders as **exclusions** only; 0-hit proof required at ingest |
| No hotlinked / outbound images | PASS | PASS | **MF-C1:** CSP bridge deleted; Wikimedia never added to CSP |
| AI replicas only in `ai_replica_images` | N/A* | PARTIAL | *Cards track is vault images; 780c should cross-cite NET-803 §2.B catalog-first rule for any catalog mirror path |
| Nothing invented | PASS | PASS | Dropped invented $95 issuePrice; commit `3936ba5f` explained (0 code lines, auto-backup docs) |
| $ cap | ADVISORY | ADVISORY | Neither plan restates hard $ cap — **inherit NET-803 §2.E $25/$20** for same `gs://numista-catalog-assets` bucket (non-blocking if 803 YES precedes or is cited at execute) |
| Rollback + preview-before-live | ADVISORY | ADVISORY | Inherit NET-803 §8; 780c should name preview before live mirror cutover |
| Tests | PASS | PASS | Unit path fixed to `test/services/...`; CSP 0-error / PII 0-hit acceptance |
| Thanksgiving Meta ad fit | PASS | PASS | Broken cards + CSP console noise would hurt ad landing trust; closed CSP is required |

**780b breakdown:** MF-B1..B4 closeout (35)=34; locks (20)=20; year-from-text + user-photo guard + nickel safety (25)=24; commit explanation + tests (10)=10; launch/advisories (10)=8. **Total 96.**

**780c breakdown:** MF-C1..C6 closeout (40)=39; locks/no-hotlink (20)=20; inventory citations verified by Argon (15)=14; PII exclusion manifest (15)=14; $cap/rollback inherit gap (10)=9. **Total 96.**

### Must-fix closeout

**780b MF-B1..B4:** PASS — no `issuePrice` on `kFallbackUsMintSkus`; no invented $95; Valuation Pending chip; purchase/cost never in valuation slot; CPG preferred over AI when CPG>0.
**780c MF-C1..C6:** PASS — CSP bridge gone; dated inventories cited; `MISSING_IMAGES.csv` linked; license manifest; AJ/receipt/invoice/microscope folders excluded; bucket pinned `gs://numista-catalog-assets` + `firebase.json:275-276`.

### Carry-forward (non-blocking CoS; clear at execute)

1. **EX-780b-1 / EX-780b-2** (Argon): propagate year-from-text into `resolveFromMap`/`resolve`; filter external URLs in `_cleanUrl` so fallthrough reaches `CoinImageService`.
2. **EX-780c-1 / EX-780c-2** (Argon): same `_cleanUrl` filter; unify tier counts with scrubbed `MISSING_IMAGES.csv` / NET-803.
3. Cite **NET-803 §2.E ($25/$20)** and **§8 rollback/preview** for any GCS mirror ingest under 780c.
4. Public/card valuations: keep **CDN CPG retail primary**; AI Value only as non-primary fallback / pending chip (780b already prefers `cpgRetail`).

---

## 2. PII Findings

- No user/AJ PII quoted as data. 780c correctly names AJ/receipt/invoice/microscope paths as **blocked intake folders**.
- Regex `(?i)(aj|invoice|receipt|packing|microscope|user_upload|eric)` is broad on `eric` — acceptable for intake quarantine; confirm it does not block legitimate public-domain filenames containing “American” etc. (it should not — pattern is path-segment oriented).

---

## 3. Two-Sentence Plain English (for Eric)

The collection-card plan fixes the broken 2026 Silver Eagle and 2023 nickel pictures and replaces the raw word “Pending” with a proper gold “Valuation Pending” badge, without inventing a $95 price or mixing your purchase cost into market value. The image plan permanently refuses to hotlink Wikimedia, keeps every catalog photo on our own Google bucket with license credits and a hard block on personal/AJ/receipt folders, and explains that yesterday’s `3936ba5f` commit was only an hourly docs backup with zero app code.

---

## 4. SAG Result (independent; grok-4.7; key never printed)

```
# SAG SCORE NET-791 (xAI API, grok-4.7, 2026-11-05 ET)

## SAG_SCORE: 83/100 FAIL
## MUST_FIX (blocking before Eric YES; or NONE blocking)
1. **780b valuation:** Ship `cpgRetail` only. If it parses `<= 0`, show the gold `Valuation Pending` chip. Delete `finalVal = valCpg > 0 ? valCpg : valAi`. Do not display AI Value, wholesale, issue price, or purchase price/cost in the value slot. Add a test: `cpgRetail` 0 + AI `"$95.00"` or `"Pending"` renders the chip, not a dollar amount.
2. **Both plans:** Restate a hard `$` cap with stop-on-exceed (a `$0` estimate is not a cap), rollback (code SHA revert + bucket generation/prefix restore), and preview-before-live (`p7-gate` green before any live publish). Keep `main` at `9f04550a`, Stripe OFF, Firestore writes out of this baton.
3. **780b RCA:** The `guest_demo_coins.json` 2026 Eagle block is not established. Argon says that file does not contain it. Remove Certification Number `69201940` and the `"$95.00"` sample as facts. Re-state the break from the real field path only.
4. **780b+780c images:** Treat `upload.wikimedia.org`, `thumb.wikimedia.org`, `commons.wikimedia.org`, and `numismatics.org` as empty in `_cleanUrl` so `CoinImageService` runs before any placeholder. `_buildCoinImage` must not `Image.network` any host outside the closed CSP. Manifest `source_url` is credit text only, never an image src.
5. **780c census:** `1,420 / 1,180 / 602` conflicts with NET-777 `2,273 / 747 / 181 / 1`, and the table says 0 missing while all 3,202 rows are in `MISSING_IMAGES.csv`. One canonical CSV must drive both plans. Do not invent coverage.
6. **Primary art + bucket:** Ban `ai_replica_images` as primary and as catalog intake. `gs://numista-catalog-assets` is the same bucket as NET-803: name the prefix owner, forbid overwrite, and tie it to the rollback in item 2.
## NON_BLOCKING
- `3936ba5f` narrative is present (docs auto-backup, 0 code claimed). Attach `git show --stat` before execute; do not treat it as proved here.
- Argon: nickel `5¢` regex and `hasUserUploadedPhotos` already exist in the tree he read. Do not re-edit if already true.
- PII regex `(?i)(aj|...|eric)` is broader than the folder denylist; prefer explicit prefixes so real coin files are not dropped.
- Do not show `Cost:` on any public catalog surface.
- One line: this failfix does not outrank Thanksgiving Meta ads #1.
- Year-from-text must not take the first year in a multi-year title; propagate the same helper into `resolve` / `resolveFromMap` (Argon EX-780b-1).
## PII_FINDINGS
No customer records, AJ photo bytes, or receipt/invoice contents are in these plans. Exclusion labels name `AJ's Coins/`, `Scans AJ June 2026/`, `AJ_Photos/`, `Row 10 Eric's microscope photos/`, plus regex tokens `aj` and `eric`. Certification number `69201940` is printed in 780b as if it were a real `guest_demo_coins.json` row; that citation is disputed — do not copy it into code, manifests, or buckets. Planned object keys are `nac_code` only. 0-hit proof is specified, not run.
## 2_SENTENCE_PLAIN_ENGLISH (for Eric)
These revised plans do close the old “open Wikimedia in CSP” mistake and they stop inventing a $95 Mint price, but they are not ready for your YES. They would still show AI value when CPG retail is missing, they never state a hard dollar cap or rollback, and the image fix can still leave the nickel card blank while the census numbers do not match the other catalog plan.
## RATIONALE (brief)
MF-B1 and MF-B4 are met in intent; MF-C1 deletes the CSP bridge; MF-C4/C5/C6 name licenses, an AJ/PII denylist, and `gs://numista-catalog-assets` with `firebase.json:275-276`. That is not a PASS. The planned value line still promotes AI Value when `cpgRetail` is 0, which breaks CPG-retail-only. Neither plan restates hard `$` cap, rollback, or a real preview-before-live gate for the shared NET-803 bucket. The Eagle JSON citation is not verified, tier counts contradict NET-777 and `MISSING_IMAGES.csv`, and the Wikimedia guard returns a placeholder before `CoinImageService`, so card 2 is not actually fixed. Argon 96/96 is not adopted.
```


## 5. Next Actions

AG amend on SAG must-fixes → re-score → Eric typed YES only after SAG ≥95. No deploy. Locks unchanged.
