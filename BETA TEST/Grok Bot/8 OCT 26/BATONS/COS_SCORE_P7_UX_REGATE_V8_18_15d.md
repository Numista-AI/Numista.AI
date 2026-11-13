# COS SCORE - P7 UX RE-GATE V8.18.15d - FAIL (Grok CoS, 22 Oct 2026 ~8:20 PM ET)

Source: BETA TEST\Grok Bot\22 OCT 26\UX_P7_GATE_V8.md (UX Designer NET-438)
Build: 1058fe8b (worktree C:\Users\ericd\Documents\p7gate_wt15d), preview numista-vault--p7-gate-8avtpz22.web.app

## Did the build land? YES
- Deployed main.dart.js (6,604,001 bytes) is byte-identical (SHA-256 match) to the local build\web\main.dart.js built from 1058fe8b.
- Both contain the 15d-only snackbar string "so we didn't add it twice". The deploy is good.
- The banner shows 'v8.18.15' because pubspec/version.json were never bumped for b/c/d (Eric accepted the missing letter). That is not a deploy miss.

## Tap targets: CODED, BUT DEFEATED AT RUNTIME (root cause)
- c0965740 (15b) did add `minimumSize: Size(..., 48)` to Send Beta Feedback and Sign Out (base_layout.dart:958, :1033), Take Photo and Upload (add_coins_hub.dart:5474, :5483), and the NGC card buttons (add_coins_hub.dart:3877, :3925).
- ThemeData in lib/main.dart (light :294, dark :332) sets no `visualDensity`. On desktop and desktop-web, Flutter's default is VisualDensity.adaptivePlatformDensity = compact (-2,-2). That takes 4px per density unit, so 8px, off a button's minimum height: 48 - 8 = **40px**, which is exactly what UX measured.
- The 15b tests only checked that the code *declares* 48. They never measured the rendered size. That's why everything was green and the live size still failed.
- Systemic fix: set `visualDensity: VisualDensity.standard` in both ThemeData objects (or `materialTapTargetSize: padded` plus a standard density on the button themes). Then add widget tests that render each button under TargetPlatform.windows/macOS/linux and assert `tester.getSize(find...).height >= 48`.

## Other items
- NGC title: add_coins_hub.dart:3744 still says 'Cert #$certNo ($grader) not found'. For NGC, change it to 'NGC lookup coming soon'. This was never changed.
- CACG front 663261171 is labeled PCGS and the grader switches to PCGS: FAIL. The cert-read/grader detection must keep CACG. It must not overwrite a grader the user picked, or one read from the label text.
- CACG rear unreadable, and there's no 'cert is on the back' prompt: FAIL. Add the prompt.
- Duplicate-import snackbar: not tested by UX (it needs Start Import on the real database). That needs a grokbot-only path. No writes to Eric's collections.

## Score: FAIL. Re-issue as V8.18.15e (NET-440).
