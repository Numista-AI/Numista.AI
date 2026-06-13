# Numista.AI Automated Test Framework

Automated Playwright end-to-end tests for **https://numista.ai**.
Runs every 2 days at 2:00 AM and generates a morning report.

## Quick Start

```powershell
# Run tests NOW (manually)
cd c:\Users\ericd\Documents\MyVertexProject\numista_tests
npx playwright test

# Run with browser visible (debug mode)
npx playwright test --headed

# Run a single suite
npx playwright test tests/01-homepage.spec.js

# View HTML report after run
npx playwright show-report
```

## Test Suites

| File | Tests | What it covers |
|------|-------|----------------|
| `01-homepage.spec.js`       | 7  | HTTP 200, title, Flutter render, no JS errors, load speed |
| `02-auth-ui.spec.js`        | 8  | Sign In, Create Account, form switching, Browse Demo, Try It Free |
| `03-demo-navigation.spec.js`| 19 | Browse Demo flow, all 11 nav items, sidebar, Ask Morgan, errors |
| `04-registration.spec.js`   | 8  | Create Account form, empty submit, Terms checkbox, double-click |
| `05-navigation.spec.js`     | 12 | Back button, refresh, rapid clicks, all demo pages individually |
| `06-edge-cases.spec.js`     | 10 | Keyboard, scroll, network errors, Sign Out, out-of-order clicks |

**Total: 64 tests**

## Morning Reports

After each run, a markdown report is generated in `reports/`:
```
reports/
  2026-06-15_morning_report.md   ← Today's report
  2026-06-13_morning_report.md   ← Previous report
  runner.log                     ← Full run log
```

To manually generate a report from last run:
```powershell
node generate_report.js
```

## Automated Schedule

The task is scheduled via Windows Task Scheduler (every 2 days at 2 AM).

```powershell
# Install/reinstall the schedule
.\setup_scheduler.ps1

# Trigger a manual run via Task Scheduler
Start-ScheduledTask -TaskName "NumistaAI-AutoTests"

# View in Task Scheduler UI
taskschd.msc

# Remove the schedule
Unregister-ScheduledTask -TaskName "NumistaAI-AutoTests" -Confirm:$false
```

## Reading Your Morning Report

Open the latest `.md` file in `reports/` each morning:
- ✅ **ALL CLEAR** — everything working, no action needed
- ⚠️ **MINOR ISSUES** — 1-3 tests failed, investigate
- 🚨 **ATTENTION REQUIRED** — 4+ tests failed, critical issues

## Screenshots

Every run saves screenshots to `screenshots/`:
- `demo-*.png` — each nav page in demo mode
- `create-account-*.png` — registration form states
- `after-*.png` — state after actions (refresh, back, signout)
- Failure screenshots are auto-saved by Playwright

## Tech Stack

- **[Playwright](https://playwright.dev/)** — browser automation
- **Chromium** — headless Chrome
- **Node.js** — report generation
- **Windows Task Scheduler** — automated scheduling

## Notes on Flutter Web Testing

Numista.AI is built with Flutter Web (CanvasKit renderer). DOM-based selectors
do not work on Flutter web apps. Tests use:
- **Screenshot size validation** (blank pages < 50KB, real content > 100KB)
- **Mouse coordinate clicks** for button interactions
- **Flutter element detection** (`flt-glass-pane`) for render validation
- **Console/pageerror listeners** for JavaScript error detection
