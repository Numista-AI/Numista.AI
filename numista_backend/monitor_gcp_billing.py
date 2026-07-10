import os
import sys
import google.auth
from google.auth.transport.requests import AuthorizedSession

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ID = "studio-9101802118-8c9a8"

def main():
    print("=" * 70)
    print("  GOOGLE CLOUD STARTUP CREDITS & BILLING MONITOR")
    print("=" * 70)
    
    # Set default credentials path
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\ericd\Documents\MyVertexProject\numista_backend\serviceAccountKey.json.json"
    
    try:
        # Load GCP credentials
        credentials, project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        session = AuthorizedSession(credentials)
        
        # 1. Fetch Project Billing Info
        url = f"https://cloudbilling.googleapis.com/v1/projects/{PROJECT_ID}/billingInfo"
        response = session.get(url)
        
        if response.status_code == 200:
            info = response.json()
            billing_account = info.get("billingAccountName", "Unknown")
            billing_enabled = info.get("billingEnabled", False)
            
            print(f"  GCP Project ID          : {PROJECT_ID}")
            print(f"  Billing Account Name    : {billing_account}")
            print(f"  Billing Enabled Status  : {billing_enabled}")
            
            if billing_account != "Unknown":
                # 2. Try fetching budgets if the API is enabled and service account has access
                # Endpoint: GET https://billingbudgets.googleapis.com/v1/billingAccounts/{billingAccountId}/budgets
                billing_acct_id = billing_account.split("/")[-1]
                budget_url = f"https://billingbudgets.googleapis.com/v1/billingAccounts/{billing_acct_id}/budgets"
                budget_resp = session.get(budget_url)
                
                if budget_resp.status_code == 200:
                    budgets = budget_resp.json().get("budgets", [])
                    print(f"  Active Budgets Found    : {len(budgets)}")
                    for b in budgets:
                        print(f"    - Budget: {b.get('displayName')} | Amount: {b.get('amount')}")
                else:
                    print("  Note: Budgets API returned status code:", budget_resp.status_code)
                    print("  (This is normal if the service account does not have Billing Account Viewer role).")
        else:
            print(f"  Failed to retrieve billing info. HTTP {response.status_code}")
            print(f"  Response: {response.text}")
            
    except Exception as e:
        print(f"  Error loading Google Cloud Billing API: {e}")
    print("=" * 70)

if __name__ == "__main__":
    main()
