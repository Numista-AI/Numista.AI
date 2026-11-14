import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/morgan_action_bus.dart';
import '../services/morgan_chat_context.dart';
import '../services/morgan_prefs.dart';
import '../services/morgan_screen_state_registry.dart';
import '../services/stt_voice_service.dart';
import '../services/tts_voice_service.dart';

/// Persists Morgan Co-Pilot privacy, voice, vision, dock, and reduced-motion preferences (§10).
class MorganSettingsService extends ChangeNotifier {
  static final MorganSettingsService instance = MorganSettingsService._();
  MorganSettingsService._();

  static const String _prefConsentDecided = 'morgan_consent_decided';
  static const String _prefAllowVision = 'morgan_allow_vision_rescue';
  static const String _prefAllowMic = 'morgan_allow_voice_mic';
  static const String _prefAllowTts = 'morgan_allow_voice_tts';
  static const String _prefReduceMotion = 'morgan_reduce_motion';
  static const String _prefDockToSide = 'morgan_dock_to_side';

  bool _loaded = false;
  bool consentDecided = false;
  bool allowVisionRescue = true;
  bool allowVoiceMic = true;
  bool allowVoiceTts = true;
  bool reduceMotion = false;
  bool dockToSide = true;

  Future<void> load() async {
    if (_loaded) return;
    final prefs = await SharedPreferences.getInstance();
    consentDecided = prefs.getBool(_prefConsentDecided) ?? false;
    allowVisionRescue = prefs.getBool(_prefAllowVision) ?? true;
    allowVoiceMic = prefs.getBool(_prefAllowMic) ?? true;
    allowVoiceTts = prefs.getBool(_prefAllowTts) ?? true;
    reduceMotion = prefs.getBool(_prefReduceMotion) ?? false;
    dockToSide = prefs.getBool(_prefDockToSide) ?? true;
    _loaded = true;
    _syncServices();
    notifyListeners();
  }

  void _syncServices() {
    MorganScreenStateRegistry.instance.allowVisionCapture = allowVisionRescue;
    MorganScreenStateRegistry.instance.visionConsentAccepted =
        !consentDecided || allowVisionRescue;
    MorganActionBus.instance.reducedMotionEnabled = reduceMotion;
    SttVoiceService.instance.micAllowed = allowVoiceMic;
    if (!allowVoiceTts) {
      TtsVoiceService.stop();
    }
  }

  Future<void> acceptFullCopilotConsent() async {
    final prefs = await SharedPreferences.getInstance();
    consentDecided = true;
    allowVisionRescue = true;
    allowVoiceMic = true;
    allowVoiceTts = true;
    await prefs.setBool(_prefConsentDecided, true);
    await prefs.setBool(_prefAllowVision, true);
    await prefs.setBool(_prefAllowMic, true);
    await prefs.setBool(_prefAllowTts, true);
    _syncServices();
    notifyListeners();
  }

  Future<void> chooseTextOnlyConsent() async {
    final prefs = await SharedPreferences.getInstance();
    consentDecided = true;
    allowVisionRescue = false;
    allowVoiceMic = false;
    await prefs.setBool(_prefConsentDecided, true);
    await prefs.setBool(_prefAllowVision, false);
    await prefs.setBool(_prefAllowMic, false);
    _syncServices();
    notifyListeners();
  }

  Future<void> setAllowVisionRescue(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    allowVisionRescue = value;
    await prefs.setBool(_prefAllowVision, value);
    _syncServices();
    notifyListeners();
  }

  Future<void> setAllowVoiceMic(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    allowVoiceMic = value;
    await prefs.setBool(_prefAllowMic, value);
    _syncServices();
    notifyListeners();
  }

  Future<void> setAllowVoiceTts(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    allowVoiceTts = value;
    await prefs.setBool(_prefAllowTts, value);
    _syncServices();
    notifyListeners();
  }

  Future<void> setReduceMotion(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    reduceMotion = value;
    await prefs.setBool(_prefReduceMotion, value);
    _syncServices();
    notifyListeners();
  }

