# NET-024 GROKCOS to AGCOS: $500 DEV CREDIT - DEV-ONLY ORDER (13 Oct 2026 ~12:25 PM ET)
**LOW PRIORITY: after T1B.** Do not start until T1B is OUT. Dev only. READ-ONLY + proposal. NO billing changes, NO deploys, NO IAM changes. Eric gives a typed YES for each change, one at a time.

## Goal
Use Eric's $500 Google Developer Program credit before it expires **29 Dec 2026**. It sits on billing account **My Billing Account (01A29C-F9BA5A-442E6B)** and covers all of GCP. Also $18 Gemini credit there, same expiry. Production stays on **Numista.Ai (010E3C-D8346A-91A35E)** ($1,000 Agent Builder credit to 23 Jan 2027; Startups credit to 29 Jan 2028).

## Grok CoS read-only snapshot (gcloud on EDS_Laptop, 13 Oct ~12:22 PM ET) - verify, do not trust
- My Billing Account: numista-qc (billing on), gen-lang-client-0504730428 "V3Tees" (billing on)
- Numista.Ai: studio-9101802118-8c9a8 "AJ's AI Coin App" (billing on; gcloud default project; likely LIVE PROD - confirm), numista-morgan-pilot (billing on; $5 budget morgan-pilot)
- Other projects visible, billing not linked to either account: erics-trackers, independent-sight-xbnm3, several gen-lang-client-* (Golf, NFL, Trackman, Gemini, T-Shirt), sys-* Untitled.

## Task 1 - READ-ONLY inventory
For each project: billing account, enabled services, what runs there (Cloud Run / Functions / Firestore / Vertex / Gemini keys / Hosting), and which env it serves (prod / staging / dev / QC / Field Tester / beta load). Confirm the live production project from repo config (.firebaserc, deploy scripts, env files, API base URLs). Show where dev/test spend lands today (billing export or console cost table by project, last 30 days). Read-only commands only (list/describe/get).

## Task 2 - Proposal
Propose moving or running dev, staging, Field Tester and beta-load (3 Nov club beta) workloads on a My Billing Account project (numista-qc preferred, or a new numista-dev). Production stays on Numista.Ai. For each workload: current project, target project, exact commands/config changes, data it needs (synthetic or copied dev data only; no prod user data), keys/secrets it needs.

## Task 3 - Risks, rollback, spend
- Risks: anything pointing at prod by accident, cross-project IAM, API keys/quotas, Firestore data separation, credit not covering a SKU, what happens after 29 Dec (spend would fall to Eric's card -> plan cutover back or shutdown before then).
- Rollback per step.
- Expected monthly spend per workload, Oct-Dec, vs $500 + $18 remaining.

## Return
File EXECUTE_DONE_CREDIT500_INVENTORY.md + RADIO NET reply to GROKCOS; pass baton BATON_CREDIT500_DEV-SPEND to GROKCOS. Grok CoS scores, then bundles one YES request per change for Eric. OVER
