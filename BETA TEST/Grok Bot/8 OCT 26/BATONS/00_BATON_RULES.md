# BATON RULES (Option 2, Eric picked 12 Oct 2026 4:46 PM ET) - replaces WHOSE_TURN.md
1. One file per track in BATONS\: BATON_<TRACK>_<HOLDER>_<PROWORD>.md. Holder = GROKCOS | AGCOS | ERIC | CLOSED.
2. Prowords: OVER (your turn), WILCO (working it), WAIT-OUT (blocked/queued, say why), SAY-AGAIN (need clarification), OUT (done/closed).
3. ONLY the current holder renames the baton, and appends a dated line to its Log when passing it.
4. Conversation goes in RADIO NET\ as T<n>-<seq>_FROM-to-TO_<topic>_<PROWORD>.md.
5. Grok CoS watch flags any baton unmoved 2+ working hours.
6. Never ask Eric to relay. Eric holds a baton only for a decision.

## Rule 8 - QUOTA SAVER (Eric, 14 Oct 2026 3:57 PM)
1. ONE JOB AT A TIME. Work one baton until it reaches a scored checkpoint. No parallel tracks or background builds. Order: P7 fix (per NET-099/100), then P5, then P6 rerun, P4, P8, P10, P9.
2. READ ONLY RECENT RADIO. Old messages are in RADIO NET\ARCHIVE. Don't open ARCHIVE unless a current message names a file there. On each wake, read only the files that are new since your last ACK.
4. TWO STRIKES. If a build, deploy, test run or command fails twice in a row for the same reason, STOP. File a NET message with the error and your best guess, and wait. No retry loops.

## Rule 9 - GEMINI QUOTA SAVER II (Eric, 16 Oct 2026 ~9:00 AM ET)
1. NO TIMER WHEN NOT HOLDING. When the baton is with GROKCOS or ERIC, AG does NOT re-arm its 25-minute self-wake timer (Rule 7). AG stands down and waits for Eric's "check radio" or the next baton passed to AGCOS.
2. ONE WATCHER. Only one AG conversation watches the board at a time. Conversation aa4cea77 is RETIRED - do not resume it.
3. ONE REVIEW PER VERSION. One GEMINI38 review per build version, never repeated. Skip the GEMINI38 review entirely for fixes touching 2 files or fewer.
4. FRESH CONVERSATION PER PHASE. Start a new AG conversation for each phase (P7, P5, P6, ...). Do not carry one long conversation across phases.
5. NO "BOARD UNCHANGED" NOTES. Grok-side watches (and AG) do not file NET notes just to say the board is unchanged. Log only when something changes.

## Rule 10 - FILE-WAKE + HOLD-ONLY TIMER (Eric YES 24 Oct 2026 ~1:17 PM ET)
1. Full order: `24 OCT 26\STANDING_ORDER_FILE_WAKE_HOLD_TIMER_V1.md`. Wake folder: `RADIO NET\WAKES\` (DONE rename to `WAKES\DONE\`, do not delete).
2. Who files WAKE: Grok CoS (primary); Desk/stall watch if baton unmoved >=2 working hours. Not FT/UX.
3. Prefixes: `WAKE_ARGON_` / `WAKE_AGCOS_`. Agents poll on wake; footer: `NEXT: poll RADIO NET\WAKES for WAKE_<you>_… or check radio`.
4. HOLD-ONLY TIMER (Rule 7 clarified): AG may re-arm 25-min self-wake ONLY while AGCOS holds baton (OVER/WILCO). Argon only while working an open NET review to Argon. Cap 2 hours or when work filed — then stop. No forever timers. Empty poll = one short line; no board-unchanged NETs (Rule 9.5).
5. Rule 9 unchanged: when baton is with GROKCOS or ERIC, AG does NOT re-arm. File-wake is the always-on backup; Remote Control preferred when Google toggle is available.
6. Safety: WAKE never authorizes live deploy, never merges main, does not override Flash Low, does not cancel 3 AM stand-down, does not replace Eric YES for live/main/rule changes.
