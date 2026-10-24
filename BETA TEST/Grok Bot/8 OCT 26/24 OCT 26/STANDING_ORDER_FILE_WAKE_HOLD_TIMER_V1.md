# STANDING ORDER — File-wake + Hold-only Timer V1

**Status:** BINDING (Eric YES 24 Oct 2026 ~1:17 PM ET)
**Author:** Grok CoS
**Supersedes:** PLAN_FILE_WAKE_AG_ARGON_V1.md draft open questions (defaults locked below)
**Pointer from:** BATONS\00_BATON_RULES.md Rule 10

---

## 1. Purpose

Cut Eric's need to type **check radio** every time Argon Reviewer or AG CoS must pick up a NET, while keeping Gemini quota under control (Rule 9 still stands).

Three paths, in preference order when available:

1. **Remote Control** (preferred when Google rolls out the laptop toggle) — Eric opens the chat from phone and types check radio only when needed.
2. **File-wake** (always-on backup) — Grok CoS / Desk drop a WAKE marker; agents poll `RADIO NET\WAKES\`.
3. **Hold-only timer** — while a chat is actively holding work, it may re-arm a 25-minute self-wake; when the hold ends, timer off.

---

## 2. File-wake mechanism

### 2.1 Folder

```
BETA TEST\Grok Bot\8 OCT 26\RADIO NET\WAKES\
BETA TEST\Grok Bot\8 OCT 26\RADIO NET\WAKES\DONE\
```

One shared folder. Prefixes distinguish the target:

- `WAKE_ARGON_<REASON>_YYYYMMDD-HHMM.md`
- `WAKE_AGCOS_<REASON>_YYYYMMDD-HHMM.md`

Body (keep short): FROM, TO, DTG, which NET to read, one-line why.

### 2.2 Who may file a WAKE

- **Grok CoS** (primary)
- **Desk / AG plan handoff stall watch** may file a WAKE when a baton is unmoved **>=2 working hours** (same spirit as stall re-flags)
- **Not** Field Tester / UX (they use radio NETs only)

### 2.3 After processing

Rename/move the WAKE to:

```
RADIO NET\WAKES\DONE\WAKE_*_DONE.md
```

Keep the audit trail. **Do not delete.**

### 2.4 Agent NEXT footer (required)

Every Argon / AG CoS reply that closes a turn ends with:

```
NEXT: poll RADIO NET\WAKES for WAKE_<you>_… or check radio
```

On finding a matching active WAKE: process the newest NET addressed to you (same as check radio), then move the WAKE to `DONE\`.

---

## 3. Hold-only timer (Rule 7 clarified; Rule 9 still stands)

### 3.1 AG CoS

- May re-arm a **25-minute** self-wake **only while AGCOS holds the baton** (OVER / WILCO).
- When the baton passes to **GROKCOS** or **ERIC**, do **NOT** re-arm (Rule 9).
- Cap: stop re-arming after **2 hours** on the same hold, or when work is filed (`EXECUTE_DONE` / NET reply) — then wait for check radio or a new WAKE.

### 3.2 Argon Reviewer

- May re-arm 25 minutes **only while working an open NET review request addressed to Argon** (example: NET-487).
- After filing PASS / FAIL-FIX (or after **2 hours**), stop.
- Do not poll forever.

### 3.3 Both chats

- Neither chat may set an **open-ended forever** timer.
- Empty polls: **one short line only**; no "board unchanged" NET notes (Rule 9.5).

### 3.4 Rule 7 / Rule 9 interaction

- Historical Rule 7 = 25-minute self-wake while working.
- Rule 9 = no timer when not holding.
- Rule 10 = Rule 7 is **hold-only** + **2-hour cap**, plus file-wake as the always-on backup. Rule 9's "no timer when not holding" is unchanged.

---

## 4. Safety (unchanged)

A WAKE file / hold-only timer wake:

- **Never** authorizes a **live deploy**
- **Never** merges to **main**
- Does **not** override **Flash Low only** (no Claude for AG CoS coding)
- Does **not** cancel the **3 AM stand-down**
- Does **not** replace **Eric YES** for live, main, or rule changes

Preview refresh still follows existing standing YES rules. Live still needs Eric typing **YES** in chat.

---

## 5. Rollout

| Step | Status |
|---|---|
| A Draft PLAN | Done 24 Oct morning |
| B Remote Control toggle | Still waiting on Google / one laptop visit home |
| C Eric YES → standing order | **DONE 24 Oct 2026 ~1:17 PM ET** (this file) |
| D First real WAKE | Deferred — do not file a test WAKE while NET-487 / FAIL-FIX path is hot |

Until agents ACK this order on their next wake, they may still be woken by Eric typing **check radio**.

---

## 6. Defaults locked by Eric YES (do not re-ask)

1. After WAKE: move to `WAKES\DONE\` (not delete).
2. Who files: Grok CoS primary; Desk/stall watch >=2h allowed; not FT/UX.
3. One shared `WAKES\` with `WAKE_ARGON_` / `WAKE_AGCOS_` prefixes.
4. Remote Control preferred when available; file-wake always-on backup; hold-only timer third path while actively holding work.

END STANDING ORDER V1
