# ?? Numista.AI — Deployment SOP (Standard Operating Procedure)
> **Read this before every production push.**
> Last updated: 2026-06-18

---

## ?? GOLDEN RULE — When to Deploy

**Do NOT deploy after every single tweak. Do NOT wait until end of day.**

? **Deploy once per focused work session** — typically 1–3 times per day.

| Session | Example |
|---|---|
| Morning session | Make 3–5 related tweaks ? test locally ? deploy ? verify live |
| Afternoon session | Make 3–5 related tweaks ? test locally ? deploy ? verify live |
| Evening (optional) | Only if needed and there's time to verify before stepping away |

> ?? **Never deploy right before stepping away from your computer.** If something breaks, you need to be available to fix it.

---

## ?? Why Updates May Not Appear on the Live Site

If you deployed but don't see the change on https://numista.ai, check these in order:

| # | Cause | Fix |
|---|---|---|
| 1 | **Browser cache / service worker** (most common) | Verify in an **Incognito window** — always |
| 2 | **Flutter analyze failed** and aborted the build | Re-read terminal output; fix errors and re-run script |
| 3 | **Backend not redeployed** | If `numista_backend/main.py` changed, run `gcloud run deploy` separately |
| 4 | **pubspec.yaml version not bumped** | Bump the version before building |
| 5 | **Wrong Firebase project targeted** | Confirm `studio-9101802118-8c9a8` appears in deploy output |
| 6 | **Firebase deploy propagation delay** | Wait 60–90 seconds, then hard-refresh in Incognito |

---

## ? STEP-BY-STEP DEPLOY CHECKLIST

### ?? Phase 1 — Before You Start Coding

- [ ] Local dev server is running (`launch_numista.ps1`)
- [ ] You know which files you are about to change
- [ ] You know if this affects the **frontend only** or **backend too**

---

### ?? Phase 2 — While Coding

- [ ] Test every change at `http://localhost:8080` before deploying
- [ ] Group related tweaks together — deploy once when the group is done, not per-tweak
- [ ] Note if `numista_backend/main.py` was modified (requires a separate backend deploy)

---

### ?? Phase 3 — Pre-Deploy

- [ ] `flutter analyze` passes with **zero errors** (the deploy script runs this automatically, but verify)
- [ ] `pubspec.yaml` version number bumped (at minimum the build number: `1.0.x+N`)
- [ ] Backend changes noted? ? will need `gcloud run deploy` after the script

---

### ?? Phase 4 — Deploy

Run from the project root:

```powershell
.\deploy_production.ps1
```

This script automatically:
1. Removes the dev service-worker kill-switch from `web/index.html`
2. Runs `flutter analyze` (aborts if errors found)
3. Runs `flutter build web --release --base-href "/"`
4. Deploys via `firebase deploy --only hosting`
5. Restores the dev service-worker kill-switch
6. Pings https://numista.ai for a 200 response

> ?? Do NOT run these steps manually unless the script fails. Use the script.

**If backend was also changed**, run separately after the script:

```powershell
# From numista_backend/
gcloud run deploy numista-backend --source . --project studio-9101802118-8c9a8 --region us-central1
```

---

### ?? Phase 5 — Post-Deploy Verification (MANDATORY)

> ? A deploy is NOT complete until you personally verify the live site.

1. **Open an Incognito window** (not your regular browser tab — it may show cached content)
2. Navigate to **https://numista.ai**
3. Verify the specific feature/fix you just deployed is visible and working
4. Open **DevTools ? Console** — confirm zero errors
5. Open **DevTools ? Application ? Service Workers** — confirm service worker is active

- [ ] Site loads without errors
- [ ] The changed feature works correctly on the live site
- [ ] No console errors in DevTools
- [ ] Service worker is registered and active

---

### ?? Phase 6 — Log It

Append a brief entry to `SESSION_LOG.md`:

```
## YYYY-MM-DD — [Short description of what was deployed]
- Changes: [list what changed]
- Backend redeployed: Yes / No
- Verified live: Yes
```

---

## ?? Things to NEVER Do

| ? Never | ? Instead |
|---|---|
| Deploy after every single small tweak | Group tweaks, deploy once per session |
| Verify the live site using your regular browser tab | Always verify in **Incognito** |
| Mark a task as done if only local dev was updated | Deploy AND verify live before marking done |
| Run flutter build steps manually, bypassing the script | Always use `deploy_production.ps1` |
| Deploy right before stepping away from your desk | Stay available to catch issues post-deploy |
| Run `flutter clean` unless explicitly needed | It deletes the web build cache |

---

## ?? Key File Reference

| Purpose | Path |
|---|---|
| **This SOP** | `DEPLOYMENT_SOP.md` |
| Production deploy script | `deploy_production.ps1` |
| Production build checklist | `PROD_BUILD_CHECKLIST.md` |
| Agent standing rules | `agent_guidance.md` |
| Session log | `SESSION_LOG.md` |
| Flutter app | `numista_mobile/` |
| Python backend | `numista_backend/` |

---

## ?? How Long Does a Deploy Take?

| Step | Time |
|---|---|
| flutter analyze | ~30 seconds |
| flutter build web --release | 2–4 minutes |
| firebase deploy --only hosting | ~30 seconds |
| Firebase CDN propagation | 30–90 seconds |
| **Total (typical)** | **~4–6 minutes** |

Plan for ~10 minutes from running the script to confirmed live verification.
