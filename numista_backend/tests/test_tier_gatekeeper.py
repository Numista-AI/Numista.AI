import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tier_gatekeeper import get_user_tier

def test_tier_beta_tester_flag():
    profile = {'beta_tester': True, 'beta_access_expires': '2020-01-01T00:00:00Z'}
    assert get_user_tier(profile) == 'family_estate'

def test_tier_creation_timestamp_before_cutoff():
    profile = {'creation_timestamp': 1795669199999}
    assert get_user_tier(profile) == 'family_estate'

def test_tier_creation_timestamp_at_cutoff():
    profile = {'creation_timestamp': 1795669200000}
    assert get_user_tier(profile) == 'free'

def test_tier_creation_timestamp_after_cutoff():
    profile = {'creation_timestamp': 1795669200001}
    assert get_user_tier(profile) == 'free'

def test_tier_lifetime_family_estate():
    profile = {'is_lifetime_family_estate': True}
    assert get_user_tier(profile) == 'family_estate'

def test_tier_empty_profile():
    profile = {}
    assert get_user_tier(profile) == 'free'
