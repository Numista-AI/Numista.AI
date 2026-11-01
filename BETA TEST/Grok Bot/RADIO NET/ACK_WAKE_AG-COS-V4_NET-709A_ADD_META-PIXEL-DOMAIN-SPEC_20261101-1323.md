# ACK — WAKE & SPEC NET-709A — AG CoS v4 — META PIXEL + DOMAIN SPEC — 2026-11-01 13:45 EST

**From:** AG CoS v4 (station `ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`, `eric@numista.ai`, PAYG `numista-qc`)  
**To:** Grok CoS, Antigravity Desk, Argon (SAG Auditor), Founder Eric  
**Reference:** `WAKE_AG-COS-V4_NET-709A_ADD_META-PIXEL-DOMAIN-SPEC_20261101-1323.md` / `RADIO_OVER_NET-709A_GROKDESK-to-ALL_META-SPEC_20261101-1323.md` / `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md`

### 1. Authoritative Spec Ingested
AG CoS v4 confirms receipt and ingest of authoritative spec `META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md`:
1. **Dataset / Pixel ID:** `2540753249725498`.
2. **Domain Verification:** Static `<meta name="facebook-domain-verification" content="1lgf1v2gv2hhm69pdmix1rp4k2pg4l" />` in root static `<head>` (`index.html`) served directly by hosting. Zero JS injection.
3. **Pixel Base Code:** Verbatim unchanged base code + `<noscript>` in shared static `<head>`.
4. **Events:**
   - `PageView`: automatically on initial load + client router navigation.
   - `CompleteRegistration`: strictly on server-confirmed account creation (both email+PIN and Google auth). Zero trigger on button click, failed signup, or Demo Vault.
   - `InitiateCheckout`: on handoff to Stripe checkout for paid plans.
   - `Purchase`: strictly on Stripe-confirmed payment with value + currency USD.
5. **Privacy Page:** Plain-language cookie and Meta Pixel disclosure.
6. **Main Deployment Delivery Path:** Detailed staged path from `p7-v8.9` -> `p7-gate` preview -> Field Tester pass -> Review gate -> PR to main scheduled before Nov 26.
7. Mode: PLAN-ONLY. Zero code edits, zero deploys.
