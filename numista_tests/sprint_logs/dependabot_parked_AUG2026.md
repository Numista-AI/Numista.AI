# dependabot_parked_AUG2026.md
Generated: 2026-08-31

Packages requiring a breaking-upgrade sprint AFTER launch. Do not upgrade in the current sprint.

| Package | Current | Target | Reason | Label |
|---|---|---|---|---|
| firebase-admin | current major | 10.3.0 | Major version — Cloud Functions v2 migration required. npm audit fix fails with peer-dep conflict. | POST-LAUNCH |
| firebase-functions | current major | 4.9.0 | Must be upgraded with firebase-admin together. | POST-LAUNCH |
| gaxios | transitive | patched | npm audit fix blocked by firebase-admin peer conflict. Resolved when firebase-admin upgrades. | POST-LAUNCH |
| xlsx | current | No clean OSS patch | SheetJS Prototype Pollution + ReDoS. No free npm fix. Evaluate exceljs replacement post-launch. | POST-LAUNCH |