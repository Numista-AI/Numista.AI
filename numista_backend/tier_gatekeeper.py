import os
import stripe
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from fastapi import HTTPException, status
from stripe_config import load_stripe_keys

# ==============================================================================
# 🛠️ FIREBASE ADMIN SDK INITIALIZATION
# ==============================================================================
# We initialize firebase-admin safely by checking if the application has already
# been initialized.

PROJECT_ID = "studio-9101802118-8c9a8"

if not firebase_admin._apps:
    # Resolve the local path for the service account key.
    # On Cloud Run, we fall back to Application Default Credentials (ADC).
    sa_path = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json")
    if not os.path.exists(sa_path):
        sa_path = os.path.join(os.path.dirname(__file__), "serviceAccountKey.json.json")
    if os.path.exists(sa_path):
        cred = credentials.Certificate(sa_path)
        firebase_admin.initialize_app(cred, {
            'projectId': PROJECT_ID
        })
    else:
        # Default initialization (ADC)
        firebase_admin.initialize_app(options={
            'projectId': PROJECT_ID
        })

# Firestore client instance from firebase-admin SDK
db = firestore.client()

# Initialize Stripe configuration from environment variables
try:
    stripe_keys = load_stripe_keys()
    stripe.api_key = stripe_keys["secret_key"]
except Exception as e:
    print(f"[Tier Gatekeeper] Warning: Could not initialize Stripe keys: {e}")

# ==============================================================================
# 📊 USER TIERS CONFIGURATION
# ==============================================================================
# In this section, we define the limits and allowances for each tier.

TIER_COIN_LIMITS = {
    "free": 20,
    "hobbyist": 100,
    "collector": 199,
    "numismatist": 500,
    "sovereign": float("inf"),
    "power_user": float("inf"),
}

# Daily allowances for AI-powered features:
# - deepdive: Vertex AI Gemini deepdive chats
# - invoice_scan: Document AI retailer invoice parsing runs
TIER_DAILY_ALLOWANCES = {
    "free": {
        "deepdive": 3,
        "invoice_scan": 1
    },
    "hobbyist": {
        "deepdive": 10,
        "invoice_scan": 5
    },
    "collector": {
        "deepdive": 25,
        "invoice_scan": 15
    },
    "numismatist": {
        "deepdive": 100,
        "invoice_scan": 50
    },
    "sovereign": {
        "deepdive": 500,
        "invoice_scan": 250
    },
    "power_user": {
        "deepdive": float("inf"),
        "invoice_scan": float("inf")
    }
}

# ==============================================================================
# 🔍 PROFILE & COLLECTION QUERY LOGIC
# ==============================================================================

def get_user_profile(email: str) -> dict:
    """
    Reads the user's active document from the Firestore path 'users/{email}'.
    Returns the document data as a dictionary, or an empty dictionary if not found.
    """
    try:
        doc_ref = db.collection("users").document(email)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return {}
    except Exception as e:
        print(f"[Tier Gatekeeper] Error reading user profile for {email}: {e}")
        return {}


def get_user_tier(user_profile: dict) -> str:
    """
    Resolves the user's subscription tier.
    Checks both 'stripe_tier' and the fallback 'tier' field to be highly robust.
    Defaults to 'free' if no tier can be determined.
    """
    # 1. Primary check: 'stripe_tier'
    tier = user_profile.get("stripe_tier")
    
    # 2. Fallback check: 'tier'
    if not tier:
        tier = user_profile.get("tier")
        
    if tier:
        return str(tier).lower().strip()
    
    return "free"


def get_coin_count(email: str) -> int:
    """
    Calculates the total coin count by querying the 'users/{email}/coins' sub-collection.
    Uses Firestore's count() aggregation query.
    """
    try:
        coins_ref = db.collection("users").document(email).collection("coins")
        count_query = coins_ref.count()
        results = count_query.get()
        return results[0][0].value
    except Exception as e:
        print(f"[Tier Gatekeeper] Error counting coins for {email}: {e}")
        return 0

# ==============================================================================
# 💳 STRIPE INTEGRATION LOGIC
# ==============================================================================

def create_upgrade_checkout_session(email: str, target_tier: str, success_url: str, cancel_url: str) -> str:
    """
    Creates a Stripe Checkout Session for upgrading a user to a target tier.
    
    Key parameters:
      - allow_promotion_codes=True: Allows beta testers to use coupon codes.
    """
    sec_key = os.getenv("STRIPE_SECRET_KEY")
    if not sec_key:
        raise ValueError("STRIPE_SECRET_KEY is not set in environment.")
    stripe.api_key = sec_key

    # Map target tiers to their corresponding Stripe Price IDs.
    price_map = {
        "hobbyist": os.getenv("STRIPE_PRICE_HOBBYIST", "price_1HobbyistMockID"),
        "collector": os.getenv("STRIPE_PRICE_COLLECTOR", "price_1CollectorMockID"),
        "numismatist": os.getenv("STRIPE_PRICE_NUMISMATIST", "price_1NumismatistMockID"),
        "sovereign": os.getenv("STRIPE_PRICE_SOVEREIGN", "price_1SovereignMockID"),
    }

    price_id = price_map.get(target_tier.lower())
    if not price_id:
        raise ValueError(f"Stripe Price ID not found for target tier: {target_tier}")

    # Build the Checkout Session request
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        customer_email=email,
        line_items=[{
            "price": price_id,
            "quantity": 1,
        }],
        mode="subscription",
        allow_promotion_codes=True,  # 🎁 Allow coupon codes for beta testers
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "user_email": email,
            "target_tier": target_tier
        }
    )
    return session.url


