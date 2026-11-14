"""
numista_hardware/test_camera_filter.py
--------------------------------------
Unit and route tests for Numista.AI Hardware Agent camera discovery,
DirectShow classification, PNA/CORS headers, and mock-hardware test gating.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import auto_capture


@pytest.fixture(autouse=True)
def reset_hardware_test_state(monkeypatch):
    """Ensure mock hardware state and camera cache are clean for every test."""
    monkeypatch.delenv("NUMISTA_TEST_MODE", raising=False)
    auto_capture._mock_hardware_state = None
    auto_capture._cached_camera_data = {
        "cameras": [],
        "camera_details": [],
        "active": -1,
        "active_name": "",
        "ts": 0.0,
    }
    yield
    auto_capture._mock_hardware_state = None


# ─── DirectShow Camera Classifier Tests ───────────────────────────────────────

@pytest.mark.parametrize(
    "name,device_path,expected_kind,expected_blocked,expected_recommended",
    [
        ("Phone Link Virtual Camera", "", "phone_virtual", True, False),
        ("Link to Windows", "", "phone_virtual", True, False),
        ("OBS Virtual Camera", "", "phone_virtual", True, False),
        ("Integrated IR Camera", "", "phone_virtual", True, False),
        ("USB2.0 PC CAMERA", "", "usb_microscope", False, True),
        ("Jiusion Digital Microscope", "", "usb_microscope", False, True),
        ("Integrated Camera", "", "integrated_webcam", False, False),
        ("Generic Camera", r"\\?\usb#vid_0c45&pid_6366#mi_00", "usb_microscope", False, True),
    ],
)
def test_classify_camera_device(
    name, device_path, expected_kind, expected_blocked, expected_recommended
):
    res = auto_capture.classify_camera_device(name, device_path)
    assert res["kind"] == expected_kind
    assert res["blocked"] is expected_blocked
    assert res["is_recommended"] is expected_recommended


# ─── Discovery Order Tests ────────────────────────────────────────────────────

def test_build_camera_discovery_order_excludes_phone_virtual_and_prefers_usb():
    details = [
        {"index": 0, "name": "Phone Link Virtual Camera", "kind": "phone_virtual", "blocked": True, "is_recommended": False},
        {"index": 1, "name": "Integrated Camera", "kind": "integrated_webcam", "blocked": False, "is_recommended": False},
        {"index": 2, "name": "USB2.0 PC CAMERA", "kind": "usb_microscope", "blocked": False, "is_recommended": True},
    ]

    # Even if Phone Link (0) is requested as preferred_idx, it must be excluded.
    order = auto_capture.build_camera_discovery_order(details, preferred_idx=0)
    assert 0 not in order
    assert order == [2, 1]

    # Valid non-blocked preferred_idx is honored first.
    order_pref = auto_capture.build_camera_discovery_order(details, preferred_idx=1)
    assert order_pref == [1, 2]


# ─── PNA & CORS Headers Tests ─────────────────────────────────────────────────

def test_pna_and_cors_headers_on_preflight_and_status():
    client = auto_capture.app.test_client()

    opt_resp = client.options(
        "/list-cameras",
        headers={
            "Origin": "https://numista-vault.web.app",
            "Access-Control-Request-Private-Network": "true",
        },
    )
    assert opt_resp.status_code == 204
    assert opt_resp.headers.get("Access-Control-Allow-Private-Network") == "true"
    assert opt_resp.headers.get("Access-Control-Allow-Origin") == "https://numista-vault.web.app"

    status_resp = client.get("/get-status")
    assert status_resp.status_code == 200
    assert status_resp.headers.get("Access-Control-Allow-Private-Network") == "true"


# ─── Mock Hardware State Endpoint & /list-cameras Integration ─────────────────

def test_mock_hardware_state_requires_test_mode_env(monkeypatch):
    client = auto_capture.app.test_client()

    blocked_resp = client.post("/test/mock-hardware-state", json={"cameras": []})
    assert blocked_resp.status_code == 404

    monkeypatch.setenv("NUMISTA_TEST_MODE", "1")
    ok_resp = client.post(
        "/test/mock-hardware-state",
        json={
            "cameras": [
                {"index": 0, "name": "Phone Link Virtual Camera"},
                {"index": 1, "name": "Integrated Camera"},
                {"index": 2, "name": "USB2.0 PC CAMERA"},
            ]
        },
    )
    assert ok_resp.status_code == 200
    assert ok_resp.get_json()["status"] == "updated"

    cam_resp = client.get("/list-cameras")
    assert cam_resp.status_code == 200
    payload = cam_resp.get_json()
    assert payload["cameras"] == [1, 2]
    assert payload["active"] == 2
    assert payload["active_name"] == "USB2.0 PC CAMERA"
    phone_entry = next(d for d in payload["camera_details"] if d["index"] == 0)
    assert phone_entry["blocked"] is True
    assert phone_entry["kind"] == "phone_virtual"

    clear_resp = client.post("/test/mock-hardware-state", json={"clear": True})
    assert clear_resp.status_code == 200
    assert clear_resp.get_json()["status"] == "cleared"
    assert auto_capture._mock_hardware_state is None
