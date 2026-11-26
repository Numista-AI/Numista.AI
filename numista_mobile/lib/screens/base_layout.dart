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
import 'analytics_screen.dart';
import 'microscope_scan_screen.dart';
import 'program_manager_screen.dart';
import 'settings_screen.dart';
import 'our_team_screen.dart';
import 'review_hub_screen.dart';
import 'add_coins_hub.dart';
import 'wishlist_screen.dart';
import 'estate_planning_screen.dart';
import 'human_ai_trainer_screen.dart';
import 'customer_service_screen.dart';
import 'ai_chat_screen.dart';
import '../utils/sold_item.dart';
import 'admin_grade_flags_screen.dart';
import 'supplies_screen.dart';
import 'currency_collection_screen.dart';
import 'welcome_screen.dart';  // for WelcomeScreen.pendingRoute
import 'add_world_item_screen.dart';
import 'attorney_portal_screen.dart';
import 'lateral_transfer_screen.dart';
import '../services/claim_link_service.dart';
import 'admin_feedback_screen.dart';
import 'my_tickets_screen.dart';
import 'support_portal_screen.dart';
import '../models/coin_model.dart';
import '../widgets/morgan_owl_avatar.dart';
import '../widgets/auth_gate.dart';
import '../services/feedback_trigger_observer.dart';
import '../services/beta_feedback_service.dart' show FeedbackTriggerReason;
import '../widgets/morgan_guide_flow.dart';
import '../widgets/morgan_chat_popout.dart';
import '../services/morgan_screen_state_registry.dart';
import '../services/morgan_action_bus.dart';
import '../services/morgan_proactive_rescue_observer.dart';
import '../widgets/morgan_spotlight_overlay.dart';
import '../widgets/morgan_privacy_mask.dart';
import '../widgets/morgan_settings_panel.dart'
    show MorganSettingsService, showMorganConsentModalIfNeeded;
import 'coin_detail_screen.dart';
import 'catalog/catalog_browse_screen.dart';
import '../theme/numista_theme.dart';
import '../services/ui_variant_service.dart';
import '../utils/numista_error_helper.dart';


class BaseLayout extends StatefulWidget {
  final bool isDemoMode;
  @visibleForTesting
  final bool testSkipFirebase;
  @visibleForTesting
  final Widget Function(String route, String? aiInitialQuery, String myCollectionTab)? testRouteBuilder;
  @visibleForTesting
  final Widget Function(String? initialQuery, VoidCallback onClose)? testPopoutBuilder;

  const BaseLayout({
    super.key,
    this.isDemoMode = false,
    this.testSkipFirebase = false,
    this.testRouteBuilder,
    this.testPopoutBuilder,
  });

  @override
  State<BaseLayout> createState() => _BaseLayoutState();
}

class _BaseLayoutState extends State<BaseLayout> {
  final GlobalKey _repaintKey = GlobalKey();
  String _activeRoute = 'Home Dashboard';
  // ITEM 5: Route history for browser back-button support.
  // Starts with 'Home Dashboard' so Back from the second screen returns Home.
  final List<String> _routeHistory = ['Home Dashboard'];
  String _myCollectionTab = 'All';
  // Optional pre-populated AI query — set when the user taps AI Deep Dive
  // on a specific coin. Consumed once and then cleared.
  String? _aiInitialQuery;
  int _aiInitialQueryNonce = 0;
  String? _aiInitialNacCode;
  String? _catalogInitialTab;
  String? _catalogInitialNacCode;
  String? _addCoinsInitialTabName;
  String? _programManagerInitialId;
  bool _isMorganPopoutOpen = false;
  bool _isMorganDocked = true;
  String? _popoutInitialQuery;
  int _popoutInitialQueryNonce = 0;
  bool _isSidebarCollapsed = false;
  bool _desktopHotkeysEnabled = true;
  FocusNode? _previousFocusNode;
  String? _openAccordionGroup; // null | 'Research' | 'Estate & Transfers' | 'Settings & Help'
  bool _isPhoneMenuOpen = false;
  String? _phoneDrillGroup; // null | 'Research' | 'Estate & Transfers' | 'Settings & Help'
  int _reviewQueueCount = 0;
  bool _isReviewCountLoading = true;

  void _openFeedbackAction() {
    FeedbackTriggerObserver.instance.fire(
      FeedbackTriggerEvent(
        reason: FeedbackTriggerReason.manualFAB,
        route: _activeRoute,
        pageTitle: _activeRoute,
        userName: AuthService.displayName,
      ),
    );
  }

