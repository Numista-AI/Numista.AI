# Numista.AI — August Desktop Beta User Testing Script

> **Version:** August 2026 | **Target Duration:** 20–25 Minutes | **Platform:** Windows Desktop / Web Browser

Welcome to the **Numista.AI August Desktop Beta**! This script guides you through testing the 3 primary pipelines of our platform. Please complete each task and log any bugs or feedback using the in-app **Feedback Button** (`admin_feedback_screen.dart`).

---

## Task 1: Spreadsheet Upload & Slang Ingestion (5–7 Minutes)

**Objective:** Test zero-reformatting CSV/Excel ingestion using colloquial collector terminology.

### Steps:
1. Navigate to **Add Coins / Bulk Ingest** in the main menu.
2. Download or use a sample CSV file containing informal shorthand (e.g. `"wheatie"`, `"walker"`, `"ike"`, `"merc"`, `"slick"`, `"DMPL"`).
3. Drag and drop the file into the upload zone and click **Import Collection**.
4. Inspect the **Review Queue** screen.

### Expected Outcome:
- The file imports without throwing column mapping or `KeyError` exceptions.
- Slang terms are mapped into canonical US Mint series (e.g. `"wheatie"` → **Lincoln Wheat Cent**, `"walker"` → **Walking Liberty Half Dollar**) and official Sheldon grades (e.g. `"slick"` → **AG-3**, `"DMPL"` → **Deep Mirror Prooflike**).

---

## Task 2: USB Microscope Focus & Auto-Capture (7–10 Minutes)

**Objective:** Verify live video stability detection, manual focus wheel guidance, and automated snapshot triggers.

### Steps:
1. Ensure the **Numista Hardware Tray Agent** (`numista_hardware`) is running on your Windows desktop.
2. Connect your Jiusion USB microscope (or standard webcam) and open the **Hardware Capture Hub** screen in Numista.AI.
3. Place a coin (e.g., Morgan Silver Dollar or Lincoln Cent) under the lens.
4. Rotate the manual focus wheel until the on-screen sharpness meter peaks.
5. Hold the coin steady for **1.2 seconds**.

### Expected Outcome:
- The Laplacian variance meter displays green clarity indicators when sharp.
- OpenCV motion variance detection triggers auto-capture after 1.2s of stability.
- Dual obverse and reverse images are uploaded and passed to Gemini Vision AI for series and grade estimation.

---

## Task 3: Estate Lot Division & PDF Passport Export (8–10 Minutes)

**Objective:** Partition a multi-coin collection among heirs using the Longest Processing Time (LPT) solver and export a legal Numismatic Passport PDF.

### Steps:
1. Open the **Estate Planning & Division** screen.
2. Input 2 or 3 heir names (e.g., *Heir A*, *Heir B*) with target percentage allocations (e.g. 50% / 50%).
3. Select an heirloom coin and apply a **Beneficiary Lock** to assign it to *Heir A*.
4. Click **Run Estate Lot Division**.
5. Inspect the calculated lot allocations and monetary **Cash Equalization Offsets**.
6. Click **Generate Numismatic Passport PDF** and download the PDF report.

### Expected Outcome:
- The LPT solver distributes unlocked coins to balance total values and calculates net-zero cash offsets.
- The downloaded PDF includes:
  - Yellow top banner: *"BETA EVALUATION DOCUMENT: Generated for software testing purposes only. Does not constitute a certified USPAP appraisal or legal IRS Form 706 valuation."*
  - Semi-transparent diagonal watermark across all pages: *"BETA – FOR EVALUATION ONLY"*.
  - Digital executor signature block and QR code.

---

## Reporting Issues & Feedback

If you encounter any UI layout glitches, misidentified coin series, or connection issues, click the **Feedback / Report Issue** button in the bottom drawer. Select the appropriate category code:
- `CAT-CSV`: Spreadsheet mapping or column errors
- `CAT-HW`: USB microscope / camera stability errors
- `CAT-EST`: Estate lot division or PDF report bugs
- `CAT-AI`: Gemini Vision identification or grading errors
- `CAT-UI`: Visual layout, text overlap, or button issues
