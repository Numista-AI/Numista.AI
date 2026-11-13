# NET-424 | GROKCOS to AGCOS | P7 V8.18.15 UX re-gate FAIL -> order Plan.v1 for V8.18.15b
Filed 2026-10-22 09:55 ET. Baton passed to AGCOS (BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md).

UX report: BETA TEST\Grok Bot\22 OCT 26\UX_P7_GATE_V7.md (FAIL, 2 items). Preview tested: p7-gate-8avtpz22, a7c83d7d, backend 00482-laj, scan 00343-mof. Field Tester result is still pending; fold in any FT findings before Plan.v1 if they land first.

ORDER: file PLAN_P7_V8_18_15b.v1.md (plan only, no code yet) for V8.18.15b on branch p7-v8.9 from a7c83d7d. Dev/preview only. Grok CoS scores the plan before you execute.

## Fix 2 (PRIORITY): slab label photo scan
- Fails: the clear PCGS label photo can't be read; the CACG rear can't be read; the CACG front spins over 2 minutes and then times out. The app never fills in the details and never tells the user the cert number may be on the back.
- Find the ROOT CAUSE (trace client -> scan_service -> model/OCR path; check request size/encoding, model call, response parse, client wait). Treat it as systemic: list every scan/lookup call path with the same pattern.
- Add a timeout of 30 s or less, end to end, with a friendly fallback (type the details or try another photo) instead of an endless spinner.
- Add a prompt: "The cert number may be on the back of the slab" when the front fails or no cert is found.
- Plan must name the test photos (PCGS clear, CACG front, CACG rear) and the pass bar: details filled in, or the fallback shown, within 30 s.

## Fix 1: tap targets at least 48 px
- NGC card "Check this slab on ngccoin.com" link and its Cancel (now 40)
- Sidebar "Send Beta Feedback" and "Sign Out" (now 32)
- Photo page "Take Photo" and "Upload" (now 40)
- Audit EVERY other tap target system-wide and list each fix in the plan.

## Wording: NGC card
Replace the mixed not-found / not-supported copy with exactly:
"We can't look up NGC numbers automatically yet. Snap the label or type the details below."

## Rules
- Phone-only fixes must not change the website: gate with !kIsWeb && (Platform.isAndroid || Platform.isIOS). If a change is intentionally shared web+phone, say so in the plan.
- No NGC scraping. Do not push past the PCGS block.
- No git commit -a; commit by explicit path. No deploys, main untouched, no live data writes, grokbot/demo only.
- Bump the version label to V8.18.15b. Keep flutter test and pytest green.
OVER
