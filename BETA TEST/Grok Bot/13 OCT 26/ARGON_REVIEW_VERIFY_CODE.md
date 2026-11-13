# ARGON_REVIEW_VERIFY_CODE: checking the outside AI review's claims against live code

Checked Tue 13 Oct 2026, ~5:50-6:40 PM ET. Grok Bot, READ-ONLY.
- **origin/main = d3f7a2cd** ("fix(t1c-p0): add /api/spot_prices to _PUBLIC_PATHS (PR #259)", 13 Oct, 5:06 PM ET), read in a temp worktree that has since been removed.
- Read-only gcloud and gh listing only: no settings changed, no secret VALUES read (key names only), no live POSTs, no messages, no git writes.

## BLUF
| # | Claim | Verdict | Key evidence |
|---|---|---|---|
| 1 | PIN sign-in has no server-side rate limit or lockout; codes don't expire | **PARTIAL** | Sign-in: CONFIRMED. There is no limiter, lockout, App Check or reCAPTCHA in the repo, only Firebase's built-in throttle (auth_service.dart:90-91, :194-195). The other codes DO expire: transfer claim PIN 60 days + 5 tries / 15-min lockout (transfer_service.py:113, :421-458); attorney token 72h (attorney_routes.py:43); estate attorney link 7 days by default but **the client can pick any number of days** (estate_routes.py:29, :75); wishlist share 90 days (affiliate_routes.py:59); appraisal URL 7 days (main.py:11846). **Certificate of Transfer has no expiry** (there is no 12-month code), and estate_reports have no expiry (firestore.rules:26). Password reset uses Firebase's own link (expiry set by Firebase, not in the repo). |
| 2 | CSV export is open to formula injection | **CONFIRMED** | The only export of user data is backup_export_service.dart:143-175. `_cleanCsvCell` (:213-217) only wraps cells in quotes and doubles `"`; it does NOT neutralise leading `=` `+` `-` `@` TAB CR. There is no xlsx export. The other CSVs are fixed templates. |
| 3 | Demo Vault is only read-only because buttons are hidden | **FALSE** (for the Demo Vault itself) / note on Guest mode | Demo Vault = Browse Demo, shown only when NOT signed in (auth_gate.dart:131-133). The data is an in-memory JSON asset with "no Firestore reads or writes" (guest_seed_service.dart:10-11). With no token, the server's default-deny middleware returns 401 on every non-public route (main.py:174-212), and the Firestore rules require `isOwner` (firestore.rules:13-15, :41-67). There is no demo-specific server check, because none is needed. Guest mode (anonymous sign-in) is different: the demo coins are seeded into the user's OWN sandbox and are editable by design; the rules only stop changes to the `is_demo` flags (firestore.rules:56-67). |
| 4 | AI valuation has no per-user daily cap; empty collection behaviour | **CONFIRMED** (no cap on valuation) | `estimate_value_text` (main.py:6377-6378) and `estimate_value_general` (main.py:6507-6508) have no `Depends` and no `_check_and_increment_rate_cap`; they need any valid Firebase token (anonymous guests included) and call Gemini on every request (:6435, :6522). They value a single item described by request fields; there is no collection input, so "empty collection" doesn't apply. Portfolio snapshot GET returns a single 0.0 placeholder when history is empty (main.py:11200-11210). tier_gatekeeper's daily allowances are **not wired** to any AI route. Caps DO exist on rag/query 50, deep_dive (Morgan) 30, analyze_binder_scan 10, upload_document 20, import_spreadsheet 5, morgan_confirm 20 (deps.py:96-124). |
| 5 | Gemini bills to which project; no budget alerts | **CONFIRMED** (no budget on the prod project) | Vertex AI through the service account, not an API key: `genai.Client(vertexai=True, project=PROJECT_ID, location=GEMINI_LOCATION)` (main.py:387; deps.py:29), PROJECT_ID = `studio-9101802118-8c9a8` (main.py:286). That bills to account 010E3C-D8346A-91A35E. **The ONLY budget on that account is "morgan-pilot", $5 USD, thresholds 20%/100%, scoped to project numista-morgan-pilot (973425551443), NOT to studio-9101802118-8c9a8 (568985927038).** So prod has no budget or low-balance alert. |
| 6 | Dependabot: 77 open (3 critical, 39 high) | **CONFIRMED counts** | 77 open = 3 critical + 39 high + 34 medium + 1 low. Buckets below: **FIX NOW 9** (PyJWT ×7 in the prod image incl. 1 critical, urllib3 ×2), **AFTER LAUNCH 9** (pypdf ×8 runtime manifest, nodemailer ×1), **NOT REACHABLE 24**. |

