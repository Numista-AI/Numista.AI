"""
Unit tests for Collector Profile & Episodic Memory Service (snake_case enforcement & tenant isolation)
"""

import pytest
from services.collector_profile_service import CollectorProfileService


class DummyProfileDoc:
    def __init__(self, exists=True, data=None):
        self.exists = exists
        self._data = data or {}

    def get(self):
        return self

    def to_dict(self):
        return self._data

    def set(self, data, merge=True):
        self._data.update(data)
        self.exists = True


class DummySubcollection:
    def __init__(self, doc_map):
        self.doc_map = doc_map

    def document(self, name):
        if name not in self.doc_map:
            self.doc_map[name] = DummyProfileDoc(exists=False)
        return self.doc_map[name]


class DummyUserDoc:
    def __init__(self):
        self.subcollections = {}

    def collection(self, name):
        if name not in self.subcollections:
            self.subcollections[name] = DummySubcollection({})
        return self.subcollections[name]


class DummyFirestoreForProfile:
    def __init__(self):
        self.users = {}

    def collection(self, name):
        assert name == "users"
        class UsersCol:
            def __init__(self, root):
                self.root = root
            def document(self, uid):
                if uid not in self.root.users:
                    self.root.users[uid] = DummyUserDoc()
                return self.root.users[uid]
        return UsersCol(self)


def test_collector_profile_defaults_and_updates():
    db_mock = DummyFirestoreForProfile()
    service = CollectorProfileService(db_client=db_mock)

    # 1. Test baseline default profile
    profile = service.get_collector_profile("test_uid_123")
    assert profile["investment_goal"] == "numismatic_study"
    assert profile["preferred_services"] == ["PCGS", "NGC"]

    # 2. Test updating preferences with snake_case validation
    update_res = service.update_collector_profile("test_uid_123", {
        "preferred_series": ["Morgan Dollar", "Saint-Gaudens"],
        "target_grade_min": "ms-65",
        "target_grade_max": "ms-67",
        "investment_goal": "estate_planning",
        "budget_tier": "advanced",
        "opt_in_chat_extraction": True,
    })
    assert update_res["status"] == "success"

    updated = service.get_collector_profile("test_uid_123")
    assert updated["preferred_series"] == ["Morgan Dollar", "Saint-Gaudens"]
    assert updated["target_grade_min"] == "MS-65"
    assert updated["target_grade_max"] == "MS-67"
    assert updated["investment_goal"] == "estate_planning"

    # 3. Test prompt context generation
    prompt_context = service.build_profile_prompt_context("test_uid_123")
    assert "Morgan Dollar, Saint-Gaudens" in prompt_context
    assert "MS-65 to MS-67" in prompt_context
    assert "Estate Planning" in prompt_context