  Future<void> setDockToSide(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    dockToSide = value;
    await prefs.setBool(_prefDockToSide, value);
    notifyListeners();
  }

  @visibleForTesting
  void resetForTesting() {
    _loaded = false;
    consentDecided = false;
    allowVisionRescue = true;
    allowVoiceMic = true;
    allowVoiceTts = true;
    reduceMotion = false;
    dockToSide = true;
    _syncServices();
    notifyListeners();
  }
}

/// Shows the Senior-Friendly First-Use Consent Modal if the user has not
/// chosen Co-Pilot vs Text-Only mode yet (§10).
Future<void> showMorganConsentModalIfNeeded(BuildContext context) async {
  final settings = MorganSettingsService.instance;
  await settings.load();
  if (settings.consentDecided || !context.mounted) return;

  await showDialog<void>(
    context: context,
    barrierDismissible: false,
    builder: (ctx) {
      return FocusTraversalGroup(
        policy: OrderedTraversalPolicy(),
        child: AlertDialog(
          backgroundColor: const Color(0xFFFFFFFF),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(18),
            side: const BorderSide(color: Color(0xFF0F172A), width: 2),
          ),
          title: const Text(
            '🦉 How Morgan Helps You',
            style: TextStyle(
              color: Color(0xFF0F172A),
              fontSize: 22,
              fontWeight: FontWeight.bold,
            ),
          ),
          content: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 460),
            child: const Text(
              'Morgan can read which screen you are on and listen to your voice '
              'so she can click buttons and guide you hands-free. Your collection '
              'stays private to your account, and sensitive pages (Estate Planning '
              '& Transfer PINs) are never photographed. You can turn Screen Vision '
              'or Voice on or off anytime in Settings.',
              style: TextStyle(
                color: Color(0xFF1E293B),
                fontSize: 16,
                height: 1.5,
              ),
            ),
          ),
          actionsAlignment: MainAxisAlignment.spaceBetween,
          actionsPadding: const EdgeInsets.fromLTRB(20, 8, 20, 20),
          actions: [
            Semantics(
              identifier: 'morgan_consent_textonly_btn',
              button: true,
              label: 'Use Text-Only Mode',
              child: ConstrainedBox(
                constraints: const BoxConstraints(minHeight: 56),
                child: OutlinedButton(
                  onPressed: () async {
                    await settings.chooseTextOnlyConsent();
                    if (ctx.mounted) Navigator.of(ctx).pop();
                  },
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF0F172A),
                    side: const BorderSide(color: Color(0xFF0F172A), width: 2),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 18, vertical: 14),
                    textStyle: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  child: const Text('Use Text-Only Mode'),
                ),
              ),
            ),
            Semantics(
              identifier: 'morgan_consent_enable_btn',
              button: true,
              label: 'Turn On Morgan Co-Pilot',
              child: ConstrainedBox(
                constraints: const BoxConstraints(minHeight: 56),
                child: ElevatedButton(
                  autofocus: true,
                  onPressed: () async {
                    await settings.acceptFullCopilotConsent();
                    if (ctx.mounted) Navigator.of(ctx).pop();
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF14532D),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                        horizontal: 20, vertical: 14),
                    textStyle: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  child: const Text('✓ Turn On Morgan Co-Pilot'),
                ),
              ),
            ),
          ],
        ),
      );
    },
  );
}

/// Accessible settings controls for Morgan Vision, Voice, TTS & Reduced Motion (§7.8 & §10).
class MorganSettingsPanel extends StatelessWidget {
  const MorganSettingsPanel({super.key});

