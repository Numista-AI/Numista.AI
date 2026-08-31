# dependabot_triage_AUG2026.md
**Generated:** 2026-08-31
**Project:** Numista.AI (studio-9101802118-8c9a8)
**Status:** ITEM C complete — all alerts classified

---

## Scope

npm audit run across all production packages. Results per sub-package:

| Sub-package | Total | High | Moderate | Low | Critical |
|---|---|---|---|---|---|
| 
umista_backend/functions | 8 | 1 | 7 | 0 | 0 |
| 
umista_tests | 0 | 0 | 0 | 0 | 0 |
| Root (playwright only) | 0 | 0 | 0 | 0 | 0 |

Dart/Flutter (pubspec) not audited via npm. Run lutter pub outdated separately.

---

## Triage: 
umista_backend/functions (8 alerts)

### HIGH (1)

| Package | Severity | Dev? | Direct? | Via / CVE | Fix Available | Category | Action |
|---|---|---|---|---|---|---|---|
| xlsx | HIGH | No | Yes (direct) | Prototype Pollution + ReDoS (SheetJS) | **No automated fix** | **BREAKING-UPGRADE** | Park to post-launch. xlsx has no patched version for these CVEs in its current major. See note below. |

**xlsx note:** The SheetJS xlsx package CVEs (Prototype Pollution, ReDoS) have no patch in the current published npm version. The upstream project moved to a paid/source-available model. Action: evaluate replacement (e.g., exceljs) post-launch OR remove xlsx from the Cloud Functions bundle if it is only used in admin scripts. Do not upgrade blindly — this is a BREAKING-UPGRADE category. Parked to dependabot_parked_AUG2026.md.

---

### MODERATE (7) — All transitive via irebase-admin / irebase-functions

| Package | Severity | Dev? | Direct? | Root Cause | Fix | Category | Action |
|---|---|---|---|---|---|---|---|
| irebase-admin | Moderate | No | Yes (direct) | Pulls in @google-cloud/storage → uuid missing buffer bounds check | irebase-admin@10.3.0 — **MAJOR** bump | BREAKING-UPGRADE | Park. Major firebase-admin upgrade requires Cloud Functions v2 migration validation. |
| irebase-functions | Moderate | No | Yes (direct) | Depends on irebase-admin | irebase-functions@4.9.0 — **MAJOR** bump | BREAKING-UPGRADE | Park with irebase-admin. Upgrade together, not separately. |
| @google-cloud/storage | Moderate | No | No (transitive) | Via etry-request, 	eeny-request | Fixed if irebase-admin upgrades | TRANSITIVE-ONLY | Resolved by firebase-admin upgrade. No direct action. |
| etry-request | Moderate | No | No (transitive) | Via 	eeny-request | Fixed if irebase-admin upgrades | TRANSITIVE-ONLY | Resolved by firebase-admin upgrade. |
| 	eeny-request | Moderate | No | No (transitive) | Via uuid | Fixed if irebase-admin upgrades | TRANSITIVE-ONLY | Resolved by firebase-admin upgrade. |
| uuid | Moderate | No | No (transitive) | Missing buffer bounds check in v3/v5/v6 when buf provided | Fixed if irebase-admin upgrades | TRANSITIVE-ONLY | Resolved by firebase-admin upgrade. |
| gaxios | Moderate | No | No (transitive) | Via uuid | 
pm audit fix resolves | PATCH-COMPATIBLE | Run 
pm audit fix in 
umista_backend/functions. Verify no breaking changes. |

---

## Action Plan

### Immediate (PATCH-COMPATIBLE — safe now)
`ash
cd numista_backend/functions
npm audit fix
# Verify gaxios is patched, firebase-admin unchanged
npm audit --production
`

### Parked (BREAKING-UPGRADE — post-launch sprint)
File: dependabot_parked_AUG2026.md

| Package | Current | Target | Blocker | Label |
|---|---|---|---|---|
| irebase-admin | current major | 10.3.0 | Requires Cloud Functions v2 validation + Gen 2 migration check | POST-LAUNCH |
| irebase-functions | current major | 4.9.0 | Must upgrade with firebase-admin, not independently | POST-LAUNCH |
| xlsx | current | No clean patch | Evaluate exceljs replacement; assess if xlsx is used in production functions or admin-only | POST-LAUNCH |

### Transitive (no direct action)
@google-cloud/storage, etry-request, 	eeny-request, uuid — all resolved by firebase-admin upgrade in the parked sprint.

---

## Summary

- **8 total alerts** in 
umista_backend/functions
- **0 alerts** fixable automatically that affect a SoR write path
- **1 PATCH-COMPATIBLE** (gaxios — 
pm audit fix in functions dir)
- **2 BREAKING-UPGRADE** (firebase-admin + firebase-functions — post-launch)
- **4 TRANSITIVE-ONLY** (resolved when firebase-admin upgrades)
- **1 BREAKING-UPGRADE / no-patch** (xlsx — evaluate post-launch)
- **0 DEV-ONLY** alerts (all production packages)


pm audit --production after 
pm audit fix in functions: expected **1 high** (xlsx) and **6 moderate** (firebase-admin chain) remaining — those are all parked.

**ITEM C complete. Does not block ITEM A, B, D, E, or F.**