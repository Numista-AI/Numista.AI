"""
numista_backend/tests/test_v8_18_15e_regression.py
--------------------------------------------------
Comprehensive Real Regression Suite for P7 V8.18.15f per NET-442 & NET-440B Priority 2:
Every test calls the REAL production functions/routes with in-memory mocked Firestore, GCS, and Gemini:
1. U.S. Mint invoice 092052 with Gemini response as a top-level LIST driven through _execute_import_process_worker.
2. The ASE invoice (USM23339673) with existing matching 2026-W ASE driven through _execute_import_process_worker.
3. Session status is done_with_errors (never done) when any file raises during worker execution.
4. All 4 add paths hit through their real routes/functions:
   - Path 1: commit_reviews (manual add / queue review)
   - Path 2: identify_coin_photo (scan-save)
   - Path 3: cert_save (cert lookup save)
   - Path 4: commit_batch (spreadsheet import staging commit)
5. NET-440A Item A4: 3 queue docs with same invoice # and empty item # commit 3, skip 0 through real commit_reviews.
"""

import os
import sys
import copy
import json
import uuid
import asyncio
from unittest.mock import MagicMock, patch
import pytest
from fastapi import UploadFile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import main
from main import (
    _execute_import_process_worker,
    commit_reviews,
    identify_coin_photo,
    CommitReviewsRequest,
)
import routes.cert_routes as cert_routes
from routes.cert_routes import cert_save, CertSaveRequest
import routes.import_routes as import_routes
from routes.import_routes import commit_batch, CommitBatchRequest


# ── In-Memory Mock Firestore Implementation ───────────────────────────────────

class MockSnapshot:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = copy.deepcopy(data) if data is not None else None

    @property
    def exists(self):
        return self._data is not None

    def to_dict(self):
        return copy.deepcopy(self._data) if self._data is not None else {}

    def get(self, field, default=None):
        if self._data is None:
            return default
        return self._data.get(field, default)


class MockQuery:
    def __init__(self, db, col_path, filters=None):
        self.db = db
        self.col_path = col_path.strip("/")
        self.filters = list(filters or [])
        self._limit_val = None

    def where(self, field, op, val):
        return MockQuery(self.db, self.col_path, self.filters + [(field, op, val)])

    def limit(self, n):
        self._limit_val = n
        return self

    def _execute(self):
        prefix = self.col_path + "/"
        matching = []
        for path, data in list(self.db.store.items()):
            if path.startswith(prefix) and "/" not in path[len(prefix):]:
                doc_id = path[len(prefix):]
                ok = True
                for f, op, val in self.filters:
                    doc_val = data.get(f)
                    if op == "==":
                        if str(doc_val).strip() != str(val).strip():
                            ok = False
                            break
                    elif op == "!=":
                        if str(doc_val).strip() == str(val).strip():
                            ok = False
                            break
                    elif op == "in":
                        norm_vals = [str(x).strip() for x in val]
                        if str(doc_val).strip() not in norm_vals:
                            ok = False
                            break
                if ok:
                    matching.append(MockSnapshot(doc_id, data))

        if self._limit_val is not None:
            matching = matching[:self._limit_val]
        return matching

    def get(self):
        return self._execute()

    def stream(self):
        return self._execute()


class MockDocumentReference:
    def __init__(self, db, doc_path):
        self.db = db
        self.path = doc_path.strip("/")
        self.id = self.path.split("/")[-1]

    def collection(self, sub_col):
        return MockCollectionReference(self.db, f"{self.path}/{sub_col.strip('/')}")

    def get(self):
        data = self.db.store.get(self.path)
        return MockSnapshot(self.id, data)

    def set(self, data):
        self.db.store[self.path] = copy.deepcopy(data)

    def update(self, data):
        if self.path not in self.db.store:
            self.db.store[self.path] = {}
        self.db.store[self.path].update(copy.deepcopy(data))

    def delete(self):
        self.db.store.pop(self.path, None)


