# DONE: `BATON_NET-803_REVISE_FAILFIX_NET-777_CATALOG_v1.3_PER-SAG-75_2026-11-05-1342.md`

- **To:** Grok Bot Chief of Staff, Argon (Gemini 3.8), Stand Alone Grok (SAG), Founder Eric
- **From:** Antigravity CoS v4 Work (`ba2bfdb2`)
- **Date / Time:** 2026-11-05 1:55 PM ET
- **Status:** **DONE (`PLAN ONLY` — Zero code modifications, zero deployments, zero Firestore writes/seeding)**
- **Target Deliverables Filed:**
  1. `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.3.md` (and mirrored to `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/`, `BETA TEST/Grok Bot/8 OCT 26/BATONS/`, and `RADIO NET/`)
  2. `docs/MISSING_IMAGES.csv` (scrubbed, verified 100% clean, mirrored to all 3 repositories)

---

## Summary of SAG-75 Resolutions in Plan v1.3

1. **SAG Must-Fix 1 (Catalog-First AI Rule):**
   - Bound into §2.B & §7.B: AI replicas may live strictly and only in labeled `ai_replica_images` metadata field; strictly forbidden from `primary_image`, `type_image`, card art, or browse index. Primary image must strictly be authentic numismatic photography.
2. **SAG Must-Fix 2 (Rollback + Preview-Before-Live Gate):**
   - Bound into §8: Full GCS asset versioning rollback, `gsutil rm` command for corrupted objects, Git revert procedure for `firebase.json` and catalog JSON files, and mandatory Field Tester gate on Firebase Preview Channel (`firebase hosting:channel:deploy pre-ads-preview`) before any production release.
3. **SAG Must-Fix 3 (CSV Hygiene & Match Claims):**
   - Reclassified all 81 `EXTERNAL_MIRROR_PENDING` blank-source rows to `MISSING` / Tier 1 Internal Staged Scan (zero unvetted collection seeds in public GCS).
   - Extracted true mint marks (`S`, `D`, `P`, `O`, `W`, `CC`) from `nac_code` across all 1,965 rows that had boolean `mint_mark = True`.
   - Scrubbed 15 collector album marketing titles into canonical series.
   - Restored cost column to `$0.00` across all 3,202 rows.
   - Dropped unproven "100% sourced" and "248 identified" claims; accurately described as candidate acquisition targets.
4. **SAG Must-Fix 4 (Hard Monthly $ Cap + Billing Alert):**
   - Bound into §2.E: Established hard monthly cap of **$25.00/month** covering GCS storage + Cloud CDN egress under Meta advertising traffic with automated Google Cloud Monitoring billing alerts at 80% ($20.00/month) and 100% ($25.00/month). Tier 4 studio photography is strictly existing owned photos ($0.00), no new spending.
5. **SAG Must-Fix 5 (Fix 3 Signed-in Route Rewritten):**
   - Bound into §4.C: Eliminated the unregistered `launchUrl('/?route=AiChatScreen...')` call. Authenticated users directly open the native `MorganChatPopout` dialog (`lib/widgets/morgan_chat_popout.dart`), which is already registered and operational in the Flutter tree.
6. **Non-Blocking Items & Argon EX-1..EX-4:**
   - Deep link modal close uses `window.history.back()` / handles `popstate` to prevent modal desync (§3.C).
   - Versioned catalog JSON filenames (`catalog_index_v{timestamp}.json`) to avoid stale CDN caching during ad launch week (§7.C).
   - All 167 `candidate_source` URLs remain strictly internal acquisition notes—never rendered as `src` or `href` attributes (§2.C).
   - Softened signed-out Morgan preview copy to reflect real, tested capabilities (§4.C).
   - Branch guard enforced: work lands on `dev` first, never direct to `main` (§9).
   - One-line explicit statement: "Founder Eric's typed YES to this plan is strictly for code execution on `dev` and GCS asset upload on dev/preview — it is NOT an approval for Firestore database writes, seeding, or Firestore security rules changes."

---

## Standing Locks
- `origin/main` strictly locked at `9f04550a`.
- Stripe strictly locked OFF across all configurations.
- Zero live deployments; zero Firestore database writes or security rules changes.
