"""
Unit tests for Active Learning Queue Triaging, FIFO Capping, and Training Export Quality Gates
"""

import pytest
from services.training_export_service import TrainingExportService
from routes.scan_routes import enforce_review_queue_fifo_cap


class DummyDocRef:
    def __init__(self, doc_id):
        self.id = doc_id


class DummyQueueItem:
    def __init__(self, doc_id):
        self.reference = DummyDocRef(doc_id)
        self.id = doc_id


class DummyBatch:
    def __init__(self):
        self.deleted = []

    def delete(self, ref):
        self.deleted.append(ref.id)

    def commit(self):
        pass


class DummyQueueCollection:
    def __init__(self, items):
        self.items = items

    def order_by(self, *args, **kwargs):
        return self

    def stream(self):
        return self.items


def test_training_export_quality_gates():
    service = TrainingExportService()

    # Empty dataset fails quality gate
    report_empty = service.validate_quality_gates([])
    assert report_empty["passed"] is False

    # Low agreement dataset fails quality gate
    low_agreement_records = [
        {"task_type": "visual_grade", "consensus_ratio": 0.60},
        {"task_type": "visual_grade", "consensus_ratio": 0.70},
    ]
    report_low = service.validate_quality_gates(low_agreement_records)
    assert report_low["passed"] is False
    assert any("agreement" in r.lower() for r in report_low["reasons"])

    # High agreement dataset passes quality gate
    high_agreement_records = [
        {"task_type": "checklist_ocr", "consensus_ratio": 0.95, "coin_id": "c1", "human_suggested_grade": "MS-65"},
        {"task_type": "visual_grade", "consensus_ratio": 0.92, "coin_id": "c2", "human_suggested_grade": "AU-58"},
    ]
    report_pass = service.validate_quality_gates(high_agreement_records)
    assert report_pass["passed"] is True
    assert report_pass["avg_agreement"] >= 0.90


def test_sft_splits_generation():
    service = TrainingExportService()
    sample_records = [
        {"coin_id": f"c_{i}", "task_type": "visual_grade", "human_suggested_grade": "MS-63"}
        for i in range(100)
    ]
    formatted = service.format_to_gemini_sft_jsonl(sample_records)
    assert len(formatted) == 100
    assert "messages" in formatted[0]

    train, val, test = service.generate_splits(formatted, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1)
    assert len(train) == 80
    assert len(val) == 10
    assert len(test) == 10