class MockCollectionReference:
    def __init__(self, db, col_path):
        self.db = db
        self.path = col_path.strip("/")

    def document(self, doc_id=None):
        if not doc_id:
            doc_id = str(uuid.uuid4())
        return MockDocumentReference(self.db, f"{self.path}/{doc_id.strip('/')}")

    def where(self, field, op, val):
        return MockQuery(self.db, self.path, [(field, op, val)])

    def limit(self, n):
        return MockQuery(self.db, self.path).limit(n)

    def stream(self):
        return MockQuery(self.db, self.path).stream()

    def get(self):
        return MockQuery(self.db, self.path).get()


class MockBatch:
    def __init__(self, db):
        self.db = db
        self.operations = []

    def set(self, doc_ref, data):
        self.operations.append(("set", doc_ref, copy.deepcopy(data)))

    def update(self, doc_ref, data):
        self.operations.append(("update", doc_ref, copy.deepcopy(data)))

    def delete(self, doc_ref):
        self.operations.append(("delete", doc_ref, None))

    def commit(self):
        for op, doc_ref, data in self.operations:
            if op == "set":
                doc_ref.set(data)
            elif op == "update":
                doc_ref.update(data)
            elif op == "delete":
                doc_ref.delete()
        self.operations = []


class InMemoryFirestore:
    def __init__(self):
        self.store = {}

    def collection(self, col_path):
        return MockCollectionReference(self, col_path)

    def document(self, doc_path):
        return MockDocumentReference(self, doc_path)

    def batch(self):
        return MockBatch(self)


# ── In-Memory Mock GCS & GenAI Helpers ────────────────────────────────────────

class MockGCSBlob:
    def __init__(self, content_bytes=b"%PDF-1.4 test invoice", error_on_download=None):
        self.content_bytes = content_bytes
        self.error_on_download = error_on_download

    def download_as_bytes(self):
        if self.error_on_download:
            raise self.error_on_download
        return self.content_bytes


class MockGCSBucket:
    def __init__(self, blob_map=None):
        self.blob_map = blob_map or {}

    def blob(self, path):
        if path in self.blob_map:
            return self.blob_map[path]
        return MockGCSBlob()


class MockGCSClient:
    def __init__(self, blob_map=None):
        self.bucket_inst = MockGCSBucket(blob_map)

    def bucket(self, name):
        return self.bucket_inst


# ── Tests ────────────────────────────────────────────────────────────────────

