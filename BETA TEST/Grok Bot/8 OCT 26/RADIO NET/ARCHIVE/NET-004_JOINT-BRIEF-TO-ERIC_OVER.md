# NET-004 | FROM: AG CoS | TO: Eric (Commander) | TOPIC: Joint Brief — Radio Protocol Options | 2026-10-12

AG CoS and Grok CoS agree on the two options below. Grok CoS's words are from `003_GROKCOS-to-AGCOS_RADIO-PROTOCOL_OVER.md`; AG CoS adds its view.

---

## Option 1 — RADIO LOG (Proword File Stream, Idea A — fixed)

**How it works:**  
Every message is its own file. File names carry the track prefix, a sequence number, the sender, a topic, and a proword in the last word:

```
T1-001_GROKCOS-to-AGCOS_REQ031-ORDER_OVER.md
T1-002_AGCOS-to-GROKCOS_PLANV1_WILCO.md
T1-003_GROKCOS-to-AGCOS_PLANV1-SCORE_OUT.md
NET-001_GROKCOS-to-AGCOS_RADIO-PROTOCOL_OVER.md
NET-002_AGCOS-to-GROKCOS_RADIO-PROTOCOL_OVER.md
```

Prowords: OVER (your turn), WILCO (will comply / working), OUT (thread closed), WAIT-OUT (holder is working, check later), SAY-AGAIN (need clarification), BREAK-ERIC (needs Commander).

Whose turn on a track = the newest-numbered file for that track. No baton file to maintain. Full paper trail — every transmission is immutable once written.

**Sample folder (3 parallel tracks, mid-work):**
```
RADIO NET/
  T1-001_GROKCOS-to-AGCOS_REQ031-ORDER_OVER.md
  T1-002_AGCOS-to-GROKCOS_PLANV1_WILCO.md
  T2-001_GROKCOS-to-AGCOS_GATE0-ORDER_OVER.md
  T2-002_AGCOS-to-GROKCOS_GATE0-PLAN_WILCO.md
  T3-001_GROKCOS-to-AGCOS_UX-ORDER_OVER.md
  NET-001_GROKCOS-to-AGCOS_RADIO-PROTOCOL_OVER.md
  NET-004_JOINT-BRIEF-TO-ERIC_OVER.md   ← this file
```

**AG CoS view:** Simple and audit-proof. A missed handoff is visible because the last file's proword shows who still holds the ball. The folder grows over time but the sort order is the full history.

**Grok CoS view:** It's the full paper trail and simple. Eric reads the last file per track to see whose turn it is.

---

## Option 2 — BATON BOARD + RADIO LOG (Tactical Net Baton, Idea B — fixed)

**How it works:**  
Same Radio Log as Option 1, PLUS one baton file per track. The baton file name is the live scoreboard:

```
BATON_T1-REQ031_AGCOS_WILCO.md
BATON_T2-GATE0_GROKCOS_OVER.md
BATON_T3-UX_AGCOS_WAITOUT.md
```

Whose turn on a track = read the 3 baton file names. One glance = full status. Every rename must have a matching Radio Log file (so the baton can't lie). Only the current holder may rename the baton. Grok CoS's 15-minute watch flags any baton unmoved for more than 2 working hours. If two batons appear for one track, the watch keeps the one matching the newest log file and reports the anomaly.

The baton replaces `WHOSE_TURN.md` (which requires manual edits and can fall out of sync).

**Sample folder (same 3 tracks):**
```
RADIO NET/
  BATON_T1-REQ031_AGCOS_WILCO.md        ← AG CoS is drafting plan
  BATON_T2-GATE0_GROKCOS_OVER.md        ← Grok CoS to score
  BATON_T3-UX_AGCOS_WAITOUT.md          ← AG CoS working, not yet sent
  T1-001_GROKCOS-to-AGCOS_REQ031-ORDER_OVER.md
  T1-002_AGCOS-to-GROKCOS_PLANV1_WILCO.md
  T2-001_GROKCOS-to-AGCOS_GATE0-ORDER_OVER.md
  T2-002_AGCOS-to-GROKCOS_GATE0-PLAN_OVER.md
  T3-001_GROKCOS-to-AGCOS_UX-ORDER_OVER.md
  NET-004_JOINT-BRIEF-TO-ERIC_OVER.md
```

**Grok CoS view (recommendation):** Eric's real need is a one-second glance across parallel tracks, and only the baton gives that.

**AG CoS view:** The baton is more powerful for multi-track monitoring, but "only the holder renames" is a coordination rule that requires discipline. If either CoS renames without a matching log file, the scoreboard lies. That's a higher failure mode than Option 1 — though Grok CoS's 15-minute watch is a good mitigant.

---

## AG CoS Recommendation

**Option 2** if Eric wants a one-glance dashboard (3 file names = full status). Choose this if parallel tracks are the norm and Eric checks frequently.  
**Option 1** if Eric prefers simplicity and doesn't mind reading the last file per track. Choose this if auditability matters more than speed of scan.

AG CoS is comfortable with either. The existing `WHOSE_TURN.md` already serves as a manual baton board; Option 2 automates it and makes it self-correcting.

---

**Eric: please pick Option 1 or Option 2.** Both CoSs will implement whichever you choose within the next session.

OVER.
