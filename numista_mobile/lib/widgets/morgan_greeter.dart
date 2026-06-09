import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Morgan — Numista.AI's AI concierge greeter.
///
/// Shown to new users (empty collection) on first login.
/// Can also be recalled at any time via the Morgan FAB button in BaseLayout.
///
/// Displays Morgan's avatar, a personal greeting, and 4 large plain-English
/// action tiles that route to the key app features.
class MorganGreeter extends StatefulWidget {
  /// Called when the user picks an action tile or dismisses Morgan.
  /// [route] is the BaseLayout route string to navigate to,
  /// or null if the user tapped "Browse on my own".
  final void Function(String? route) onAction;

  /// Whether this is the very first time the user has seen Morgan.
  /// Affects the greeting message slightly.
  final bool isFirstVisit;

  const MorganGreeter({
    super.key,
    required this.onAction,
    this.isFirstVisit = true,
  });

  static const String _prefKey = 'morgan_greeter_seen';

  static Future<bool> shouldShow() async {
    final prefs = await SharedPreferences.getInstance();
    return !(prefs.getBool(_prefKey) ?? false);
  }

  static Future<void> markSeen() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_prefKey, true);
  }

  @override
  State<MorganGreeter> createState() => _MorganGreeterState();
}

class _MorganGreeterState extends State<MorganGreeter>
    with TickerProviderStateMixin {

  // ── Animation controllers ───────────────────────────────────────────────────
  late final AnimationController _fadeCtrl;
  late final AnimationController _bobCtrl;
  late final AnimationController _tilesCtrl;

  late final Animation<double> _fadeAnim;
  late final Animation<double> _bobAnim;
  late final Animation<double> _tilesAnim;

  // ── Colours ─────────────────────────────────────────────────────────────────
  static const _bg      = Color(0xFF0B1220);   // deep navy
  static const _teal    = Color(0xFF2DD4BF);   // teal accent (matches logo eyes)
  static const _text    = Colors.white;
  static const _sub     = Color(0xFF94A3B8);

  @override
  void initState() {
    super.initState();

    // Overall fade-in
    _fadeCtrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 600));
    _fadeAnim = CurvedAnimation(parent: _fadeCtrl, curve: Curves.easeOut);

    // Gentle avatar bob: up 4px → down 4px → repeat
    _bobCtrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 2800));
    _bobAnim = Tween<double>(begin: -4, end: 4).animate(
        CurvedAnimation(parent: _bobCtrl, curve: Curves.easeInOut));
    _bobCtrl.repeat(reverse: true);

    // Staggered tile slide-up
    _tilesCtrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 500));
    _tilesAnim = CurvedAnimation(parent: _tilesCtrl, curve: Curves.easeOut);

    // Start animations in sequence
    _fadeCtrl.forward().then((_) => _tilesCtrl.forward());
  }

  @override
  void dispose() {
    _fadeCtrl.dispose();
    _bobCtrl.dispose();
    _tilesCtrl.dispose();
    super.dispose();
  }

  // ── Greeting copy ───────────────────────────────────────────────────────────
  String get _firstName {
    final user = FirebaseAuth.instance.currentUser;
    final name = user?.displayName ?? user?.email?.split('@').first ?? 'there';
    // Return just first name if display name has spaces
    return name.split(' ').first;
  }

  String get _greeting {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  }

  String get _headlineText => widget.isFirstVisit
      ? '$_greeting, $_firstName! 👋\nWelcome to Numista.AI!'
      : '$_greeting, $_firstName! 👋\nWhat would you like to do today?';

  String get _subText => widget.isFirstVisit
      ? "I'm Morgan, your personal numismatic guide.\nWhat would you like to do first?"
      : "I'm right here whenever you need me.";

  // ── Action tiles data ───────────────────────────────────────────────────────
  List<_ActionTile> get _tiles => [
    _ActionTile(
      emoji: '📄',
      icon: Icons.receipt_long_rounded,
      color: const Color(0xFF3B82F6),  // blue
      title: 'Add coins from a receipt or invoice',
      subtitle: 'Photo or PDF — I\'ll read it for you',
      route: 'Add New Coins',
    ),
    _ActionTile(
      emoji: '🔬',
      icon: Icons.biotech_rounded,
      color: _teal,
      title: 'Identify a coin with the Microscope',
      subtitle: 'Place your coin — I\'ll tell you what it is',
      route: 'Microscope Scanner',
    ),
    _ActionTile(
      emoji: '📱',
      icon: Icons.photo_camera_rounded,
      color: const Color(0xFFF59E0B),  // amber
      title: 'Take a photo to identify a coin',
      subtitle: 'Just snap a pic — I\'ll do the rest',
      route: 'Add New Coins',
    ),
    _ActionTile(
      emoji: '🗂️',
      icon: Icons.collections_bookmark_rounded,
      color: const Color(0xFF8B5CF6),  // purple
      title: 'Browse my collection',
      subtitle: 'See everything you\'ve added so far',
      route: 'My Collection',
    ),
  ];

  // ── Build ───────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      body: SafeArea(
        child: FadeTransition(
          opacity: _fadeAnim,
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 560),
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
                child: Column(
                  children: [
                    // ── Morgan avatar ──────────────────────────────────────
                    AnimatedBuilder(
                      animation: _bobAnim,
                      builder: (_, child) => Transform.translate(
                        offset: Offset(0, _bobAnim.value),
                        child: child,
                      ),
                      child: _MorganAvatar(),
                    ),
                    const SizedBox(height: 24),

                    // ── Greeting ───────────────────────────────────────────
                    Text(
                      _headlineText,
                      style: const TextStyle(
                        color: _text,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        height: 1.3,
                        letterSpacing: -0.3,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 10),
                    Text(
                      _subText,
                      style: const TextStyle(
                          color: _sub, fontSize: 15, height: 1.5),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 32),

                    // ── Action tiles ───────────────────────────────────────
                    AnimatedBuilder(
                      animation: _tilesAnim,
                      builder: (_, child) => Opacity(
                        opacity: _tilesAnim.value,
                        child: Transform.translate(
                          offset: Offset(0, 20 * (1 - _tilesAnim.value)),
                          child: child,
                        ),
                      ),
                      child: Column(
                        children: _tiles.map((tile) => Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: _ActionTileCard(
                            tile: tile,
                            onTap: () async {
                              await MorganGreeter.markSeen();
                              widget.onAction(tile.route);
                            },
                          ),
                        )).toList(),
                      ),
                    ),
                    const SizedBox(height: 8),

                    // ── "Browse on my own" link ────────────────────────────
                    TextButton(
                      onPressed: () async {
                        await MorganGreeter.markSeen();
                        widget.onAction(null);
                      },
                      child: const Text(
                        'I\'ll browse on my own, thanks',
                        style: TextStyle(color: _sub, fontSize: 13),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // ── Morgan credit line ────────────────────────────────
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          width: 6, height: 6,
                          decoration: BoxDecoration(
                            color: _teal,
                            shape: BoxShape.circle,
                            boxShadow: [BoxShadow(
                                color: _teal.withAlpha(150),
                                blurRadius: 6,
                                spreadRadius: 1)],
                          ),
                        ),
                        const SizedBox(width: 6),
                        const Text(
                          'Morgan • Your Numista.AI Guide',
                          style: TextStyle(color: _sub, fontSize: 11),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// ── Morgan Avatar widget ───────────────────────────────────────────────────────
class _MorganAvatar extends StatelessWidget {
  static const _gold = Color(0xFFD4A843);
  static const _teal = Color(0xFF2DD4BF);

  @override
  Widget build(BuildContext context) {
    return Stack(
      alignment: Alignment.center,
      children: [
        // Outer glow ring
        Container(
          width: 116,
          height: 116,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: RadialGradient(
              colors: [
                _teal.withAlpha(40),
                _gold.withAlpha(20),
                Colors.transparent,
              ],
            ),
          ),
        ),
        // Gold border ring
        Container(
          width: 104,
          height: 104,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            gradient: const LinearGradient(
              colors: [Color(0xFFD4A843), Color(0xFF8B6914)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            boxShadow: [
              BoxShadow(
                  color: _gold.withAlpha(80),
                  blurRadius: 16,
                  spreadRadius: 2),
              BoxShadow(
                  color: _teal.withAlpha(60),
                  blurRadius: 24,
                  spreadRadius: 0),
            ],
          ),
        ),
        // Avatar image
        ClipOval(
          child: Image.asset(
            'assets/morgan_avatar.png',
            width: 98,
            height: 98,
            fit: BoxFit.cover,
            errorBuilder: (context, error, stackTrace) => Container(
              width: 98,
              height: 98,
              color: const Color(0xFF162033),
              child: const Icon(Icons.smart_toy_rounded,
                  color: Color(0xFF2DD4BF), size: 48),
            ),
          ),
        ),
      ],
    );
  }
}

// ── Data class for action tiles ────────────────────────────────────────────────
class _ActionTile {
  final String emoji;
  final IconData icon;
  final Color color;
  final String title;
  final String subtitle;
  final String route;

  const _ActionTile({
    required this.emoji,
    required this.icon,
    required this.color,
    required this.title,
    required this.subtitle,
    required this.route,
  });
}

// ── Individual action tile card ────────────────────────────────────────────────
class _ActionTileCard extends StatefulWidget {
  final _ActionTile tile;
  final VoidCallback onTap;
  const _ActionTileCard({required this.tile, required this.onTap});

  @override
  State<_ActionTileCard> createState() => _ActionTileCardState();
}

class _ActionTileCardState extends State<_ActionTileCard> {
  bool _pressed = false;

  static const _surface = Color(0xFF162033);
  static const _text    = Colors.white;
  static const _sub     = Color(0xFF94A3B8);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown:   (_) => setState(() => _pressed = true),
      onTapUp:     (_) => setState(() => _pressed = false),
      onTapCancel: ()  => setState(() => _pressed = false),
      onTap: widget.onTap,
      child: AnimatedScale(
        scale: _pressed ? 0.97 : 1.0,
        duration: const Duration(milliseconds: 100),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          padding: const EdgeInsets.all(18),
          decoration: BoxDecoration(
            color: _pressed
                ? widget.tile.color.withAlpha(20)
                : _surface,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: _pressed
                  ? widget.tile.color.withAlpha(180)
                  : widget.tile.color.withAlpha(60),
              width: 1.5,
            ),
            boxShadow: _pressed
                ? [BoxShadow(
                    color: widget.tile.color.withAlpha(40),
                    blurRadius: 12,
                    offset: const Offset(0, 4))]
                : [],
          ),
          child: Row(
            children: [
              // Icon badge
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: widget.tile.color.withAlpha(25),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                      color: widget.tile.color.withAlpha(80), width: 1),
                ),
                child: Icon(widget.tile.icon,
                    color: widget.tile.color, size: 26),
              ),
              const SizedBox(width: 16),
              // Text
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.tile.title,
                      style: const TextStyle(
                        color: _text,
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        height: 1.3,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      widget.tile.subtitle,
                      style: const TextStyle(
                          color: _sub, fontSize: 12, height: 1.4),
                    ),
                  ],
                ),
              ),
              // Chevron
              Icon(Icons.chevron_right_rounded,
                  color: widget.tile.color.withAlpha(150), size: 22),
            ],
          ),
        ),
      ),
    );
  }
}
