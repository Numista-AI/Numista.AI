# Numista.Ai Implementation Plan: Simpler UI + Morgan as a Safe AI Helper
Prepared by Chief of Staff, 8 Oct 2026. Status: PLAN ONLY (v2, revised after outside Grok review 10:34 AM ET). Nothing built or deployed.
Code baseline: branch `dev`, commit `e5f5760c`. Reviewed by Grok (CoS) and independently by Gemini 3.8 (PASS).

## Background
- Numista.Ai is an AI coin collection manager. Most future customers are older collectors (60+).
- Founder's idea: Morgan, the in-app AI coin assistant, becomes the single interface for all transactions unless the user opts out.
- UX Designer proposed 5 visual simplifications.
- Guiding rules:
  - simplicity, security, anonymity
  - the only PII stored is an email address
  - PIN sign-in, no passwords
  - collection values are never exposed to outside parties
  - AI-taught facts need founder or admin approval

## What Morgan can do today (verified in code)
- Model: Gemini Flash on Vertex AI.
- The chat endpoint is `/api/deep_dive` (main.py:2715-2998).
- Three write tools: add coin (2303-2534), edit storage/condition/cost/notes (2579-2637), delete via "undo" (2640-2655).
- **Writes run with no confirmation.** The prompt says add "immediately" (2909).
- If no coin id is given, the edit falls back to the most recently created coin (2618-2621).
- "Undo" hard-deletes whatever id it gets. The client can call it directly with `INTERNAL_UNDO:<id>` (2746).
- Every prompt includes up to 2,000 coins with AI value and cost (collection_inventory.py:105,156,175; main.py:2790). The second chat route adds portfolio value and P/L (ai_routes.py:110-116).
- Client-sent `collection_context` is appended to the prompt (main.py:2804-2805).
- Rate limiting only logs and never blocks (logging_config.py:113). Chat calls aren't even counted (main.py:122). Each action costs 2 model calls.
- Audit trail: adds record provenance; edits and deletes record nothing.
- Missing: checklist check-off, transfers, selling (Certificate of Transfer), reports, voice input (no speech-to-text; read-aloud is web only).
- Sign-in scoping on `/api/deep_dive` is correct (main.py:2722-2735).
- But other write routes trust a body/form `user_email` with no token check:
  - checklist/add_coins (7784)
  - review/commit (3000)
  - binder scan (3908, 4606)
  - `/api/v1/rag/query` calls the model with no sign-in at all
