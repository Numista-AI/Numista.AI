import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../services/auth_service.dart';
import '../services/coin_normalizer_service.dart';
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
import 'estate_planning_screen.dart';
import 'human_ai_trainer_screen.dart';
import 'login_screen.dart';
import 'customer_service_screen.dart';
import 'ai_chat_screen.dart';
import 'admin_grade_flags_screen.dart';
import 'supplies_screen.dart';
import 'coin_search_screen.dart';
import 'currency_collection_screen.dart';
import 'mint_error_library_screen.dart';
import 'glossary_academy_screen.dart';
import 'welcome_screen.dart';  // for WelcomeScreen.pendingRoute
import 'add_world_item_screen.dart';
import 'attorney_portal_screen.dart';
import 'lateral_transfer_screen.dart';
import 'admin_feedback_screen.dart';
import '../models/coin_model.dart';
import '../widgets/beta_feedback_widget.dart';
import '../services/feedback_trigger_observer.dart';
import '../services/beta_feedback_service.dart' show FeedbackTriggerReason;
import '../widgets/morgan_guide_flow.dart';
import '../widgets/morgan_chat_popout.dart';
import 'coin_detail_screen.dart';

class BaseLayout extends StatefulWidget {
  final bool isDemoMode;
  const BaseLayout({super.key, this.isDemoMode = false});

  @override
  State<BaseLayout> createState() => _BaseLayoutState();
}

class _BaseLayoutState extends State<BaseLayout> {
  final GlobalKey _repaintKey = GlobalKey();
  String _activeRoute = 'Home Dashboard';
  String _myCollectionTab = 'All';
  // Optional pre-populated AI query — set when the user taps AI Deep Dive
  // on a specific coin. Consumed once and then cleared.
  String? _aiInitialQuery;
  String? _addCoinsInitialTabName;
  String? _programManagerInitialId;
  bool _isMorganPopoutOpen = false;
  String? _popoutInitialQuery;
  bool _isSidebarCollapsed = false;
  bool _desktopHotkeysEnabled = true;
  FocusNode? _previousFocusNode;

  // ── Show Morgan overlay — re-opens guide or shows greeter dialog ───────────
  void _showMorganDialog() {
    final gs = MorganGuideService.current.value;
    if (gs != null) {
      // A guide is already active — just un-collapse it if needed.
      if (gs.collapsed) MorganGuideService.toggleCollapsed();
      return;
    }

    if (MediaQuery.of(context).size.width < 800) {
      // Mobile: Switch tab to AI Deepdive
      setState(() {
        _activeRoute = 'AI Deepdive';
      });
      return;
    }

    // Desktop: Toggle resizable/draggable popout!
    setState(() {
      _isMorganPopoutOpen = !_isMorganPopoutOpen;
      if (_isMorganPopoutOpen) {
        _popoutInitialQuery = null;
      }
    });
  }

  // ── Morgan inline search — called by MorganGuidePanel ─────────────────────
  Future<List<MorganSearchResult>> _onMorganSearch(String query) async {
    try {
      final email = FirebaseAuth.instance.currentUser?.email ?? '';
      if (email.isEmpty) return [];
      final q = query.toLowerCase();
      final snap = await FirebaseFirestore.instance
          .collection('users')
          .doc(email)
          .collection('coins')
          .get();
      return snap.docs
          .where((d) {
            final data = d.data();
            final denom   = (data['Denomination']   ?? '').toString().toLowerCase();
            final year    = (data['Year']            ?? '').toString().toLowerCase();
            final series  = (data['Program/Series']  ?? '').toString().toLowerCase();
            final country = (data['Country']         ?? '').toString().toLowerCase();
            final variety = (data['Variety']         ?? '').toString().toLowerCase();
            return denom.contains(q)   || year.contains(q) ||
                   series.contains(q)  || country.contains(q) ||
                   variety.contains(q);
          })
          .take(5)
          .map((d) {
            final data   = d.data();
            final year   = data['Year']?.toString() ?? '';
            final denom  = data['Denomination']?.toString() ?? '';
            final title  = '$year $denom'.trim();
            final series = data['Program/Series']?.toString() ?? '';
            final aiVal  = data['AI Estimated Value']?.toString() ?? '';
            final valStr = (aiVal.isNotEmpty &&
                            aiVal != 'Pending' &&
                            aiVal != 'null')
                ? '\$$aiVal'
                : '';
            return MorganSearchResult(
              id:       d.id,
              title:    title.isNotEmpty ? title : 'Coin',
              subtitle: series,
              value:    valStr,
            );
          })
          .toList();
    } catch (_) {
      return [];
    }
  }

