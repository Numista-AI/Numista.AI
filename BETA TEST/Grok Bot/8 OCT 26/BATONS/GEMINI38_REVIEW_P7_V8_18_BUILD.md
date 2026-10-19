# GEMINI 3.8 FLASH CODE REVIEW — P7 V8.18 BUILD

**Target Commit**: `1137b7324bc4f77862a30bc53488afd103fbac2e`  
**Branch**: `p7-v8.9`  
**Reviewer**: Gemini 3.8 Flash (via AG CoS P7 V8.18 Builder)  
**Date**: 2026-10-19  
**Verdict**: **PASS**

---

## 1. Executive Summary & Verification Checklist

The P7 V8.18 build resolves all UX and functional test gate blockers identified across the Add Coins hub, bulk HTML importer, hardware/microscope scanner integration, and authentication/export subsystems:

- [x] **FIX 1 (Syntax / Brace Fix)**: Fixed missing closing brace in `startImport()` in `add_coins.html`.
- [x] **FIX 2 (CI Script Validation)**: Added `tools/check_html_scripts.ps1` and `tools/check_html_scripts.sh` which extract and validate inline JavaScript via `node --check` and JSON-LD via JSON parser. 6/6 HTML files pass.
- [x] **FIX 3 (Window Exports & API Passthrough)**: Exported `window.resolveApiBase` and `window.getApiBaseUrl` on window object in `add_coins.html`.
- [x] **FIX 4 (Immersive Importer UI & Light Mode)**: Replaced missing image with styled owl emoji container (`aria-label="Morgan the Owl"`), added staged files preview card (`#staged-files-container`), and added `@media (prefers-color-scheme: light)` CSS tokens.
- [x] **FIX 5 (Flutter Hub API URL Helper)**: Implemented `buildAddCoinsHtmlPath(String email, {String apiBase = kApiBaseUrl})` in `add_coins_hub.dart` and wired to "Open Bulk Import →" button.
- [x] **FIX 6 (Scan Error & Timeout UI)**: Added `_buildScanErrorCard()` with 56px action buttons ("Choose a photo instead", "Try again", "Type it in"), 30s timeout guard, camera `NotFoundError` handling, and auto-focus via `_pcgsSingleFocusNode`.
- [x] **FIX 7 (Camera & Scanner Navigation Alignment)**: Wired "Take a photo" in quick add cards and sidebar to navigate to fullscreen camera flow (`showCameraFullScreen: true`), changed Microscope Scanner icon to `Icons.biotech_outlined`.
- [x] **FIX 8 (Localhost Polling Guard & Microscope Settings)**: Added `HardwareService.isMicroscopeConfigured()` guard against unsolicited localhost network calls, added settings toggle in `settings_screen.dart`, and guarded status banner in `microscope_scan_screen.dart`.
- [x] **FIX 9 (Text Legibility & Touch Targets)**: Enforced 16px minimum font size across cert lookup, help dialog, bulk import, and lookup result card; replaced "More ways to add" with 48px minHeight `Material` + `InkWell`.
- [x] **FIX 10 (Session Persistence & Version Alignment)**: Made `_welcomeDone` static in `auth_gate.dart`; bound `backup_export_service.dart` app version to dynamic `kAppVersion.replaceFirst('v', '')`.
- [x] **TESTS & LINT**:
  - `tools/check_html_scripts.ps1` -> 6/6 HTML files passed
  - `flutter analyze lib/` -> 0 errors, 0 warnings (No issues found!)
  - `flutter test --reporter compact` -> 583 passed (baseline 581 + 2 new unit tests)

---

## 2. File-by-File Verbatim Code Review

### File 1: `tools/check_html_scripts.ps1`
**Location:** `tools/check_html_scripts.ps1:48-61`  
**Verbatim Code:**
```powershell
        $isModule = ($tag -match 'type=["'']module["'']')
        $ext = if ($isModule) { ".mjs" } else { ".js" }

        $tempFile = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), "check_script_$($idx)" + $ext)
        [System.IO.File]::WriteAllText($tempFile, $scriptContent)

        $checkOutput = & node --check $tempFile 2>&1
        $exitCode = $LASTEXITCODE
        Remove-Item -Path $tempFile -Force -ErrorAction SilentlyContinue

        if ($exitCode -ne 0) {
            $filePassed = $false
            Write-Host "FAIL: $($file.Name) (script block #$idx)" -ForegroundColor Red
            Write-Host "$checkOutput" -ForegroundColor DarkRed
        }
```
- **Checklist:**
  - [x] Runs `node --check` on script blocks: **PASS**
  - [x] Handles module vs script extensions: **PASS**
  - [x] Validates JSON-LD blocks: **PASS**

---

