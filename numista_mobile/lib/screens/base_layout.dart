import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/auth_service.dart';
import '../services/epn_service.dart';
import '../services/guest_seed_service.dart';
import '../services/wizard_service.dart';
import '../widgets/wizard_overlay.dart';
import 'home_dashboard.dart';
import 'my_collection_screen.dart';
import 'microscope_scan_screen.dart';
import 'program_manager_screen.dart';
import 'settings_screen.dart';
import 'our_team_screen.dart';
import 'review_hub_screen.dart';
import 'add_coins_hub.dart';
import 'wishlist_screen.dart';
import 'human_ai_trainer_screen.dart';
import 'login_screen.dart';
import 'customer_service_screen.dart';
import 'ai_chat_screen.dart';

class BaseLayout extends StatefulWidget {
  final bool isDemoMode;
  const BaseLayout({super.key, this.isDemoMode = false});

  @override
  State<BaseLayout> createState() => _BaseLayoutState();
}

class _BaseLayoutState extends State<BaseLayout> {
  String _activeRoute = 'Home Dashboard';
  // Optional pre-populated AI query — set when the user taps AI Deep Dive
  // on a specific coin. Consumed once and then cleared.
  String? _aiInitialQuery;

  @override
  void initState() {
    super.initState();
    // Load eBay credentials from Firestore into SharedPreferences.
    EpnService.loadFromFirestore();
    // Auto-start the guided wizard for first-time Guest users.
    // Demo mode gets a read-only experience without the wizard.
    if (AuthService.isGuest && !widget.isDemoMode) {
      WizardService.start(
        'guest',
        onNavigate: (route) => setState(() => _activeRoute = route),
      );
    } else {
      // Register the navigate callback even if wizard isn't active yet,
      // so a future wizard invocation can still drive the nav.
      WizardService.setNavigateCallback(
        (route) => setState(() => _activeRoute = route),
      );
    }
  }

