import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/morgan_prefs.dart';
import 'morgan_setup_dialog.dart';
import 'morgan_guide_flow.dart';
import 'morgan_guides.dart';

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
  final void Function(String? route, String? tabName) onAction;

  /// Whether this is the very first time the user has seen Morgan.
  /// Affects the greeting message slightly.
  final bool isFirstVisit;

  const MorganGreeter({
    super.key,
    required this.onAction,
    this.isFirstVisit = true,
  });

  static const String _prefKey = 'morgan_greeter_seen';

  /// Show Morgan on startup unless the user has explicitly opted out.
  /// Default is true — Morgan greets everyone on every login.
  static Future<bool> shouldShow() => MorganPrefs.showOnStartup();

  /// Legacy "mark as seen" — kept for compatibility but no longer hides Morgan.
  static Future<void> markSeen() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_prefKey, true); // marks first-visit done only
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

  // ── Greeting copy ───────────────────────────────────────────────────────────
  String _firstName = 'there'; // populated async in initState
  bool _showingSubMenu = false;

  @override
  void initState() {
    super.initState();

    // Load preferred name async — rebuild once loaded
    MorganPrefs.getDisplayName().then((name) {
      if (mounted) setState(() => _firstName = name);
    });

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

  // ── Main Menu Tiles ──────────────────────────────────────────────────────────
  List<_ActionTile> get _mainTiles => [
    _ActionTile(
      tileId: 'add_collection',
      emoji: '➕',
      icon: Icons.add_circle_outline_rounded,
      color: const Color(0xFF10B981), // emerald green
      title: 'Add coins, notes, or medals',
      subtitle: 'Interactive tools: checklists, scanning, spreadsheets...',
      route: '',
    ),
    _ActionTile(
      tileId: 'dashboard',
      emoji: '🏠',
      icon: Icons.dashboard_rounded,
      color: const Color(0xFF3B82F6), // vibrant blue
      title: 'Go to Homepage / Dashboard',
      subtitle: 'Check portfolio value, market updates, and stats',
      route: 'Home Dashboard',
    ),
    _ActionTile(
      tileId: 'collection',
      emoji: '🗂️',
      icon: Icons.collections_bookmark_rounded,
      color: const Color(0xFF8B5CF6), // royal purple
      title: 'Browse my collection',
      subtitle: 'See everything you\'ve added so far',
      route: 'My Collection',
    ),
    _ActionTile(
      tileId: 'chat',
      emoji: '💬',
      icon: Icons.forum_rounded,
      color: _teal, // teal accent
      title: 'Chat with Morgan',
      subtitle: 'Ask me anything about coins, history, or values',
      route: 'AI Deepdive',
    ),
  ];

  // ── Sub-Menu Ingestion Tiles ────────────────────────────────────────────────
  List<_ActionTile> get _subTiles => [
    _ActionTile(
      tileId: 'programs',
      emoji: '📋',
      icon: Icons.playlist_add_check_rounded,
      color: const Color(0xFFF59E0B), // amber
      title: 'US Mint Coin Programs',
      subtitle: 'Interactive checklists for state quarters, dollars, etc.',
      route: 'Coin Programs',
    ),
    _ActionTile(
      tileId: 'invoice',
      emoji: '📄',
      icon: Icons.receipt_long_rounded,
      color: const Color(0xFF3B82F6), // blue
      title: 'Receipt or Invoice Scan',
      subtitle: 'Photo or PDF — I\'ll read and extract coins',
      route: 'Add New Coins',
      tabName: 'upload',
    ),
    _ActionTile(
      tileId: 'spreadsheet',
      emoji: '📊',
      icon: Icons.table_chart_rounded,
      color: const Color(0xFF10B981), // emerald green
      title: 'Upload Spreadsheet or CSV',
      subtitle: 'Import list from Excel or CSV files',
      route: 'Add New Coins',
      tabName: 'upload',
    ),
    _ActionTile(
      tileId: 'microscope',
      emoji: '🔬',
      icon: Icons.biotech_rounded,
      color: _teal, // teal
      title: 'Identify with Microscope',
      subtitle: 'Place your coin — I\'ll tell you what it is',
      route: 'Microscope Scanner',
    ),
    _ActionTile(
      tileId: 'photo',
      emoji: '📷',
      icon: Icons.photo_camera_rounded,
      color: const Color(0xFFEC4899), // pink
      title: 'Upload Photo to ID',
      subtitle: 'Snap or upload photo to identify a coin',
      route: 'Add New Coins',
      tabName: 'upload',
    ),
    _ActionTile(
      tileId: 'manual',
      emoji: '✍️',
      icon: Icons.edit_note_rounded,
      color: const Color(0xFF8B5CF6), // purple
      title: 'Manual Form Entry',
      subtitle: 'Type coin, note, or medal details directly',
      route: 'Add New Coins',
      tabName: 'manual',
    ),
  ];

  // ── Build ───────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    final isDesktop = MediaQuery.of(context).size.width >= 800;
    final maxWidth = isDesktop && _showingSubMenu ? 780.0 : 540.0;

    return Scaffold(
      backgroundColor: _bg,
      body: SafeArea(
        child: FadeTransition(
          opacity: _fadeAnim,
          child: Center(
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 250),
              curve: Curves.easeInOut,
              constraints: BoxConstraints(maxWidth: maxWidth),
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 24),
                child: AnimatedSwitcher(
                  duration: const Duration(milliseconds: 350),
                  switchInCurve: Curves.easeOutCubic,
                  switchOutCurve: Curves.easeInCubic,
                  transitionBuilder: (Widget child, Animation<double> animation) {
                    final isSubMenu = child.key == const ValueKey('sub_menu');
                    final beginOffset = isSubMenu ? const Offset(0.2, 0.0) : const Offset(-0.2, 0.0);
                    final slide = Tween<Offset>(begin: beginOffset, end: Offset.zero)
                        .animate(CurvedAnimation(parent: animation, curve: Curves.easeOutCubic));
                    return FadeTransition(
                      opacity: animation,
                      child: SlideTransition(position: slide, child: child),
                    );
                  },
                  child: _showingSubMenu
                      ? _buildSubMenu(context, isDesktop)
                      : _buildMainMenu(context),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildMainMenu(BuildContext context) {
    return Column(
      key: const ValueKey('main_menu'),
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
        const SizedBox(height: 20),

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
        const SizedBox(height: 8),
        Text(
          _subText,
          style: const TextStyle(
            color: _sub,
            fontSize: 14,
            height: 1.4,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 28),

        // ── Action tiles ───────────────────────────────────────
        AnimatedBuilder(
          animation: _tilesAnim,
          builder: (_, child) => Opacity(
            opacity: _tilesAnim.value,
            child: Transform.translate(
              offset: Offset(0, 15 * (1 - _tilesAnim.value)),
              child: child,
            ),
          ),
          child: Column(
            children: _mainTiles.map((tile) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: _ActionTileCard(
                tile: tile,
                onTap: () => _onTileTap(tile),
              ),
            )).toList(),
          ),
        ),
        const SizedBox(height: 8),

        // ── "Browse on my own" link ────────────────────────────
        TextButton(
          onPressed: () async {
            await MorganGreeter.markSeen();
            widget.onAction(null, null);
          },
          child: const Text(
            'I\'ll browse on my own, thanks',
            style: TextStyle(color: _sub, fontSize: 13),
          ),
        ),
        const SizedBox(height: 12),

        // ── Morgan credit line ────────────────────────────────
        _buildCreditLine(),
      ],
    );
  }

  Widget _buildSubMenu(BuildContext context, bool isDesktop) {
    return Column(
      key: const ValueKey('sub_menu'),
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // ── Back Button & Header ───────────────────────────────
        Row(
          children: [
            IconButton(
              icon: const Icon(Icons.arrow_back_rounded, color: _text, size: 24),
              onPressed: () => setState(() => _showingSubMenu = false),
              tooltip: 'Back to main menu',
            ),
            const SizedBox(width: 8),
            const Text(
              'Add to Collection',
              style: TextStyle(
                color: _text,
                fontSize: 20,
                fontWeight: FontWeight.bold,
                letterSpacing: -0.2,
              ),
            ),
          ],
        ),
        const Padding(
          padding: EdgeInsets.only(left: 12, top: 4, bottom: 20),
          child: Text(
            'Choose how you\'d like to add items.',
            style: TextStyle(color: _sub, fontSize: 13),
          ),
        ),

        // ── Sub-menu options (Responsive Grid / List) ──────────
        if (isDesktop)
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              mainAxisExtent: 82, // tight height to fit on screen
            ),
            itemCount: _subTiles.length,
            itemBuilder: (context, index) {
              final tile = _subTiles[index];
              return _ActionTileCard(
                tile: tile,
                compact: true,
                onTap: () => _onTileTap(tile),
              );
            },
          )
        else
          Column(
            children: _subTiles.map((tile) => Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: _ActionTileCard(
                tile: tile,
                compact: true,
                onTap: () => _onTileTap(tile),
              ),
            )).toList(),
          ),
        
        const SizedBox(height: 24),
        Center(child: _buildCreditLine()),
      ],
    );
  }

  Widget _buildCreditLine() {
    return Row(
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
    );
  }

  // ── Tile tap handler ──────────────────────────────────────────────────────
  Future<void> _onTileTap(_ActionTile tile) async {
    if (tile.tileId == 'add_collection') {
      setState(() {
        _showingSubMenu = true;
      });
      return;
    }

    await MorganGreeter.markSeen();

    // Show name setup on very first tile tap
    final setupDone = await MorganPrefs.isSetupDone();
    if (!setupDone && mounted) {
      final confirmed = await showMorganSetup(context);
      if (!confirmed) return; // user dismissed without confirming
    }

    // Start the matching guide flow
    final guide = MorganGuides.forTileId(tile.tileId);
    if (guide != null) MorganGuideService.start(guide);

    // Navigate to the target screen
    if (mounted) widget.onAction(tile.route, tile.tabName);
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
  final String tileId;  // used by MorganGuides.forTileId()
  final String emoji;
  final IconData icon;
  final Color color;
  final String title;
  final String subtitle;
  final String route;
  final String? tabName;

  const _ActionTile({
    required this.tileId,
    required this.emoji,
    required this.icon,
    required this.color,
    required this.title,
    required this.subtitle,
    required this.route,
    this.tabName,
  });
}

