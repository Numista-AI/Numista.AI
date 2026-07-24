import os
import sys
import subprocess

def run_full_qa_pipeline():
    print("==================================================================")
    print("           NUMISTA.AI 1-CLICK QA TEST AUDIT RUNNER               ")
    print("==================================================================")
    
    project_dir = r"C:\Users\ericd\Documents\MyVertexProject"
    os.chdir(project_dir)

    # Step 1: Re-scan qa_dataset folder & update Ground-Truth Master CSV
    print("\n[STEP 1/5] Re-scanning qa_dataset folder & generating updated Master CSV...")
    exporter_script = os.path.join(project_dir, "scratch", "export_master_78_col_csv.py")
    subprocess.run([sys.executable, exporter_script], cwd=project_dir)

    # Step 2: Pre-clean Firestore Test Account
    print("\n[STEP 2/5] Purging previous test data for qa_test_user_20260724@numista.ai...")
    subprocess.run([sys.executable, "-m", "numista_qa_runner.purge_test_account"], cwd=project_dir)

    # Step 3: Run Playwright E2E Browser Test
    print("\n[STEP 3/5] Launching Playwright E2E Browser Test (Human UI Flow)...")
    tests_dir = os.path.join(project_dir, "numista_tests")
    subprocess.run(["npx", "playwright", "test", "tests/13-dataset-synthetic-user.spec.js"], cwd=tests_dir, shell=True)

    # Step 4: Ingest Updated Dataset into Firestore Account
    print("\n[STEP 4/5] Ingesting updated dataset into qa_test_user_20260724@numista.ai Firestore Vault...")
    subprocess.run([sys.executable, "-m", "numista_qa_runner.seed_qa_dataset"], cwd=project_dir)

    # Step 5: Run 8-Field Accuracy Auditor & Display Scorecard
    print("\n[STEP 5/5] Exporting Firestore database & calculating 8-Field Accuracy Scorecard...")
    subprocess.run([sys.executable, "-m", "numista_qa_runner.qa_account_auditor"], cwd=project_dir)

    scorecard_path = r"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\qa_account_accuracy_scorecard.md"
    print("\nOpening QA Accuracy Scorecard Report...")
    if os.path.exists(scorecard_path):
        os.startfile(scorecard_path)

    print("\n==================================================================")
    print("  SUCCESS: QA Test Audit Finished! Report opened on your screen. ")
    print("==================================================================")

if __name__ == "__main__":
    run_full_qa_pipeline()