def create_customer_portal_session(email: str, return_url: str) -> str:
    """
    Creates a Stripe Customer Portal Session allowing the user to manage their billing.
    """
    sec_key = os.getenv("STRIPE_SECRET_KEY")
    if not sec_key:
        raise ValueError("STRIPE_SECRET_KEY is not set in environment.")
    stripe.api_key = sec_key

    # Search for an existing customer in Stripe by email
    customers = stripe.Customer.list(email=email, limit=1)
    
    if customers.data:
        customer_id = customers.data[0].id
    else:
        # If no Stripe customer exists, create a new one to bind them
        customer = stripe.Customer.create(email=email)
        customer_id = customer.id

    # Create the billing portal session
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url
    )
    return session.url

# ==============================================================================
# 🛡️ FEATURE GATEKEEPING & COUNTER CHECKS
# ==============================================================================

def check_and_enforce_coin_limit(email: str, success_url: str = "https://numista.ai/success", cancel_url: str = "https://numista.ai/cancel") -> bool:
    """
    Enforces tier limits based on the user's coin count.
    
    If the user has exceeded their limit, raises a FastAPI HTTPException 
    (HTTP 403 Forbidden) with JSON details including their collection stats
    and a custom Stripe upgrade checkout link.
    
    Returns:
      - True: User is within limits, access granted.
    Raises:
      - HTTPException: If user exceeds limits.
    """
    user_profile = get_user_profile(email)
    tier = get_user_tier(user_profile)

    # 1. Bypass limit checks completely for power_user
    if tier == "power_user" or user_profile.get("power_user") is True:
        return True

    # 2. Query total coins in sub-collection
    coin_count = get_coin_count(email)
    
    # 3. Retrieve tier limit
    limit = TIER_COIN_LIMITS.get(tier, TIER_COIN_LIMITS["free"])

    # 4. Enforce limit
    if coin_count > limit:
        # Construct upgrade target tier
        tier_order = ["free", "hobbyist", "collector", "numismatist", "sovereign"]
        try:
            current_idx = tier_order.index(tier)
            next_tier = tier_order[current_idx + 1] if current_idx + 1 < len(tier_order) else "sovereign"
        except ValueError:
            next_tier = "hobbyist"

        try:
            checkout_link = create_upgrade_checkout_session(email, next_tier, success_url, cancel_url)
        except Exception as ex:
            checkout_link = None
            print(f"[Tier Gatekeeper] Error creating upgrade checkout link: {ex}")

        # Return a FastAPI HTTP 403 Forbidden JSON response by raising HTTPException
        detail = {
            "error": "tier_limit_exceeded",
            "message": f"Tier limit exceeded: You have {coin_count} coins, but the {tier.capitalize()} tier limit is {limit} coins.",
            "stats": {
                "coin_count": coin_count,
                "limit": limit,
                "tier": tier,
                "next_tier": next_tier
            },
            "upgrade_url": checkout_link
        }
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )

    return True


def check_and_increment_daily_usage(email: str, feature_type: str) -> bool:
    """
    Verifies and manages daily usage tokens for:
      - 'deepdive' (Vertex AI Gemini Deepdive)
      - 'invoice_scan' (Document AI Invoice parsing)

    Behavior:
      - If user's tier resolves to 'power_user' or profile has 'power_user: true', bypasses counters entirely (returns True).
      - Compares 'last_usage_date' with today's date. If different, resets counts to 0.
      - Checks if user has remaining tokens. If yes, increments count in Firestore and returns True.
      - If limit is reached, returns False.
    """
    user_profile = get_user_profile(email)
    tier = get_user_tier(user_profile)

    # 1. 🌟 POWER USER BYPASS
    if tier == "power_user" or user_profile.get("power_user") is True:
        return True

    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 2. Get existing counters or initialize defaults
    last_date = user_profile.get("last_usage_date", "")
    deepdive_count = user_profile.get("deepdive_count", 0)
    invoice_scan_count = user_profile.get("invoice_scan_count", 0)

    # 3. Check for daily reset trigger
    is_new_day = (last_date != today_str)
    if is_new_day:
        deepdive_count = 0
        invoice_scan_count = 0
        last_date = today_str

    # 4. Resolve limits based on user's tier
    allowance = TIER_DAILY_ALLOWANCES.get(tier, TIER_DAILY_ALLOWANCES["free"])
    limit = allowance.get(feature_type, 0)
    current_count = deepdive_count if feature_type == "deepdive" else invoice_scan_count

    # 5. Check if user is out of tokens
    if current_count >= limit:
        return False

    # 6. Increment and save back to Firestore
    new_count = current_count + 1
    doc_ref = db.collection("users").document(email)

    update_payload = {
        "last_usage_date": today_str
    }
    if feature_type == "deepdive":
        update_payload["deepdive_count"] = new_count
        if is_new_day:
            update_payload["invoice_scan_count"] = 0
    else:
        update_payload["invoice_scan_count"] = new_count
        if is_new_day:
            update_payload["deepdive_count"] = 0

    doc_ref.set(update_payload, merge=True)
    return True

