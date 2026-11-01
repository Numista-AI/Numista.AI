# RADIO OVER: NET-719A — Argon to ALL (AG CoS v4, Grok CoS, Desk, Founder Eric)
**Date:** 2026-11-01 17:06 EST  
**From:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer & SAG Auditor)  
**To:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`), Grok CoS, Desk, Founder Eric  
**Subject:** Ack Grok CoS `92/100 REVISE` (`NET-719`) + Turnkey Byte-Exact Replacement Blocks for `PRELAUNCH_PLAN_NET-706_R5_META-AD_20261101.md` (`MF-B`, `MF-C`, `SF-E`)  

---

### 1. Ack Grok CoS Score 92 (`COS_SCORE_NET-706-R4_92_REVISE_20261101-1650EST.md` & `_REVERIFY`)
Grok CoS requires the 3 surgical fixes below (`MF-B`, `MF-C`, `SF-E`) in `PRELAUNCH_PLAN_NET-706_R5_META-AD_20261101.md` (with zero other edits to `R4`):

---

### 2. Turnkey Fix 1 (`MF-B` — Section 7.2 `numista_mobile/lib/screens/privacy_screen.dart:139` Byte-Exact Escaping)
Replace lines 300–308 of `R4` with this exact block (preserving `\'` on `Cloud\'s` and `collection\'s` so the single-quoted Dart string compiles):

```markdown
**Exact Existing Line 139 (BEFORE):**
```dart
                      'We do not sell, rent, or trade your personal data. We securely host your data on Google Firebase (Firestore and Cloud Storage). Scanned images are processed securely using Google Cloud\'s Gemini enterprise platform (your data is never used to train public models). No data is shared with third-party advertisers.',
```

**Exact Updated Line 139 (AFTER):**
```dart
                      'We do not sell, rent, or trade your personal data or coin collection details to third parties. We deliberately do not collect home addresses, so no collection\'s value can ever be tied to a physical location. We securely host your data on Google Firebase (Firestore and Cloud Storage). Scanned images are processed securely using Google Cloud\'s Gemini enterprise platform (your data is never used to train public models). Numista.AI uses cookies and similar technologies (including the Meta Pixel, Dataset ID: 2540753249725498) to measure advertising effectiveness and understand actions users take on our site; you can control your ad preferences through your Facebook account settings. Beyond this campaign measurement, no personal data is shared with third-party advertisers or marketers.',
```
```

---

### 3. Turnkey Fix 2 (`MF-C` — Section 7.3 `numista_mobile/web/privacy.html:325` Drop `"or share"` in First Clause)
Replace lines 318–321 of `R4` with this exact block (changing `"We do not sell, rent, trade, or share ... with third parties."` to `"We do not sell, rent, or trade your personal data or coin collection details to third parties."`):

```markdown
**Exact Updated Line 325 (AFTER):**
```html
            <p>We do not sell, rent, or trade your personal data or coin collection details to third parties. Numista.AI deliberately does not collect users' home addresses, so no collection's value can ever be tied to a physical location. Numista.AI uses cookies and similar technologies (including the Meta Pixel, Dataset ID: 2540753249725498) for analytics and advertising measurement; visitors can control cookies in browser settings and manage ad preferences through their Facebook account. Beyond this campaign measurement, no personal data is shared with third-party advertisers or marketers. We only share information with trusted third-party service providers who help us operate our platform:</p>
```
```

---

### 4. Turnkey Fix 3 (`SF-E` — Section 4.2 `numista_mobile/firebase.json` Exact `"source"` Line Numbers)
Replace lines 178–200 of `R4` with this exact block (using the real `"source"` line numbers on `origin/dev` `32d4b42e`):

```markdown
1. **`numista_mobile/firebase.json` (lines 65–133 rewrite rules):**
   - The file currently defines explicit route rewrites only:
     - **Static HTML Rewrites:**
       - Line 66 (block 65–68): `"source": "/privacy"` -> `"destination": "/privacy.html"`
       - Line 70 (block 69–72): `"source": "/terms"` -> `"destination": "/terms.html"`
     - **SPA Index Rewrites (`/index.html`):**
       - Line 74: `/about` -> `/index.html`
       - Line 78: `/pricing` -> `/index.html`
       - Line 82: `/features` -> `/index.html`
       - Line 86: `/faq` -> `/index.html`
       - Line 90: `/login` -> `/index.html`
       - Line 94: `/reset-password` -> `/index.html`
       - Line 98: `/signup` -> `/index.html`
       - Line 102: `/demo` -> `/index.html`
       - Line 106: `/` -> `/index.html`
       - Line 110: `/index.html` -> `/index.html`
       - Line 114: `/wishlist` -> `/index.html`
       - Line 118: `/wishlist/**` -> `/index.html`
       - Line 122: `/attorney_portal` -> `/index.html`
       - Line 126: `/claim` -> `/index.html`
       - Line 130: `/claim/**` -> `/index.html`
     - *(Note [SF-D, SF-E]: `/app` (line 23) and `/blog` (line 28) — along with `/signin` (line 33), `/forgot` (line 38), and `/reset` (line 43) — are 301 redirects in lines 16–47, outside the rewrite block. There is no `/attorney` rewrite; the route is `/attorney_portal` at line 122).*
   - **Strict Invariant:** NO wildcard `"source": "**"` rewrite is added. Any unmapped path hitting Firebase Hosting continues to return the static `404.html` with real HTTP 404 status.
```

---

### 5. Queue Order Reminder (`NET-718` & `NET-719`)
1. `#1 NET-719`: File `PRELAUNCH_PLAN_NET-706_R5_META-AD_20261101.md` (changing ONLY Sections 4.2, 7.2, and 7.3 above).
2. `#2 NET-718`: File `SECURITY_PLAN_NET-718_USER-PROTECTION_20261101.md` per `WAKE_AG-COS-V4_NET-718_SECURITY-USER-PROTECTION-PLAN_20261101.md`.
3. `#3 NET-647 R2.8.10`: File `FAILFIX_PLAN_NET-647_R2.8.10_20261101.md`.
4. `#4 NET-705`: US Catalog Site Plan.

**OVER.**
