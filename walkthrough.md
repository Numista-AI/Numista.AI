# Walkthrough — Daily Task Schedule Reconfiguration (7:00 AM)

I have reconfigured the local Windows Task Scheduler automated test job (`NumistaAI-AutoTests`) to run every morning at **7:00 AM** with `WakeToRun` enabled.

## 🛠️ Changes Implemented

1. **Schedule Configuration Update**:
   - **[setup_scheduler.ps1](file:///C:/Users/ericd/Documents/MyVertexProject/numista_tests/setup_scheduler.ps1)**:
     - Reconfigured `$startTime` to **7:00 AM** (`-Hour 7 -Minute 0 -Second 0`).
     - Added `-WakeToRun` to `New-ScheduledTaskSettingsSet` so Windows will automatically wake the laptop at 7:00 AM if it is sleeping.
     - Updated description and task outputs.

2. **Windows Task Scheduler Registration**:
   - Executed `setup_scheduler.ps1` to update the active Windows Task Scheduler task `NumistaAI-AutoTests`.
   - Verified that `NextRunTime` is now set to **7/26/2026 7:00:00 AM** with `WakeToRun: True`.

---

## 🧪 Verification Results

* **Task Name**: `NumistaAI-AutoTests`
* **State**: `Ready`
* **Schedule**: Daily at 7:00 AM
* **Next Run Time**: 7/26/2026 7:00:00 AM
* **WakeToRun**: `True` (Windows will wake computer to execute test suite at 7 AM)

---

## 📦 Git Synchronization
- Committed and pushed changes to `origin/dev` (commit `6101b3b`):
  ```bash
  git pull --rebase origin dev && git push origin dev
  ```
