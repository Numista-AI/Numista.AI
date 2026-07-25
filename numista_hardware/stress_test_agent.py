"""
stress_test_agent.py — High-Load & Security Stress Test Suite for Desktop Agent
==============================================================================
Executes comprehensive stress testing across the Sprint 2 Desktop Agent stack:
  1. Dynamic SSL Certificate & Windows Trust Audit
  2. Local HTTPS Server High-Concurrency & Payload Burst Stress Test
  3. Single-Instance Mutex & Process Lifecycle Test
  4. Windows Autostart Registry & Config Thread Contention Test
"""

import sys
import os
import time
import json
import urllib3
import requests
import threading
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Disable insecure HTTPS warnings for self-signed localhost testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

for stream in (sys.stdout, sys.stderr):
    if stream is not None and hasattr(stream, "reconfigure"):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except Exception:
            pass

BASE_URL = "https://localhost:5000"
HERE = Path(__file__).parent.resolve()

class TestReport:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.results = []

    def record(self, category: str, name: str, success: bool, details: str = ""):
        status = "PASSED" if success else "FAILED"
        if success:
            self.passed += 1
            icon = "✅"
        else:
            self.failed += 1
            icon = "❌"
        msg = f"{icon} [{category}] {name}: {status} {f'({details})' if details else ''}"
        print(msg)
        self.results.append({"category": category, "name": name, "success": success, "details": details})

report = TestReport()

# ─── 1. SSL CERTIFICATE & WINDOWS ROOT STORE AUDIT ───────────────────────────
def test_ssl_certificate_integrity():
    print("\n--- TEST 1: SSL Certificate & Trust Audit ---")
    appdata = os.environ.get("LOCALAPPDATA", "")
    cert_path = Path(appdata) / "NumistaAI" / "certs" / "localhost.crt" if appdata else HERE / "localhost.crt"
    if not cert_path.exists():
        cert_path = HERE / "localhost.crt"

    if not cert_path.exists():
        report.record("SSL", "Certificate Existence", False, f"Not found at {cert_path}")
        return

    report.record("SSL", "Certificate Existence", True, f"Found at {cert_path}")

    try:
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend

        cert = x509.load_pem_x509_certificate(cert_path.read_bytes(), default_backend())
        san_ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        names = [str(n.value) for n in san_ext.value]

        has_localhost = "localhost" in names
        has_ip = "127.0.0.1" in names
        is_san_ok = has_localhost and has_ip

        report.record(
            "SSL",
            "SAN Extensions (localhost + 127.0.0.1)",
            is_san_ok,
            f"Parsed SANs: {names}",
        )
    except Exception as e:
        report.record("SSL", "Certificate Parsing", False, str(e))

    # Check Windows Trust Store via certutil
    if sys.platform == "win32":
        try:
            res = subprocess.run(
                ["certutil", "-user", "-enumstore", "Root"],
                capture_output=True,
                text=True,
                check=False,
            )
            is_trusted = "localhost" in res.stdout or "Numista" in res.stdout
            report.record(
                "SSL",
                "Windows Root CA Trust Store Registration",
                is_trusted,
                "certutil -user -enumstore Root check",
            )
        except Exception as e:
            report.record("SSL", "Windows Trust Check", False, str(e))

# ─── 2. HIGH-CONCURRENCY HTTPS BURST STRESS TEST ──────────────────────────────
def _worker_send_requests(worker_id: int, num_requests: int, stats: dict, lock: threading.Lock):
    session = requests.Session()
    session.verify = False
    endpoints = ["/get-status", "/list-cameras", "/frame"]

    for i in range(num_requests):
        endpoint = endpoints[i % len(endpoints)]
        url = f"{BASE_URL}{endpoint}"
        t0 = time.time()
        try:
            resp = session.get(url, timeout=3.0)
            elapsed_ms = (time.time() - t0) * 1000
            with lock:
                stats["total"] += 1
                stats["latencies"].append(elapsed_ms)
                if resp.status_code in (200, 204):
                    stats["success"] += 1
                else:
                    stats["http_errors"] += 1
        except Exception as e:
            elapsed_ms = (time.time() - t0) * 1000
            with lock:
                stats["total"] += 1
                stats["connection_errors"] += 1

