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
!define INSTALL_DIR         "$LOCALAPPDATA\NumistaAI"
!define REG_RUN_KEY         "Software\Microsoft\Windows\CurrentVersion\Run"
!define REG_UNINSTALL_KEY   "Software\Microsoft\Windows\CurrentVersion\Uninstall\NumistaAgent"
!define STARTMENU_GROUP     "Numista.AI"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "NumistaAgentSetup.exe"
InstallDir "${INSTALL_DIR}"
RequestExecutionLevel user
SetCompressor /SOLID lzma
SetCompress auto
CRCCheck on
BrandingText "${PRODUCT_PUBLISHER}"

!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "coin.ico"
!define MUI_UNICON "coin.ico"

!define MUI_WELCOMEPAGE_TITLE  "Welcome to Numista.AI Desktop Agent Setup"
!define MUI_WELCOMEPAGE_TEXT   "This installer will configure the Numista.AI Desktop Agent for your USB microscope.$\r$\n$\r$\nInstallation takes ~15 seconds."
!insertmacro MUI_PAGE_WELCOME

!insertmacro MUI_PAGE_INSTFILES

!define MUI_FINISHPAGE_TITLE   "Numista.AI Desktop Agent Ready!"
!define MUI_FINISHPAGE_TEXT    "The Numista.AI Desktop Agent has been installed and started.$\r$\n$\r$\nLook for the green coin icon in your system tray."
!define MUI_FINISHPAGE_LINK    "Open Numista.AI"
!define MUI_FINISHPAGE_LINK_LOCATION "https://numista.ai"
!define MUI_FINISHPAGE_NOREBOOTSUPPORT
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "Main" SecMain
    SectionIn RO

    SetOutPath "$INSTDIR"

    ; Copy agent executable (per-machine SSL cert is generated on startup via install_cert.py)
    File "dist\${PRODUCT_EXE}"

    DetailPrint "Creating Start Menu shortcuts..."
    CreateDirectory "$SMPROGRAMS\${STARTMENU_GROUP}"
    CreateShortcut  "$SMPROGRAMS\${STARTMENU_GROUP}\Numista.AI Desktop Agent.lnk" \
                    "$INSTDIR\${PRODUCT_EXE}"
    CreateShortcut  "$SMPROGRAMS\${STARTMENU_GROUP}\Uninstall.lnk" \
                    "$INSTDIR\uninstall.exe"

    WriteRegStr   HKCU "${REG_UNINSTALL_KEY}" "DisplayName"     "${PRODUCT_NAME}"
    WriteRegStr   HKCU "${REG_UNINSTALL_KEY}" "DisplayVersion"  "${PRODUCT_VERSION}"
    WriteRegStr   HKCU "${REG_UNINSTALL_KEY}" "Publisher"       "${PRODUCT_PUBLISHER}"
    WriteRegStr   HKCU "${REG_UNINSTALL_KEY}" "URLInfoAbout"    "${PRODUCT_URL}"
    WriteRegStr   HKCU "${REG_UNINSTALL_KEY}" "InstallLocation" "$INSTDIR"
    WriteRegStr   HKCU "${REG_UNINSTALL_KEY}" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegDWORD HKCU "${REG_UNINSTALL_KEY}" "NoModify"        1
    WriteRegDWORD HKCU "${REG_UNINSTALL_KEY}" "NoRepair"        1

    WriteUninstaller "$INSTDIR\uninstall.exe"

    DetailPrint "Starting Numista.AI Desktop Agent..."
    Exec '"$INSTDIR\${PRODUCT_EXE}"'
SectionEnd

Section "Uninstall"
    ExecWait 'taskkill /F /IM "${PRODUCT_EXE}" /T'

    DeleteRegValue HKCU "${REG_RUN_KEY}" "NumistaAgent"
    DeleteRegKey   HKCU "${REG_UNINSTALL_KEY}"

    ExecWait 'certutil -user -delstore Root "localhost"'

    Delete "$SMPROGRAMS\${STARTMENU_GROUP}\Numista.AI Desktop Agent.lnk"
    Delete "$SMPROGRAMS\${STARTMENU_GROUP}\Uninstall.lnk"
    RMDir  "$SMPROGRAMS\${STARTMENU_GROUP}"

    Delete "$INSTDIR\${PRODUCT_EXE}"
    Delete "$INSTDIR\uninstall.exe"
    RMDir  "$INSTDIR"

    MessageBox MB_OK "Numista.AI Desktop Agent has been uninstalled successfully."
SectionEnd