  // ── Show Morgan overlay — opens unified Morgan Co-Pilot window ───────────
  void _showMorganDialog() {
    final gs = MorganGuideService.current.value;
    if (MediaQuery.of(context).size.width < 800) {
      // Mobile: Switch tab to AI Deepdive
      _navigateTo('AI Deepdive');
      return;
    }

    // Desktop: Always open/toggle the SINGLE unified Morgan Co-Pilot window
    setState(() {
      _isMorganPopoutOpen = gs != null ? true : !_isMorganPopoutOpen;
      if (_isMorganPopoutOpen) {
        _popoutInitialQuery = null;
      }
    });
    if (_isMorganPopoutOpen) {
      showMorganConsentModalIfNeeded(context);
    }
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
            if (isSoldItem(data)) return false; // R3: Sold items excluded from active search
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
          SnackBar(content: Text(NumistaErrorHelper.toUserFriendly(e))),
        );
      }
    }
  }

  void _onMorganGuideStateChanged() {
    if (!mounted) return;
    if (MorganGuideService.current.value != null &&
        morganGuideUnifiedWithCopilot &&
        MediaQuery.of(context).size.width >= 800 &&
        !_isMorganPopoutOpen) {
      setState(() => _isMorganPopoutOpen = true);
    }
  }

  @override
  void initState() {
    super.initState();
    _loadDefaultTab();
    _loadDesktopPrefs();

    MorganScreenStateRegistry.instance.repaintBoundaryKey = _repaintKey;
    MorganActionBus.instance.onNavigateToRoute = (route, {subTab}) async {
      _navigateTo(route);
    };
    MorganGuideService.current.addListener(_onMorganGuideStateChanged);
    MorganSettingsService.instance.load().then((_) {
      if (mounted) {
        setState(() {
          _isMorganDocked = MorganSettingsService.instance.dockToSide;
        });
      }
    });
 
    // ── Morgan deep-link: if the user tapped a tile in the greeter,
    // navigate directly to that screen instead of Home Dashboard.
    final morganRoute = WelcomeScreen.pendingRoute;
    if (morganRoute != null) {
      WelcomeScreen.pendingRoute = null;  // consume once
      _activeRoute = morganRoute;
      _addCoinsInitialTabName = WelcomeScreen.pendingTabName;
      WelcomeScreen.pendingTabName = null;
    }

    // Claim link (#/claim?t=TOKEN): after sign-in, open the Claim tab. The token stays in memory only.
    if (ClaimLinkService.hasPendingToken && !widget.testSkipFirebase && !widget.isDemoMode &&
        !GuestSeedService.isBrowseDemoMode) {
      _activeRoute = 'Claim Transfer';
    }

    // Load eBay credentials from Firestore into SharedPreferences.
    // Skip in demo mode to enforce zero Firestore network reads.
    if (!widget.testSkipFirebase && !widget.isDemoMode && !GuestSeedService.isBrowseDemoMode) {
      EpnService.loadFromFirestore();
    }
    // Run US Mint data normalization silently in background for all accounts.
    // Only processes coins that haven't been normalized yet.
    if (!widget.testSkipFirebase && !AuthService.isGuest && !widget.isDemoMode && !GuestSeedService.isBrowseDemoMode && AuthService.isSignedIn) {
      CoinNormalizerService.runForUser();
    }
    // Auto-start the guided wizard for first-time Guest users.
    // Demo mode gets a read-only experience without the wizard.
    if (!widget.testSkipFirebase && AuthService.isGuest && !widget.isDemoMode) {
      WizardService.start(
        'guest',
        onNavigate: (route) {
          if (mounted) _navigateTo(route);
        },
      );
    } else {
      // Register the navigate callback even if wizard isn't active yet,
      // so a future wizard invocation can still drive the nav.
      WizardService.setNavigateCallback(
        (route) {
          if (mounted) _navigateTo(route);
        },
      );
    }

    MorganScreenStateRegistry.instance.markScreenHydrated(
      route: _activeRoute,
      hydrated: _activeRoute != 'Microscope Scanner',
    );
  }

  @override
  void dispose() {
    MorganGuideService.current.removeListener(_onMorganGuideStateChanged);
    super.dispose();
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

  String _resolveRouteAlias(String rawRoute) {
    if (rawRoute == 'Add new coins/notes/etc.') return 'Add New Coins';
    if (rawRoute == 'Admin Grade Flags') return 'Admin: Grade Flags';
    if (rawRoute == '🔍 Numista Lookup' ||
        rawRoute == 'Numista Lookup' ||
        rawRoute == 'Coin Search' ||
        rawRoute == 'U.S. Numismatics Catalog') {
      return 'Catalog of American Numismatics';
    }
    if (rawRoute == 'Ask Morgan') {
      return 'AI Deepdive';
    }
    return rawRoute;
  }

  /// All prior desktop width >= 800 intercepts for the 'AI Deepdive' / 'Ask Morgan' route have been removed; Ask Morgan always lands in the main pane.
  void _navigateTo(
    String route, {
    String? subTab,
    String? aiInitialQuery,
    String? aiInitialNacCode,
    bool pushHistory = true,
  }) {
    MorganProactiveRescueObserver.instance.recordUserActivity();
    final aliased = _resolveRouteAlias(route);
    String resolvedRoute = aliased;
    final String resolvedSubTab = subTab ?? '';

    setState(() {
      if (subTab != null) {
        _myCollectionTab = subTab;
      }
      if (aiInitialQuery != null) {
        final trimmed = aiInitialQuery.trim();
        if (trimmed.isNotEmpty) {
          _aiInitialQuery = trimmed;
          _aiInitialQueryNonce++;
        }
      } else if (resolvedRoute != 'AI Deepdive') {
        _aiInitialQuery = null;
        _aiInitialNacCode = null;
      }
      if (aiInitialNacCode != null) {
        _aiInitialNacCode = aiInitialNacCode;
      }
      if (resolvedRoute == 'Error Library') {
        _catalogInitialTab = 'errors';
        resolvedRoute = 'Catalog of American Numismatics';
      } else if (resolvedRoute == 'Upcoming Releases') {
        _catalogInitialTab = 'upcoming';
        resolvedRoute = 'Catalog of American Numismatics';
      } else if (resolvedRoute == 'Glossary Academy') {
        _catalogInitialTab = 'glossary';
        resolvedRoute = 'Catalog of American Numismatics';
      } else if (resolvedRoute == 'Catalog of American Numismatics' && subTab != null) {
        _catalogInitialTab = subTab;
      }
      if (aliased.startsWith('Coin Programs:')) {
        final parts = aliased.split(':');
        _programManagerInitialId = parts[1];
        resolvedRoute = 'Coin Programs';
      }
      _activeRoute = resolvedRoute;
      if (resolvedRoute == 'AI Deepdive' && _isMorganPopoutOpen) {
        // Main pane is now full-screen AI Deepdive; close side popout so two
        // AiChatScreen instances are never mounted simultaneously.
        _isMorganPopoutOpen = false;
        _popoutInitialQuery = null;
      }
      if (pushHistory &&
          (_routeHistory.isEmpty || _routeHistory.last != resolvedRoute)) {
        _routeHistory.add(resolvedRoute);
        if (_routeHistory.length > 50) {
          _routeHistory.removeAt(0);
        }
      }
    });

    MorganScreenStateRegistry.instance.beginRouteTransition(
      resolvedRoute,
      subTab: resolvedSubTab,
      hydratedImmediately: false,
    );
    MorganScreenStateRegistry.instance.markScreenHydrated(
      route: resolvedRoute,
      subTab: resolvedSubTab,
      hydrated: resolvedRoute != 'Microscope Scanner',
    );
  }

  Widget _buildBody() {
    Widget bodyWidget;
    // Phase A: alt site variant check
    if (UiVariantService.current == UiVariant.alt && _activeRoute == 'Home Dashboard') {
      // For now Phase A is in place — alt shows a banner indicating alt mode.
      // Full alt screens are Phase B/C (need Eric's YES).
      // We insert a thin info banner at the top of Home Dashboard only.
      bodyWidget = _AltSiteBanner(child: _buildBodyForRoute());
    } else {
      bodyWidget = _buildBodyForRoute();
    }
    if (MorganPrivacyMask.isRouteSensitive(_activeRoute)) {
      return MorganPrivacyMask(reason: _activeRoute, child: bodyWidget);
    }
    return bodyWidget;
  }

  Widget _buildBodyForRoute() {
    if (widget.testRouteBuilder != null) {
      final consumedQuery = _activeRoute == 'AI Deepdive' ? _aiInitialQuery : null;
      if (_activeRoute == 'AI Deepdive') {
        _aiInitialQuery = null;
      }
      return widget.testRouteBuilder!(_activeRoute, consumedQuery, _myCollectionTab);
    }
    switch (_activeRoute) {
      case 'Home Dashboard':
        return PrimaryScrollController.none(
          child: HomeDashboard(
            testStream: widget.testSkipFirebase
                ? Stream<CombinedDashboardData>.value(
                    CombinedDashboardData(
                      coins: const [],
                      currency: const [],
                      worldItems: const [],
                    ),
                  )
                : null,
            onAskMorgan: () {
              if (MediaQuery.of(context).size.width >= 800) {
                setState(() {
                  _isMorganPopoutOpen = true;
                  _popoutInitialQuery = null;
                });
                showMorganConsentModalIfNeeded(context);
              } else {
                _navigateTo('AI Deepdive');
              }
            },
            onAskMorganWithQuery: (query) {
              final trimmed = query.trim();
              if (trimmed.isEmpty) return;
              if (MediaQuery.of(context).size.width >= 800) {
                setState(() {
                  _isMorganPopoutOpen = true;
                  _popoutInitialQuery = trimmed;
                  _popoutInitialQueryNonce++;
                });
              } else {
                _navigateTo('AI Deepdive', aiInitialQuery: trimmed);
              }
            },
            onNavigateToCollection: () => _navigateTo('My Collection'),
            onAddCoin: () => _navigateTo('Add New Coins'),
            onTakePhoto: () => _navigateTo('Take a photo'),
            onOpenReview: () => _navigateTo('Review Hub'),
            onOpenPrograms: () => _navigateTo('Coin Programs'),
            reviewQueueCount: _reviewQueueCount,
            isReviewCountLoading: _isReviewCountLoading,
          ),
        );
      case 'Analytics':
        return AnalyticsScreen(
          onExpandMorganToFullChat: () => _navigateTo('AI Deepdive'),
        );
      case 'My Collection':
        return MyCollectionScreen(
          initialTab: _myCollectionTab,
          onNavigate: _navigateTo,
          onNavigateWithQuery: (route, query) =>
              _navigateTo(route, aiInitialQuery: query),
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
      case 'Take a photo':
      case 'AI Photo Identification':
        return AddCoinsHub(
          onNavigate: _navigateTo,
          initialTabName: 'camera',
          showCameraFullScreen: true,
        );
      case 'World & Specialty':
        return AddWorldItemScreen(
          onNavigate: _navigateTo,
        );
      case 'AI Deepdive':
      case 'Ask Morgan':
        // Passed through with nonce; cleared in onInitialQueryConsumed or on route exit.
        return AiChatScreen(
          initialQuery: _aiInitialQuery,
          initialQueryNonce: _aiInitialQueryNonce,
          onInitialQueryConsumed: (consumedNonce) {
            if (_aiInitialQueryNonce == consumedNonce && _aiInitialQuery != null) {
              _aiInitialQuery = null;
              _aiInitialNacCode = null;
            }
          },
          initialNacCode: _aiInitialNacCode,
          testSkipFirebase: widget.testSkipFirebase,
          onNavigateToCollection: () => _navigateTo('My Collection'),
          onOpenCatalogNac: (nacCode) {
            setState(() {
              _catalogInitialNacCode = nacCode;
            });
            _navigateTo('Catalog of American Numismatics');
          },
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
        if (!AuthService.isAdmin) {
          return const Center(child: Text('Admin access required.'));
        }
        return const AdminGradeFlagsScreen();
      case 'Admin: Beta Dashboard':
      case 'Beta Feedback Inbox':
      case 'Feedback Inbox':
        return const AdminFeedbackScreen();
      case 'Customer Service':
        return CustomerServiceScreen(
          onNavigateToTickets: () => _navigateTo('My Tickets'),
        );
      case 'My Tickets':
        return const MyTicketsScreen();
      case 'Admin: Support Portal':
        return const SupportPortalScreen();

      case 'Inventory':
        return const SuppliesScreen();
      case 'Catalog of American Numismatics':
      case 'Coin Search':
        final catTab = _catalogInitialTab;
        final catNac = _catalogInitialNacCode;
        _catalogInitialTab = null;
        _catalogInitialNacCode = null;
        return CatalogBrowseScreen(initialTab: catTab, initialNacCode: catNac);
      case 'Currency Collection':
        return const CurrencyCollectionScreen();
      case 'Error Library':
        return const CatalogBrowseScreen(initialTab: 'errors');
      case 'Glossary Academy':
        return const CatalogBrowseScreen(initialTab: 'glossary');
      case 'Upcoming Releases':
        return const CatalogBrowseScreen(initialTab: 'upcoming');
      default:
        return const _UnderConstruction();
    }
  }

  Widget _wrapBodyWithMaxWidth(Widget body, String route) {
    final double maxWidth;
    switch (route) {
      case 'Add New Coins':
      case 'Take a photo':
      case 'AI Photo Identification':
        maxWidth = 1100.0;
        break;
      case 'Analytics':
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
      case 'Upcoming Releases':
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
    final user = widget.testSkipFirebase ? null : FirebaseAuth.instance.currentUser;
    final displayName = user?.displayName?.isNotEmpty == true
        ? user!.displayName!
        : (user?.email?.split('@').first ?? 'Collector');
    final email = user?.email ?? '';

    final rootContent = StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
      stream: !widget.testSkipFirebase && email.isNotEmpty
          ? FirebaseFirestore.instance
              .collection('users')
              .doc(email)
              .collection('review_queue')
              .snapshots()
          : const Stream.empty(),
      builder: (context, reviewSnap) {
        _isReviewCountLoading =
            !widget.testSkipFirebase &&
            email.isNotEmpty &&
            reviewSnap.connectionState == ConnectionState.waiting &&
            !reviewSnap.hasData;
        final rawDocs = reviewSnap.data?.docs ?? const [];
        _reviewQueueCount = rawDocs.where((d) {
          final status = (d.data()['status'] ?? 'pending').toString().toLowerCase();
          return status == 'pending';
        }).length;

        return LayoutBuilder(
          builder: (context, constraints) {
            final isMobile = constraints.maxWidth < 800;
            return isMobile
                ? _buildMobileLayout(email, displayName)
                : _buildDesktopLayout(email, displayName);
          },
        );
      },
    );

    // ITEM 5: Intercept browser Back button. PopScope prevents the Flutter
    // Navigator from popping the root route (which exits the app / shows a
    // blank tab on desktop web). Instead we walk our own _routeHistory stack.
    Widget body = PopScope<Object?>(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        if (didPop) return; // already popped — nothing to do
        if (_isMorganPopoutOpen) {
          setState(() {
            _isMorganPopoutOpen = false;
            _popoutInitialQuery = null;
          });
          return;
        }
        if (_routeHistory.length > 1) {
          _routeHistory.removeLast();
          final previous = _routeHistory.last;
          _navigateTo(previous, pushHistory: false);
        } else {
          // At root (Home Dashboard) — show a friendly "use X to close" hint
          // on desktop web instead of silently doing nothing.
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text("You're on the Home screen. "
                  'Close the browser tab to exit Numista.AI.'),
              duration: Duration(seconds: 3),
              behavior: SnackBarBehavior.floating,
            ),
          );
        }
      },
      child: rootContent,
    );

    if (!_desktopHotkeysEnabled) {
      return body;
    }

    return CallbackShortcuts(
      bindings: <ShortcutActivator, VoidCallback>{
        SingleActivator(LogicalKeyboardKey.keyK, control: true): () =>
            _navigateTo('Catalog of American Numismatics'),
        SingleActivator(LogicalKeyboardKey.keyK, meta: true): () =>
            _navigateTo('Catalog of American Numismatics'),
        SingleActivator(LogicalKeyboardKey.keyM, control: true): _showMorganDialog,
        SingleActivator(LogicalKeyboardKey.keyM, meta: true): _showMorganDialog,
        SingleActivator(LogicalKeyboardKey.escape): () {
          if (_isMorganPopoutOpen) {
            setState(() => _isMorganPopoutOpen = false);
            _previousFocusNode?.requestFocus();
          }
        },
      },
      child: body,
    );
  }

  // ─── Mobile layout: labeled Menu header + full-screen drill-in overlay ───
  Widget _buildMobileLayout(String email, String displayName) {
    final badgeCount = _isReviewCountLoading ? 0 : _reviewQueueCount;

    return Scaffold(
      backgroundColor: const Color(0xFFEEF3F8),
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
                      AuthGate.navigateTo(context, initialAuthTab: 1);
                    }),
                  if (!widget.testSkipFirebase && AuthService.isGuest) _GuestBanner(),
                  // Phone top bar: Numista.Ai + labeled Menu button (>= 56px)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                    decoration: const BoxDecoration(
                      color: Color(0xFFFFFFFF),
                      border: Border(bottom: BorderSide(color: Color(0xFFD5DEEA))),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        RichText(
                          text: const TextSpan(
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.w800,
                              color: Color(0xFF0B1A2E),
                            ),
                            children: [
                              TextSpan(text: 'Numista.'),
                              TextSpan(
                                text: 'Ai',
                                style: TextStyle(color: Color(0xFF1D4F91)),
                              ),
                            ],
                          ),
                        ),
                        OutlinedButton.icon(
                          onPressed: () => setState(() {
                            _isPhoneMenuOpen = true;
                            _phoneDrillGroup = null;
                          }),
                          icon: const Icon(Icons.menu, color: Color(0xFF0B1A2E), size: 22),
                          label: const Text(
                            'Menu',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF0B1A2E),
                            ),
                          ),
                          style: OutlinedButton.styleFrom(
                            minimumSize: const Size(110, 56),
                            side: const BorderSide(color: Color(0xFF1D4F91), width: 1.5),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          ),
                        ),
                      ],
                    ),
                  ),
                  Expanded(child: _buildBody()),
                ],
              ),
            ),
            if (_isPhoneMenuOpen)
              Positioned.fill(
                child: PhoneMenuOverlay(
                  displayName: displayName,
                  activeRoute: _activeRoute,
                  reviewCount: badgeCount,
                  isReviewLoading: _isReviewCountLoading,
                  drillGroup: _phoneDrillGroup,
                  isAdmin: !widget.testSkipFirebase && AuthService.isAdmin,
                  onClose: () => setState(() {
                    _isPhoneMenuOpen = false;
                    _phoneDrillGroup = null;
                  }),
                  onBack: () => setState(() => _phoneDrillGroup = null),
                  onOpenGroup: (group) => setState(() => _phoneDrillGroup = group),
                  onSelectRoute: (route) {
                    setState(() {
                      _isPhoneMenuOpen = false;
                      _phoneDrillGroup = null;
                    });
                    if (route == '__SEND_FEEDBACK__') {
                      _openFeedbackAction();
                    } else {
                      _navigateTo(route);
                    }
                  },
                ),
              ),
            WizardOverlay(
              onCreateAccount: () {
                AuthGate.navigateTo(context, initialAuthTab: 1);
              },
            ),
            // Morgan guide panel — floats above screen when a guide is active
            MorganGuidePanel(
              onSearch: _onMorganSearch,
              onSearchResultTap: _handleMorganSearchResultTap,
            ),
          ],
        ),
      ),
    );
  }

  // ─── Desktop/tablet layout: sidebar ──────────────────────────────────────
  Widget _buildDesktopLayout(String email, String displayName) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final sidebarWidth = _isSidebarCollapsed ? 72.0 : 280.0;
    final badgeCount = _isReviewCountLoading ? 0 : _reviewQueueCount;

    return Scaffold(
      backgroundColor: const Color(0xFFEEF3F8),
      body: Row(
        children: [
          // ─── Sidebar ─────────────────────────────────────────────────────
          AnimatedContainer(
            duration: const Duration(milliseconds: 200),
            width: sidebarWidth,
            decoration: const BoxDecoration(
              color: Color(0xFFF7F9FC),
              border: Border(
                right: BorderSide(color: Color(0xFFD5DEEA)),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 12),
                // Sidebar header: Numista.Ai + collapse toggle
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  child: Row(
                    mainAxisAlignment: _isSidebarCollapsed
                        ? MainAxisAlignment.center
                        : MainAxisAlignment.spaceBetween,
                    children: [
                      if (!_isSidebarCollapsed)
                        Flexible(
                          child: FittedBox(
                            fit: BoxFit.scaleDown,
                            alignment: Alignment.centerLeft,
                            child: RichText(
                              text: const TextSpan(
                                style: TextStyle(
                                  fontSize: 24,
                                  fontWeight: FontWeight.w800,
                                  color: Color(0xFF0B1A2E),
                                ),
                                children: [
                                  TextSpan(text: 'Numista.'),
                                  TextSpan(
                                    text: 'Ai',
                                    style: TextStyle(color: Color(0xFF1D4F91)),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        )
                      else
                        Flexible(
                          child: Image.asset('assets/logo_owl.png',
                              height: 36, fit: BoxFit.contain),
                        ),
                      SizedBox(
                        width: 48,
                        height: 48,
                        child: IconButton(
                          constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
                          icon: Icon(
                            _isSidebarCollapsed
                                ? Icons.chevron_right
                                : Icons.chevron_left,
                            color: const Color(0xFF0B1A2E),
                            size: 22,
                          ),
                          tooltip: _isSidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar',
                          onPressed: _toggleSidebar,
                        ),
                      ),
                    ],
                  ),
                ),
                if (!_isSidebarCollapsed) ...[
                  Padding(
                    padding: const EdgeInsets.fromLTRB(12, 2, 12, 10),
                    child: Text(
                      'Hello, $displayName',
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w500,
                        color: Color(0xFF0B1A2E),
                      ),
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.fromLTRB(12, 0, 12, 12),
                    child: ElevatedButton.icon(
                      onPressed: () => _navigateTo('Add New Coins'),
                      icon: const Icon(Icons.add_circle_outline, size: 22),
                      label: const Text(
                        'Add to collection',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF1D4F91),
                        foregroundColor: Colors.white,
                        minimumSize: const Size(double.infinity, 56),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        elevation: 0,
                      ),
                    ),
                  ),
                ] else ...[
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                    child: Tooltip(
                      message: 'Add to collection',
                      child: IconButton(
                        onPressed: () => _navigateTo('Add New Coins'),
                        icon: const Icon(Icons.add_circle, color: Color(0xFF1D4F91), size: 28),
                        constraints: const BoxConstraints(minWidth: 56, minHeight: 56),
                      ),
                    ),
                  ),
                ],

                Expanded(
                  child: Scrollbar(
                    thumbVisibility: true,
                    child: ValueListenableBuilder<WizardState?>(
                      valueListenable: WizardService.state,
                      builder: (context, ws, _) => ListView(
                        padding: const EdgeInsets.symmetric(horizontal: 10),
                        children: [
                          _buildNavItem('Home Dashboard',
                              displayLabel: 'Home', icon: Icons.home_outlined),
                          WizardNavPulse(
                            active: ws?.step.targetRoute == 'My Collection',
                            child: _buildNavItem('My Collection',
                                icon: Icons.layers_outlined),
                          ),
                          _buildNavItem('Catalog of American Numismatics',
                              displayLabel: 'Catalog',
                              icon: Icons.auto_stories_outlined),
                          _buildNavItem('Analytics',
                              icon: Icons.insights_rounded),
                          WizardNavPulse(
                            active: ws?.step.targetRoute == 'Coin Programs',
                            child: _buildNavItem('Coin Programs',
                                icon: Icons.article_outlined),
                          ),
                          WizardNavPulse(
                            active: ws?.step.targetRoute == 'My Wishlist',
                            child: _buildNavItem('My Wishlist',
                                displayLabel: 'Wishlist',
                                icon: Icons.favorite_border),
                          ),
                          _buildNavItem('Review Hub',
                              displayLabel: 'Review',
                              icon: Icons.fact_check_outlined,
                              badgeCount: badgeCount),
                          const SizedBox(height: 6),
                          if (!_isSidebarCollapsed) ...[
                            SidebarAccordionGroup(
                              title: 'Research',
                              icon: Icons.search,
                              isExpanded: _openAccordionGroup == 'Research',
                              onToggle: () => setState(() {
                                _openAccordionGroup =
                                    _openAccordionGroup == 'Research' ? null : 'Research';
                              }),
                              children: _kNavGroups['Research']!
                                  .map((item) => _buildNavItem(item.route,
                                      displayLabel: item.label, icon: item.icon))
                                  .toList(),
                            ),
                            SidebarAccordionGroup(
                              title: 'Estate & Transfers',
                              icon: Icons.description_outlined,
                              isExpanded: _openAccordionGroup == 'Estate & Transfers',
                              onToggle: () => setState(() {
                                _openAccordionGroup =
                                    _openAccordionGroup == 'Estate & Transfers'
                                        ? null
                                        : 'Estate & Transfers';
                              }),
                              children: _kNavGroups['Estate & Transfers']!
                                  .map((item) => _buildNavItem(item.route,
                                      displayLabel: item.label, icon: item.icon))
                                  .toList(),
                            ),
                            SidebarAccordionGroup(
                              title: 'Settings & Help',
                              icon: Icons.settings_outlined,
                              isExpanded: _openAccordionGroup == 'Settings & Help',
                              onToggle: () => setState(() {
                                _openAccordionGroup =
                                    _openAccordionGroup == 'Settings & Help'
                                        ? null
                                        : 'Settings & Help';
                              }),
                              children: [
                                ..._kNavGroups['Settings & Help']!.map((item) {
                                  if (item.route == '__SEND_FEEDBACK__') {
                                    return _buildNavItem(
                                      item.route,
                                      displayLabel: item.label,
                                      icon: item.icon,
                                      onCustomTap: _openFeedbackAction,
                                    );
                                  }
                                  return _buildNavItem(item.route,
                                      displayLabel: item.label, icon: item.icon);
                                }),
                                if (!widget.testSkipFirebase && AuthService.isAdmin) ...[
                                  const Divider(color: Color(0xFFD5DEEA)),
                                  _buildNavItem('AI Trainer Board',
                                      icon: Icons.how_to_vote_outlined),
                                  _buildNavItem('Admin Grade Flags',
                                      icon: Icons.admin_panel_settings_outlined),
                                  _buildNavItem('Feedback Inbox',
                                      icon: Icons.rate_review_outlined),
                                  _buildNavItem('Admin: Support Portal',
                                      icon: Icons.support_agent_outlined),
                                ],
                              ],
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                ),
                // ── Morgan sidebar button (hidden on Home and Analytics — Single-Morgan-Per-Screen rule) ──
                if (_activeRoute != 'Home Dashboard' && _activeRoute != 'Home' && _activeRoute != 'Analytics') ...[
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
                          icon: const MorganOwlAvatar(size: 28),
                          onPressed: _showMorganDialog,
                        ),
                      ),
                    ),
                ],

                if (!_isSidebarCollapsed) ...[
                  Padding(
                    padding: const EdgeInsets.fromLTRB(8, 0, 8, 4),
                    child: SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Theme.of(context).brightness == Brightness.dark ? const Color(0xFF2A1F4E) : const Color(0xFFE0E7FF),
                          foregroundColor: Theme.of(context).brightness == Brightness.dark ? const Color(0xFFFFD700) : const Color(0xFF4338CA),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                          minimumSize: const Size(double.infinity, 48),
                          visualDensity: VisualDensity.standard,
                          elevation: 0,
                        ),
                        icon: Icon(Icons.feedback_outlined, size: 14, color: Theme.of(context).brightness == Brightness.dark ? const Color(0xFFFFD700) : const Color(0xFF4338CA)),
                        label: const Text(
                          'Send Feedback',
                          style: TextStyle(fontSize: NumistaTheme.textBodySm, fontWeight: FontWeight.w600),
                        ),
                        onPressed: () {
                          showDialog<String>(
                            context: context,
                            builder: (ctx) => AlertDialog(
                              title: const Text('How can we help?'),
                              contentPadding: const EdgeInsets.fromLTRB(24, 16, 24, 0),
                              content: Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  ListTile(
                                    leading: const Icon(Icons.rate_review_outlined,
                                        color: Color(0xFF1967D2)),
                                    title: const Text('Send general feedback',
                                        style: TextStyle(fontWeight: FontWeight.w600)),
                                    subtitle: const Text(
                                        'Ratings, suggestions, compliments',
                                        style: TextStyle(fontSize: NumistaTheme.textCaption)),
                                    onTap: () => Navigator.pop(ctx, 'feedback'),
                                  ),
                                  const Divider(height: 1),
                                  ListTile(
                                    leading: const Icon(Icons.confirmation_number_outlined,
                                        color: Color(0xFFE37400)),
                                    title: const Text('Report a problem / get help',
                                        style: TextStyle(fontWeight: FontWeight.w600)),
                                    subtitle: const Text(
                                        'Opens the support ticket form',
                                        style: TextStyle(fontSize: NumistaTheme.textCaption)),
                                    onTap: () => Navigator.pop(ctx, 'ticket'),
                                  ),
                                ],
                              ),
                              actions: [
                                TextButton(
                                  onPressed: () => Navigator.pop(ctx),
                                  child: const Text('Cancel'),
                                ),
                              ],
                            ),
                          ).then((choice) {
                            if (choice == 'feedback') {
                              FeedbackTriggerObserver.instance.fire(
                                FeedbackTriggerEvent(
                                  reason: FeedbackTriggerReason.manualFAB,
                                  route: _activeRoute,
                                  pageTitle: _activeRoute,
                                  userName: AuthService.displayName,
                                ),
                              );
                            } else if (choice == 'ticket') {
                              _navigateTo('Customer Service');
                            }
                          });
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
                          minimumSize: const Size(double.infinity, 48),
                          visualDensity: VisualDensity.standard,
                        ),
                        icon: const Icon(Icons.logout, size: 14),
                        label: Text(
                          (widget.isDemoMode || GuestSeedService.isBrowseDemoMode)
                              ? 'Exit Demo'
                              : (!widget.testSkipFirebase && AuthService.isGuest ? 'Exit Guest' : 'Sign Out'),
                          style: const TextStyle(fontSize: NumistaTheme.textBodySm),
                        ),
                        onPressed: () => _confirmSignOut(context),
                      ),
                    ),
                  ),
                ] else ...[
                  Tooltip(
                    message: (widget.isDemoMode || GuestSeedService.isBrowseDemoMode)
                        ? 'Exit Demo'
                        : (!widget.testSkipFirebase && AuthService.isGuest ? 'Exit Guest' : 'Sign Out'),
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
            child: Listener(
              behavior: HitTestBehavior.translucent,
              onPointerDown: (_) =>
                  MorganProactiveRescueObserver.instance.recordUserActivity(),
              child: RepaintBoundary(
                key: _repaintKey,
                child: Stack(
                  children: [
                    Column(
                      children: [
                        if (widget.isDemoMode || GuestSeedService.isBrowseDemoMode)
                          _DemoBanner(onTryFree: () {
                            GuestSeedService.deactivateBrowseDemo();
                            AuthGate.navigateTo(context, initialAuthTab: 1);
                          }),
                        if (!widget.testSkipFirebase && !widget.isDemoMode && AuthService.isGuest) _GuestBanner(),
                        Expanded(child: _wrapBodyWithMaxWidth(_buildBody(), _activeRoute)),
                      ],
                    ),
                    WizardOverlay(
                      onCreateAccount: () {
                        AuthGate.navigateTo(context, initialAuthTab: 1);
                      },
                    ),
                    // Morgan guide panel — unified into single Morgan Co-Pilot window
                    MorganGuidePanel(
                      onSearch: _onMorganSearch,
                      onSearchResultTap: _handleMorganSearchResultTap,
                    ),
                    // WCAG AAA High-Contrast Spotlight Overlay
                    MorganSpotlightOverlay(
                      controller: MorganSpotlightController.instance,
                      reducedMotionOverride:
                          MorganSettingsService.instance.reduceMotion,
                    ),
                    if (_isMorganPopoutOpen &&
                        (!_isMorganDocked || MediaQuery.sizeOf(context).width < 1024))
                      widget.testPopoutBuilder != null
                          ? widget.testPopoutBuilder!(
                              _popoutInitialQuery,
                              () => setState(() {
                                _isMorganPopoutOpen = false;
                                _popoutInitialQuery = null;
                              }),
                            )
                          : MorganChatPopout(
                              initialQuery: _popoutInitialQuery,
                              initialQueryNonce: _popoutInitialQueryNonce,
                              onInitialQueryConsumed: (consumedNonce) {
                                if (_popoutInitialQueryNonce == consumedNonce) {
                                  _popoutInitialQuery = null;
                                }
                              },
                              isDocked: false,
                              testSkipFirebase: widget.testSkipFirebase,
                              onToggleDock: () {
                                setState(() => _isMorganDocked = true);
                                MorganSettingsService.instance.setDockToSide(true);
                              },
                              onClose: () => setState(() {
                                _isMorganPopoutOpen = false;
                                _popoutInitialQuery = null;
                              }),
                              onNavigateToCollection: () => _navigateTo('My Collection'),
                            ),
                  ],
                ),
              ),
            ),
          ),
          if (_isMorganPopoutOpen &&
              _isMorganDocked &&
              MediaQuery.sizeOf(context).width >= 1024)
            widget.testPopoutBuilder != null
                ? widget.testPopoutBuilder!(
                    _popoutInitialQuery,
                    () => setState(() {
                      _isMorganPopoutOpen = false;
                      _popoutInitialQuery = null;
                    }),
                  )
                : MorganChatPopout(
                    initialQuery: _popoutInitialQuery,
                    initialQueryNonce: _popoutInitialQueryNonce,
                    onInitialQueryConsumed: (consumedNonce) {
                      if (_popoutInitialQueryNonce == consumedNonce) {
                        _popoutInitialQuery = null;
                      }
                    },
                    isDocked: true,
                    testSkipFirebase: widget.testSkipFirebase,
                    onToggleDock: () {
                      setState(() => _isMorganDocked = false);
                      MorganSettingsService.instance.setDockToSide(false);
                    },
                    onClose: () => setState(() {
                      _isMorganPopoutOpen = false;
                      _popoutInitialQuery = null;
                    }),
                    onNavigateToCollection: () => _navigateTo('My Collection'),
                  ),
        ],
      ),
    );
  }

  // ─── Nav item builder ────────────────────────────────────────────────────
  Widget _buildNavItem(String title, {
    String? displayLabel,
    IconData? icon,
    int badgeCount = 0,
    bool isSubItem = false,
    String? subItemKey,
    VoidCallback? onCustomTap,
  }) {
    final String label = displayLabel ?? title;
    final bool isActive = subItemKey != null
        ? (_activeRoute == 'My Collection' && _myCollectionTab == subItemKey)
        : (_activeRoute == title);
    final bool isDark = Theme.of(context).brightness == Brightness.dark;
    
    // Items without a backing screen are disabled
    final bool isEnabled = subItemKey != null || onCustomTap != null
        ? true
        : const {
            'Home Dashboard',
            'My Collection',
            'Currency Collection',
            'Review Hub',
            'Take a photo',
            'AI Photo Identification',
            'Microscope Scanner',
            'Coin Programs',
            'Catalog of American Numismatics',
            'Ask Morgan',
            'Coin Search',
            '🔍 Numista Lookup',
            'Add New Coins',
            'My Wishlist',
            'Estate Planning',
            'Attorney Portal',
            'Lateral Transfer',
            'Claim Transfer',
            'AI Deepdive',
            'Human AI Trainer Review Board',
            'AI Trainer Board',
            'Admin: Grade Flags',
            'Feedback Inbox',
            'Settings & Backup',
            'Our Team',
            'Customer Service',
            'My Tickets',
            'Admin: Support Portal',
            'Inventory',
            'Error Library',
            'Glossary Academy',
            'Upcoming Releases',
          }.contains(title == 'Add new coins/notes/etc.' ? 'Add New Coins' : (title == 'Admin Grade Flags' ? 'Admin: Grade Flags' : title));

    final IconData effectiveIcon = icon ?? Icons.circle_outlined;

    if (_isSidebarCollapsed) {
      return Tooltip(
        message: title,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 4),
          child: InkWell(
            onTap: isEnabled
                ? (onCustomTap ??
                    () => _navigateTo(
                          subItemKey != null ? 'My Collection' : title,
                          subTab: subItemKey,
                        ))
                : null,
            borderRadius: BorderRadius.circular(8),
            child: Container(
              constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
              alignment: Alignment.center,
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
            ? (onCustomTap ??
                () => _navigateTo(
                      subItemKey != null ? 'My Collection' : title,
                      subTab: subItemKey,
                    ))
            : null,
        borderRadius: BorderRadius.circular(10),
        child: Container(
          constraints: const BoxConstraints(minHeight: 56),
          alignment: Alignment.centerLeft,
          padding: EdgeInsets.symmetric(vertical: 10, horizontal: isSubItem ? 16 : 12),
          decoration: BoxDecoration(
            color: isActive ? const Color(0xFFE8F0FB) : Colors.transparent,
            borderRadius: BorderRadius.circular(10),
            border: isActive
                ? const Border(left: BorderSide(color: Color(0xFFC9A400), width: 6))
                : null,
          ),
          child: Row(children: [
            if (icon != null)
              Icon(icon,
                  size: 22,
                  color: const Color(0xFF0B1A2E))
            else
              Container(
                width: 16,
                height: 16,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: isActive
                      ? const Color(0xFF1D4F91)
                      : Colors.transparent,
                  border: Border.all(
                    color: isActive
                        ? const Color(0xFF1D4F91)
                        : const Color(0xFF0B1A2E),
                    width: isActive ? 4 : 1,
                  ),
                ),
              ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                label,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  color: const Color(0xFF0B1A2E),
                  fontSize: 18,
                  fontWeight:
                      isActive ? FontWeight.w700 : FontWeight.w500,
                ),
              ),
            ),
            if (badgeCount > 0) ...[
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFF1D4F91),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Text(
                  badgeCount.toString(),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
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
    final isDemo = widget.isDemoMode || GuestSeedService.isBrowseDemoMode;
    final confirm = await showDialog<bool>(
      context: ctx,
      builder: (dctx) => AlertDialog(
        backgroundColor: isDark ? const Color(0xFF1A1D27) : Colors.white,
        title: Text(isDemo ? 'Exit Demo Vault' : 'Sign Out',
            style: TextStyle(color: isDark ? Colors.white : const Color(0xFF0F172A))),
        content: Text(
            isDemo
                ? 'Are you sure you want to exit the demo vault and return to the login screen?'
                : 'Are you sure you want to sign out of your vault?',
            style: TextStyle(color: isDark ? Colors.white70 : const Color(0xFF475569))),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dctx, false),
            child: Text('Cancel',
                style: TextStyle(color: isDark ? Colors.white54 : Colors.grey)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(dctx, true),
            child: Text(isDemo ? 'Exit Demo' : 'Sign Out',
                style: const TextStyle(color: Color(0xFFF63366))),
          ),
        ],
      ),
    );
    if (confirm == true) {
      AuthGate.resetWelcome();
      if (isDemo) {
        GuestSeedService.deactivateBrowseDemo();
        UiVariantService.reset();
        if (ctx.mounted) {
          AuthGate.navigateTo(ctx);
        }
      } else {
        UiVariantService.reset();
        await AuthService.signOut();
      }
    }
    // The StreamBuilder in AuthGate automatically redirects to LoginScreen upon signOut
  }
}

// ─── Alt Site Variant Banner (Phase A) ──────────────────────────────────────
class _AltSiteBanner extends StatelessWidget {
  final Widget child;
  const _AltSiteBanner({required this.child});

  @override
  Widget build(BuildContext context) {
    return Column(children: [
      Container(
        width: double.infinity,
        color: const Color(0xFF4338CA),
        padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 16),
        child: const Text(
          'Alt site variant — Phase A (admin preview)',
          style: TextStyle(color: Colors.white, fontSize: NumistaTheme.textBodySm),
          textAlign: TextAlign.center,
        ),
      ),
      Expanded(child: child),
    ]);
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
                    fontSize: NumistaTheme.textXl,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF31333F))),
            SizedBox(height: 8),
            Text('This feature is under construction.',
                style: TextStyle(color: Color(0xFF5A5C69))),
          ],
        ),
      );
}

