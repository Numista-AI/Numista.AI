# PROGRESS: NET-647 Mint FAIL-FIX on p7-gate (Execution Commenced)

**Date & Time:** Thu 29 Oct 2026, 7:25 PM ET  
**Station From:** AG CoS (builder) (`9a4c2c35-9ee3-4d58-851a-199248a3bc68`)  
**Station To:** Desk (Eric Seaman, Founder) / Grok CoS (`87de4a6a`) / Field Tester  
**Track:** NET-647 Mint FAIL-FIX on `p7-gate` (Branch: `p7-v8.9` only)  
**Status:** **IN PROGRESS (Executing P1–P3 surgical fixes)**  

---

## 1. Context & Sequencing Lock
- Received Founder YES (Eric, 7:24 PM ET) to execute **NET-646 Plan v3.3** (Scores: GB CoS 96, SAG 96 GO).
- **Strict Execution Order Enforced:**
  1. **NET-647 on `p7-gate` FIRST:** Must complete all 9 fixes, run full Rule 8 test suite, deploy to `p7-gate`, and achieve Field Tester PASS (including Folder-Drop verification).
  2. **NET-646 WAITS:** Zero catalog commits or modifications until NET-647 is officially DONE.
  3. **Live & Main LOCKED:** No live deployment, no merge to `main`. Preview channel only. Stripe stays completely OFF.

---

## 2. NET-647 Execution Timeline & Target Hand-off
- **Start Time:** 7:25 PM ET
- **Active Changes in Flight on `p7-v8.9`:**
  - `add_coins_hub.dart`: P1 direct launch for "Upload an invoice", P1 single-scroll container eliminating scroll trap.
  - `add_coins.html`: P2 above-the-fold compact header, P2 auto-scroll on file pick and completion, P3 delete line 390 dealer search tip, P3 consolidate duplicate paper-trail links.
  - `review_hub_screen.dart`: P3 cost "$X.XX each" for QTY > 1, P3 remove top storage chip, P3 add coin image thumbnail to review card.
  - `morgan_guides.dart`: P3 reposition Morgan invoice guide step 1 away from Add Coins quick cards.
- **Estimated Completion for NET-647 Code & Deploy:** **~8:05 PM ET** (40 mins).
- **Field Tester Baton Target:** **~8:05 PM ET** (Folder-Drop & All-Invoices test).
- **NET-646 P0 Start Target:** **~8:20 PM ET** (Immediately following Field Tester PASS and DONE filing).

---

## 3. Progress Update
All target files mapped. Branch `p7-v8.9` checked out. Applying surgical edits now.

`OVER`
