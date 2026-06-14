# Add Coins – Bulk – By Holder Image (Binder Scan Feature)

## Overview

This feature allows users to photograph their physical coin collection binders/folders and have Numista.AI automatically identify which coins are present (and absent), then add them to the collection with the binder's image attached. It also supports checklist PDFs/images as an alternative input method.

---

## User Review Required

> [!IMPORTANT]
> **Firestore Cost:** Delta detection (comparing new scan to previous) requires fetching the full prior binder state from Firestore on each upload. For a 60-coin binder, this is negligible. Please confirm this is acceptable.

> [!IMPORTANT]
> **Storage Location Naming:** The system will use the book/binder's detected title (e.g., "50 State Commemorative Quarters Collector's Map") as the `Storage Location` for all coins added via that scan. Users can rename it. Does this naming convention work for you?

> [!WARNING]
> **Duplicate Handling Logic:** A coin in a binder is treated as a **separate, distinct item** from an identically-described coin stored elsewhere. The uniqueness key for binder coins will be `Year + Mint Mark + Denomination + Storage Location`. This means if you have a 1999-P NJ Quarter both in your binder AND in your regular collection, both will appear — with a confirmation prompt asking you to verify the separate storage. Please confirm this logic.

> [!CAUTION]
> **Multi-Mint Clarification:** The AI will ask about P vs D mint marks when it can't determine them visually. For the Alternate Mint page (labeled "D"), the AI will auto-assign "D" mint mark to all coins on that page. For the map page, it will default to "P" (or whichever mint is shown on the right side legend). You can override per-coin in the confirmation step.

---

## Architecture

### Data Flow

```
User photos binder pages → Flutter picks images
    → Upload to backend /api/analyze_binder_scan
    → Gemini 2.5 Pro multimodal analyzes ALL images together
    → AI returns: { book_title, programs_detected, coins_present, coins_absent }
    → Coins uploaded to GCS bucket (as binder_images/)
    → User reviews results in new BinderScanReviewScreen
    → Confirms coins, fills metadata (cost, date, retailer)
    → Committed to Firestore with Storage Location = book_title
    → Book view available via "My Binders" section
```

### New Firestore Structure

```
users/{email}/
  coins/{coinId}                   ← existing, no change
  binder_scans/{binderId}          ← NEW: one doc per binder
    title: "50 State Commemorative Quarters..."
    programs: ["50 State Quarters", "DC & US Territories"]
    mint_pages: { "P": "map_page", "D": "alternate_mint_page" }
    last_scan_date: Timestamp
    image_urls: [gs://..., gs://...]
    coin_slots: [                  ← full expected coin list
      { year: "1999", mint: "P", subject: "Delaware", present: true, coinId: "abc123" },
      { year: "1999", mint: "D", subject: "Delaware", present: false, coinId: null },
      ...
    ]
```

---

## Proposed Changes

### Backend — New API Endpoint

#### [MODIFY] [main.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py)

Add three new FastAPI endpoints:

**`POST /api/analyze_binder_scan`**
- Accepts: `user_email` (form), `binder_title` (form, optional), `images[]` (multiple files: JPG/PNG/PDF)
- Logic:
  1. Upload all images to GCS under `binder-scans/{user_email}/{uuid}/`
  2. Send ALL images + a comprehensive structured prompt to **Gemini 2.5 Pro** multimodal
  3. Prompt tells the AI to:
     - Detect the binder title from any text visible in images
     - Identify all programs (e.g., "50 State Quarters" + "DC & Territories")
     - Detect which page layout is which mint mark (map=P, alternate=D)
     - For EVERY coin slot on every page: determine if a coin is present (slot filled) or absent (slot empty)
     - Identify the coin: Year, State/Subject, Denomination
     - Flag when mint mark is ambiguous
  4. Return structured JSON with `book_title`, `programs`, `coin_slots[]`, `image_gcs_urls[]`

**`POST /api/analyze_checklist`**
- Accepts: `user_email`, `images[]` or `file` (PDF)
- Same Gemini multimodal analysis but tuned for paper checklists (checked boxes, stamps, marks)
- Returns same coin_slots structure