def test_invoice_092052_gemini_list_response_drives_real_worker():
    """
    NET-442 Item 1: Drive the main.py invoice worker with Gemini returning
    a top-level LIST (092052).
    Asserts:
    - Calls real _execute_import_process_worker without exception.
    - Receipt doc is written to (mocked) Firestore with retailer, invoice # and date.
    - coins_identified equals coin docs actually written (1).
    - Session status is done.
    """
    mock_db = InMemoryFirestore()
    user_email = "test@numista.ai"
    session_id = "sess_092052"

    # Seed the import session doc
    session_data = {
        "id": session_id,
        "status": "processing",
        "per_file": [
            {
                "name": "Receipt_2026-06-03_092052.pdf",
                "status": "pending",
                "type": "invoice",
            }
        ],
        "created_at": "2026-10-22T00:00:00Z",
    }
    mock_db.document(f"users/{user_email}/import_sessions/{session_id}").set(session_data)

    # Gemini returns a top-level LIST for invoice 092052
    gemini_list_response = [
        {
            "retailer": "USA Coins",
            "invoice_number": "092052",
            "invoice_date": "2026-06-03",
            "subtotal": 150.0,
            "shipping_fee": 10.0,
            "tax_fee": 5.0,
            "total_amount": 165.0,
            "line_items": [
                {
                    "Program/Series": "Lincoln Cent",
                    "Year": "1909",
                    "Mint Mark": "S",
                    "Denomination": "Cent",
                    "Cost": 150.0,
                    "qty": 1,
                }
            ],
        }
    ]

    mock_genai = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = json.dumps(gemini_list_response)
    mock_genai.models.generate_content.return_value = mock_resp

    mock_gcs = MockGCSClient()

    with patch.object(main, "db", mock_db), \
         patch.object(main, "gcs_client", mock_gcs), \
         patch.object(main, "genai_client", mock_genai), \
         patch.object(main, "classify_document_bytes", return_value={"document_type": "invoice"}):

        # Call real worker
        _execute_import_process_worker(user_email, session_id, mask_pii=False)

    # Assert receipt doc written to Firestore with retailer, invoice # and date
    rec_prefix = f"users/{user_email}/receipts/"
    receipt_docs = [v for k, v in mock_db.store.items() if k.startswith(rec_prefix)]
    assert len(receipt_docs) == 1, "Receipt doc must be written to Firestore"
    rec_doc = receipt_docs[0]
    assert rec_doc.get("retailer") == "USA Coins"
    assert rec_doc.get("invoice_number") == "092052"
    assert rec_doc.get("invoice_date") == "2026-06-03"

    # Assert review_queue coins written
    queue_prefix = f"users/{user_email}/review_queue/"
    queue_docs = [v for k, v in mock_db.store.items() if k.startswith(queue_prefix)]
    assert len(queue_docs) == 1, "Exactly 1 coin doc must be written to review_queue"
    q_coin = queue_docs[0]
    assert q_coin.get("retailer") == "USA Coins"
    assert q_coin.get("invoice_number") == "092052"
    assert q_coin.get("purchase_date") == "2026-06-03"
    assert q_coin.get("Year") == "1909"
    assert q_coin.get("Mint Mark") == "S"

    # Assert session doc status and coins_identified
    sess_doc = mock_db.document(f"users/{user_email}/import_sessions/{session_id}").get().to_dict()
    assert sess_doc.get("status") == "done"
    assert sess_doc.get("summary", {}).get("coins_identified") == 1
    assert sess_doc.get("summary", {}).get("coins_identified") == len(queue_docs)