class _NavEntry {
  final String route;
  final String label;
  final IconData icon;
  const _NavEntry({
    required this.route,
    required this.label,
    required this.icon,
  });
}

const List<_NavEntry> _kTopLevelNavItems = [
  _NavEntry(route: 'Home Dashboard', label: 'Home', icon: Icons.home_outlined),
  _NavEntry(route: 'My Collection', label: 'My Collection', icon: Icons.layers_outlined),
  _NavEntry(route: 'Catalog of American Numismatics', label: 'Catalog', icon: Icons.auto_stories_outlined),
  _NavEntry(route: 'Coin Programs', label: 'Coin Programs', icon: Icons.article_outlined),
  _NavEntry(route: 'My Wishlist', label: 'Wishlist', icon: Icons.favorite_border),
  _NavEntry(route: 'Review Hub', label: 'Review', icon: Icons.fact_check_outlined),
];

// Wave 2 Component B: Consolidated Research navigation (duplicate Numista Lookup deleted;
// Error Library, Upcoming Releases, and Glossary Academy folded into Catalog tabs;
// AI Deepdive renamed to Ask Morgan). Legacy route strings remain supported via aliases.
const Map<String, List<_NavEntry>> _kNavGroups = {
  'Research': [
    _NavEntry(route: 'Catalog of American Numismatics', label: 'Catalog of American Numismatics', icon: Icons.manage_search_outlined),
    _NavEntry(route: 'AI Deepdive', label: 'Ask Morgan', icon: Icons.auto_awesome_outlined),
  ],
  'Estate & Transfers': [
    _NavEntry(route: 'Estate Planning', label: 'Estate Planning', icon: Icons.description_outlined),
    _NavEntry(route: 'Attorney Portal', label: 'Attorney Portal', icon: Icons.balance_outlined),
    _NavEntry(route: 'Lateral Transfer', label: 'Lateral Transfer', icon: Icons.swap_horiz_outlined),
    _NavEntry(route: 'Claim Transfer', label: 'Claim Transfer', icon: Icons.check_box_outlined),
  ],
  'Settings & Help': [
    _NavEntry(route: 'Settings & Backup', label: 'Settings & Backup', icon: Icons.settings_outlined),
    _NavEntry(route: 'Customer Service', label: 'Customer Service', icon: Icons.headset_mic_outlined),
    _NavEntry(route: 'My Tickets', label: 'My Tickets', icon: Icons.confirmation_number_outlined),
    _NavEntry(route: 'Our Team', label: 'Our Team', icon: Icons.people_outline),
    _NavEntry(route: '__SEND_FEEDBACK__', label: 'Send Feedback', icon: Icons.feedback_outlined),
  ],
};

