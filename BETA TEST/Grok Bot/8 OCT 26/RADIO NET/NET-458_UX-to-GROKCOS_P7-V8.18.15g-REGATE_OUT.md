# NET-458 (re NET-456) UX Designer -> CoS: P7 re-gate v8.18.15g (23 Oct 2026, 5:53 PM ET) - FAIL (partial)
Preview: numista-vault--p7-gate-8avtpz22.web.app, grokbot only. Eric approved 1 invoice + 1 dup CSV (5:41 PM). No deletes, no Review Hub commits.

## Improved
- Invoice 092052: Import Complete, no timeout. 17 coins identified, 17 duplicates flagged, $298.55. The Paper Trail linked it to Littleton 67000011 (16 linked, 1 unlinked "Lincoln Cent & Jefferson Nickel $0").
- dup.csv (Bulk Import): Import Complete, 1 coin, 1 duplicate flagged. The 'subtotal_val' error is gone.

## Still failing
1. "Upload a list" on Add New Coins does nothing when tapped (no file picker). This breaks a core path. The workaround is Open Bulk Import.
2. There's no "View Collection" button after an import.
3. Review Hub "Add All (72)" mixes in older pending rows from other files. Picking only one import's rows is unreliable with the virtual scroll. NOT committed, so the Commit step is untested (waiting on Eric's OK for the 17).
4. Count 314 -> 316: RESOLVED per CoS. Field Tester added 2 test coins in that window (NET-457); not a leak.
5. Melt mismatch persists: Home $2,186.57 vs My Collection $5,559.19. Face $260.88 vs $250.87. Morgan's greeting says $3,724.60 vs dashboard Est. $2,757.61 (before the import).
6. My Collection's "Date" column is mostly blank. There's no reliable date-added.
7. The console showed 18 errors on My Collection.
