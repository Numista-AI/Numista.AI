# Numista.AI Automated Testing Framework
## Built June 13, 2026

---

## What Was Built

A complete, automated end-to-end testing system for **https://numista.ai** that:
- Runs 63 Playwright tests against the live production site
- Executes automatically every 2 days at 2:00 AM (both locally and in the cloud)
- Generates a markdown morning report with pass/fail details and screenshots
- Sends an automatic summary to this Antigravity conversation every Monday, Wednesday, and Friday at 7:30 AM

---

## Files Created

All test files live in:
```
c:\Users\ericd\Documents\MyVertexProject\numista_tests\
```

| File | Purpose |
|------|---------|
| `tests/01-homepage.spec.js` | HTTP 200, title, Flutter render, load speed, no JS errors |
| `tests/02-auth-ui.spec.js` | Sign In / Create Account UI, Browse Demo, Try It Free buttons |
| `tests/03-demo-navigation.spec.js` | Browse Demo flow, all 11 nav sidebar items |
| `tests/04-registration.spec.js` | Create Account form validation edge cases |
| `tests/07-error-library.spec.js` | Error Library Verification — Firestore permission check |
| `tests/08-greysheet-valuation.spec.js` | **[v4.0]** Home Dashboard health, CPG portfolio value, Wishlist EPN, Estate Planning, backend API endpoints |
| `tests/09-deals-arbitrage.spec.js` | **[v4.0]** Arbitrage Deal Spotter card, DealsScreen launch, EPN affiliate endpoint, Wishlist scan |
| `tests/10-greysheet-coin-detail.spec.js` | **[v4.0]** Greysheet Pricing Table in Financials tab, valuation toggle in Settings, CAC, portfolio snapshot endpoint |
| `tests/05-navigation.spec.js` | In-app navigation, refresh, rapid clicks, all demo pages |
| `tests/06-edge-cases.spec.js` | Keyboard, scroll, network errors, Sign Out, resilience |
| `playwright.config.js` | Playwright settings: Chromium, 1280×720, retries, reporters |
| `generate_report.js` | Reads test-results.json → generates markdown morning report |
| `run_tests.ps1` | PowerShell wrapper called by Windows Task Scheduler |
| `setup_scheduler.ps1` | One-time script that registered the Windows Task Scheduler job |
| `README.md` | Full usage guide for the test framework |
| `reports/` | Morning reports saved here after each run (gitignored) |
| `screenshots/` | PNG screenshots of every page, saved each run (gitignored) |

GitHub Actions workflow:
```
c:\Users\ericd\Documents\MyVertexProject\.github\workflows\numista-ai-tests.yml
```

---

## How to Run Tests Manually

```powershell
cd c:\Users\ericd\Documents\MyVertexProject\numista_tests

# Run all 63 tests (generates report automatically)
npx playwright test

# Run a single suite
npx playwright test tests/01-homepage.spec.js

# Run with browser visible (useful for debugging)
npx playwright test --headed

# View the interactive HTML report after a run
npx playwright show-report

# Generate the morning report from last run's results
node generate_report.js
```

---

## Automated Schedule

### Local (Windows Task Scheduler)
- **Task name:** `NumistaAI-AutoTests`
- **Schedule:** Every 2 days at 2:00 AM
- **Requires:** Laptop on and connected to internet (sleep is OK, hibernate/shutdown is not)
- **Manage via:** `taskschd.msc` or PowerShell:
  ```powershell
  # Trigger manually
  Start-ScheduledTask -TaskName "NumistaAI-AutoTests"
  # Remove schedule
  Unregister-ScheduledTask -TaskName "NumistaAI-AutoTests" -Confirm:$false
  # Reinstall schedule
  .\setup_scheduler.ps1
  ```

### Cloud (GitHub Actions)
- **Repo:** https://github.com/Numista-AI/Numista.AI/actions
- **Schedule:** Every 2 days at 6:00 AM UTC (2:00 AM Eastern)
- **Requires:** Nothing — runs on GitHub's servers, laptop not needed
- **Trigger manually:** Actions tab → "Numista.AI Automated Tests" → "Run workflow"
- **Results:** Click any run → Summary tab (report pasted inline) or Artifacts section (downloadable)
- **Retention:** Reports kept 90 days, screenshots 30 days

