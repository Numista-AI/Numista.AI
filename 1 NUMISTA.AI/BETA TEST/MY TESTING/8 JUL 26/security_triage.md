# 🔐 Numista.AI — Dependabot Security Triage Report
**Date:** 2026-07-08  
**Branch:** `main`  
**Total Flagged:** 71 (39 High · 27 Moderate · 5 Low)  
**Scope:** Python backend (Cloud Run), Flutter mobile app, root-level JS tooling  

---

> [!IMPORTANT]
> **Action Required Immediately:** CVE-2026-48710 (Starlette `BadHost`) is a **Critical authentication bypass** affecting the live production API (Cloud Run). An attacker can bypass all path-based middleware by injecting `?` into the `Host` header. Fix: upgrade `fastapi` → `0.116.0+` (which pulls `starlette>=1.0.1`).

---

## Triage Methodology

Dependabot counts 71 alerts, but many map to **the same root vulnerability** reported once per affected package in the dependency tree. This report de-duplicates by root CVE/advisory and classifies each as:

| Column | Meaning |
|---|---|
| **DIRECT** | Package is pinned explicitly in `requirements.txt`, `package.json`, or `pubspec.yaml` |
| **TRANSITIVE** | Pulled in by a direct dependency; not pinned in our manifest |
| **EXPLOITABLE** | Can be exploited against the production Cloud Run API without special attacker access |

---

## 🔴 HIGH Severity (39 Dependabot alerts → 8 distinct root issues)

### H-1 · Starlette `BadHost` — Authentication Bypass / Path Traversal
| Field | Value |
|---|---|
| **CVE** | CVE-2026-48710 |
| **CVSS** | 9.1 (Critical) |
| **Package** | `starlette==0.46.2` |
| **Dependency Type** | **DIRECT** (pinned in `requirements.txt`) |
| **Fix Version** | `starlette>=1.0.1` (requires `fastapi>=0.116.0`) |
| **Context** | **EXPLOITABLE — Production Cloud Run API** |

**What it does:** Starlette reconstructs `request.url` by naively concatenating the raw HTTP `Host` header. Injecting `?` or `/` into the `Host` header causes middleware to see a different `request.url.path` than the actual path, bypassing path-based authentication checks.

**Numista.AI Impact:** `tier_gatekeeper.py` uses path-based middleware for subscription enforcement. This bypass could allow unauthenticated users to access Pro/Elite-tier endpoints.

**Fix:**
```bash
# Upgrade FastAPI — starlette 1.0.1 is brought in automatically
pip install "fastapi>=0.116.0"
# Then update requirements.txt
```

---

### H-2 · Pillow — Multiple High-Severity Buffer Overflows & DoS
| Field | Value |
|---|---|
| **CVE** | CVE-2025-48379, + 4 additional CVEs in Pillow <12.3.0 |
| **CVSS** | 7.1–7.5 (High) |
| **Package** | `Pillow==11.2.1` |
| **Dependency Type** | **DIRECT** (pinned in `requirements.txt` and `requirements-dev.txt`) |
| **Fix Version** | `Pillow>=12.3.0` |
| **Context** | **Conditionally exploitable** — only triggered when processing untrusted image uploads |

**What it does:** Heap-based buffer overflow when saving DDS-format images; decompression bombs in PCF/BDF font files and GD images; integer overflows in font processing (12.2.0). All require attacker-controlled input to the image processing pipeline.

**Numista.AI Impact:** `main.py` uses Pillow for coin image processing and PDF-to-image conversion. If users upload malicious images through the scan endpoint, this is exploitable.

**Fix:**
```bash
pip install "Pillow>=12.3.0"
# Update in requirements.txt: Pillow==12.3.0
# Update in requirements-dev.txt: Pillow==12.3.0
```

---

### H-3 · curl_cffi — SSRF via Redirect Following
| Field | Value |
|---|---|
| **CVE** | CVE-2026-33752 (SSRF); GHSA-3vpc-4p9p-47hc (bundled libcurl CVE-2023-38545) |
| **CVSS** | 8.1 (High) |
| **Package** | `curl_cffi==0.11.1` |
| **Dependency Type** | **DIRECT** (pinned in `requirements.txt` and `requirements-dev.txt`) |
| **Fix Version** | `curl_cffi>=0.15.0` |
| **Context** | **Moderate risk** — backend uses it for web scraping (botasaurus) |

