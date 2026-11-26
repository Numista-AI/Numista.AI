import 'dart:async';
import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../services/guest_seed_service.dart';
import '../services/stripe_service.dart';
import '../widgets/auth_gate.dart';

/// Clean public shell providing branded informational views (/about, /features, /pricing, /faq).
class PublicInfoShell extends StatelessWidget {
  final String targetRoute;
  @visibleForTesting
  final DateTime? nowUtcOverride;
  @visibleForTesting
  final Future<SubscriptionStatusSnapshot?> Function(String uid)? statusFetcherOverride;
  @visibleForTesting
  final Future<CheckoutLaunchResult> Function({
    required String tier,
    String interval,
    String? promoCode,
  })? checkoutStarterOverride;
  @visibleForTesting
  final Future<bool> Function()? portalStarterOverride;
  @visibleForTesting
  final bool? isSignedInOverride;
  @visibleForTesting
  final String? uidOverride;

  const PublicInfoShell({
    super.key,
    required this.targetRoute,
    this.nowUtcOverride,
    this.statusFetcherOverride,
    this.checkoutStarterOverride,
    this.portalStarterOverride,
    this.isSignedInOverride,
    this.uidOverride,
  });

  static const Color _bg = Color(0xFFF8FAFC);
  static const Color _surface = Colors.white;
  static const Color _text = Color(0xFF0F172A);
  static const Color _border = Color(0xFFE2E8F0);
  static const Color _bronze = Color(0xFF8C7355);
  static const Color _blue = Color(0xFF1E3A8A);

  String? _resolvedSignedInUid() {
    if (isSignedInOverride != null) {
      if (!isSignedInOverride!) return null;
      final explicit = (uidOverride ?? '').trim();
      return explicit.isNotEmpty ? explicit : 'uid_override';
    }
    try {
      final user = FirebaseAuth.instance.currentUser;
      if (user == null || user.isAnonymous) return null;
      return user.uid;
    } catch (_) {
      return null;
    }
  }

  @override
  Widget build(BuildContext context) {
    final signedInUid = _resolvedSignedInUid();
    final isSignedIn = signedInUid != null;
    return Scaffold(
      backgroundColor: _bg,
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(68),
        child: Container(
          decoration: BoxDecoration(
            color: _surface,
            border: Border(bottom: BorderSide(color: _border)),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: SafeArea(
            bottom: false,
            child: Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.arrow_back_rounded, color: _text),
                  tooltip: 'Back to Vault',
                  onPressed: () {
                    AuthGate.navigateTo(context);
                  },
                ),
                const SizedBox(width: 8),
                InkWell(
                  onTap: () {
                    AuthGate.navigateTo(context);
                  },
                  borderRadius: BorderRadius.circular(8),
                  child: Row(
                    children: [
                      Image.asset(
                        'assets/logo_owl.png',
                        height: 36,
                        errorBuilder: (ctx, err, st) => const Icon(
                          Icons.account_balance_rounded,
                          color: _bronze,
                          size: 32,
                        ),
                      ),
                      const SizedBox(width: 10),
                      const Text(
                        'NUMISTA.AI',
                        style: TextStyle(
                          color: _text,
                          fontSize: 18,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 1.2,
                        ),
                      ),
                    ],
                  ),
                ),
                const Spacer(),
                if (isSignedIn)
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _blue,
                      foregroundColor: Colors.white,
                      elevation: 0,
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    onPressed: () {
                      AuthGate.navigateTo(context);
                    },
                    icon: const Icon(Icons.arrow_back_rounded, size: 16),
                    label: const Text('Back to Vault', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                  )
                else
                  Wrap(
                    spacing: 8,
                    runSpacing: 4,
                    alignment: WrapAlignment.end,
                    crossAxisAlignment: WrapCrossAlignment.center,
                    children: [
                      TextButton.icon(
                        onPressed: () async {
                          await GuestSeedService.activateBrowseDemo();
                          if (context.mounted) {
                            AuthGate.navigateTo(context, isDemo: true);
                          }
                        },
                        icon: const Icon(Icons.explore_outlined, size: 16, color: _bronze),
                        label: const Text(
                          'Explore Demo Vault',
                          style: TextStyle(
                            color: _bronze,
                            fontWeight: FontWeight.bold,
                            fontSize: 13,
                          ),
                        ),
                      ),
                      ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _blue,
                          foregroundColor: Colors.white,
                          elevation: 0,
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        onPressed: () {
                          AuthGate.navigateTo(context, initialAuthTab: 1);
                        },
                        child: const Text('Get Started', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                      ),
                    ],
                  ),
              ],
            ),
          ),
        ),
      ),
      body: SingleChildScrollView(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 860),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 40),
              child: _buildRouteContent(context, signedInUid: signedInUid),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildRouteContent(BuildContext context, {String? signedInUid}) {
    switch (targetRoute) {
      case '/features':
        return const _FeaturesView();
      case '/pricing':
        return _PricingView(
          signedInUid: signedInUid,
          nowUtcOverride: nowUtcOverride,
          statusFetcherOverride: statusFetcherOverride,
          checkoutStarterOverride: checkoutStarterOverride,
          portalStarterOverride: portalStarterOverride,
        );
      case '/faq':
        return const _FaqView();
      case '/about':
      default:
        return const _AboutView();
    }
  }
}

