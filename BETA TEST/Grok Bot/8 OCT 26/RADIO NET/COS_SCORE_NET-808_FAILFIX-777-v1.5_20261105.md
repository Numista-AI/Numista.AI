# GB CoS SCORE — NET-808 / FAILFIX_PLAN_NET-777_CATALOG_v1.5

- Scorer: Grok Bot Chief of Staff · 2026-11-05 ~5:00 PM ET (America/New_York)
- Repo checked read-only: p7-v8.9 @ 4c97c7f0; origin/dev @ b0b05808; origin/main @ 9f04550a
- Mode: SCORE ONLY; no execute, deploy, Firestore write, rules change, main change, or Stripe change
- **CoS: 87 / 100 FAIL** (pass >=95)
- Argon: see corresponding Argon review; not treated as repo evidence
- SAG: independent xAI grok-4.7 result filed separately
- Eric YES gate: BLOCKED pending revision and independent pass

## 1. Real-code verification

| Check | Result | Evidence |
|---|---|---|
| Rollback main / Hosting | **PARTIAL** | Removes forbidden 9f04550a file checkouts and names a Hosting restore. But pins file restore to 18a8b8e5 instead of recording the actual pre-execute dev HEAD (currently b0b05808), and omits main.dart/new helpers/new payloads from rollback. |
| Foreign Coins + (source) | **PASS** | Both are correctly SPECIFIED for removal, not claimed already removed; real origin/dev lines 599-603 and 1010-1017 match. |
| Egress hard stop | **FAIL** | Plan §3.E still says Cloud Function stop-public-egress automatically changes IAM/CDN origins. No such implementation exists, and bucket IAM cannot stop Firebase Hosting traffic. Human hosting:disable/channel-delete is the only valid shutoff currently specified. |
| Retail / images / PII | **PASS** | Explicit CDN CPG retail only, no wholesale; AI only ai_replica_images; internal-image policy; no AJ PII found. |
| Real loader and schema wiring | **FAIL** | Screen loads assets/catalog/catalog_public_v1.json. Proposed catalog_index_v20261105.json + catalog_details and cpgRetail fields are not wired into that loader or its migration. sourceInstitution is not defined in _buildMintageRow. |
| Catalog evidence | **PASS** | 3202 master rows (2965 coins,181 notes,56 medals), 9 pre_federal; CSV 3202 and tier totals 2354/639/181/1/27; mint distribution 1214 blank/730 S/619 D/472 P/104 O/36 W/27 CC. |

## 2. Breakdown

- Image/AI-field/PII: 29/30
- Locks & plan-only: 20/20
- Prior must-fix closeout: 15/25
- Grounded implementation & rollback: 13/15
- Launch fit: 10/10
- **Total: 87/100 FAIL**

## 3. Blocking must-fixes

1. Record current pre-execute origin/dev SHA at execute start (b0b05808 at review); use git revert for the complete execute commit set and retain the prior Hosting release restore. Do not use 18a8b8e5 as a branch restore or omit newly added files.
2. Remove the assertion of a functioning IAM/CDN Cloud Function. Until a Hosting-disabling control is implemented and verified, specify only the human owner running hosting:disable or deleting the preview channel at the threshold; verify project/bucket/topic mappings before naming them active.
3. Wire the two-tier payload migration into the actual catalog_public_v1.json loader (including fallback/migration and tests), define cpgRetail on public data, and replace sourceInstitution with data actually available in _buildMintageRow.

## 4. PII and locks

No AJ PII found in the plan or supplied excerpts. origin/main remains 9f04550a; Stripe OFF. No execution or deployment performed.
