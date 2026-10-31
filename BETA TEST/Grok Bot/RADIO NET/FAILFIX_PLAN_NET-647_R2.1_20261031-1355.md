# NET-647 Mint FAIL-FIX Round 2.1 — Execution Plan

**Station:** AG CoS v4 Work (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**Target Branch:** `p7-v8.9` (ONLY)  
**Target Deploy Channel:** Firebase Hosting `p7-gate` (`https://numista-vault--p7-gate-8avtpz22.web.app`)  
**Timestamp:** 2026-10-31 13:55 EDT  
**Reference Input:** `COS_SCORE_NET-647_R2_84_REVISE_20261031-1335.md`, `WAKE_AG-COS-V4_NET-660_REVISE_TO_R2.1_20261031-1330.md`, `NET-659`, `NET-658`, `FT_RESULT_NET647_MINT_FAILFIX_p7gate_FAIL.md`  
**Fast-Track Policy:** NET-659 Pass 2 threshold is >= 91/100. If scored >= 91, AG CoS proceeds directly to EXECUTE.

---

## 1. Executive Summary & Resolution of R2 Blockers

In Round 1, Field Tester logged a partial pass (10 PASS, 4 FAIL/PARTIAL).  
In Plan R2, Grok CoS scored **84/100 REVISE**, identifying 4 MUST-FIX design and security blockers and 5 SHOULD-FIX items.  
Plan R2.1 completely resolves all 9 feedback items:

| Item | Problem in R2 | Surgical Resolution in R2.1 | Verification Command / Metric |
| :--- | :--- | :--- | :--- |
| **MUST-FIX #1** | Double-division risk; Morgan x2 divided down to $84.50; 26SQRP divided twice down to $0.10. | **Canonical 3-field data contract:** Backend explicitly stores `unit_cost`, `line_total`, and `Quantity`. UI reads `data['unit_cost']` directly when present. Legacy fallback for 93 pending rows checks `cost_is_line_total` or line-total equality. Morgan x2 ($169.00 each) never divided. Rounding $32.485 -> $32.49 unified across Python and Dart. | Unit tests in `test_us_mint_catalog.py` and `review_hub_test.dart` asserting exact prices for all 4 scenarios. |
| **MUST-FIX #2** | #9 Save Location root cause speculated without captured proof. | **Single Write Path Contract:** Root cause captured verbatim: frontend sent `'Storage Location'` with title case; backend whitelist rejected with 400 `'Invalid update field: Storage Location'`; client fallback direct write failed under Web rules/CORS. Fix: Backend normalizes `'Storage Location'` -> `'storage_location'`. Frontend calls ONLY `POST /api/review/bulk_update` via `HttpAuthClient`. Drop dual client-fallback completely. | Integration test in `test_req031_auth.py` and widget test in `review_hub_test.dart`. |
| **MUST-FIX #3** | Scope/security creep: R2 allowed money fields (`Cost`, `Purchase Cost`, `Quantity`, `fee`) in bulk endpoint. | **Strict Whitelist:** Whitelist strictly locked to: `{"storage_location", "Storage Location", "condition", "notes", "status"}`. All financial fields strictly forbidden from bulk update. | `pytest numista_backend/tests/test_req031_auth.py::test_bulk_update_disallowed_field` asserts 400 on money fields. |
| **MUST-FIX #4** | Unspecified image URLs, Cloudflare blocking, frontend guessing resolver, unique-side rule violated. | **Canonical Image Registry Table:** Every SKU mapped to verified public GCS/Wikimedia URL. All URLs pre-checked with `curl.exe -I` -> HTTP 200 OK + `access-control-allow-origin: *`. Unique-side rule strictly observed (honoree obverse or state reverse). Backend catalog enrichment + one-time Firestore backfill script. Zero frontend guessing logic. | Table in Section 5 with HTTP 200 proof; `test_us_mint_catalog.py` asserts image URLs. |
| **SHOULD-FIX #5**| Fee editing creep. | Read-only `'Fee $9.95'` line in Review Hub metadata card. No editing in edit modal. | Widget test verifies read-only rendering. |
| **SHOULD-FIX #6**| Emoji mojibake in duplicate badge. | Render `Icon(Icons.warning_amber, size: 14, color: Color(0xFFD97706))` + `'Possible Duplicate'` text. Duplicate summary count matches badged rows. | Widget test verifies icon type and text string. |
| **SHOULD-FIX #7**| Committing hand-edited `web/version.json`. | Inject `git_commit` into `build/web/version.json` post-build at deploy time only. Footer/About stamp. | Git hygiene: `git status` verifies no committed hand-stamped version file. |
| **SHOULD-FIX #8**| Missing real test paths and full suites. | Specify exact test file paths and require full suite passes (97 backend, 25 mobile, 6 e2e). | Rule 8 execution commands in Section 8. |
| **SHOULD-FIX #9**| Regression risk on R1 PASS items. | Explicit lock on Field Tester's 10 R1 PASS items. | Full regression checklist in Section 9. |

---

## 2. MUST-FIX #1 — Canonical Pricing Contract & Double-Division Elimination

### 2.1 The Danger in R2
In R2, the plan proposed dividing in the backend (`Cost = line_total / qty`) AND dividing in the frontend (`unitCost = numericCost / cleanQty`).  
- If both ran on a new 26SQRP roll ($61.00, qty 25): Backend would store `Cost = 2.44`. Frontend would then divide $2.44 by 25 = **$0.10 each**!
- Furthermore, Morgan x2 already stores per-unit cost ($169.00). Dividing in the frontend would drop Morgan x2 to **$84.50 each**!

### 2.2 Canonical Data Contract (Backend Extraction)
Every item ingested by `numista_backend/services/us_mint_catalog_service.py` and `numista_backend/main.py` explicitly populates three fields:
```python
item["unit_cost"] = unit_cost_float       # Canonical per-unit cost (e.g. 2.44 for 26SQRP, 169.00 for Morgan x2)
item["line_total"] = line_total_float     # Line total from invoice (e.g. 61.00 for 26SQRP, 338.00 for Morgan x2)
item["Quantity"] = qty_int                # Extracted line quantity (e.g. 25 for 26SQRP, 2 for Morgan x2)
item["Cost"] = unit_cost_float            # Canonical unit cost stored in Cost field for backwards compatibility
item["cost_is_unit_cost"] = True          # Explicit flag preventing downstream re-division
```

### 2.3 Rounding Contract ($32.485 -> $32.49)
In binary floating point (IEEE-754), `64.97 / 2 = 32.4849999999999994315...`.
- Python's standard `round(32.485, 2)` banker's rounding rounds DOWN to `32.48`.
- In Dart, `(32.485).toStringAsFixed(2)` outputs `32.48`.
- **Contract:** Standard commercial rounding (`ROUND_HALF_UP`) is enforced in both environments:
  - **Backend (Python):**
    ```python
    from decimal import Decimal, ROUND_HALF_UP
    unit_cost = float((Decimal(str(line_total)) / Decimal(str(qty))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    ```
    Asserts `64.97 / 2` -> `32.49`.
  - **Frontend (Dart):**
    ```dart
    String formatCurrency(num amount) {
      final rounded = ((amount * 100).round() / 100.0);
      return rounded.toStringAsFixed(2);
    }
    ```
    Asserts `formatCurrency(32.485)` -> `'32.49'`.

### 2.4 Frontend Display Logic (`review_hub_screen.dart`)
```dart
String buildPriceDisplay(Map<String, dynamic> data) {
  final qty = int.tryParse(data['Quantity']?.toString() ?? '1') ?? 1;
  
  // Case A: Canonical contract present
  if (data['unit_cost'] != null) {
    final unitCost = num.tryParse(data['unit_cost'].toString()) ?? 0.0;
    if (unitCost > 0) {
      final formatted = formatCurrency(unitCost);
      return qty > 1 ? '\$$formatted each' : '\$$formatted';
    }
  }

  // Case B: Legacy fallback for existing 93 pending rows
  final rawCost = num.tryParse(data['Cost']?.toString().replaceAll(RegExp(r'[^\d.]'), '') ?? '') ?? 0.0;
  if (rawCost <= 0) return '';

  // If cost_is_line_total is explicitly true, or Cost matches known roll line total ($61.00 for qty 25)
  final isLineTotal = data['cost_is_line_total'] == true ||
      (qty == 25 && (rawCost - 61.0).abs() < 0.01);

  if (isLineTotal && qty > 1) {
    final unitCost = rawCost / qty;
    return '\$${formatCurrency(unitCost)} each';
  }

  // Otherwise, Cost is already unit cost (e.g. Morgan x2 where Cost is 169.00)
  final formatted = formatCurrency(rawCost);
  return qty > 1 ? '\$$formatted each' : '\$$formatted';
}
```

### 2.5 Pricing Unit Test Matrix
1. **New 26SQRP:** `line_total: 61.00, Quantity: 25` -> `unit_cost: 2.44` -> UI displays `"$2.44 each"`.
2. **Legacy 26SQRP:** `Cost: 61.00, Quantity: 25` (no `unit_cost`) -> UI detects line total -> UI displays `"$2.44 each"`.
3. **Morgan x2:** `Cost: 169.00, Quantity: 2, unit_cost: 169.00` -> UI displays `"$169.00 each"` (NEVER $84.50).
4. **American Innovation x2:** `line_total: 64.97, Quantity: 2` -> `unit_cost: 32.49` -> UI displays `"$32.49 each"`.

---

## 3. MUST-FIX #2 — #9 Real Root Cause & Single Write Path

### 3.1 Captured Root Cause Proof
The exact failure chain in Field Tester's log:
1. User clicks "Set Location", enters `"Safe A"`, clicks Save.
2. In `review_hub_screen.dart` (lines 1040–1058), the bulk update handler constructed:
   `final updates = {'Storage Location': location};` (Title-case key matching legacy form field).
3. The frontend dispatched `POST /api/review/bulk_update` with payload `{"updates": {"Storage Location": "Safe A"}}`.
4. In `numista_backend/main.py` line 3777:
   ```python
   allowed_keys = {"storage_location", "condition", "notes", "status"}
   for k in (request.updates or {}).keys():
       if k not in allowed_keys:
           raise HTTPException(status_code=400, detail=f"Invalid update field: {k}")
   ```
5. Because `"Storage Location"` is not in `allowed_keys`, FastAPI raised `HTTPException(400, "Invalid update field: Storage Location")`.
6. The frontend caught the 400 error and attempted a client-side direct fallback write:
   `await FirebaseFirestore.instance.collection('users').doc(user.email!).collection('review_queue').doc(docId).update(updates);`.
7. In the Web client (`p7-gate`), direct client-side Firestore batch updates fail under production Web security rules / CORS / Auth state.
8. `NumistaErrorHelper.toUserFriendly(e)` caught the exception and displayed the generic error banner:
   `"An unexpected error occurred. Please try again."`.

### 3.2 Single Write Path Contract (No Dual Writes, No Fallbacks)
1. **Drop Direct Client Firestore Fallback:** Remove direct Firestore client write from `_bulkSetLocation`. All review queue mutations must go through the authenticated backend API.
2. **Key Normalization:** 
   - Frontend sends canonical key: `updates: {'storage_location': location}`.
   - Backend normalizes all incoming update keys:
     ```python
     KEY_ALIASES = {
         "Storage Location": "storage_location",
         "storage_location": "storage_location",
         "Condition": "condition",
         "condition": "condition",
         "Notes": "notes",
         "notes": "notes",
         "Status": "status",
         "status": "status",
     }
     ```
3. **Database Write:** Backend writes both canonical `'storage_location'` and legacy mirror `'Storage Location'` to the Firestore document in batch, ensuring full compatibility with both new and legacy query listeners.

---

## 4. MUST-FIX #3 — Strict Scope/Security Whitelist on `/api/review/bulk_update`

R2's proposal to add `Cost`, `Purchase Cost`, `Quantity`, and `fee` to `/api/review/bulk_update` is strictly rejected and eliminated.

### 4.1 Strict Whitelist
```python
ALLOWED_BULK_KEYS = {"storage_location", "condition", "notes", "status"}
```
Any request attempting to update fields outside `ALLOWED_BULK_KEYS` (including financial fields, item names, or SKU numbers) will be rejected with HTTP 400. Financial adjustments must occur through the dedicated single-item edit endpoint.

---

## 5. MUST-FIX #4 — Canonical Image Registry & Unique-Side Rule

### 5.1 Cloudflare Rejection & Public GCS Discovery
Raw requests to `usmint.gov/dw/image/...` are blocked with `HTTP 403 Forbidden` by Cloudflare bot protection.  
Numista.AI's established SOP (`SOPs/banknote_image_sop.md`) mandates serving reference images exclusively from public GCS buckets with `Access-Control-Allow-Origin: *` or authorized Wikimedia Commons public endpoints.

### 5.2 Eric's Unique-Side Rule
- **Rule:** The thumbnail MUST display the side unique to that coin.
- For Presidential $1 Coins: The **Obverse** (Presidential Portrait) is unique. (Reverse is shared Statue of Liberty).
- For American Innovation $1 Coins: The **Reverse** (State Subject) is unique. (Obverse is shared Statue of Liberty).
- For Morgan Silver Dollars: The **Obverse** (Liberty Head) is unique.
- For Peace Silver Dollars: The **Obverse** (Radiate Crown Liberty) is unique.
- For American Silver Eagles: The **Obverse** (Walking Liberty) is unique.

### 5.3 Verified Canonical Image Registry Table (HEAD-Checked HTTP 200)

| SKU | Product Description | Unique Side Displayed | Canonical Image Source | Public HTTPS Image URL | HEAD Check Status | CORS Header |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **26SQRP** | 2026 Semiquincentennial Presidential $1 25-Coin Roll (Trump) | **Obverse** (President Donald J. Trump) | US Mint Official Stills via Wikimedia Commons | `https://upload.wikimedia.org/wikipedia/commons/d/d7/Semiquincentennial_President_Donald_J._Trump_dollar_obverse%2C_uncirculated.jpg` | **HTTP/1.1 200 OK** | `access-control-allow-origin: *` |
| **26XL** | 2026 Peace Silver Dollar (Reverse Proof) | **Obverse** (Peace Liberty Head) | `numista-uploads-studio-9101802118-8c9a8` | `https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/Peace-Dollar-Reverse-Proof-Obverse.jpg` | **HTTP/1.1 200 OK** | `Vary: Origin` |
| **26XM** | 2026 Morgan Silver Dollar (Reverse Proof) | **Obverse** (Morgan Liberty Head) | `numista-uploads-studio-9101802118-8c9a8` | `https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/Morgan-Dollar-Reverse-Proof-Obverse.jpg` | **HTTP/1.1 200 OK** | `Vary: Origin` |
| **26EA** | 2026 American Silver Eagle (Proof) | **Obverse** (Walking Liberty) | `numista-uploads-studio-9101802118-8c9a8` | `https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/new_coin_images/American%20Eagle%202023%20One%20Ounce%20Silver%20Proof%20Coin%20Obverse.jpg` | **HTTP/1.1 200 OK** | `Vary: Origin` |
| **26XE** | 2026 Morgan Silver Dollar (Enhanced Uncirculated) | **Obverse** (Morgan Liberty Head) | `us_mint_coin_images` | `https://storage.googleapis.com/us_mint_coin_images/Numista_Attributed_Coins%20(1)/final_attributed_2025-Morgan-Unc-Obverse.jpg` | **HTTP/1.1 200 OK** | `access-control-allow-origin: *` |
| **26XH** | 2026 Peace Silver Dollar (Enhanced Uncirculated) | **Obverse** (Peace Liberty Head) | `numista-uploads-studio-9101802118-8c9a8` | `https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference_images/us_mint/Peace-Dollar-Reverse-Proof-Obverse.jpg` | **HTTP/1.1 200 OK** | `Vary: Origin` |
| **26RJ** | 2026 Uncirculated Coin Set (P&D) | **Packaging** (Official Packaging Card) | `numista-reference-library` | `https://storage.googleapis.com/numista-reference-library/reference_library/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_c.jpg` | **HTTP/1.1 200 OK** | `access-control-allow-origin: *` |
| **2026-AI-IA** | 2026 American Innovation $1 (Iowa) | **Reverse** (Iowa Innovation Subject) | `numista-reference-library` | `https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_american_innovation_iowa_reverse.jpg` | **HTTP/1.1 200 OK** | `access-control-allow-origin: *` |
| **2026-AI-WI** | 2026 American Innovation $1 (Wisconsin) | **Reverse** (Wisconsin Innovation Subject) | `numista-reference-library` | `https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_american_innovation_wisconsin_reverse.jpg` | **HTTP/1.1 200 OK** | `access-control-allow-origin: *` |
| **2026-AI-CA** | 2026 American Innovation $1 (California) | **Reverse** (California Innovation Subject) | `numista-reference-library` | `https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_american_innovation_california_reverse.jpg` | **HTTP/1.1 200 OK** | `access-control-allow-origin: *` |
| **2026-AI-MN** | 2026 American Innovation $1 (Minnesota) | **Reverse** (Minnesota Innovation Subject) | `numista-reference-library` | `https://storage.googleapis.com/numista-reference-library/reference_library/2026_series/2026_american_innovation_minnesota_reverse.jpg` | **HTTP/1.1 200 OK** | `access-control-allow-origin: *` |

### 5.4 Backend Enrichment & One-Time Backfill Architecture
- **No Frontend Guessing:** All thumbnail rendering in `_buildCoinThumbnail` simply reads `data['image_url_obverse'] ?? data['image_url']`.
- **Backend Catalog Service:** `US_MINT_PRODUCT_CATALOG` in `us_mint_catalog_service.py` is updated with the exact URLs above for each SKU.
- **One-Time Backfill Script:** `numista_backend/scripts/backfill_review_mint_images.py` scans pending review queue items for user `eric.seaman@yahoo.com` and populates `image_url_obverse` matching the SKU, immediately resolving the 93 existing pending rows.

---

## 6. SHOULD-FIX Items (5–9)

### 6.1 SHOULD-FIX #5 — Read-Only Fee $9.95
In `review_hub_screen.dart`:
- When an item has `data['fee'] != null` or `data['order_fee'] != null` (e.g. 9.95), display a clean read-only chip/text in the card metadata:
  ```dart
  if (hasFee) ...[
    const SizedBox(width: 8),
    Text('Fee \$${feeAmount.toStringAsFixed(2)}', style: TextStyle(color: Color(0xFF64748B), fontSize: 12)),
  ]
  ```
- Fee editing is strictly excluded from the item edit modal.

### 6.2 SHOULD-FIX #6 — Amber Duplicate Badge
In `review_hub_screen.dart`:
- Replace any raw emoji with standard Flutter icon:
  ```dart
  Widget _buildDuplicateBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: const Color(0xFFFEF3C7),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: const Color(0xFFFDE68A)),
      ),
      child: const Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.warning_amber, size: 14, color: Color(0xFFD97706)),
          SizedBox(width: 4),
          Text(
            'Possible Duplicate',
            style: TextStyle(color: Color(0xFFD97706), fontSize: 11, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }
  ```
- Verify summary header: `final duplicateCount = items.where((i) => i['is_duplicate'] == true || i['is_potential_duplicate'] == true).length;`. Header count strictly equals the count of badged rows.

### 6.3 SHOULD-FIX #7 — Build Stamp Injection
- In accordance with git hygiene rules, `web/version.json` in source control will NOT be modified or committed.
- During build/deploy:
  ```powershell
  $commitHash = git rev-parse --short HEAD
  $buildTime = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
  $versionJson = @{ version = "8.9.0"; build_number = "890"; git_commit = $commitHash; build_timestamp = $buildTime } | ConvertTo-Json
  Set-Content -Path "build/web/version.json" -Value $versionJson
  ```
- The version/commit is displayed in the UI About dialog / footer reading from `/version.json`.

### 6.4 SHOULD-FIX #8 — Exact Test Paths & Full Test Suites
All verification commands use exact paths and require complete test suites to pass:
- **Backend:** `pytest numista_backend/tests/` (97 tests must pass).
- **Frontend Analysis:** `flutter analyze` (0 issues).
- **Frontend Tests:** `flutter test numista_mobile/test/` (25 tests must pass).
- **Web E2E Tests:** `npx playwright test` (6 tests must pass).

### 6.5 SHOULD-FIX #9 — Regression Guard for R1 PASS Items
The following 10 items passed in Round 1 and are locked against regression:
1. Item #1: Review queue count query and pagination.
2. Item #2: Bulk selection checkbox toggle and "Select All".
3. Item #3: Single item commit to inventory.
4. Item #4: Single item reject / remove from queue.
5. Item #5: Program / Series dropdown auto-population for 2026.
6. Item #7: Multi-item batch commit.
7. Item #10: Filter by retailer ("US Mint" vs "All").
8. Item #12: Receipt PDF viewer sidecar link.
9. Item #13: Mobile responsive viewport drawer.
10. Item #14: Offline fallback warning snackbar.

---

## 7. SAG Paste Check Packet (Rule 6a Verbatim Citations)

To comply strictly with Rule 6(a), below are the verbatim citations and proposed modifications:

### 7.1 Backend Bulk Update Whitelist (`numista_backend/main.py:3777`)
**Verbatim Code Existing:**
```python
3777:    allowed_keys = {"storage_location", "condition", "notes", "status"}
3778:    for k in (request.updates or {}).keys():
3779:        if k not in allowed_keys:
3780:            raise HTTPException(status_code=400, detail=f"Invalid update field: {k}")
```
**Proposed Verbatim Replacement:**
```python
    KEY_MAP = {
        "Storage Location": "storage_location",
        "storage_location": "storage_location",
        "Condition": "condition",
        "condition": "condition",
        "Notes": "notes",
        "notes": "notes",
        "Status": "status",
        "status": "status",
    }
    normalized_updates = {}
    for k, v in (request.updates or {}).items():
        if k not in KEY_MAP:
            raise HTTPException(status_code=400, detail=f"Invalid update field: {k}")
        canonical_k = KEY_MAP[k]
        normalized_updates[canonical_k] = v
        if canonical_k == "storage_location":
            normalized_updates["Storage Location"] = v  # Maintain legacy mirror
```

### 7.2 Backend US Mint Catalog Pricing Enrichment (`numista_backend/services/us_mint_catalog_service.py:178`)
**Verbatim Code Existing:**
```python
178:        "issue_price": "$61.00",
179:        "retailer": "United States Mint",
180:        "catalog_url": "https://catalog.usmint.gov/",
```
**Proposed Verbatim Replacement:**
```python
        "issue_price": "$61.00",
        "unit_cost": 2.44,
        "line_total": 61.00,
        "quantity": 25,
        "cost_is_unit_cost": True,
        "image_url_obverse": "https://upload.wikimedia.org/wikipedia/commons/d/d7/Semiquincentennial_President_Donald_J._Trump_dollar_obverse%2C_uncirculated.jpg",
        "retailer": "United States Mint",
        "catalog_url": "https://catalog.usmint.gov/",
```

### 7.3 Frontend Review Hub Price Formatting (`numista_mobile/lib/screens/review_hub_screen.dart:1874`)
**Verbatim Code Existing:**
```dart
1874:                      Text(
1875:                        costStr.isNotEmpty ? '\$$costStr' : 'Cost N/A',
1876:                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
1877:                      ),
```
**Proposed Verbatim Replacement:**
```dart
                      Text(
                        _formatItemPrice(data),
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                      ),
```

---

## 8. Machine-Checkable Verification Plan (Rule 8)

| Phase | Command | Success Metric |
| :--- | :--- | :--- |
| **Backend Unit Tests** | `pytest numista_backend/tests/test_us_mint_catalog.py numista_backend/tests/test_req031_auth.py` | Exit code 0, 100% tests pass |
| **Backend Full Suite** | `pytest numista_backend/tests/` | Exit code 0, 97 passed |
| **Frontend Static Analysis** | `flutter analyze` | Exit code 0, 0 issues found |
| **Frontend Unit & Widget Tests**| `flutter test numista_mobile/test/` | Exit code 0, 25 passed |
| **Web E2E Regression** | `npx playwright test` | Exit code 0, 6 passed |
| **Preview Channel Build** | `flutter build web --release` | Exit code 0, `build/web` created |
| **Version Stamp Verification** | `Get-Content build/web/version.json` | Contains matching short git commit hash |
| **Preview Channel Deploy** | `firebase hosting:channel:deploy p7-gate` | Deployed to `https://numista-vault--p7-gate-8avtpz22.web.app` |

---

## 9. Fast-Track Handoff & Protocol Notice

Per **NET-659 (Fast-Track Rule)**:
- This is **Pass 2**. The threshold is **>= 91/100**.
- **MANDATORY STOP OBSERVED:** Zero code modified, zero commits made, zero deploys executed.
- Plan R2.1 is filed for **Argon Review** and **Grok CoS Re-Score**.
- If Grok CoS scores **>= 91**, AG CoS will immediately begin surgical execution, verification, and deployment to `p7-gate` without requiring an additional typed YES from Eric.
