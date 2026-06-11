import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../services/morgan_prefs.dart';

/// One-time dialog where Morgan learns the user's preferred name.
///
/// Shown ONCE: right after the first action tile tap, before navigating
/// to any guided flow.  After completion, [MorganPrefs.isSetupDone] is true
/// and this dialog is never shown again.
///
/// Usage:
/// ```dart
/// final confirmed = await showMorganSetup(context);
/// if (confirmed) { /* proceed */ }
/// ```
Future<bool> showMorganSetup(BuildContext context) {
  return showGeneralDialog<bool>(
    context: context,
    barrierDismissible: false,
    barrierColor: Colors.black87,
    transitionDuration: const Duration(milliseconds: 350),
    transitionBuilder: (ctx, anim, secondaryAnim, child) => FadeTransition(
      opacity: anim,
      child: ScaleTransition(
        scale: Tween<double>(begin: 0.92, end: 1.0)
            .animate(CurvedAnimation(parent: anim, curve: Curves.easeOutBack)),
        child: child,
      ),
    ),
    pageBuilder: (ctx, animation, secondaryAnimation) =>
        const _MorganSetupDialog(),
  ).then((v) => v ?? false);
}

// ── Internal dialog widget ─────────────────────────────────────────────────────
class _MorganSetupDialog extends StatefulWidget {
  const _MorganSetupDialog();

  @override
  State<_MorganSetupDialog> createState() => _MorganSetupDialogState();
}

class _MorganSetupDialogState extends State<_MorganSetupDialog> {
  // 0 = ask name screen, 1 = confirmation screen
  int _screen = 0;
  final _ctrl = TextEditingController();
  final _focus = FocusNode();
  String _saved = '';

  // Colours (same palette as MorganGreeter)
  static const _bg   = Color(0xFF0B1220);
  static const _surf = Color(0xFF162033);
  static const _teal = Color(0xFF2DD4BF);
  static const _gold = Color(0xFFD4A843);
  static const _sub  = Color(0xFF94A3B8);

  @override
  void initState() {
    super.initState();
    // Pre-fill with the account first name as a helpful default
    final user = FirebaseAuth.instance.currentUser;
    final raw = user?.displayName?.trim().isNotEmpty == true
        ? user!.displayName!.trim()
        : (user?.email?.split('@').first ?? '');
    _ctrl.text = raw.split(' ').first;
    _ctrl.selection =
        TextSelection(baseOffset: 0, extentOffset: _ctrl.text.length);
  }

  @override
  void dispose() {
    _ctrl.dispose();
    _focus.dispose();
    super.dispose();
  }

  // ── Quick-pick name chips ─────────────────────────────────────────────────
  List<String> get _chips {
    final user = FirebaseAuth.instance.currentUser;
    final first = (user?.displayName?.split(' ').first ??
            user?.email?.split('@').first ??
            '')
        .trim();
    return [
      if (first.isNotEmpty) first,
      'Sir',
      'Ma\'am',
      'Skip',
    ];
  }

  void _pickChip(String chip) {
    if (chip == 'Skip') {
      _ctrl.text = '';
    } else {
      _ctrl.text = chip;
    }
    _ctrl.selection =
        TextSelection(baseOffset: 0, extentOffset: _ctrl.text.length);
    _focus.requestFocus();
  }

  Future<void> _confirm() async {
    final name = _ctrl.text.trim();
    _saved = name;
    if (name.isNotEmpty) await MorganPrefs.setPreferredName(name);
    await MorganPrefs.markSetupDone();
    setState(() => _screen = 1);
  }

