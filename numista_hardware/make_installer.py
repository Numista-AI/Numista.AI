import os, shutil, subprocess, tempfile

here = os.path.dirname(os.path.abspath(__file__))
AGENT_EXE = os.path.join(here, "dist", "NumistaAgent.exe")
CERT_FILE  = os.path.join(here, "localhost.crt")
OUT_SETUP  = os.path.join(here, "NumistaAgentSetup.exe")

for f in [AGENT_EXE, CERT_FILE]:
    if not os.path.exists(f):
        print(f"ERROR: Missing {f}")
        raise SystemExit(1)

tmp = tempfile.mkdtemp(prefix="numista_setup_")

# --- PowerShell bootstrap that runs after IExpress extracts files -----------
ps1 = (
    "$installDir = \"$env:LOCALAPPDATA\\NumistaAI\"\n"
    "New-Item -ItemType Directory -Path $installDir -Force | Out-Null\n"
    "Copy-Item \"$PSScriptRoot\\NumistaAgent.exe\" \"$installDir\\NumistaAgent.exe\" -Force\n"
    "Copy-Item \"$PSScriptRoot\\localhost.crt\"    \"$installDir\\localhost.crt\"    -Force\n"
    "certutil -user -addstore Root \"$installDir\\localhost.crt\" | Out-Null\n"
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
with open(ps1_path, "w", encoding="utf-8") as fh:
    fh.write(ps1)

shutil.copy(AGENT_EXE, os.path.join(tmp, "NumistaAgent.exe"))
shutil.copy(CERT_FILE,  os.path.join(tmp, "localhost.crt"))

target_abs = os.path.abspath(OUT_SETUP)
src_dir    = tmp + "\\"

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
    "DisplayLicense=",
    "FinishMessage=",
    f"TargetName={target_abs}",
    "FriendlyName=Numista.AI Desktop Agent Setup",
    "AppLaunched=cmd /c powershell.exe -ExecutionPolicy Bypass -WindowStyle Normal -File install.ps1",
    "PostInstallCmd=<None>",
    "AdminQuietInstCmd=",
    "UserQuietInstCmd=",
    "[Strings]",
    "InstallPrompt=Install Numista.AI Desktop Agent?",
    "DisplayLicense=",
    "FinishMessage=",
    f"TargetName={target_abs}",
    "FriendlyName=Numista.AI Desktop Agent Setup",
    "AppLaunched=cmd /c powershell.exe -ExecutionPolicy Bypass -WindowStyle Normal -File install.ps1",
    "PostInstallCmd=<None>",
    "AdminQuietInstCmd=",
    "UserQuietInstCmd=",
    "[SourceFiles]",
    f"SourceFiles0={src_dir}",
    "[SourceFiles0]",
    "%FILE0%=NumistaAgent.exe",
    "%FILE1%=localhost.crt",
    "%FILE2%=install.ps1",
]

sed_path = os.path.join(tmp, "setup.sed")
with open(sed_path, "w", encoding="utf-8") as fh:
    fh.write("\r\n".join(sed_lines))

print("Running IExpress (this bundles the 133 MB exe — takes ~2 min)...")
r = subprocess.run(["iexpress", "/N", "/Q", sed_path])
print("IExpress exit code:", r.returncode)

shutil.rmtree(tmp, ignore_errors=True)

if os.path.exists(OUT_SETUP):
    size_mb = os.path.getsize(OUT_SETUP) / 1024 / 1024
    print(f"SUCCESS: {OUT_SETUP}  ({size_mb:.1f} MB)")
else:
    print("FAILED: output file not created.")
    raise SystemExit(1)
