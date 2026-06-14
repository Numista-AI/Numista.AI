# Numista.AI — MVP Beta Checklist
**Goal:** Get 5–10 friends & family beta testing the app.
**Scope:** Image Upload + Wish List working, then stabilize what exists.
**Last updated:** 2026-04-30

---

## ✅ Already Done (Today)
- [x] Image pipeline: GCS upload, indexing, 3-tier fallback matching
- [x] Coin Set Viewer widget (Jamul set ingested, flip animation)
- [x] Roll / Batch Entry wizard (4 roll types, auto mint-mark fill)
- [x] AJ's collection: 99.97% image coverage (3,909/3,910)

---

## 🔴 Phase 0 — Hard Blockers (Nothing works without these)
*Must be done first. Estimated: 1–2 days.*

- [ ] **GCS bucket permissions** — Confirm `numista-reference-library` images serve publicly (or add signed URL generation to the backend). Images won't display in Flutter until this is resolved.
  - *Test:* Paste a `public_url` from Firestore into a browser — does it load without a login?

- [ ] **User authentication flow** — Sign-up, sign-in, and password reset must work end-to-end for a brand-new user on a fresh device (no existing account).
  - *Test:* Create a new account as `betauser01@gmail.com` from scratch. Can you log in and see an empty collection?

- [ ] **Backend health check** — Confirm `numista-backend-568985927038.us-central1.run.app` is healthy and all API endpoints respond (`/api/process_invoice`, `/api/import_spreadsheet`, etc.).
  - *Test:* `curl https://numista-backend-568985927038.us-central1.run.app/health` returns 200.

- [ ] **Firestore rules** — Ensure users can only read/write their own `users/{email}/coins` subcollection. No user should be able to see another's data.
  - *Test:* Verify Firestore Security Rules in Firebase Console → Rules.

---

## 🟠 Phase 1 — The Two Requested Features
*Estimated: 2–3 days.*

### 1A. Image Upload (User's Own Coin Photos)
Users should be able to attach their own photos to any coin in My Collection.

- [ ] **Obverse / Reverse upload buttons** — Already wired in `my_collection_screen.dart` (`_buildCoinVaultGallery`). Verify the upload actually saves to Firebase Storage under `users/{email}/coins/{coinId}/` and writes the URL back to Firestore.
  - *Test:* Upload a photo on web. Reload the page. Does the image still appear?

- [ ] **Mobile camera support** — `image_picker` is imported. Confirm it works on Android (and iOS if available) — both "take photo" and "choose from gallery."
  - *Test:* On Android, tap the upload button → camera opens → photo saves and displays.

- [ ] **Upload progress indicator** — `_uploadProgressObverse` state variable exists. Confirm it shows a linear progress bar during upload and clears when done.

- [ ] **Image delete / replace** — User should be able to swap a photo they don't like. Add a "Replace" option alongside the existing image.

- [ ] **GCS public URL display** — When no personal photo exists, fall back to the reference library image from `coin_image_index`. Confirm `CoinSetViewer` and single-coin inspector both display correctly.

### 1B. Wish List
- [ ] **Add to Wish List** — Verify the "Add to Wish List" button works from the coin inspector in My Collection and from the Program Manager / checklist view.
  - *Test:* Find a coin not in collection → add to Wish List → navigate to Wish List screen → coin appears.

- [ ] **Wish List screen** — Confirm the Wish List screen renders, shows all items, and supports removal.
  - *Test:* Add 3 items, remove 1, confirm 2 remain after reload.

- [ ] **Smart ownership detection** — When a coin is manually added that matches a Wish List item, the prompt to remove from Wish List appears (`_showWishlistMatchPrompt`). Verify this fires.

- [ ] **Wish List → Collection migration** — "I found it!" button on a Wish List item should move it to the collection (or prompt to fill in details first).

---

## 🟡 Phase 2 — Stabilize What Exists
*Polish and bug-fix existing features. Estimated: 3–5 days.*

### My Collection
- [ ] **Search works** — Type in the search box → table filters correctly. Test with year, mint, denomination, series.
- [ ] **Sort works** — Click every column header → ascending/descending toggles correctly.
- [ ] **Inspector panel** — Selecting any row shows the correct coin's details. No stale data from a previously selected coin.
- [ ] **Edit coin** — Can update a field (e.g., Condition) and the change persists after reload.
- [ ] **Delete coin** — Can remove a coin with a confirmation prompt. Confirm it's gone from Firestore.
- [ ] **`set_id` display** — Coins with a `set_id` show the `CoinSetViewer` strip in the inspector.
- [ ] **`roll_id` display** — Coins from a roll show a "Part of a roll of N" badge in the inspector.