### Morning Summary (Antigravity)
- **Conversation:** This one (1b2bf7ff-c2f1-4028-9ed2-001b8c36f4e9)
- **Schedule:** Monday, Wednesday, Friday at 7:30 AM Eastern
- **What it does:** Reads latest `.md` from `numista_tests\reports\` and posts a plain-English summary
- **Task ID:** task-282 (cron: `30 11 * * 1,3,5`)

---

## Morning Routine

```
2:00 AM  → Tests run automatically (GitHub cloud, no laptop needed)
2:15 AM  → Report written to numista_tests\reports\YYYY-MM-DD_morning_report.md
7:30 AM  → Antigravity reads report and posts summary to this conversation
```

**If tests pass:** You see "✅ All clear — numista.ai is healthy."

**If tests fail:** You see a list of what broke and why. Then say:
> *"Fix the failures from this morning's report"*

---

## Technical Notes (Flutter Web)

Numista.AI is built with **Flutter Web (CanvasKit renderer)**. This means:
- Standard DOM selectors (`getByRole`, `getByText`) **do not work**
- All button clicks use **coordinate-based mouse interaction**: `page.mouse.click(x, y)`
- Page health is validated by **screenshot file size** (blank page < 10KB, real content > 50KB)
- Flutter elements are detected via `flt-glass-pane` CSS selector
- Browser back button **does not navigate Flutter routes** (SPA behavior) — this is expected

### Button Coordinates (1280×720 viewport)
| Button | X | Y |
|--------|---|---|
| Browse Demo | 714 | 631 |
| Try It Free | 902 | 631 |
| Sign In tab | 1046 | 86 |
| Create Account tab | 1340 | 86 |

### Sidebar Nav Coordinates (in demo mode)
| Nav Item | X | Y |
|----------|---|---|
| Home Dashboard | 80 | 147 |
| My Collection | 70 | 172 |
| Review Hub | 66 | 198 |
| Coin Programs | 73 | 224 |
| Add New Coins | 75 | 250 |
| Microscope Scanner | 88 | 276 |
| Inventory | 59 | 302 |
| My Wishlist | 65 | 328 |
| Coin Search | 66 | 354 |
| AI Deepdive | 66 | 380 |
| AI Trainer Board | 77 | 407 |
| Sign Out | 100 | 716 |

---

## Test Results — Baseline (June 13, 2026)

| Suite | Tests | Result |
|-------|-------|--------|
| 01 - Homepage | 7 | ✅ All pass |
| 02 - Auth UI | 8 | ✅ All pass |
| 03 - Demo Navigation | 19 | ✅ All pass |
| 04 - Registration | 8 | ✅ All pass |
| 05 - Navigation | 12 | ✅ All pass |
| 06 - Edge Cases | 9 | ✅ All pass |
| **TOTAL (pre-v4.0)** | **63** | **100% ✅** |

## Test Results — v4.0 Baseline (July 8, 2026)

> [!NOTE]
> Three new test suites were added to cover the Greysheet Market Valuation integration (v4.0). They have not yet been run against production. The next scheduled run will establish the new baseline.

| Suite | Tests | Result |
|-------|-------|--------|
| 01 - Homepage | 7 | ✅ (established baseline) |
| 02 - Auth UI | 8 | ✅ (established baseline) |
| 03 - Demo Navigation | 19 | ✅ (established baseline) |
| 04 - Registration | 8 | ✅ (established baseline) |
| 05 - Navigation | 12 | ✅ (established baseline) |
| 06 - Edge Cases | 9 | ✅ (established baseline) |
| 07 - Error Library | 1 | ✅ (established baseline) |
| 08 - Greysheet Valuation | 12 | ⏳ Not yet run |
| 09 - Deals & Arbitrage | 8 | ⏳ Not yet run |
| 10 - Greysheet Coin Detail | 14 | ⏳ Not yet run |
| **TOTAL** | **~98** | **63 baseline + 34 new** |

> [!NOTE]
> The "Dashboard unavailable" and "Could not load collection" errors shown in demo mode are **expected behavior** — the demo runs with a read-only account and cannot load real data. Tests verify these error states render gracefully rather than crashing.

---

## MCP / Playwright Integration

The Playwright MCP server is configured in:
```
C:\Users\ericd\.gemini\antigravity\mcp_config.json
```
This allows Antigravity to directly control a browser using `browser_*` tools (screenshot, click, navigate, etc.) for live interactive testing and debugging.

---

## How to Add a New Test

1. Create `numista_tests/tests/11-your-new-suite.spec.js`
2. Use coordinate-based clicks (see button coordinates above)
3. Use screenshot size validation for assertions
4. Run `npx playwright test tests/07-your-new-suite.spec.js` to verify
5. Commit and push — GitHub Actions picks it up automatically

---

*Generated by Antigravity | Conversation: 1b2bf7ff-c2f1-4028-9ed2-001b8c36f4e9*
