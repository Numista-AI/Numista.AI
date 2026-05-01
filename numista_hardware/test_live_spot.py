import logging
import time
from pcgs_service import PCGSService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def test_live_spot_fetching():
    print("=" * 60)
    print("  Numista.AI Live Silver Spot Verification")
    print("=" * 60)

    service = PCGSService()

    # 1. Initial Fetch
    print("\n1. Testing first fetch (should trigger network call)...")
    melt_1oz = service._estimate_melt_value(1.0)
    print(f"   Melt value for 1.0 oz: {melt_1oz}")
    
    spot_1 = PCGSService._live_spot_cache
    if spot_1:
        print(f"   [SUCCESS] Live spot price cached: ${spot_1:.2f}")
    else:
        print("   [FAILURE] No spot price in cache.")

    # 2. Cache Test
    print("\n2. Testing second fetch (should use cache)...")
    start_time = time.time()
    melt_again = service._estimate_melt_value(1.0)
    duration = time.time() - start_time
    print(f"   Melt value (cached): {melt_again}")
    print(f"   Fetch duration: {duration:.4f}s")
    
    if duration < 0.01:
        print("   [SUCCESS] Data retrieved from cache instantly.")
    else:
        print("   [WARNING] Second fetch took longer than expected; might not have cached.")

    # 3. Specific Coin Test
    print("\n3. Testing specific coin (Morgan Dollar ~0.77344 oz)...")
    morgan_melt = service._estimate_melt_value(0.77344)
    expected = 0.77344 * spot_1 if spot_1 else 0.77344 * PCGSService._DEFAULT_SPOT
    print(f"   Morgan Dollar melt value: {morgan_melt} (Calculated: ~${expected:.2f})")

    print("\n" + "=" * 60)
    print("  Verification Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_live_spot_fetching()
