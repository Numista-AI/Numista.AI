"""
Unit tests for Dynamic Few-Shot Exemplar Service
"""

import pytest
import os
import json
from services.few_shot_service import FewShotExemplarService


class DummyFirestoreQuery:
    def __init__(self, items):
        self.items = items

    def where(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def stream(self):
        class Doc:
            def __init__(self, data):
                self._data = data
            def to_dict(self):
                return self._data
        return [Doc(item) for item in self.items]


class DummyFirestoreCollection:
    def __init__(self, items):
        self.items = items

    def where(self, *args, **kwargs):
        return DummyFirestoreQuery(self.items)

    def limit(self, *args, **kwargs):
        return DummyFirestoreQuery(self.items)


class DummyFirestoreClient:
    def __init__(self, items):
        self.items = items

    def collection(self, name):
        return DummyFirestoreCollection(self.items)


def test_few_shot_service_firestore_retrieval():
    mock_data = [
        {
            "task_type": "checklist_ocr",
            "consensus_status": "verified",
            "consensus_ratio": 0.85,
            "input_payload": "81-S Morgan DGR",
            "verified_output": "1881-S Morgan Silver Dollar",
        },
        {
            "task_type": "checklist_ocr",
            "consensus_status": "verified",
            "consensus_ratio": 0.50,  # Below 0.67 threshold
            "input_payload": "Bad row",
            "verified_output": "Bad parse",
        }
    ]
    client = DummyFirestoreClient(mock_data)
    service = FewShotExemplarService(db_client=client)

    exemplars = service.get_verified_exemplars("checklist_ocr", limit=5)
    assert len(exemplars) == 1
    assert exemplars[0]["input_payload"] == "81-S Morgan DGR"


def test_few_shot_service_prompt_formatting():
    service = FewShotExemplarService()
    sample_exemplars = [
        {
            "input_payload": "1921-D Morgan VF30",
            "verified_output": "1921-D Morgan Dollar VF-30",
        }
    ]
    prompt_snippet = service.format_exemplars_for_prompt(sample_exemplars)
    assert "### VERIFIED NUMISMATIC REFERENCE EXEMPLARS" in prompt_snippet
    assert "1921-D Morgan VF30" in prompt_snippet
    assert "1921-D Morgan Dollar VF-30" in prompt_snippet