**`POST /api/confirm_binder_scan`**
- Accepts: full confirmed coin list + binder metadata
- Creates/updates `binder_scans/{binderId}` document
- Adds confirmed present coins to `review_queue` (same staging area as invoice import)
- Sets `Storage Location` = binder title on all staged coins
- Sets `image_url_obverse` = the GCS URL of the relevant binder page image
- If binder exists already (delta scan): only stages **newly added** coins

---

### Flutter — New Screen & Tab

#### [NEW] `lib/screens/binder_scan_screen.dart`

A new multi-step wizard screen with these phases:

**Phase 1: Upload**
- Prominent "📷 Upload Binder Photos" button (multi-image, PNG/JPG)
- "📄 Upload Checklist (PDF/Image)" toggle  
- Optional: manual binder title text field (pre-filled once AI detects it)
- Shows uploading progress per image

**Phase 2: AI Analysis (Processing)**
- Full-screen animated state: "Numista.AI is examining your binder..."
- Shows progress steps: "Identifying coins...", "Checking all pages...", "Done!"

**Phase 3: Results Review**
- Split view: **Thumbnail of binder page** on left | **Coin grid on right**
- Grid shows every expected coin slot (all ~110 state quarter slots for this example)
- ✅ Green = coin present (AI found it)   🔴 Red = missing (empty slot)
- Each row shows: Year | State | P Mint | D Mint | Status
- User can click any coin to toggle present/absent, or change mint mark
- "Mint Mark Clarification" banner appears if AI was uncertain

**Phase 4: Metadata Entry**
- Bulk fields: Purchase Cost, Purchase Date, Retailer (applied to all)
- Storage Location (pre-filled with detected book title, editable)
- Individual coin notes field

**Phase 5: Duplicate Check**
- For each present coin, backend checks if same Year+Mint+Denomination already exists in collection **with a different Storage Location**
- Renders confirmation dialogs: "Your 1999-P New Jersey Quarter is separate from the same coin in your binder, correct?"

**Phase 6: Confirmation**
- Summary: "Adding 47 coins, 14 already missing from your binder"
- "Add to Collection" button → commits to review_queue → navigates to Review Hub

---

#### [MODIFY] `lib/screens/add_coins_hub.dart`

Add a **5th tab**: "Binder/Book Scan" with icon `Icons.menu_book`
- Clicking opens `BinderScanScreen` as a full-page overlay or new tab content
- Description: "Photograph your collection binder. AI identifies what you have and don't have."

---

#### [NEW] `lib/screens/my_binders_screen.dart`

A new "My Binders" section accessible from the main navigation:

**Layout:**
- Card grid showing each binder registered by the user
- Each card: binder image thumbnail | title | coins present count | coins total count | progress bar
- Clicking a binder card opens **BinderDetailView**

**BinderDetailView:**
- Shows the binder page image(s) as a scrollable gallery at top
- Below: filterable coin list
  - Filter: "Present" | "Missing" | "All"
  - Each row: Year | Subject | Mint | Status | Link to coin in My Collection
- "Re-scan Binder" button → opens upload flow again for delta detection
- Delta detection compares new scan result against previous `coin_slots[]` in Firestore
- Shows only newly-added coins for confirmation: "We found 3 new coins since your last scan: 2008P Alaska, 2007D Montana, 2005P Oregon. Is this correct?"

---

#### [MODIFY] `lib/screens/base_layout.dart`

Add "My Binders" to the navigation sidebar, positioned after "My Collection" and before "Wishlist".

---

### Flutter — New Service

#### [NEW] `lib/services/binder_service.dart`

Handles:
- Fetching all binders for current user from Firestore
- Fetching coin slot status for a specific binder
- Computing delta between two scans
- Building the "missing coins" list for a binder view
- Checking if a proposed coin would be a cross-location duplicate

---

### Flutter — Widgets

#### [NEW] `lib/widgets/binder_coin_slot_card.dart`
A visual coin slot widget: circular coin placeholder with present/absent state indicator. Shows the coin details below. Supports tap-to-toggle and mint mark dropdown.

#### [NEW] `lib/widgets/binder_result_grid.dart`
Full binder grid view — renders all slots in rows by year, grouped by program/page, with filtering.

---

## AI Prompt Engineering (Key Design Detail)