  Widget _buildBody() {
    switch (_activeRoute) {
      case 'Home Dashboard':
        return const HomeDashboard();
      case 'My Collection':
        return MyCollectionScreen(
          onNavigate: (route) => setState(() => _activeRoute = route),
          onNavigateWithQuery: (route, query) => setState(() {
            _activeRoute = route;
            _aiInitialQuery = query;
          }),
        );
      case 'Microscope Scanner':
        return const MicroscopeScanScreen();
      case 'Coin Programs':
        return const ProgramManagerScreen();
      case 'Settings & Backup':
        return const SettingsScreen();
      case 'Our Team':
        return const OurTeamScreen();
      case 'Add New Coins':
        return AddCoinsHub(onNavigate: (route) => setState(() => _activeRoute = route));
      case 'AI Deepdive':
        // Consume the initial query once, then clear it so subsequent opens
        // of AI Deepdive (from sidebar) start with an empty chat.
        final q = _aiInitialQuery;
        _aiInitialQuery = null;
        return AiChatScreen(initialQuery: q);
      case 'Review Hub':
        return const ReviewHubScreen();
      case 'My Wishlist':
        return const WishlistScreen();
      case 'AI Trainer Board':
        return const HumanAiTrainerScreen();
      case 'Customer Service':
        return const CustomerServiceScreen();
      default:
        return const _UnderConstruction();
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = FirebaseAuth.instance.currentUser;
    final displayName = user?.displayName?.isNotEmpty == true
        ? user!.displayName!
        : (user?.email?.split('@').first ?? 'Collector');
    final email = user?.email ?? '';

    return LayoutBuilder(
      builder: (context, constraints) {
        final isMobile = constraints.maxWidth < 800;
        return isMobile
            ? _buildMobileLayout(email)
            : _buildDesktopLayout(email, displayName);
      },
    );
  }

  // ─── Mobile layout: bottom nav bar ───────────────────────────────────────
  Widget _buildMobileLayout(String email) {
    // 5-tab mobile-first nav
    // Add Coins is reachable via FAB on the Collection tab
    final mobileRoutes = [
      'Home Dashboard',
      'Coin Programs',
      'My Collection',
      'AI Deepdive',
      'Settings & Backup',
    ];
    final currentIndex = mobileRoutes.indexOf(_activeRoute).clamp(0, 4);

    return Scaffold(
      backgroundColor: const Color(0xFFF0F2F6),
      body: SafeArea(
        child: Stack(
          children: [
            Column(
              children: [
                if (GuestSeedService.isBrowseDemoMode)
                  _DemoBanner(onTryFree: () {
                    GuestSeedService.deactivateBrowseDemo();
                    Navigator.of(context).pushReplacement(
                      MaterialPageRoute(builder: (_) => const LoginScreen()),
                    );
                  }),
                if (AuthService.isGuest) _GuestBanner(),
                Expanded(child: _buildBody()),
              ],
            ),
            WizardOverlay(
              onCreateAccount: () {
                Navigator.of(context).pushReplacement(
                  MaterialPageRoute(builder: (_) => const LoginScreen()),
                );
              },
            ),
          ],
        ),
      ),
      // FAB: only on Collection tab — opens Add Coins Hub
      floatingActionButton: _activeRoute == 'My Collection'
          ? FloatingActionButton(
              onPressed: () => setState(() => _activeRoute = 'Add New Coins'),
              backgroundColor: const Color(0xFFF63366),
              child: const Icon(Icons.add, color: Colors.white),
            )
          : null,
      bottomNavigationBar: NavigationBar(
        selectedIndex: currentIndex,
        onDestinationSelected: (i) =>
            setState(() => _activeRoute = mobileRoutes[i]),
        backgroundColor: const Color(0xFF0E1117),
        indicatorColor: const Color(0xFFF63366).withAlpha(40),
        labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.dashboard_outlined, color: Colors.white54),
            selectedIcon: Icon(Icons.dashboard, color: Color(0xFFF63366)),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.auto_awesome_outlined, color: Colors.white54),
            selectedIcon: Icon(Icons.auto_awesome, color: Color(0xFFF63366)),
            label: 'Programs',
          ),
          NavigationDestination(
            icon: Icon(Icons.collections_bookmark_outlined, color: Colors.white54),
            selectedIcon: Icon(Icons.collections_bookmark, color: Color(0xFFF63366)),
            label: 'Collection',
          ),
          NavigationDestination(
            icon: Icon(Icons.psychology_outlined, color: Colors.white54),
            selectedIcon: Icon(Icons.psychology, color: Color(0xFFF63366)),
            label: 'AI Chat',
          ),
          NavigationDestination(
            icon: Icon(Icons.settings_outlined, color: Colors.white54),
            selectedIcon: Icon(Icons.settings, color: Color(0xFFF63366)),
            label: 'Settings',
          ),
        ],
      ),
    );
  }

  // ─── Desktop/tablet layout: sidebar ──────────────────────────────────────
  Widget _buildDesktopLayout(String email, String displayName) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F2F6),
      body: Row(
        children: [
          // ─── Sidebar ─────────────────────────────────────────────────────
          Container(
            width: 200,
            color: const Color(0xFF0E1117),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 12),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Image.asset('assets/logo_owl.png',
                      height: 56, fit: BoxFit.contain),
                ),
                const SizedBox(height: 10),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 10),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.white.withAlpha(8),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.white.withAlpha(20)),
                    ),
                    child: Row(children: [
                      const CircleAvatar(
                        radius: 12,
                        backgroundColor: Color(0xFFF63366),
                        child: Icon(Icons.person, color: Colors.white, size: 14),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(displayName,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                    color: Colors.white,
                                    fontWeight: FontWeight.w600,
                                    fontSize: 11)),
                            Text(email,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                    color: Colors.blueAccent, fontSize: 9)),
                          ],
                        ),
                      ),
                    ]),
                  ),
                ),
                const SizedBox(height: 10),
                Expanded(
                  child: ValueListenableBuilder<WizardState?>(
                    valueListenable: WizardService.state,
                    builder: (context, ws, _) => ListView(
                      padding: const EdgeInsets.symmetric(horizontal: 8),
                      children: [
                        _buildNavItem('Home Dashboard', icon: Icons.dashboard_outlined),
                        WizardNavPulse(
                          active: ws?.step.targetRoute == 'My Collection',
                          child: _buildNavItem('My Collection', icon: Icons.collections_bookmark_outlined),
                        ),
                        StreamBuilder<QuerySnapshot>(
                          stream: email.isNotEmpty
                              ? FirebaseFirestore.instance
                                  .collection('users')
                                  .doc(email)
                                  .collection('review_queue')
                                  .snapshots()
                              : const Stream.empty(),
                          builder: (context, snapshot) {
                            final count = snapshot.data?.docs.length ?? 0;
                            return _buildNavItem('Review Hub',
                                icon: Icons.fact_check_outlined,
                                badgeCount: count);
                          },
                        ),
                        WizardNavPulse(
                          active: ws?.step.targetRoute == 'Coin Programs',
                          child: _buildNavItem('Coin Programs', icon: Icons.auto_awesome_outlined),
                        ),
                        WizardNavPulse(
                          active: ws?.step.targetRoute == 'Add New Coins',
                          child: _buildNavItem('Add New Coins', icon: Icons.add_circle_outline),
                        ),
                        _buildNavItem('Microscope Scanner', icon: Icons.camera_alt_outlined),
                        _buildNavItem('Inventory', icon: Icons.inventory_2_outlined),
                        WizardNavPulse(
                          active: ws?.step.targetRoute == 'My Wishlist',
                          child: _buildNavItem('My Wishlist', icon: Icons.favorite_outline),
                        ),
                        _buildNavItem('AI Deepdive', icon: Icons.psychology_outlined),
                        _buildNavItem('AI Trainer Board', icon: Icons.how_to_vote_outlined),
                        _buildNavItem('Settings & Backup', icon: Icons.settings_outlined),
                        const _SidebarDivider(),
                        _buildNavItem('Our Team', icon: Icons.people_outline),
                        _buildNavItem('Customer Service', icon: Icons.support_agent_outlined),
                        _buildNavItem('🔍 Numista Lookup'),
                      ],
                    ),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(8, 0, 8, 4),
                  child: SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2A1F4E),
                        foregroundColor: const Color(0xFFFFD700),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                        elevation: 0,
                      ),
                      icon: const Icon(Icons.feedback_outlined, size: 14, color: Color(0xFFFFD700)),
                      label: const Text(
                        'Send Beta Feedback',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600),
                      ),
                      onPressed: () async {
                        final email = FirebaseAuth.instance.currentUser?.email ?? 'beta tester';
                        final subject = Uri.encodeComponent('Numista.AI Beta Feedback');
                        final body = Uri.encodeComponent(
                          'Beta tester: $email\n'
                          'Version: Beta v1.0\n\n'
                          'Feedback / Bug Report:\n\n'
                          '---\n'
                          '(Please describe what happened, what you expected, and any steps to reproduce)\n',
                        );
                        final uri = Uri.parse('mailto:beta@numista.ai?subject=$subject&body=$body');
                        if (await canLaunchUrl(uri)) {
                          await launchUrl(uri);
                        }
                      },
                    ),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(8, 4, 8, 10),
                  child: SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.white70,
                        side: const BorderSide(color: Colors.white24),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                      ),
                      icon: const Icon(Icons.logout, size: 14),
                      label: Text(
                        AuthService.isGuest ? 'Exit Guest' : 'Sign Out',
                        style: const TextStyle(fontSize: 11),
                      ),
                      onPressed: () => _confirmSignOut(context),
                    ),
                  ),
                ),
              ],
            ),
          ),

          // ─── Main Content ───────────────────────────────────────────────
          Expanded(
            child: Stack(
              children: [
                Column(
                  children: [
                    if (widget.isDemoMode || GuestSeedService.isBrowseDemoMode)
                      _DemoBanner(onTryFree: () {
                        GuestSeedService.deactivateBrowseDemo();
                        Navigator.of(context).pushReplacement(
                          MaterialPageRoute(builder: (_) => const LoginScreen()),
                        );
                      }),
                    if (!widget.isDemoMode && AuthService.isGuest) _GuestBanner(),
                    Expanded(child: _buildBody()),
                  ],
                ),
                WizardOverlay(
                  onCreateAccount: () {
                    Navigator.of(context).pushReplacement(
                      MaterialPageRoute(builder: (_) => const LoginScreen()),
                    );
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }


  // ─── Nav item builder ────────────────────────────────────────────────────
  Widget _buildNavItem(String title, {IconData? icon, int badgeCount = 0}) {
    final bool isActive = _activeRoute == title;
    // Items without a backing screen are disabled
    final bool isEnabled = const {
      'Home Dashboard',
      'My Collection',
      'Review Hub',
      'Microscope Scanner',
      'Coin Programs',
      'Add New Coins',
      'My Wishlist',
      'AI Deepdive',
      'Human AI Trainer Review Board',
      'AI Trainer Board',
      'Settings & Backup',
      'Our Team',
      'Customer Service',
    }.contains(title);

    return Opacity(
      opacity: isEnabled ? 1.0 : 0.45,
      child: InkWell(
        onTap: isEnabled ? () => setState(() => _activeRoute = title) : null,
        borderRadius: BorderRadius.circular(6),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 5, horizontal: 6),
          decoration: BoxDecoration(
            color: isActive
                ? Colors.white.withAlpha(16)
                : Colors.transparent,
            borderRadius: BorderRadius.circular(6),
          ),
          child: Row(children: [
            if (icon != null)
              Icon(icon,
                  size: 14,
                  color: isActive
                      ? const Color(0xFFF63366)
                      : Colors.white54)
            else
              Container(
                width: 16,
                height: 16,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: isActive
                      ? const Color(0xFFF63366)
                      : Colors.transparent,
                  border: Border.all(
                    color: isActive
                        ? const Color(0xFFF63366)
                        : Colors.white38,
                    width: isActive ? 4 : 1,
                  ),
                ),
              ),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                title,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  color: isActive ? Colors.white : Colors.white60,
                  fontSize: 11,
                  fontWeight:
                      isActive ? FontWeight.w600 : FontWeight.normal,
                ),
              ),
            ),
            if (badgeCount > 0) ...[
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: const Color(0xFFF63366),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  badgeCount.toString(),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ]),
        ),
      ),
    );
  }

  // ─── Sign-out confirmation ────────────────────────────────────────────────
  Future<void> _confirmSignOut(BuildContext ctx) async {
    final confirm = await showDialog<bool>(
      context: ctx,
      builder: (dctx) => AlertDialog(
        backgroundColor: const Color(0xFF1A1D27),
        title: const Text('Sign Out',
            style: TextStyle(color: Colors.white)),
        content: const Text(
            'Are you sure you want to sign out of your vault?',
            style: TextStyle(color: Colors.white70)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dctx, false),
            child: const Text('Cancel',
                style: TextStyle(color: Colors.white54)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(dctx, true),
            child: const Text('Sign Out',
                style: TextStyle(color: Color(0xFFF63366))),
          ),
        ],
      ),
    );
    if (confirm == true) await AuthService.signOut();
    // The StreamBuilder in main.dart automatically redirects to LoginScreen
  }
}

