# BATON: `BATON_NET-805_ARGON_REVIEW_780b-780c_v1.2_2026-11-05-1540.md`

- **From:** Antigravity CoS v4 Work (`ba2bfdb2`)
- **To:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Gemini 3.8 Code & Data Auditor)
- **Date / Time:** 2026-11-05 3:40 PM ET
- **Priority:** HIGH — 780b Cards & 780c Images Failfix Revision v1.2
- **Mode:** **REVIEW ONLY (`NO EXECUTE`)** — Zero code modifications, zero deployments, zero Firestore writes/seeding.
- **Reference Batons:**
  - `BATON_NET-805_REVISE_780b-780c_v1.2_PER-COS-82-SAG-67_2026-11-05-1455.md`
  - `BETA TEST/Grok Bot/8 OCT 26/BATONS/COS_SCORE_NET-791_FAILFIX-780b-780c-v1.1_20261105.md` (CoS 82 FAIL / SAG 67 FAIL on v1.1)
- **Target Files for Argon Review:**
  1. `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.2.md` (mirrored across `INBOX/`, `BATONS/`, and `RADIO NET/`)
  2. `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.2.md` (mirrored across `INBOX/`, `BATONS/`, and `RADIO NET/`)
  3. `BETA TEST/Grok Bot/8 OCT 26/BATONS/DONE_BATON_NET-805_REVISE_780b-780c_v1.2_2026-11-05-1535.md`

---

## Instructions for Argon (Gemini 3.8):
1. Audit both revised plans against the CoS/SAG must-fixes:
   - **780b Cards:**
     - Nickel regex boundary fixed (`r'(?:\b5c\b|5¢|\bfive cents?\b|\bnickel\b)'`) without trailing `\b` after `¢`.
     - Strict CDN CPG retail rule bound; zero unlabeled AI fallback; missing/$\le 0$ values render styled gold `'Valuation Pending'` chip.
     - NGC cert redacted to `"[cert no. redacted]"`; demo figures removed.
     - Rollback section added with pinned revert to `9f04550a`.
   - **780c Images:**
     - Census synchronized to `docs/MISSING_IMAGES.csv` (2,354 / 639 / 181 / 1 / 27 = 3,202).
     - Strict own-origin allowlist guard in memory before fetch; zero outside hotlinks.
     - Anchored folder-prefix regex for PII intake; zero false hits on `"American"` or `"Ajax"`; personal folders kept in local config.
     - Manifest tooling explicitly marked as to-be-created implementation artifacts; `NAC1.*` canonical primary keys.
     - Rollback section added with pinned revert to `9f04550a`.
   - **Cross-Cutting:**
     - Catalog-First AI rule bound (`ai_replica_images` only; `numista-uploads-studio` excluded).
     - US-only intake scope; $0.00 spend cap; no wholesale pricing; 26 Nov 2026 launch cut noted.
2. File review as `ARGON_REVIEW_NET-780_FAILFIX_v1.2.md` in `INBOX/`, `BATONS/`, and `RADIO NET/`.
3. Next in chain: Grok Bot CoS (`>= 95`) -> Stand Alone Grok (SAG, `>= 95`) -> Founder Eric typed YES.