// ─── Desktop Single-Open Accordion Group ─────────────────────────────────────
class SidebarAccordionGroup extends StatelessWidget {
  final String title;
  final IconData icon;
  final bool isExpanded;
  final VoidCallback onToggle;
  final List<Widget> children;

  const SidebarAccordionGroup({
    super.key,
    required this.title,
    required this.icon,
    required this.isExpanded,
    required this.onToggle,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        InkWell(
          onTap: onToggle,
          borderRadius: BorderRadius.circular(10),
          child: ConstrainedBox(
            constraints: const BoxConstraints(minHeight: 56),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              child: Row(
                children: [
                  Icon(icon, size: 22, color: const Color(0xFF0B1A2E)),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      title,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: isExpanded ? FontWeight.w700 : FontWeight.w500,
                        color: const Color(0xFF0B1A2E),
                      ),
                    ),
                  ),
                  Icon(
                    isExpanded ? Icons.keyboard_arrow_down : Icons.chevron_right,
                    size: 22,
                    color: const Color(0xFF0B1A2E),
                  ),
                ],
              ),
            ),
          ),
        ),
        if (isExpanded)
          Padding(
            padding: const EdgeInsets.only(left: 14),
            child: Column(children: children),
          ),
      ],
    );
  }
}

// ─── Phone Full-Screen Menu Overlay with Group Drill-In ──────────────────────
class PhoneMenuOverlay extends StatelessWidget {
  final String displayName;
  final String activeRoute;
  final int reviewCount;
  final bool isReviewLoading;
  final String? drillGroup;
  final bool isAdmin;
  final VoidCallback onClose;
  final VoidCallback onBack;
  final ValueChanged<String> onOpenGroup;
  final ValueChanged<String> onSelectRoute;

