# Primary authority record: Eric's go-live answers, 10 Nov 2026 (filed by Grok Bot CoS, 10:35 AM ET)
All quotes below are verbatim from Eric's own messages and card answers in the Chief of Staff Grok Bot chat.

1. 10:06 AM ET, answer to card t2455s9467, which asked "Deploy Catalog Chunk 1 to the p7-gate preview site only, so Field Tester can test it? Main, production, Firestore, Stripe and the catalog fold stay excluded.":
   "YES, deploy Catalog Chunk 1 (p7-v8.9 at c547b7a0) to the p7-gate preview channel only; no main, production, Firestore, Stripe or catalog fold"
2. Card t2462s9497 (10:20 AM ET) asked "Build the Stripe checkout (NET-827 v1.2) on the p7-gate preview, after the catalog check, using Stripe test mode only?" Option A was labeled "YES, build NET-827 v1.2 on p7-gate preview, test mode only", with the value "YES, build NET-827 v1.2 on the p7-gate preview after the Catalog Chunk 1 field test; Stripe test mode only, live OFF, no main, no production".
   Eric replied in chat at 10:29 AM ET (t2465u): "A, but if Field Tester passes it in the 90+ range, lets go live, we need to start testing stuff 'Real World'"
3. 10:32 AM ET, answer to card t2465s9506, which asked "If Field Tester scores 90 or higher, what goes live?":
   "If Field Tester scores 90+, deploy both to live numista.ai and turn on real Stripe payments"

Production details in the addendum (targeted fold, Secret Manager, Stripe prerequisites, the wrong-charge stop rule, and the Christmas code staying off before 26 Nov 00:00 UTC) are CoS-specified safeguards within that authority. The trigger stays NOT ACTIVE until CoS confirms in writing that each Field Tester result is 90 or higher.
