# PLAN — File-wake for AG / Argon (V1 DRAFT — not binding yet)

**Date:** 24 Oct 2026
**Author:** Grok CoS (draft for Eric)
**Status:** DRAFT ONLY. Do **not** change AG / Argon standing rules until Eric types **YES** when home.
**Related:** Phone experiment (buzz Eric for decisions); Antigravity Remote Control not enabled on laptop yet.

---

## 1. Problem

Argon Reviewer and AG CoS usually only act when Eric types **check radio** in that chat.

When Eric is on his phone and away from the laptop:
- He can answer YES/NO to Grok Bot.
- He **cannot** open the Antigravity chats on the laptop.
- Remote Control on the phone dashboard currently shows **"Connect your first instance"** — the laptop toggle is not on yet (and Google may still be rolling the feature out).

Result: radio NETs sit unread. We get stuck waiting on a laptop visit just to say two words.

---

## 2. Goal

Let **Grok CoS** (or Desk / a stall watch) drop a small **WAKE marker file** that Argon / AG CoS are later ordered to poll.

Eric only decides **YES/NO** on the phone via Grok Bot. He does **not** have to type check radio for every stall — once this plan is live.

---

## 3. Proposed mechanism (adopt later with Eric YES)

### 3.1 Wake folder

```
BETA TEST\Grok Bot\8 OCT 26\RADIO NET\WAKES\
```

Example files:
- `WAKE_ARGON_<reason>_YYYYMMDD-HHMM.md`
- `WAKE_AGCOS_<reason>_YYYYMMDD-HHMM.md`

Keep the body short: who, why, which NET to read, DTG.

### 3.2 Standing order (NOT in force until Eric YES)

When this plan is enabled:
1. Every Argon / AG CoS reply ends with something like:
   `NEXT: poll RADIO NET\WAKES or check radio`
2. On finding a WAKE addressed to them:
   - Process the **newest NET** addressed to them (same as check radio).
   - Then **delete** the WAKE file, or rename it to `*_DONE.md` / move to `WAKES\DONE\`.
3. CoS files **WAKE + NET** together when an order needs attention and Eric is away.
4. Desk / stall watch may also file a WAKE if a track is stalled **>2 hours** (same spirit as today's stall re-flags).

### 3.3 Who may file a WAKE

- Grok CoS (primary)
- Desk / automated watch on stall (>2h)
- Not Field Tester / UX (they use radio NETs only)

---

## 4. Remote Control (still preferred when available)

Docs: https://antigravity.google/docs/remote-control/

**Laptop (one-time):**
1. Antigravity → Settings (`Ctrl+,`) → **App**
2. Toggle **Enable Remote Control** On
3. Leave Antigravity running; keep the laptop **awake and online**

**Phone (no app install):**
1. Browser only → https://antigravity.google.com/ (same Google account)
2. Pick the laptop instance
3. Open Argon Reviewer or AG CoS → type `check radio`

**Do not** download / install Antigravity on the phone. The blue download button is for the computer.

### Today's status (24 Oct 2026 morning)
- Phone dashboard: **"Connect your first instance"** — no laptop listed.
- Laptop Remote Control toggle: **not enabled yet** (needs one visit home).
- Google banner may say the feature is still rolling out; if Settings → App has no toggle, fall back to this file-wake plan.

---

## 5. Safety (unchanged)

A WAKE file:
- **Never** authorizes a **live deploy**
- **Never** merges to **main**
- Does **not** override **Flash Low only** (no Claude for AG CoS coding)
- Does **not** cancel the **3 AM stand-down**
- Does **not** replace Eric YES for anything that already needs Eric YES (live, main, rule changes)

Preview refresh still follows existing standing YES rules. Live still needs Eric typing **YES** in chat.

---

## 6. Rollout

| Step | When | What |
|---|---|---|
| A | Today (this file) | Draft only. Commit to `origin/dev`. No standing-rule change. |
| B | Eric home | Optional: enable Remote Control on laptop; confirm phone sees the instance. |
| C | Eric types **YES** | Adopt §3 standing order into AG / Argon rules; create `WAKES\` folder; CoS may start filing wakes. |
| D | First real wake | CoS files one test WAKE + NET; Argon/AG process; CoS confirms DONE rename. |

Until Eric types **YES**, agents keep using **check radio** only. This PLAN is informational.

---

## 7. Open questions for Eric (when home)

1. Prefer **delete** WAKE vs rename to `*_DONE`?
2. Should Desk auto-wake at 2h stall, or only CoS after a human-style decision?
3. One shared `WAKES\` folder, or separate Argon vs AGCOS subfolders?
4. Keep Remote Control as primary and file-wake as backup, or the reverse while traveling?

---

## 8. Bottom line

**Problem:** phone + no Remote Control = stuck on Argon/AG wakes.
**Draft fix:** WAKE marker files in `RADIO NET\WAKES\` that agents poll.
**Not live yet.** Enable only after Eric is home and types **YES**.
**Remote Control** remains the nicer path once the laptop toggle is on.

END PLAN V1 DRAFT
