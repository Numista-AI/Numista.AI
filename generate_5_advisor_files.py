"""
generate_5_advisor_files.py
Creates all 5 recommended production & testing files for Numista.AI:
1. slang_dictionary.json
2. estate_logic_rules.md
3. /numista_tests/fixtures/ingestion/ (Sample Ingestion Corpus CSVs)
4. microscope_config.json
5. beta_feedback_rubric.md
"""
import json
import pathlib

ROOT = pathlib.Path(r"C:\Users\ericd\Documents\MyVertexProject")
ADVISOR_DIR = ROOT / "Gemini Advisor Documents"
ADVISOR_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# 1. slang_dictionary.json
# ---------------------------------------------------------
slang_data = {
    "version": "1.0-AUG2026",
    "description": "Numismatic terminology and colloquial slang mapping dictionary for Numista.AI ingestion pipeline",
    "denomination_slang": {
        "wheatie": {"denomination": "1 Cent", "series": "Lincoln Wheat Cent", "canonical_country": "United States"},
        "wheat penny": {"denomination": "1 Cent", "series": "Lincoln Wheat Cent", "canonical_country": "United States"},
        "steelie": {"denomination": "1 Cent", "series": "Lincoln Steel Cent", "year": 1943, "canonical_country": "United States"},
        "indian head": {"denomination": "1 Cent", "series": "Indian Head Cent", "canonical_country": "United States"},
        "v nickel": {"denomination": "5 Cents", "series": "Liberty Head Nickel", "canonical_country": "United States"},
        "buffalo": {"denomination": "5 Cents", "series": "Buffalo Nickel", "canonical_country": "United States"},
        "walker": {"denomination": "50 Cents", "series": "Walking Liberty Half Dollar", "canonical_country": "United States"},
        "walking liberty": {"denomination": "50 Cents", "series": "Walking Liberty Half Dollar", "canonical_country": "United States"},
        "franklin": {"denomination": "50 Cents", "series": "Franklin Half Dollar", "canonical_country": "United States"},
        "morgan": {"denomination": "$1", "series": "Morgan Dollar", "canonical_country": "United States"},
        "peace": {"denomination": "$1", "series": "Peace Dollar", "canonical_country": "United States"},
        "ike": {"denomination": "$1", "series": "Eisenhower Dollar", "canonical_country": "United States"},
        "standing liberty": {"denomination": "25 Cents", "series": "Standing Liberty Quarter", "canonical_country": "United States"},
        "barber dime": {"denomination": "10 Cents", "series": "Barber Dime", "canonical_country": "United States"},
        "barber quarter": {"denomination": "25 Cents", "series": "Barber Quarter", "canonical_country": "United States"},
        "barber half": {"denomination": "50 Cents", "series": "Barber Half Dollar", "canonical_country": "United States"},
        "mercury": {"denomination": "10 Cents", "series": "Mercury Dime", "canonical_country": "United States"},
        "merc": {"denomination": "10 Cents", "series": "Mercury Dime", "canonical_country": "United States"},
        "saint": {"denomination": "$20", "series": "Saint-Gaudens Double Eagle", "canonical_country": "United States"},
        "st gaudens": {"denomination": "$20", "series": "Saint-Gaudens Double Eagle", "canonical_country": "United States"},
        "double eagle": {"denomination": "$20", "series": "Double Eagle", "canonical_country": "United States"},
        "half eagle": {"denomination": "$5", "series": "Half Eagle", "canonical_country": "United States"},
        "quarter eagle": {"denomination": "$2.50", "series": "Quarter Eagle", "canonical_country": "United States"},
        "ase": {"denomination": "$1", "series": "American Silver Eagle", "canonical_country": "United States"},
        "age": {"denomination": "$50", "series": "American Gold Eagle", "canonical_country": "United States"}
    },
    "grade_slang": {
        "bu": "MS-63",
        "bup": "MS-63",
        "gem bu": "MS-65",
        "choice bu": "MS-64",
        "raw bu": "MS-63",
        "prooflike": "MS-63 Prooflike",
        "pl": "MS-63 Prooflike",
        "dmpl": "MS-65 Deep Mirror Prooflike",
        "shiny": "Uncirculated",
        "bright": "Uncirculated",
        "slick": "About Good-3",
        "smooth": "Good-4",
        "heavily worn": "About Good-3",
        "details": "Problem Coin / Details",
        "cleaned": "Details - Cleaned",
        "scratched": "Details - Scratched",
        "damaged": "Details - Damaged"
    },
    "container_slang": {
        "roll": {"container": "Roll/Tube", "default_quantities": {"1 Cent": 50, "5 Cents": 40, "10 Cents": 50, "25 Cents": 40, "50 Cents": 20, "$1": 20}},
        "tube": {"container": "Roll/Tube", "default_quantities": {"1 Cent": 50, "5 Cents": 40, "10 Cents": 50, "25 Cents": 40, "50 Cents": 20, "$1": 20}},
        "monster box": {"container": "Monster Box", "default_quantities": {"$1": 500}},
        "cull": {"note": "Junk Silver / Melt Category"},
        "junk silver": {"note": "90% Silver Melt Category"}
    }
}