### File 2: `tools/check_html_scripts.sh`
**Location:** `tools/check_html_scripts.sh:53-65`  
**Verbatim Code:**
```bash
  const tmpPath = path.join(os.tmpdir(), `check_${Date.now()}_${idx}${ext}`);
  fs.writeFileSync(tmpPath, scriptContent);

  try {
    execFileSync('node', ['--check', tmpPath], { stdio: 'pipe' });
  } catch (err) {
    fileFailed = true;
    console.error(`FAIL: ${fileName} (script block #${idx})`);
    if (err.stderr) console.error(err.stderr.toString());
  } finally {
    try { fs.unlinkSync(tmpPath); } catch (e) {}
  }
```
- **Checklist:**
  - [x] Cross-platform bash check script: **PASS**
  - [x] Cleans up temporary files in finally block: **PASS**

---

### File 3: `numista_mobile/web/add_coins.html`

#### Cite: `numista_mobile/web/add_coins.html:343`
**Verbatim Code:**
```html
          <div style="width: 46px; height: 46px; border-radius: 50%; border: 2px solid #D4A843; background: linear-gradient(135deg, #1e293b, #0f172a); display: flex; align-items: center; justify-content: center; font-size: 26px; box-shadow: 0 0 16px rgba(212,168,67,0.4); flex-shrink: 0;" aria-label="Morgan the Owl">🦉</div>
```
- **Checklist:**
  - [x] Replaces missing asset with styled container: **PASS**
  - [x] Accessible `aria-label="Morgan the Owl"`: **PASS**

#### Cite: `numista_mobile/web/add_coins.html:433-440`
**Verbatim Code:**
```html
    <!-- Staged Files Preview (shown when files are dropped or selected) -->
    <div id="staged-files-container" style="display: none; margin-top: 18px;">
      <div style="font-size: 0.85rem; font-weight: 600; color: var(--text); margin-bottom: 8px;">
        Selected Files (<span id="staged-files-count">0</span>):
      </div>
      <div class="file-list" id="staged-file-list" style="max-height: 220px; overflow-y: auto;"></div>
    </div>