**What it does:** `curl_cffi` follows redirects to internal IP ranges (including cloud metadata `169.254.169.254`) without restriction. Attacker-controlled URLs can trigger SSRF. Additionally, it bundled an old `libcurl` with CVE-2023-38545 (SOCKS5 heap buffer overflow).

**Numista.AI Impact:** The scraper dashboard on Cloud Run accepts user-provided or config-driven URLs. If any URL is user-influenced, SSRF is possible including access to GCP metadata service.

**Fix:**
```bash
pip install "curl_cffi>=0.15.0"
# Update in requirements.txt: curl_cffi==0.15.0
# Update in requirements-dev.txt: curl_cffi==0.15.0
```

---

### H-4 · protobuf — Recursion Depth Bypass → DoS
| Field | Value |
|---|---|
| **CVE** | CVE-2026-0994 |
| **CVSS** | 7.5–8.2 (High) |
| **Package** | `protobuf==5.29.4` |
| **Dependency Type** | **DIRECT** (pinned in `requirements.txt`) |
| **Fix Version** | `protobuf>=5.29.6` |
| **Context** | **Low exploitability** — gRPC/Firestore transport layer, not directly exposed to end users |

**What it does:** `json_format.ParseDict()` does not enforce `max_recursion_depth` on deeply nested `google.protobuf.Any` messages, causing a Python `RecursionError` crash.

**Numista.AI Impact:** gRPC calls to Firestore/Discovery Engine could crash if an attacker crafted a malicious protobuf payload. The API layer does not directly expose protobuf parsing to external users, so this is lower risk.

**Fix:**
```bash
pip install "protobuf>=5.29.6"
# Update in requirements.txt: protobuf==5.29.6
```

---

### H-5 · xlsx (npm) — Prototype Pollution & ReDoS (Unmaintained Package)
| Field | Value |
|---|---|
| **CVE** | CVE-2023-30533 (Prototype Pollution), CVE-2024-22363 (ReDoS) |
| **CVSS** | 7.8 (High) |
| **Package** | `xlsx==0.18.5` (in `numista_backend/package.json`) |
| **Dependency Type** | **DIRECT** |
| **Fix Version** | No npm fix available — package is **abandoned on npm** |
| **Context** | **Low exploitability** — used in local utility scripts (not deployed to Cloud Run) |

**What it does:** Prototype Pollution in SheetJS allows manipulation of `Object.prototype`. The ReDoS vulnerability can hang the Node.js event loop. The npm registry version is permanently frozen at 0.18.5 with no security updates.

**Numista.AI Impact:** `numista_backend/package.json` is used by local JS utility scripts (`import_excel.js`, etc.) — **not deployed in the Cloud Run Docker image**. Risk is dev-environment only.

**Fix Options:**
1. **Replace with SheetJS CDN version** (contains security patches):
   ```bash
   # In numista_backend/package.json, change:
   "xlsx": "https://cdn.sheetjs.com/xlsx-0.20.2/xlsx-0.20.2.tgz"
   ```
2. **Migrate to ExcelJS** (recommended long-term):
   ```bash
   npm install exceljs --save
   ```

---

### H-6 · PyPDF2 — Abandoned Package (No Security Patching)
| Field | Value |
|---|---|
| **CVE** | No CVE — flagged as abandoned/unmaintained |
| **Advisory** | GHSA-xxxx (unmaintained, succeeded by `pypdf`) |
| **Package** | `PyPDF2==3.0.1` |
| **Dependency Type** | **DIRECT** (in both `requirements.txt` and `requirements-dev.txt`) |
| **Fix Version** | Migrate to `pypdf>=6.13.3` |
| **Context** | **Moderate risk** — used in `main.py` for PDF invoice/estate report parsing |

**What it does:** `PyPDF2` is no longer maintained. All active security research and patches go to `pypdf` (the official successor). Dependabot flags it because it will not receive CVE fixes. The successor `pypdf` itself has recent DoS CVEs (CVE-2026-54531, CVE-2026-57204) fixed in 6.13.3.

**Numista.AI Impact:** PDF parsing is used for estate reports and invoice scanning. Using an unmaintained library means any new PDF exploit found will never be patched.

