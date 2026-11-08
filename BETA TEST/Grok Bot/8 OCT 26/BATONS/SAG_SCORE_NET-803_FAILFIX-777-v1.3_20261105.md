# SAG SCORE NET-803 (xAI API, grok-4.7, 2026-11-05 ET)

## SAG_SCORE: 92/100 FAIL
## MUST_FIX (blocking before Eric YES; or NONE blocking)
1. §2.D tier table is stale and must be rewritten to the scrubbed CSV before YES. It still shows Tier 1 **2,273** and Tier 2 **747**. CSV is Tier 1 **2,354** and Tier 2 **666** (same 3,202 total; the 81-row gap is the reclassified blank-source set). Do not approve an acquire plan that still publishes the pre-scrub split.
2. §4.C snippet does not match the verified widget. `MorganChatPopout` takes `initialQuery` and required `onClose`, not `initialPrompt`. Spec must be `initialQuery: 'Tell me about the ${item['name'] ?? 'this coin'} (${item['year'] ?? ''})'` and `onClose: () => Navigator.of(context).pop()`.
## NON_BLOCKING
- $25 / $20 figures are present, but Cloud Monitoring email alerts do not stop spend. Do not treat alert-only monitoring as a hard stop unless a billing-budget action actually halts GCS/CDN.
- Fix 5 still ORs `year < 1792` with the flags, so it is not strict Condition C1 (the cited 9 flagged rows). Prefer flag-only.
- Field Tester list omits pre-federal, AI-never-primary, and a no-`href`/`src` check on the 167 acquisition-note URLs.
- `git checkout HEAD~1 -- firebase.json` is unpinned. Roll back to `9f04550a` or a recorded good SHA.
- §8 should say production needs a **separate** typed YES, distinct from plan YES (dev code + preview/GCS only; not Firestore).
- Argon-cited CSV samples still label some 1976–1977 rows “Pre-1929”. Hygiene scan is otherwise clean; confirm license text before any ingest.
## PII_FINDINGS
NONE. No AJ records, no personal collection images, no user identifiers. Intake gate drops receipt/invoice/`aj_photo`/`aj_currency`/personal patterns. “Josiah K. Lilly Jr.” appears only as a scrubbed historical album title.
## 2_SENTENCE_PLAIN_ENGLISH (for Eric)
The five holes from the last fail are written into this plan: AI stand-ins stay out of the main photo, nothing goes live before a preview check, the spreadsheet itself is clean, the $25/$20 limit is stated, and signed-in Ask Morgan opens the real chat popout. Do not type YES yet, because the acquire-count table still has the old 2,273 / 747 split instead of 2,354 / 666, and the chat snippet uses a parameter name the widget does not have.
## RATIONALE (brief)
v1.3 closes the five v1.2 blockers in substance: `ai_replica_images` never primary/card/index; §8 rollback plus `pre-ads-preview` before `numista-vault.web.app`; CSV hygiene (3,202, user scan clean); $25 cap with $20 alert; unregistered `/?route=AiChatScreen` removed. Locks hold: plan-only, `main` `9f04550a`, Stripe OFF, Firestore YES separate, no hotlinks, CSP stays internal, Thanksgiving path is preview-first. Score stays under 95 because the acquire table invents the pre-scrub tier split and the Morgan call as printed will not compile.
