# NET-194 GROKCOS -> AGCOS: P7 V8 preview up, UX/FT re-gate requested

- Time: 2026-10-15 14:20 ET
- Preview URL: https://numista-vault--p7-v8-gate-ibg4oycd.web.app (expires 2026-10-22 14:19 ET)
- Channel: p7-v8-gate, site numista-vault, project studio-9101802118-8c9a8
- Built from: origin/dev 371989db (contains V8.2 PASS 6c68dd57), clean worktree, `flutter build web --release --dart-define=FLUTTER_ENV=prod`
- Scope: hosting PREVIEW CHANNEL only. Live, CORS backend, and firestore.rules NOT deployed.
- Known: preview calls the live backend. Checklist 'Add Selected Coins' may fail with 'Failed to fetch' until the CORS backend fix deploys (Eric's typed YES). Gates mark it BLOCKED-BY-CORS, not a code fail.
- Gates requested: UX Designer + Field Tester. Test accounts only, no writes to Eric's collections. Score confirm card, demo guard, phone layout, manual entry full screen, plain errors, /assets 404, Firestore 403, $ wrap, PIN clip.
- Rule 8: P7 remains the one job. AG holds until gate results.

OVER.
