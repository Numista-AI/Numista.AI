; ==============================================================================
;  installer.nsi — NSIS Installer Configuration for Numista.AI Desktop Agent
;  Produces: NumistaAgentSetup.exe
;  Build: makensis installer.nsi
; ==============================================================================

!define PRODUCT_NAME        "Numista.AI Desktop Agent"
!define PRODUCT_VERSION     "2.0.0"
!define PRODUCT_PUBLISHER   "Numista.AI"
!define PRODUCT_URL         "https://numista.ai"
!define PRODUCT_EXE         "numista-agent.exe"
!define CERT_FILE           "localhost.crt"
!define INSTALL_DIR         "$LOCALAPPDATA\NumistaAI"
!define REG_RUN_KEY         "Software\Microsoft\Windows\CurrentVersion\Run"
!define REG_UNINSTALL_KEY   "Software\Microsoft\Windows\CurrentVersion\Uninstall\NumistaAgent"
!define STARTMENU_GROUP     "Numista.AI"

; NSIS Settings
Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "NumistaAgentSetup.exe"
InstallDir "${INSTALL_DIR}"
RequestExecutionLevel user   ; Non-elevated install
SetCompressor /SOLID lzma
SetCompress auto
CRCCheck on
BrandingText "${PRODUCT_PUBLISHER}"

; Modern UI
!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "coin.ico"
!define MUI_UNICON "coin.ico"

; Pages
!define MUI_WELCOMEPAGE_TITLE  "Welcome to Numista.AI Desktop Agent Setup"
!define MUI_WELCOMEPAGE_TEXT   "This installer will configure the Numista.AI Desktop Agent for your USB microscope.$\r$\n$\r$\nIt registers the local HTTPS certificate into your Windows Current User Root CA store so video feeds work seamlessly in Chrome and Edge.$\r$\n$\r$\nInstallation takes ~15 seconds."
!insertmacro MUI_PAGE_WELCOME

!insertmacro MUI_PAGE_INSTFILES

!define MUI_FINISHPAGE_TITLE   "Numista.AI Desktop Agent Ready!"
!define MUI_FINISHPAGE_TEXT    "The Numista.AI Desktop Agent has been installed and started.$\r$\n$\r$\nLook for the green coin icon in your system tray.$\r$\n$\r$\nYour USB microscope is now ready to scan coins directly into numista.ai."
!define MUI_FINISHPAGE_LINK    "Open Numista.AI"
!define MUI_FINISHPAGE_LINK_LOCATION "https://numista.ai"
!define MUI_FINISHPAGE_NOREBOOTSUPPORT
!insertmacro MUI_PAGE_FINISH

; Uninstall Pages
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

; Install Section
Section "Main" SecMain
    SectionIn RO

    SetOutPath "$INSTDIR"

    ; Copy agent executable and SSL cert
    File "dist\${PRODUCT_EXE}"
    File "${CERT_FILE}"

    ; Register SSL certificate in Windows Current User Root CA store
    DetailPrint "Trusting localhost SSL certificate in Windows Root CA store..."
    ExecWait 'certutil -user -addstore Root "$INSTDIR\${CERT_FILE}"'

    ; Start Menu Shortcut
    DetailPrint "Creating Start Menu shortcuts..."
    CreateDirectory "$SMPROGRAMS\${STARTMENU_GROUP}"
    CreateShortcut  "$SMPROGRAMS\${STARTMENU_GROUP}\Numista.AI Desktop Agent.lnk" \
                    "$INSTDIR\${PRODUCT_EXE}"
    CreateShortcut  "$SMPROGRAMS\${STARTMENU_GROUP}\Uninstall.lnk" \
                    "$INSTDIR\uninstall.exe"

    ; Register Uninstaller
    WriteRegStr   HKCU "${REG_UNINSTALL_KEY}" "DisplayName"     "${PRODUCT_NAME}"
    WriteRegStr   HKCU "${REG_UNINSTALL_KEY}" "DisplayVersion"  "${PRODUCT_VERSION}"
    WriteRegStr   HKCU "${REG_UNINSTALL_KEY}" "Publisher"       "${PRODUCT_PUBLISHER}"
    WriteRegStr   HKCU "${REG_UNINSTALL_KEY}" "URLInfoAbout"    "${PRODUCT_URL}"
    WriteRegStr   HKCU "${REG_UNINSTALL_KEY}" "InstallLocation" "$INSTDIR"
    WriteRegStr   HKCU "${REG_UNINSTALL_KEY}" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegDWORD HKCU "${REG_UNINSTALL_KEY}" "NoModify"        1
    WriteRegDWORD HKCU "${REG_UNINSTALL_KEY}" "NoRepair"        1

    WriteUninstaller "$INSTDIR\uninstall.exe"

    ; Launch agent process
    DetailPrint "Starting Numista.AI Desktop Agent..."
    Exec '"$INSTDIR\${PRODUCT_EXE}"'
SectionEnd

; Uninstall Section
Section "Uninstall"
    ; Terminate running agent process cleanly
    ExecWait 'taskkill /F /IM "${PRODUCT_EXE}" /T'

    ; Remove registry entries
    DeleteRegValue HKCU "${REG_RUN_KEY}" "NumistaAgent"
    DeleteRegKey   HKCU "${REG_UNINSTALL_KEY}"

    ; Remove trusted certificate from Windows store
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

    MessageBox MB_OK "Numista.AI Desktop Agent has been uninstalled successfully."
SectionEnd
