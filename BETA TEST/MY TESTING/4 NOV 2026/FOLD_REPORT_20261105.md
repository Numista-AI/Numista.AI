# Legislation fold report — CANDIDATE only (5 Nov 2026 run)
Authorized by Eric's "The word" at about 8:40 PM ET on 4 Nov 2026. Script: `merge_legislation_scoped.py`
Output: `/workspace/catalog-preview/entries_master_LEGIS_CANDIDATE_20261105.jsonl`

## Counts
- Entries in: 3202 / out: 3202
- Entries with at least one legislation object: 2813 (389 have none)
- Act attachments: 2744 full-provision, 934 name-and-date only (total 3678). There are no unmapped act_ids.
- A1875 has 0 catalog attachments because the mapping CSV doesn't map it to any entry.

## Full objects (PROVISIONS_SUPPORTED, 24)
A1792, A1793, A1834, A1837, A1851, A1853a, A1853b, A1857, A1864, A1865, A1866, A1873, A1878, A1890a, A1918, A1934a, A1934b, A1942, A1965, A1970, A1973, A1978, A1985a, P1796

## Name-and-date only (14): act_id, act_name, date, status
A1849, A1890b, A1985b, A1996, A1997a, A1997b, A2003, A2005, A2007, A2008a, A2008b, A2018, A2020 (NEEDS_PRIMARY_SOURCE); A1875 (NUMBERS_SUPPORTED_LINK_TO_VERIFY)

## Spot checks (all passed)
- 10D CAPBUST 1795 → A1792 (full)
- D1 FLOWINGHAI 1795 → A1792 (full)
- 1D MORGANSILV 1878 CC → A1878 (full)
- 1C LINCOLNCEN 1943 WHEATZINC → A1864 + A1942 (both full)

## Safety
- Master untouched. MD5 before and after: 20261104 = 67c41aae…2038, 20261103 = 6164b138…8e39
- Nothing was written to Firestore, GCS, or production.
- Cost: $0. This was a local file merge with no Discovery or GCP calls.
