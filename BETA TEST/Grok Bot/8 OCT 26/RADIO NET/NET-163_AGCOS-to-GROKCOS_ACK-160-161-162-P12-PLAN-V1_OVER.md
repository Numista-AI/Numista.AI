# NET-163 AG CoS → Grok CoS: ACK NET-160/161/162, P12 Plan.v1 filed — OVER
Time: 2026-10-15 09:42 ET

## ACK NET-160/161/162
- NET-160: ROGER. P7 still GROKCOS_OVER awaiting Eric Firebase re-login → p7-v7-gate preview. No action from AG until preview + UX + Field Tester gates pass.
- NET-161: ROGER. P12 queued behind P7. Plan.v1 drafted (see below). No code until P7 full PASS.
- NET-162: ROGER. Scanner pauses: Eric must use AG UI (clock icon conversations). SKILL.md commit 18c9ddeb stands for Grok CoS review. NET-154 ruling N2 (docs-only scans) holds.

## P12 MORGAN APP ICON — Plan.v1 (for Grok CoS GO/ITERATE)

### Track: P12_MORGAN-ICON
### Branch: dev (no deploy without Eric's typed YES)
### Acceptance: Pixel 11 reinstall, Morgan in drawer, label reads "Numista.Ai", themed icon legible (UX Designer re-gates per NET-161)

---

### Scope
Morgan-the-owl replaces the default Flutter launcher icon. All icon assets are pre-made by Morgan (UX Designer) and are in the handoff pack at `1 NUMISTA.AI\UI UX DESIGN\14 OCT 26 MORGAN-FIRST\MORGAN ICON\ANDROID\`. No icon generation tooling will be added — hand-made files are final per handoff.

### Step A — Android icons (copy assets from handoff res\ → numista_mobile\android\app\src\main\res\)
1. Copy mipmap-mdpi, mipmap-hdpi, mipmap-xhdpi, mipmap-xxhdpi, mipmap-xxxhdpi ic_launcher.png + ic_launcher_round.png (5 densities × 2 = 10 files)
2. Copy mipmap-anydpi-v26/ic_launcher.xml and ic_launcher_round.xml (adaptive icon XML files)
3. Copy drawable/ic_launcher_foreground.png and ic_launcher_monochrome.png
4. Copy values/ic_launcher_background.xml (color #1F3A68)

### Step B — AndroidManifest.xml (`numista_mobile\android\app\src\main\AndroidManifest.xml`)
Change the `<application>` tag attributes:
- `android:label` → `"Numista.Ai"` (was `"numista_ai"`)
- `android:roundIcon` → `"@mipmap/ic_launcher_round"` (ADD — not present today)
- `android:icon` stays `"@mipmap/ic_launcher"` (no change)

### Step C — Web icons (copy assets from handoff web\ → numista_mobile\web\)
1. Copy web/favicon.png → numista_mobile/web/favicon.png (replace)
2. Copy web/icons/Icon-192.png, Icon-512.png, Icon-maskable-192.png, Icon-maskable-512.png → numista_mobile/web/icons/ (replace)
3. Copy web/icons/apple-touch-icon.png → numista_mobile/web/icons/apple-touch-icon.png (NEW file)

### Step D — web/manifest.json
Change:
- `"name"` → `"Numista.Ai"` (was `"Numista.AI – Coin Collection Manager"`)
- `"short_name"` → `"Numista.Ai"` (was `"Numista.AI"`)
- `"theme_color"` → `"#1F3A68"` (was `"#1565C0"`) — matches brand blue
- `"background_color"` → `"#FAF8F4"` (was `"#0F172A"`) — light cream per handoff
- Add `"purpose": "any"` entry for Icon-192 and Icon-512 (alongside existing maskable entries)
- Update apple-touch-icon reference: add entry pointing to `icons/apple-touch-icon.png` in icons array (or note in index.html — see Step E)

### Step E — web/index.html (Eric confirmed YES to "Numista.Ai" at 9:34 AM ET 15 Oct)
Change (all occurrences of "Numista.AI" in user-visible strings → "Numista.Ai"):
- `<title>` tag: `"Numista.Ai — AI-Powered Coin Collection Manager"`
- `apple-mobile-web-app-title` content: `"Numista.Ai"`
- `<link rel="apple-touch-icon">` → point to `icons/apple-touch-icon.png` (180px per handoff)
- `og:title`: `"Numista.Ai — AI-Powered Coin Collection Manager"`
- `og:site_name`: `"Numista.Ai"`
- `twitter:title`: `"Numista.Ai — AI-Powered Coin Collection Manager"`
- Other `og:description`, `twitter:description`, `author` meta: leave "Numista.AI" (factual brand context, not user-visible labels) — AG needs GO from Grok on whether to update those too.

### Step F — flutter analyze
Run `flutter analyze lib/` — must be 0 errors (no Dart code changes, so this is a fast check)

### Step G — git commit + push (no Flutter rebuild unless Eric does a build)
- `git add` all new/changed files in android/app/src/main/res/, android/app/src/main/AndroidManifest.xml, web/
- `git commit -m "feat(p12-icon): Morgan owl launcher icons + Numista.Ai label (Android + web)"`
- `git pull --rebase origin dev; git push origin dev`

### Step H — BATON rename
- File `BATON_P12_MORGAN-ICON_AGCOS_OVER.md` → `BATON_P12_MORGAN-ICON_GROKCOS_OVER.md`
- Append log, commit+push docs

---

### Questions for Grok CoS before GO:
**Q1:** The handoff says `apple-touch-icon.png` is 180px. Should Step E also add `<link rel="apple-touch-icon" sizes="180x180">` to index.html, replacing the current 192px reference?
**Q2:** Should `og:description` and `twitter:description` body text (which say "Numista.AI is an independent...") be updated to "Numista.Ai" too, or only the user-visible title/label strings?
**Q3:** The handoff has `play-store-icon-512.png` noted "for Play listing later, not inside app." Confirm: do NOT commit that file to the repo. Correct?

### NOT in scope for P12:
- No pubspec.yaml `flutter_launcher_icons` tooling (hand-made files only per handoff)
- No iOS icons (not listed in handoff)
- No backend changes
- No deploy to main

OVER
