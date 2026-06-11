import 'package:flutter/material.dart';
import '../services/morgan_prefs.dart';
import '../services/morgan_chat_context.dart';

// ══════════════════════════════════════════════════════════════════════════════
//  MorganSettingsPanel
//  ───────────────────
//  A bottom-sheet settings panel for Morgan's behaviour.
//  Accessible from the header in AiChatScreen and from the app settings.
//
//  Settings available:
//    • Preferred name (edit)
//    • Show Morgan on startup  (toggle)
//    • Voice narration         (toggle — Phase 4 placeholder)
//    • Reset / forget name
// ══════════════════════════════════════════════════════════════════════════════

/// Show the Morgan settings panel as a bottom sheet.
/// Returns true if any settings were changed (so callers can rebuild).
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
  // ── Colours ────────────────────────────────────────────────────────────────
  static const _bg   = Color(0xFF0B1220);
  static const _surf = Color(0xFF162033);
  static const _teal = Color(0xFF2DD4BF);
  static const _gold = Color(0xFFD4A843);
  static const _sub  = Color(0xFF94A3B8);
  static const _red  = Color(0xFFEF4444);

  // ── State ──────────────────────────────────────────────────────────────────
  bool _loaded        = false;
  bool _showOnStartup = true;
  bool _voiceEnabled  = false;
  String _currentName = '';
  bool _changed       = false;

  final _nameCtrl  = TextEditingController();
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
    final name    = await MorganPrefs.getPreferredName() ?? '';
    final startup = await MorganPrefs.showOnStartup();
    final voice   = await MorganPrefs.isVoiceEnabled();
    setState(() {
      _currentName    = name;
      _showOnStartup  = startup;
      _voiceEnabled   = voice;
      _nameCtrl.text  = name;
      _loaded         = true;
    });
  }

  Future<void> _saveName() async {
    final name = _nameCtrl.text.trim();
    if (name == _currentName) return;
    await MorganPrefs.setPreferredName(name);
    _currentName = name;
    // Invalidate collection context so opening message regenerates with new name
    MorganChatContextService.invalidate();
    setState(() => _changed = true);
    _nameFocus.unfocus();
    _showSnack('Name updated to "$name" 👋');
  }

  Future<void> _setStartup(bool value) async {
    await MorganPrefs.setShowOnStartup(value);
    setState(() {
      _showOnStartup = value;
      _changed = true;
    });
  }

  Future<void> _setVoice(bool value) async {
    await MorganPrefs.setVoiceEnabled(value);
    setState(() {
      _voiceEnabled = value;
      _changed = true;
    });
  }

  Future<void> _resetName() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: _surf,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        title: const Text('Reset name?',
            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        content: const Text(
          'Morgan will ask your name again next time.',
          style: TextStyle(color: _sub, fontSize: 14),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel', style: TextStyle(color: _sub)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
                backgroundColor: _red, foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8))),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Reset'),
          ),
        ],
      ),
    );
    if (confirm == true) {
      await MorganPrefs.clearAll();
      setState(() {
        _currentName = '';
        _nameCtrl.text = '';
        _showOnStartup = true;
        _voiceEnabled = false;
        _changed = true;
      });
      _showSnack('Morgan settings reset ✓');
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
          border: Border(top: BorderSide(color: _gold.withAlpha(50), width: 1.5)),
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
    child: Center(child: CircularProgressIndicator(color: Color(0xFF2DD4BF))),
  );

  Widget _buildContent() {
    return Padding(
      padding: EdgeInsets.only(
        left: 20, right: 20, top: 4,
        bottom: MediaQuery.of(context).viewInsets.bottom + 16,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // ── Drag handle ────────────────────────────────────────────────
          Center(
            child: Container(
              width: 36, height: 4,
              margin: const EdgeInsets.symmetric(vertical: 12),
              decoration: BoxDecoration(
                color: _sub.withAlpha(80),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),

          // ── Title ──────────────────────────────────────────────────────
          Row(
            children: [
              Container(
                width: 36, height: 36,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: LinearGradient(
                    colors: [Color(0xFFD4A843), Color(0xFF8B6914)],
                  ),
                ),
                child: ClipOval(
                  child: Image.asset(
                    'assets/morgan_avatar.png',
                    fit: BoxFit.cover,
                    errorBuilder: (ctx, err, stack) => const Icon(
                        Icons.smart_toy_rounded, color: Colors.white, size: 18),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Morgan Settings',
                      style: TextStyle(
                          color: Colors.white,
                          fontSize: 18,
                          fontWeight: FontWeight.bold)),
                  Text('Personalise your AI guide',
                      style: TextStyle(color: _sub, fontSize: 12)),
                ],
              ),
              const Spacer(),
              // Done button
              GestureDetector(
                onTap: () => Navigator.pop(context, _changed),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
                  decoration: BoxDecoration(
                    color: _teal,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: const Text('Done',
                      style: TextStyle(
                          color: Colors.black87,
                          fontWeight: FontWeight.bold,
                          fontSize: 13)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),

          // ── Name field ─────────────────────────────────────────────────
          _sectionLabel('Your preferred name'),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: _surf,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: _teal.withAlpha(70), width: 1.5),
                  ),
                  child: TextField(
                    controller: _nameCtrl,
                    focusNode: _nameFocus,
                    style: const TextStyle(
                        color: Colors.white,
                        fontSize: 17,
                        fontWeight: FontWeight.w500),
                    textCapitalization: TextCapitalization.words,
                    decoration: InputDecoration(
                      hintText: 'How should Morgan address you?',
                      hintStyle: TextStyle(color: _sub.withAlpha(140), fontSize: 14),
                      border: InputBorder.none,
                      contentPadding: const EdgeInsets.symmetric(
                          horizontal: 16, vertical: 13),
                    ),
                    onSubmitted: (_) => _saveName(),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              GestureDetector(
                onTap: _saveName,
                child: Container(
                  height: 48,
                  width: 48,
                  decoration: BoxDecoration(
                    color: _teal,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.check_rounded,
                      color: Colors.black87, size: 22),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            'Morgan will call you this in every conversation.',
            style: TextStyle(color: _sub.withAlpha(160), fontSize: 12),
          ),
          const SizedBox(height: 20),

          // ── Toggle: Show on startup ────────────────────────────────────
          _sectionLabel('Behaviour'),
          const SizedBox(height: 8),
          _toggleRow(
            icon: Icons.waving_hand_rounded,
            iconColor: _gold,
            title: 'Greet me when I log in',
            subtitle: 'Morgan appears every time you open the app',
            value: _showOnStartup,
            onChanged: _setStartup,
          ),
          const SizedBox(height: 8),
          _toggleRow(
            icon: Icons.record_voice_over_rounded,
            iconColor: _teal,
            title: 'Voice narration',
            subtitle: 'Morgan reads instructions aloud (coming soon)',
            value: _voiceEnabled,
            onChanged: _setVoice,
            disabled: true,   // Phase 4 — not yet implemented
          ),
          const SizedBox(height: 24),

          // ── Danger zone ────────────────────────────────────────────────
          GestureDetector(
            onTap: _resetName,
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 13),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: _red.withAlpha(80), width: 1.5),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.restart_alt_rounded,
                      color: _red.withAlpha(200), size: 18),
                  const SizedBox(width: 8),
                  Text('Reset Morgan settings',
                      style: TextStyle(
                          color: _red.withAlpha(200),
                          fontSize: 14,
                          fontWeight: FontWeight.w500)),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),
        ],
      ),
    );
  }

  Widget _sectionLabel(String label) => Text(
    label.toUpperCase(),
    style: TextStyle(
        color: _sub.withAlpha(180),
        fontSize: 10,
        fontWeight: FontWeight.w700,
        letterSpacing: 0.8),
  );

  Widget _toggleRow({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
    bool disabled = false,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: _surf,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withAlpha(15)),
      ),
      child: Row(
        children: [
          Container(
            width: 36, height: 36,
            decoration: BoxDecoration(
              color: iconColor.withAlpha(25),
              borderRadius: BorderRadius.circular(9),
            ),
            child: Icon(icon, color: disabled ? _sub : iconColor, size: 18),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: TextStyle(
                        color: disabled ? _sub : Colors.white,
                        fontSize: 14,
                        fontWeight: FontWeight.w500)),
                const SizedBox(height: 2),
                Text(subtitle,
                    style: const TextStyle(color: _sub, fontSize: 12)),
              ],
            ),
          ),
          Switch(
            value: value,
            onChanged: disabled ? null : onChanged,
            activeThumbColor: _teal,
            activeTrackColor: _teal.withAlpha(60),
            inactiveThumbColor: _sub,
            inactiveTrackColor: _surf,
          ),
        ],
      ),
    );
  }
}
