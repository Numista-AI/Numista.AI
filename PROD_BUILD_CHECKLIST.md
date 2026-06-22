# Numista.AI - Production Build Checklist

> **Read this file before every `flutter build web` or Cloud Run deployment.**
> Last updated: 2026-06-22

---

## IMPORTANT: PRIMARY DEPLOYMENT METHOD

**Push to the `main` branch.** GitHub Actions handles everything automatically.

```powershell
git add -A
git commit -m "Deploy: <description>"
git push origin main
```

This checklist applies when running `deploy_production.ps1` as an **emergency fallback only**.

---

## STEP 1 - Remove the Dev Service Worker Kill-Switch

**File:** `numista_mobile/web/index.html`

Delete the entire block between (and including) the STOP banner comment and the
closing `</script>` tag:

```html
<!-- STOP - DEV-ONLY BLOCK ... -->
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

> NOTE: `deploy_production.ps1` does this automatically. Only do it manually if building by hand.

---

## STEP 2 - Pre-Build Checklist

- [ ] Service worker kill-switch removed from `numista_mobile/web/index.html`
- [ ] `flutter analyze` passes with no errors
- [ ] `pubspec.yaml` version number bumped
- [ ] Firebase config points to production project (`studio-9101802118-8c9a8`)
- [ ] NewsAPI key set as Cloud Run env var `NEWSAPI_KEY` (not just Firestore)
- [ ] Backend `main.py` latest version committed and pushed (GitHub Actions will deploy it)

---

## STEP 3 - Build and Deploy

### Primary (CI/CD - always use this)

```powershell
# From project root
git add -A
git commit -m "Deploy: <description>"
git push origin main
# Monitor: https://github.com/Numista-AI/Numista.AI/actions
```

### Emergency frontend-only (deploy_production.ps1)

```powershell
# From project root
.\deploy_production.ps1
# This cd's into numista_mobile/ automatically
```

### Emergency backend-only (Artifact Registry - use ONLY if CI/CD is down)

```powershell
# From numista_backend/
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
docker build -t us-central1-docker.pkg.dev/studio-9101802118-8c9a8/cloud-run-source-deploy/numista-backend:latest .
docker push us-central1-docker.pkg.dev/studio-9101802118-8c9a8/cloud-run-source-deploy/numista-backend:latest
gcloud run deploy numista-backend `
  --image us-central1-docker.pkg.dev/studio-9101802118-8c9a8/cloud-run-source-deploy/numista-backend:latest `
  --region us-central1 --project studio-9101802118-8c9a8 --quiet
```

**Registry rule:** Always `us-central1-docker.pkg.dev`. Never `gcr.io`. The `numista-app` service is retired.

---

## STEP 4 - Post-Build Validation

- [ ] App loads fast on repeat visits (service worker is active)
- [ ] Service worker IS registered (DevTools > Application > Service Workers)
- [ ] News feed shows articles (`"source": "newsapi"` in network tab)
- [ ] PCGS cert # links open correctly
- [ ] Profit/Loss card shows correct values
- [ ] Collection table scrolls horizontally

---

## STEP 5 - After Build, Re-Enable Dev Block

Restore the service worker kill-switch in `numista_mobile/web/index.html` so the dev loop
works again for the next sprint.

> `deploy_production.ps1` does this automatically. Only needed for manual builds.
