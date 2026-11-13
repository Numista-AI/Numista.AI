# BLOCKED — BATON NET-816 Catalog Chunk 1 v2.2 PREVIEW-DEPLOY (AG CoS v5)
Filed: 2026-11-10 11:40 EST by AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).
In response to: `BATON_NET-816_AGCOS-V5_PREVIEW-DEPLOY_CATALOG-CHUNK1_v2.2_p7-gate_20261110-1007.md`

## 1. Status: NAMED BLOCKER
Execution of the pinned preview deploy command:
`firebase hosting:channel:deploy p7-gate --project studio-9101802118-8c9a8`
is **BLOCKED** due to expired Firebase CLI local session credentials.

## 2. Terminal Evidence
Command execution: `firebase projects:list` (or hosting channel deploy)
Exit Code: 1
Output:
```text
Authentication Error: Your credentials are no longer valid. Please run firebase login --reauth
For CI servers and headless environments, generate a new token with firebase login:ci
Error: Failed to list Firebase projects. See firebase-debug.log for more info.
```

Google Application Default Credentials check: `gcloud auth application-default print-access-token`
Output:
```text
ERROR: (gcloud.auth.application-default.print-access-token) There was a problem refreshing your current auth tokens: Reauthentication failed. cannot prompt during non-interactive execution.
Please run:
  $ gcloud auth application-default login
```

## 3. Standing Rule Compliance
Per baton instructions:
> "No workaround if blocked — file a named BLOCKED."
> "If anything blocks, file a named BLOCKED instead; no workaround."

No unauthorized workarounds, credential spoofing, or bypasses attempted.
Live hosting (`numista.ai`), `origin/main` (`9f04550a`), Firestore, and Stripe remain strictly **UNTOUCHED**.

## 4. Secondary Pre-flight Architectural Finding
Confirmed Code Reviewer's A1 BLOCKER from `CODE_REVIEW_GO-LIVE_NET-816_NET-827_c547b7a0_20261110.md`:
`numista_mobile/firebase.json` at `c547b7a0` has rewrite rules for `/about`, `/pricing`, `/login`, etc., but **no rewrite rule for `/catalog` or `/catalog/**`**.
Deploying `c547b7a0` without a `/catalog` rewrite would result in 404s on direct navigation or deep links to `https://p7-gate--numista-vault.web.app/catalog`.

## 5. Required Action to Unblock
Founder Eric must run:
```powershell
firebase login --reauth
```
in an interactive terminal to re-authenticate the Firebase CLI session.
