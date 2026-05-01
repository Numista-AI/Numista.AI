# 🚀 Numista.AI — Production Build Checklist

> **Read this file before every `flutter build web` or Cloud Run deployment.**
> Last updated: 2026-04-30

---

## 🚨 STEP 1 — Remove the Dev Service Worker Kill-Switch

**File:** `numista_mobile/web/index.html`

Delete the entire block between (and including) the STOP banner comment and the
closing `</script>` tag. It looks like this:

```html
<!--
  ╔══════════════════════════════...
  ║  🚨 STOP — DEV-ONLY BLOCK...
  ╚══════════════════════════════...
-->
<script>
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.getRegistrations().then(...)
    navigator.serviceWorker.register = () => Promise.resolve(...)
  }
</script>
```

**Why:** Shipping this breaks PWA caching and forces every user to re-download
~5MB of JS on every page load.

**After the prod build:** Restore the block so the dev loop keeps working.

---

## ✅ STEP 2 — Pre-Build Checklist

- [ ] Service worker kill-switch removed from `web/index.html`
- [ ] `flutter analyze` passes with no errors
- [ ] `pubspec.yaml` version number bumped
- [ ] Firebase config points to production project (`studio-9101802118-8c9a8`)
- [ ] NewsAPI key set as Cloud Run env var `NEWSAPI_KEY` (not just Firestore)
- [ ] Backend `main.py` latest version deployed to Cloud Run

---

## ✅ STEP 3 — Build & Deploy

```powershell
# From numista_mobile/
flutter build web --release --base-href "/"

# Deploy to Firebase Hosting (if applicable)
firebase deploy --only hosting
```

---

## ✅ STEP 4 — Post-Build Validation

- [ ] App loads fast on repeat visits (service worker is active)
- [ ] Service worker IS registered (DevTools > Application > Service Workers)
- [ ] News feed shows articles (`"source": "newsapi"` in network tab)
- [ ] PCGS cert # links open correctly
- [ ] Profit/Loss card shows correct values
- [ ] Collection table scrolls horizontally

---

## ✅ STEP 5 — After Build, Re-Enable Dev Block

Restore the service worker kill-switch in `web/index.html` so the dev loop
works again for the next sprint.