// ─── 1. About View ────────────────────────────────────────────────────────────
class _AboutView extends StatelessWidget {
  const _AboutView();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _tagBadge('ABOUT NUMISTA.AI'),
        const SizedBox(height: 12),
        const Text(
          'Built for Collectors, Powered by Rigorous Inventory Systems',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontSize: 32,
            fontWeight: FontWeight.bold,
            height: 1.25,
          ),
        ),
        const SizedBox(height: 12),
        const Text(
          'Numista.AI brings structured property management and artificial intelligence to coin collection cataloging.',
          style: TextStyle(
            color: Color(0xFF475569),
            fontSize: 17,
            height: 1.5,
          ),
        ),
        const SizedBox(height: 32),
        _contentCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: const [
              Text(
                'Numista.AI was founded by a retired U.S. Army Supply NCO with over 20 years of military property accountability and large-scale inventory management experience.',
                style: TextStyle(color: Color(0xFF0F172A), fontSize: 15, height: 1.6),
              ),
              SizedBox(height: 16),
              Text(
                'As a newer coin collector (entering the hobby within the past year), our founder recognized that traditional collection tracking often relies on fragmented spreadsheets, handwritten notebooks, or disconnected reference binders. Numista.AI applies proven inventory management discipline to numismatics—combining AI photo identification, automated Greysheet-based market value estimates, and organized vault documentation so collectors know exactly what they have, what it\'s worth, and where it is stored.',
                style: TextStyle(color: Color(0xFF0F172A), fontSize: 15, height: 1.6),
              ),
            ],
          ),
        ),
        const SizedBox(height: 32),
        _actionRow(context),
      ],
    );
  }
}