# Write slang_dictionary.json
backend_data = ROOT / "numista_backend" / "data"
backend_data.mkdir(parents=True, exist_ok=True)

with open(backend_data / "slang_dictionary.json", "w", encoding="utf-8") as f:
    json.dump(slang_data, f, indent=2)

with open(ADVISOR_DIR / "slang_dictionary.json", "w", encoding="utf-8") as f:
    json.dump(slang_data, f, indent=2)

print("Saved 1/5: slang_dictionary.json")

# ---------------------------------------------------------
# 2. estate_logic_rules.md
# ---------------------------------------------------------
estate_md = """# Numista.AI — Estate Planning & Lot Division Logic Specification

> **Version:** August 2026 | **Author:** Numista Estate & Legal Engineering | **Status:** Active Production Specification

---

## 1. Overview

The Numista.AI Estate Division Engine (`estate_planning_screen.dart` & `attorney_portal_screen.dart`) enables collectors, executors, and estate attorneys to partition numismatic inventories among $N$ heirs with mathematical precision, transparent audit trails, and legal accountability.

---

## 2. Partitioning Algorithm: Longest Processing Time (LPT) Greedy Solver

The lot division engine utilizes a modified **Longest Processing Time (LPT)** greedy bin-packing solver:

1. **Valuation Matrix Assembly**:
   - Total inventory value $V_{total} = \sum v(c_i)$ for all un-locked coins.
   - Target lot value per heir $k$: $T_k = V_{total} \times P_k$, where $P_k$ is the target percentage allocation (e.g., Heir A = 50%, Heir B = 50%).

2. **Sorting & Allocation Loop**:
   - Sort all un-locked items in descending order of calculated market value: $v(c_1) \ge v(c_2) \ge \dots \ge v(c_m)$.
   - For each coin $c_i$, assign it to the heir whose current accumulated lot value is furthest below their target $T_k$.

3. **Lock Pre-Assignment Precedence**:
   - Coins marked with `heir_lock: "Heir Name"` are pre-allocated to that beneficiary *before* the LPT algorithm executes.
   - Pre-allocated item values count toward that beneficiary's accumulated lot total before distributing remaining un-locked items.

---

## 3. Cash Offset Compensation Logic

When physical coin values cannot be divided evenly to exact dollar amounts, the engine calculates monetary cash equalization offsets:

$$\text{Cash Offset}_k = \text{Target Value}_k - \text{Allocated Coin Value}_k$$

- **Positive Offset**: Beneficiary received less physical coin value than their target split; they receive a cash payout from the estate.
- **Negative Offset**: Beneficiary received higher-value physical coins than their target split; they owe a cash balancing payment into the estate pool.
- Net cash sum across all heirs equals zero: $\sum \text{Cash Offset}_k = 0$.

---

## 4. Valuation Floor Hierarchy Defaults

For tax assessment, probate accounting, and estate distributions, the engine supports 4 configurable valuation tiers:

1. **Greysheet CPG Wholesale (Default for Estate Partition)**: Standard dealer buy/wholesale valuation baseline.
2. **Greysheet Retail**: Fair market retail valuation baseline for estate sale planning.
3. **Precious Metal Melt Floor**: Liquidation floor based on live spot metal prices (Gold, Silver, Platinum).
4. **Tax Cost Basis (Stepped-Up Basis)**: Historical purchase cost or date-of-death valuation basis for IRS Form 706 reporting.

---

## 5. Numismatic Passport Export Specification

The ReportLab engine (`passport_pdf_generator.py`) serializes the approved division into a legal-grade PDF containing:
- Certificate of Executor Verification & Timestamp
- Detailed Heir Distribution Schedules with High-Res Image Proofs
- Cash Equalization Summary Table
- Attorney Read-Only Portal Audit Signature Block
"""

with open(ROOT / "estate_logic_rules.md", "w", encoding="utf-8") as f:
    f.write(estate_md)
with open(ADVISOR_DIR / "estate_logic_rules.md", "w", encoding="utf-8") as f:
    f.write(estate_md)

print("Saved 2/5: estate_logic_rules.md")

# ---------------------------------------------------------
# 3. CSV & Invoice Test Corpus (/numista_tests/fixtures/ingestion/)
# ---------------------------------------------------------
fixtures_dir = ROOT / "numista_tests" / "fixtures" / "ingestion"
fixtures_dir.mkdir(parents=True, exist_ok=True)

sample_csv = """Title,Year,Mint Mark,Denomination,Cost,My Notes,Cert #
1921 Morgan Silver Dollar,1921,S,$1,$32.50,Wheatie included in deal,12345678
1937-D Buffalo Nickel,1937,D,5 Cents,$15.00,3 legged variety check,
1955 Doubled Die Cent,1955,,1 Cent,$1200.00,Gem BU raw,
1896 $1 Silver Certificate,1896,,$1,$450.00,Educational Series VF,
2023-W American Gold Eagle,2023,W,$50,$2150.00,Proof 70 Deep Cameo,98765432
"""

