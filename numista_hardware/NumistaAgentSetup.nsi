; ==============================================================================
;  NumistaAgentSetup.nsi — NSIS Installer for Numista.AI Desktop Agent
;  Produces: NumistaAgentSetup.exe
;
;  Build:  makensis NumistaAgentSetup.nsi
;          (requires NSIS installed: https://nsis.sourceforge.io/)
;
;  What this installer does:
;    1. Copies NumistaAgent.exe to %LOCALAPPDATA%\NumistaAI\
;    2. Trusts localhost.crt in Windows Root CA store (certutil)
;    3. Sets HKCU autostart registry key
;    4. Creates Start Menu shortcut
;    5. Launches the agent immediately (shows setup wizard on first run)
;    6. Creates an Uninstaller
; ==============================================================================

!define PRODUCT_NAME        "Numista.AI Desktop Agent"
!define PRODUCT_VERSION     "2.0.0"
!define PRODUCT_PUBLISHER   "Numista.AI"
!define PRODUCT_URL         "https://numista.ai"
!define PRODUCT_EXE         "NumistaAgent.exe"
!define CERT_FILE           "localhost.crt"
!define INSTALL_DIR         "$LOCALAPPDATA\NumistaAI"
!define REG_RUN_KEY         "Software\Microsoft\Windows\CurrentVersion\Run"
!define REG_UNINSTALL_KEY   "Software\Microsoft\Windows\CurrentVersion\Uninstall\NumistaAgent"
!define STARTMENU_GROUP     "Numista.AI"

; NSIS settings
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "NumistaAgentSetup.exe"
InstallDir "${INSTALL_DIR}"
RequestExecutionLevel user   ; No UAC needed (LOCALAPPDATA + HKCU)
SetCompressor /SOLID lzma
SetCompress auto
CRCCheck on
BrandingText "${PRODUCT_PUBLISHER}"

; Modern UI
!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "coin.ico"
!define MUI_UNICON "coin.ico"

; ── Pages ─────────────────────────────────────────────────────────────────────
; Welcome page
!define MUI_WELCOMEPAGE_TITLE  "Welcome to Numista.AI Desktop Agent"
!define MUI_WELCOMEPAGE_TEXT   "This wizard will install the Numista.AI Desktop Agent on your computer.$\r$\n$\r$\nThe agent runs silently in your system tray and enables your USB microscope to work with numista.ai.$\r$\n$\r$\nInstallation takes about 30 seconds."
!insertmacro MUI_PAGE_WELCOME

; Directory page (hidden from user — always installs to %LOCALAPPDATA%\NumistaAI)
; !insertmacro MUI_PAGE_DIRECTORY

; Install page
!insertmacro MUI_PAGE_INSTFILES

; Finish page
!define MUI_FINISHPAGE_TITLE   "Numista.AI Desktop Agent Installed!"
!define MUI_FINISHPAGE_TEXT    "The Numista.AI Desktop Agent has been installed and started.$\r$\n$\r$\nLook for the gold coin icon in your system tray. The agent will start automatically every time Windows starts.$\r$\n$\r$\nOn first launch, you will see a brief setup window to enter your Numista.AI email."
!define MUI_FINISHPAGE_LINK    "Open Numista.AI"
!define MUI_FINISHPAGE_LINK_LOCATION "https://numista.ai"
!define MUI_FINISHPAGE_NOREBOOTSUPPORT
!insertmacro MUI_PAGE_FINISH

; Uninstall pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

; ── Install Section ────────────────────────────────────────────────────────────
Section "Main" SecMain
    SectionIn RO  ; Required — cannot be unchecked

    SetOutPath "$INSTDIR"

    ; ── Copy the main executable ────────────────────────────────────────────
    File "dist\${PRODUCT_EXE}"
    File "${CERT_FILE}"

    ; ── Trust the SSL certificate (certutil -user -addstore Root) ───────────
    DetailPrint "Trusting localhost SSL certificate..."
    ExecWait 'certutil -user -addstore Root "$INSTDIR\${CERT_FILE}"'
    ; If -user fails on some systems, try without (may need elevated rights)
    ; The installer already requested user-level execution, so -user should work.

    ; ── Registry: add to Windows autostart ──────────────────────────────────
    DetailPrint "Setting Windows autostart..."
    WriteRegStr HKCU "${REG_RUN_KEY}" "NumistaAgent" '"$INSTDIR\${PRODUCT_EXE}"'

    ; ── Start Menu shortcut ─────────────────────────────────────────────────
    DetailPrint "Creating Start Menu shortcut..."
    CreateDirectory "$SMPROGRAMS\${STARTMENU_GROUP}"
    CreateShortcut  "$SMPROGRAMS\${STARTMENU_GROUP}\Numista.AI Desktop Agent.lnk" \
                    "$INSTDIR\${PRODUCT_EXE}"
    CreateShortcut  "$SMPROGRAMS\${STARTMENU_GROUP}\Uninstall.lnk" \
                    "$INSTDIR\uninstall.exe"

    ; ── Write uninstall info to registry ────────────────────────────────────
    WriteRegStr   HKCU "${REG_UNINSTALL_KEY}" "DisplayName"     "${PRODUCT_NAME}"
    WriteRegStr   HKCU "${REG_UNINSTALL_KEY}" "DisplayVersion"  "${PRODUCT_VERSION}"
    WriteRegStr   HKCU "${REG_UNINSTALL_KEY}" "Publisher"       "${PRODUCT_PUBLISHER}"
    WriteRegStr   HKCU "${REG_UNINSTALL_KEY}" "URLInfoAbout"    "${PRODUCT_URL}"
    WriteRegStr   HKCU "${REG_UNINSTALL_KEY}" "InstallLocation" "$INSTDIR"
    WriteRegStr   HKCU "${REG_UNINSTALL_KEY}" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegDWORD HKCU "${REG_UNINSTALL_KEY}" "NoModify"        1
    WriteRegDWORD HKCU "${REG_UNINSTALL_KEY}" "NoRepair"        1

    ; ── Write the uninstaller itself ─────────────────────────────────────────
    WriteUninstaller "$INSTDIR\uninstall.exe"

    ; ── Launch the agent now ─────────────────────────────────────────────────
    DetailPrint "Starting Numista.AI Desktop Agent..."
    Exec '"$INSTDIR\${PRODUCT_EXE}"'

SectionEnd

; ── Uninstall Section ─────────────────────────────────────────────────────────
Section "Uninstall"

    ; Stop the running agent
    ExecWait 'taskkill /F /IM "${PRODUCT_EXE}"'

    ; Remove registry keys
    DeleteRegValue HKCU "${REG_RUN_KEY}" "NumistaAgent"
    DeleteRegKey   HKCU "${REG_UNINSTALL_KEY}"

    ; Remove the trusted certificate
    ExecWait 'certutil -user -delstore Root "localhost"'

    ; Remove Start Menu shortcuts
    Delete "$SMPROGRAMS\${STARTMENU_GROUP}\Numista.AI Desktop Agent.lnk"
    Delete "$SMPROGRAMS\${STARTMENU_GROUP}\Uninstall.lnk"
    RMDir  "$SMPROGRAMS\${STARTMENU_GROUP}"

    ; Remove installed files
    Delete "$INSTDIR\${PRODUCT_EXE}"
    Delete "$INSTDIR\${CERT_FILE}"
    Delete "$INSTDIR\uninstall.exe"
    RMDir  "$INSTDIR"

    ; NOTE: We intentionally do NOT delete %APPDATA%\NumistaAI\config.json
    ; so the user's email/settings survive a reinstall. The user can delete
    ; %APPDATA%\NumistaAI manually if they want a full clean slate.
    MessageBox MB_OK "Numista.AI Desktop Agent has been uninstalled.$\r$\nYour scan history and config in %APPDATA%\NumistaAI\ have been kept."

SectionEnd