// ─── 2. Features View ─────────────────────────────────────────────────────────
class _FeaturesView extends StatelessWidget {
  const _FeaturesView();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _tagBadge('PRODUCT CAPABILITIES'),
        const SizedBox(height: 12),
        const Text(
          'Tools for Cataloging and Preserving Your Collection',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontSize: 32,
            fontWeight: FontWeight.bold,
            height: 1.25,
          ),
        ),
        const SizedBox(height: 28),
        _featureItem(
          icon: Icons.camera_alt_outlined,
          title: 'AI Photo Identification',
          status: 'AVAILABLE NOW',
          statusColor: const Color(0xFF059669),
          desc: 'Upload or snap photos of your coins for automated denomination, series, year, and mint mark recognition.',
        ),
        const SizedBox(height: 16),
        _featureItem(
          icon: Icons.trending_up_rounded,
          title: 'Greysheet-Based Value Estimates',
          status: 'AVAILABLE NOW',
          statusColor: const Color(0xFF059669),
          desc: 'View reference pricing and market value estimates linked directly to your cataloged inventory.',
        ),
        const SizedBox(height: 16),
        _featureItem(
          icon: Icons.show_chart_rounded,
          title: 'Total Collection Value Tracking',
          status: 'AVAILABLE NOW',
          statusColor: const Color(0xFF059669),
          desc: "Track your collection's total value over time as you add coins and market prices update.",
        ),
        const SizedBox(height: 16),
        _featureItem(
          icon: Icons.open_in_new_rounded,
          title: 'eBay Sold Listings Search',
          status: 'AVAILABLE NOW',
          statusColor: const Color(0xFF059669),
          desc: 'One-tap link to search recent eBay sold listings for any coin in your collection.',
        ),
        const SizedBox(height: 16),
        _featureItem(
          icon: Icons.chat_bubble_outline_rounded,
          title: 'Morgan Numismatic Assistant',
          status: 'AVAILABLE NOW',
          statusColor: const Color(0xFF059669),
          desc: 'An AI assistant to help research coin history, metal compositions, mintage statistics, and collection details.',
        ),
        const SizedBox(height: 16),
        _featureItem(
          icon: Icons.verified_user_outlined,
          title: 'AI Trainer Review Board',
          status: 'AVAILABLE NOW',
          statusColor: const Color(0xFF059669),
          desc: 'Community and numismatic review board regularly updates and validates AI identification references.',
        ),
        const SizedBox(height: 16),
        _featureItem(
          icon: Icons.picture_as_pdf_outlined,
          title: 'Estate Documentation & Reports',
          status: 'EARLY ACCESS',
          statusColor: const Color(0xFFD97706),
          desc: 'Structured estate PDF reports for personal records, insurance documentation, and family review.',
        ),
        const SizedBox(height: 32),
        _actionRow(context),
      ],
    );
  }

  Widget _featureItem({
    required IconData icon,
    required String title,
    required String status,
    required Color statusColor,
    required String desc,
  }) {
    return _contentCard(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: const Color(0xFF8C7355), size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        title,
                        style: const TextStyle(
                          color: Color(0xFF0F172A),
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: statusColor.withAlpha(25),
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(color: statusColor.withAlpha(75)),
                      ),
                      child: Text(
                        status,
                        style: TextStyle(
                          color: statusColor,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 0.5,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  desc,
                  style: const TextStyle(color: Color(0xFF475569), fontSize: 14, height: 1.5),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ─── 3. Pricing View ──────────────────────────────────────────────────────────
class _PricingView extends StatefulWidget {
  final String? signedInUid;
  final DateTime? nowUtcOverride;
  final Future<SubscriptionStatusSnapshot?> Function(String uid)? statusFetcherOverride;
  final Future<CheckoutLaunchResult> Function({
    required String tier,
    String interval,
    String? promoCode,
  })? checkoutStarterOverride;
  final Future<bool> Function()? portalStarterOverride;

  const _PricingView({
    this.signedInUid,
    this.nowUtcOverride,
    this.statusFetcherOverride,
    this.checkoutStarterOverride,
    this.portalStarterOverride,
  });

  @override
  State<_PricingView> createState() => _PricingViewState();
}

enum _PricingStatusState { idle, loading, loaded, error }

class _PricingViewState extends State<_PricingView> {
  static final DateTime _christmasStartUtc = DateTime.utc(2026, 12, 15, 5);
  static final DateTime _christmasEndUtc = DateTime.utc(2027, 1, 16, 5);
  static const Duration _statusTimeout = Duration(seconds: 15);

  bool _isYearly = false;
  bool _showPromoInput = false;
  _PricingStatusState _statusState = _PricingStatusState.idle;
  int _statusLoadSeq = 0;
  Timer? _statusTimeoutTimer;
  bool _submitting = false;
  String? _actionMessage;
  bool _actionIsError = false;
  SubscriptionStatusSnapshot? _status;
  final TextEditingController _promoCtrl = TextEditingController();

  bool get _inChristmasWindow {
    final nowUtc = widget.nowUtcOverride ?? DateTime.now().toUtc();
    return !nowUtc.isBefore(_christmasStartUtc) && nowUtc.isBefore(_christmasEndUtc);
  }

  bool get _isSignedIn => widget.signedInUid != null && widget.signedInUid!.isNotEmpty;

  @override
  void initState() {
    super.initState();
    if (_isSignedIn) {
      _statusState = _PricingStatusState.loading;
      _loadStatus(fromInit: true);
    }
  }

  @override
  void didUpdateWidget(covariant _PricingView oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.signedInUid != widget.signedInUid) {
      _statusTimeoutTimer?.cancel();
      _statusLoadSeq++;
      _status = null;
      if (_isSignedIn) {
        _statusState = _PricingStatusState.loading;
        _loadStatus(fromInit: true);
      } else {
        _statusState = _PricingStatusState.idle;
      }
    }
  }

  @override
  void dispose() {
    _statusTimeoutTimer?.cancel();
    _promoCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadStatus({bool fromInit = false}) async {
    final uid = widget.signedInUid;
    if (uid == null || uid.isEmpty) return;
    _statusTimeoutTimer?.cancel();
    final seq = ++_statusLoadSeq;
    if (fromInit) {
      _status = null;
      _statusState = _PricingStatusState.loading;
    } else {
      setState(() {
        _status = null;
        _statusState = _PricingStatusState.loading;
      });
    }
    _statusTimeoutTimer = Timer(_statusTimeout, () {
      if (!mounted || seq != _statusLoadSeq || _statusState != _PricingStatusState.loading) {
        return;
      }
      setState(() {
        _status = null;
        _statusState = _PricingStatusState.error;
      });
    });
    try {
      final fetcher = widget.statusFetcherOverride ??
          ((String id) => StripeService.fetchSubscriptionStatus(uid: id));
      final snap = await fetcher(uid);
      if (!mounted || seq != _statusLoadSeq) return;
      _statusTimeoutTimer?.cancel();
      setState(() {
        if (snap == null) {
          _status = null;
          _statusState = _PricingStatusState.error;
        } else {
          _status = snap;
          _statusState = _PricingStatusState.loaded;
        }
      });
    } catch (_) {
      if (!mounted || seq != _statusLoadSeq) return;
      _statusTimeoutTimer?.cancel();
      setState(() {
        _status = null;
        _statusState = _PricingStatusState.error;
      });
    }
  }

  String _paidCtaLabel({
    required bool isStatusLoading,
    required bool isFoundingBeta,
    required String signedOutLabel,
    required String eligibleLabel,
  }) {
    if (!_isSignedIn) return signedOutLabel;
    if (isStatusLoading) return 'Checking account...';
    if (isFoundingBeta) return 'Included with Founding Beta';
    return eligibleLabel;
  }

  VoidCallback? _paidCtaOnPressed({
    required bool canCheckout,
    required String tier,
    required bool isLifetime,
  }) {
    if (!_isSignedIn) {
      return () => AuthGate.navigateTo(context, initialAuthTab: 1);
    }
    if (!canCheckout) return null;
    return () => _handleCheckout(tier: tier, isLifetime: isLifetime);
  }

  Future<void> _handleCheckout({required String tier, required bool isLifetime}) async {
    if (!_isSignedIn) {
      AuthGate.navigateTo(context, initialAuthTab: 1);
      return;
    }
    if (_statusState != _PricingStatusState.loaded ||
        _status == null ||
        _status!.stripeTier == 'founding_beta') {
      return;
    }
    setState(() {
      _submitting = true;
      _actionMessage = null;
      _actionIsError = false;
    });
    final promo = _promoCtrl.text.trim();
    final starter = widget.checkoutStarterOverride ??
        ({required String tier, String interval = 'month', String? promoCode}) =>
            StripeService.startCheckout(
              tier: tier,
              interval: interval,
              promoCode: promoCode,
            );
    final res = await starter(
      tier: tier,
      interval: isLifetime ? 'year' : (_isYearly ? 'year' : 'month'),
      promoCode: promo.isEmpty ? null : promo,
    );
    if (!mounted) return;
    setState(() {
      _submitting = false;
      if (!res.ok) {
        _actionIsError = true;
        _actionMessage = res.message ?? 'Unable to start checkout.';
      } else {
        _actionIsError = false;
        _actionMessage = 'Redirecting to secure Stripe Checkout...';
      }
    });
  }

  Future<void> _handleManageBilling() async {
    setState(() {
      _submitting = true;
      _actionMessage = null;
      _actionIsError = false;
    });
    final portal = widget.portalStarterOverride ?? (() => StripeService.launchCustomerPortal());
    final ok = await portal();
    if (!mounted) return;
    setState(() {
      _submitting = false;
      if (!ok) {
        _actionIsError = true;
        _actionMessage = 'Unable to open Stripe billing portal.';
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final bool isStatusLoading = _isSignedIn && _statusState == _PricingStatusState.loading;
    final bool isStatusError = _isSignedIn && _statusState == _PricingStatusState.error;
    final bool isStatusLoaded =
        _isSignedIn && _statusState == _PricingStatusState.loaded && _status != null;
    final isFoundingBeta = isStatusLoaded && _status!.stripeTier == 'founding_beta';
    final hasPaidOrLifetime =
        isStatusLoaded && (_status!.hasPaidSubscription || _status!.lifetimeFamilyEstate);
    final bool canCheckout = isStatusLoaded && !isFoundingBeta && !_submitting;
    final intervalLabel = _isYearly ? 'Yearly' : 'Monthly';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _tagBadge('PLANS & PRICING'),
        const SizedBox(height: 12),
        const Text(
          'Simple Plans for Every Collection Size',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontSize: 32,
            fontWeight: FontWeight.bold,
            height: 1.25,
          ),
        ),
        const SizedBox(height: 10),
        const Text(
          'Start free with up to 10 items, upgrade as your vault grows, or choose Lifetime Family Estate.',
          style: TextStyle(color: Color(0xFF475569), fontSize: 15, height: 1.5),
        ),
        const SizedBox(height: 20),

        // Placeholder Founding Beta Banner (for Eric confirmation before merge)
        if (_isSignedIn && isFoundingBeta) ...[
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: const Color(0xFF059669).withAlpha(18),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFF059669).withAlpha(110)),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Founding Beta Member — Lifetime Access (including Estate) Included',
                  style: TextStyle(
                    color: Color(0xFF065F46),
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                SizedBox(height: 6),
                Text(
                  'Thank you for joining early. Your Founding Beta account includes unlimited items and Legal Estate Suite at no charge.',
                  style: TextStyle(color: Color(0xFF065F46), fontSize: 13.5, height: 1.5),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
        ],

        // Placeholder CHRISTMAS2026 Banner (shown automatically only inside Dec 15 - Jan 15 window)
        if (_inChristmasWindow) ...[
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: const Color(0xFFFEF3C7),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFFD97706)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        'CHRISTMAS2026 Holiday Sale — 50% Off ($intervalLabel Plans)',
                        style: const TextStyle(
                          color: Color(0xFF78350F),
                          fontSize: 16,
                          fontWeight: FontWeight.w800,
                        ),
                      ),
                    ),
                    TextButton(
                      onPressed: () {
                        setState(() {
                          _showPromoInput = true;
                          _promoCtrl.text = 'CHRISTMAS2026';
                        });
                      },
                      child: const Text('Use CHRISTMAS2026'),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                const Text(
                  r'Sale prices with code CHRISTMAS2026: Copper $1.99/mo or $19.99/yr, Silver $3.99/mo or $39.99/yr, Platinum $4.99/mo or $49.50/yr, Gold $7.99/mo or $75.00/yr.',
                  style: TextStyle(color: Color(0xFF78350F), fontSize: 13.5, height: 1.5),
                ),
                const SizedBox(height: 6),
                const Text(
                  r'Offer ends January 15, 2027. Discount applies to the first year (yearly plans: $39.99 / $79.99 / $99.00 / $150.00 renewal) or first 12 months (monthly plans: $3.99 / $7.99 / $9.99 / $15.99 renewal), then automatically renews at full regular price. Lifetime Family Estate ($500) is excluded.',
                  style: TextStyle(color: Color(0xFF92400E), fontSize: 12.5, height: 1.45),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),
        ],

        // Billing Interval Toggle + Optional Promo Code + Manage Billing
        Wrap(
          spacing: 12,
          runSpacing: 12,
          crossAxisAlignment: WrapCrossAlignment.center,
          children: [
            ChoiceChip(
              key: const Key('billing_toggle_monthly'),
              label: const Text('Monthly'),
              selected: !_isYearly,
              onSelected: (_) => setState(() => _isYearly = false),
            ),
            ChoiceChip(
              key: const Key('billing_toggle_yearly'),
              label: const Text('Yearly'),
              selected: _isYearly,
              onSelected: (_) => setState(() => _isYearly = true),
            ),
            TextButton.icon(
              onPressed: () => setState(() => _showPromoInput = !_showPromoInput),
              icon: const Icon(Icons.local_offer_outlined, size: 16),
              label: const Text('Have a promo code?'),
            ),
            if (_isSignedIn && hasPaidOrLifetime)
              OutlinedButton.icon(
                key: const Key('pricing_manage_billing_btn'),
                onPressed: _submitting ? null : _handleManageBilling,
                icon: const Icon(Icons.manage_accounts_outlined, size: 16),
                label: const Text('Manage Billing'),
              ),
          ],
        ),

        if (_showPromoInput) ...[
          const SizedBox(height: 12),
          SizedBox(
            width: 320,
            child: TextField(
              key: const Key('pricing_promo_field'),
              controller: _promoCtrl,
              textCapitalization: TextCapitalization.characters,
              decoration: const InputDecoration(
                labelText: 'Promo code',
                hintText: 'Enter promo code',
                border: OutlineInputBorder(),
                isDense: true,
              ),
            ),
          ),
        ],

        if (isStatusLoading) ...[
          const SizedBox(height: 12),
          Container(
            key: const Key('pricing_status_loading_banner'),
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFDBEAFE),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFF1E3A8A)),
            ),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                    SizedBox(width: 10),
                    Text(
                      'Checking your account...',
                      style: TextStyle(
                        color: Color(0xFF1E3A8A),
                        fontSize: 13.5,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
                SizedBox(height: 8),
                LinearProgressIndicator(minHeight: 2),
              ],
            ),
          ),
        ],

        if (isStatusError) ...[
          const SizedBox(height: 12),
          Container(
            key: const Key('pricing_status_error_banner'),
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFFEE2E2),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFFDC2626)),
            ),
            child: Row(
              children: [
                const Expanded(
                  child: Text(
                    'Unable to verify your account status right now. Plan upgrades are paused until your account check succeeds.',
                    style: TextStyle(
                      color: Color(0xFF991B1B),
                      fontSize: 13.5,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                OutlinedButton(
                  key: const Key('pricing_status_retry_btn'),
                  onPressed: _loadStatus,
                  child: const Text('Retry'),
                ),
              ],
            ),
          ),
        ],

        if (_actionMessage != null) ...[
          const SizedBox(height: 14),
          Container(
            key: const Key('pricing_action_banner'),
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: _actionIsError ? const Color(0xFFFEE2E2) : const Color(0xFFDBEAFE),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                color: _actionIsError ? const Color(0xFFDC2626) : const Color(0xFF1E3A8A),
              ),
            ),
            child: Text(
              _actionMessage!,
              style: TextStyle(
                color: _actionIsError ? const Color(0xFF991B1B) : const Color(0xFF1E3A8A),
                fontSize: 13.5,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],

        const SizedBox(height: 24),

        // 1. Free Plan (Q-G1: lists Free = 10 items on current main; invents no Guest number)
        _buildPlanCard(
          displayName: 'Free',
          badge: 'FREE STARTER',
          priceText: r'$0',
          promoNote: null,
          features: const [
            '10 items in your vault',
            'AI coin identification (3 deep dives / day, 1 invoice scan / day)',
            'Sign in required to subscribe or buy Lifetime',
          ],
          ctaKey: const Key('plan_cta_free'),
          ctaLabel: _isSignedIn ? 'Included' : 'Sign in to Subscribe',
          onPressed: _isSignedIn ? null : () => AuthGate.navigateTo(context, initialAuthTab: 1),
        ),
        const SizedBox(height: 16),

        // 2. Copper
        _buildPlanCard(
          displayName: 'Copper',
          badge: 'UP TO 100 ITEMS',
          priceText: _isYearly ? r'$39.99/yr' : r'$3.99/mo',
          promoNote: _inChristmasWindow
              ? (_isYearly
                  ? r'Sale $19.99/yr first year with CHRISTMAS2026 (renews at $39.99/yr)'
                  : r'Sale $1.99/mo first 12 months with CHRISTMAS2026 (renews at $3.99/mo)')
              : null,
          features: const [
            '100 items in your vault',
            '25 AI deep dives / day · 15 invoice scans / day',
          ],
          ctaKey: const Key('plan_cta_pro'),
          ctaLabel: _paidCtaLabel(
            isStatusLoading: isStatusLoading,
            isFoundingBeta: isFoundingBeta,
            signedOutLabel: 'Sign in to Subscribe',
            eligibleLabel: 'Subscribe',
          ),
          onPressed: _paidCtaOnPressed(
            canCheckout: canCheckout,
            tier: 'pro',
            isLifetime: false,
          ),
        ),
        const SizedBox(height: 16),

        // 3. Silver
        _buildPlanCard(
          displayName: 'Silver',
          badge: 'UP TO 249 ITEMS',
          priceText: _isYearly ? r'$79.99/yr' : r'$7.99/mo',
          promoNote: _inChristmasWindow
              ? (_isYearly
                  ? r'Sale $39.99/yr first year with CHRISTMAS2026 (renews at $79.99/yr)'
                  : r'Sale $3.99/mo first 12 months with CHRISTMAS2026 (renews at $7.99/mo)')
              : null,
          features: const [
            '249 items in your vault',
            '50 AI deep dives / day · 30 invoice scans / day',
          ],
          ctaKey: const Key('plan_cta_numismatist'),
          ctaLabel: _paidCtaLabel(
            isStatusLoading: isStatusLoading,
            isFoundingBeta: isFoundingBeta,
            signedOutLabel: 'Sign in to Subscribe',
            eligibleLabel: 'Subscribe',
          ),
          onPressed: _paidCtaOnPressed(
            canCheckout: canCheckout,
            tier: 'numismatist',
            isLifetime: false,
          ),
        ),
        const SizedBox(height: 16),

        // 4. Platinum
        _buildPlanCard(
          displayName: 'Platinum',
          badge: 'UP TO 500 ITEMS',
          priceText: _isYearly ? r'$99.00/yr' : r'$9.99/mo',
          promoNote: _inChristmasWindow
              ? (_isYearly
                  ? r'Sale $49.50/yr first year with CHRISTMAS2026 (renews at $99.00/yr)'
                  : r'Sale $4.99/mo first 12 months with CHRISTMAS2026 (renews at $9.99/mo)')
              : null,
          features: const [
            '500 items in your vault',
            '100 AI deep dives / day · 50 invoice scans / day',
          ],
          ctaKey: const Key('plan_cta_dealer'),
          ctaLabel: _paidCtaLabel(
            isStatusLoading: isStatusLoading,
            isFoundingBeta: isFoundingBeta,
            signedOutLabel: 'Sign in to Subscribe',
            eligibleLabel: 'Subscribe',
          ),
          onPressed: _paidCtaOnPressed(
            canCheckout: canCheckout,
            tier: 'dealer',
            isLifetime: false,
          ),
        ),
        const SizedBox(height: 16),

        // 5. Gold
        _buildPlanCard(
          displayName: 'Gold',
          badge: 'TOP SUBSCRIPTION TIER',
          priceText: _isYearly ? r'$150.00/yr' : r'$15.99/mo',
          promoNote: _inChristmasWindow
              ? (_isYearly
                  ? r'Sale $75.00/yr first year with CHRISTMAS2026 (renews at $150.00/yr)'
                  : r'Sale $7.99/mo first 12 months with CHRISTMAS2026 (renews at $15.99/mo)')
              : null,
          features: const [
            'Unlimited items in your vault',
            '500 AI deep dives / day · 250 invoice scans / day',
            'Legal Estate Suite requires Lifetime Family Estate',
          ],
          ctaKey: const Key('plan_cta_estate'),
          ctaLabel: _paidCtaLabel(
            isStatusLoading: isStatusLoading,
            isFoundingBeta: isFoundingBeta,
            signedOutLabel: 'Sign in to Subscribe',
            eligibleLabel: 'Subscribe',
          ),
          onPressed: _paidCtaOnPressed(
            canCheckout: canCheckout,
            tier: 'estate',
            isLifetime: false,
          ),
        ),
        const SizedBox(height: 16),

        // 6. Lifetime Family Estate
        _buildPlanCard(
          displayName: 'Lifetime Family Estate',
          badge: 'ONE-TIME · INCLUDES ESTATE SUITE',
          priceText: r'$500.00 one-time',
          promoNote: 'Excluded from CHRISTMAS2026 discount.',
          features: const [
            'Unlimited items forever + full Legal Estate Suite (PDF reports, fiduciary custody, spot checks)',
            'Good standing rule: Open accounts in good standing can keep updating Estate Plans.',
          ],
          ctaKey: const Key('plan_cta_family_estate'),
          ctaLabel: _paidCtaLabel(
            isStatusLoading: isStatusLoading,
            isFoundingBeta: isFoundingBeta,
            signedOutLabel: 'Sign in to Buy',
            eligibleLabel: r'Buy Lifetime ($500)',
          ),
          onPressed: _paidCtaOnPressed(
            canCheckout: canCheckout,
            tier: 'family_estate',
            isLifetime: true,
          ),
        ),

        const SizedBox(height: 20),
        const Text(
          'Applicable sales tax is calculated at checkout.',
          style: TextStyle(color: Color(0xFF475569), fontSize: 13.5, fontWeight: FontWeight.w500),
        ),
        const SizedBox(height: 20),
        _contentCard(
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Why is Gold our top tier?',
                style: TextStyle(
                  color: Color(0xFF0F172A),
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 8),
              Text(
                'Many people assume platinum is worth more than gold. It often was in the past, but gold has traded well above platinum in recent years. As a true numismatics site, we rank our plans the way the metals actually trade.',
                style: TextStyle(color: Color(0xFF475569), fontSize: 14, height: 1.55),
              ),
            ],
          ),
        ),
        const SizedBox(height: 32),
        if (!_isSignedIn) _actionRow(context),
      ],
    );
  }

  Widget _buildPlanCard({
    required String displayName,
    required String badge,
    required String priceText,
    required String? promoNote,
    required List<String> features,
    required Key ctaKey,
    required String ctaLabel,
    required VoidCallback? onPressed,
  }) {
    return _contentCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFF8C7355).withAlpha(22),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: const Color(0xFF8C7355).withAlpha(90)),
                ),
                child: Text(
                  badge,
                  style: const TextStyle(
                    color: Color(0xFF8C7355),
                    fontWeight: FontWeight.bold,
                    fontSize: 11,
                    letterSpacing: 0.9,
                  ),
                ),
              ),
              const Spacer(),
              Text(
                priceText,
                style: const TextStyle(
                  color: Color(0xFF0F172A),
                  fontSize: 20,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            displayName,
            style: const TextStyle(
              color: Color(0xFF0F172A),
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          if (promoNote != null) ...[
            const SizedBox(height: 6),
            Text(
              promoNote,
              style: const TextStyle(
                color: Color(0xFF92400E),
                fontSize: 13,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
          const SizedBox(height: 10),
          for (final f in features) ...[
            Text(
              '• $f',
              style: const TextStyle(color: Color(0xFF334155), fontSize: 14, height: 1.5),
            ),
            const SizedBox(height: 4),
          ],
          const SizedBox(height: 12),
          ElevatedButton(
            key: ctaKey,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF1E3A8A),
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            onPressed: onPressed,
            child: Text(ctaLabel, style: const TextStyle(fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}

// ─── 4. FAQ View ──────────────────────────────────────────────────────────────
class _FaqView extends StatelessWidget {
  const _FaqView();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _tagBadge('QUESTIONS & ANSWERS'),
        const SizedBox(height: 12),
        const Text(
          'Frequently Asked Questions',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontSize: 32,
            fontWeight: FontWeight.bold,
            height: 1.25,
          ),
        ),
        const SizedBox(height: 28),
        _faqTile(
          question: '1. How is my collection data kept private?',
          answer: 'Your vault is private to your account. We do not make your collection records public. For full details on our data protection practices, see our Privacy Policy.',
        ),
        _faqTile(
          question: '2. How accurate is AI photo identification?',
          answer: 'Numista provides AI photo identification based on verified reference coin specifications and historical data. It is designed as a cataloging and research assistant, and is not a professional third-party grading service (such as PCGS or NGC).',
        ),
        _faqTile(
          question: '3. Can I export / print an estate report?',
          answer: 'Yes. Numista provides structured export tools so you can generate professional collection summaries for personal records, insurance documentation, and family estate planning.',
        ),
        _faqTile(
          question: '4. What features are included today, and how do I send feedback?',
          answer: 'Most core features—including collection cataloging, photo lookup, and Greysheet value estimates—work today, while select advanced features are still being polished. You can submit feedback through Ask Morgan or participate in our sidebar AI Trainer Board, where community members review and rate AI coin classifications.',
        ),
        _faqTile(
          question: '5. Does Guest / Demo save my coins?',
          answer: 'No. The Demo Vault runs entirely in-memory with sample coins for exploration. Any changes made during a demo session are not saved. To build and preserve your personal collection vault, create a free account.',
        ),
        const SizedBox(height: 32),
        _actionRow(context),
      ],
    );
  }

  Widget _faqTile({required String question, required String answer}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: _contentCard(
        child: Theme(
          data: ThemeData(dividerColor: Colors.transparent),
          child: ExpansionTile(
            tilePadding: EdgeInsets.zero,
            childrenPadding: const EdgeInsets.only(top: 8),
            title: Text(
              question,
              style: const TextStyle(
                color: Color(0xFF0F172A),
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            children: [
              Text(
                answer,
                style: const TextStyle(color: Color(0xFF475569), fontSize: 14, height: 1.6),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
Widget _tagBadge(String label) {
  return Container(
    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
    decoration: BoxDecoration(
      color: const Color(0xFF8C7355).withAlpha(20),
      borderRadius: BorderRadius.circular(6),
    ),
    child: Text(
      label,
      style: const TextStyle(
        color: Color(0xFF8C7355),
        fontSize: 11,
        fontWeight: FontWeight.w700,
        letterSpacing: 1.1,
      ),
    ),
  );
}

Widget _contentCard({required Widget child}) {
  return Container(
    width: double.infinity,
    padding: const EdgeInsets.all(24),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(12),
      border: Border.all(color: const Color(0xFFE2E8F0)),
      boxShadow: [
        BoxShadow(
          color: Colors.black.withAlpha(8),
          blurRadius: 10,
          offset: const Offset(0, 2),
        ),
      ],
    ),
    child: child,
  );
}

Widget _actionRow(BuildContext context) {
  return Wrap(
    spacing: 12,
    runSpacing: 12,
    children: [
      ElevatedButton.icon(
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF1E3A8A),
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
        onPressed: () {
          AuthGate.navigateTo(context, initialAuthTab: 1);
        },
        icon: const Icon(Icons.rocket_launch_outlined, size: 18),
        label: const Text('Create Free Account', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      OutlinedButton.icon(
        style: OutlinedButton.styleFrom(
          foregroundColor: const Color(0xFF8C7355),
          side: const BorderSide(color: Color(0xFF8C7355)),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
        onPressed: () async {
          await GuestSeedService.activateBrowseDemo();
          if (context.mounted) {
            AuthGate.navigateTo(context, isDemo: true);
          }
        },
        icon: const Icon(Icons.explore_outlined, size: 18),
        label: const Text('Explore Demo Vault', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
    ],
  );
}