// ── Individual action tile card ────────────────────────────────────────────────
class _ActionTileCard extends StatefulWidget {
  final _ActionTile tile;
  final VoidCallback onTap;
  final bool compact;
  const _ActionTileCard({
    required this.tile,
    required this.onTap,
    this.compact = false,
  });

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
    final compact = widget.compact;
    final colorAccent = widget.tile.color;
    final surfaceColor = _surface.withValues(alpha: 0.55);

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
          padding: EdgeInsets.all(compact ? 10 : 18),
          decoration: BoxDecoration(
            color: _pressed
                ? colorAccent.withValues(alpha: 0.15)
                : surfaceColor,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: _pressed
                  ? colorAccent.withValues(alpha: 0.8)
                  : colorAccent.withValues(alpha: 0.25),
              width: 1.5,
            ),
            boxShadow: [
              BoxShadow(
                color: colorAccent.withValues(alpha: _pressed ? 0.25 : 0.05),
                blurRadius: _pressed ? 16 : 8,
                spreadRadius: _pressed ? 2 : 0,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Row(
            children: [
              // Icon badge
              Container(
                width: compact ? 38 : 52,
                height: compact ? 38 : 52,
                decoration: BoxDecoration(
                  color: colorAccent.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                      color: colorAccent.withValues(alpha: 0.4), width: 1),
                ),
                child: Icon(widget.tile.icon,
                    color: colorAccent, size: compact ? 20 : 26),
              ),
              SizedBox(width: compact ? 12 : 16),
              // Text
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      widget.tile.title,
                      style: TextStyle(
                        color: _text,
                        fontSize: compact ? 13 : 15,
                        fontWeight: FontWeight.w600,
                        height: 1.2,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      widget.tile.subtitle,
                      style: TextStyle(
                          color: _sub, fontSize: compact ? 11 : 12, height: 1.3),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              // Chevron
              Icon(Icons.chevron_right_rounded,
                  color: colorAccent.withValues(alpha: 0.6), size: compact ? 18 : 22),
            ],
          ),
        ),
      ),
    );
  }
}
