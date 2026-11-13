# COS_SCORE - NET-585 UX PREVIEW 3 FIXES - 2234f7e4 - PASS WITH NOTES (8/10)

- **DTG:** 2026-10-27 ~10:25 AM ET
- **Scorer:** Grok CoS (baton watch)
- **Build:** `2234f7e4` on `dev`; preview `https://numista-vault--p7-gate-8avtpz22.web.app` (version `607435b7c613d98f`, expires 2026-11-03)
- **Source:** `BATONS\PREVIEW_READY_NET585_UX_3FIXES_2234f7e4.md`, `RADIO NET\NET-590_AGCOS-to-GROKCOS_PREVIEW-READY-3FIXES_OVER.md`
- **GEMINI38:** SKIPPED per Rule 9.3 (fix touches 2 files: `add_coins_hub.dart` +13/-21, `review_hub_screen.dart` +199/-?). Code reviewed directly by Grok CoS (`git show 2234f7e4`).
- **Machine checks (AG-reported, Rule 8):** `flutter analyze` 0 issues; cert_lookup 20/20; cert_flow 6/6; measured_height 25/25; probe 200.

## Verdict: PASS WITH NOTES - FT re-GO issued (NET-593)

## Fix-by-fix
1. **Dedupe SS4 (PASS).** 'Cert Lookup' tab + `_buildCertLookupTab()` removed; `TabController length: 8 -> 7`; sku/roll/world/set indices shifted 4-7 -> 3-6 consistently. Deep links `cert|pcgs|ngc|cac` now route to the fullscreen cert Scaffold:
   ```dart
   if (widget.showCertFullScreen ||
       (widget.initialTabName != null &&
           ['cert', 'pcgs', 'ngc', 'cac']
               .contains(widget.initialTabName!.toLowerCase()))) {
   ```
2. **Shorter cert path (PASS, note N1/N2).** `autofocus: true` on `_pcgsSingleCtrl`; auto-pop after success in two places:
   ```dart
   if (widget.showCertFullScreen && Navigator.canPop(context)) {
     Navigator.pop(context);
   }
   ```
3. **Quick storage on Review Hub (PASS, note N3/N4).** Badge + metadata item open `_showQuickStorageDialog`; save writes only the review-queue doc of the signed-in user:
   ```dart
   .collection('users').doc(userEmail).collection('review_queue').doc(docId)
   .update({'storage_location': newLoc, 'Storage Location': newLoc});
   ```
   Scoped to own user doc, both field spellings kept in sync, error path uses `NumistaErrorHelper`. Good.

## Notes for FT to check (not blockers)
- **N1 - auto-pop gap:** auto-pop keys only on `showCertFullScreen`. When the fullscreen cert screen is reached via deep link (`initialTabName = cert/pcgs/ngc/cac`) it renders fullscreen but will NOT auto-pop. FT: test both entry paths (top card and a deep link).
- **N2 - "View" SnackBar after pop:** SnackBar with "View" is shown, then the route pops. FT: tap "View" after a successful add and confirm it opens the coin (no dead button / no red error from a disposed context).
- **N3 - controller leak (minor):** `TextEditingController` in the storage dialog is never disposed. Fold into next touch of this file.
- **N4 - live data:** preview reads/writes the shared Firestore. FT must test storage edits on Eric's / tester account items only; clearing to empty is allowed and shows "Storage location cleared".

## Guardrails
Preview only. Live `numista.ai` / `main` OFF. No deploy, no main merge. Any live deploy = cherry-pick approved commit(s) onto a branch from main, only on Eric typed YES.