with open(fixtures_dir / "messy_collection_import.csv", "w", encoding="utf-8") as f:
    f.write(sample_csv)
with open(ADVISOR_DIR / "sample_messy_ingestion_corpus.csv", "w", encoding="utf-8") as f:
    f.write(sample_csv)

print("Saved 3/5: sample_messy_ingestion_corpus.csv")

# ---------------------------------------------------------
# 4. microscope_config.json
# ---------------------------------------------------------
microscope_config = {
    "device_name": "Jiusion USB Microscope (1000x HD)",
    "version": "1.0-AUG2026",
    "camera_index": 0,
    "native_resolution": {"width": 1920, "height": 1080},
    "fallback_resolution": {"width": 1280, "height": 720},
    "local_server": {
        "host": "localhost",
        "port": 8443,
        "protocol": "https",
        "cert_file": "localhost.crt",
        "key_file": "localhost.key"
    },
    "auto_capture_engine": {
        "stability_delay_seconds": 1.2,
        "motion_diff_threshold": 0.02,
        "laplacian_variance_thresholds": {
            "silver_eagle_luster": 120.0,
            "gold_proof": 150.0,
            "copper_cent_toned": 85.0,
            "clad_quarter": 100.0,
            "minimum_sharpness_cutoff": 60.0
        },
        "bounding_box_padding_pct": 5.0,
        "output_format": "PNG",
        "jpeg_quality": 95
    },
    "gcs_sync": {
        "target_bucket": "studio-9101802118-8c9a8-uploads",
        "staging_collection": "staging_area"
    }
}

hardware_dir = ROOT / "numista_hardware"
hardware_dir.mkdir(parents=True, exist_ok=True)

with open(hardware_dir / "agent_config.json", "w", encoding="utf-8") as f:
    json.dump(microscope_config, f, indent=2)
with open(ADVISOR_DIR / "microscope_config.json", "w", encoding="utf-8") as f:
    json.dump(microscope_config, f, indent=2)

print("Saved 4/5: microscope_config.json")

# ---------------------------------------------------------
# 5. beta_feedback_rubric.md
# ---------------------------------------------------------
beta_rubric_md = """# Numista.AI — August Desktop Beta & November Launch Feedback Rubric

> **Version:** August 2026 | **Author:** Numista QA & Product Management | **Status:** Active Beta Triage Rubric

---

## 1. Issue Categorization Matrix

All feedback submitted via `admin_feedback_screen.dart` or user beta forms is triaged into 5 core functional categories:

| Category Code | Category Name | Target Module | Escalation Team |
|---|---|---|---|
| `CAT-AI` | AI Identification & Grading Accuracy | `numista_backend/routes/ai_routes.py` | AI Engineering |
| `CAT-HW` | USB Microscope Connection & Motion | `numista_hardware/auto_capture.py` | Hardware Desktop Team |
| `CAT-CSV`| CSV Mapping & Ingestion Errors | `numista_backend/routes/import_routes.py` | Backend Data Team |
| `CAT-EST`| Estate Partition & PDF Export | `numista_backend/services/passport_pdf_generator.py` | Legal & Estate Team |
| `CAT-UI` | UI Friction & Responsive Layout | `numista_mobile/lib/screens/` | Frontend Flutter Team |

---

## 2. Severity Classification Scale

| Level | Severity Name | Impact Criteria | SLA Resolution Time |
|---|---|---|---|
| **P0** | **Blocker / Crash** | App crash, login failure, Cloud Run 500 error, USB agent hardware disconnection loop. | **Immediate (< 4 Hours)** |
| **P1** | **AI Misidentification** | Gemini returns wrong coin series or invalid grade string. | **Within 24 Hours** |
| **P2** | **UI / Friction** | Layout overlap, slow table rendering, missing tooltip, misaligned badge. | **Within 48 Hours** |
| **P3** | **Feature Request** | Minor enhancement suggestion or cosmetic polish. | **Targeted for November Launch** |

---

## 3. Triage Workflow & Patch Deployment

```
[Beta User Submission]
          │
          ▼
 [admin_feedback_screen.dart]
          │
          +---> Auto-categorize (CAT-AI, CAT-HW, etc.) & assign Severity (P0-P3)
          │
          v
 [Development Fix committed to 'dev' branch]
          │
          v
 [Automated Playwright E2E Verification]
          │
          v
 [Approved PR merge -> Push to 'main' -> Production Live Site]
```
"""

with open(ROOT / "beta_feedback_rubric.md", "w", encoding="utf-8") as f:
    f.write(beta_rubric_md)
with open(ADVISOR_DIR / "beta_feedback_rubric.md", "w", encoding="utf-8") as f:
    f.write(beta_rubric_md)

print("Saved 5/5: beta_feedback_rubric.md")
print("\nALL 5 TARGET FILES CREATED SUCCESSFULLY!")
