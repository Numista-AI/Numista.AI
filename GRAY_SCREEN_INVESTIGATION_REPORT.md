# Comprehensive Investigation Report: 'Solid Gray Screen' Issue on `numista.ai`

**Document Purpose**: This document provides an exhaustive, step-by-step record of all technical investigations, root cause analyses, code edits, git commits, deployment details, and open hypotheses regarding the **"Solid Gray Screen"** issue on the **My Collection (Coins)** screen of [https://numista.ai](https://numista.ai). It is specifically structured so that another AI agent or software engineer can immediately take over and resolve the issue.

---

## 1. Problem Description & Visual Evidence

* **URL**: `https://numista.ai`
* **Target Screen**: `My Collection` (`my_collection_screen.dart`), tab: **Coins**
* **User Context**: Logged-in user (e.g. `eric.seaman@yahoo.com`), tested in Chrome Incognito mode after pressing `Ctrl + Shift + R` (hard refresh).
* **Symptom**:
  * The left navigation sidebar renders correctly.
  * The top header ("My Collection") and the gold "BETA TESTING" banner render correctly.
  * **Below the gold banner**, the entire main content area (where the coin collection table/grid should appear) renders as a **solid, uniform gray rectangle** (`#9E9E9E` / `#E2E2DF`).
* **Flutter Technical Context**:
  * In **Flutter Web release mode** (production builds), Flutter's default `ErrorWidget.builder` catches unhandled widget `build()` or `layout()` exceptions and renders a **solid grey box with zero text** instead of the red debug error box.

---

## 2. Chronological Log of All Attempted Fixes & Commits

Below is every modification made to the codebase in an attempt to address this issue:

### Attempt 1: Restoring Missing Syntax & Try-Catch Block
* **Commit**: `338da11` — `fix(build): restore missing try { block in my_collection_screen — orphaned catch was causing Dart syntax error`
* **Commit**: `3f0c54a` — `fix(web): resolve closing bracket syntax in my_collection_screen`
* **File**: `numista_mobile/lib/screens/my_collection_screen.dart`
* **Action**: Discovered an orphaned `catch (e, stack)` block inside `cellBuilder` of `TableView.builder`. Added back the missing `try {` block around cell rendering to catch individual cell formatting errors.

### Attempt 2: Removing Nested Dual Scrollbars
* **Commit**: `093f35b` — `fix(estate-v3): harden state machine, morgan context, pdf clean schema, and web scrollbar`
* **File**: `numista_mobile/lib/screens/my_collection_screen.dart`
* **Action**: Removed a top-oriented `RawScrollbar` that was nested inside another bottom-oriented `RawScrollbar` around `TableView.builder`.

### Attempt 3: Complete Removal of 1D `RawScrollbar` Around 2D `TableView`
* **Commit**: `809af8c` — `fix(collection): remove incompatible RawScrollbar wrapper around TableView.builder resolving solid gray screen crash on web`
* **File**: `numista_mobile/lib/screens/my_collection_screen.dart`
* **Action**:
  * **Analysis**: `my_collection_screen.dart` was wrapping `TableView.builder` (from the `two_dimensional_scrollables` package) inside a standard 1D `RawScrollbar(controller: _tvHorizCtrl)`.
  * **Why it fails**: In Flutter 3.22+ Web, `TableView.builder` attaches a 2D `TwoDimensionalScrollPosition` to `_tvHorizCtrl`. Standard 1D `RawScrollbar` expects a 1D `ScrollPosition`. When `RawScrollbar` tries to register a listener on `controller.position`, Flutter throws a `TypeError: TwoDimensionalScrollPosition is not a subtype of ScrollPosition` during widget layout.
  * **Code Edit**: Stripped out `RawScrollbar` entirely from lines 1936-1945 in `_buildDataTable`, allowing `TableView.builder` to manage its own horizontal and vertical details natively.

---

## 3. Why the Last Push Did Not Fix `numista.ai` (Deployment Reality)

If the solid gray screen persists on `https://numista.ai` after hard-refreshing (`Ctrl + Shift + R`), there are two primary categories of reasons:

### Reason A: Branch Isolation & Merge Requirement (Most Likely)
* **Git Workflow Rules**: Per project safety rules (`.agents/AGENTS.md` Rule 7), AI agents commit and push **exclusively to the `dev` branch** (`origin/dev`).
* **Live Site Source**: `https://numista.ai` is deployed from the **`main` branch** via Firebase Hosting / GitHub Actions (`Deploy to numista.ai`).
* **Status**: Commits `809af8c` and `af38b89` live on `dev`. **They have NOT yet been merged into `main` via a Pull Request.** Therefore, `numista.ai` is still running the OLD web build from before the fix.

### Reason B: An Unhandled Runtime Exception Beyond `RawScrollbar`
If the code IS deployed to `main` and still displays a gray screen, another unhandled exception is occurring during widget initialization or rendering.

---

## 4. Technical Architecture of `my_collection_screen.dart`

To help the next AI or developer trace the code, here is the execution chain when `My Collection` -> `Coins` renders:

```
my_collection_screen.dart
  └─ build(BuildContext context)
      └─ _buildTabContent(email)  [Line 651]
          └─ StreamBuilder<QuerySnapshot>(_coinsStream)  [Line 654]
              └─ FutureBuilder<bool>(ValuationModeService.isAdvancedMode())  [Line 676]
                  └─ _buildCoinsTab(docs, allDocs, advanced)  [Line 695]
                      └─ SizedBox(height: 520, child: _isCardView ? _buildCardGrid(...) : _buildDataTable(...))  [Line 770]
                          └─ _buildDataTable(docs, advanced)  [Line 1913]
                              └─ TableView.builder(...)  [Line 1933]
```

---

## 5. Remaining Hypotheses & Checklist for the Next AI / Developer

If the gray screen persists after merging `dev` into `main`, investigate these 5 potential root causes:

### Hypothesis 1: `TableView.builder` 2D Layout Constraint Failure on Web
* **Location**: `my_collection_screen.dart` line 770:
  ```dart
  SizedBox(
    height: 520,
    child: _isCardView 
        ? _buildCardGrid(docs, advanced: advanced)
        : _buildDataTable(docs, advanced: advanced),
  )
  ```
* **Issue**: On certain screen widths or CanvasKit web renderers, `TableView.builder` inside a fixed `SizedBox(height: 520)` might fail layout constraints if column widths exceed viewport or if `package:two_dimensional_scrollables` (v0.4.2 vs v0.5.3) encounters a web canvas calculation error.
* **Test**: Temporarily switch default `bool _isCardView = true;` (line 107). If Card View renders without a gray box, the bug is 100% inside `TableView.builder`.

### Hypothesis 2: Firestore Document Schema / Field Type Exception
* **Location**: `_filtered(docs)` [line 490] and `_sortKey(field, m)` [line 354]
* **Issue**: If `eric.seaman@yahoo.com` has a coin document in Firestore where a field (e.g. `parent_set_id`, `cpgRetail`, `transferStatus`, `year`) is stored as an unexpected data type (e.g. integer or list instead of string/num), lines like:
  ```dart
  final parentSetId = m['parent_set_id']?.toString() ?? '';
  final cpg = (m['cpgRetail'] as num?)?.toDouble() ?? 0.0;
  ```
  or sorting `_sortKey` comparing `Comparable` types could throw a runtime `TypeError`.
* **Test**: Wrap the contents of `_buildCoinsTab` or `_buildDataTable` in a top-level `try/catch` widget that returns a fallback `Text('Error loading collection: $e')`.

### Hypothesis 3: `ValuationModeService.isAdvancedMode()` Incognito Restriction
* **Location**: `my_collection_screen.dart` line 676:
  ```dart
  FutureBuilder<bool>(
    future: ValuationModeService.isAdvancedMode(),
    builder: (context, modeSnap) { ... }
  )
  ```
* **Issue**: `ValuationModeService.isAdvancedMode()` accesses `SharedPreferences`. In Chrome Incognito mode with third-party cookie/storage blocking enabled, accessing local storage or async preference getters can throw a DOMException / SecurityError on web.
* **Test**: Check if `modeSnap.hasError` is handled in `FutureBuilder`. Currently, line 679 does `final advanced = modeSnap.data ?? false;` without checking `modeSnap.hasError`.

### Hypothesis 4: Missing Custom `ErrorWidget.builder` in `main.dart`
* **Location**: `numista_mobile/lib/main.dart`
* **Issue**: Flutter Web release builds default to showing a solid grey box when any widget throws an exception.
* **Recommendation**: Add a custom global `ErrorWidget.builder` in `main.dart`:
  ```dart
  void main() {
    ErrorWidget.builder = (FlutterErrorDetails details) {
      return Material(
        color: const Color(0xFF1E2937),
        child: Center(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              'UI Error: ${details.exception}',
              style: const TextStyle(color: Colors.redAccent, fontSize: 13),
            ),
          ),
        ),
      );
    };
    runApp(const MyApp());
  }
  ```
  *This will immediately reveal the exact text of any runtime exception on `numista.ai` instead of displaying a solid gray box!*

### Hypothesis 5: `AuthService.coinsPath` Auth Identity Mismatch
* **Location**: `auth_service.dart` line 42:
  ```dart
  static String get coinsPath {
    final user = _auth.currentUser;
    if (user == null) return 'users/unknown/coins';
    if (user.isAnonymous) return 'users/${user.uid}/coins';
    final identifier = user.email != null ? user.email!.trim().toLowerCase() : user.uid;
    return 'users/$identifier/coins';
  }
  ```
* **Issue**: If `_auth.currentUser` is in an intermediate loading state when `MyCollectionScreen` initializes `_coinsStream = _buildCoinsStream()`, `_coinsStream` will listen to `users/unknown/coins` instead of `users/eric.seaman@yahoo.com/coins`.

---

## 6. Recommended Action Plan for the Next AI / Developer

1. **Verify Deployment First**:
   * Check if PR from `dev` to `main` has been created and merged.
   * Verify GitHub Action `Deploy to numista.ai` finished successfully.
2. **Add Custom `ErrorWidget.builder`**:
   * Add the custom `ErrorWidget.builder` in `main.dart` so any production layout crash displays the actual exception message on screen instead of a gray box.
3. **Set Default View to Cards as Fallback**:
   * Set `bool _isCardView = true;` or add a fallback toggle if `TableView.builder` encounters CanvasKit 2D rendering issues.
4. **Test Incognito SharedPreferences**:
   * Wrap `ValuationModeService.isAdvancedMode()` in a try/catch guard against Incognito storage access exceptions.
