# Rebuilding Coin Catalog with Slug-Aware Image Matching & Baseline Series Repair

This implementation plan addresses the image coverage statistics mismatch and the residual row index shift where baseline coin series names were overwritten by generic denominations.

## Proposed Changes

---

### Catalog Loader Component

#### [MODIFY] [load_definitive_catalog.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/load_definitive_catalog.py)
- **Problem**: Baseline coins are currently assigned generic series names like "Dollar", "Half Dollar", or "Quarter" based on their category column, overwriting the actual specific series.
- **Fix**: 
  - Add an `extract_program_name(title, category)` helper function to extract the true specific series name from quotes (e.g., `"Lincoln Memorial Cent"`), parentheses (e.g., `(George Washington)` -> `Presidential Dollars`), hyphens, or by stripping denomination prefixes.
  - Update the baseline coin processing loop to assign this extracted specific series name to the `"series"` key before appending to the consolidated catalog.

---

### Marketing CSV Generation Component

#### [MODIFY] [generate_marketing_csv.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/generate_marketing_csv.py)
- **Problem**: Ad-hoc patching of the baseline series names in the generator script was incomplete and bypasses database cleanliness. Additionally, literal matching against the image index yielded only 329 matches because it didn't use slugified program name matching.
- **Fix**:
  - Remove the temporary/incomplete patching of series and years inside `generate_marketing_csv.py` (since this is now correctly handled in `load_definitive_catalog.py`).
  - Implement a slugify helper `get_program_slug(series)` mapping canonical program names to lowercase, hyphenated slugs (e.g. `morgan-dollar`, `50-state-quarters`).
  - In the image matching loop, search for the slugified program name in the `filename`, `gcs_path`, `tags`, or `denomination` fields of `reference_library_export.csv` to successfully match all relevant images.
  - Rebuild the CSV using `ai_audited_status = "Yes"` (replacing any reference to "Grok" for compliance).

## Verification Plan

### Automated Verification
1. Run `python load_definitive_catalog.py` to rebuild the database `definitive_reference` table.
2. Run `python generate_marketing_csv.py` to regenerate the marketing CSV.
3. Run `python get_stats.py` (or a similar script) to verify the new coverage statistics.

### Manual Verification
- Review the first 100 rows of `numista_marketing_breakdown.csv` to ensure specific series names (e.g., "Lincoln Memorial Cents", "Washington Quarters (Classic)") are present.
- Verify that the total image matches are in the expected high range (approaching the ~10K image library count).