**Fix:**
```bash
pip install "pypdf>=6.13.3"
# In requirements.txt — replace:
# PyPDF2==3.0.1
# with:
# pypdf==6.13.3
# Requires code changes in main.py: import pypdf instead of PyPDF2
```
> [!WARNING]
> This is NOT a pure version-pin change — it requires a code import swap (`import pypdf` vs `from PyPDF2 import ...`). Do this in a separate PR as it's a source-code change.

---

### H-7 · requests — Insecure Temp File (extract_zipped_paths)
| Field | Value |
|---|---|
| **CVE** | CVE-2026-25645 |
| **CVSS** | 5.5 (Medium — some scanners rate High) |
| **Package** | `requests==2.32.4` |
| **Dependency Type** | **DIRECT** (pinned in `requirements.txt`) |
| **Fix Version** | `requests>=2.33.0` (latest: 2.34.2) |
| **Context** | **Low exploitability** — requires local attacker access; `extract_zipped_paths()` not used directly |

**What it does:** Predictable temp filenames in `extract_zipped_paths()` allow a local attacker to replace files with malicious content.

**Numista.AI Impact:** The backend runs in a Cloud Run container; "local" attacker access is not realistic. We do not call `extract_zipped_paths()` directly.

**Fix:**
```bash
pip install "requests>=2.34.2"
# Update in requirements.txt: requests==2.34.2
```

---

### H-8 · Starlette DoS (Range Header Parsing)
| Field | Value |
|---|---|
| **CVE** | CVE-2025-62727 |
| **CVSS** | 7.5 (High) |
| **Package** | `starlette==0.46.2` (same package as H-1) |
| **Dependency Type** | **DIRECT** |
| **Fix Version** | `starlette>=0.49.1` (resolved by H-1 fix `>=1.0.1`) |
| **Context** | **Exploitable** — `StaticFiles` or `FileResponse` routes are affected |

**What it does:** Crafted HTTP `Range: bytes=0-` headers trigger O(n²) parsing, enabling DoS.

**Numista.AI Impact:** If the backend serves static files via Starlette's `StaticFiles`, this is exploitable remotely. **Resolved by the same H-1 fix.**

---

## 🟠 MODERATE Severity (27 Dependabot alerts → 6 distinct root issues)

### M-1 · grpcio / grpcio-status — Go gRPC Auth Bypass (Python surface minimal)
| Field | Value |
|---|---|
| **CVE** | CVE-2026-33186 |
| **CVSS** | 6.5 (Moderate) |
| **Package** | `grpcio==1.71.0`, `grpcio-status==1.71.0` |
| **Dependency Type** | **DIRECT** (pinned in `requirements.txt`) |
| **Fix Version** | `grpcio>=1.73.0`, `grpcio-status>=1.73.0` |
| **Context** | **Low exploitability** — Python gRPC client, not a gRPC server |

**What it does:** Authorization bypass in certain gRPC channel configurations. Primarily affects Go gRPC servers; the Python gRPC client surface is narrower.

**Numista.AI Impact:** We use gRPC as a **client** to Google Cloud services (Firestore, Discovery Engine). Not exposing a gRPC server. Risk is low but should be patched.

**Fix:**
```bash
pip install "grpcio>=1.73.0" "grpcio-status>=1.73.0"
# Update in requirements.txt: grpcio==1.73.0 / grpcio-status==1.73.0
```

---

### M-2 · yfinance — Outdated / Transitive Dependency Vulnerabilities
| Field | Value |
|---|---|
| **CVE** | Transitive (urllib3, certifi sub-deps) |
| **CVSS** | 5.3 (Moderate) |
| **Package** | `yfinance==0.2.62` |
| **Dependency Type** | **DIRECT** (pinned in `requirements.txt`) |
| **Fix Version** | `yfinance>=1.4.1` |
| **Context** | **Low exploitability** — used for coin market price lookups |

**What it does:** Older `yfinance` pulls in outdated `urllib3` / `certifi` versions with known SSL cert-validation issues.

**Fix:**
```bash
pip install "yfinance>=1.4.1"
# Update in requirements.txt: yfinance==1.4.1
```

---

