# NET-108 AG CoS to Grok CoS — P7 PREVIEW CHANNEL INFO — OVER

14 Oct 2026, ~18:18 ET. Updated with correct Firebase project info (per Eric).

## Correct deploy command (for V6 gate preview)

`numista-vault` is a **hosting site** (not a project) inside Firebase project `studio-9101802118-8c9a8` ("AJ's AI Coin App"). Correct command:

```
firebase hosting:channel:deploy p7-v6-gate --project studio-9101802118-8c9a8 --only numista-vault --expires 7d
```

`eric@numista.ai` CAN see `studio-9101802118-8c9a8` in `firebase projects:list` — so this account can deploy the preview channel. Preview channel gets its own temporary URL and does not touch the live site.

## Build command (run first from numista_mobile\ dir)
```
flutter build web --release --dart-define=FLUTTER_ENV=prod
```

## Per NET-112
No V5 preview needed. Grok CoS handles the preview deploy with Eric after V6 code PASS.
V6 is in progress now (AG CoS subagent). Will file NET when V6 done.

## Backend / test account for V6 gate
- Backend: numista-qc Cloud Run (FLUTTER_ENV=prod points to QC backend, not live)
- Firestore: numista-qc project only — grokbot@numista.ai test adds only, no live user data
- Test viewports: 390×844 (phone) and 1024 wide (tablet/web)

## OVER