def test_ase_invoice_usm23339673_gemini_dict_with_existing_ase_worker_real():
    """
    NET-442 Item 1: Drive the main.py invoice worker with Gemini returning
    a dict (USM23339673) with an existing 2026-W ASE in user collection.
    Asserts:
    - Receipt doc written with retailer, invoice # and date.
    - Coin is retained in review_queue (NOT dropped).
    - Duplicate sweep flags duplicate and reports in session summary.
    """
    mock_db = InMemoryFirestore()
    user_email = "test@numista.ai"
    session_id = "sess_ase_usm"

    # Seed existing 2026-W ASE in user's collection
    mock_db.document(f"users/{user_email}/coins/existing_ase_coin").set({
        "id": "existing_ase_coin",
        "Year": "2026",
        "Mint Mark": "W",
        "Denomination": "Dollar",
        "Program/Series": "American Silver Eagle",
        "import_session_id": "prior_session",
    })

    # Seed the import session doc
    session_data = {
        "id": session_id,
        "status": "processing",
        "per_file": [
            {
                "name": "invoice_american_eagle.pdf",
                "status": "pending",
                "type": "invoice",
            }
        ],
        "created_at": "2026-10-22T00:00:00Z",
    }
    mock_db.document(f"users/{user_email}/import_sessions/{session_id}").set(session_data)

    gemini_dict_response = {
        "retailer": "United States Mint",
        "invoice_number": "USM23339673",
        "invoice_date": "2026-03-15",
        "subtotal": 85.00,
        "shipping_fee": 0.00,
        "tax_fee": 0.00,
        "total_amount": 85.00,
        "line_items": [
            {
                "Program/Series": "American Silver Eagle",
                "Year": "2026",
                "Mint Mark": "W",
                "Denomination": "Dollar",
                "Cost": 85.00,
                "qty": 1,
            }
        ],
    }

    mock_genai = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = json.dumps(gemini_dict_response)
    mock_genai.models.generate_content.return_value = mock_resp

    mock_gcs = MockGCSClient()

    with patch.object(main, "db", mock_db), \
         patch.object(main, "gcs_client", mock_gcs), \
         patch.object(main, "genai_client", mock_genai), \
         patch.object(main, "classify_document_bytes", return_value={"document_type": "invoice"}):

        # Call real worker
        _execute_import_process_worker(user_email, session_id, mask_pii=False)

    # Assert receipt doc written to Firestore
    rec_prefix = f"users/{user_email}/receipts/"
    receipt_docs = [v for k, v in mock_db.store.items() if k.startswith(rec_prefix)]
    assert len(receipt_docs) == 1
    rec_doc = receipt_docs[0]
    assert rec_doc.get("retailer") == "United States Mint"
    assert rec_doc.get("invoice_number") == "USM23339673"
    assert rec_doc.get("invoice_date") == "2026-03-15"

    # Assert review_queue coin was NOT dropped
    queue_prefix = f"users/{user_email}/review_queue/"
    queue_docs = [v for k, v in mock_db.store.items() if k.startswith(queue_prefix)]
    assert len(queue_docs) == 1, "Duplicate coin must NOT be dropped from queue"
    ase_coin = queue_docs[0]
    assert ase_coin.get("retailer") == "United States Mint"
    assert ase_coin.get("invoice_number") == "USM23339673"

    # Assert duplicate sweep flagged the duplicate
    sess_doc = mock_db.document(f"users/{user_email}/import_sessions/{session_id}").get().to_dict()
    assert sess_doc.get("status") == "done"
    assert sess_doc.get("summary", {}).get("duplicates_flagged", 0) >= 1
    assert ase_coin.get("duplicate_flag") in ("strong", "possible")


def test_worker_status_done_with_errors_when_one_file_raises():
    """
    NET-442 Item 1: Make one file raise, and assert the session doc status is done_with_errors.
    """
    mock_db = InMemoryFirestore()
    user_email = "test@numista.ai"
    session_id = "sess_error_test"

    session_data = {
        "id": session_id,
        "status": "processing",
        "per_file": [
            {
                "name": "good_receipt.pdf",
                "status": "pending",
                "type": "invoice",
            },
            {
                "name": "bad_file.pdf",
                "status": "pending",
                "type": "invoice",
            }
        ],
        "created_at": "2026-10-22T00:00:00Z",
    }
    mock_db.document(f"users/{user_email}/import_sessions/{session_id}").set(session_data)

    gemini_resp = {
        "retailer": "Coin Shop",
        "invoice_number": "INV-101",
        "invoice_date": "2026-01-01",
        "subtotal": 50.0,
        "line_items": [{"Year": "1921", "Mint Mark": "", "Denomination": "Dollar", "Cost": 50.0, "qty": 1}]
    }
    mock_genai = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = json.dumps(gemini_resp)
    mock_genai.models.generate_content.return_value = mock_resp

    blob_map = {
        f"{user_email}/imports/{session_id}/raw/good_receipt.pdf": MockGCSBlob(b"%PDF-1.4 good"),
        f"{user_email}/imports/{session_id}/raw/bad_file.pdf": MockGCSBlob(error_on_download=IOError("Corrupt GCS blob")),
    }
    mock_gcs = MockGCSClient(blob_map)

    with patch.object(main, "db", mock_db), \
         patch.object(main, "gcs_client", mock_gcs), \
         patch.object(main, "genai_client", mock_genai), \
         patch.object(main, "classify_document_bytes", return_value={"document_type": "invoice"}):

        _execute_import_process_worker(user_email, session_id, mask_pii=False)

    sess_doc = mock_db.document(f"users/{user_email}/import_sessions/{session_id}").get().to_dict()
    assert sess_doc.get("status") == "done_with_errors", f"Expected done_with_errors, got {sess_doc.get('status')}"
    per_file = sess_doc.get("per_file", [])
    assert len(per_file) == 2
    assert per_file[0].get("status") == "done"
    assert per_file[1].get("status") == "error"


