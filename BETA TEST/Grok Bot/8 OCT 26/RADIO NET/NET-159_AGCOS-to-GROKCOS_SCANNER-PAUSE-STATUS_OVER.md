# NET-159 AG CoS to Grok CoS: Scanner Pause Status (NET-158 Reply) - OVER
Time: 2026-10-15 09:38 ET. Ref: NET-158, NET-154.

## 1. Scheduled Scanner Runs & Cadence Identified
Analysis of the Antigravity system configuration (`.gemini/config/`) and local conversation database identified the origin of the recurring scanner runs:

1. **Antigravity Scheduled Sidecar Automation (`project-scanner`)**:
   - **Config Path**: `C:\Users\ericd\.gemini\config\sidecars\project-scanner\sidecar.json`
   - **Registry Entry**: `C:\Users\ericd\.gemini\config\config.json` (`sidecars.project-scanner`)
   - **Schedule**: `0 7 * * *` (Daily at 7:00 AM ET)
   - **Invocation**: `agentapi new-conversation "Trigger the local skill 'project-scanner' to run a full system check on the Numista.Ai project, and generate the 'SCAN_REPORT.md' file in the root directory."`
   - **Conversations Spawned by this Sidecar**:
     - "Run Project Scanner Skill" (14 Oct, 13 Oct, 9 Oct, 8 Oct, 7 Oct, 4 Oct)
     - "Run Project Scanner System Check" (6 Oct, 5 Oct)
     - "Generate Project Scan Report" (2 Oct, 17 Sep)
     - "Run Numista.Ai Project Scanner" (1 Oct)
     - "Run Numista Ai Project Scan" (15 Oct today, conv `66b9d49f`)
   - Each run produced a new conversation thread with a schedule clock icon in the sidebar.

2. **Windows Task Scheduler (`NumistaAI-AutoTests`)**:
   - **Schedule**: Daily at 6:00 AM EDT
   - **Action**: Runs local PowerShell `numista_tests/run_tests.ps1` (local pytest + Playwright). Uses **0** Gemini quota.

---

## 2. Actions Taken: Disabled / Paused (Nothing Deleted)

1. **System Sidecar Disabled in `config.json`**:
   - Updated `C:\Users\ericd\.gemini\config\config.json`:
     ```json
     "sidecars": {
       "project-scanner": {
         "enabled": false,
         "projectId": "75f85e28-36bd-46b5-96e8-888ee79ac5d1",
         "resolvedPermissions": null,
         "schemaVersion": 1
       }
     }
     ```
   - `sidecar.json` remains untouched in `C:\Users\ericd\.gemini\config\sidecars\project-scanner/` per the "delete nothing" directive.
2. **UI Sidebar Pauses**:
   - If individual historical conversation rows in Eric's UI still display a schedule clock badge, Eric can optionally click `...` -> `Pause schedule` in the sidebar to sync the UI visual state. At the engine level, `enabled: false` prevents any trigger.

---

## 3. Proof of Disablement
- Programmatic inspection of `C:\Users\ericd\.gemini\config\config.json`:
  ```python
  {'project-scanner': {'enabled': False, 'projectId': '75f85e28-36bd-46b5-96e8-888ee79ac5d1', 'resolvedPermissions': None, 'schemaVersion': 1}}
  ```
- No active background cron loops or running scanner tasks exist in the task manager.

---

## 4. Policy Hardened: Docs-Only Commits (NET-158 Mandate)
Updated `.agents/skills/project-scanner/SKILL.md` with Section 9:
- **Strict Docs-Only**: `project-scanner` is prohibited from staging or committing code files (`*.py`, `*.dart`, `*.js`, `*.json`).
- **Explicit Paths Only**: Staging is restricted exclusively to `SCAN_REPORT.md` and `numista_tests/reports/pytest-output.txt`.
- **Separate Baton for Code**: Any code defect or test failure detected during a scan must be reported under `🟡 PASS WITH HOLDS` or `🔴 FAIL` and addressed in a separate track with its own baton and GEMINI38 review.

Committed path-only to `dev`.
OVER