  void _handleMorganSearchResultTap(String coinId) async {
    if (coinId.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Coin reference is missing.')),
      );
      return;
    }

    final email = AuthService.userEmail;
    if (email.isEmpty) return;

    try {
      final docSnap = await FirebaseFirestore.instance
          .collection('users')
          .doc(email)
          .collection('coins')
          .doc(coinId)
          .get();

      if (!docSnap.exists) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Coin not found in vault inventory.')),
          );
        }
        return;
      }

      if (mounted) {
        final coinData = docSnap.data() as Map<String, dynamic>;
        final coin = CoinModel.fromMap(coinData, docSnap.id);
        CoinDetailScreen.show(context, coin: coin);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error opening coin: $e')),
        );
      }
    }
  }

  @override
  void initState() {
    super.initState();
    _loadDefaultTab();
    _loadDesktopPrefs();
 
    // ── Morgan deep-link: if the user tapped a tile in the greeter,
    // navigate directly to that screen instead of Home Dashboard.
    final morganRoute = WelcomeScreen.pendingRoute;
    if (morganRoute != null) {
      WelcomeScreen.pendingRoute = null;  // consume once
      _activeRoute = morganRoute;
      _addCoinsInitialTabName = WelcomeScreen.pendingTabName;
      WelcomeScreen.pendingTabName = null;
    }

    // Load eBay credentials from Firestore into SharedPreferences.
    EpnService.loadFromFirestore();
    // Run US Mint data normalization silently in background for all accounts.
    // Only processes coins that haven't been normalized yet.
    if (!AuthService.isGuest) {
      CoinNormalizerService.runForUser();
    }
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

  void _loadDefaultTab() async {
    final prefs = await SharedPreferences.getInstance();
    final tab = prefs.getString('my_collection_default_tab');
    if (tab != null && mounted) {
      setState(() {
        _myCollectionTab = tab;
      });
    }
  }

  void _loadDesktopPrefs() async {
    final prefs = await SharedPreferences.getInstance();
    final collapsed = prefs.getBool('desktop_sidebar_collapsed') ?? false;
    final hotkeys = prefs.getBool('desktop_hotkeys_enabled') ?? true;
    if (mounted) {
      setState(() {
        _isSidebarCollapsed = collapsed;
        _desktopHotkeysEnabled = hotkeys;
      });
    }
  }

  void _toggleSidebar() async {
    final nextState = !_isSidebarCollapsed;
    setState(() {
      _isSidebarCollapsed = nextState;
    });
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('desktop_sidebar_collapsed', nextState);
  }

  /// Child tab changes must never setState while BaseLayout is building.
  /// didUpdateWidget on MyCollectionScreen can fire mid-build when
  /// initialTab changes; deferring keeps the sidebar in sync without
  /// "setState() or markNeedsBuild() called during build".
  void _onMyCollectionTabChanged(String tab) {
    if (_myCollectionTab == tab) return;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted || _myCollectionTab == tab) return;
      setState(() => _myCollectionTab = tab);
    });
  }

  void _navigateTo(String route) {
    if (route == 'AI Deepdive' && MediaQuery.of(context).size.width >= 800) {
      setState(() {
        _isMorganPopoutOpen = true;
        _popoutInitialQuery = null;
      });
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _popoutInitialQuery = null;
      });
      return;
    }
    setState(() {
      if (route.startsWith('Coin Programs:')) {
        final parts = route.split(':');
        _programManagerInitialId = parts[1];
        _activeRoute = 'Coin Programs';
      } else {
        _activeRoute = route;
      }
    });
  }

  Widget _buildBody() {
    switch (_activeRoute) {
      case 'Home Dashboard':
        return HomeDashboard(
          onAskMorgan: () => _navigateTo('AI Deepdive'),
          onAskMorganWithQuery: (query) {
            if (MediaQuery.of(context).size.width >= 800) {
              setState(() {
                _isMorganPopoutOpen = true;
                _popoutInitialQuery = query;
              });
              WidgetsBinding.instance.addPostFrameCallback((_) {
                _popoutInitialQuery = null;
              });
            } else {
              setState(() {
                _aiInitialQuery = query;
                _activeRoute = 'AI Deepdive';
              });
            }
          },
          onNavigateToCollection: () => _navigateTo('My Collection'),
        );
      case 'My Collection':
        return MyCollectionScreen(
          initialTab: _myCollectionTab,
          onNavigate: _navigateTo,
          onNavigateWithQuery: (route, query) {
            if (route == 'AI Deepdive' && MediaQuery.of(context).size.width >= 800) {
              setState(() {
                _isMorganPopoutOpen = true;
                _popoutInitialQuery = query;
              });
              WidgetsBinding.instance.addPostFrameCallback((_) {
                _popoutInitialQuery = null;
              });
            } else {
              setState(() {
                _activeRoute = route;
                _aiInitialQuery = query;
              });
            }
          },
          onTabChanged: _onMyCollectionTabChanged,
        );
      case 'Microscope Scanner':
        return const MicroscopeScanScreen();
      case 'Coin Programs':
        final progId = _programManagerInitialId;
        _programManagerInitialId = null; // consume
        return ProgramManagerScreen(initialProgramId: progId);
      case 'Settings & Backup':
        return const SettingsScreen();
      case 'Our Team':
        return const OurTeamScreen();
      case 'Add New Coins':
        final tabName = _addCoinsInitialTabName;
        _addCoinsInitialTabName = null; // consume once
        return AddCoinsHub(
          onNavigate: _navigateTo,
          initialTabName: tabName,
        );
      case 'World & Specialty':
        return AddWorldItemScreen(
          onNavigate: _navigateTo,
        );
      case 'AI Deepdive':
        // Consume the initial query once, then clear it so subsequent opens
        // of AI Deepdive (from sidebar) start with an empty chat.
        final q = _aiInitialQuery;
        _aiInitialQuery = null;
        return AiChatScreen(
          initialQuery: q,
          onNavigateToCollection: () => _navigateTo('My Collection'),
        );
      case 'Review Hub':
        return const ReviewHubScreen();
      case 'My Wishlist':
        return const WishlistScreen();
      case 'Estate Planning':
        return const EstatePlanningScreen();
      case 'Attorney Portal':
        final user = FirebaseAuth.instance.currentUser;
        final userUid = user?.uid ?? user?.email ?? '';
        return AttorneyPortalScreen(uid: userUid, token: '');
      case 'Lateral Transfer':
        final email = AuthService.userEmail;
        return LateralTransferScreen(userId: email, itemsToTransfer: const [], initialTab: 'send');
      case 'Claim Transfer':
      case 'Claim Incoming Transfer':
        final email = AuthService.userEmail;
        return LateralTransferScreen(userId: email, itemsToTransfer: const [], initialTab: 'claim');
      case 'AI Trainer Board':
        return const HumanAiTrainerScreen();
      case 'Admin: Grade Flags':
        return const AdminGradeFlagsScreen();
      case 'Admin: Beta Dashboard':
      case 'Beta Feedback Inbox':
        return const AdminFeedbackScreen();
      case 'Customer Service':
        return const CustomerServiceScreen();
      case 'Inventory':
        return const SuppliesScreen();
      case 'Coin Search':
        return const CoinSearchScreen();
      case 'Currency Collection':
        return const CurrencyCollectionScreen();
      case 'Error Library':
        return const MintErrorLibraryScreen();
      case 'Glossary Academy':
        return const GlossaryAcademyScreen();
      default:
        return const _UnderConstruction();
    }
  }

  Widget _wrapBodyWithMaxWidth(Widget body, String route) {
    final double maxWidth;
    switch (route) {
      case 'Add New Coins':
        maxWidth = 1100.0;
        break;
      case 'My Collection':
      case 'Currency Collection':
        maxWidth = 1440.0;
        break;
      case 'Estate Planning':
        maxWidth = 1600.0;
        break;
      case 'Home Dashboard':
      case 'Settings & Backup':
      case 'Our Team':
      case 'Customer Service':
      default:
        maxWidth = 1280.0;
        break;
    }
    return Align(
      alignment: Alignment.topCenter,
      child: ConstrainedBox(
        constraints: BoxConstraints(maxWidth: maxWidth),
        child: body,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final user = FirebaseAuth.instance.currentUser;
    final displayName = user?.displayName?.isNotEmpty == true
        ? user!.displayName!
        : (user?.email?.split('@').first ?? 'Collector');
    final email = user?.email ?? '';

    final rootContent = LayoutBuilder(
      builder: (context, constraints) {
        final isMobile = constraints.maxWidth < 800;
        return isMobile
            ? _buildMobileLayout(email)
            : _buildDesktopLayout(email, displayName);
      },
    );

    if (!_desktopHotkeysEnabled) {
      return rootContent;
    }

    return CallbackShortcuts(
      bindings: <ShortcutActivator, VoidCallback>{
        SingleActivator(LogicalKeyboardKey.keyK, control: true): () {
          setState(() => _activeRoute = 'Coin Search');
        },
        SingleActivator(LogicalKeyboardKey.keyK, meta: true): () {
          setState(() => _activeRoute = 'Coin Search');
        },
        SingleActivator(LogicalKeyboardKey.keyM, control: true): _showMorganDialog,
        SingleActivator(LogicalKeyboardKey.keyM, meta: true): _showMorganDialog,
        SingleActivator(LogicalKeyboardKey.escape): () {
          if (_isMorganPopoutOpen) {
            setState(() => _isMorganPopoutOpen = false);
            _previousFocusNode?.requestFocus();
          }
        },
      },
      child: rootContent,
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
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: SafeArea(
        child: Stack(
          children: [
            RepaintBoundary(
              key: _repaintKey,
              child: Column(
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
            ),
            WizardOverlay(
              onCreateAccount: () {
                Navigator.of(context).pushReplacement(
                  MaterialPageRoute(builder: (_) => const LoginScreen()),
                );
              },
            ),
            // Morgan guide panel — floats above screen when a guide is active
            MorganGuidePanel(
              onSearch: _onMorganSearch,
              onSearchResultTap: _handleMorganSearchResultTap,
            ),
            BetaFeedbackWidget(
              currentRoute: _activeRoute,
              pageTitle: _activeRoute,
            ),
          ],
        ),
      ),
      // FAB column: Morgan owl (always) + Add Coins (Collection tab only)
      floatingActionButton: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          _MorganFab(onTap: _showMorganDialog),
          if (_activeRoute == 'My Collection') ...[
            const SizedBox(height: 12),
            FloatingActionButton(
              heroTag: 'fab_add_coins',
              onPressed: () => setState(() => _activeRoute = 'Add New Coins'),
              backgroundColor: const Color(0xFFF63366),
              child: const Icon(Icons.add, color: Colors.white),
            ),
          ],
        ],
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
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
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final sidebarWidth = _isSidebarCollapsed ? 72.0 : 240.0;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: Row(
        children: [
          // ─── Sidebar ─────────────────────────────────────────────────────
          AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            width: sidebarWidth,
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF0E1117) : const Color(0xFFF8FAFC),
              border: Border(
                right: BorderSide(
                  color: isDark ? Colors.white.withAlpha(12) : Colors.black.withAlpha(12),
                ),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 12),
                // Sidebar header with collapse/expand toggle button
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8),
                  child: Row(
                    mainAxisAlignment: _isSidebarCollapsed
                        ? MainAxisAlignment.center
                        : MainAxisAlignment.spaceBetween,
                    children: [
                      if (!_isSidebarCollapsed)
                        Image.asset('assets/logo_owl.png',
                            height: 48, fit: BoxFit.contain)
                      else
                        Image.asset('assets/logo_owl.png',
                            height: 36, fit: BoxFit.contain),
                      IconButton(
                        icon: Icon(
                          _isSidebarCollapsed
                              ? Icons.chevron_right
                              : Icons.chevron_left,
                          color: isDark ? Colors.white70 : Colors.black54,
                          size: 20,
                        ),
                        tooltip: _isSidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar',
                        onPressed: _toggleSidebar,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 8),
                if (!_isSidebarCollapsed) ...[
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 10),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
                      decoration: BoxDecoration(
                        color: isDark ? Colors.white.withAlpha(8) : Colors.black.withAlpha(8),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(
                            color: isDark ? Colors.white.withAlpha(20) : Colors.black.withAlpha(20)),
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
                                  style: TextStyle(
                                      color: isDark ? Colors.white : const Color(0xFF0F172A),
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
                ] else ...[
                  Tooltip(
                    message: '$displayName\n$email',
                    child: const Center(
                      child: CircleAvatar(
                        radius: 14,
                        backgroundColor: Color(0xFFF63366),
                        child: Icon(Icons.person, color: Colors.white, size: 16),
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                ],

                Expanded(
                  child: ValueListenableBuilder<WizardState?>(
                    valueListenable: WizardService.state,
                    builder: (context, ws, _) => ListView(
                      padding: const EdgeInsets.symmetric(horizontal: 6),
                      children: [
                        _buildNavItem('Home Dashboard', icon: Icons.dashboard_outlined),
                        WizardNavPulse(
                          active: ws?.step.targetRoute == 'Coin Programs',
                          child: _buildNavItem('Coin Programs', icon: Icons.auto_awesome_outlined),
                        ),

                        if (!_isSidebarCollapsed) const _SidebarSectionHeader(title: 'MY COLLECTION'),
                        WizardNavPulse(
                          active: ws?.step.targetRoute == 'My Collection' && _myCollectionTab == 'All',
                          child: _buildNavItem('All', icon: Icons.collections_bookmark_outlined, isSubItem: true, subItemKey: 'All'),
                        ),
                        _buildNavItem('Coins', icon: Icons.monetization_on_outlined, isSubItem: true, subItemKey: 'Coins'),
                        _buildNavItem('Currency Collection', icon: Icons.money_outlined, isSubItem: true, subItemKey: 'Currency'),
                        _buildNavItem('World and Specialty', icon: Icons.public_outlined, isSubItem: true, subItemKey: 'World & Specialty'),
                        _buildNavItem('Inventory', icon: Icons.inventory_2_outlined, isSubItem: true),

                        const SizedBox(height: 8),
                        WizardNavPulse(
                          active: ws?.step.targetRoute == 'My Wishlist',
                          child: _buildNavItem('My Wishlist', icon: Icons.favorite_outline),
                        ),

                        if (!_isSidebarCollapsed) const _SidebarSectionHeader(title: 'ASSET VAULT & TRANSFERS'),
                        _buildNavItem('Estate Planning', icon: Icons.account_balance_outlined),
                        _buildNavItem('Attorney Portal', icon: Icons.gavel_outlined),
                        _buildNavItem('Lateral Transfer', icon: Icons.vpn_key_outlined),
                        _buildNavItem('Claim Transfer', icon: Icons.download_for_offline_outlined),

                        if (!_isSidebarCollapsed) const _SidebarSectionHeader(title: 'ADD NEW COINS/NOTES/ETC.'),
                        WizardNavPulse(
                          active: ws?.step.targetRoute == 'Add New Coins',
                          child: _buildNavItem('Add new coins/notes/etc.', icon: Icons.add_circle_outline),
                        ),
                        _buildNavItem('Microscope Scanner', icon: Icons.camera_alt_outlined),
                        StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
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

                        if (!_isSidebarCollapsed) const _SidebarSectionHeader(title: 'AI TRAINING'),
                        _buildNavItem('AI Trainer Board', icon: Icons.how_to_vote_outlined),
                        // Admin-only: Grade Flag & Beta Feedback Inbox
                        if (email == 'jseaman1204@gmail.com' ||
                            email.endsWith('@numista.ai')) ...[
                          _buildNavItem('Admin Grade Flags',
                              icon: Icons.admin_panel_settings_outlined),
                          StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
                            stream: FirebaseFirestore.instance
                                .collection('beta_feedback')
                                .where('status', isEqualTo: 'OPEN')
                                .snapshots(),
                            builder: (context, snapshot) {
                              final openCount = snapshot.data?.docs.length ?? 0;
                              return _buildNavItem(
                                'Beta Feedback Inbox',
                                icon: Icons.rate_review_outlined,
                                badgeCount: openCount,
                              );
                            },
                          ),
                        ],

                        if (!_isSidebarCollapsed) const _SidebarSectionHeader(title: 'NUMISMATIC RESEARCH'),
                        _buildNavItem('Error Library', icon: Icons.bug_report_outlined),
                        _buildNavItem('Glossary Academy', icon: Icons.school_outlined),
                        _buildNavItem('Coin Search', icon: Icons.manage_search_outlined),
                        _buildNavItem('AI Deepdive', icon: Icons.psychology_outlined),

                        const SizedBox(height: 8),
                        _buildNavItem('Settings & Backup', icon: Icons.settings_outlined),
                        const _SidebarDivider(),
                        _buildNavItem('Our Team', icon: Icons.people_outline),
                        _buildNavItem('Customer Service', icon: Icons.support_agent_outlined),
                        _buildNavItem('🔍 Numista Lookup', icon: Icons.search_outlined),
                      ],
                    ),
                  ),
                ),
                // ── Morgan sidebar button ──────────────────────────────────
                if (!_isSidebarCollapsed)
                  Padding(
                    padding: const EdgeInsets.fromLTRB(8, 0, 8, 6),
                    child: _MorganSidebarButton(onTap: _showMorganDialog),
                  )
                else
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Tooltip(
                      message: 'Ask Morgan AI',
                      child: IconButton(
                        icon: Image.asset('assets/logo_owl.png', height: 28),
                        onPressed: _showMorganDialog,
                      ),
                    ),
                  ),

                if (!_isSidebarCollapsed) ...[
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
                        onPressed: () {
                          FeedbackTriggerObserver.instance.fire(
                            FeedbackTriggerEvent(
                              reason: FeedbackTriggerReason.manualFAB,
                              route: _activeRoute,
                              pageTitle: _activeRoute,
                              userName: AuthService.displayName,
                            ),
                          );
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
                          foregroundColor: isDark ? Colors.white70 : const Color(0xFF475569),
                          side: BorderSide(color: isDark ? Colors.white24 : Colors.black26),
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
                ] else ...[
                  Tooltip(
                    message: AuthService.isGuest ? 'Exit Guest' : 'Sign Out',
                    child: IconButton(
                      icon: const Icon(Icons.logout, size: 18),
                      onPressed: () => _confirmSignOut(context),
                    ),
                  ),
                  const SizedBox(height: 8),
                ],
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
                    Expanded(child: _wrapBodyWithMaxWidth(_buildBody(), _activeRoute)),
                  ],
                ),
                WizardOverlay(
                  onCreateAccount: () {
                    Navigator.of(context).pushReplacement(
                      MaterialPageRoute(builder: (_) => const LoginScreen()),
                    );
                  },
                ),
                // Morgan guide panel — floats above screen when a guide is active
                MorganGuidePanel(
                  onSearch: _onMorganSearch,
                  onSearchResultTap: _handleMorganSearchResultTap,
                ),
                BetaFeedbackWidget(
                  currentRoute: _activeRoute,
                  pageTitle: _activeRoute,
                ),
                if (_isMorganPopoutOpen)
                  MorganChatPopout(
                    initialQuery: _popoutInitialQuery,
                    onClose: () => setState(() => _isMorganPopoutOpen = false),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }



  // ─── Nav item builder ────────────────────────────────────────────────────
  Widget _buildNavItem(String title, {
    IconData? icon,
    int badgeCount = 0,
    bool isSubItem = false,
    String? subItemKey,
  }) {
    final bool isActive = subItemKey != null
        ? (_activeRoute == 'My Collection' && _myCollectionTab == subItemKey)
        : (_activeRoute == title);
    final bool isDark = Theme.of(context).brightness == Brightness.dark;
    
    // Items without a backing screen are disabled
    final bool isEnabled = subItemKey != null
        ? true
        : const {
            'Home Dashboard',
            'My Collection',
            'Currency Collection',
            'Review Hub',
            'Microscope Scanner',
            'Coin Programs',
            'Coin Search',
            '🔍 Numista Lookup',
            'Add New Coins',
            'My Wishlist',
            'Estate Planning',
            'Attorney Portal',
            'Lateral Transfer',
            'AI Deepdive',
            'Human AI Trainer Review Board',
            'AI Trainer Board',
            'Admin: Grade Flags',
            'Settings & Backup',
            'Our Team',
            'Customer Service',
            'Inventory',
            'Error Library',
            'Glossary Academy',
          }.contains(title == 'Add new coins/notes/etc.' ? 'Add New Coins' : (title == 'Admin Grade Flags' ? 'Admin: Grade Flags' : title));

    final IconData effectiveIcon = icon ?? Icons.circle_outlined;

    if (_isSidebarCollapsed) {
      return Tooltip(
        message: title,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 4),
          child: InkWell(
            onTap: isEnabled
                ? () {
                    if (subItemKey != null) {
                      setState(() {
                        _activeRoute = 'My Collection';
                        _myCollectionTab = subItemKey;
                      });
                    } else if (title == 'Add new coins/notes/etc.') {
                      setState(() => _activeRoute = 'Add New Coins');
                    } else if (title == 'Admin Grade Flags') {
                      setState(() => _activeRoute = 'Admin: Grade Flags');
                    } else if (title == '🔍 Numista Lookup' || title == 'Numista Lookup') {
                      setState(() => _activeRoute = 'Coin Search');
                    } else if (title == 'AI Deepdive') {
                      if (MediaQuery.of(context).size.width >= 800) {
                        setState(() {
                          _isMorganPopoutOpen = !_isMorganPopoutOpen;
                          if (_isMorganPopoutOpen) {
                            _popoutInitialQuery = null;
                          }
                        });
                      } else {
                        setState(() => _activeRoute = title);
                      }
                    } else {
                      setState(() => _activeRoute = title);
                    }
                  }
                : null,
            borderRadius: BorderRadius.circular(8),
            child: Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: isActive
                    ? (isDark ? Colors.white.withAlpha(20) : Colors.black.withAlpha(15))
                    : Colors.transparent,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                effectiveIcon,
                size: 20,
                color: isActive
                    ? const Color(0xFFF63366)
                    : (isDark ? Colors.white70 : Colors.black54),
              ),
            ),
          ),
        ),
      );
    }

    return Opacity(
      opacity: isEnabled ? 1.0 : 0.45,
      child: InkWell(
        onTap: isEnabled
            ? () {
                if (subItemKey != null) {
                  setState(() {
                    _activeRoute = 'My Collection';
                    _myCollectionTab = subItemKey;
                  });
                } else if (title == 'Add new coins/notes/etc.') {
                  setState(() => _activeRoute = 'Add New Coins');
                } else if (title == 'Admin Grade Flags') {
                  setState(() => _activeRoute = 'Admin: Grade Flags');
                } else if (title == '🔍 Numista Lookup' || title == 'Numista Lookup') {
                  setState(() => _activeRoute = 'Coin Search');
                } else if (title == 'AI Deepdive') {
                  if (MediaQuery.of(context).size.width >= 800) {
                    setState(() {
                      _isMorganPopoutOpen = !_isMorganPopoutOpen;
                      if (_isMorganPopoutOpen) {
                        _popoutInitialQuery = null;
                      }
                    });
                  } else {
                    setState(() => _activeRoute = title);
                  }
                } else {
                  setState(() => _activeRoute = title);
                }
              }
            : null,
        borderRadius: BorderRadius.circular(6),
        child: Container(
          padding: EdgeInsets.symmetric(vertical: 8, horizontal: isSubItem ? 16 : 8),
          decoration: BoxDecoration(
            color: isActive
                ? (isDark ? Colors.white.withAlpha(20) : Colors.black.withAlpha(15))
                : Colors.transparent,
            borderRadius: BorderRadius.circular(6),
          ),
          child: Row(children: [
            if (icon != null)
              Icon(icon,
                  size: 17,
                  color: isActive
                      ? const Color(0xFFF63366)
                      : (isDark ? Colors.white54 : Colors.black54))
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
                        : (isDark ? Colors.white38 : Colors.black38),
                    width: isActive ? 4 : 1,
                  ),
                ),
              ),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                title,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  color: isActive
                      ? (isDark ? Colors.white : const Color(0xFF0F172A))
                      : (isDark ? Colors.white60 : const Color(0xFF475569)),
                  fontSize: 13,
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
    final isDark = Theme.of(ctx).brightness == Brightness.dark;
    final confirm = await showDialog<bool>(
      context: ctx,
      builder: (dctx) => AlertDialog(
        backgroundColor: isDark ? const Color(0xFF1A1D27) : Colors.white,
        title: Text('Sign Out',
            style: TextStyle(color: isDark ? Colors.white : const Color(0xFF0F172A))),
        content: Text(
            'Are you sure you want to sign out of your vault?',
            style: TextStyle(color: isDark ? Colors.white70 : const Color(0xFF475569))),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dctx, false),
            child: Text('Cancel',
                style: TextStyle(color: isDark ? Colors.white54 : Colors.grey)),
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
        child: Divider(
          color: Theme.of(context).brightness == Brightness.dark
              ? Colors.white.withAlpha(20)
              : Colors.black.withAlpha(20),
          thickness: 1,
        ),
      );
}

// ─── Sidebar section header ──────────────────────────────────────────────────
class _SidebarSectionHeader extends StatelessWidget {
  final String title;
  const _SidebarSectionHeader({required this.title});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Padding(
      padding: const EdgeInsets.only(left: 8, top: 22, bottom: 6),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 10.5,
          fontWeight: FontWeight.bold,
          color: isDark ? Colors.white38 : Colors.black45,
          letterSpacing: 0.8,
        ),
      ),
    );
  }
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

// ── Morgan FAB — floating owl button (mobile) ─────────────────────────────────
class _MorganFab extends StatefulWidget {
  final VoidCallback onTap;
  const _MorganFab({required this.onTap});

  @override
  State<_MorganFab> createState() => _MorganFabState();
}

class _MorganFabState extends State<_MorganFab>
    with SingleTickerProviderStateMixin {
  late final AnimationController _pulse;
  late final Animation<double> _scale;

  @override
  void initState() {
    super.initState();
    _pulse = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 1800));
    _scale = Tween<double>(begin: 1.0, end: 1.08).animate(
        CurvedAnimation(parent: _pulse, curve: Curves.easeInOut));
    _pulse.repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulse.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _scale,
      builder: (_, child) => Transform.scale(scale: _scale.value, child: child),
      child: Tooltip(
        message: 'Ask Morgan',
        child: GestureDetector(
          onTap: widget.onTap,
          child: Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: const LinearGradient(
                colors: [Color(0xFF0B3D6E), Color(0xFF0B5E8A)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              border: Border.all(color: const Color(0xFFD4A843), width: 1.5),
              boxShadow: [
                BoxShadow(
                    color: const Color(0xFF2DD4BF).withAlpha(100),
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
                    size: 26),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// ── Morgan sidebar button (desktop) ───────────────────────────────────────
class _MorganSidebarButton extends StatefulWidget {
  final VoidCallback onTap;
  const _MorganSidebarButton({required this.onTap});

  @override
  State<_MorganSidebarButton> createState() => _MorganSidebarButtonState();
}

class _MorganSidebarButtonState extends State<_MorganSidebarButton> {
  bool _hovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter:  (_) => setState(() => _hovered = true),
      onExit:   (_) => setState(() => _hovered = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 7),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(8),
            color: _hovered
                ? const Color(0xFF2DD4BF).withAlpha(20)
                : const Color(0xFF0B3D6E).withAlpha(120),
            border: Border.all(
              color: _hovered
                  ? const Color(0xFFD4A843).withAlpha(200)
                  : const Color(0xFFD4A843).withAlpha(80),
              width: 1,
            ),
            boxShadow: _hovered
                ? [BoxShadow(
                    color: const Color(0xFF2DD4BF).withAlpha(40),
                    blurRadius: 8)]
                : [],
          ),
          child: Row(
            children: [
              // Mini owl avatar
              Container(
                width: 26,
                height: 26,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                      color: const Color(0xFFD4A843).withAlpha(150), width: 1),
                ),
                child: ClipOval(
                  child: Image.asset(
                    'assets/morgan_avatar.png',
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) => const Icon(
                        Icons.smart_toy_rounded,
                        color: Color(0xFF2DD4BF),
                        size: 14),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Ask Morgan',
                        style: TextStyle(
                            color: Colors.white,
                            fontSize: 11,
                            fontWeight: FontWeight.w600)),
                    Text('Your AI guide',
                        style: TextStyle(
                            color: Color(0xFF2DD4BF),
                            fontSize: 9)),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right_rounded,
                  color: Color(0xFFD4A843), size: 14),
            ],
          ),
        ),
      ),
    );
  }
}