- Also in scope: scan_routes review/* (84-359), import_routes (76, 234), /api/ai/essay (237).
- A reusable safe pattern exists: group-photo ID proposes, and the user taps "Confirm & Save" (ai_chat_screen.dart:1169-1230, 1390-1554).
- Document ingest uses a staged review_queue with commit/abort.

## Decision
Not "Morgan-first, default on" today. Instead, a phased hybrid:
- Morgan sits front and center and proposes actions.
- The user taps a big Confirm card.
- The simplified menus stay underneath, with an opt-out checkbox.

## Workstream A: UX fixes (REQ_032, Older User Onboarding)
Model: Claude Sonnet 4.6 (Thinking). Order:
1. **Fix 2, bigger darker text.**
   - 18px+ body text and full-width buttons.
   - Centralize theme tokens first; current text is hard-coded at 9-13px.
2. **Fix 3, PIN sign-in.**
   - Six big PIN boxes, number keypad, a clear "Show PIN" button, and a prominent "Forgot your PIN?".
   - Fix the garbled dot glyphs.
   - Keep the REQ_025 5-guess lockout.
3. **Fix 1, checklist.**
   - One big row per coin with its full name, and big P/D/S tap buttons.
   - Show "7 of 19 collected, 12 to go" instead of "System of Record completion %".
   - Depends on REQ_034/036 for accurate slot counts and name matching.
   - Also fix the demo "View Checklist" mislink on every program card.
4. **Fix 4, menu.**
   - Six items: Home, My Coins, Add a Coin, Coin Programs, Help & Ask Morgan, More.
   - Everything else goes under More; nothing is removed.
5. **Fix 5, Add a coin.**
   - Three choices: Take a photo, Type it in, Upload a list.
   - Rarer methods go under "More ways".
   - Plain wording, no "schema".

Acceptance:
- Tablet and phone screenshots before and after.
- No text under 16px on primary screens.
- Tap targets of 44px or more.
- Field Tester regression pass.
- Dev only; deploy only on the founder's YES.

## Workstream B: Morgan safety, Gate 0 (required before any Morgan expansion)
Model: Claude Opus 4.6 (Thinking).
1. **Confirm before every write.** Morgan returns a proposal card, and the server writes only after an explicit user Confirm. Remove the "immediately" instruction.
2. **Never guess the target coin.** Remove the most-recent fallback. Edits show the target's thumbnail, year and mint before Confirm.
3. **Soft delete.** Deletes go to a 30-day Trash with Restore. `INTERNAL_UNDO` is limited to coins Morgan added for this user in this session. Remove hard delete from the AI's tools.
4. **Server-side action log** for every AI-proposed and confirmed add, edit and delete: who, what, before and after, time.
5. **Real usage caps that block.** Per-user caps on model calls, caps on the background web scraper and the essay endpoint, and a daily spend alert.
6. **Privacy.**
   - Strip value and cost from Morgan's prompt by default.
   - Include them only when the user explicitly asks about value.
   - Privacy Mode (REQ_026) means zero financial figures, ever.
7. **Prompt-injection guards.**
   - Ignore client-sent `collection_context` and `chat_history` as authority; use server-side inventory.
   - Treat coin notes and OCR/receipt text as data, never instructions.
   - Do nothing without a Confirm tap.
8. **REQ_031 API lockdown.** Every write route derives the user from the sign-in token, never from a body or form email. Covered routes:
   - checklist/add_coins
   - review/commit
   - binder scan analyze/confirm
   - scan_routes review/*
   - import routes
   - rag/query
9. Fix the `/api/ai/chat` uid-vs-email lookup bug and the missing `/api/ai/chat/stream` route (or remove the call).

Acceptance:
- Tests prove the following:
  - no write happens without Confirm
  - a cross-account write is rejected
  - a delete can be restored
  - caps block
  - values are absent from the prompt in Privacy Mode
  - an injected note can't trigger an action
- Code Reviewer and Gemini sign off.

## Phase 1: Morgan as guide (read-only)
- Answers questions.
- Handles "take me to ..." navigation to the simplified screens; the existing greeter tiles can be reused.
- **Voice input:** hold-to-talk speech-to-text on mobile, plus read-aloud on mobile.

## Phase 2: Morgan drafts, the user confirms
Order of actions:
1. Add a coin (proposal card, then Confirm & Save).
2. Check off a checklist slot.
3. Edit coin details (with a thumbnail of the target).
4. Soft delete.
- Transfers and selling are never executed in chat. Morgan takes the user to those screens, which keep their PIN steps.
- Every card has Undo.

## Phase 3: Morgan as the default front door
Turn on as default only when all of these are true:
- Fact-accuracy verification (F1) and the REQ_033 corrections have passed.
- Over 30 days, fewer than 1% of Morgan-drafted actions are undone or corrected.
- Cost is within budget.
- The founder types YES.

The opt-out checkbox stays permanently.

## Review cycle
1. Antigravity CoS writes a Plan.v1 per workstream.
2. Gemini 3.8 Flash reviews it, quoting the file:line it actually opened.
3. Chief of Staff scores it.
4. The founder says Proceed.
5. Execute on dev.
6. Code Reviewer and Field Tester check it.
7. The founder says YES to deploy.

## Questions for an outside reviewer
1. Is the phase order right, or should anything move earlier or later?
2. Is anything missing from Gate 0 security?
3. For older users, is voice input essential before Phase 2?
4. Are the Phase 3 thresholds the right gates?


---
# v2 CHANGES (8 Oct 2026, after outside Grok review). These override anything above.

## Sequencing
- **REQ_031 API lockdown becomes a standalone HOTFIX, starting now, separate from the Morgan project.**
  - Routes in scope:
    - checklist/add_coins
    - review/commit
    - binder scan analyze/confirm
    - scan_routes review/*
    - import routes
    - `/api/v1/rag/query` (no sign-in at all)
  - Today these are live cross-account-write and unauthenticated-model-call defects, not future prerequisites.
  - It still follows Plan.v1, then Gemini, then CoS score, then the founder's Proceed and deploy YES. It is prioritized, not fast-tracked past review.
- **Workstream A (UX) runs in parallel with Gate 0.** The only shared file is the chat screen; coordinate on that file only.

## Gate 0 additions
1. **Server-held proposals.**
   - Morgan's proposal is stored server-side, bound to the signed-in user, with a short expiry (about 5 minutes).
   - The Confirm endpoint takes only the proposal id, reloads the coin, and applies exactly the stored action. It never trusts a client-built card.
2. **Server-resolved targets only.**
   - No most-recent fallback, and no client- or model-supplied coin id.
   - The target is resolved server-side for this user.
   - The thumbnail, year and mint on the card come from that server read, not from the model.
3. **Idempotent, single-use Confirm.** A double tap or replay returns the same result, never a second coin. Expired proposals are rejected.
4. **Undo is checked server-side against the action log** (this user, this session, Morgan-added), never against whatever id arrives. `INTERNAL_UNDO:<id>` is replaced by undo-by-action-id.
5. **Action log fields:** who, action, coin id, before, after, proposal id, confirm time.
   - The full prompt is never logged.
   - The model never writes a log line; the server writes it.
   - "Before" is also kept in Trash and edit history, so the log isn't the only copy.
6. **Caps fail closed.** They cover chat, confirm, scraper and essay, and chat calls must be counted. If the limiter errors, the request is blocked. The daily spend alert is in addition to the block, not instead of it.
7. **Privacy is enforced on the server everywhere.** Value, cost and P/L are stripped from:
   - the prompt
   - tool results
   - navigation payloads
   - the second chat route (`/api/ai/chat`)
   Notes and OCR text are wrapped in a hard data delimiter and are never treated as instructions.
8. **Two-step delete.** Add and edit use one Confirm card. A soft delete restates the coin and needs a second, distinct confirm. Selling and transfers stay out of chat in every phase.
9. **One confirm style only.** Reuse the group-photo "Confirm & Save" card and the review-queue commit/abort path. Do not invent a third.
10. **Shrink the 2,000-coin context** to a capped, value-free summary plus on-demand lookups. This is needed for both cost and privacy, starting in Phase 1.

## Voice
- Voice does **not** gate Phase 2. This overrides Gemini's "mandatory" view; CoS sides with Grok.
- Hold-to-talk speech-to-text plus mobile read-aloud ship in Phase 1, where Morgan is read-only and a mishear only fetches the wrong answer.
- Phase 1 measures the misheard coin-term rate (mint marks, years, series names like Walking Liberty) before voice is allowed to start drafts in Phase 2.

## Phase 3 gates (replaces the 1% line)
- **Minimum volume:** at least 500 confirmed actions AND 30 days AND at least 50 per action type, whichever comes later.
- **Split undo/correction rates:**
  - adds under 1%
  - edits under 0.5%
  - deletes: zero restores caused by a Morgan mistake
- **Confirmed-without-reading check:** confirms under 2 seconds count against the gate, especially deletes.
- F1 and REQ_033 fact accuracy remain hard gates.
- **A dollar cost ceiling** per active user per month is set before Phase 3, with the reduced context in place.
- The founder's YES is last. The opt-out checkbox is permanent.

## Acceptance tests added
- A replayed or double-tapped Confirm creates one coin.
- An expired proposal is rejected.
- A forged proposal or coin id from the client is rejected.
- An undo of a coin not added by Morgan in this session is rejected.
- The limiter failing blocks the request instead of letting it through.
- Privacy Mode shows no values in tool results or navigation payloads.
- A delete requires two distinct confirms.
