"""Regression suite proving numista_hardware builds and imports without bundled secrets (Task 2)."""

import os
import pathlib
import subprocess
import sys
import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
HW_DIR = REPO_ROOT / "numista_hardware"

FORBIDDEN_SPEC_TOKENS = (
    ".env",
    "serviceAccountKey",
    "localhost.key",
    "localhost.crt",
)

BUNDLED_MODULES = (
    "identify_coin",
    "auto_capture",
    "pcgs_service",
    "agent_config",
    "agent_setup",
    "install_cert",
    "tray_agent",
)

SOURCE_FILES = (
    "identify_coin.py",
    "auto_capture.py",
    "pcgs_service.py",
    "agent_config.py",
    "agent_setup.py",
    "install_cert.py",
    "tray_agent.py",
    "coin_engine.py",
)

INSTALLER_FILES = (
    "make_installer.py",
    "build_installer_fallback.py",
    "NumistaAgentSetup.nsi",
    "installer.nsi",
)


@pytest.mark.parametrize("spec_name", ["NumistaAgent.spec", "numista-agent.spec"])
def test_pyinstaller_specs_exclude_secrets_and_keys(spec_name: str):
    """Both PyInstaller spec files must never bundle .env, serviceAccountKey*.json, or static SSL keys."""
    spec_path = HW_DIR / spec_name
    content = spec_path.read_text(encoding="utf-8")
    active_lines = [
        line.split("#", 1)[0]
        for line in content.splitlines()
        if not line.strip().startswith("#")
    ]
    active_code = "\n".join(active_lines)
    for token in FORBIDDEN_SPEC_TOKENS:
        assert token not in active_code, f"{spec_name} still references forbidden token {token!r}"
    assert "install_cert.py" in active_code, f"{spec_name} must bundle install_cert.py for dynamic per-machine certs"


@pytest.mark.parametrize("filename", SOURCE_FILES)
def test_hardware_sources_free_of_hardcoded_keys_and_sa_files(filename: str):
    """Hardware Python modules must contain zero hardcoded AIzaSy keys or serviceAccountKey references."""
    src = (HW_DIR / filename.strip()).read_text(encoding="utf-8")
    assert "AIzaSy" not in src, f"{filename} contains a hardcoded Google API key"
    assert "serviceAccountKey" not in src, f"{filename} still references serviceAccountKey"


@pytest.mark.parametrize("filename", INSTALLER_FILES)
def test_installer_scripts_exclude_secrets_and_static_keys(filename: str):
    """Installer wrapper scripts must not package .env, serviceAccountKey, or static localhost.key/.crt."""
    src = (HW_DIR / filename).read_text(encoding="utf-8")
    active_lines = [
        line for line in src.splitlines()
        if not line.strip().startswith(("#", ";"))
    ]
    active_code = "\n".join(active_lines)
    for token in FORBIDDEN_SPEC_TOKENS:
        assert token not in active_code, f"{filename} still references forbidden token {token!r}"


@pytest.mark.parametrize("module_name", BUNDLED_MODULES)
def test_bundled_modules_import_cleanly_without_env_vars(module_name: str, tmp_path: pathlib.Path):
    """Every bundled module must import with zero crash when GOOGLE_API_KEY and PCGS_ACCESS_TOKEN are empty."""
    env = os.environ.copy()
    env["GOOGLE_API_KEY"] = ""
    env["GEMINI_API_KEY"] = ""
    env["PCGS_ACCESS_TOKEN"] = ""

    code = (
        "import os, sys; "
        f"os.environ['APPDATA'] = {str(tmp_path)!r}; "
        f"os.environ['LOCALAPPDATA'] = {str(tmp_path)!r}; "
        f"sys.path.insert(0, {str(HW_DIR)!r}); "
        "sys.frozen = True; "
        f"import {module_name}; "
        "print('IMPORT_OK')"
    )
    res = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, timeout=20)
    assert res.returncode == 0, f"Importing {module_name} with empty env failed:\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}"
    assert "IMPORT_OK" in res.stdout


def test_compiled_exe_carchivereader_toc_is_secret_free():
    """If dist/NumistaAgent.exe or dist/numista-agent.exe exist, their CArchiveReader TOC must contain zero secrets."""
    from PyInstaller.archive.readers import CArchiveReader

    forbidden_toc = {".env", "serviceaccountkey.json", "serviceaccountkey.json.json", "localhost.key", "localhost.crt"}
    for exe_name in ("NumistaAgent.exe", "numista-agent.exe"):
        exe_path = HW_DIR / "dist" / exe_name
        if not exe_path.exists():
            continue
        reader = CArchiveReader(str(exe_path))
        toc_keys = set(reader.toc.keys())
        bad = [k for k in toc_keys if any(f in k.lower() for f in forbidden_toc)]
        assert not bad, f"{exe_name} CArchiveReader TOC contains forbidden entries: {bad}"
        assert "install_cert.py" in toc_keys, f"{exe_name} CArchiveReader TOC is missing install_cert.py"
