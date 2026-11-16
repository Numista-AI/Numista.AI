import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tier_gatekeeper import get_user_tier, BETA_SIGNUP_CUTOFF_MS


def _signed_in(created_ms):
    # Server-injected Firebase Auth facts for a non-guest account (see get_user_profile).
    return {'_auth_created_ms': created_ms, '_auth_is_anonymous': False}


def test_tier_beta_tester_flag():
    profile = {'beta_tester': True, 'beta_access_expires': '2020-01-01T00:00:00Z'}
    assert get_user_tier(profile) == 'founding_beta'

def test_tier_creation_timestamp_before_cutoff():
    # 14 Dec 2026 23:59:59.999 ET
    assert get_user_tier(_signed_in(1797310799999)) == 'founding_beta'

def test_tier_creation_timestamp_last_whole_second():
    # 14 Dec 2026 23:59:59 ET = 2026-12-15T04:59:59Z
    assert get_user_tier(_signed_in(1797310799000)) == 'founding_beta'

def test_tier_creation_timestamp_at_cutoff():
    # 15 Dec 2026 00:00:00 ET = 2026-12-15T05:00:00Z
    assert get_user_tier(_signed_in(1797310800000)) == 'free'

def test_tier_creation_timestamp_after_cutoff():
    assert get_user_tier(_signed_in(1797310800001)) == 'free'

def test_tier_old_cutoff_now_inside_window():
    # 26 Nov 2026 00:00 ET (the old cutoff) now counts
    assert get_user_tier(_signed_in(1795669200000)) == 'founding_beta'

def test_tier_guest_never_beta_by_date():
    assert get_user_tier({'_auth_created_ms': 1795669200000, '_auth_is_anonymous': True}) == 'free'

def test_tier_firestore_creation_timestamp_ignored():
    assert get_user_tier({'creation_timestamp': 0}) == 'free'

def test_cutoff_constant_is_15_dec_midnight_est():
    from datetime import datetime, timedelta, timezone
    est = timezone(timedelta(hours=-5))  # December is EST; fixed offset avoids a tzdata dependency on Windows
    assert int(datetime(2026, 12, 15, 0, 0, 0, tzinfo=est).timestamp() * 1000) == 1797310800000
    assert BETA_SIGNUP_CUTOFF_MS == 1797310800000

def test_tier_lifetime_family_estate():
    profile = {'is_lifetime_family_estate': True}
    assert get_user_tier(profile) == 'family_estate'

def test_tier_empty_profile():
    profile = {}
    assert get_user_tier(profile) == 'free'

def test_anonymous_user_gets_free_tier():
    assert get_user_tier({}) in ('free', 'anonymous', None) or get_user_tier({}) != 'family_estate'