// ─── Placeholder for unbuilt screens ─────────────────────────────────────────
class _UnderConstruction extends StatelessWidget {
  const _UnderConstruction();
  @override
  Widget build(BuildContext context) => const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.construction, size: 48, color: Color(0xFFA0A3AB)),
            SizedBox(height: 16),
            Text('Coming Soon',
                style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF31333F))),
            SizedBox(height: 8),
            Text('This feature is under construction.',
                style: TextStyle(color: Color(0xFF5A5C69))),
          ],
        ),
      );
}

// ─── Sidebar section divider ──────────────────────────────────────────────────
class _SidebarDivider extends StatelessWidget {
  const _SidebarDivider();
  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Divider(color: Colors.white.withAlpha(20), thickness: 1),
      );
}

// ─── Browse Demo top banner ───────────────────────────────────────────────────
class _DemoBanner extends StatelessWidget {
  final VoidCallback onTryFree;
  const _DemoBanner({required this.onTryFree});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      color: const Color(0xFF1565C0),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      child: Row(
        children: [
          const Icon(Icons.visibility_outlined, color: Colors.white70, size: 16),
          const SizedBox(width: 10),
          const Expanded(
            child: Text(
              "You're browsing a read-only demo. Create a free account to add coins, use the scanner, and save your collection.",
              style: TextStyle(color: Colors.white, fontSize: 12),
            ),
          ),
          const SizedBox(width: 12),
          OutlinedButton(
            onPressed: onTryFree,
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.white,
              side: const BorderSide(color: Colors.white54),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
              textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
            ),
            child: const Text('Try It Free →'),
          ),
        ],
      ),
    );
  }
}

// ─── Guest session top banner ─────────────────────────────────────────────────
class _GuestBanner extends StatelessWidget {
  const _GuestBanner();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      color: const Color(0xFF0D9488),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      child: Row(
        children: [
          const Icon(Icons.rocket_launch_rounded, color: Colors.white70, size: 16),
          const SizedBox(width: 10),
          const Expanded(
            child: Text(
              'Guest session active — your coins are saved for 30 days. Create a free account to keep them permanently.',
              style: TextStyle(color: Colors.white, fontSize: 12),
            ),
          ),
          const SizedBox(width: 12),
          OutlinedButton(
            onPressed: () => Navigator.of(context).pushReplacement(
              MaterialPageRoute(builder: (_) => const LoginScreen()),
            ),
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.white,
              side: const BorderSide(color: Colors.white54),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
              textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
            ),
            child: const Text('Create Account →'),
          ),
        ],
      ),
    );
  }
}

