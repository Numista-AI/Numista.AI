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
    print("\n[STEP 1/6] Re-scanning qa_dataset folder & generating updated Master CSV...")
    exporter_script = os.path.join(project_dir, "scratch", "export_master_78_col_csv.py")
    subprocess.run([sys.executable, exporter_script], cwd=project_dir)

    # Step 2: Pre-clean Firestore Test Account
    print("\n[STEP 2/6] Purging previous test data for qa_test_user_20260724@numista.ai...")
    subprocess.run([sys.executable, "-m", "numista_qa_runner.purge_test_account"], cwd=project_dir)

    # Step 3: Run Playwright E2E Browser Test
    print("\n[STEP 3/6] Launching Playwright E2E Browser Test (Human UI Flow)...")
    tests_dir = os.path.join(project_dir, "numista_tests")
    subprocess.run(["npx", "playwright", "test", "tests/13-dataset-synthetic-user.spec.js"], cwd=tests_dir, shell=True)

    # Step 4: Ingest Updated Dataset into Firestore Account
    print("\n[STEP 4/6] Ingesting updated dataset into qa_test_user_20260724@numista.ai Firestore Vault...")
    subprocess.run([sys.executable, "-m", "numista_qa_runner.seed_qa_dataset"], cwd=project_dir)

    # Step 5: Run 8-Field Accuracy Auditor & Display Scorecard
    print("\n[STEP 5/6] Exporting Firestore database & calculating 8-Field Accuracy Scorecard...")
    subprocess.run([sys.executable, "-m", "numista_qa_runner.qa_account_auditor"], cwd=project_dir)

    # Step 6: Generate Estate Bequest Report for Beneficiary 'Nat' & Render Printout
    print("\n[STEP 6/6] Generating Estate Bequest Report for Beneficiary 'Nat' & Rendering Printout...")
    subprocess.run([sys.executable, "-m", "numista_qa_runner.qa_estate_report_tester"], cwd=project_dir)

    scorecard_path = r"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\qa_account_accuracy_scorecard.md"
    pdf_report_path = r"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\qa_estate_report_nat_bequest.pdf"

    print("\nOpening QA Accuracy Scorecard Report...")
    if os.path.exists(scorecard_path):
        os.startfile(scorecard_path)

    print(f"Opening Generated Estate Bequest PDF Report ({pdf_report_path})...")
    if os.path.exists(pdf_report_path):
        os.startfile(pdf_report_path)

    print("\n==================================================================")
    print("  SUCCESS: Full QA Test Audit & Estate Report Pipeline Finished!  ")
    print("==================================================================")

if __name__ == "__main__":
    run_full_qa_pipeline()
