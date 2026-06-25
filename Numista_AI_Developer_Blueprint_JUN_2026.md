# Numista.AI — Developer Blueprint
> **Version:** June 2026 | **Author:** Numista Development Team | **Status:** Reference Document for Standalone AI Advisor

This document outlines the codebase conventions, directory structures, architectural patterns, and development guidelines for the Numista.AI application. It is designed to be uploaded directly into standalone AI advisors to ensure code changes conform to the project's standards.

---

## 1. Codebase Structure

The codebase is organized into four primary component directories:

```
Numista.AI/
├── numista_mobile/        # Google Flutter Frontend (Web, iOS, Android)
├── numista_backend/       # Python FastAPI Backend (Cloud Run)
├── numista_hardware/      # Windows Microscope Capture Agent (Python/Flask)
└── numista_tests/         # End-to-End Test Suite (Playwright/Node)
```

### 1.1 Development & Run Environment
- **Local Dev Server**: `http://localhost:8080` (FastAPI backend port 8080)
- **Local Microscope Agent**: `http://localhost:5000` (Flask port 5000)
- **GCP Target Project**: `studio-9101802118-8c9a8` (AJ's AI Coin App)

---

## 2. Core Developer Rules & Protocol

### 2.1 Rule 0 — Version Verification Protocol
Never assume package version numbers or deprecation schedules from training memory.
Before adding any packages to `requirements.txt`, `pubspec.yaml`, or `package.json`:
1. Check the deprecation guidelines located in the local directory: `Gemini Deprecation Schedules/`
2. Validate the active version availability by executing:
   - `pip index versions <package_name>` (Python)
   - `npm view <package_name> version` (Node)
   - `dart pub outdated` (Flutter)

### 2.2 Version Constraints (As of June 2026)
- **Backend Runtime**: Python `3.11-slim` base image.
- **Backend AI SDK**: `google-genai==1.71.0` (Unified SDK; legacy `vertexai` or `google-generativeai` are retired).
- **Flutter SDK**: `^3.11.3`
- **Flutter Firebase AI SDK**: `firebase_ai: ^3.10.0`

### 2.3 Standalone Session Rules
- **No Global Packages**: Never run raw `pip install`. Execute commands inside the virtual environment `numista_backend\.venv\Scripts\python.exe -m pip install`.
- **Exclusion Rules**: Ensure local secrets, virtual environment directories, temporary download directories, `.env` files, and binaries are listed in `.gitignore` and `.gcloudignore`.

---

## 3. Flutter App Architecture (`numista_mobile`)

The frontend utilizes Flutter for responsive layouts, serving web and mobile builds from a single code base.

### 3.1 Main Entry & Auth Gate (`lib/main.dart`)
Initializes Firebase and establishes the Authentication Gate using `StreamBuilder<User?>` on `FirebaseAuth.instance.authStateChanges()`.
- **Signed Out**: Routes the user to `LoginScreen`.
- **Signed In**: Restores the session and loads `BaseLayout`.

### 3.2 Key Screens Catalog
- `LoginScreen` (`lib/screens/login_screen.dart`): Handles authentication with visual stats strips and a "PIN Auth Hint" to simplify user onboarding.
- `BaseLayout` (`lib/screens/base_layout.dart`): Sidebar-driven navigation layout wrapping responsive view screens.
- `HomeDashboard` (`lib/screens/home_dashboard.dart`): Displays portfolio metrics, latest version notes, and interactive Suggestion Chips that trigger pre-configured prompts inside `AIChatScreen`.
- `MyCollectionScreen` (`lib/screens/my_collection_screen.dart`): A premium horizontal scrollable collection grid rendering comprehensive coin metadata. Includes a slide-out drawer indicating metal value badges.
- `AddCoinsHub` (`lib/screens/add_coins_hub.dart`): Tab-based input coordinator (Manual Form, AI Photo ID, PCGS Cert lookup, Spreadsheet ingestion).
- `WishlistScreen` (`lib/screens/wishlist_screen.dart`): Tracks wanted specimens, resolving affiliate product matches via eBay Partner Network (EPN).
- `SuppliesScreen` (`lib/screens/supplies_screen.dart`): Inventory grid showing folders, binders, albums, and capsules logged under `supplies_log`.
- `HeirDivisionScreen` (`lib/screens/heir_division_screen.dart`): UI for defining heirs and executing division simulations.

### 3.3 Core Services
- `auth_service.dart`: Exposes `userEmail` and dynamically constructs Firestore collection paths.
- `wishlist_service.dart`: Handles wishlist additions and triggers ownership detections when a coin is added.
- `epn_service.dart`: Dynamically structures eBay Partner Network affiliate tracking URLs.
- `photo_sharing_service.dart`: Syncs user photo sharing preferences to local storage and Firestore.

---

## 4. FastAPI Backend Architecture (`numista_backend`)

The Python backend is deployed to Cloud Run as `numista-backend` in `us-central1`.

### 4.1 Production Core API (`numista_backend/main.py`)
FastAPI serves endpoints routing to specialized modules:
- `/api/import_spreadsheet`: Handles CSV/Excel processing.
- `/api/process_invoice`: Ingests PDFs, extracts table lines via Gemini, and routes items.
- `/api/identify_coin_photo`: Endpoint supporting double-pass Gemini Vision verification for manual image uploads.
- `/api/pcgs/cert/{cert_no}`: A Cloud Run proxy endpoint to bypass CORS and scraper restrictions when fetching cert facts.
- `/api/review/break_up_set`: Endpoint to deconstruct a coin set in the staging review queue into individual child records sharing a `set_id`.
- `/api/review/keep_set_as_is`: Ingests set records as unified coin models into the collection.

### 4.2 Support Scripts (`numista_backend/_scripts/`)
- `build_image_index.py`: Builds and merges the reference image index based on files stored in GCS.
- `promote_user_photos.py`: Promotes high-quality user-uploaded photos to the global reference library.

---

## 5. Microscope Desktop Agent (`numista_hardware`)

A local Python Flask daemon communicating with Firestore via a Command Bus architecture to trigger USB microscope captures.

### 5.1 Command Bus Architecture
To bypass browser secure sandboxing (preventing direct HTTP calls from `https://numista.ai` to `http://localhost:5000`), commands are serialized in Firestore:

```
Flutter Client (App) -> writes "start_scan" to Firestore: `commands/{email}/pending/{docId}`
                                        │
                                        ▼
Local Desktop Agent -> listens via real-time stream `on_snapshot()`
                                        │
                                        ▼
                Agent deletes pending doc -> runs CV2 camera thread
                                        │
                                        ▼
Local Desktop Agent -> uploads photos to GCS -> writes coin data to Firestore
                                        │
                                        ▼
Flutter Client (App) -> reads confirmation from: `commands/{email}/results/{coinId}`
```

### 5.2 Local Flask Routing (`auto_capture.py`)
- `/pair` (POST): Dynamically updates the desktop agent's active user email.
- `/start-scan` (POST): Spawns the capture thread.
- `/get-status` (GET): Renders current sharpness variance, motion thresholds, and active countdown timer status.

---

## 6. Coin Image Operating Procedure

Numista.AI utilizes a prioritized three-layer reference image configuration:

| Layer | Type | Target Path |
|---|---|---|
| **Layer 1** | Personal Photos | `gs://studio-9101802118-8c9a8.firebasestorage.app/users/{email}/coins/{coin_id}/` |
| **Layer 2** | Reference Library Index | `coin_image_index` Firestore catalog routing to public GCS paths |
| **Layer 3** | AI Generated Fallback | `gs://numista-reference-library/reference_library/ai_generated/` (Imagen Fallbacks) |

### 6.1 Naming Convention Rules
Reference images must conform to the following formatting structure:
`{year}[_{mint}][_{subject}]_{program-slug}_{side}.{ext}`
- Keep all letters lowercase (except Mint marks: `P`, `D`, `S`, `W`, `CC`, `O` which are uppercase).
- Use underscores to separate fields; use hyphens to separate words within fields.
- Examples:
  - `1921_morgan-dollar_obverse.jpg`
  - `1999_P_50-state-quarters_delaware_reverse.jpg`
  - `2022_american-women-quarters_maya-angelou_obverse.jpg`

### 6.2 User Photo Contribution Consent Flow
1. When a user uploads a personal coin image via `my_collection_screen.dart`, the system runs a quality score check (resolution $\ge$ 800px, sharpness, glare, contrast).
2. On the first eligible upload, the app triggers a one-time consent popup.
3. If opted in, the preference is written to `users/{email}/settings/photo_sharing` (`opted_in: true`) and the coin document field `contribute_to_library` is set to `true`.
4. The backend promotion script `promote_user_photos.py` runs on a schedule, copying approved images to the public reference bucket, tagging them `source_tier: 1`, and setting `contribute_to_library = "PROMOTED"` on the source coin document.

---

## 7. Firestore Security Rules Spec
Security rules restrict data visibility to the authenticated owner. Below is the configuration deployed:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // User-isolated collection rules
    match /users/{email}/{document=**} {
      allow read, write: if request.auth != null && request.auth.token.email == email;
    }
    
    // Commands bus access
    match /commands/{email}/{document=**} {
      allow read, write: if request.auth != null && request.auth.token.email == email;
    }

    // Global reference materials (read-only for authenticated users)
    match /global_programs/{programId} {
      allow read: if request.auth != null;
      allow write: if false;
    }
    match /coin_set_index/{setId} {
      allow read: if request.auth != null;
      allow write: if false;
    }
  }
}
```
