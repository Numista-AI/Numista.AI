"""
qa_estate_report_tester.py — Test script for Numista.AI QA Harness

Seeds beneficiary "Nat" into qa_test_user_20260724@numista.ai estate profile,
generates a PDF Estate Bequest & Distribution Report, saves the PDF file,
and renders preview images of the report pages.
"""

import os
import sys
import asyncio
import google.auth
from google.cloud import firestore
from datetime import datetime

# Add scan_service to sys.path
PROJECT_DIR = r"C:\Users\ericd\Documents\MyVertexProject"
SCAN_SERVICE_DIR = os.path.join(PROJECT_DIR, "numista_backend", "scan_service")
if SCAN_SERVICE_DIR not in sys.path:
    sys.path.insert(0, SCAN_SERVICE_DIR)

from estate_report_generator import generate_estate_report

TEST_EMAIL = "qa_test_user_20260724@numista.ai"
OUTPUT_DIR = os.path.join(PROJECT_DIR, "1 NUMISTA.AI", "BETA TEST", "MY TESTING")
PDF_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "qa_estate_report_nat_bequest.pdf")

def setup_firestore():
    sa_path = os.path.join(PROJECT_DIR, "numista_backend", "serviceAccountKey.json.json")
    if os.path.exists(sa_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_path

    creds, _ = google.auth.default()
    return firestore.Client(credentials=creds, project="studio-9101802118-8c9a8")

def seed_estate_profile_and_beneficiary(db: firestore.Client, email: str = TEST_EMAIL):
    print(f"=== SEEDING ESTATE PROFILE & BENEFICIARY 'NAT' FOR {email} ===")
    user_ref = db.collection("users").document(email)
    
    profile_data = {
        "owner_name": "Eric",
        "estate_name": "Eric's Numismatic Estate & Coin Collection",
        "attorney_name": "Robert Vance, Esq.",
        "attorney_firm": "Vance & Associates Estate Law",
        "attorney_phone": "(555) 234-5678",
        "state": "FL",
        "beneficiaries": [
            {
                "id": "ben_nat_001",
                "alias": "Nat",
                "relationship": "Daughter",
                "share": 1.0,
                "njClass": "A",
                "notes": "Primary Beneficiary — Leaving 100% of coin collection to daughter Nat"
            }
        ],
        "updated_at": firestore.SERVER_TIMESTAMP
    }
    
    profile_ref = user_ref.collection("estate_profile").document("primary")
    profile_ref.set(profile_data, merge=True)
    print("SUCCESS: Estate profile updated with beneficiary Nat (Daughter, 100% share).")

async def run_estate_report_test():
    print("=== RUNNING QA ESTATE REPORT GENERATION TEST ===")
    db = setup_firestore()
    seed_estate_profile_and_beneficiary(db, TEST_EMAIL)
    
    report_request = {
        "mode": "estate_bequest",
        "state": "FL",
        "owner_name": "Eric",
        "report_date": datetime.now().strftime("%B %d, %Y"),
        "beneficiaries": [
            {
                "name": "Nat",
                "relationship": "Daughter",
                "share": 1.0,
                "notes": "Leaving 100% of coin collection to daughter Nat"
            }
        ]
    }
    
    print(f"Calling generate_estate_report for {TEST_EMAIL}...")
    try:
        result = await generate_estate_report(
            db=db,
            client=None,
            model="gemini-3.5-flash",
            uid=TEST_EMAIL,
            report_request=report_request
        )
        
        pdf_bytes = result.get("pdf_bytes")
        metadata = result.get("report_metadata", {})
        
        if not pdf_bytes or len(pdf_bytes) < 1000:
            print("ERROR: Generated PDF is empty or invalid.")
            return False
            
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(PDF_OUTPUT_PATH, "wb") as f:
            f.write(pdf_bytes)
            
        print(f"SUCCESS: Estate PDF Report saved to: {PDF_OUTPUT_PATH} ({len(pdf_bytes):,} bytes)")
        print(f"Report Metadata: {metadata}")
        
        try:
            import fitz
            doc = fitz.open(PDF_OUTPUT_PATH)
            print(f"PDF Page Count: {len(doc)}")
            for i, page in enumerate(doc):
                pix = page.get_pixmap(dpi=150)
                page_img_path = os.path.join(OUTPUT_DIR, f"qa_estate_report_nat_bequest_page{i+1}.png")
                pix.save(page_img_path)
                print(f"  Rendered Page {i+1} preview: {page_img_path}")
        except Exception as e:
            print(f"Page rendering warning (non-fatal): {e}")
            
        return True
    except Exception as e:
        print(f"ERROR generating estate report: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    asyncio.run(run_estate_report_test())

if __name__ == "__main__":
    main()
