"""
Numista.AI -- Test Auth Storage State Generator
Generates transient, non-interactive auth storage state for Playwright E2E tests.
Saves to numista_tests/fixtures/.auth_storage_state.json (.gitignored).
"""
import os
import json
import time

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fixtures")
AUTH_STATE_PATH = os.path.join(FIXTURES_DIR, ".auth_storage_state.json")

def generate_auth_state():
    os.makedirs(FIXTURES_DIR, exist_ok=True)
    
    # Mock authenticated localStorage context for studio-9101802118-8c9a8
    auth_state = {
        "cookies": [],
        "origins": [
            {
                "origin": "https://numista.ai",
                "localStorage": [
                    {
                        "name": "numista_auth_token",
                        "value": "MOCK_EPHEMERAL_QA_TOKEN_" + str(int(time.time()))
                    },
                    {
                        "name": "numista_user_email",
                        "value": "eric.seaman@yahoo.com"
                    },
                    {
                        "name": "numista_sandbox_email",
                        "value": "ericdcman@gmail.com"
                    }
                ]
            },
            {
                "origin": "http://localhost:8080",
                "localStorage": [
                    {
                        "name": "numista_auth_token",
                        "value": "MOCK_EPHEMERAL_QA_TOKEN_" + str(int(time.time()))
                    },
                    {
                        "name": "numista_user_email",
                        "value": "eric.seaman@yahoo.com"
                    }
                ]
            }
        ]
    }
    
    with open(AUTH_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(auth_state, f, indent=2)
        
    print(f"[AUTH STATE GENERATED] Saved to: {AUTH_STATE_PATH}")
    return AUTH_STATE_PATH

if __name__ == "__main__":
    generate_auth_state()