  @override
  Widget build(BuildContext context) {
    final settings = MorganSettingsService.instance;
    return ListenableBuilder(
      listenable: settings,
      builder: (context, _) {
        return FocusTraversalGroup(
          policy: OrderedTraversalPolicy(),
          child: Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: const Color(0xFFCBD5E1), width: 1.5),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text(
                  'Morgan Comfort & Privacy Controls',
                  style: TextStyle(
                    color: Color(0xFF0F172A),
                    fontSize: 17,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                _SettingRow(
                  identifier: 'morgan_setting_vision',
                  label: 'Allow Morgan to see my screen (Vision Rescue)',
                  value: settings.allowVisionRescue,
                  onChanged: settings.setAllowVisionRescue,
                ),
                _SettingRow(
                  identifier: 'morgan_setting_mic',
                  label: 'Allow Morgan to hear me (Voice Microphone)',
                  value: settings.allowVoiceMic,
                  onChanged: settings.setAllowVoiceMic,
                ),
                _SettingRow(
                  identifier: 'morgan_setting_tts',
                  label: 'Allow Morgan to speak aloud (Voice Speaker)',
                  value: settings.allowVoiceTts,
                  onChanged: settings.setAllowVoiceTts,
                ),
                _SettingRow(
                  identifier: 'morgan_setting_reduced_motion',
                  label: 'Reduce motion & flashing',
                  value: settings.reduceMotion,
                  onChanged: settings.setReduceMotion,
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _SettingRow extends StatelessWidget {
  final String identifier;
  final String label;
  final bool value;
  final ValueChanged<bool> onChanged;

  const _SettingRow({
    required this.identifier,
    required this.label,
    required this.value,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      identifier: identifier,
      toggled: value,
      label: label,
      child: ConstrainedBox(
        constraints: const BoxConstraints(minHeight: 56),
        child: SwitchListTile(
          contentPadding: const EdgeInsets.symmetric(horizontal: 4),
          title: Text(
            label,
            style: const TextStyle(
              color: Color(0xFF1E293B),
              fontSize: 16,
              fontWeight: FontWeight.w500,
              height: 1.35,
            ),
          ),
          value: value,
          activeThumbColor: const Color(0xFF14532D),
          onChanged: onChanged,
        ),
      ),
    );
  }
}

/// Shows the Morgan personalisation & behaviour sheet (restored for callers).
Future<bool> showMorganSettings(BuildContext context) async {
  final changed = await showModalBottomSheet<bool>(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (_) => const _MorganSettingsSheet(),
  );
  return changed ?? false;
}

class _MorganSettingsSheet extends StatefulWidget {
  const _MorganSettingsSheet();

  @override
  State<_MorganSettingsSheet> createState() => _MorganSettingsSheetState();
}

class _MorganSettingsSheetState extends State<_MorganSettingsSheet> {
  Color get _bg => Theme.of(context).brightness == Brightness.dark
      ? const Color(0xFF0B1220)
      : const Color(0xFFF4F4F2);
  Color get _surf => Theme.of(context).brightness == Brightness.dark
      ? const Color(0xFF162033)
      : Colors.white;
  static const _teal = Color(0xFF2DD4BF);
  static const _gold = Color(0xFFD4A843);
  Color get _sub => Theme.of(context).brightness == Brightness.dark
      ? const Color(0xFF94A3B8)
      : const Color(0xFF5A5C69);
  Color get _text => Theme.of(context).brightness == Brightness.dark
      ? Colors.white
      : const Color(0xFF0F172A);
  static const _red = Color(0xFFEF4444);

  bool _loaded = false;
  bool _showOnStartup = true;
  String _currentName = '';
  bool _changed = false;

  final _nameCtrl = TextEditingController();
  final _nameFocus = FocusNode();

  @override
  void initState() {
    super.initState();
    _loadPrefs();
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    _nameFocus.dispose();
    super.dispose();
  }

  Future<void> _loadPrefs() async {
    final name = await MorganPrefs.getPreferredName() ?? '';
    final startup = await MorganPrefs.showOnStartup();
    await MorganSettingsService.instance.load();
    if (!mounted) return;
    setState(() {
      _currentName = name;
      _showOnStartup = startup;
      _nameCtrl.text = name;
      _loaded = true;
    });
  }

  Future<void> _saveName() async {
    final name = _nameCtrl.text.trim();
    if (name == _currentName) return;
    await MorganPrefs.setPreferredName(name);
    _currentName = name;
    MorganChatContextService.invalidate();
    setState(() => _changed = true);
    _nameFocus.unfocus();
    _showSnack('Name updated to "$name"');
  }

  Future<void> _setStartup(bool value) async {
    await MorganPrefs.setShowOnStartup(value);
    setState(() {
      _showOnStartup = value;
      _changed = true;
    });
  }

  Future<void> _resetName() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: _surf,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        title: Text(
          'Reset name?',
          style: TextStyle(color: _text, fontWeight: FontWeight.bold),
        ),
        content: Text(
          'Morgan will ask your name again next time.',
          style: TextStyle(color: _sub, fontSize: 16),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text('Cancel', style: TextStyle(color: _sub)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: _red,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8)),
            ),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Reset'),
          ),
        ],
      ),
    );
    if (confirm == true) {
      await MorganPrefs.clearAll();
      if (!mounted) return;
      setState(() {
        _currentName = '';
        _nameCtrl.text = '';
        _showOnStartup = true;
        _changed = true;
      });
      _showSnack('Morgan settings reset');
    }
  }

  void _showSnack(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(msg),
        backgroundColor: _surf,
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => _nameFocus.unfocus(),
      child: Container(
        decoration: BoxDecoration(
          color: _bg,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
          border:
              Border(top: BorderSide(color: _gold.withAlpha(50), width: 1.5)),
        ),
        child: SafeArea(
          top: false,
          child: _loaded ? _buildContent() : _buildLoading(),
        ),
      ),
    );
  }