## 1) PIN sign-in and other codes
**Sign-in (CONFIRMED: no repo-side limit)**
- auth_service.dart:87-91:
  ```
  static Future<AuthResult> signIn(String email, String pin, {bool passwordMode = false}) async {
    try { await _auth.signInWithEmailAndPassword(email: email.trim().toLowerCase(), password: pin.trim());
  ```
  The PIN IS the Firebase password. No backend route handles sign-in, so there is no server lockout.
- The only protection is Firebase Auth's built-in throttle, shown to the user at auth_service.dart:194-195: `case 'too-many-requests': return 'Too many tries. Please wait a few minutes, or use Forgot your PIN.';`
- grep finds **no** App Check (`firebase_app_check`), reCAPTCHA, `RecaptchaVerifier`, or attempt counter in numista_mobile/lib, pubspec.yaml, web/index.html or the backend.
- Risk: a 6-digit PIN has 1,000,000 combinations, and Firebase's throttle is per IP/account but not a hard lockout. Recommendations:
  - turn on Firebase **Email Enumeration Protection** and **App Check** (reCAPTCHA Enterprise) for Auth;
  - consider a longer PIN or password option;
  - optionally put a Cloud Function / Identity Platform blocking function in front for per-account lockout.

**Other codes**
| Code | Expiry / limit | Evidence |
|---|---|---|
| Transfer claim PIN | **60 days**, 5 wrong tries, then a **15-minute lockout** stored on the transfer doc; checked only after the recipient-identity lock | transfer_service.py:113 `expires_at = now + timedelta(days=60)`; :246-251 expiry check; :408-417 recipient check first; :421-422 `PIN_MAX_ATTEMPTS = 5`, `PIN_LOCKOUT_MINUTES = 15`; :449-458 increment and lock. Note: the count is read then incremented with `firestore.Increment`; it is not one transaction (carried over from 027F item 10). |
| Certificate of Transfer / passport | **No expiry, no code.** The PDF is token-gated (sender / claimer / recipient); `/api/provenance/verify/{passport_id}` is public on purpose | main.py:11675; main.py:144 and :163 (_PUBLIC_PATHS). No "12 months" anywhere in code. |
| Attorney portal token (attorney_routes) | **72 hours**, checked on read | attorney_routes.py:43 `TOKEN_TTL_HOURS = 72`; :136 `expires_at = now + timedelta(hours=TOKEN_TTL_HOURS)`; :217-222 check |
| Estate attorney link (estate_routes) | **7 days by default, but the client chooses `valid_days` with no upper limit**; revocable | estate_routes.py:29 `valid_days: Optional[int] = 7`; :75 `timedelta(days=req.valid_days or 7)`; :161 revoke; :179-183 revoked/expiry check. Fix: cap it, e.g. `min(max(valid_days,1),30)`. |
| Estate report doc (Firestore) | **Never expires.** Anyone who knows the reportId can GET it | firestore.rules:24-27 `allow get: if true; // attorney portal - token == reportId` |
| Wishlist share link | **90 days** | affiliate_routes.py:55-59 `token = secrets.token_urlsafe(9)[:12]` … `expires_at = now + timedelta(days=90)`; :117 rejects expired (HTTP 444) |
| Estate appraisal URL | **7 days** | main.py:11846 `expires_at = now + pd.Timedelta(days=7)` (route at main.py:~11800 `/api/estate/generate-appraisal-url`) |
| Password / PIN reset | The Firebase-managed oobCode link; the expiry is set by Firebase, not by the repo (there's no custom `actionCodeSettings`) | auth_service.dart:140 `await _auth.sendPasswordResetEmail(email: email.trim());` |

## 2) CSV / Excel export (CONFIRMED vulnerable)
| Path | What | Escaping |
|---|---|---|
| numista_mobile/lib/services/backup_export_service.dart:143-175 `exportCsvDownload()` (Settings button, settings_screen.dart:248) | **User collection data**: Year, Denomination, Series, Theme, Condition, Cost, AI value, Cert #, Storage Location, photo URLs, Added | **NONE for formulas.** :213-217: `static String _cleanCsvCell(dynamic val) { if (val == null) return '""'; final str = val.toString().replaceAll('"', '""'); return '"$str"'; }` A cell like `=HYPERLINK("http://evil","x")` or `+cmd|...` in Storage Location or Notes stays live when opened in Excel or Sheets. Quoting does not stop formula evaluation. |
| backup_export_service.dart:179-199 `downloadCsvTemplate()` | Static template | Fixed text, no user data |
| numista_backend/main.py:1395-1415 `GET /api/template` | Static template | Fixed text |
| numista_mobile/web/add_coins.html:983-989 | Static template | Fixed text |
| numista_mobile/web/index.html:134-135 `window._downloadCSV` | Blob helper | Passes through whatever it is given |
| Backend xlsx / openpyxl / pandas `to_csv` / `to_excel` | **None** in main.py, routes/, services/ or scan_service | n/a |
| JSON backup (backup_export_service.dart:125-140) | JSON | Not affected |

**Fix (Flutter, 3 lines):** in `_cleanCsvCell`, if `str` starts with any of `= + - @ \t \r`, prefix it with `'` before quoting. Test: the cell `=1+1` exports as `"'=1+1"`.

## 3) Demo Vault (FALSE as stated)
- **What "Demo Vault" is:**
  - auth_gate.dart:131-133: `// 2. If demo mode requested or active, show BaseLayout in demo mode` / `if (widget.isDemo || GuestSeedService.isBrowseDemoMode) { return const BaseLayout(isDemoMode: true); }`. This is reached only in the **not signed in** branch (auth_gate.dart:125).
  - base_layout.dart:1281-1289 labels the exit button "Exit Demo Vault".
  - guest_seed_service.dart:10-11: `[browseDemoMode] - Read-only. Coins loaded from JSON asset into memory, no Firestore reads or writes. Zero Firebase auth.`
- **Server enforcement:** no demo-specific check is needed, because there is no token.
  - main.py:174-212 `default_deny_auth_middleware`: anything not on `_PUBLIC_PATHS` (main.py:129-155) without a valid Bearer returns **401**. No public path is a coin or collection write.
  - firestore.rules:13-15 `function isOwner(email) { return request.auth != null && (...) }`; every user write path requires isOwner (e.g. :41-67), so an unauthenticated client cannot write.
  - storage.rules: same owner-based model (not changed by demo mode).
- **Guest mode (anonymous sign-in) is NOT read-only, by design** (guest_seed_service.dart:13-15: "100 demo coins are seeded into the user's own Firestore collection. Full features except CSV download and wishlist share").
  - The rules only lock the demo flags: firestore.rules:56-59 (create needs `is_demo == false`), :64-67 (update can't change `is_demo` / `is_demo_cleared`).
  - Server: sandbox_routes.py:24-60 soft-archives (`is_demo_cleared: true`) and never deletes.
- **Side note:** the middleware ACCEPTS anonymous Firebase tokens, because `verify_firebase_bearer_token` succeeds. So guest users can call any token-only route, including the uncapped AI valuation routes (see #4).

## 4) AI valuation: empty collection and daily caps (CONFIRMED: no cap)
| Route | Auth | Daily cap | Gemini call | Empty-collection behaviour |
|---|---|---|---|---|
| POST /api/estimate_value_text, main.py:6377-6378 `async def estimate_value_text(request: TextValuationRequest):` | middleware token only (anonymous OK) | **NONE** | main.py:6435 `genai_client.models.generate_content(model=PRIMARY_MODEL, ...)` | N/A: the input is one item (`year`, `denomination` required, TextValuationRequest). It does not read the collection. |
| POST /api/estimate_value_general, main.py:6507-6508 | middleware token only | **NONE** | main.py:6522 | N/A, same |
| POST /api/deep_dive (Morgan) | manual token check | **30/day** (main.py:3078 `_check_and_increment_rate_cap(caller_uid, "deep_dive", 30, is_admin=is_admin)`) | yes | Answers from the user's own collection; an empty collection just gives an empty context (code trace, not run) |
| POST /api/v1/rag/query | Depends | **50/day** (main.py:273) | yes | n/a |
| GET /api/portfolio/snapshot, main.py:11189-11190 `async def get_portfolio_snapshot_history(user_id: str):` | middleware token only, **takes `user_id` from the query** (no ownership check, IDOR) | n/a | no | Empty history returns `[{... "totalValue": 0.0, ...}]` (main.py:11200-11210) |
| POST /api/portfolio/snapshot/daily, main.py:10660-10661 | `Depends(require_admin_user)` | n/a | no | Sums parsed prices; empty gives 0.0 |

- **Cap helper** deps.py:96-124 `check_and_increment_rate_cap`: Firestore `_rate_limits/{uid}/{endpoint}/{date}`, 429 at the limit, fails closed. It's used only by the routes listed (also import_routes.py:90 = 5, scan_routes.py:100 = 20, morgan_routes.py:160 = 20, main.py:4381 = 10).
- **tier_gatekeeper:** `TIER_DAILY_ALLOWANCES` (tier_gatekeeper.py:52) and `check_and_enforce_coin_limit` (:234) are imported only by payment_routes.py:16-21 for display (:140); **no AI route enforces tier allowances.**
- I did NOT run an offline TestClient for these; this is a code trace (the route signatures show no cap, so a run wouldn't add anything).
- **Fix:** add `_user: dict = Depends(get_current_user)` plus `_check_and_increment_rate_cap(uid, "estimate_value", N)` to both estimate routes; reject anonymous tokens on AI routes; fix the portfolio-snapshot `user_id` IDOR (take the user from the token).

## 5) Gemini billing project and alerts (CONFIRMED: no prod budget)
- **Code:**
  - main.py:286 `PROJECT_ID = "studio-9101802118-8c9a8"`;
  - :287 `LOCATION = "global"`;
  - :386 `GEMINI_LOCATION = os.environ.get("GEMINI_LOCATION", LOCATION)`;
  - :387 `genai_client = genai.Client(vertexai=True, project=PROJECT_ID, location=GEMINI_LOCATION)`;
  - deps.py:29 `genai.Client(vertexai=True, project=PROJECT_ID, location="us-central1")`;
  - vector_rag_service.py:39 embeddings `location="global"`.
  - **No Gemini API key env var.** Calls authenticate with the Cloud Run service account (ADC) and bill to **studio-9101802118-8c9a8**.
  - Exception: services/variety_detector.py:63 `genai.Client()` with no args reads GOOGLE_API_KEY / GOOGLE_GENAI_USE_VERTEXAI from the env. Neither is set on Cloud Run, so it currently fails ("No API key was provided", seen in the 12 Oct sweep).
- **deploy-production.yml:**
  - :152-158 `gcloud run deploy numista-backend --image us-central1-docker.pkg.dev/studio-9101802118-8c9a8/... --region us-central1 --project studio-9101802118-8c9a8 --update-secrets=EBAY_CERT_ID=EBAY_CERT_ID:latest --min-instances 1`;
  - scan service :214-217, same project and region;
  - Firebase deploys use `secrets.FIREBASE_SERVICE_ACCOUNT` (:69, :96, :127, :189).
- **Live Cloud Run env NAMES (read-only `gcloud run services describe`, names only):**
  - numista-backend: NUMISTA_SCRAPE_HTTP_PROXY, NUMISTA_SCRAPE_HTTPS_PROXY, GREYSHEET_API_KEY, GREYSHEET_API_TOKEN, STRIPE_WEBHOOK_SECRET, NUMISTA_API_KEY, STRIPE_PUBLISHABLE_KEY, PCGS_BEARER_TOKEN, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SENDER_EMAIL, RAG_RETRIEVAL, EBAY_CERT_ID.
  - Only **EBAY_CERT_ID** comes from Secret Manager. **The other secret-type values (STRIPE_WEBHOOK_SECRET, SMTP_PASSWORD, GREYSHEET_*, PCGS_BEARER_TOKEN, NUMISTA_API_KEY) are plain env vars.** That's a hygiene finding: move them to Secret Manager.
  - No GEMINI_LOCATION, so location = "global".
  - numista-scan-service: no env vars.
- **Billing (read-only gcloud, logged in as eric@numista.ai, project studio-9101802118-8c9a8):**
  - `gcloud billing projects describe` gives billingAccounts/010E3C-D8346A-91A35E, billingEnabled True.
  - Projects on that account: studio-9101802118-8c9a8 and numista-morgan-pilot.
  - `gcloud billing budgets list` returns **one budget: "morgan-pilot", 5 USD, thresholds 0.2 and 1.0, filter projects/973425551443 (= numista-morgan-pilot).** studio-9101802118-8c9a8 is project number **568985927038**, so **the production project has NO budget and NO alert.**
- **Repo:** there is no budget config (no Terraform or budget YAML). numista_backend/monitor_gcp_billing.py only reads budgets through the billingbudgets API; it's a manual script with no alerting.
- **Recommendation (for Eric to approve; I changed nothing):** create a budget on billing account 010E3C-D8346A-91A35E scoped to studio-9101802118-8c9a8 (e.g. $50/month, alerts at 50/90/100% to eric@numista.ai), optionally with a Pub/Sub cap action.

## 6) Dependabot triage (gh api, read-only, Numista-AI/Numista.AI)
**Open: 77 = 3 critical, 39 high, 34 medium, 1 low.** Prod images install `numista_backend/requirements.txt` (Dockerfile:21). requirements-dev.txt is a duplicate pin set used only in dev/CI.

**Critical (3)**
| Package | Manifest | Bucket | Reason |
|---|---|---|---|
| PyJWT 2.13.0 → 2.14.0 (asymmetric-PEM detection bypass) | numista_backend/requirements.txt | **FIX NOW** | Installed in the prod backend image (it's a firebase_admin 7.3.0 dependency). Our code never imports `jwt` (Firebase ID tokens go through google-auth), so real-world reachability is low, but it's a one-line pin bump. |
| PyJWT (same) | numista_backend/requirements-dev.txt | NOT REACHABLE | Dev pins only; bump together with the line above |
| next → 16.3.6 (RCE in next/og ImageResponse) | numista_admin/package-lock.json | NOT REACHABLE* | numista_admin isn't deployed by any workflow and isn't in firebase.json hosting. *If the admin app is hosted anywhere by hand, it becomes FIX NOW. |

**High (39)**
| Package | Count | Manifest | Bucket | Reason |
|---|---|---|---|---|
| PyJWT (JWK-as-HMAC, BOM bypass, DER-as-HMAC, empty HMAC key, JWKS redirects) → 2.14.0 | 6 | numista_backend/requirements.txt | **FIX NOW** | Same pin bump as the critical; in the prod image |
| urllib3 2.7.0 → 2.8.0 (unbounded chunked buffering; HTTPS-proxy TLS config ignored) | 2 | numista_backend/requirements.txt | **FIX NOW** | `requests` is used at runtime (main.py, news_routes.py, pcgs_routes.py), and the backend uses HTTPS scrape proxies (NUMISTA_SCRAPE_HTTPS_PROXY), so the proxy-TLS bug is relevant |
| pypdf 6.16.2 → 6.19.0 (memory/runtime DoS on crafted PDFs) | 8 | numista_backend/requirements.txt | AFTER LAUNCH | Installed in prod, but only imported by `_scripts/*` (check_gemini_model_updates, extract_pdfs, extract_wiki, parse_pdf); no route parses user PDFs with pypdf |
| nodemailer → 10.0.6 (addressparser ReDoS) | 1 | numista_backend/functions/package.json | AFTER LAUNCH | The function `onFeedbackCreated` is ACTIVE, but it sends only to the constants ALERT_TO/ALERT_FROM (feedbackIntelligence.js:95-114), not user-supplied addresses |
| tornado 6.5.8 → 6.5.9 (curl client size limit; StaticFileHandler symlinks) | 2 | numista_backend/requirements.txt | NOT REACHABLE | Installed but never imported; the app serves with uvicorn/FastAPI |
| PyJWT / pypdf / tornado / urllib3 duplicates | 6+8+2+2 = 18 | numista_backend/requirements-dev.txt | NOT REACHABLE | Dev-only pin file |
| next (SSRF in image optimisation) | 1 | numista_admin/package-lock.json | NOT REACHABLE* | Admin app not deployed (see above) |
| sharp (librsvg CVE) | 1 | numista_admin/package-lock.json | NOT REACHABLE | Transitive, admin app not deployed |
| source-map-js (event-loop DoS) | 1 | numista_admin/package-lock.json | NOT REACHABLE | Build-time transitive |
| source-map-js | 1 | numista_hardware/Original_logic/package-lock.json | NOT REACHABLE | Development scope, hardware prototype dir |

**Critical + high buckets:** FIX NOW **9** (PyJWT 7 + urllib3 2), AFTER LAUNCH **9** (pypdf 8 + nodemailer 1), NOT REACHABLE **24**.

**Medium (34) and low (1), counts by bucket:**
| Bucket | Count | What |
|---|---|---|
| FIX NOW (bundled into the same pin bumps) | 9 | PyJWT ×8 + urllib3 ×1 (requirements.txt) |
| AFTER LAUNCH | 6 | Werkzeug ×1, tornado ×1, GitPython ×1, pillow-heif ×1 (requirements.txt; pillow-heif is used for HEIC conversion, so look at it first), nodemailer ×2 (functions) |
| NOT REACHABLE | 19 med + 1 low | requirements-dev.txt duplicates ×13 (PyJWT 8, Werkzeug, tornado, GitPython, urllib3, pillow-heif), numista_admin next ×4 med + 1 low, brace-expansion ×2 (13 + 4 + 2 = 19 med) |

(Mediums total: 9 + 6 + 19 = 34; low = 1, admin next.)

**Cheapest fix for the FIX NOW set:**
- numista_backend/requirements.txt (and -dev): `PyJWT==2.14.0`, `urllib3==2.8.0`;
- optionally in the same PR: `pypdf==6.19.0`, `tornado==6.5.9`;
- then the full pytest run and a deploy.

## Notes
- Folders: both `MyVertexProject\1 NUMISTA.AI\BETA TEST\Grok Bot\13 OCT 26\` and a top-level `MyVertexProject\BETA TEST\Grok Bot\13 OCT 26\` exist or were created; this file is saved in **both**.
- Read-only commands I ran:
  - `gcloud config list`, `gcloud auth list`;
  - `gcloud billing projects describe/list`, `gcloud billing budgets list`;
  - `gcloud projects describe/list`;
  - `gcloud run services describe` (env names only);
  - `gcloud functions list`;
  - `gh auth status`, `gh api .../dependabot/alerts`.
- No settings changed.
