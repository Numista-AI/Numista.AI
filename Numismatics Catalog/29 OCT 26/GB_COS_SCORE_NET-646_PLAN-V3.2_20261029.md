# GB CoS Score: NET-646 Plan v3.2
Scored by: Grok Bot (Chief of Staff) | 7:16 PM ET, 29 Oct 2026 | Docs only
Inputs: US_NUMISMATICS_CATALOG_IMPLEMENTATION_PLAN_V3.2.md + NET-646_V3.0_APPENDIX_WRITE_AUDIT.md

## Score: 96 / 100 (GO for planning, pass mark 95). Trend: 88, 89, 93, 96.
GO means the plan is ready for Eric's typed YES to start P0. SAG has not scored v3.2: the box launch was blocked, so a paste packet was filed.

## v3.1 blockers
| # | Blocker | Status |
|---|---|---|
| 1 | Set fields client-editable after P3; group assumed 4:1 | CLOSED. Server-only set_shell_id from P1, in _serverAssignedKeys with an R5 test. At P3 is_set/set_id/parent_set_id/set_contents are update-denied on all three collections. Group/ungroup use each child's clamped stored weight (signed delta; weight-1 child adds 0). Before P3 only a valid server link weighs 1, and the nightly recount re-weights and alerts. |
| 2 | Top-ups dropped by the high-water-mark check | CLOSED. One-time payments skip the check and use the event-id marker plus grant in one transaction; an ineligible account goes to stripe_unresolved for a refund by hand. |
| minor | Restore on a read-only account | CLOSED. Allowed, with no lifetime charge. |

## 7:08 PM founder answers: all reflected
Guest AI cap $0.10 (100000 micros); AJ ai_cap_exempt; top-up $5/1,000 forfeited on cancel and not restored on re-subscribe; basic export = zip of CSV plus own photos, with no expiring links; full export 6x monthly of last tier ($29.94/$53.94/$65.94/$95.94); snapshot owned by Grok CoS with a dry run the day before. The billing gate also waits for snapshot_done (a sensible addition).

## Remaining items (not blocking)
- Pending Eric (not scored): full export for never-paid accounts (402 NO_PRICE), Legacy top-ups without a subscription, hand refunds, the full founder email address, and creating 13 Stripe prices.
- Wording to tidy: §4.4 says a Legacy account's top-up credits bought while paying are forfeited when the subscription ends, while §12 Q2 assumes Legacy credits are kept with no subscription. That is consistent, but tell Eric both cases in one line.
- Process: Grok CoS owns the Nov 27 05:00Z snapshot run. That needs a scheduled routine plus Eric's YES for the run.

## Verdict
GO at 96 (planning). Execute still needs the P0 inventory verified, Eric's typed YES, and ideally the SAG score.
