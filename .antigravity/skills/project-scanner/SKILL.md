---
name: project-scanner
description: Run a comprehensive check on the Numista.Ai codebase, including error checks, pipeline audit, and running test suites to produce a scan report.
---

# Numista.Ai System Scanner Skill

## Context
This skill is triggered to perform a comprehensive system check, error audit, and pipeline verification for the Numista.Ai coin-recognition/data project.

## Instructions
1. **Error Check:** Scan the repository for broken imports, syntax errors, and malfunctioning LLM integration boundaries or API keys.
2. **Data Pipeline Audit:** Verify that local data schemas match the expected format for coin datasets.
3. **Execution:** Run any existing local test suites (`pytest`, `npm test`, etc.) and log the output.
4. **No Wandering:** Do not attempt to fix the errors automatically during this scan. Only audit and document them.

## Output Requirement
Generate a clean, human-readable markdown file titled `SCAN_REPORT.md` in the project root. Use the "Artifacts" framework to present the data with sections for:
- Executive Summary (Pass/Fail status)
- Critical Errors & Warnings
- Test Logs Summary
- Recommended Fixes