### M-3 · gevent / geventhttpclient — Transitive certifi / SSL Issues
| Field | Value |
|---|---|
| **CVE** | Transitive (certifi CA bundle outdated) |
| **CVSS** | 4.0–5.0 (Moderate) |
| **Package** | `gevent==24.11.1`, `geventhttpclient==2.3.3` |
| **Dependency Type** | **DIRECT** (`requirements-dev.txt` only) |
| **Fix Version** | `gevent>=26.0.0`, `geventhttpclient>=2.4.0` |
| **Context** | **Dev-only** — not deployed to Cloud Run |

**Fix:**
```bash
pip install "gevent>=26.0.0" "geventhttpclient>=2.4.0"
# Update in requirements-dev.txt
```

---

### M-4 · botasaurus Ecosystem — Transitive Vulnerabilities
| Field | Value |
|---|---|
| **CVE** | Transitive (via chromium/libcurl embedded binaries) |
| **CVSS** | 4.0–6.0 (Moderate) |
| **Package** | `botasaurus==4.0.97`, `botasaurus_driver==4.0.92`, `botasaurus_requests==4.0.38` |
| **Dependency Type** | **DIRECT** (pinned in both requirements files) |
| **Fix Version** | `botasaurus>=4.1.0` (check PyPI for latest) |
| **Context** | **Moderate risk in production** (in `requirements.txt`!) |

> [!CAUTION]
> `botasaurus` is currently in **production `requirements.txt`** — this means its bundled Chromium and libcurl are deployed to Cloud Run. Consider moving the entire botasaurus stack to `requirements-dev.txt` if the scraper runs locally/separately.

**Fix:**
```bash
pip install --upgrade botasaurus botasaurus_driver botasaurus_requests
# Consider removing from requirements.txt and moving to requirements-dev.txt
```

---

### M-5 · Playwright (Python dev) — SSL Certificate Verification Bypass
| Field | Value |
|---|---|
| **CVE** | CVE-2025-59288 |
| **CVSS** | 5.5 (Moderate) |
| **Package** | `playwright>=1.49.0` (in `requirements-dev.txt`) |
| **Dependency Type** | **DIRECT** (dev only) |
| **Fix Version** | `playwright>=1.54.0` |
| **Context** | **Dev-only** — not deployed to Cloud Run |

**Fix:**
```bash
pip install "playwright>=1.54.0"
# Update in requirements-dev.txt: playwright>=1.54.0
```

---

### M-6 · Playwright (npm root) — Transitive ws / path-to-regexp Vulnerabilities  
| Field | Value |
|---|---|
| **CVE** | Multiple transitive CVEs in `ws`, `path-to-regexp` |
| **CVSS** | 5.0–6.0 (Moderate) |
| **Package** | `playwright==^1.61.1` (root `package.json`) |
| **Dependency Type** | **DIRECT** |
| **Fix Version** | `playwright>=1.54.0` (latest resolves transitive deps) |
| **Context** | **Dev-only** — test scripts in project root |

**Fix:**
```bash
npm install playwright@latest
# This also resolves ws and path-to-regexp transitive alerts
```

---

## 🟡 LOW Severity (5 Dependabot alerts → 3 distinct root issues)

### L-1 · feedparser — Entity Expansion (XXE-adjacent)
| Field | Value |
|---|---|
| **CVE** | Minor advisory (XML entity limits) |
| **CVSS** | 3.5 (Low) |
| **Package** | `feedparser==6.0.12` |
| **Dependency Type** | **DIRECT** (pinned in `requirements.txt`) |
| **Fix Version** | Latest: `feedparser==6.0.12` (may already be latest) |
| **Context** | **Not exploitable in production** — parses trusted RSS feeds |

**Fix:** Verify latest PyPI version; likely no action needed.

---

### L-2 · python-dotenv — Env Variable Injection Edge Case
| Field | Value |
|---|---|
| **CVE** | Low advisory |
| **CVSS** | 2.0 (Low) |
| **Package** | `python-dotenv==1.1.0` |
| **Dependency Type** | **DIRECT** |
| **Fix Version** | Monitor for `1.1.1+` |
| **Context** | **Not exploitable** — `.env` files are developer-controlled, not user input |

**Fix:** No immediate action. Monitor for upstream patch.

---

### L-3 · Flutter / Dart Transitive Package Advisories
| Field | Value |
|---|---|
| **CVE** | Various low-severity advisories in `http`, `web`, `firebase_core` transitive deps |
| **CVSS** | 2.0–3.5 (Low) |
| **Package** | `numista_mobile/pubspec.yaml` transitive deps |
| **Dependency Type** | **TRANSITIVE** |
| **Fix Version** | `flutter pub upgrade` |
| **Context** | **Mobile app** — runs on user devices, isolated from server data |

