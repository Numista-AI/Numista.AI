# Writer handoff — Morgan proposals, NOT accepted catalog corrections
7 Nov 2026, 7:36 PM EST. Local report only.

**Status: PROPOSED CORRECTIONS PENDING INDEPENDENT PRIMARY VERIFICATION.**
Ten proposal rows in `proposed_corrections.csv` / `.json`. Nothing is accepted, merged, renamed or verified by this handoff. Read with original `gaps.csv`, `mapping_rule_checks.csv`, prior validation and dataset hashes, not as replacement history.

## Evidence and epistemic boundary
Read `/workspace/catalog-preview/morgan_verdicts_20261107.md` in full (45 content lines). SHA256:
`829555ce05acae180c344aee44b0ea582e0509d015ab42c352b9745479e4f787` (10,924 bytes).
Morgan:2,43–45 explicitly requires independent review. Morgan used search-index Mint copies, had a direct-fetch timeout (NOT confirmed 403), rejected a misleading search synthesis, and read a proclamation transcription rather than archival facsimile. Source claims/confidence are Morgan's, not new verification by this QA. Government-domain URLs and stored citations do not establish claim-level primary support. This pass opened no URLs and did not independently read the primary texts; supplied URLs are verification targets, never endorsements of verification.

## Work packages and acceptance
### P01–P03: 1796 half-cent authority roles and effective specifications
Record `NAC1.CN.US.HC.LIBCAP.1796.P.BASE.9`, LEGIS candidate **line23**.
Our internal A1792 [1793,1793] copper-rule incompatibility stands as a rule conflict, NOT proof foundational A1792 authority is irrelevant. Morgan:15–19 proposes:
- Retain A1792 denomination authorization **as amended**, separate from weight specification.
- Chain: 14 Jan1793 ch2, 1 Stat299 (104 grains); 3 Mar1795 ch47 §8, 1 Stat439/440 delegation; proclamation signed 26 Jan1796, claimed effective 27 Dec1795, 84-grain nominal half-cent standard.
- Verify each date, pinpoint, legal role and nominal-vs-specimen distinction independently. Do not broaden a single weight rule or invent an “Act of26 Jan1795.” No new authority ID assigned here.
Supplied source targets (Morgan:18):
- https://www.usmint.gov/learn/history/historical-documents/coinage-act-of-april-2-1792
- https://www.govinfo.gov/app/details/STATUTE-1/STATUTE-1-Pg299
- https://www.govinfo.gov/content/pkg/STATUTE-1/pdf/STATUTE-1-Pg439.pdf
- https://www.presidency.ucsb.edu/documents/proclamation-reduction-weight-the-copper-coin
The proclamation outside-government transcription still needs independent primary-document/pinpoint review. Prior P1796 NEEDS_PRIMARY_SOURCE is NOT automatically closed by this proposal.

### P04–P05: 1965 clad quarter and dime
Records `NAC1.CN.US.25C.WASHQCLAD.1965.XX.BASE.E` (**line1528**) and `NAC1.CN.US.10C.ROOSEVCLAD.1965.XX.BASE.F` (**line1530**).
Morgan:21–26 proposes replacement of A1866 composition/denomination role with existing **A1965**, Coinage Act of1965 **Pub.L.89-81 §101(a)(2)–(3),79 Stat254**, enactment **1965-07-23**. These are not five-cent coins merely because cladding contains copper/nickel. Do not broaden A1866 coverage to mask the conflict.
Independently check subsection-to-denomination, mass and cladding/core language. 75/25 is proposed cladding alloy, not whole-coin composition. Prior July22/23 OCR discrepancy remains a reconciliation task, not silently resolved by this report.
Supplied targets (Morgan:25):
- https://www.congress.gov/89/statute/STATUTE-79/STATUTE-79-Pg254.pdf
- https://fraser.stlouisfed.org/title/coinage-act-1965-1123/fulltext
- https://www.congress.gov/bill/89th-congress/senate-bill/2080

