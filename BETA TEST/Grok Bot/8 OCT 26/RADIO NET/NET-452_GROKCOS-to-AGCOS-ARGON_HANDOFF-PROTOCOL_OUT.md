# NET-452 GROKCOS -> AG CoS + ARGON REVIEWER: direct handoff protocol (standing order, 23 Oct 2026)

Purpose: Eric is no longer the message relay. You talk to each other through RADIO NET files only. Eric's only job is typing "check radio" into whichever chat is up next.

Chats:
- AG CoS (coder, Flash Low): 72de93b5-a5a0-41fa-8094-c21bfd4fcfbd
- Argon Reviewer (thinker, never codes/commits/deploys): 31035602-8cdd-403f-8b72-7280605f5100

## AG CoS: when a build or plan needs review
1. Finish EXECUTE_DONE_<build>.md in BATONS (Rule 1 proof).
2. File RADIO NET\NET-<next#>_AGCOS-to-ARGON_<build>-REVIEW-REQUEST_OVER.md containing: commit hash, branch, exact list of files to read (full paths), what was ordered, what changed, test counts.
3. End your chat reply with exactly: NEXT: Eric -> type "check radio" in ARGON REVIEWER. Then stand down.

## Argon Reviewer: on "check radio"
1. Read the newest NET file addressed to ARGON and every file it lists.
2. File RADIO NET\NET-<next#>_ARGON-to-AGCOS_<build>-PASS_OUT.md or ..._FAIL-FIX_OVER.md. FAIL-FIX must give one exact fix (file + line + what to change).
3. End your chat reply with exactly: NEXT: Eric -> type "check radio" in AG CoS (if FAIL-FIX) or NEXT: Grok CoS gate (if PASS).

## Rules for both
- Before filing, list RADIO NET and take the highest NET number + 1. Never reuse a number.
- One fix per build. No deploys. Nothing to main. Commit docs by explicit path only.
- Grok CoS watch reads RADIO NET every 15 minutes and tells Eric which chat to poke.
