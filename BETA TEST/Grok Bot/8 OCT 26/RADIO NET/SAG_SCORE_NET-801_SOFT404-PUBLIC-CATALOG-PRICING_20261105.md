# SAG SCORE NET-801 (xAI API, grok-4.7, 2026-11-05 ET)

## SAG_SCORE: 68/100 FAIL
## MUST_FIX (blocking before Eric YES; or NONE blocking)
1. Do not lock **5,142** into titles, meta, badges, or Option A. Homepage 5,142 ≠ entries_master **3202** (coin 2965 + note 181 + medal 56). MISSING_IMAGES=3202 (= full master). Real mismatch. Nothing invented. Reconcile the public number before any catalog or ad copy.
2. Thanksgiving Meta ads are #1. JS `document.title` / `pushState` does not feed non-JS scrapers. Plan must require static `<title>` plus `og:title` / `og:description` (S404-2) and prove them on a **preview** HTML body, not `curl -I` of live.
3. Public values are unbound. If any value is shown: **CDN CPG retail only**. Never wholesale, never Greysheet wholesale, never AI-primary. Plan does not bind this.
4. Image rule unbound. `ai_replica_images` never primary. No hotlinks. MISSING_IMAGES covers the full master, so “high-resolution imagery” must not ship as fact. Missing stays placeholder.
5. Eric must **type A, B, or C**. CoS “recommend A” is not a decision. Option C must not skip that typed choice.
6. Standing controls missing: hard **$cap**, **rollback**, **preview-before-live**. Section 6 probes production `numista-vault.web.app`. Do not treat that as the gate.
7. Defect D is not fixed. §4.4 still uses `InkWell` and does not add real `<a href>`, so middle-click / new-tab still fails.
8. Drop unsourced **99.4%** and the claim of **5,000+ indexable pages**. SPA rewrite to `index.html` does not create those pages.
## NON_BLOCKING
- Routing and AuthGate diagnosis match the cited `firebase.json`, `main.dart`, `auth_gate.dart`, and `login_screen.dart` lines. Plan-only, `main` @ `9f04550a`, Stripe OFF, zero Firestore writes: stated and held.
- S404-1: on integrate, keep `dev` `/catalog` and `/catalog/:nacCode` → `CatalogBrowseScreen`. Do not clobber that from `p7-v8.9`.
- `gs://numista-reference-library` is asserted, not evidenced in the audited files. Do not treat the bucket as verified.
- `FirebaseAuth.instance.currentUser` inside `build` will not track auth changes; use the existing auth stream when this is executed.
- PIN/password labels, jargon, and footer semantics are fine once unsourced stats are removed.
## PII_FINDINGS
Plan text: no collector PII, no AJ, no emails, no account data. Argon review embeds a local path with Windows username `ericd` plus a reviewer UUID. Do not republish that path. No AJ token in either file.
## 2_SENTENCE_PLAIN_ENGLISH (for Eric)
The plan correctly finds the broken Pricing path and the missing /catalog route, but it is not ready for your YES. It still sells 5,142 coins when the master list is 3,202, and it does not lock Meta ad titles, retail-only public prices, image rules, a spending cap, rollback, or a preview before anything goes live — you must type A, B, or C yourself.
## RATIONALE (brief)
Argon 96/100 demoted launch blockers to notes. SAG does not. Soft-404 and AuthGate root cause are real; the executable package is not. It hardcodes a false count, misses static OG titles required for 26 Nov Meta, leaves public values and images unbound (CDN CPG retail only; `ai_replica_images` never primary; no hotlinks), and omits $cap, rollback, and preview-before-live. Option A is a recommendation, not authorization. PASS bar is 95. This is FAIL until those locks are in the plan and you type A, B, or C.