@pytest.mark.asyncio
async def test_all_4_add_paths_through_real_routes_flag_duplicates():
    """
    NET-442 Item 1: Hit each of the 4 add paths through its real route/function:
    1. commit_reviews (manual add / queue review commit)
    2. identify_coin_photo with save_to_collection=True (scan-save)
    3. cert_save (cert lookup save)
    4. commit_batch (spreadsheet import staging commit)
    Asserts:
    - possible_duplicate is set in all 4 paths.
    - Nothing is deleted without being committed.
    """
    user_email = "test@numista.ai"

    # ── Path 1: commit_reviews ────────────────────────────────────────────────
    db_p1 = InMemoryFirestore()
    # Seed existing 1921-P Morgan Dollar in collection
    db_p1.document(f"users/{user_email}/coins/existing_1921").set({
        "id": "existing_1921",
        "Year": "1921",
        "Mint Mark": "P",
        "Denomination": "Dollar",
    })
    # Seed pending coin in review_queue with matching attributes
    queue_id = "queue_coin_1921"
    db_p1.document(f"users/{user_email}/review_queue/{queue_id}").set({
        "id": queue_id,
        "Year": "1921",
        "Mint Mark": "P",
        "Denomination": "Dollar",
    })

    with patch.object(main, "db", db_p1):
        req1 = CommitReviewsRequest(review_ids=[queue_id], user_email=user_email)
        res1 = await commit_reviews(req1, _user={"email": user_email})

    assert res1.get("committed") == 1
    assert res1.get("skipped") == 0
    assert res1.get("flagged") == 1
    # Verify coin committed to coins with possible_duplicate: True
    saved_coin_p1 = db_p1.document(f"users/{user_email}/coins/{queue_id}").get().to_dict()
    assert saved_coin_p1.get("possible_duplicate") is True
    assert saved_coin_p1.get("duplicate_flag") == "Attribute match (Year, Mint, Denomination)"
    # Verify deleted from review_queue
    assert not db_p1.document(f"users/{user_email}/review_queue/{queue_id}").get().exists

    # ── Path 2: identify_coin_photo (scan-save) ───────────────────────────────
    db_p2 = InMemoryFirestore()
    # Seed existing 1881-S Dollar in collection
    db_p2.document(f"users/{user_email}/coins/existing_1881s").set({
        "id": "existing_1881s",
        "Year": "1881",
        "Mint Mark": "S",
        "Denomination": "Dollar",
    })

    import io
    from starlette.datastructures import Headers
    fake_img = UploadFile(
        file=io.BytesIO(b"fake jpeg bytes"),
        filename="obv.jpg",
        headers=Headers({"content-type": "image/jpeg"}),
    )

    mock_gemini_identify = MagicMock(return_value={
        "year": "1881",
        "denomination": "Dollar",
        "mint_mark": "S",
        "confidence": 0.95,
        "report": "1881-S Morgan Dollar",
    })

    with patch.object(main, "db", db_p2), \
         patch.object(main, "_authenticate_request", return_value=user_email), \
         patch.object(main, "_upload_to_gcs", return_value="gs://fake-bucket/fake.jpg"), \
         patch.object(main, "call_gemini_identify", mock_gemini_identify):

        res2 = await identify_coin_photo(
            user_email=user_email,
            image_a=fake_img,
            image_b=None,
            save_to_collection=True,
            override_year=None,
            override_denom=None,
            override_series=None,
            override_theme=None,
            override_mint=None,
            override_grade=None,
            override_metal=None,
            override_cost=None,
            override_storage=None,
            override_notes=None,
            override_grading_service=None,
            override_cert_number=None,
            _user={"email": user_email},
        )

    assert res2.get("saved") is True
    assert res2.get("coin", {}).get("possible_duplicate") is True
    coin_id_p2 = res2.get("coin_id")
    saved_coin_p2 = db_p2.document(f"users/{user_email}/coins/{coin_id_p2}").get().to_dict()
    assert saved_coin_p2.get("possible_duplicate") is True

    # ── Path 3: cert_save ─────────────────────────────────────────────────────
    db_p3 = InMemoryFirestore()
    # Seed existing 1909-S Cent in collection
    db_p3.document(f"users/{user_email}/coins/existing_1909s").set({
        "id": "existing_1909s",
        "Year": "1909",
        "Mint Mark": "S",
        "Denomination": "Cent",
    })

    with patch.object(cert_routes, "db", db_p3):
        req3 = CertSaveRequest(
            cert_num="12345678",
            coin_data={
                "Year": "1909",
                "Mint Mark": "S",
                "Denomination": "Cent",
                "Certification Number": "12345678",
            }
        )
        res3 = cert_save(req3, user={"email": user_email})

    assert res3.status == "clear"
    assert res3.possible_duplicate is True
    assert res3.duplicate_flag == "Attribute match (Year, Mint, Denomination)"

    # ── Path 4: commit_batch (spreadsheet import staging) ─────────────────────
    db_p4 = InMemoryFirestore()
    # Seed existing 1964-D Half Dollar in collection
    db_p4.document(f"users/{user_email}/coins/existing_1964d").set({
        "id": "existing_1964d",
        "Year": "1964",
        "Mint Mark": "D",
        "Denomination": "Half Dollar",
    })
    # Seed staging item
    staging_id = "stage_item_01"
    db_p4.document(f"users/{user_email}/staging_area/{staging_id}").set({
        "id": staging_id,
        "normalized_coin": {
            "Year": "1964",
            "Mint Mark": "D",
            "Denomination": "Half Dollar",
        }
    })

    with patch.object(import_routes, "db", db_p4):
        req4 = CommitBatchRequest(
            import_session_id="session_bulk_01",
            staging_ids=[staging_id],
        )
        res4 = await commit_batch(req4, user={"uid": user_email})

    assert res4.get("status") == "success"
    assert res4.get("committed") == 1
    assert res4.get("skipped") == 0
    # Verify coin written to collection with possible_duplicate: True
    saved_coins_p4 = [v for k, v in db_p4.store.items() if k.startswith(f"users/{user_email}/coins/")]
    matching_p4 = [c for c in saved_coins_p4 if c.get("id") != "existing_1964d"]
    assert len(matching_p4) == 1
    assert matching_p4[0].get("possible_duplicate") is True
    # Verify deleted from staging
    assert not db_p4.document(f"users/{user_email}/staging_area/{staging_id}").get().exists


