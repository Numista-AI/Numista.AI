r"""
build_installer_fallback.py
============================
Creates NumistaAgentSetup.exe using Windows IExpress + a PowerShell bootstrap stub,
bypassing NSIS entirely. The output is a self-extracting installer that:
  1. Extracts NumistaAgent.exe to %LOCALAPPDATA%\NumistaAI\
  2. Sets HKCU autostart registry key
  3. Creates a Start Menu shortcut
  4. Launches the agent (which generates & registers its per-machine SSL cert via install_cert.py)

Usage:  python build_installer_fallback.py
Output: NumistaAgentSetup.exe  (in current directory)
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
AGENT_EXE = os.path.join(HERE, "dist", "NumistaAgent.exe")
OUT_SETUP = os.path.join(HERE, "NumistaAgentSetup.exe")

BOOTSTRAP_PS1 = r"""
$installDir = "$env:LOCALAPPDATA\NumistaAI"
$extractDir  = $PSScriptRoot  # temp extract location

Write-Host ""
Write-Host "  ================================================" -ForegroundColor Cyan
Write-Host "    Numista.AI Desktop Agent Setup               " -ForegroundColor Cyan
Write-Host "  ================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Installing to: $installDir" -ForegroundColor DarkGray
Write-Host ""

# 1. Create install dir
New-Item -ItemType Directory -Path $installDir -Force | Out-Null

# 2. Copy exe
Copy-Item "$extractDir\NumistaAgent.exe" "$installDir\NumistaAgent.exe" -Force
Write-Host "  [1/3] Files copied." -ForegroundColor Green

# 3. Autostart registry key
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
Set-ItemProperty -Path $regPath -Name "NumistaAgent" -Value "`"$installDir\NumistaAgent.exe`""
Write-Host "  [2/3] Windows autostart set." -ForegroundColor Green

# 4. Start Menu shortcut
$wsh      = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Numista.AI Desktop Agent.lnk")
$shortcut.TargetPath   = "$installDir\NumistaAgent.exe"
$shortcut.Description  = "Numista.AI Desktop Agent"
$shortcut.Save()
Write-Host "  [3/3] Start Menu shortcut created." -ForegroundColor Green

# 5. Launch immediately
Write-Host ""
Write-Host "  Starting Numista.AI Desktop Agent..." -ForegroundColor Cyan
Start-Process "$installDir\NumistaAgent.exe"

Write-Host ""
Write-Host "  ================================================" -ForegroundColor Green
Write-Host "    INSTALLATION COMPLETE!                       " -ForegroundColor Green
Write-Host "  ================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Look for the gold coin icon in your system tray." -ForegroundColor White
Write-Host "  Open numista.ai and go to Microscope Scanner to begin." -ForegroundColor White
Write-Host ""
Start-Sleep -Seconds 4
"""


def build():
    if not os.path.exists(AGENT_EXE):
        print(f"ERROR: Required file not found: {AGENT_EXE}")
        sys.exit(1)

    tmp = tempfile.mkdtemp(prefix="numista_setup_")
    try:
        ps1_path = os.path.join(tmp, "install.ps1")
        with open(ps1_path, "w", encoding="ascii") as f:
            f.write(BOOTSTRAP_PS1)

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
            'InstallPrompt="Install Numista.AI Desktop Agent v2.0?"',
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
        with open(sed_path, "w", encoding="ascii") as f:
            f.write("\r\n".join(sed_lines) + "\r\n")

        print("\n  Building self-extracting installer via IExpress...")
        result = subprocess.run(
            ["iexpress.exe", "/N", "/Q", sed_path],
            cwd=tmp,
            capture_output=True, text=True
        )

        if os.path.exists(tmp_target):
            shutil.copy2(tmp_target, OUT_SETUP)
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
                    raise RuntimeError(f"Secret byte pattern detected in {OUT_SETUP}")
            size_mb = os.path.getsize(OUT_SETUP) / 1024 / 1024
            print(f"\n  ✅ SUCCESS: {OUT_SETUP} ({size_mb:.1f} MB)")
            return True
        else:
            print(f"  IExpress output: {result.stdout}\n  {result.stderr}")
            print("  ❌ IExpress failed.")
            return False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    print("\n  Numista.AI Installer Builder (Python/IExpress fallback)")
    print("  " + "=" * 52)
    ok = build()
    sys.exit(0 if ok else 1)
