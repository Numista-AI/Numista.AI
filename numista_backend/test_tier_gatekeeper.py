import os
import sys
import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

# Set environment variables for Stripe configuration before importing tier_gatekeeper
# Keys are loaded from numista_backend/.env (gitignored) at runtime.
# For local test runs: ensure .env is present. For CI: inject via secrets.
os.environ.setdefault("STRIPE_PUBLISHABLE_KEY", "pk_test_REPLACE_ME")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_REPLACE_ME")
os.environ["STRIPE_PRICE_HOBBYIST"] = "price_1HobbyistMockID"
os.environ["STRIPE_PRICE_COLLECTOR"] = "price_1CollectorMockID"
os.environ["STRIPE_PRICE_NUMISMATIST"] = "price_1NumismatistMockID"
os.environ["STRIPE_PRICE_SOVEREIGN"] = "price_1SovereignMockID"

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Import the module under test
import tier_gatekeeper

class TestTierGatekeeper(unittest.TestCase):
    
    def setUp(self):
        self.test_email = "test_entrepreneur_upskill@numista.ai"
        # Reset/clean up the test document in Firestore before each test
        self.db = tier_gatekeeper.db
        self._cleanup_test_user()

    def tearDown(self):
        self._cleanup_test_user()

    def _cleanup_test_user(self):
        # Delete user coins subcollection
        coins_ref = self.db.collection("users").document(self.test_email).collection("coins")
        for doc in coins_ref.stream():
            doc.reference.delete()
        # Delete user document
        self.db.collection("users").document(self.test_email).delete()

    def test_user_tier_resolution(self):
        print("\n--- Running Test: User Tier Resolution ---")
        # Test default/fallback
        profile = {}
        self.assertEqual(tier_gatekeeper.get_user_tier(profile), "free")
        
        # Test tier field
        profile = {"tier": "Hobbyist"}
        self.assertEqual(tier_gatekeeper.get_user_tier(profile), "hobbyist")

        # Test stripe_tier field
        profile = {"stripe_tier": "Collector"}
        self.assertEqual(tier_gatekeeper.get_user_tier(profile), "collector")

        # Test stripe_tier takes precedence over tier
        profile = {"stripe_tier": "Numismatist", "tier": "Hobbyist"}
        self.assertEqual(tier_gatekeeper.get_user_tier(profile), "numismatist")
        print("[OK] User Tier Resolution tests passed successfully!")

    def test_coin_count_query(self):
        print("\n--- Running Test: Coin Count Query ---")
        # Add 3 mock coins
        user_ref = self.db.collection("users").document(self.test_email)
        user_ref.set({"stripe_tier": "free"})
        
        coins_ref = user_ref.collection("coins")
        coins_ref.document("coin1").set({"Year": "1921", "Denomination": "1 Dollar"})
        coins_ref.document("coin2").set({"Year": "1909", "Denomination": "1 Cent"})
        coins_ref.document("coin3").set({"Year": "1916", "Denomination": "10 Cents"})
        
        count = tier_gatekeeper.get_coin_count(self.test_email)
        self.assertEqual(count, 3)
        print(f"[OK] Coin count resolved to: {count} (Expected: 3)")

    def test_daily_usage_limits_and_reset(self):
        print("\n--- Running Test: Daily Usage Limits & Counter Resets ---")
        user_ref = self.db.collection("users").document(self.test_email)
        
        # 1. Test Free tier limit (Free tier deepdive limit: 3)
        user_ref.set({
            "stripe_tier": "free",
            "last_usage_date": "2026-01-01", # Outdated date to trigger reset
            "deepdive_count": 5
        })
        
        # Attempt 1 (triggers date reset to today, count becomes 1)
        allowed = tier_gatekeeper.check_and_increment_daily_usage(self.test_email, "deepdive")
        self.assertTrue(allowed)
        
        # Verify it reset to today and count is 1 in Firestore
        profile = tier_gatekeeper.get_user_profile(self.test_email)
        self.assertEqual(profile.get("deepdive_count"), 1)
        
        # Attempt 2 (count becomes 2)
        allowed = tier_gatekeeper.check_and_increment_daily_usage(self.test_email, "deepdive")
        self.assertTrue(allowed)
        
        # Attempt 3 (count becomes 3)
        allowed = tier_gatekeeper.check_and_increment_daily_usage(self.test_email, "deepdive")
        self.assertTrue(allowed)
        
        # Attempt 4 (fails, exceeds limit of 3)
        allowed = tier_gatekeeper.check_and_increment_daily_usage(self.test_email, "deepdive")
        self.assertFalse(allowed)
        print("[OK] Daily usage limits correctly enforced for Free tier!")

    def test_power_user_bypass(self):
        print("\n--- Running Test: Power User Bypass ---")
        user_ref = self.db.collection("users").document(self.test_email)
        
        # Set user as power_user with high existing counts
        user_ref.set({
            "stripe_tier": "power_user",
            "last_usage_date": "2026-06-19",
            "deepdive_count": 9999,
            "invoice_scan_count": 9999
        })
        
        # Power user should bypass the checks and allow usage without incrementing or blocking
        allowed_deepdive = tier_gatekeeper.check_and_increment_daily_usage(self.test_email, "deepdive")
        allowed_scan = tier_gatekeeper.check_and_increment_daily_usage(self.test_email, "invoice_scan")
        
        self.assertTrue(allowed_deepdive)
        self.assertTrue(allowed_scan)
        
        # Verify counts remained same
        profile = tier_gatekeeper.get_user_profile(self.test_email)
        self.assertEqual(profile.get("deepdive_count"), 9999)
        self.assertEqual(profile.get("invoice_scan_count"), 9999)
        
        # Test power_user bypass via user document flag 'power_user: True'
        user_ref.set({
            "stripe_tier": "free",
            "power_user": True,
            "last_usage_date": "2026-06-19",
            "deepdive_count": 9999,
            "invoice_scan_count": 9999
        })
        allowed_deepdive = tier_gatekeeper.check_and_increment_daily_usage(self.test_email, "deepdive")
        self.assertTrue(allowed_deepdive)
        
        print("[OK] Power User bypass verified successfully (No limits applied)!")

    @patch("stripe.checkout.Session.create")
    @patch("stripe.billing_portal.Session.create")
    @patch("stripe.Customer.list")
    def test_stripe_session_creation(self, mock_cust_list, mock_portal_create, mock_checkout_create):
        print("\n--- Running Test: Stripe Session Generation ---")
        
        # Mock Stripe API return values
        mock_checkout_create.return_value = MagicMock(url="https://checkout.stripe.com/pay/test_session_123")
        mock_portal_create.return_value = MagicMock(url="https://billing.stripe.com/p/session/test_portal_123")
        mock_cust_list.return_value = MagicMock(data=[MagicMock(id="cus_test123")])
        
        # Test Checkout session creation (with allow_promotion_codes=True)
        url = tier_gatekeeper.create_upgrade_checkout_session(
            email=self.test_email,
            target_tier="hobbyist",
            success_url="https://numista.ai/success",
            cancel_url="https://numista.ai/cancel"
        )
        self.assertEqual(url, "https://checkout.stripe.com/pay/test_session_123")
        mock_checkout_create.assert_called_once()
        # Verify allow_promotion_codes was explicitly set to True
        kwargs = mock_checkout_create.call_args[1]
        self.assertTrue(kwargs.get("allow_promotion_codes"))
        
        # Test Customer Portal session creation
        portal_url = tier_gatekeeper.create_customer_portal_session(
            email=self.test_email,
            return_url="https://numista.ai/cancel"
        )
        self.assertEqual(portal_url, "https://billing.stripe.com/p/session/test_portal_123")
        mock_portal_create.assert_called_once()
        print("[OK] Stripe Checkout & Billing Portal URL generation verified successfully!")

    @patch("stripe.checkout.Session.create")
    def test_check_and_enforce_coin_limit(self, mock_checkout_create):
        print("\n--- Running Test: Check and Enforce Coin Limit ---")
        mock_checkout_create.return_value = MagicMock(url="https://checkout.stripe.com/pay/test_session_123")

        user_ref = self.db.collection("users").document(self.test_email)
        
        # 1. Under limit test
        user_ref.set({"stripe_tier": "free"})
        coins_ref = user_ref.collection("coins")
        coins_ref.document("coin1").set({"Year": "1921", "Denomination": "1 Dollar"})
        
        allowed = tier_gatekeeper.check_and_enforce_coin_limit(self.test_email)
        self.assertTrue(allowed)
        
        # 2. Power user bypass limit check
        user_ref.set({"stripe_tier": "free", "power_user": True})
        # Add more coins exceeding Free tier limit (limit = 20)
        for i in range(25):
            coins_ref.document(f"coin_{i}").set({"Year": "1921", "Denomination": "1 Dollar"})
            
        allowed = tier_gatekeeper.check_and_enforce_coin_limit(self.test_email)
        self.assertTrue(allowed)
        
        # 3. Standard user exceeding limit test (Free user with 26 coins)
        user_ref.set({"stripe_tier": "free"})
        with self.assertRaises(HTTPException) as ctx:
            tier_gatekeeper.check_and_enforce_coin_limit(self.test_email)
        
        self.assertEqual(ctx.exception.status_code, 403)
        self.assertEqual(ctx.exception.detail["error"], "tier_limit_exceeded")
        self.assertEqual(ctx.exception.detail["stats"]["coin_count"], 26)
        self.assertEqual(ctx.exception.detail["stats"]["limit"], 20)
        self.assertEqual(ctx.exception.detail["stats"]["tier"], "free")
        self.assertEqual(ctx.exception.detail["stats"]["next_tier"], "hobbyist")
        self.assertEqual(ctx.exception.detail["upgrade_url"], "https://checkout.stripe.com/pay/test_session_123")
        print("[OK] Coin limit enforcement and FastAPI HTTPException detail verified successfully!")

if __name__ == "__main__":
    unittest.main()

