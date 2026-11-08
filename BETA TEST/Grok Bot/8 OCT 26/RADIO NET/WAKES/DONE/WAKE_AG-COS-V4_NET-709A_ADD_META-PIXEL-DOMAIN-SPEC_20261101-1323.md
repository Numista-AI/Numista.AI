# WAKE AG CoS v4 (ba2bfdb2) - NET-709A ADDENDUM: Meta Pixel + Domain Spec

Source: Chief of Staff relaying Eric, 1:22 PM ET, 1 Nov 2026.

- AUTHORITATIVE pixel + domain-tag section of the NET-706 Meta plan: INBOX\META_PIXEL_DOMAIN_SPEC_NET-706_ERIC_20261101.md (Dataset/Pixel ID 2540753249725498). Do not edit the spec.
- Meta domain-verification tag and pixel base code go VERBATIM into the served static <head>. No JS injection.
- Events: CompleteRegistration only on server-confirmed signup; InitiateCheckout on Stripe handoff; Purchase only after Stripe confirms payment.
- Privacy page gets a cookie line.
- NOT a direct paste task: plan -> Argon -> GB CoS 95+ -> SAG -> Eric typed YES -> test on p7-gate -> live.
- Plan must state how the tag reaches main's served HTML before Thu 26 Nov.
- PLAN-ONLY. Locks unchanged: main/live 9f04550a, dev 9b55f3d9, Stripe OFF, HOLD 586-590 held. No execute, deploy, or push.
- Queue unchanged: 1) NET-706 Meta, 2) NET-647 R2.8.10 fix-only, 3) NET-705 catalog. ACK still due ~3:15 PM ET.
