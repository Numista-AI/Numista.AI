### ROLE: Senior QA Automation Engineer & Python Developer
### GOAL: Full System Health Check & Regression Test for Numista.AI

Perform a comprehensive audit of the Numista.AI local build. Do not mark this task as complete until all phases are verified. If an error is found, attempt to fix it or provide a detailed log in an Artifact.

#### PHASE 1: Technical Integrity & Error Scan
1. Run the project build command (e.g., `npm run dev` or `python main.py`). 
2. Scan the terminal output and the browser console for any Critical or Warning errors.
3. Check all Python/JavaScript files for syntax errors or unresolved imports introduced in the latest update.

#### PHASE 2: Link & Navigation Crawl
1. Use the Browser Agent to navigate to the homepage.
2. Systematically click every internal link (Home, Collection, Add Coin, Settings, etc.).
3. Verify that no page returns a 404 error or a blank "white screen of death."
4. Ensure the navigation bar remains consistent across all views.

#### PHASE 3: Core Functional Stress Test (Numismatic Logic)
1. **Coin Entry:** Attempt to add a "1891 Morgan Silver Dollar" to the collection. Verify that fields like 'Mint Mark' and 'Grade' are saving correctly to the database.
2. **Portfolio Math:** Add three coins (e.g., Morgan Dollar, 1964 Quarter, 1909 Cent). Verify that the "Total Portfolio Value" updates in real-time.
3. **Face Value & Melt Value Check:** After adding the silver dollar and quarter, verify the Dashboard correctly aggregates the Face Value mathematically (e.g. at least $1.26), and check that Melt Value immediately > $0.00 without needing AI generation.
4. **Search & Filter:** Search for "Morgan." Ensure the results list filters correctly without crashing the UI.

#### PHASE 4: Reporting
1. Generate an Artifact summarizing:
   - Total links checked / Total broken.
   - Any functional failures found.
   - Screenshots of the 'Collection' page and any error states.
2. If any files were modified to fix errors, list them clearly.
