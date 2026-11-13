**SAG Independent Full-Plan Review — RSI-CONTROLS Process Controls Plan v1.4**

**Score: 97/100**  
**Disposition: REVISE** (one material finding; otherwise strong; no CRITICAL)

Reviewed the full A1 document (505 lines) as a whole. A1 SHA-256 reviewed: `f07505baa3e3a93c06d2950fba21a3a44d766168b47b7eb219a2c619f1a2172f`.

### Material Findings
**MATERIAL — Pilot velocity metric cohort-start ambiguity (metric validity)**  
- Anchors: A1 L346–347 (Packets-to-Dual-Pass formula counting “all writers, lineage inherited” + population = tracks/chunks “whose first counted packet was formally delivered within the window”), cross-referenced with §7.1 L337–342 (named candidates all have pre-pilot history: NET-810 v1.1+, NET-813 v1.4+, NET-814 v1.3+, NET-817 RP chunks), §7.3 L357/L364 (prospective-only language), L350 (metric distinct from 4/10 caps), and §4.2 L226–231 (parent lineage inheritance for chunks).  
- Why material: The primary improvement metric (the one the founder asked for) has an undefined start point on the exact pilot candidates named in the plan. A literal reading of “first counted packet” + “lineage inherited” can exclude every named ongoing track from the pilot population (empty set) or pull pre-pilot history into pilot velocity (contradicting the never-pooled / prospective rules). This makes the metric non-reproducible without an extra interpretation step. Cap accounting and rework-rate populations in §7.3 are cleaner; this one is not.  
- Minimal fix: Add one clarifying sentence at L347 (or immediately after the formula): “For the pilot cohort, the first counted packet is the first pilot-eligible delivered packet (next-eligible version or approved chunk) formally delivered within the window; parent/pre-pilot lineage is retained for audit and reported separately and is never included in the pilot Packets-to-Dual-Pass count.”

No other material or CRITICAL findings. The rest of the plan is tight.

### Explicit Checks
(a) Exact 4/10 rule is quoted correctly (L21 and L131 match the controlling Desk 1257 wording) and operative rules are consistent: writer retired after 4 terminal non-passing delivered tries (L146–147, §3.1 item 3), 10th review is permitted then hard halt with no 11th monolithic attempt (L190–200, §4.1 item 2), notify Eric + split proposal required (L201–205).  
(b) Attempt counting, terminal dispositions, and pending ≠ failed have no loophole: formal delivery alone counts (completeness/preflight/score independent, L133–134); four explicit terminal non-passing types (L141–143); gate owner records them and unrecorded stays pending (L144); supersession/withdrawal/SAY-AGAIN/unscored all trigger on the 4th (L146–147, table §3.2); one pending packet rule is a consequence of supersession, not a new gate.  
(c) Metric populations are coherent except for the pilot velocity cohort-start ambiguity noted above; rework-rate populations (L356–370) are clean (unique terminal delivered packets, pending excluded both sides, historical-unknown excluded, rate ≤100%).  
(d) No unverified fact is presented as verified: EVD-04–06/08 and script paths labeled WRITER-REPORTED/UNVERIFIED with true limits (L274–278, §0.1 items 5–8, §11 L487–496); baseline and main-lock honestly desk-asserted or writer-asserted (L271–273); prior-plan digests limited to box-copy matches (L279–281); illustrative counts labeled as such (L109, EVD-07).  
(e) Nothing implies execution, activation, or permission beyond plan-only: strict PLAN ONLY invariants (L92 and header), UNAPPLIED banner on watch text (L379–380), read-only schema (L414–423), Phase 2–4 gated on Eric scoped typed YES (L477–479), sign-off disclaims any change (L505).  
(f) No regression versus v1.3 safeguards: Stripe live OFF + track-scoped test-mode preserved (L95, L325); applicable gates and permitted skips (not universal 5-gate) preserved (§6.1, §6.3); empirical beta evidence required (Scope G); 4/10 non-toggleable (L410–411); override audit required (L412–413); schema read-only (L414–423); no instant-restore claim (L424–425); pilot ≠ permanent adoption (L428–429).

Non-scoring precision only (not scored, not blocking): §2.2 L120 still lists “ACK/Delivery” among gates while §6.2 matrix is G-1..G-5; L257 generic “git push” filing-time wording; §8.2 L385 “any AG submission” (replacement writer is not AG).

This review is independent, grants no execution/activation/permission of any kind, and is not a new plan attempt.
