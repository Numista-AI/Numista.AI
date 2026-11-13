# NET-570 — AG personal account confirm (Desk → CoS)
**From:** Antigravity Desk (GROKCOS)
**To:** Chief of Staff / AG CoS / FIN OPS
**Filed:** 2026-10-26 6:49 PM ET
**Status:** OVER (Desk confirm filed; AG self-ACK wake LIVE)

## BLUF
Eric switched Antigravity to **personal** account + AG CoS model **Sonnet 5.5 Low**. Desk checked machine-side auth/workspace.

## Answers (YES/NO + catch)
1. **Numista.Ai workspace/repo write:** **YES** — MyVertexProject still on disk; local folder write does not depend on which Google login Antigravity uses. **Catch:** AG must keep MyVertexProject open/linked under the personal account (re-add folder if sidebar lost it).
2. **Sonnet 5.5 Low EXECUTE FAIL-FIX / p7gate preview (NET-565):** **YES** — EXECUTE is tools (edit + Firebase Hosting/Run to p7-gate), not Ultra plan. Low = lighter thinking, not read-only. **Catch:** personal/Starter Claude weekly quota is smaller than Business Ultra — keep 565 bursts short; may throttle sooner.
3. **Auth/project binding break leaving work/numista AG login:** **NO hard break for deploys** — Firebase CLI still **Logged in as eric@numista.ai** (also has eric.seaman@v3tees.com available). **Catches:** (a) AG cloud rate limits / business project chips may differ on personal; (b) Vertex 429 cool-down is **GCP** (not AG login) — still no Mint harvest + catalog + 565 concurrent; (c) live/main still OFF.

## Priority
**NET-565 #1** once cool-down clear. Overnight NET-568 stays spare/PAUSED rules; PH INCLUDE M8a–c.
