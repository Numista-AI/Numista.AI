"""
make_installer.py — Self-Extracting Installer Builder (Secret-Free — Task 2 ARGON)
===================================================================================
Packages dist/NumistaAgent.exe into NumistaAgentSetup.exe using Windows IExpress.
Uses a space-free temporary directory for TargetName so IExpress never fails on paths
with spaces, and runs a post-build byte scan to verify zero secrets in NumistaAgentSetup.exe.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

here = os.path.dirname(os.path.abspath(__file__))
AGENT_EXE = os.path.join(here, "dist", "NumistaAgent.exe")
OUT_SETUP = os.path.join(here, "NumistaAgentSetup.exe")

if not os.path.exists(AGENT_EXE):
    print(f"ERROR: Missing {AGENT_EXE}")
    raise SystemExit(1)

tmp = tempfile.mkdtemp(prefix="numista_setup_")

try:
    # --- PowerShell bootstrap that runs after IExpress extracts files -----------
    # Note: tray_agent.py dynamically generates and registers its per-machine SSL
    # certificate via install_cert.ensure_ssl_cert() on startup.
    ps1 = (
        "$installDir = \"$env:LOCALAPPDATA\\NumistaAI\"\n"
        "New-Item -ItemType Directory -Path $installDir -Force | Out-Null\n"
        "Copy-Item \"$PSScriptRoot\\NumistaAgent.exe\" \"$installDir\\NumistaAgent.exe\" -Force\n"
        "$rk = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run'\n"
        "Set-ItemProperty -Path $rk -Name NumistaAgent -Value \"`\"$installDir\\NumistaAgent.exe`\"\"\n"
        "$wsh = New-Object -ComObject WScript.Shell\n"
        "$lnkDir = \"$env:APPDATA\\Microsoft\\Windows\\Start Menu\\Programs\"\n"
        "$sc = $wsh.CreateShortcut(\"$lnkDir\\Numista.AI Desktop Agent.lnk\")\n"
        "$sc.TargetPath = \"$installDir\\NumistaAgent.exe\"\n"
        "$sc.Save()\n"
        "Start-Process \"$installDir\\NumistaAgent.exe\"\n"
        "Write-Host 'Done! Look for the gold coin icon in your system tray.'\n"
        "Start-Sleep 3\n"
    )

    ps1_path = os.path.join(tmp, "install.ps1")
    with open(ps1_path, "w", encoding="ascii") as fh:
        fh.write(ps1)

    shutil.copy2(AGENT_EXE, os.path.join(tmp, "NumistaAgent.exe"))

    tmp_target = os.path.join(tmp, "NumistaAgentSetup.exe")
    src_dir = tmp + "\\"

    sed_lines = [
        "[Version]",
        "Class=IEXPRESS",
        "SEDVersion=3",
        "[Options]",
        "PackagePurpose=InstallApp",
        "ShowInstallProgramWindow=1",
        "HideExtractAnimation=0",
        "UseLongFileName=1",
        "InsideCompressed=0",
        "CAB_FixedSize=0",
        "CAB_ResvCodeSigning=0",
        "RebootMode=N",
        "InstallPrompt=%InstallPrompt%",
        "DisplayLicense=%DisplayLicense%",
        "FinishMessage=%FinishMessage%",
        "TargetName=%TargetName%",
        "FriendlyName=%FriendlyName%",
        "AppLaunched=%AppLaunched%",
        "PostInstallCmd=%PostInstallCmd%",
        "AdminQuietInstCmd=%AdminQuietInstCmd%",
        "UserQuietInstCmd=%UserQuietInstCmd%",
        "SourceFiles=SourceFiles",
        "[Strings]",
        'InstallPrompt="Install Numista.AI Desktop Agent?"',
        'DisplayLicense=""',
        'FinishMessage=""',
        f'TargetName="{tmp_target}"',
        'FriendlyName="Numista.AI Desktop Agent Setup"',
        'AppLaunched="cmd /c powershell.exe -ExecutionPolicy Bypass -WindowStyle Normal -File install.ps1"',
        'PostInstallCmd="<None>"',
        'AdminQuietInstCmd=""',
        'UserQuietInstCmd=""',
        'FILE0="NumistaAgent.exe"',
        'FILE1="install.ps1"',
        "[SourceFiles]",
        f"SourceFiles0={src_dir}",
        "[SourceFiles0]",
        "%FILE0%=",
        "%FILE1%=",
    ]

    sed_path = os.path.join(tmp, "setup.sed")
    with open(sed_path, "w", encoding="ascii") as fh:
        fh.write("\r\n".join(sed_lines) + "\r\n")

    print("Running IExpress (bundling secret-free NumistaAgent.exe)...")
    r = subprocess.run(["iexpress.exe", "/N", "/Q", sed_path], cwd=tmp, capture_output=True, text=True)
    print("IExpress exit code:", r.returncode)

    if not os.path.exists(tmp_target):
        print(f"FAILED: IExpress did not create {tmp_target}. stdout={r.stdout} stderr={r.stderr}")
        raise SystemExit(1)

    shutil.copy2(tmp_target, OUT_SETUP)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

if os.path.exists(OUT_SETUP):
    raw = Path(OUT_SETUP).read_bytes()
    for pat in (
        b"AIzaSy",
        b"7af45f7e0a341f369ff1a6034175825f8b9e81af",
        b"f2eb11c27044ca5d178e5e5a31678f037e88940b",
        b"BEGIN PRIVATE KEY",
        b"BEGIN RSA PRIVATE KEY",
    ):
        if pat in raw:
            os.remove(OUT_SETUP)
            raise SystemExit(f"FATAL: Secret pattern detected in {OUT_SETUP}")
    size_mb = os.path.getsize(OUT_SETUP) / 1024 / 1024
    print(f"SUCCESS: {OUT_SETUP}  ({size_mb:.1f} MB, Secret-Free Verified)")
else:
    print("FAILED: output file not created.")
    raise SystemExit(1)
