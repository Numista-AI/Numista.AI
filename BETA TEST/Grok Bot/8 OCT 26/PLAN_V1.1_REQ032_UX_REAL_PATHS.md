# PLAN V1.1 — REQ_032 UX Real File Paths
Prepared by: Antigravity CoS  
Date: 2026-10-12  
Purpose: Satisfies COS_SCORE_REQ032_UX.md condition #1 and #2 — real paths with file:line before code is written.

---

## Actual Navigation Structure (from base_layout.dart, read 2026-10-12)

### Mobile bottom nav — `base_layout.dart:535-631`
5 tabs (NavigationBar, `NavigationDestination`):
1. **Home** → `'Home Dashboard'` (base_layout.dart:536, 606-610)
2. **Programs** → `'Coin Programs'` (base_layout.dart:537, 611-615)
3. **Collection** → `'My Collection'` (base_layout.dart:538, 616-620)
4. **AI Chat** → `'AI Deepdive'` (base_layout.dart:539, 621-625)
5. **Settings** → `'Settings & Backup'` (base_layout.dart:540, 626-630)

### Desktop/tablet sidebar — `base_layout.dart:749-837` (ListView, `_buildNavItem` calls)

**Top level (no section header):**
1. Home Dashboard (749)
2. Coin Programs (752)
3. Upcoming Releases (754)

**MY COLLECTION section (section header: base_layout.dart:756):**
4. All (759) — sub-item
5. Coins (761) — sub-item
6. Currency Collection (762) — sub-item
7. World and Specialty (763) — sub-item
8. Inventory (764) — sub-item
9. My Wishlist (769)

**ASSET VAULT & TRANSFERS section (header: 772):**
10. Estate Planning (773)
11. Attorney Portal (774)
12. Lateral Transfer (775)
13. Claim Transfer (776)

**ADD NEW COINS/NOTES/ETC. section (header: 778):**
14. Add new coins/notes/etc. (781)
15. Microscope Scanner (783)
16. Review Hub (794) — with badge count

**AI TRAINING section (header: 800):**
17. AI Trainer Board (801)
18. Admin Grade Flags (805) — admin-only (email check: base_layout.dart:803)
19. Beta Feedback Inbox (815) — admin-only, with badge count
20. Admin: Support Portal (821) — admin-only

**NUMISMATIC RESEARCH section (header: 825):**
21. Error Library (826)
22. Glossary Academy (827)
23. Coin Search (828)
24. AI Deepdive (829)

**Other:**
25. Settings & Backup (832)
26. Our Team (834)
27. Customer Service (835)
28. My Tickets (836)
29. 🔍 Numista Lookup (837)

**Total sidebar items: 29** (confirms Grok CoS's count over the plan's estimate of 25). Admin-only items: 3 (#18, #19, #20) — shown only when `email == 'jseaman1204@gmail.com' || email.endsWith('@numista.ai')`.

Non-admin users see 26 items. Admin users see 29.

---

## Actual Font Sizes in Sidebar (from base_layout.dart read)

| Line | Size | Location |
|---|---|---|
| 717 | 11px | Sidebar display name |
| 721 | 9px | Sidebar email address |
| 877 | 11px | "Send Beta Feedback" button label |
| 895, 906 | 12px | ListTile subtitle in feedback dialog |
| 952 | 11px | Sign Out button label |
| 1196 | 13px | Nav item label (confirmed in `_buildNavItem`) |
| 1214 | 10px | Nav item sub-label |
| 1281 | 22px | Morgan sidebar button (acceptable) |
| 1320 | 10.5px | Small text label |
| 1348, 1385 | 12px | Tooltip text |
| 1358, 1395 | 12px | TextStyle in button |
| 1549 | 11px | Legend text |
| 1554 | 9px | Legend sub-text |

**All sizes below 16px** are in violation of REQ_032 Fix 2. The centralized theme token (`NumistaTheme.textBodySm = 16.0`) will replace all of these. Exceptions to document: sidebar email (9px) → increase to 12px minimum even in collapsed mode.

---

## Fix 4 Correct Scope — Navigation Reduction Plan

**Current:** Mobile = 5 tabs ✅. Desktop sidebar = 29 items (26 non-admin, 29 admin).

**Target:** Desktop sidebar reduced to **6 top-level items + "More ▼" overflow section.**

Top 6 (to remain visible always):
1. Home
2. My Coins (→ 'My Collection')
3. Add a Coin (→ 'Add new coins/notes/etc.')
4. Coin Programs
5. Help & Ask Morgan (→ triggers `_showMorganDialog`)
6. More ▼ (bottom sheet or expandable with remaining 20-23 items)

"More ▼" groupings:
- My Account: Wishlist, Settings & Backup, Estate Planning, Attorney Portal
- Transfers: Lateral Transfer, Claim Transfer, Transfer Inbox
- Research: Error Library, Glossary Academy, Coin Search, AI Deepdive, Upcoming Releases
- Help: Customer Service, My Tickets, Our Team, Numista Lookup
- Review (if scanner in queue): Review Hub, AI Trainer Board
- Admin (if admin): Admin Grade Flags, Beta Feedback Inbox, Admin: Support Portal

Mobile bottom nav stays as 5 tabs — no change needed (already compact).

**Regression test must cover:** all 29 routes still reachable (26 non-admin + 3 admin).

---

## Add Coin Screen Real Location

`numista_mobile/lib/screens/add_coins_hub.dart` — this is the real file name (confirmed from screens/ directory listing). Fix 5 changes apply here.

## PIN Screen Real Location

`numista_mobile/lib/screens/login_screen.dart:32-104` — PIN controller is `_pinCtrl` (line 32), sign-in function at lines 88-104. Current implementation uses `TextEditingController` with `obscureText` on a TextField — this is what causes the glyph issue. The fix replaces this with a custom 6-box widget.

## Theme File Real Location

`numista_mobile/lib/services/theme_provider.dart` — exists, has `TextScaleMode` enum and SharedPreferences loading. The new `numista_theme.dart` tokens file will be created at `numista_mobile/lib/theme/numista_theme.dart` (directory to be created).

---

## Files Changed (updated from V1 guesses → real paths)

| File | Change | Real path confirmed |
|---|---|---|
| `numista_mobile/lib/theme/numista_theme.dart` | CREATE | Directory does not exist yet; create it |
| `numista_mobile/lib/screens/base_layout.dart` | Replace font sizes 9-15 with tokens; sidebar 6-item restructure | ✅ real |
| `numista_mobile/lib/screens/login_screen.dart` | Fix PIN widget (lines 32-104) | ✅ real |
| `numista_mobile/lib/screens/add_coins_hub.dart` | Fix 5 — 3 primary choices | ✅ real (was guessed as add_coin_screen.dart) |
| `numista_mobile/lib/services/theme_provider.dart` | No change needed; tokens are separate file | ✅ real |

---

*V1.1 note filed. Code build on dev may proceed per COS_SCORE_REQ032_UX.md PASS.*
