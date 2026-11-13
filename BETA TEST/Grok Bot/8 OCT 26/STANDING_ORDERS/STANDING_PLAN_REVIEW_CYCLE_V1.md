# STANDING ORDER — PLAN REVIEW CYCLE V1
Issued: 26 Oct 2026 · Authority: Eric (owner) + Grok CoS · Applies to: AG, CoS, Desk, Argon

## When the FULL loop is required
Any plan that touches: write paths · SoR (system of record) · cost/fee math · privacy · new user flows.

1. AG writes **Plan v1** (no code).
2. Eric pastes the plan into **Gemini** using the Aug 12 Gemini prompt.
3. CoS runs **Stand Alone Grok** with the Grok prompt from the same doc (Must-Fix 3–5, Agree, Push-back, edge cases, MAJOR/MINOR verdict).
4. AG produces **Plan vN+1** with a **decision matrix** (accept / reject-with-argument per item) and **proof quotes** from code/docs.
5. Repeat 2–4 until both reviewers say **MINOR**.
6. **Eric says "go" before any code.** Then AG executes.

## When to SKIP the full loop
Tiny FAIL-FIX patches (single guard / narrow bug) use the lean path: CoS score → AG/Argon NET EXECUTE → Argon re-review. Example: NET-518 B4 shipping-credit cap.

## Crunch rules
- Cap **2–3 review rounds** per plan.
- Gemini vs Grok conflict that changes **who writes data / what a coin is / what admin sees** → `/grill-me` Eric **same day**. Never silent-pick.

## CoS duties
- Holds Grok Must-Fix lists across plan versions; checks each is closed or argued in vN+1.
- Does **not** claim "it works" until Field Tester clears the Invoices PDFs.

## Source prompts
Eric's Word doc (Aug 12): *Antigravity, GROK & GEMINI feedback prompts*. CoS has the text banked; Eric holds the original. Not copied here.

---
## AMEND 2026-10-27 ~12:20 PM ET — Eric full chain + 4-round / partial ship (applies to NET-602+ write-path plans)

**Chain:** AG Plan.vN → Argon → Grok Bot CoS (GB) → Stand Alone Grok → ONLY THEN EXECUTE → FT → live.
**Not enough:** Argon alone. Do not EXECUTE after Argon YES without GB + Stand Alone Grok.
**Rounds:** up to **4** (Plan v1–v4).
**After v4:** if not fully ready → **partial ship** ready parts (preview→FT→live per typed YES); keep iterating only not-ready parts.
Tiny FAIL-FIX may still use NET EXECUTE path when Eric/CoS explicitly say so; B- Mint NET-602 is on this full chain.