**Fix:**
```bash
cd numista_mobile
flutter pub upgrade
```

---

## 📊 Vulnerability Summary Table

| ID | Package | CVE | Severity | Direct/Trans | Context | Fix Version |
|---|---|---|---|---|---|---|
| **H-1** | starlette | CVE-2026-48710 | 🔴 CRITICAL | DIRECT | Prod API ⚠️ | starlette≥1.0.1 via fastapi≥0.116.0 |
| **H-2** | Pillow | CVE-2025-48379 + 4 | 🔴 HIGH | DIRECT | Prod API ⚠️ | Pillow==12.3.0 |
| **H-3** | curl_cffi | CVE-2026-33752 | 🔴 HIGH | DIRECT | Prod + Dev | curl_cffi==0.15.0 |
| **H-4** | protobuf | CVE-2026-0994 | 🔴 HIGH | DIRECT | Prod (low risk) | protobuf==5.29.6 |
| **H-5** | xlsx (npm) | CVE-2023-30533 | 🔴 HIGH | DIRECT | Dev-only | CDN tarball or exceljs |
| **H-6** | PyPDF2 | Abandoned | 🔴 HIGH | DIRECT | Prod API ⚠️ | pypdf==6.13.3 (needs code change) |
| **H-7** | requests | CVE-2026-25645 | 🟠 HIGH/Med | DIRECT | Prod (low risk) | requests==2.34.2 |
| **H-8** | starlette | CVE-2025-62727 | 🔴 HIGH | DIRECT | Prod API | (Fixed by H-1) |
| **M-1** | grpcio | CVE-2026-33186 | 🟠 MOD | DIRECT | Prod (low risk) | grpcio==1.73.0 |
| **M-2** | yfinance | Transitive | 🟠 MOD | DIRECT | Prod | yfinance==1.4.1 |
| **M-3** | gevent | Transitive | 🟠 MOD | DIRECT | Dev-only | gevent==26.0.0 |
| **M-4** | botasaurus* | Transitive | 🟠 MOD | DIRECT | Prod+Dev ⚠️ | Upgrade to latest |
| **M-5** | playwright (py) | CVE-2025-59288 | 🟠 MOD | DIRECT | Dev-only | playwright==1.54.0 |
| **M-6** | playwright (npm) | Transitive | 🟠 MOD | DIRECT | Dev-only | playwright@latest |
| **L-1** | feedparser | Minor | 🟡 LOW | DIRECT | Prod (no risk) | Monitor |
| **L-2** | python-dotenv | Minor | 🟡 LOW | DIRECT | Prod (no risk) | Monitor |
| **L-3** | Flutter deps | Various | 🟡 LOW | TRANSITIVE | Mobile | flutter pub upgrade |

---

## 🚦 Prioritized Fix Order

### Phase 1 — Fix in Current Sprint (24–48 hours) · Production API Risk

**1. Starlette / FastAPI (CVE-2026-48710 — Authentication Bypass)**
```bash
# requirements.txt changes:
# fastapi==0.115.12  →  fastapi==0.116.1  (or latest >=0.116.0)
# starlette==0.46.2  →  starlette==1.0.1  (let fastapi manage this, or pin explicitly)
pip install "fastapi>=0.116.0" "starlette>=1.0.1"
```

**2. Pillow (multiple buffer overflows)**
```bash
# requirements.txt + requirements-dev.txt:
# Pillow==11.2.1  →  Pillow==12.3.0
pip install "Pillow>=12.3.0"
```

**3. curl_cffi (SSRF + bundled libcurl)**
```bash
# requirements.txt + requirements-dev.txt:
# curl_cffi==0.11.1  →  curl_cffi==0.15.0
pip install "curl_cffi>=0.15.0"
```

**4. requests (temp file security)**
```bash
# requirements.txt:
# requests==2.32.4  →  requests==2.34.2
pip install "requests>=2.34.2"
```

---

### Phase 2 — Fix This Week · Infrastructure Hardening

**5. protobuf (DoS via recursion)**
```bash
# requirements.txt:
# protobuf==5.29.4  →  protobuf==5.29.6
pip install "protobuf>=5.29.6"
```

