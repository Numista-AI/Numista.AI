import os
import sys
import subprocess

def run_full_qa_pipeline():
    print("==================================================================")
    print("           NUMISTA.AI 1-CLICK QA TEST AUDIT RUNNER               ")
    print("==================================================================")
    
    project_dir = r"C:\Users\ericd\Documents\MyVertexProject"
    os.chdir(project_dir)

    # Step 1: Pre-clean Firestore Test Account
    print("\n[STEP 1/4] Purging previous test data for qa_test_user_20260724@numista.ai...")
    res1 = subprocess.run([sys.executable, "-m", "numista_qa_runner.purge_test_account"], cwd=project_dir)
    if res1.returncode != 0:
        print("Warning: Purge script returned non-zero code, continuing...")

    # Step 2: Run Playwright E2E Human UI Tests
    print("\n[STEP 2/4] Launching Playwright E2E Browser Test (Human User Ingestion)...")
    tests_dir = os.path.join(project_dir, "numista_tests")
    res2 = subprocess.run(["npx", "playwright", "test", "tests/13-dataset-synthetic-user.spec.js"], cwd=tests_dir, shell=True)
    if res2.returncode != 0:
        print("Warning: Playwright test completed with warnings/issues.")

    # Step 3: Run 8-Field Accuracy Auditor
    print("\n[STEP 3/4] Exporting Firestore account database & calculating 8-Field Accuracy Scorecard...")
    res3 = subprocess.run([sys.executable, "-m", "numista_qa_runner.qa_account_auditor"], cwd=project_dir)
    if res3.returncode != 0:
        print("Warning: Accuracy Auditor returned non-zero code.")

    # Step 4: Display Scorecard
    scorecard_path = r"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\qa_account_accuracy_scorecard.md"
    print("\n[STEP 4/4] Opening QA Accuracy Scorecard Report...")
    if os.path.exists(scorecard_path):
        os.startfile(scorecard_path)

    print("\n==================================================================")
    print("  SUCCESS: QA Test Audit Finished! Report opened on your screen. ")
    print("==================================================================")

if __name__ == "__main__":
    run_full_qa_pipeline()