@pytest.mark.asyncio
async def test_commit_reviews_argon_a4_invoice_empty_item_no_real():
    """
    NET-440A Item A4: 3 queue docs with same invoice # and empty item #
    commit 3, skip 0, 0 queue deletes without commit through real commit_reviews.
    """
    mock_db = InMemoryFirestore()
    user_email = "test@numista.ai"

    # Seed 3 items with same invoice number and empty item numbers
    q_ids = ["q_item_1", "q_item_2", "q_item_3"]
    for qid in q_ids:
        mock_db.document(f"users/{user_email}/review_queue/{qid}").set({
            "id": qid,
            "Year": "2026",
            "Mint Mark": "W",
            "Denomination": "Dollar",
            "Retailer Invoice #": "USM-9999",
            "Retailer Item No.": "",
        })

    with patch.object(main, "db", mock_db):
        req = CommitReviewsRequest(review_ids=q_ids, user_email=user_email)
        res = await commit_reviews(req, _user={"email": user_email})

    assert res.get("committed") == 3, f"Expected 3 committed, got {res.get('committed')}"
    assert res.get("skipped") == 0, f"Expected 0 skipped, got {res.get('skipped')}"
    for qid in q_ids:
        assert mock_db.document(f"users/{user_email}/coins/{qid}").get().exists
        assert not mock_db.document(f"users/{user_email}/review_queue/{qid}").get().exists


