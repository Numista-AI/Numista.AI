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
3. Pull and rebase, then push — **always use this exact sequence**:
   ```bash
   git pull --rebase origin main && git push origin main
   ```
   The `--rebase` absorbs any commits that landed since your last pull (from other sessions,
   the auto-backup cron, or the user) and places your commit cleanly on top.
   Never use a bare `git push` without the pull-rebase prefix.
4. Confirm the push succeeded (look for `branch -> branch` in the output).

**Only after a confirmed push may you write `walkthrough.md` or emit `<!-- GOAL_COMPLETE -->`.**

> A task that is not pushed to GitHub is NOT done — it is only done locally.

---

### Rule 2 — Check branch sync at the start of every session

At the beginning of any session that will make code changes, run:

```bash
git status
git log --oneline origin/main..HEAD
git log --oneline origin/dev..HEAD
```

If either local branch is **ahead** of its remote, push those commits first before starting new work:

```bash
git pull --rebase origin main && git push origin main
git pull --rebase origin dev  && git push origin dev
```

This prevents commits from being silently stranded when you switch branches between sessions.

---

### Rule 3 — Never write the walkthrough before pushing

The order must always be:

```
code changes → git add → git commit → git push → confirm → walkthrough.md → GOAL_COMPLETE
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

Multiple concurrent sessions pushing to `main` simultaneously causes cascading build
failures. Before starting any session that will push to `main`:

- **Do not run two sessions that touch the same files at the same time.**
  (e.g. don't run a security triage and a dependency upgrade session in parallel —
  both will edit `requirements.txt` and fight each other.)
- If you suspect another session is mid-push, run `git fetch origin` and check
  `git log --oneline origin/main..HEAD` before pushing.
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