The Gemini prompt for binder analysis will be carefully engineered to handle:

1. **Multi-page scans** — All images sent in a single multimodal request so the AI can cross-reference across pages
2. **Page identification** — "The page labeled 'Alternate Mint – Use this space for D mint coins' = Denver mint coins"
3. **Slot occupancy** — Distinguish between: filled slot (coin present), empty slot (fabric/cardboard visible), and partially visible slot
4. **Combined programs** — "This book contains both 50 State Quarters AND DC/Territories; list all slots for both"
5. **Mint mark assignment** — "For the US map page, assume P mint unless labeled otherwise. For the 'Alternate Mint' page, assume D mint."
6. **Ambiguity flags** — AI will flag coins where it's uncertain of mint mark with `"mint_uncertain": true`

**Sample prompt structure:**
```
You are an expert numismatic AI analyzing photos of a coin collector's binder.
Images provided: [image1=US map page, image2=Alternate Mint page, ...]

For EACH coin slot visible across ALL pages:
1. Is a coin physically present in the slot? (coin visible vs empty fabric)
2. What coin belongs there? (year, state/subject, denomination)
3. What mint mark applies based on page layout?
4. Are you certain of the mint mark? Flag if uncertain.

Return JSON: {
  "book_title": "...",
  "programs": ["50 State Quarters", "DC and US Territories"],
  "page_mint_assignments": {"map_page": "P", "alternate_mint_page": "D"},
  "coin_slots": [
    { "year": "1999", "subject": "Delaware", "denomination": "Quarter",
      "mint": "P", "mint_uncertain": false, "present": true,
      "page": "map_page", "position_hint": "top-left" }
  ]
}
```

---

## Checklist Feature (Associated)

The "Upload Checklist" flow is nearly identical but the AI prompt is adjusted:
- Instead of looking for physical coins in slots, look for **check marks, stamps, stickers, or handwritten marks** next to coin entries
- The checklist PDF from Littleton Coin Co. (in the GCS bucket) will be used as a training/testing reference
- Returns same `coin_slots` structure with `present: true` for checked items

---

## Verification Plan

### Backend Tests
1. Deploy updated `main.py` to Cloud Run
2. Test `/api/analyze_binder_scan` with the two provided binder photos (map page + alternate mint page)
3. Verify AI correctly identifies: ~47 coins present on map page (P mint), ~20 coins on alternate mint page (D mint)
4. Verify missing slot detection

### Flutter Tests
1. Run app, navigate to Add Coins → Binder/Book Scan tab
2. Upload the test binder photos  
3. Verify Phase 3 review screen shows correct present/absent breakdown
4. Confirm a subset of coins and verify they appear in Review Hub with correct Storage Location
5. Navigate to My Binders to verify binder appears with correct coin count
6. Upload binder images again to test delta detection (should show 0 new coins)

### Duplicate Detection Tests
1. Manually add a "1999-P New Jersey Quarter" to the collection
2. Upload binder scan containing the same coin
3. Verify confirmation dialog appears before adding

---

## Open Questions

> [!IMPORTANT]
> **Navigation:** Should "My Binders" be a top-level navigation item in the sidebar, or a sub-section within "My Collection"? My recommendation: top-level item for discoverability.

> [!IMPORTANT]
> **Checklist PDF location:** You mentioned the example checklist PDF is at `numista-training-docs/Numista.AI Training Data/US Mint Coin Programs/LC-KGW-50-State-Commemorative-Quarter-Checklist`. Should I download and test against this file during implementation?

> [!IMPORTANT]
> **GCS Bucket for Binder Images:** I'll create a `binder-scans/` prefix in the existing storage bucket for uploaded binder photos. Please confirm the GCS bucket name to use.

> [!NOTE]
> **Coin Image Assignment:** Per your requirements, the binder page image will be stored as `image_url_obverse` for every coin added via that scan. Should a specific page crop (zoomed to that coin's slot) be created, or is the full page image acceptable?

> [!NOTE]
> **Phase rollout:** This is a large feature (~8 new files, 3 new API endpoints). I recommend implementing in this order: (1) Backend API + AI prompt, (2) Binder Scan wizard screen, (3) My Binders view. Confirm to proceed with full implementation or phased approach.
