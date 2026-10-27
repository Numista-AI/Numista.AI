# NET-610 Check Grounding cost estimate (prep only — no spend)

**When:** 27 Oct 2026 ~3:23 PM ET  
**Scope:** Small CG pass against evidence pack HOLD rows 586–590 only (FG-586-01…FG-590-20, **20 rows**). Sandbox **numista-morgan-pilot**. **No** live catalog/Brain fold/merge. **No** burn-order 1+.  
**Eric YES required** before any Check Grounding / Agent Builder burn (separate from this estimate).

## BLUF
| Option | What it is | Est. GenAI App Builder list $ | Notes |
|---|---|---|---|
| **A — CG RPC only** | Score pack claims vs pack citations | **~$0.00–$0.10** | Check Grounding ~$0.00075 / 1,000 calls — effectively free |
| **B — Fold-gate-style (recommended ceiling)** | Same shape as NET-605: search + Adv Gen Answers + rank + CG on 20 redesigned queries | **~$3.50–$5.00** (center **~$4**) | Prior fold-gate AG claim **$3.86** for 20 rows / ~540 HTTP 200 |
| **C — Redesign overshoot** | Extra retries / 2–3× queries per row | **up to ~$6–$8** | Stop if >25% over B without new YES |

**FinOps ask for Eric:** type YES for **Option B ≤ $5** on morgan-pilot only (or quote a lower cap). Wed 28 Oct 1:00 PM Billing reconcile still covers Week-1 $5.36 + prior fold-gate $3.86; this pass would be incremental.

## Basis (not fabricated billing)
- Prior fold-gate (NET-605/607) AG list: search **$1.92** + Adv Gen Answers **$1.92** + rank **$0.02** + CG **~$0** = **$3.86**; quality all CONDITIONAL_SUPPORT — CoS NO fold.
- Plan SKUs (Discovery / Agent Builder credit eligible): Enterprise search + advanced answers ≈ **$8 / 1,000** queries; Check Grounding **$0.00075 / 1,000**.
- Desk NET-607 log shape: **540** HTTP 200 (480 / 40 / 20) for the 20-row gate — CG line was negligible; search + gen answers drove $.
- Pack: CoS/Desk filed **20** rows FG-586-01…FG-590-20; Franklin Mint-primary **2,876,381** locked; Walker **548,000** Mint-primary; prep-only zero CG so far.

## What this estimate is NOT
- Not authorization to spend.
- Not a catalog fold or burn-order 1+.
- Not Workspace Antigravity / Claude Marketplace (separate OOP Vertex path on studio).

## Credits
Burns **GenAI App Builder** on Numista.Ai / **numista-morgan-pilot** only. Does **not** touch Developer Program, GFS reserve intent, or studio Claude OOP alert.

## Standing
**Eric YES ~3:25 PM ET 27 Oct (FIN OPS widget):** exact quote `YES Option B ≤ $5 fold-gate style NET-610`. CoS+Desk notified to EXECUTE. FinOps tracks toward Wed reconcile + post-run actuals.