```
- **Checklist:**
  - [x] Shows staged files list immediately upon drop/select: **PASS**

#### Cite: `numista_mobile/web/add_coins.html:591-592`
**Verbatim Code:**
```javascript
window.resolveApiBase = resolveApiBase;
window.getApiBaseUrl = getApiBaseUrl;
```
- **Checklist:**
  - [x] Exposes URL resolver helpers on window: **PASS**

#### Cite: `numista_mobile/web/add_coins.html:930-933`
**Verbatim Code:**
```javascript
  } finally {
    resetImportUIState();
  }
}
```
- **Checklist:**
  - [x] Properly closes `startImport()` function scope: **PASS**
  - [x] Confirmed valid syntax via `node --check`: **PASS**

---

### File 4: `numista_mobile/lib/screens/add_coins_hub.dart`

#### Cite: `numista_mobile/lib/screens/add_coins_hub.dart:30-34`
**Verbatim Code:**
```dart
String buildAddCoinsHtmlPath(String email, {String apiBase = kApiBaseUrl}) {
  const liveBackend = 'https://numista-backend-568985927038.us-central1.run.app';
  final apiParam = apiBase != liveBackend ? '&api=${Uri.encodeComponent(apiBase)}' : '';
  return '/add_coins.html?email=${Uri.encodeComponent(email)}$apiParam';
}
```
- **Checklist:**
  - [x] Encodes email and apiBase parameters: **PASS**
  - [x] Omits `&api=` when pointing to live production backend: **PASS**

#### Cite: `numista_mobile/lib/screens/add_coins_hub.dart:722-747`
**Verbatim Code:**
```dart
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                borderRadius: BorderRadius.circular(8),
                onTap: () => setState(() => _showMoreWays = !_showMoreWays),
                child: ConstrainedBox(
                  constraints: const BoxConstraints(minHeight: 48, minWidth: 160),
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(_showMoreWays ? Icons.expand_less : Icons.expand_more, size: 20, color: const Color(0xFF2563EB)),
                        const SizedBox(width: 8),
                        Text(
                          _showMoreWays ? 'Fewer ways to add' : 'More ways to add',
                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: Color(0xFF2563EB)),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
```
- **Checklist:**
  - [x] Minimum touch target height >= 48px: **PASS**
  - [x] Font size >= 16px: **PASS**
  - [x] Wrapped in `Material` to prevent no-material render crashes: **PASS**

#### Cite: `numista_mobile/lib/screens/add_coins_hub.dart:3099-3187`
**Verbatim Code:**
```dart
  Widget _buildScanErrorCard() {
    if (_scanErrorType == null) return const SizedBox.shrink();

    final isDark = Theme.of(context).brightness == Brightness.dark;
    final isNoCamera = _scanErrorType == 'no_camera';

    return Container(
      margin: const EdgeInsets.only(top: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF332024) : const Color(0xFFFEF2F2),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: isDark ? const Color(0xFF991B1B) : const Color(0xFFF87171)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                isNoCamera ? Icons.no_photography_outlined : Icons.warning_amber_rounded,
                color: isDark ? const Color(0xFFF87171) : const Color(0xFFDC2626),
                size: 22,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  _scanErrorMsg ?? 'Scan error',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: isDark ? const Color(0xFFFECACA) : const Color(0xFF991B1B),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (isNoCamera) ...[
            ElevatedButton.icon(
              onPressed: () => _scanSlabPhoto(directSource: ImageSource.gallery),
              icon: const Icon(Icons.photo_library_outlined, size: 20),
              label: const Text('Choose a photo instead',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(double.infinity, 56),
                backgroundColor: const Color(0xFF2563EB),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
            ),
          ] else ...[
            Wrap(
              spacing: 12,
              runSpacing: 10,
              children: [
                ElevatedButton.icon(
                  onPressed: () => _scanSlabPhoto(),
                  icon: const Icon(Icons.refresh, size: 20),
                  label: const Text('Try again',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(140, 56),
                    backgroundColor: const Color(0xFF2563EB),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                ),
                OutlinedButton.icon(
                  onPressed: () {
                    _pcgsSingleFocusNode.requestFocus();
                  },
                  icon: const Icon(Icons.edit_outlined, size: 20),
                  label: const Text('Type it in',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size(140, 56),
                    foregroundColor: isDark ? Colors.white : const Color(0xFF1E293B),
                    side: BorderSide(color: isDark ? const Color(0xFF64748B) : const Color(0xFF94A3B8)),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                ),
              ],
            ),
          ],
        ],
      ),
    );
  }
```
- **Checklist:**
  - [x] Friendly error messages with distinct iconography: **PASS**
  - [x] 56px minimum height action buttons: **PASS**
  - [x] "Type it in" focuses input via `FocusNode`: **PASS**

---

### File 5: `numista_mobile/lib/screens/base_layout.dart`

#### Cite: `numista_mobile/lib/screens/base_layout.dart:385-391`
**Verbatim Code:**
```dart
      case 'Take a photo':
      case 'AI Photo Identification':
        return AddCoinsHub(
          onNavigate: _navigateTo,
          initialTabName: 'camera',
          showCameraFullScreen: true,
        );
```
- **Checklist:**
  - [x] Fullscreen camera route routing: **PASS**

#### Cite: `numista_mobile/lib/screens/base_layout.dart:862-863`
**Verbatim Code:**
```dart
                            _buildNavItem('Take a photo', icon: Icons.camera_alt_outlined),
                            _buildNavItem('Microscope Scanner', icon: Icons.biotech_outlined),
```
- **Checklist:**
  - [x] Dedicated "Take a photo" navigation button: **PASS**
  - [x] Distinct microscope scanner icon: **PASS**

---

### File 6: `numista_mobile/lib/services/hardware_service.dart`

#### Cite: `numista_mobile/lib/services/hardware_service.dart:28-38`
**Verbatim Code:**
```dart
  static const String prefMicroscopeEnabled = 'microscope_enabled';

  static Future<bool> isMicroscopeConfigured() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(prefMicroscopeEnabled) ?? false;
  }

  static Future<void> setMicroscopeConfigured(bool enabled) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(prefMicroscopeEnabled, enabled);
  }
```
- **Checklist:**
  - [x] Defaults to `false`: **PASS**
  - [x] Persists configured status in SharedPreferences: **PASS**

#### Cite: `numista_mobile/lib/services/hardware_service.dart:120-122`
**Verbatim Code:**
```dart
    if (!(await isMicroscopeConfigured())) {
      return null;
    }
```
- **Checklist:**
  - [x] Prevents background localhost GET requests when disabled: **PASS**

---

### File 7: `numista_mobile/lib/screens/settings_screen.dart`

#### Cite: `numista_mobile/lib/screens/settings_screen.dart:557-615`
**Verbatim Code:**
```dart
  Widget _buildMicroscopeCard(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final descColor = isDark ? const Color(0xFF94A3B8) : const Color(0xFF64748B);
    final cardBg = isDark ? const Color(0xFF1E293B) : Colors.white;
    final borderColor = isDark ? const Color(0xFF374151) : const Color(0xFFE2E6E9);

    return Container(
      padding: const EdgeInsets.all(20.0),
      decoration: BoxDecoration(
        color: cardBg,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: borderColor),
      ),
      child: Row(
        children: [
          const Icon(Icons.biotech_outlined, color: Color(0xFF2DD4BF), size: 28),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Enable USB Microscope Scanner (Local Agent)',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: isDark ? Colors.white : const Color(0xFF0F172A),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Connects digital USB microscopes via the Numista Desktop Agent on localhost. Keep disabled if you use phone camera or file uploads.',
                  style: TextStyle(fontSize: 13, color: descColor),
                ),
              ],
            ),
          ),
          Switch(
            value: _microscopeEnabled,
            activeThumbColor: const Color(0xFF2DD4BF),
            onChanged: (val) async {
              setState(() => _microscopeEnabled = val);
              await HardwareService.setMicroscopeConfigured(val);
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(val
                        ? 'USB Microscope enabled — agent can connect.'
                        : 'USB Microscope disabled — localhost polling stopped.'),
                    duration: const Duration(seconds: 2),
                  ),
                );
              }
            },
          ),
        ],
      ),
    );
  }