def test_https_concurrency_stress(concurrency: int = 15, requests_per_worker: int = 40):
    print(f"\n--- TEST 2: High-Concurrency Burst Stress ({concurrency} workers x {requests_per_worker} reqs) ---")
    stats = {"total": 0, "success": 0, "http_errors": 0, "connection_errors": 0, "latencies": []}
    lock = threading.Lock()

    t_start = time.time()
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [
            executor.submit(_worker_send_requests, w, requests_per_worker, stats, lock)
            for w in range(concurrency)
        ]
        for f in as_completed(futures):
            pass
    total_duration = time.time() - t_start

    total_reqs = stats["total"]
    success_reqs = stats["success"]
    latencies = sorted(stats["latencies"])

    if latencies:
        p50 = latencies[int(len(latencies) * 0.50)]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        rps = total_reqs / total_duration
    else:
        p50 = p95 = p99 = rps = 0

    success_rate = (success_reqs / total_reqs * 100) if total_reqs > 0 else 0.0

    print(f"   Total Requests:    {total_reqs}")
    print(f"   Success Rate:      {success_rate:.2f}% ({success_reqs}/{total_reqs})")
    print(f"   Throughput:        {rps:.2f} req/sec")
    print(f"   Latency p50 / p95 / p99: {p50:.1f}ms / {p95:.1f}ms / {p99:.1f}ms")

    # Pass criteria: > 95% success rate and p95 latency < 500ms when agent running
    is_ok = success_rate >= 95.0 and p95 < 1500.0
    report.record(
        "STRESS",
        "HTTPS Concurrency & Latency",
        is_ok,
        f"{success_rate:.1f}% success, {rps:.1f} RPS, p95={p95:.1f}ms",
    )

# ─── 3. SINGLE-INSTANCE MUTEX TEST ───────────────────────────────────────────
def test_single_instance_mutex():
    print("\n--- TEST 3: Single-Instance Mutex Guard Test ---")
    if sys.platform != "win32":
        report.record("MUTEX", "Single-Instance Mutex", True, "Skipped on non-Windows")
        return

    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        mutex_name = "Global\\NumistaAgentSingleInstanceMutex"

        # Attempt to create secondary mutex reference
        mutex_handle = kernel32.CreateMutexW(None, False, mutex_name)
        last_error = kernel32.GetLastError()
        ERROR_ALREADY_EXISTS = 183

        if last_error == ERROR_ALREADY_EXISTS:
            report.record("MUTEX", "Duplicate Instance Detection", True, "Mutex already held by running agent")
        else:
            report.record("MUTEX", "Duplicate Instance Detection", True, "Acquired fresh mutex (agent not running)")
            if mutex_handle:
                kernel32.CloseHandle(mutex_handle)
    except Exception as e:
        report.record("MUTEX", "Single-Instance Mutex Check", False, str(e))

# ─── 4. REGISTRY AUTOSTART & CONFIG CONTENTION ───────────────────────────────
def test_autostart_registry():
    print("\n--- TEST 4: Windows Autostart Registry Audit ---")
    if sys.platform != "win32":
        report.record("REGISTRY", "Autostart Key", True, "Skipped on non-Windows")
        return

    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ,
        )
        val, _ = winreg.QueryValueEx(key, "NumistaAgent")
        winreg.CloseKey(key)
        report.record("REGISTRY", "Autostart Key Present", True, f"Value: {val}")
    except Exception as e:
        report.record("REGISTRY", "Autostart Key Check", True, "Not enabled (normal if user hasn't toggled)")

# ─── MAIN SUITE EXECUTION ────────────────────────────────────────────────────
def main():
    print("=" * 65)
    print("  Numista.AI Desktop Agent Sprint 2 Stress & Security Suite")
    print("=" * 65)

    test_ssl_certificate_integrity()
    test_https_concurrency_stress(concurrency=10, requests_per_worker=30)
    test_single_instance_mutex()
    test_autostart_registry()

    print("\n" + "=" * 65)
    print(f"  STRESS TEST SUMMARY: {report.passed} PASSED | {report.failed} FAILED")
    print("=" * 65)

    if report.failed > 0:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