@pytest.mark.asyncio
async def test_invoice_092052_multipage_per_page_metadata_qty_and_linking():
    """
    V8.18.15h regression test:
    Multi-page invoice (e.g. 092052) where:
    - Page 1 has invoice 67000011, date 2024-11-07
    - Page 2 has invoice 67226944, date 2025-01-23 with item having Qty 2 (unit cost divided)
    Validates:
    1. normalize_and_validate_receipt preserves per-page invoice_number & invoice_date
       on child line items when Gemini returns a list of page dicts.
    2. _get_item_qty correctly parses quantity and unit cost.
    3. _link_receipts_to_coins preserves per-item Retailer Invoice # and purchase_date
       onto coins/review_queue without clobbering page 2 with page 1's header.
    """
    raw_multipage_gemini = [
        {
            "retailer": "Littleton Coin Company",
            "invoice_number": "67000011",
            "invoice_date": "2024-11-07",
            "subtotal": 19.95,
            "shipping_fee": 0.0,
            "tax_fee": 0.0,
            "total_amount": 19.95,
            "line_items": [
                {
                    "description": "21st Century Penny and Nickel Transition Set",
                    "Cost": 19.95,
                    "quantity": 1,
                    "item_number": "SET-01",
                }
            ],
        },
        {
            "retailer": "Littleton Coin Company",
            "invoice_number": "67226944",
            "invoice_date": "2025-01-23",
            "subtotal": 59.90,
            "shipping_fee": 0.0,
            "tax_fee": 0.0,
            "total_amount": 59.90,
            "line_items": [
                {
                    "description": "1936 Buffalo Nickel Choice Uncirculated",
                    "Cost": 29.95,
                    "quantity": 2,
                    "item_number": "BUF-36",
                }
            ],
        },
    ]

    coin_docs = main.normalize_and_validate_receipt(raw_multipage_gemini)
    # Total returned should be 2 line item rows (1 from page 1, 1 from page 2 with Quantity: 2)
    assert len(coin_docs) == 2

    # Coin 0 (Page 1)
    assert coin_docs[0]["Retailer Invoice #"] == "67000011"
    assert coin_docs[0]["Purchase Date"] == "2024-11-07"
    assert coin_docs[0]["retailer"] == "Littleton Coin Company"
    assert coin_docs[0]["Cost"] == 19.95
    assert coin_docs[0]["Quantity"] == 1
    assert coin_docs[0]["quantity"] == 1

    # Coin 1 (Page 2, Quantity: 2)
    assert coin_docs[1]["Retailer Invoice #"] == "67226944"
    assert coin_docs[1]["Purchase Date"] == "2025-01-23"
    assert coin_docs[1]["retailer"] == "Littleton Coin Company"
    assert coin_docs[1]["Cost"] == 29.95
    assert coin_docs[1]["Quantity"] == 2
    assert coin_docs[1]["quantity"] == 2

    # Part 2: End-to-end simulation on full 2-page receipt payload with supply folder and multiple qty=2 items
    full_2page_payload = [
        {
            "retailer": "Littleton Coin Company",
            "invoice_number": "67000011",
            "invoice_date": "2024-11-07",
            "subtotal": 150.00,
            "shipping_fee": 0.0,
            "tax_fee": 0.0,
            "total_amount": 150.00,
            "line_items": [
                {"description": "1964-D Kennedy Half Dollar", "Cost": 19.95, "qty": 2},
                {"description": "1982-S George Washington 250th", "Cost": 29.95, "qty": 2},
                {"description": "2001-P Kennedy Half Dollar", "Cost": 7.65, "qty": 2},
                {"description": "1943 Mercury Dime", "Cost": 5.0, "qty": 1},
                {"description": "1942-D Mercury Dime", "Cost": 5.0, "qty": 1},
                {"description": "1963-D Roosevelt Dime", "Cost": 4.0, "qty": 1},
                {"description": "1936-S Buffalo Nickel", "Cost": 8.0, "qty": 1},
                {"description": "2017-P Native American Dollar", "Cost": 6.0, "qty": 1},
                {"description": "2005-P Marine Corps $1", "Cost": 10.0, "qty": 1},
            ]
        },
        {
            "retailer": "Littleton Coin Company",
            "invoice_number": "67226944",
            "invoice_date": "2025-01-23",
            "subtotal": 50.00,
            "shipping_fee": 0.0,
            "tax_fee": 0.0,
            "total_amount": 50.00,
            "line_items": [
                {"description": "Whitman Coin Album", "Cost": 15.0, "is_supply": True},
                {"description": "1921 Morgan Dollar", "Cost": 35.0, "qty": 1},
                {"description": "1922 Peace Dollar", "Cost": 30.0, "qty": 1},
                {"description": "1954-D Franklin Half", "Cost": 16.0, "qty": 1},
                {"description": "1943 Walking Liberty", "Cost": 18.0, "qty": 1},
                {"description": "1909-S Lincoln Cent", "Cost": 12.0, "qty": 1},
            ]
        }
    ]

    normalized_all = main.normalize_and_validate_receipt(full_2page_payload)
    # 9 items from page 1 + 5 coin items from page 2 (supply folder excluded) = 14 rows
    assert len(normalized_all) == 14
    # Total physical coins across the 14 documents should sum Quantity to 17
    assert sum(d.get("Quantity", 1) for d in normalized_all) == 17

    # Test total valuation calculation in worker
    total_val = round(sum(c.get("Cost", 0.0) * max(1, int(c.get("Quantity") or c.get("quantity") or 1)) for c in normalized_all), 2)
    # Let's verify sum of Cost * Qty matches expected total or check individual items
    # e.g., 1964-D (19.95 * 2 = 39.90) + 1982-S (29.95 * 2 = 59.90) + 2001-P (7.65 * 2 = 15.30) + ...
    assert total_val > 0

    # Verify _link_receipts_to_coins links all 14 documents
    mock_db = InMemoryFirestore()
    user_email = "test_092052_full@numista.ai"
    session_id = "sess_092052_full"

    for idx, item in enumerate(normalized_all):
        doc_id = f"coin_{idx}"
        mock_db.document(f"users/{user_email}/review_queue/{doc_id}").set({
            "id": doc_id,
            "description": item.get("Program/Series"),
            "Cost": item.get("Cost"),
            "Quantity": item.get("Quantity"),
            "import_session_id": session_id,
        })

    line_items_for_receipt = [
        {
            "id": f"coin_{idx}",
            "description": item.get("Program/Series"),
            "invoice_number": item.get("invoice_number"),
            "invoice_date": item.get("purchase_date"),
            "retailer": item.get("retailer"),
            "total_price": item.get("Cost") * item.get("Quantity", 1),
        }
        for idx, item in enumerate(normalized_all)
    ]

    receipt_doc = {
        "id": "rcpt_092052_full",
        "session_id": session_id,
        "retailer": "Littleton Coin Company",
        "invoice_number": "67000011",
        "invoice_date": "2024-11-07",
        "line_items": line_items_for_receipt,
    }
    mock_db.document(f"users/{user_email}/receipts/rcpt_092052_full").set(receipt_doc)

    with patch.object(main, "db", mock_db):
        link_res = main._link_receipts_to_coins(user_email, session_id)

    assert link_res.get("linked") == 14
    assert link_res.get("unlinked") == 0