  const PhoneMenuOverlay({
    super.key,
    required this.displayName,
    required this.activeRoute,
    required this.reviewCount,
    required this.isReviewLoading,
    required this.drillGroup,
    required this.isAdmin,
    required this.onClose,
    required this.onBack,
    required this.onOpenGroup,
    required this.onSelectRoute,
  });

  Widget _buildMenuRow({
    required String label,
    required IconData icon,
    required bool isActive,
    required VoidCallback onTap,
    int badgeCount = 0,
    bool showChevron = false,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: Container(
        constraints: const BoxConstraints(minHeight: 56),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          color: isActive ? const Color(0xFFE8F0FB) : Colors.transparent,
          borderRadius: BorderRadius.circular(10),
          border: isActive
              ? const Border(left: BorderSide(color: Color(0xFFC9A400), width: 6))
              : null,
        ),
        child: Row(
          children: [
            Icon(icon, size: 22, color: const Color(0xFF0B1A2E)),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                label,
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: isActive ? FontWeight.w700 : FontWeight.w500,
                  color: const Color(0xFF0B1A2E),
                ),
              ),
            ),
            if (badgeCount > 0)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFF1D4F91),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: Text(
                  badgeCount.toString(),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            if (showChevron)
              const Icon(Icons.chevron_right, size: 22, color: Color(0xFF0B1A2E)),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildTopLevelItems() {
    final badge = isReviewLoading ? 0 : reviewCount;
    return [
      Text(
        'Hello, $displayName',
        style: const TextStyle(
          fontSize: 20,
          fontWeight: FontWeight.w500,
          color: Color(0xFF0B1A2E),
        ),
      ),
      const SizedBox(height: 12),
      ElevatedButton.icon(
        onPressed: () => onSelectRoute('Add New Coins'),
        icon: const Icon(Icons.add_circle_outline, size: 22),
        label: const Text(
          'Add to collection',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
        ),
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF1D4F91),
          foregroundColor: Colors.white,
          minimumSize: const Size(double.infinity, 56),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          elevation: 0,
        ),
      ),
      const SizedBox(height: 8),
      const Text(
        'Save a coin to your collection',
        style: TextStyle(fontSize: 20, color: Color(0xFF0B1A2E)),
      ),
      const SizedBox(height: 12),
      ..._kTopLevelNavItems.map((item) => _buildMenuRow(
            label: item.label,
            icon: item.icon,
            isActive: activeRoute == item.route,
            badgeCount: item.route == 'Review Hub' ? badge : 0,
            onTap: () => onSelectRoute(item.route),
          )),
      const SizedBox(height: 6),
      _buildMenuRow(
        label: 'Research',
        icon: Icons.search,
        isActive: false,
        showChevron: true,
        onTap: () => onOpenGroup('Research'),
      ),
      _buildMenuRow(
        label: 'Estate & Transfers',
        icon: Icons.description_outlined,
        isActive: false,
        showChevron: true,
        onTap: () => onOpenGroup('Estate & Transfers'),
      ),
      _buildMenuRow(
        label: 'Settings & Help',
        icon: Icons.settings_outlined,
        isActive: false,
        showChevron: true,
        onTap: () => onOpenGroup('Settings & Help'),
      ),
    ];
  }

  List<Widget> _buildGroupChildren(String groupName) {
    final items = _kNavGroups[groupName] ?? const [];
    return [
      ...items.map((item) => _buildMenuRow(
            label: item.label,
            icon: item.icon,
            isActive: activeRoute == item.route,
            onTap: () => onSelectRoute(item.route),
          )),
      if (groupName == 'Settings & Help' && isAdmin) ...[
        const Divider(color: Color(0xFFD5DEEA)),
        _buildMenuRow(
          label: 'AI Trainer Board',
          icon: Icons.how_to_vote_outlined,
          isActive: activeRoute == 'AI Trainer Board',
          onTap: () => onSelectRoute('AI Trainer Board'),
        ),
        _buildMenuRow(
          label: 'Admin: Grade Flags',
          icon: Icons.admin_panel_settings_outlined,
          isActive: activeRoute == 'Admin: Grade Flags',
          onTap: () => onSelectRoute('Admin: Grade Flags'),
        ),
        _buildMenuRow(
          label: 'Feedback Inbox',
          icon: Icons.rate_review_outlined,
          isActive: activeRoute == 'Feedback Inbox' || activeRoute == 'Beta Feedback Inbox',
          onTap: () => onSelectRoute('Feedback Inbox'),
        ),
        _buildMenuRow(
          label: 'Admin: Support Portal',
          icon: Icons.support_agent_outlined,
          isActive: activeRoute == 'Admin: Support Portal',
          onTap: () => onSelectRoute('Admin: Support Portal'),
        ),
      ],
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Material(
      color: const Color(0xFFF7F9FC),
      child: SafeArea(
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: const BoxDecoration(
                color: Color(0xFFFFFFFF),
                border: Border(bottom: BorderSide(color: Color(0xFFD5DEEA))),
              ),
              child: Row(
                children: [
                  if (drillGroup != null) ...[
                    OutlinedButton.icon(
                      onPressed: onBack,
                      icon: const Icon(Icons.chevron_left, color: Color(0xFF0B1A2E)),
                      label: const Text(
                        'Back',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF0B1A2E),
                        ),
                      ),
                      style: OutlinedButton.styleFrom(
                        minimumSize: const Size(0, 56),
                        side: const BorderSide(color: Color(0xFF1D4F91), width: 1.5),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        drillGroup!,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.w800,
                          color: Color(0xFF0B1A2E),
                        ),
                      ),
                    ),
                  ] else ...[
                    const Expanded(
                      child: Text(
                        'Menu',
                        style: TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.w800,
                          color: Color(0xFF0B1A2E),
                        ),
                      ),
                    ),
                    OutlinedButton.icon(
                      onPressed: onClose,
                      icon: const Icon(Icons.close, color: Color(0xFF0B1A2E)),
                      label: const Text(
                        'Close',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF0B1A2E),
                        ),
                      ),
                      style: OutlinedButton.styleFrom(
                        minimumSize: const Size(0, 56),
                        side: const BorderSide(color: Color(0xFF1D4F91), width: 1.5),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                  ],
                ],
              ),
            ),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: drillGroup == null
                    ? _buildTopLevelItems()
                    : _buildGroupChildren(drillGroup!),
              ),
            ),
          ],
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
              style: TextStyle(color: Colors.white, fontSize: NumistaTheme.textCaption),
            ),
          ),
          const SizedBox(width: 12),
          OutlinedButton(
            onPressed: onTryFree,
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.white,
              side: const BorderSide(color: Colors.white54),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
              textStyle: const TextStyle(fontSize: NumistaTheme.textCaption, fontWeight: FontWeight.w600),
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
              style: TextStyle(color: Colors.white, fontSize: NumistaTheme.textCaption),
            ),
          ),
          const SizedBox(width: 12),
          OutlinedButton(
            onPressed: () => AuthGate.navigateTo(context, initialAuthTab: 1),
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.white,
              side: const BorderSide(color: Colors.white54),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
              textStyle: const TextStyle(fontSize: NumistaTheme.textCaption, fontWeight: FontWeight.w600),
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
                : (Theme.of(context).brightness == Brightness.dark ? const Color(0xFF0B3D6E).withAlpha(120) : const Color(0xFFF1F5F9)),
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
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Ask Morgan',
                        style: TextStyle(
                            color: Theme.of(context).brightness == Brightness.dark ? Colors.white : const Color(0xFF0F172A),
                            fontSize: NumistaTheme.textBodySm,
                            fontWeight: FontWeight.w600)),
                    Text('Your AI guide',
                        style: TextStyle(
                            color: Theme.of(context).brightness == Brightness.dark ? const Color(0xFF2DD4BF) : const Color(0xFF0F172A).withAlpha(180),
                            fontSize: NumistaTheme.textBodySm)),
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
