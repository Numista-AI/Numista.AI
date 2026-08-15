# Pre-Flight Brief Testing Protocol (For Overnight & Complex Tasks)

**Purpose:** Eliminate **Correlated Failures** during autonomous `/goal` or multi-hour sessions. A gap in your prompt doesn't produce random mistakes; it produces the exact same mistake repeatedly across the entire run.

---

## The Pre-Flight Check Prompt

Before submitting a long-running brief to an overnight session or `/goal` agent, paste your draft prompt inside the template below and run it in a single-turn inquiry:

```markdown
Antigravity, I am preparing a complex, multi-hour autonomous task brief for an overnight agent who will receive NO follow-up turns or clarifications.

Read the draft brief below as an isolated worker model:
1. List everything you would have to guess or assume to execute this task.
2. Identify the top 3 ambiguities where an agent is most likely to make an incorrect assumption.
3. Suggest specific machine-executable exit commands that should be added to the brief.

--- DRAFT BRIEF ---
[Paste your intended task prompt here]
-------------------
```

---

## How to Act on the Output:
1. **Context Gaps:** Any items listed under "things you'd have to guess" represent context held in your head that was missing from the written brief. Add explicit rules or paths for those items.
2. **Ambiguities:** Clarify edge cases (e.g., error handling, file overwrite policies, branch targets).
3. **Exit Commands:** Ensure at least one terminal test command is included so the agent knows when it has genuinely completed the task.