  Widget _buildLoading() => const Padding(
        padding: EdgeInsets.all(40),
        child: Center(
            child: CircularProgressIndicator(color: Color(0xFF2DD4BF))),
      );

  Widget _buildContent() {
    return SingleChildScrollView(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 4,
        bottom: MediaQuery.of(context).viewInsets.bottom + 16,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Center(
            child: Container(
              width: 36,
              height: 4,
              margin: const EdgeInsets.symmetric(vertical: 12),
              decoration: BoxDecoration(
                color: _sub.withAlpha(80),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          Row(
            children: [
              Text(
                'Morgan Settings',
                style: TextStyle(
                    color: _text, fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const Spacer(),
              TextButton(
                onPressed: () => Navigator.pop(context, _changed),
                child: const Text('Done',
                    style: TextStyle(
                        color: _teal,
                        fontWeight: FontWeight.bold,
                        fontSize: 16)),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _nameCtrl,
                  focusNode: _nameFocus,
                  style: TextStyle(color: _text, fontSize: 16),
                  textCapitalization: TextCapitalization.words,
                  decoration: InputDecoration(
                    hintText: 'How should Morgan address you?',
                    filled: true,
                    fillColor: _surf,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  onSubmitted: (_) => _saveName(),
                ),
              ),
              const SizedBox(width: 8),
              ElevatedButton(
                onPressed: _saveName,
                style: ElevatedButton.styleFrom(
                  backgroundColor: _teal,
                  foregroundColor: Colors.black87,
                  minimumSize: const Size(56, 52),
                ),
                child: const Icon(Icons.check_rounded),
              ),
            ],
          ),
          const SizedBox(height: 12),
          SwitchListTile(
            title: Text('Greet me when I log in',
                style: TextStyle(color: _text, fontSize: 16)),
            value: _showOnStartup,
            activeThumbColor: _teal,
            onChanged: _setStartup,
          ),
          const SizedBox(height: 8),
          const MorganSettingsPanel(),
          const SizedBox(height: 16),
          TextButton.icon(
            onPressed: _resetName,
            icon: const Icon(Icons.restart_alt_rounded, color: _red),
            label: const Text('Reset Morgan settings',
                style: TextStyle(color: _red, fontSize: 15)),
          ),
        ],
      ),
    );
  }
}
