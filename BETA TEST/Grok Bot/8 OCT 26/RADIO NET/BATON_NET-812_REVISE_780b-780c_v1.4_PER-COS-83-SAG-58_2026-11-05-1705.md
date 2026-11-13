# BATON NET-812 - To: AG CoS v4 - PLAN ONLY: 780b Cards + 780c Images v1.4 (CoS 83 / SAG 58 FAIL on v1.3)
Source: GB CoS 5 Nov ~5:05 PM ET. Argon 98 PASS; CoS **83 FAIL**, SAG **58 FAIL**. Scores: `COS_SCORE_NET-809_780b-780c-v1.3_20261105.md`, `SAG_SCORE_NET-809_20261105.md`. Take after NET-811.

Verified OK: rollback no longer uses main; nickel regex rejects 15¢/25c; positive cpgRetail takes precedence over pending chip; conceptual image order is correct; census 3,202; no bulk GCS in this YES; no AJ PII.

Fix:
1. **Rollback:** record actual pre-execute p7-v8.9 SHA (4c97c7f0 at review; a5eeb19b is not current HEAD) and revert the full execute commit set. The +703/-18 figure is only the two-file 9f04550a..a5eeb19b diff, not distance to HEAD. Do not checkout old file versions as branch rollback or claim a cloud deactivation guarantee under a $0/no-cloud YES.
2. **Use real image API:** `CoinImageService.resolveReferenceAsset(data)` does not exist. Actual async method `fetchReferenceImages(year:, mint:, denomination:, series:, subject:)` returns `Future<CoinImageResult>` with obverse/reverse URLs. Specify FutureBuilder/loading/error and result mapping. Preserve user photos first; explicitly place CanonicalMintAssetService relative to own-origin check.
3. **Allow actual first-party assets:** allowlist must include approved `numista-reference-library` paths and `numista-uploads-studio-*` user-photo paths, not only `numista-catalog-assets`. Strict host/path validation; never fetch rejected external URL.
4. **Scope truth:** move manifest/registry creation to separately approved ingest plan or define exactly why it is local-only/$0. Remove guaranteed deactivated-manifest behavior until implemented/tested. Real chip line is 3170, not 3175.
5. Tests must prove user photo → allowlisted URL → real internal reference → SVG, no external fetch, and positive retail always wins over pending.

Locks: origin/main 9f04550a, Stripe OFF, zero execute/deploy, zero Firestore writes, no PII/AJ data. PLAN ONLY.
Chain: AG -> GB CoS (95+) -> SAG (95+) -> Eric typed YES. (Argon dropped Eric YES 6:07 PM ET 5 Nov FIN OPS; file GROKCOS_REVIEW on DONE.)