### Add Coins Hub
- [ ] **Manual Entry** — Add a coin via the form → appears in My Collection immediately (or after refresh).
- [ ] **Invoice Scan** — Upload a PDF purchase invoice → coins extracted and appear in Review Hub.
- [ ] **PCGS Import** — Enter a cert number → coin details auto-populated → can confirm and add.
- [ ] **Roll / Batch Wizard** — Complete all 3 roll types (identical, sequential, lot) end-to-end.
- [ ] **Checklist Scan** — Upload a photo of a checked Littleton checklist → coins extracted correctly.
- [ ] **Excel/CSV Upload** — Upload a basic CSV with Year, Denomination, Mint columns → imports correctly.

### Review Hub
- [ ] **Pending items appear** — After any AI-extracted import, coins appear in Review Hub for confirmation.
- [ ] **Approve / Reject** — Approving moves coin to My Collection. Rejecting removes from queue.
- [ ] **Bulk approve** — "Approve All" button works for clean imports.

### Navigation & Layout
- [ ] **All 5 tabs navigate** — Home, Programs, Collection, AI Chat, Settings all load without crash.
- [ ] **Back navigation** — No orphaned screens or broken back-stack on mobile.
- [ ] **Responsive layout** — Works at 375px wide (mobile) and 1280px wide (desktop/tablet). No overflow errors.
- [ ] **Dark/light mode** — If supported, switching doesn't break layouts.

### AI Chat
- [ ] **Basic question works** — Ask "What is a Morgan Dollar?" → gets a coherent response.
- [ ] **Collection-aware question** — Ask "What's my most valuable coin?" → response references actual collection data.

---

## 🟢 Phase 3 — Beta Distribution & Onboarding
*Getting real users in. Estimated: 1–2 days.*

### Onboarding
- [ ] **Welcome screen** — New users see a brief "Welcome to Numista.AI" screen explaining what to do first.
- [ ] **Empty state** — A brand-new user with zero coins sees a helpful prompt ("Add your first coin!") not a blank table.
- [ ] **Error messages are human-readable** — No raw exceptions or Firestore error codes shown to users.

### Beta Access
- [ ] **Web URL** — Confirm the Flutter Web build is deployed and accessible at a stable URL (Firebase Hosting or Cloud Run). Share with beta testers.
- [ ] **Android APK / TestFlight** (optional for MVP) — If any testers prefer mobile-first, build a debug APK or TestFlight build. Not required for all 5–10 testers.
- [ ] **Beta tester accounts** — Create accounts for each tester OR confirm self-sign-up works cleanly.
- [ ] **Feedback channel** — Set up a simple way for testers to report bugs (Google Form, email alias `beta@numista.ai`, or a shared Discord/Slack channel).

### Legal / Privacy (Minimum)
- [ ] **Privacy notice** — One-line "Your data is stored securely and not shared" on the sign-up screen. (Full privacy policy can wait for public launch.)
- [ ] **Terms of use acknowledgement** — Checkbox on sign-up: "I agree this is a beta — features may change."
- [ ] **Image attribution** — Confirm reference library images display attribution text (already in `CoinSetViewer` and the index `attribution` field).

---

## 📊 Summary Estimate

| Phase | Items | Est. Days |
|---|---|---|
| Phase 0 — Blockers | 4 | 1–2 |
| Phase 1 — Image Upload + Wish List | 9 | 2–3 |
| Phase 2 — Stabilize | ~20 | 3–5 |
| Phase 3 — Distribution | 8 | 1–2 |
| **Total** | **~41** | **7–12 days** |

> [!TIP]
> Start every session by running `flutter analyze` and fixing any errors before adding features. A clean codebase makes beta bugs much easier to isolate.

> [!IMPORTANT]
> The single highest-risk item is **Firestore Security Rules** (Phase 0). A misconfigured rule could expose one user's collection to another. Verify this before sharing any URL with testers.

> [!NOTE]
> "Minimally Viable" for beta means: a new user can sign up, add at least one coin (by any method), see it in their collection with an image, and add something to their Wish List — without hitting an error they can't recover from.

---

## 🗓️ Suggested Session Order

1. **Session 1** — Phase 0: Bucket permissions + auth flow + Firestore rules
2. **Session 2** — Phase 1A: Image upload (web + mobile)
3. **Session 3** — Phase 1B: Wish List end-to-end
4. **Session 4** — Phase 2: My Collection stability (edit, delete, search, sort)
5. **Session 5** — Phase 2: Add Coins Hub — test all 7 tabs end-to-end
6. **Session 6** — Phase 2: Review Hub + Navigation/Layout audit
7. **Session 7** — Phase 3: Onboarding, web deployment, tester accounts
8. **Session 8 (buffer)** — Bug fixes from internal testing before handing to beta users
