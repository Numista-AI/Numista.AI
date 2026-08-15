# Numista.AI — Agent Rules

## Git: Always Push Before Declaring Done

These rules apply to **every session** that modifies source code in this workspace.

### Rule 1 — Push is the finish line, not local verification

Before writing `walkthrough.md` or declaring a task/goal complete, you MUST:

1. Stage all modified source files:
   ```bash
   git add <files>
   ```
2. Commit with a descriptive message:
   ```bash
   git commit -m "<type>(<scope>): <summary>"
   ```
3. Pull and rebase, then push to **`dev`** — **always use this exact sequence**:
   ```bash
   git pull --rebase origin dev
   git push origin dev
   ```
   The `--rebase` absorbs any commits that landed since your last pull (from other sessions,
   the auto-backup cron, or the user) and places your commit cleanly on top.
   Never push directly to `main`. Never use a bare `git push` without the pull-rebase prefix.
4. Confirm the push succeeded (look for `dev -> dev` in the output).

**Only after a confirmed push to `dev` may you write `walkthrough.md` or emit `<!-- GOAL_COMPLETE -->`.**

> A task that is not pushed to GitHub is NOT done — it is only done locally.

---

### Rule 2 — Check branch sync at the start of every session

At the beginning of any session that will make code changes, run:

```bash
git status
git log --oneline origin/main..HEAD
git log --oneline origin/dev..HEAD
```

If the local `dev` branch is **ahead** of `origin/dev`, push those commits first:

```bash
git pull --rebase origin dev
git push origin dev
```

This prevents commits from being silently stranded when you switch branches between sessions.

---

### Rule 3 — Never write the walkthrough before pushing

The order must always be:

```
code changes → git add → git commit → push to dev → confirm → walkthrough.md → GOAL_COMPLETE
```

Not:

```
code changes → walkthrough.md → GOAL_COMPLETE   ← WRONG
```

---

### Rule 4 — Scratch files and build artifacts are not committed

The following should never be staged or committed:
- `scratch/` directory (test scripts, one-off analysis)
- `output/` directory
- `*.firebase/*.cache` files
- `numista_backend/database/*.db` files
- `numista_backend/latest_scraper_report.md`
- `numista_backend/sourcing_audit_report.md` (unless intentional)

Add these to `.gitignore` if they keep appearing as untracked.

---

### Rule 5 — Never push while another session is actively pushing

Multiple concurrent sessions pushing simultaneously causes cascading build failures.

- **Do not run two sessions that touch the same files at the same time.**
  (e.g. don't run a security triage and a dependency upgrade session in parallel —
  both will edit `requirements.txt` and fight each other.)
- If you suspect another session is mid-push, run `git fetch origin` and check
  `git log --oneline origin/dev..HEAD` before pushing.
- For long-running overnight tasks, use a **single `/goal` session**, not multiple
  parallel sessions over the same file area.

---

### Rule 6 — Mandatory Gemini Model Policy

Before changing any Gemini model ID (e.g., changing `gemini-3.5-flash` to anything else), you **MUST**:

1. Read the latest PDF documentation in:
   `C:\Users\ericd\Documents\MyVertexProject\Gemini Deprecation Schedules\`
2. Verify the "Shutdown date" and "Recommended replacement" for the proposed model.
3. NEVER downgrade to a model that has an earlier shutdown date than the current one (e.g., do not move from `gemini-3.5` back to `gemini-1.5` if `1.5` shuts down sooner).
4. If a model is 404ing, check the `location='global'` setting before assuming the model is retired.

---

### Rule 7 — NEVER push code changes directly to `main` without explicit user approval

**This rule overrides Rule 1 with respect to the `main` branch.**

Pushing to `main` deploys to the live production site (numista-vault.web.app) and is
**exclusively the owner's responsibility**. Agents do not merge to `main` under any
circumstances — not even after asking.
**All agent code changes MUST follow this workflow:**

1. Work on the `dev` branch (or a dedicated feature branch, e.g., `agent/feature-name`).
2. Commit and push to `dev` only:
   ```bash
   git checkout dev
   git add <files>
   git commit -m "<type>(<scope>): <summary>"
   git pull --rebase origin dev
   git push origin dev
   ```
3. When work is complete, present a summary to the user and say:
   > "Changes are pushed to `dev`. Please review and open a PR to deploy to the live site:
   > https://github.com/Numista-AI/Numista.AI/compare/main...dev"

**Agents NEVER:**
- Push to `main` directly
- Run `git merge` targeting `main`
- Run `git checkout main` followed by any push
- Ask "do you want me to merge to main?" and then do it

**The ONLY exception** where touching `main` is permitted:
- The designated deploy conversation (ID: 7485fc0a-544c-4a5f-8e87-ff9e22099b5e) when
  the user says **"Prepare to Deploy"**. That conversation is the sole gatekeeper for
  merging `dev` into `main` and deploying to the live site.

  **Deploy flow for that conversation:**
  1. Run `git fetch origin` and compare `origin/dev` vs `origin/main`
  2. Summarize every commit in plain English (no jargon)
  3. Say **"Ready to deploy?"** and wait for the user to say YES
  4. On YES: `gh pr create` + `gh pr merge` via GitHub CLI, confirm build is green
- Commits containing ONLY documentation files (`walkthrough.md`, `AGENTS.md`, scan reports,
  `*.md` in `scratch/`) that do not trigger a Flutter rebuild and do not affect the live site.

**Why this rule exists:** On 2026-07-09, Antigravity sessions pushed unauthorized UX redesign
changes directly to `main`, deploying them to the live site without the owner's review or
approval. This rule is a direct response to that incident.

---

### Rule 8 — Exit on Commands, Not Adjectives (Generate-and-Select)

Before declaring any code modification, refactor, or feature implementation complete:

1. **Criteria Must Be Commands, Not Adjectives**:
   Never rely on a subjective assessment (e.g. "code looks clean and complete"). Execute at least one machine-checkable command and confirm exit code 0:
   - **Frontend / Flutter**: `flutter analyze` or `flutter test <target_test>`
   - **Backend / Python**: `pytest numista_tests/<target_test>.py`
   - **E2E / Browser**: `npx playwright test <target_spec>`
   - **Git Hygiene**: `git status` confirming only target files modified.

2. **Send Failures Back to the Loop**:
   If a test or command fails, do not silently patch around it or declare partial success. Feed the exact terminal traceback back into the editing loop until the test passes.

3. **Pre-Flight Brief Testing for Overnight `/goal` Runs**:
   Before launching a multi-hour autonomous `/goal` session, test the task brief against an isolated perspective to detect hidden ambiguities and prevent correlated failures.