  // ── Build ─────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 480),
          child: Container(
            margin: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: _bg,
              borderRadius: BorderRadius.circular(24),
              border: Border.all(color: _gold.withAlpha(60), width: 1.5),
              boxShadow: [
                BoxShadow(
                    color: _teal.withAlpha(30),
                    blurRadius: 40,
                    spreadRadius: 2),
              ],
            ),
            child: AnimatedSwitcher(
              duration: const Duration(milliseconds: 350),
              transitionBuilder: (child, anim) => FadeTransition(
                opacity: anim,
                child: SlideTransition(
                  position: Tween<Offset>(
                    begin: const Offset(0.1, 0),
                    end: Offset.zero,
                  ).animate(anim),
                  child: child,
                ),
              ),
              child: _screen == 0
                  ? _buildNameScreen()
                  : _buildConfirmScreen(),
            ),
          ),
        ),
      ),
    );
  }

  // ── Screen 1: Ask name ────────────────────────────────────────────────────
  Widget _buildNameScreen() {
    return Padding(
      key: const ValueKey('name'),
      padding: const EdgeInsets.all(28),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Morgan avatar (small)
          _SmallOwl(),
          const SizedBox(height: 20),

          // Question
          const Text(
            'Before we get started —',
            style: TextStyle(color: _sub, fontSize: 15),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 6),
          const Text(
            'What should I call you?',
            style: TextStyle(
                color: Colors.white,
                fontSize: 24,
                fontWeight: FontWeight.bold,
                letterSpacing: -0.3),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          const Text(
            'You can say "Eric", "Sir", "Grandpa" —\nwhatever feels right to you!',
            style: TextStyle(color: _sub, fontSize: 14, height: 1.5),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 24),

          // Name field
          Container(
            decoration: BoxDecoration(
              color: _surf,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: _teal.withAlpha(80), width: 1.5),
            ),
            child: TextField(
              controller: _ctrl,
              focusNode: _focus,
              autofocus: true,
              style: const TextStyle(
                  color: Colors.white,
                  fontSize: 20,
                  fontWeight: FontWeight.w500),
              textCapitalization: TextCapitalization.words,
              textAlign: TextAlign.center,
              decoration: const InputDecoration(
                hintText: 'Type your name here…',
                hintStyle: TextStyle(color: _sub, fontSize: 16),
                border: InputBorder.none,
                contentPadding:
                    EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              ),
            ),
          ),
          const SizedBox(height: 14),

          // Quick-pick chips
          Wrap(
            spacing: 8,
            runSpacing: 8,
            alignment: WrapAlignment.center,
            children: _chips.map((chip) {
              return GestureDetector(
                onTap: () => _pickChip(chip),
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: chip == 'Skip'
                        ? Colors.transparent
                        : _surf,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: chip == 'Skip'
                          ? _sub.withAlpha(80)
                          : _teal.withAlpha(100),
                    ),
                  ),
                  child: Text(
                    chip,
                    style: TextStyle(
                      color: chip == 'Skip' ? _sub : _teal,
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 28),

          // Confirm button
          SizedBox(
            width: double.infinity,
            height: 56,
            child: ElevatedButton(
              onPressed: _confirm,
              style: ElevatedButton.styleFrom(
                backgroundColor: _teal,
                foregroundColor: Colors.black87,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14)),
                elevation: 0,
              ),
              child: const Text(
                "That's me! →",
                style: TextStyle(
                    fontSize: 17, fontWeight: FontWeight.bold),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Screen 2: Confirmation ────────────────────────────────────────────────
  Widget _buildConfirmScreen() {
    final name = _saved.isEmpty ? '' : ', $_saved';
    return Padding(
      key: const ValueKey('confirm'),
      padding: const EdgeInsets.all(28),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          _SmallOwl(),
          const SizedBox(height: 24),

          Text(
            'Perfect$name! 😊',
            style: const TextStyle(
                color: Colors.white,
                fontSize: 26,
                fontWeight: FontWeight.bold),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12),
          Text(
            _saved.isEmpty
                ? "I'll take you through this one step at a time.\nYou can ask me anything, any time."
                : "I'll call you $_saved from now on.\nI'll take you through this one step at a time.",
            style:
                const TextStyle(color: _sub, fontSize: 16, height: 1.6),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 32),

          SizedBox(
            width: double.infinity,
            height: 56,
            child: ElevatedButton(
              onPressed: () => Navigator.of(context).pop(true),
              style: ElevatedButton.styleFrom(
                backgroundColor: _teal,
                foregroundColor: Colors.black87,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14)),
                elevation: 0,
              ),
              child: const Text(
                "Let's go! →",
                style: TextStyle(
                    fontSize: 17, fontWeight: FontWeight.bold),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ── Small owl avatar used inside setup dialog ─────────────────────────────────
class _SmallOwl extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 80,
      height: 80,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: const LinearGradient(
          colors: [Color(0xFFD4A843), Color(0xFF8B6914)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        boxShadow: [
          BoxShadow(
              color: const Color(0xFFD4A843).withAlpha(60),
              blurRadius: 12,
              spreadRadius: 1),
        ],
      ),
      child: ClipOval(
        child: Image.asset(
          'assets/morgan_avatar.png',
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) => const Icon(
              Icons.smart_toy_rounded,
              color: Color(0xFF2DD4BF),
              size: 36),
        ),
      ),
    );
  }
}