### P06–P08: Three-Cent Nickel identity quarantine and possible ID defect
Record `NAC1.CN.US.5C.THREECENTN.1866.P.BASE.0`, **line347**.
Observed local inconsistency remains: name/series Three-Cent Nickel, denomination5 cents. Morgan:28–33 conditionally proposes **3 cents**, retain1866 and A1865 **only if intended name/series identity is independently confirmed**. Morgan:32 cites 3 Mar1865 ch100 §1,13 Stat517 (three-cent copper-nickel piece). No image/item evidence resolves identity; 1866 fits both Three-Cent and Shield nickels. Do not reclassify to Shield from prefix alone. Mintmark boolean `true` is a separate verification item: Philadelphia facility P token does not prove an actual P mark.
Verification target: https://www.govinfo.gov/content/pkg/STATUTE-13/pdf/STATUTE-13-Pg517.pdf
Supporting Mint history URLs are in proposal rows/Morgan:32; no direct page verification performed here.

**ID migration is NOT a denomination-only edit.** If three-cent identity is confirmed, 5C prefix may be defective. No replacement NAC, checksum or alias computed/promoted. Required separate plan: canonical token/check rules; collision scan; stable-ID continuity/aliases/redirect policy; all inbound/outbound catalog, collection, social, candidate/export references; idempotency, rollback and audit trail. Require independent identity review, reviewed stable-ID/alias/reference migration plan and **separate explicit approval** before any rename/reference changes. If original object evidence instead proves five cents, name/series/authority corrections require their own reviewed proposal.

### P09–P10: keep citation backlogs separate
Independently recounted raw snapshots; Morgan:35–40 arithmetic matches:
- Older LEGIS candidate: **3,203 cards; 2,378 distinct cards** with at least one empty citation.
- These contain **2,615 empty embedded links across33 distinct authority IDs**.
- **2,570 links** point to IDs whose later proposal citation field is populated. That is potential reviewed propagation work, NOT automatically verified links or permission to fold.
- **45 links** remain tied to uncited authorities: P1796=30, A1853b=3, A1942=12.
- Newer6Nov proposal: **3 of38 authority records** uncited: P1796 **line3**, A1853b **line9**, A1942 **line22**. One is a proclamation, so “3 Acts” is imprecise.
- Older5Nov proposal:37 of38 uncited;34 authority-level fields populated later. Old embedded cards were not thereby updated.
`citation_backlog_crosswalk.csv` has all2,615 old-link source lines, stable card IDs, nested indexes and newer proposal row locators. Links/cards/authority rows are separate measures, not accuracy metrics.

Prior limits persist: A1942 nickel text does not establish1943 steel-cent authority; A1853b needs exact primary citation; P1796 primary-text identity/date/weight requires independent review. Prior108 STILL_BELOW_THRESHOLD rechecks were not rerun and are not108 disproven laws. Wrong/truncated source windows and date concerns in prior validation remain open. Do not mark all act links VERIFIED or copy citation-status wholesale merely because a citation exists.

## Safe writer scope and files
Writer can prepare plan-only diffs and verification checklist; this pack authorizes no implementation. No master/RP/LEGIS/proposal mutation, repo/app runtime, external messaging, network/cloud/paid calls, extraction, indexing, deletes or deploys in this pass.
- `proposed_corrections.csv` / `.json`:10 rows, old/proposed fields, exact Morgan line ranges, primary targets, verification tasks and acceptance conditions.
- `citation_backlog_crosswalk.csv`:2,615 source-link locators.
- `morgan_proposal_evidence.json`: verdict hash, five unchanged input hashes, arithmetic.
- `propose_morgan.py`: reproducible additive report script.
All five catalog/proposal SHA256s match original audit inventory and were rechecked after processing. Prior audit outputs/history preserved; BLUF appended with this handoff rather than rewriting original findings.