```
- **Checklist:**
  - [x] Microscope toggle switch in Settings: **PASS**
  - [x] Clear explanatory text informing user about localhost desktop agent: **PASS**

---

### File 8: `numista_mobile/lib/screens/microscope_scan_screen.dart`

#### Cite: `numista_mobile/lib/screens/microscope_scan_screen.dart:78-85`
**Verbatim Code:**
```dart
    final configured = await HardwareService.isMicroscopeConfigured();
    if (!mounted) return;
    setState(() => _microscopeConfigured = configured);
    if (!configured) {
      setState(() => _serverOnline = false);
      return;
    }
```
- **Checklist:**
  - [x] Bypasses polling when microscope not enabled: **PASS**

---

### File 9: `numista_mobile/lib/widgets/auth_gate.dart`

#### Cite: `numista_mobile/lib/widgets/auth_gate.dart:62`
**Verbatim Code:**
```dart
  static bool _welcomeDone = false;
```
- **Checklist:**
  - [x] Preserves welcome state across widget rebuilds: **PASS**

---

### File 10: `numista_mobile/lib/services/backup_export_service.dart`

#### Cite: `numista_mobile/lib/services/backup_export_service.dart:28, 134`
**Verbatim Code:**
```dart
        'app_version': kAppVersion.replaceFirst('v', ''),
```
- **Checklist:**
  - [x] Dynamic app version alignment without hardcoding: **PASS**

---

### File 11: `numista_mobile/test/p7_v8_ux_safety_test.dart`

#### Cite: `numista_mobile/test/p7_v8_ux_safety_test.dart:1874-1921`
**Verbatim Code:**
```dart
    test('p7_v818_buildAddCoinsHtmlPath_live_and_custom_api', () {
      const email = 'user@example.com';
      // Default / live backend -> no &api= param
      final livePath = buildAddCoinsHtmlPath(email);
      expect(livePath, equals('/add_coins.html?email=user%40example.com'));

      // Explicit live backend -> no &api= param
      final explicitLivePath = buildAddCoinsHtmlPath(
        email,
        apiBase: 'https://numista-backend-568985927038.us-central1.run.app',
      );
      expect(explicitLivePath, equals('/add_coins.html?email=user%40example.com'));

      // Preview / custom backend -> &api= param included
      const customApi = 'https://numista-backend-preview-568985927038.us-central1.run.app';
      final customPath = buildAddCoinsHtmlPath(email, apiBase: customApi);
      expect(
        customPath,
        equals('/add_coins.html?email=user%40example.com&api=https%3A%2F%2Fnumista-backend-preview-568985927038.us-central1.run.app'),
      );
    });

    test('p7_v818_microscope_guard_no_localhost_when_disabled', () async {
      SharedPreferences.setMockInitialValues({'microscope_enabled': false});

      final configured = await HardwareService.isMicroscopeConfigured();
      expect(configured, isFalse);

      final hw = HardwareService();

      // Guarded methods must return null / false / empty without making network calls
      final status = await hw.getStatus();
      expect(status, isNull);

      final running = await hw.isServerRunning();
      expect(running, isFalse);

      final cameras = await hw.listCameras();
      expect(cameras['cameras'], isEmpty);

      final frame = await hw.fetchFrame();
      expect(frame, isNull);

      // Now enable and verify
      await HardwareService.setMicroscopeConfigured(true);
      final configuredNow = await HardwareService.isMicroscopeConfigured();
      expect(configuredNow, isTrue);
    });
```
- **Checklist:**
  - [x] Unit test for path and API passthrough: **PASS**
  - [x] Unit test for microscope localhost guard: **PASS**

---

## 3. Final Verdict

**FINAL VERDICT: PASS**

The build strictly satisfies all safety, lint, test, and UX criteria. No Firestore writes or unauthenticated network leaks occur. All 583 automated tests and HTML validation scripts pass with 0 warnings and 0 errors. Commit `1137b7324bc4f77862a30bc53488afd103fbac2e` on branch `p7-v8.9` is certified ready for deployment.
