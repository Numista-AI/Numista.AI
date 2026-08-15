# Golden Prompts: Generate-and-Select Command Patterns for Antigravity

These prompt templates operationalize the **Generate-and-Select** methodology inside Antigravity sessions. Use them to ensure tasks complete against verified machine commands rather than subjective reviews.

---

## 1. Feature / Bug Fix Prompt (With Executable Exit Criteria)

```markdown
Antigravity, please implement [Feature / Bug Fix Description] in [Target File(s)].

### Constraints & Scope:
- Keep changes localized to [Target Files / Directories].
- Follow existing architecture in ARCHITECTURE.md.

### Machine Exit Criteria (Generate-and-Select):
Before declaring this task complete, run the following verification commands and confirm they exit 0:
1. Python Backend: `pytest numista_tests/test_[feature].py`
2. Frontend: `flutter analyze`
3. Git Hygiene: `git status` (confirm only target files were touched)

If any test fails, feed the raw terminal output back into your edit loop and fix the root cause.
```

---

## 2. Refactoring Prompt (Inherited Test Suite Verifier)

```markdown
Antigravity, refactor [Component / Module Name] in [Target File] to improve [performance / modularity / readability].

### Ground Truth Verification:
The existing test suite at `numista_tests/test_[module].py` is our ground truth specification.
- Step 1: Run `pytest numista_tests/test_[module].py` to establish a clean baseline.
- Step 2: Perform the refactor.
- Step 3: Re-run `pytest numista_tests/test_[module].py` until 100% of tests pass.
- Step 4: Do not ask for manual human code review until all tests exit code 0.
```

---

## 3. Web UI / E2E Verification Prompt

```markdown
Antigravity, update the UI component [Component Name] in `numista_mobile/lib/screens/[Screen].dart`.

### Mechanical Verifiers:
1. Run `flutter analyze` to verify zero lint/type errors.
2. Run `npx playwright test numista_tests/e2e/[test].spec.ts` against local dev server to verify the UI interaction renders and responds without error.
3. If an element selector fails, update the code/test until Playwright passes.
```