**6. grpcio / grpcio-status (auth bypass)**
```bash
# requirements.txt:
# grpcio==1.71.0  →  grpcio==1.73.0
# grpcio-status==1.71.0  →  grpcio-status==1.73.0
pip install "grpcio>=1.73.0" "grpcio-status>=1.73.0"
```

**7. yfinance (transitive SSL)**
```bash
# requirements.txt:
# yfinance==0.2.62  →  yfinance==1.4.1
pip install "yfinance>=1.4.1"
```

**8. botasaurus — Consider moving to dev-only**
```bash
# Move botasaurus, botasaurus_requests, botasaurus_driver, curl_cffi
# OUT of requirements.txt and INTO requirements-dev.txt
# This prevents Chromium+libcurl from being deployed to Cloud Run unnecessarily
```

---

### Phase 3 — Fix Next Week · Dev-Environment & Long-Tail

**9. xlsx (npm) — Replace with CDN or ExcelJS**
```json
// numista_backend/package.json
"xlsx": "https://cdn.sheetjs.com/xlsx-0.20.2/xlsx-0.20.2.tgz"
```

**10. gevent / geventhttpclient (requirements-dev.txt)**
```bash
pip install "gevent>=26.0.0" "geventhttpclient>=2.4.0"
```

**11. Playwright (Python dev + npm root)**
```bash
pip install "playwright>=1.54.0"     # requirements-dev.txt
npm install playwright@latest        # root package.json
```

**12. Flutter mobile app**
```bash
cd numista_mobile && flutter pub upgrade
```

---

### Phase 4 — Source Code Required (Separate PR)

**13. PyPDF2 → pypdf migration**
This requires updating Python imports in `main.py`:
```python
# Before:
from PyPDF2 import PdfReader
# After:
from pypdf import PdfReader
```
```bash
pip install "pypdf>=6.13.3"
# requirements.txt: replace PyPDF2==3.0.1 with pypdf==6.13.3
```

---

## 🛠️ Exact Upgrade Commands

### Production `requirements.txt` (Phase 1–2 only — no source changes)

```bash
cd c:\Users\ericd\Documents\MyVertexProject\numista_backend
pip install \
  "fastapi>=0.116.0" \
  "starlette>=1.0.1" \
  "Pillow>=12.3.0" \
  "curl_cffi>=0.15.0" \
  "requests>=2.34.2" \
  "protobuf>=5.29.6" \
  "grpcio>=1.73.0" \
  "grpcio-status>=1.73.0" \
  "yfinance>=1.4.1"
```

### Dev `requirements-dev.txt` additional packages

```bash
pip install \
  "gevent>=26.0.0" \
  "geventhttpclient>=2.4.0" \
  "playwright>=1.54.0"
```

### npm (root `package.json`)

```bash
cd c:\Users\ericd\Documents\MyVertexProject
npm install playwright@latest
```

### npm (backend `numista_backend/package.json`)

```bash
cd c:\Users\ericd\Documents\MyVertexProject\numista_backend
npm install "https://cdn.sheetjs.com/xlsx-0.20.2/xlsx-0.20.2.tgz"
```

### Flutter mobile

```bash
cd c:\Users\ericd\Documents\MyVertexProject\numista_mobile
flutter pub upgrade
```

---

## ⚠️ Important Notes

1. **Starlette 1.0.1 is a major version bump.** FastAPI `>=0.116.0` is required to safely use it. The `starlette` pin in `requirements.txt` should be updated in lockstep with `fastapi`.

2. **botasaurus in production is a footgun.** Having full Chromium + libcurl bundled in the Cloud Run image inflates both the attack surface and the image size. Consider whether it's actually needed at runtime or only in dev scripts.

3. **PyPDF2 cannot be fixed by version pin alone.** It requires source code changes. Do not commit it in Phase 1 — schedule it as a tracked engineering task.

4. **The ~60 "remaining" Dependabot alerts** after these 17 distinct issues are resolved are **transitive-only** — Dependabot often counts every package in the dependency chain once per vulnerability. Fixing the root packages above will automatically resolve most of the 71-alert total count.

5. **After pushing fixes:** Re-run `pip audit` or `safety check` locally to confirm zero remaining known CVEs in the installed environment:
   ```bash
   pip install pip-audit
   pip-audit -r numista_backend/requirements.txt
   ```
