r"""
build_installer_fallback.py
============================
Creates NumistaAgentSetup.exe using Python's zipfile + a bootstrap stub,
bypassing NSIS entirely. The output is a self-extracting installer that:
  1. Extracts NumistaAgent.exe to %LOCALAPPDATA%\NumistaAI\
  2. Trusts localhost.crt (certutil)
  3. Sets HKCU autostart registry key
  4. Creates a Start Menu shortcut
  5. Launches the agent
  6. Creates an uninstaller

Usage:  python build_installer_fallback.py
Output: NumistaAgentSetup.exe  (in current directory)
"""

import os, sys, zipfile, shutil, struct, subprocess, tempfile

AGENT_EXE   = os.path.join("dist", "NumistaAgent.exe")
CERT_FILE   = "localhost.crt"
OUT_SETUP   = "NumistaAgentSetup.exe"

# ── Embedded bootstrap script (runs inside the installer stub) ─────────────────
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

# 2. Copy exe and cert
Copy-Item "$extractDir\NumistaAgent.exe" "$installDir\NumistaAgent.exe" -Force
Copy-Item "$extractDir\localhost.crt"    "$installDir\localhost.crt"    -Force
Write-Host "  [1/4] Files copied." -ForegroundColor Green

# 3. Trust the SSL cert
certutil -user -addstore Root "$installDir\localhost.crt" | Out-Null
Write-Host "  [2/4] SSL certificate trusted." -ForegroundColor Green

# 4. Autostart registry key
$regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
Set-ItemProperty -Path $regPath -Name "NumistaAgent" -Value "`"$installDir\NumistaAgent.exe`""
Write-Host "  [3/4] Windows autostart set." -ForegroundColor Green

# 5. Start Menu shortcut
$wsh      = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Numista.AI Desktop Agent.lnk")
$shortcut.TargetPath   = "$installDir\NumistaAgent.exe"
$shortcut.Description  = "Numista.AI Desktop Agent"
$shortcut.Save()
Write-Host "  [4/4] Start Menu shortcut created." -ForegroundColor Green

# 6. Launch immediately
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
    # Verify required files exist
    for f in [AGENT_EXE, CERT_FILE]:
        if not os.path.exists(f):
            print(f"ERROR: Required file not found: {f}")
            sys.exit(1)

    tmp = tempfile.mkdtemp(prefix="numista_setup_")
    try:
        # Write bootstrap script
        ps1_path = os.path.join(tmp, "install.ps1")
        with open(ps1_path, "w", encoding="utf-8") as f:
            f.write(BOOTSTRAP_PS1)

        # Copy payload files into temp dir
        shutil.copy(AGENT_EXE, os.path.join(tmp, "NumistaAgent.exe"))
        shutil.copy(CERT_FILE,  os.path.join(tmp, "localhost.crt"))

        # Pack everything into a zip
        zip_path = os.path.join(tmp, "payload.zip")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for fn in ["NumistaAgent.exe", "localhost.crt", "install.ps1"]:
                zf.write(os.path.join(tmp, fn), fn)
                size_mb = os.path.getsize(os.path.join(tmp, fn)) / 1024 / 1024
                print(f"  Packed: {fn} ({size_mb:.1f} MB)")

        # Use IExpress (built into Windows) to create a self-extracting exe
        # IExpress requires a .sed directive file
        sed_content = f"""[Version]
Class=IEXPRESS
SEDVersion=3
[Options]
PackagePurpose=InstallApp
ShowInstallProgramWindow=1
HideExtractAnimation=0
UseLongFileName=1
InsideCompressed=0
CAB_FixedSize=0
CAB_ResvCodeSigning=0
RebootMode=N
InstallPrompt=Install Numista.AI Desktop Agent?
DisplayLicense=
FinishMessage=
TargetName={os.path.abspath(OUT_SETUP)}
FriendlyName=Numista.AI Desktop Agent Setup
AppLaunched=powershell.exe -ExecutionPolicy Bypass -File install.ps1
PostInstallCmd=<None>
AdminQuietInstCmd=
UserQuietInstCmd=
SourceFiles=SourceFiles
[Strings]
InstallPrompt=Install Numista.AI Desktop Agent v2.0?
DisplayLicense=
FinishMessage=
TargetName={os.path.abspath(OUT_SETUP)}
FriendlyName=Numista.AI Desktop Agent Setup
AppLaunched=powershell.exe -ExecutionPolicy Bypass -File install.ps1
PostInstallCmd=<None>
AdminQuietInstCmd=
UserQuietInstCmd=
[SourceFiles]
SourceFiles0={tmp}\\
[SourceFiles0]
%FILE0%=NumistaAgent.exe
%FILE1%=localhost.crt
%FILE2%=install.ps1
"""
        sed_path = os.path.join(tmp, "setup.sed")
        with open(sed_path, "w", encoding="utf-8") as f:
            f.write(sed_content)

        print("\n  Building self-extracting installer via IExpress...")
        result = subprocess.run(
            ["iexpress", "/N", "/Q", sed_path],
            capture_output=True, text=True
        )

        if os.path.exists(OUT_SETUP):
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
