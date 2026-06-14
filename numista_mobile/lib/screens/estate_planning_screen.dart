import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:intl/intl.dart';
import 'package:uuid/uuid.dart';
import '../models/estate_models.dart';
import '../models/coin_model.dart';
import '../services/estate_profile_service.dart';
import '../services/estate_data_service.dart';
import '../services/estate_report_service.dart';

// ─────────────────────────────────────────────────────────────────────────────
// Theme constants
// ─────────────────────────────────────────────────────────────────────────────
const _kNavy       = Color(0xFF0E1117);
const _kDeepPurple = Color(0xFF1a1a2e);
const _kGold       = Color(0xFFFFD700);
const _kRed        = Color(0xFFF63366);
const _kCard       = Color(0xFF161B27);
const _kCardBorder = Color(0xFF2A3045);
const _kTextPrimary   = Color(0xFFECEFF4);
const _kTextSecondary = Color(0xFF8B92A5);

final _dollarFmt = NumberFormat.currency(symbol: '\$', decimalDigits: 0);

// ─────────────────────────────────────────────────────────────────────────────
// Supported jurisdictions
// ─────────────────────────────────────────────────────────────────────────────
const _jurisdictions = ['NY', 'NC', 'NJ', 'FL', 'CA', 'TX', 'SC', 'Other'];

Map<String, _StateInfo> _stateInfo = {
  'NY': _StateInfo(
    color: const Color(0xFFF59E0B),
    icon: Icons.warning_amber_rounded,
    title: 'New York — Estate Tax Cliff',
    body: 'NY imposes a state estate tax with a "cliff" effect. If the '
        'taxable estate exceeds 105% of the \$7.35M exemption, the ENTIRE '
        'estate is taxed (not just the excess). Tangible personal property '
        '(TPP) like coins is not subject to the NY estate tax memo '
        'restriction. Recommend formal appraisal for coins over \$3,000.',
  ),
  'NJ': _StateInfo(
    color: const Color(0xFFEF4444),
    icon: Icons.gavel_rounded,
    title: 'New Jersey — Inheritance Tax',
    body: 'NJ levies an inheritance tax based on the beneficiary\'s '
        'relationship class (A, C, D, E). Class A (spouse, children) pays '
        'no tax. Class D (friends, distant relatives) pays up to 16%. '
        'Assign beneficiary classes to each beneficiary in your profile.',
  ),
  'FL': _StateInfo(
    color: const Color(0xFF10B981),
    icon: Icons.lock_outline_rounded,
    title: 'Florida — Probate Inventory Confidentiality',
    body: 'Florida provides strong probate inventory confidentiality. '
        'Coin collection inventories filed with the court are not public '
        'records. No state estate or inheritance tax.',
  ),
  'CA': _StateInfo(
    color: const Color(0xFFF59E0B),
    icon: Icons.info_outline_rounded,
    title: 'California — TPP Memo Cap',
    body: 'CA Probate Code §13006 allows a TPP memo to transfer personal '
        'property, but is capped at \$25,000 retail value. Collections '
        'exceeding this must go through formal probate or a trust. '
        'Community property rules apply to coins purchased during marriage.',
  ),
  'TX': _StateInfo(
    color: const Color(0xFF3B82F6),
    icon: Icons.gavel_rounded,
    title: 'Texas — Coins Explicitly in Statute',
    body: 'Texas Estates Code explicitly lists coins and currency as '
        'tangible personal property. No state estate tax. Community '
        'property rules apply. Consider a transfer-on-death deed for '
        'collections held in a safe or safety deposit box.',
  ),
  'NC': _StateInfo(
    color: const Color(0xFF10B981),
    icon: Icons.check_circle_outline_rounded,
    title: 'North Carolina — TPP Memo Allowed',
    body: 'NC allows tangible personal property memoranda to direct '
        'specific items (including coins) to named beneficiaries outside '
        'of probate. The memo can be updated any time without attorney '
        'involvement. No state inheritance tax.',
  ),
  'SC': _StateInfo(
    color: const Color(0xFF10B981),
    icon: Icons.check_circle_outline_rounded,
    title: 'South Carolina — TPP Memo Allowed',
    body: 'SC allows TPP memos similar to NC. Coins can be directed to '
        'specific beneficiaries by memo attached to your will. No state '
        'inheritance tax.',
  ),
};

class _StateInfo {
  final Color color;
  final IconData icon;
  final String title;
  final String body;
  const _StateInfo({
    required this.color,
    required this.icon,
    required this.title,
    required this.body,
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// EstatePlanningScreen — main entry point
// ─────────────────────────────────────────────────────────────────────────────
class EstatePlanningScreen extends StatefulWidget {
  const EstatePlanningScreen({super.key});

  @override
  State<EstatePlanningScreen> createState() => _EstatePlanningScreenState();
}

class _EstatePlanningScreenState extends State<EstatePlanningScreen>
    with SingleTickerProviderStateMixin {
  late final TabController _tabs;
  String get _uid =>
      FirebaseAuth.instance.currentUser?.email ?? '';

  // ── Subscription tier ───────────────────────────────────────────────────────
  // AJ (Customer #1) and @numista.ai accounts always have access.
  // All other users need 'estate' or 'pro' subscription_tier in Firestore.
  String _subscriptionTier = '';      // '', 'free', 'estate', 'pro'
  bool   _tierLoaded       = false;
  StreamSubscription<DocumentSnapshot>? _tierSub;

  bool get _hasEstateAccess =>
      _uid == 'jseaman1204@gmail.com' ||
      _uid.endsWith('@numista.ai') ||
      _subscriptionTier == 'estate'   ||
      _subscriptionTier == 'pro';

  @override
  void initState() {
    super.initState();
    _tabs = TabController(length: 3, vsync: this);
    _listenToTier();
  }

  void _listenToTier() {
    // AJ and internal accounts bypass Firestore lookup
    if (_uid == 'jseaman1204@gmail.com' || _uid.endsWith('@numista.ai')) {
      setState(() { _subscriptionTier = 'estate'; _tierLoaded = true; });
      return;
    }
    _tierSub = FirebaseFirestore.instance
        .collection('users')
        .doc(_uid)
        .collection('subscription')
        .doc('status')
        .snapshots()
        .listen((snap) {
      if (!mounted) return;
      final tier = (snap.data()?['tier'] as String?) ?? 'free';
      setState(() { _subscriptionTier = tier; _tierLoaded = true; });
    }, onError: (_) {
      // Firestore unavailable — fail open so users aren't incorrectly blocked
      if (mounted) setState(() { _subscriptionTier = 'free'; _tierLoaded = true; });
    });
  }

  @override
  void dispose() {
    _tierSub?.cancel();
    _tabs.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Theme(
      data: _estateTheme(context),
      child: Scaffold(
        backgroundColor: _kNavy,
        body: Column(
          children: [
            _buildHeader(),
            Expanded(
              child: !_tierLoaded
                  ? const Center(child: CircularProgressIndicator(color: _kGold))
                  : _hasEstateAccess
                      ? TabBarView(
                          controller: _tabs,
                          children: [
                            _ProfileTab(uid: _uid),
                            _CollectionTab(uid: _uid),
                            _GenerateTab(uid: _uid),
                          ],
                        )
                      : _PremiumGate(onUpgrade: _showUpgradeSheet),
            ),
          ],
        ),
      ),
    );
  }

  void _showUpgradeSheet() {
    showModalBottomSheet<void>(
      context: context,
      backgroundColor: const Color(0xFF161B27),
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => DraggableScrollableSheet(
        initialChildSize: 0.72,
        maxChildSize: 0.92,
        minChildSize: 0.5,
        expand: false,
        builder: (_, scroll) => SingleChildScrollView(
          controller: scroll,
          child: Padding(
            padding: const EdgeInsets.fromLTRB(24, 8, 24, 40),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Drag handle
                Center(
                  child: Container(
                    width: 40, height: 4,
                    margin: const EdgeInsets.only(bottom: 20),
                    decoration: BoxDecoration(
                      color: const Color(0xFF3A4055),
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
                // Header
                const Text('\u{1F451}', style: TextStyle(fontSize: 40)),
                const SizedBox(height: 12),
                const Text('Estate Tier',
                    style: TextStyle(
                        color: _kGold, fontSize: 26, fontWeight: FontWeight.w800)),
                const SizedBox(height: 6),
                const Text(
                  'Court-ready estate reports for serious collectors.',
                  style: TextStyle(color: _kTextSecondary, fontSize: 14, height: 1.5),
                ),
                const SizedBox(height: 24),

                // Feature list
                ..._kEstateFeatures.map((f) => Padding(
                  padding: const EdgeInsets.only(bottom: 14),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        width: 36, height: 36,
                        decoration: BoxDecoration(
                          color: _kGold.withAlpha(20),
                          borderRadius: BorderRadius.circular(9),
                          border: Border.all(color: _kGold.withAlpha(50)),
                        ),
                        child: Icon(f.$1, color: _kGold, size: 18),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(f.$2,
                                style: const TextStyle(
                                    color: _kTextPrimary,
                                    fontSize: 13,
                                    fontWeight: FontWeight.w600)),
                            const SizedBox(height: 2),
                            Text(f.$3,
                                style: const TextStyle(
                                    color: _kTextSecondary, fontSize: 12)),
                          ],
                        ),
                      ),
                    ],
                  ),
                )),

                const SizedBox(height: 24),

                // Price row
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFF0E1117),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: _kGold.withAlpha(60)),
                  ),
                  child: Row(
                    children: [
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Estate Tier',
                                style: TextStyle(
                                    color: _kGold,
                                    fontSize: 15,
                                    fontWeight: FontWeight.w700)),
                            Text('Billed annually',
                                style: TextStyle(
                                    color: _kTextSecondary, fontSize: 11)),
                          ],
                        ),
                      ),
                      const Text('\$9.99',
                          style: TextStyle(
                              color: _kTextPrimary,
                              fontSize: 22,
                              fontWeight: FontWeight.w800)),
                      const Text('/mo',
                          style: TextStyle(
                              color: _kTextSecondary, fontSize: 13)),
                    ],
                  ),
                ),

                const SizedBox(height: 20),

                // CTA
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pop(ctx);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Estate Tier billing coming soon \u2014 contact support@numista.ai'),
                          backgroundColor: Color(0xFF161B27),
                          duration: Duration(seconds: 5),
                        ),
                      );
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _kGold,
                      foregroundColor: _kNavy,
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12)),
                      textStyle: const TextStyle(
                          fontSize: 16, fontWeight: FontWeight.w800),
                    ),
                    child: const Text('Get Estate Tier'),
                  ),
                ),
                const SizedBox(height: 12),
                Center(
                  child: TextButton(
                    onPressed: () => Navigator.pop(ctx),
                    child: const Text('Maybe later',
                        style: TextStyle(color: _kTextSecondary, fontSize: 13)),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // Feature list for upgrade sheet
  static const _kEstateFeatures = [
    (Icons.picture_as_pdf_rounded,
     'Court-Ready PDF Reports',
     'Professionally formatted estate inventory accepted by Surrogate\'s Court'),
    (Icons.gavel_rounded,
     'State-Specific Legal Guidance',
     'NY cliff rule, ET-706 deadlines, TPP memo rules for 7 states'),
    (Icons.link_rounded,
     'Attorney Portal Link',
     'Shareable, read-only access for your estate attorney \u2014 no login required'),
    (Icons.cloud_upload_rounded,
     'Secure Cloud Storage',
     'Every report stored in GCS with permanent download links'),
    (Icons.assessment_rounded,
     'IRS Appraisal Flagging',
     'Automatically identifies coins requiring a qualified appraisal (>\$3,000 FMV)'),
    (Icons.trending_up_rounded,
     'Step-Up Basis Calculator',
     'Quantifies the stepped-up basis benefit at death for your entire collection'),
  ];

  Widget _buildHeader() {

    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          colors: [_kNavy, _kDeepPurple],
          begin: Alignment.centerLeft,
          end: Alignment.centerRight,
        ),
        border: Border(
          bottom: BorderSide(color: _kCardBorder, width: 1),
        ),
      ),
      child: SafeArea(
        bottom: false,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 16, 20, 4),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: _kGold.withAlpha(20),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: _kGold.withAlpha(60)),
                    ),
                    child: const Icon(Icons.account_balance_outlined,
                        color: _kGold, size: 20),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Estate Planning',
                          style: TextStyle(
                            color: _kGold,
                            fontSize: 20,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 0.5,
                          ),
                        ),
                        Text(
                          'Legal-grade coin collection documentation',
                          style: TextStyle(
                            color: _kTextSecondary,
                            fontSize: 11,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            TabBar(
              controller: _tabs,
              indicatorColor: _kGold,
              indicatorWeight: 2,
              labelColor: _kGold,
              unselectedLabelColor: _kTextSecondary,
              labelStyle: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.3,
              ),
              unselectedLabelStyle: const TextStyle(fontSize: 12),
              tabs: const [
                Tab(icon: Icon(Icons.person_outline, size: 16), text: 'My Profile'),
                Tab(icon: Icon(Icons.paid_outlined, size: 16), text: 'Collection'),
                Tab(icon: Icon(Icons.description_outlined, size: 16), text: 'Generate'),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// TAB 1 — Estate Profile
// ─────────────────────────────────────────────────────────────────────────────
class _ProfileTab extends StatefulWidget {
  final String uid;
  const _ProfileTab({required this.uid});

  @override
  State<_ProfileTab> createState() => _ProfileTabState();
}

class _ProfileTabState extends State<_ProfileTab> {
  final _formKey = GlobalKey<FormState>();
  bool _loading = true;
  bool _saving = false;

  // Form controllers
  final _ownerNameCtrl    = TextEditingController();
  final _ownerEmailCtrl   = TextEditingController();
  final _execNameCtrl     = TextEditingController();
  final _execEmailCtrl    = TextEditingController();
  final _execPhoneCtrl    = TextEditingController();
  final _attNameCtrl      = TextEditingController();
  final _attEmailCtrl     = TextEditingController();
  final _attFirmCtrl      = TextEditingController();
  final _attPhoneCtrl     = TextEditingController();
  final _maritalNotesCtrl = TextEditingController();

  String _maritalStatus    = 'Single';
  String _jurisdiction     = '';
  String _willTrustStatus  = 'Unknown';
  List<EstateBeneficiary> _beneficiaries = [];

  StreamSubscription<EstateProfile?>? _sub;

  @override
  void initState() {
    super.initState();
    _sub = EstateProfileService.watchProfile(widget.uid).listen((p) {
      if (!mounted) return;
      if (p != null) _applyProfile(p);
      if (_loading) setState(() => _loading = false);
    });
    // If stream takes time, show form quickly
    Future.delayed(const Duration(seconds: 1), () {
      if (mounted && _loading) setState(() => _loading = false);
    });
  }

  void _applyProfile(EstateProfile p) {
    _ownerNameCtrl.text    = p.ownerName;
    _ownerEmailCtrl.text   = p.ownerEmail;
    _execNameCtrl.text     = p.executorName;
    _execEmailCtrl.text    = p.executorEmail;
    _execPhoneCtrl.text    = p.executorPhone;
    _attNameCtrl.text      = p.attorneyName;
    _attEmailCtrl.text     = p.attorneyEmail;
    _attFirmCtrl.text      = p.attorneyFirm;
    _attPhoneCtrl.text     = p.attorneyPhone;
    _maritalNotesCtrl.text = p.maritalPropertyNotes;
    _maritalStatus         = p.maritalStatus;
    _jurisdiction          = p.jurisdiction;
    _willTrustStatus       = p.willOrTrustStatus;
    _beneficiaries         = List.from(p.beneficiaries);
    setState(() {});
  }

  @override
  void dispose() {
    _sub?.cancel();
    for (final c in [
      _ownerNameCtrl, _ownerEmailCtrl, _execNameCtrl, _execEmailCtrl,
      _execPhoneCtrl, _attNameCtrl, _attEmailCtrl, _attFirmCtrl,
      _attPhoneCtrl, _maritalNotesCtrl,
    ]) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> _save() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    setState(() => _saving = true);
    try {
      final updated = EstateProfile(
        ownerName:          _ownerNameCtrl.text.trim(),
        ownerEmail:         _ownerEmailCtrl.text.trim(),
        jurisdiction:       _jurisdiction,
        maritalStatus:      _maritalStatus,
        executorName:       _execNameCtrl.text.trim(),
        executorEmail:      _execEmailCtrl.text.trim(),
        executorPhone:      _execPhoneCtrl.text.trim(),
        attorneyName:       _attNameCtrl.text.trim(),
        attorneyEmail:      _attEmailCtrl.text.trim(),
        attorneyFirm:       _attFirmCtrl.text.trim(),
        attorneyPhone:      _attPhoneCtrl.text.trim(),
        willOrTrustStatus:  _willTrustStatus,
        beneficiaries:      _beneficiaries,
        isMarried:          _maritalStatus == 'Married',
        maritalPropertyNotes: _maritalNotesCtrl.text.trim(),
      );
      await EstateProfileService.saveProfile(widget.uid, updated);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Estate profile saved.'),
            backgroundColor: Color(0xFF10B981),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(
        child: CircularProgressIndicator(color: _kGold),
      );
    }

    return Form(
      key: _formKey,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // ── Personal Information ──────────────────────────────────────
          _SectionHeader(title: 'Personal Information', icon: Icons.person_outline),
          _EstateCard(children: [
            _formField('Owner Full Legal Name', _ownerNameCtrl,
                hint: 'As it appears on legal documents',
                required: true),
            _formField('Email', _ownerEmailCtrl,
                hint: 'owner@example.com',
                keyboardType: TextInputType.emailAddress),
            const SizedBox(height: 12),
            _label('Marital Status'),
            const SizedBox(height: 6),
            _SegmentedPicker(
              options: const ['Single', 'Married', 'Widowed', 'Divorced'],
              value: _maritalStatus,
              onChanged: (v) => setState(() => _maritalStatus = v),
            ),
            if (_maritalStatus == 'Married' &&
                const {'CA', 'TX', 'NV', 'WA', 'AZ', 'ID', 'NM', 'WI', 'LA'}
                    .contains(_jurisdiction)) ...[
              const SizedBox(height: 12),
              _InfoBanner(
                color: const Color(0xFFF59E0B),
                icon: Icons.warning_amber_rounded,
                title: 'Community Property State',
                body: 'Coins purchased during your marriage in $_jurisdiction '
                    'may be community property. Add notes below to clarify '
                    'which coins are separate vs. community property.',
              ),
              const SizedBox(height: 8),
              _formField('Community Property Notes', _maritalNotesCtrl,
                  hint: 'e.g. "Coins purchased before 2005 are separate property"',
                  maxLines: 3),
            ],
          ]),

          const SizedBox(height: 16),

          // ── Jurisdiction ──────────────────────────────────────────────
          _SectionHeader(title: 'Jurisdiction', icon: Icons.location_city_outlined),
          _EstateCard(children: [
            _label('State / Jurisdiction'),
            const SizedBox(height: 6),
            DropdownButtonFormField<String>(
              // ignore: deprecated_member_use — `value` drives selected item on a controlled dropdown
              value: _jurisdiction.isEmpty ? null : _jurisdiction,
              decoration: _inputDecoration(hint: 'Select your state'),
              dropdownColor: _kCard,
              style: const TextStyle(color: _kTextPrimary, fontSize: 14),
              items: _jurisdictions.map((s) => DropdownMenuItem(
                value: s,
                child: Text(s, style: const TextStyle(color: _kTextPrimary)),
              )).toList(),
              onChanged: (v) => setState(() => _jurisdiction = v ?? ''),
              validator: (v) => (v == null || v.isEmpty)
                  ? 'Please select a jurisdiction'
                  : null,
            ),
            if (_jurisdiction.isNotEmpty && _stateInfo.containsKey(_jurisdiction)) ...[
              const SizedBox(height: 12),
              _InfoBanner(
                color: _stateInfo[_jurisdiction]!.color,
                icon: _stateInfo[_jurisdiction]!.icon,
                title: _stateInfo[_jurisdiction]!.title,
                body: _stateInfo[_jurisdiction]!.body,
              ),
            ],
          ]),

          const SizedBox(height: 16),

          // ── Estate Documents ──────────────────────────────────────────
          _SectionHeader(title: 'Estate Documents', icon: Icons.description_outlined),
          _EstateCard(children: [
            _label('Will / Trust Status'),
            const SizedBox(height: 6),
            _SegmentedPicker(
              options: const ['Has Will', 'Has Trust', 'Has Both', 'Neither', 'Unknown'],
              value: _willTrustStatus,
              onChanged: (v) => setState(() => _willTrustStatus = v),
            ),
            const SizedBox(height: 16),
            _label('Attorney'),
            const SizedBox(height: 8),
            _formField('Attorney Full Name', _attNameCtrl,
                hint: 'John Smith, Esq.'),
            _formField('Law Firm', _attFirmCtrl,
                hint: 'Smith & Associates, LLP'),
            _formField('Attorney Email', _attEmailCtrl,
                hint: 'attorney@lawfirm.com',
                keyboardType: TextInputType.emailAddress),
            _formField('Attorney Phone', _attPhoneCtrl,
                hint: '(212) 555-0100',
                keyboardType: TextInputType.phone),
          ]),

          const SizedBox(height: 16),

          // ── Executor ──────────────────────────────────────────────────
          _SectionHeader(
              title: 'Executor / Personal Representative',
              icon: Icons.manage_accounts_outlined),
          _EstateCard(children: [
            _formField('Executor Full Name', _execNameCtrl,
                hint: 'Jane Doe'),
            _formField('Executor Email', _execEmailCtrl,
                hint: 'executor@example.com',
                keyboardType: TextInputType.emailAddress),
            _formField('Executor Phone', _execPhoneCtrl,
                hint: '(212) 555-0200',
                keyboardType: TextInputType.phone),
          ]),

          const SizedBox(height: 16),

          // ── Beneficiaries ─────────────────────────────────────────────
          _SectionHeader(
            title: 'Beneficiaries',
            icon: Icons.people_outline,
            trailing: Tooltip(
              message: 'Assigning beneficiaries lets you direct specific coins '
                  'to specific heirs in the report. Required for NJ '
                  'inheritance tax class calculations.',
              child: const Icon(Icons.help_outline,
                  size: 16, color: _kTextSecondary),
            ),
          ),
          _BeneficiaryListEditor(
            beneficiaries: _beneficiaries,
            showNjClass: _jurisdiction == 'NJ',
            onChanged: (list) => setState(() => _beneficiaries = list),
          ),

          const SizedBox(height: 24),

          // ── Save button ───────────────────────────────────────────────
          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton(
              onPressed: _saving ? null : _save,
              style: ElevatedButton.styleFrom(
                backgroundColor: _kNavy,
                foregroundColor: _kGold,
                side: const BorderSide(color: _kGold, width: 1.5),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10)),
                textStyle: const TextStyle(
                    fontSize: 15, fontWeight: FontWeight.w700,
                    letterSpacing: 0.5),
              ),
              child: _saving
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                          color: _kGold, strokeWidth: 2))
                  : const Text('Save Estate Profile'),
            ),
          ),

          const SizedBox(height: 32),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// TAB 2 — Collection Review
// ─────────────────────────────────────────────────────────────────────────────
class _CollectionTab extends StatefulWidget {
  final String uid;
  const _CollectionTab({required this.uid});

  @override
  State<_CollectionTab> createState() => _CollectionTabState();
}

class _CollectionTabState extends State<_CollectionTab> {
  List<CoinModel> _coins = [];
  Map<String, CoinEstateData> _estateData = {};
  List<EstateBeneficiary> _beneficiaries = [];
  bool _loading = true;
  String _filter = 'All'; // 'All' | 'Unassigned' | 'Needs Appraisal'
  StreamSubscription<Map<String, CoinEstateData>>? _estateSub;
  StreamSubscription<EstateProfile?>? _profileSub;

  @override
  void initState() {
    super.initState();
    _loadCoins();
    _estateSub = EstateDataService.watchEstateData(widget.uid).listen((data) {
      if (mounted) setState(() => _estateData = data);
    });
    _profileSub = EstateProfileService.watchProfile(widget.uid).listen((p) {
      if (mounted && p != null) {
        setState(() => _beneficiaries = p.beneficiaries);
      }
    });
  }

  Future<void> _loadCoins() async {
    try {
      final snap = await FirebaseFirestore.instance
          .collection('users')
          .doc(widget.uid)
          .collection('coins')
          .orderBy('timestamp', descending: true)
          .get();
      final coins = snap.docs
          .map((d) => CoinModel.fromFirestore(d))
          .toList();
      if (mounted) setState(() { _coins = coins; _loading = false; });
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  void dispose() {
    _estateSub?.cancel();
    _profileSub?.cancel();
    super.dispose();
  }

  List<CoinModel> get _filteredCoins {
    switch (_filter) {
      case 'Unassigned':
        return _coins.where((c) =>
            _estateData[c.id]?.beneficiaryId == null).toList();
      case 'Needs Appraisal':
        return _coins.where((c) => _parseFmv(c) > 3000).toList();
      default:
        return _coins;
    }
  }

  double _parseFmv(CoinModel c) {
    final raw = _estateData[c.id]?.fmvOverride
        ?? _parseValue(c.aiEstimatedValue);
    return raw;
  }

  double _parseValue(String v) {
    final cleaned = v.replaceAll(RegExp(r'[^\d.]'), '');
    return double.tryParse(cleaned) ?? 0.0;
  }

  double get _totalFmv =>
      _coins.fold(0.0, (acc, c) => acc + _parseFmv(c));

  int get _assignedCount =>
      _coins.where((c) => _estateData[c.id]?.beneficiaryId != null).length;

  int get _needsAppraisalCount =>
      _coins.where((c) => _parseFmv(c) > 3000).length;

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator(color: _kGold));
    }

    return Column(
      children: [
        // ── Stat cards ──────────────────────────────────────────────────
        Container(
          color: _kDeepPurple.withAlpha(180),
          padding: const EdgeInsets.fromLTRB(12, 12, 12, 8),
          child: Row(
            children: [
              _StatChip('Coins', _coins.length.toString()),
              _StatChip('Est. FMV', _dollarFmt.format(_totalFmv),
                  highlight: true),
              _StatChip(
                  'Assigned',
                  '$_assignedCount / ${_coins.length}'),
              _StatChip('Need Appraisal', _needsAppraisalCount.toString(),
                  warn: _needsAppraisalCount > 0),
            ],
          ),
        ),

        // ── Filter buttons ───────────────────────────────────────────────
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          child: Row(
            children: ['All', 'Unassigned', 'Needs Appraisal'].map((f) {
              final active = _filter == f;
              return Padding(
                padding: const EdgeInsets.only(right: 8),
                child: GestureDetector(
                  onTap: () => setState(() => _filter = f),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 160),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: active ? _kGold.withAlpha(30) : Colors.transparent,
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                        color: active ? _kGold : _kCardBorder,
                      ),
                    ),
                    child: Text(f,
                        style: TextStyle(
                          color: active ? _kGold : _kTextSecondary,
                          fontSize: 12,
                          fontWeight: active
                              ? FontWeight.w600
                              : FontWeight.normal,
                        )),
                  ),
                ),
              );
            }).toList(),
          ),
        ),

        // ── Coin list ─────────────────────────────────────────────────────
        Expanded(
          child: _filteredCoins.isEmpty
              ? Center(
                  child: Text(
                    'No coins match this filter.',
                    style: TextStyle(color: _kTextSecondary),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  itemCount: _filteredCoins.length,
                  itemBuilder: (ctx, i) {
                    final coin = _filteredCoins[i];
                    final estData = _estateData[coin.id];
                    final fmv = _parseFmv(coin);
                    final needsAppraisal = fmv > 3000;
                    return _CoinEstateRow(
                      coin: coin,
                      estateData: estData,
                      fmv: fmv,
                      needsAppraisal: needsAppraisal,
                      onTap: () => _openEditSheet(coin, estData),
                    );
                  },
                ),
        ),
      ],
    );
  }

  void _openEditSheet(CoinModel coin, CoinEstateData? existing) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _CoinEstateEditSheet(
        coin: coin,
        existing: existing,
        beneficiaries: _beneficiaries,
        uid: widget.uid,
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// TAB 3 — Generate Report
// ─────────────────────────────────────────────────────────────────────────────
class _GenerateTab extends StatefulWidget {
  final String uid;
  const _GenerateTab({required this.uid});

  @override
  State<_GenerateTab> createState() => _GenerateTabState();
}

class _GenerateTabState extends State<_GenerateTab> {
  EstateProfile? _profile;
  int _coinCount = 0;
  bool _loadingProfile = true;

  String _mode = 'living_inventory';
  DateTime? _dateOfDeath;
  bool _includePhotos = true;

  bool _generating = false;
  int _progressStep = 0;
  String _progressMsg = '';
  List<EstateReportRecord> _history = [];
  bool _loadingHistory = false;

  static const _progressMessages = [
    'Analyzing your collection...',
    'Calculating valuations...',
    'Generating AI narrative...',
    'Building PDF...',
    'Done!',
  ];

  StreamSubscription<EstateProfile?>? _profileSub;

  @override
  void initState() {
    super.initState();
    _profileSub = EstateProfileService.watchProfile(widget.uid).listen((p) {
      if (mounted) {
        setState(() {
          _profile = p;
          _loadingProfile = false;
        });
      }
    });
    _loadCoinCount();
    _loadHistory();
    Future.delayed(const Duration(seconds: 1), () {
      if (mounted && _loadingProfile) setState(() => _loadingProfile = false);
    });
  }

  Future<void> _loadCoinCount() async {
    try {
      final snap = await FirebaseFirestore.instance
          .collection('users')
          .doc(widget.uid)
          .collection('coins')
          .count()
          .get();
      if (mounted) setState(() => _coinCount = snap.count ?? 0);
    } catch (_) {}
  }

  Future<void> _loadHistory() async {
    setState(() => _loadingHistory = true);
    final history = await EstateReportService.getReportHistory(widget.uid);
    if (mounted) setState(() { _history = history; _loadingHistory = false; });
  }

  @override
  void dispose() {
    _profileSub?.cancel();
    super.dispose();
  }

  bool get _canGenerate {
    final p = _profile;
    if (p == null) return false;
    if (p.ownerName.isEmpty) return false;
    if (p.jurisdiction.isEmpty) return false;
    if (_coinCount == 0) return false;
    if (_mode == 'estate_settlement' && _dateOfDeath == null) return false;
    return true;
  }

  Future<void> _generate() async {
    if (_profile == null || !_canGenerate) return;
    setState(() {
      _generating = true;
      _progressStep = 0;
      _progressMsg = _progressMessages[0];
    });

    // Animate progress messages
    final timer = Timer.periodic(const Duration(seconds: 4), (t) {
      if (!mounted) { t.cancel(); return; }
      setState(() {
        _progressStep = (_progressStep + 1).clamp(0, 3);
        _progressMsg = _progressMessages[_progressStep];
      });
    });

    try {
      final result = await EstateReportService.generateReport(
        uid: widget.uid,
        profile: _profile!,
        mode: _mode,
        dateOfDeath: _dateOfDeath != null
            ? DateFormat('yyyy-MM-dd').format(_dateOfDeath!)
            : null,
        includePhotos: _includePhotos,
      );

      timer.cancel();
      if (!mounted) return;
      setState(() {
        _progressStep = 4;
        _progressMsg = _progressMessages[4];
      });

      await Future.delayed(const Duration(milliseconds: 600));
      final filename =
          'estate_report_${_mode}_${DateFormat('yyyy-MM-dd').format(DateTime.now())}.pdf';
      await EstateReportService.openPdf(result.pdfBytes, filename);

      if (mounted) {
        setState(() => _generating = false);
        await _loadHistory();
        // Show share sheet so user can send link to attorney
        if (result.reportId.isNotEmpty) {
          await _showShareSheet(result.reportId);
        }
      }
    } catch (e) {
      timer.cancel();
      if (!mounted) return;
      setState(() => _generating = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error: ${e.toString().replaceFirst('Exception: ', '')}'),
          backgroundColor: Colors.red,
          duration: const Duration(seconds: 8),
        ),
      );
    }
  }

  Future<void> _showShareSheet(String reportId) async {
    if (!mounted) return;
    final uid = widget.uid;
    final messenger = ScaffoldMessenger.of(context);

    await showModalBottomSheet<void>(
      context: context,
      backgroundColor: const Color(0xFF161B27),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.fromLTRB(24, 20, 24, 32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              const Icon(Icons.share_rounded, color: _kGold, size: 20),
              const SizedBox(width: 10),
              const Text('Share Report',
                  style: TextStyle(
                      color: _kGold,
                      fontSize: 16,
                      fontWeight: FontWeight.w700)),
              const Spacer(),
              IconButton(
                icon: const Icon(Icons.close_rounded,
                    color: _kTextSecondary, size: 20),
                onPressed: () => Navigator.pop(ctx),
              ),
            ]),
            const SizedBox(height: 4),
            const Text(
              'Your PDF has been generated. Send the attorney portal link to your estate attorney for a live, interactive view.',
              style: TextStyle(color: _kTextSecondary, fontSize: 12),
            ),
            const SizedBox(height: 20),

            // Copy Attorney Link
            _ShareOption(
              icon: Icons.link_rounded,
              color: _kGold,
              title: 'Copy Attorney Portal Link',
              subtitle: 'Interactive, read-only — expires in 30 days',
              onTap: () async {
                await EstateReportService.copyAttorneyLink(uid, reportId);
                if (ctx.mounted) {
                  Navigator.pop(ctx);
                  messenger.showSnackBar(
                    const SnackBar(
                      content: Text('Attorney portal link copied! Valid for 30 days.'),
                      backgroundColor: Color(0xFF161B27),
                    ),
                  );
                }
              },
            ),
            const SizedBox(height: 12),

            // Download PDF reminder
            _ShareOption(
              icon: Icons.download_rounded,
              color: const Color(0xFF10B981),
              title: 'PDF Already Downloaded',
              subtitle: 'The PDF opened in a new tab — save it from there',
              onTap: () => Navigator.pop(ctx),
            ),
            const SizedBox(height: 12),

            // Report ID reference
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF0E1117),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFF2A3045)),
              ),
              child: Row(children: [
                const Icon(Icons.fingerprint_rounded,
                    color: _kTextSecondary, size: 14),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Report ID: $reportId',
                    style: const TextStyle(
                        color: _kTextSecondary,
                        fontSize: 10,
                        fontFamily: 'monospace'),
                  ),
                ),
                GestureDetector(
                  onTap: () => Clipboard.setData(
                      ClipboardData(text: reportId)),
                  child: const Icon(Icons.copy_rounded,
                      color: _kTextSecondary, size: 14),
                ),
              ]),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loadingProfile) {
      return const Center(child: CircularProgressIndicator(color: _kGold));
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // ── Mode Selection ───────────────────────────────────────────────
        _SectionHeader(title: 'Report Mode', icon: Icons.tune_outlined),
        _ModeCard(
          selected: _mode == 'living_inventory',
          icon: '📋',
          title: 'Living Inventory Mode',
          subtitle: 'I am alive and preparing my estate plan proactively.',
          onTap: () => setState(() => _mode = 'living_inventory'),
        ),
        const SizedBox(height: 8),
        _ModeCard(
          selected: _mode == 'estate_settlement',
          icon: '⚖️',
          title: 'Estate Settlement Mode',
          subtitle: 'I am the executor filing for probate after the owner\'s passing.',
          onTap: () => setState(() => _mode = 'estate_settlement'),
        ),

        // ── Estate settlement extra fields ───────────────────────────────
        if (_mode == 'estate_settlement') ...[
          const SizedBox(height: 12),
          _EstateCard(children: [
            _label('Date of Death'),
            const SizedBox(height: 8),
            GestureDetector(
              onTap: () async {
                final picked = await showDatePicker(
                  context: context,
                  initialDate: _dateOfDeath ?? DateTime.now(),
                  firstDate: DateTime(1900),
                  lastDate: DateTime.now(),
                  builder: (ctx, child) => Theme(
                    data: _estateTheme(ctx),
                    child: child!,
                  ),
                );
                if (picked != null && mounted) {
                  setState(() => _dateOfDeath = picked);
                }
              },
              child: Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 14, vertical: 14),
                decoration: BoxDecoration(
                  border: Border.all(
                      color: _dateOfDeath == null
                          ? _kRed.withAlpha(180)
                          : _kCardBorder),
                  borderRadius: BorderRadius.circular(8),
                  color: _kCard,
                ),
                child: Row(
                  children: [
                    Icon(Icons.calendar_today_outlined,
                        size: 16,
                        color: _dateOfDeath == null
                            ? _kRed
                            : _kTextSecondary),
                    const SizedBox(width: 10),
                    Text(
                      _dateOfDeath != null
                          ? DateFormat('MMMM d, yyyy').format(_dateOfDeath!)
                          : 'Select date of death (required)',
                      style: TextStyle(
                        color: _dateOfDeath != null
                            ? _kTextPrimary
                            : _kTextSecondary,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            if (_profile?.executorName.isNotEmpty == true) ...[
              const SizedBox(height: 12),
              Row(
                children: [
                  const Icon(Icons.manage_accounts_outlined,
                      size: 14, color: _kTextSecondary),
                  const SizedBox(width: 6),
                  Text('Executor: ${_profile!.executorName}',
                      style: const TextStyle(
                          color: _kTextSecondary, fontSize: 12)),
                ],
              ),
            ],
          ]),
        ],

        const SizedBox(height: 16),

        // ── Report Options ───────────────────────────────────────────────
        _SectionHeader(title: 'Report Options', icon: Icons.settings_outlined),
        _EstateCard(children: [
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Include Coin Photos',
                        style: TextStyle(
                            color: _kTextPrimary,
                            fontSize: 13,
                            fontWeight: FontWeight.w500)),
                    Text('Embeds obverse images in the PDF',
                        style: TextStyle(
                            color: _kTextSecondary, fontSize: 11)),
                  ],
                ),
              ),
              Switch(
                value: _includePhotos,
                onChanged: (v) => setState(() => _includePhotos = v),
                activeThumbColor: _kGold,
                activeTrackColor: _kGold.withAlpha(80),
                inactiveTrackColor: _kCardBorder,
              ),
            ],
          ),
        ]),

        const SizedBox(height: 16),

        // ── Readiness Checklist ──────────────────────────────────────────
        _SectionHeader(
            title: 'Readiness Checklist', icon: Icons.checklist_outlined),
        _ChecklistCard(profile: _profile, coinCount: _coinCount),

        const SizedBox(height: 20),

        // ── NY-Specific Warnings (only shown for NY users) ───────────────
        if (_profile?.jurisdiction == 'NY') ...[
          _NyWarningCard(totalFmv: null), // FMV not available pre-generation
          const SizedBox(height: 16),
        ],

        // ── Generate Button ──────────────────────────────────────────────
        _GenerateButton(
          canGenerate: _canGenerate && !_generating,
          generating: _generating,
          progressStep: _progressStep,
          progressMsg: _progressMsg,
          onGenerate: _generate,
        ),

        const SizedBox(height: 24),

        // ── Report History ───────────────────────────────────────────────
        if (_loadingHistory)
          const Center(child: CircularProgressIndicator(color: _kGold))
        else if (_history.isNotEmpty) ...[
          _SectionHeader(
              title: 'Report History', icon: Icons.history_outlined),
          ..._history.map((r) => _ReportHistoryRow(
                record: r,
                onReopen: () async {
                  if (r.downloadUrl != null) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                          content: Text(
                              'Re-opening reports requires your local download. Please regenerate.')),
                    );
                  }
                },
              )),
          const SizedBox(height: 24),
        ],
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Bottom Sheet — Edit coin estate data
// ─────────────────────────────────────────────────────────────────────────────
class _CoinEstateEditSheet extends StatefulWidget {
  final CoinModel coin;
  final CoinEstateData? existing;
  final List<EstateBeneficiary> beneficiaries;
  final String uid;

  const _CoinEstateEditSheet({
    required this.coin,
    required this.existing,
    required this.beneficiaries,
    required this.uid,
  });

  @override
  State<_CoinEstateEditSheet> createState() => _CoinEstateEditSheetState();
}

class _CoinEstateEditSheetState extends State<_CoinEstateEditSheet> {
  String? _beneficiaryId;
  final _notesCtrl         = TextEditingController();
  final _fmvOverrideCtrl   = TextEditingController();
  final _appraiserCtrl     = TextEditingController();
  final _appraisalValCtrl  = TextEditingController();
  final _certNumCtrl       = TextEditingController();
  DateTime? _appraisalDate;
  bool _isHeirloom         = false;
  bool _excludeFromReport  = false;
  bool _useFmvOverride     = false;
  bool _saving             = false;

  @override
  void initState() {
    super.initState();
    final e = widget.existing;
    if (e != null) {
      _beneficiaryId    = e.beneficiaryId;
      _notesCtrl.text   = e.estateNotes ?? '';
      _isHeirloom       = e.isHeirloom;
      _excludeFromReport = e.excludeFromReport;
      if (e.fmvOverride != null) {
        _useFmvOverride = true;
        _fmvOverrideCtrl.text = e.fmvOverride!.toStringAsFixed(2);
      }
      _appraiserCtrl.text    = e.appraiserName ?? '';
      _appraisalValCtrl.text = e.formalAppraisalValue?.toStringAsFixed(2) ?? '';
      _certNumCtrl.text      = e.appraisalCertNumber ?? '';
      _appraisalDate         = e.appraisalDate;
    }
  }

  @override
  void dispose() {
    _notesCtrl.dispose();
    _fmvOverrideCtrl.dispose();
    _appraiserCtrl.dispose();
    _appraisalValCtrl.dispose();
    _certNumCtrl.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    setState(() => _saving = true);
    try {
      final bene = widget.beneficiaries
          .cast<EstateBeneficiary?>()
          .firstWhere((b) => b?.id == _beneficiaryId, orElse: () => null);

      final data = CoinEstateData(
        coinId:               widget.coin.id,
        beneficiaryId:        _beneficiaryId,
        beneficiaryName:      bene?.name,
        fmvOverride:          _useFmvOverride
            ? double.tryParse(_fmvOverrideCtrl.text)
            : null,
        appraiserName:        _appraiserCtrl.text.trim().isEmpty
            ? null
            : _appraiserCtrl.text.trim(),
        formalAppraisalValue: double.tryParse(_appraisalValCtrl.text),
        appraisalDate:        _appraisalDate,
        appraisalCertNumber:  _certNumCtrl.text.trim().isEmpty
            ? null
            : _certNumCtrl.text.trim(),
        estateNotes:          _notesCtrl.text.trim().isEmpty
            ? null
            : _notesCtrl.text.trim(),
        isHeirloom:           _isHeirloom,
        excludeFromReport:    _excludeFromReport,
      );

      await EstateDataService.saveCoinEstateData(widget.uid, data);
      if (mounted) Navigator.of(context).pop();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final coinTitle =
        '${widget.coin.year}${widget.coin.mintMark.isNotEmpty ? widget.coin.mintMark : ''} '
        '${widget.coin.denomination}';

    return DraggableScrollableSheet(
      initialChildSize: 0.85,
      maxChildSize: 0.95,
      minChildSize: 0.5,
      expand: false,
      builder: (_, scrollCtrl) => Container(
        decoration: const BoxDecoration(
          color: _kCard,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
          border: Border(top: BorderSide(color: _kCardBorder)),
        ),
        child: Column(
          children: [
            // Handle
            Center(
              child: Container(
                margin: const EdgeInsets.only(top: 10),
                width: 36,
                height: 4,
                decoration: BoxDecoration(
                  color: _kCardBorder,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            // Header
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
              child: Row(
                children: [
                  if (widget.coin.imageUrlObverse.isNotEmpty)
                    Container(
                      width: 40,
                      height: 40,
                      margin: const EdgeInsets.only(right: 10),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(6),
                        image: DecorationImage(
                          image: NetworkImage(widget.coin.imageUrlObverse),
                          fit: BoxFit.cover,
                        ),
                      ),
                    ),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(coinTitle,
                            style: const TextStyle(
                                color: _kTextPrimary,
                                fontSize: 15,
                                fontWeight: FontWeight.w700)),
                        if (widget.coin.condition.isNotEmpty)
                          Text(widget.coin.condition,
                              style: TextStyle(
                                  color: _kTextSecondary, fontSize: 11)),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: _kTextSecondary),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
            ),
            const Divider(color: _kCardBorder, height: 1),
            // Body
            Expanded(
              child: ListView(
                controller: scrollCtrl,
                padding: const EdgeInsets.all(16),
                children: [
                  // Beneficiary
                  _label('Assign to Beneficiary'),
                  const SizedBox(height: 6),
                  DropdownButtonFormField<String?>(
                    // ignore: deprecated_member_use — `value` drives selected item on a controlled dropdown
                    value: _beneficiaryId,
                    decoration: _inputDecoration(hint: 'Unassigned'),
                    dropdownColor: _kCard,
                    style: const TextStyle(color: _kTextPrimary, fontSize: 14),
                    items: [
                      const DropdownMenuItem(
                          value: null,
                          child: Text('Unassigned',
                              style: TextStyle(color: _kTextSecondary))),
                      ...widget.beneficiaries.map((b) => DropdownMenuItem(
                            value: b.id,
                            child: Text(b.name,
                                style: const TextStyle(color: _kTextPrimary)),
                          )),
                    ],
                    onChanged: (v) => setState(() => _beneficiaryId = v),
                  ),

                  const SizedBox(height: 14),

                  // Estate Notes
                  _label('Estate Notes'),
                  const SizedBox(height: 6),
                  TextFormField(
                    controller: _notesCtrl,
                    maxLines: 2,
                    style: const TextStyle(color: _kTextPrimary, fontSize: 14),
                    decoration: _inputDecoration(
                        hint: 'e.g. "Heirloom — do not sell", "Store separately"'),
                  ),

                  const SizedBox(height: 14),

                  // Heirloom + Exclude toggles
                  Row(
                    children: [
                      Expanded(
                        child: _ToggleTile(
                          label: 'Heirloom',
                          value: _isHeirloom,
                          onChanged: (v) => setState(() => _isHeirloom = v),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: _ToggleTile(
                          label: 'Exclude from Report',
                          value: _excludeFromReport,
                          onChanged: (v) =>
                              setState(() => _excludeFromReport = v),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 14),

                  // FMV Override
                  _ToggleTile(
                    label: 'Override AI FMV Estimate',
                    value: _useFmvOverride,
                    onChanged: (v) => setState(() => _useFmvOverride = v),
                  ),
                  if (_useFmvOverride) ...[
                    const SizedBox(height: 8),
                    TextFormField(
                      controller: _fmvOverrideCtrl,
                      keyboardType: const TextInputType.numberWithOptions(
                          decimal: true),
                      style: const TextStyle(
                          color: _kTextPrimary, fontSize: 14),
                      decoration: _inputDecoration(hint: 'e.g. 4500.00'),
                    ),
                  ],

                  const SizedBox(height: 16),
                  const Divider(color: _kCardBorder),
                  const SizedBox(height: 8),

                  // Formal Appraisal
                  Text('Formal Appraisal (optional)',
                      style: TextStyle(
                          color: _kGold,
                          fontSize: 12,
                          fontWeight: FontWeight.w600)),
                  const SizedBox(height: 10),
                  _sheetField('Appraiser Name', _appraiserCtrl,
                      hint: 'John Doe, ANA Certified'),
                  _sheetField('Appraisal Value (\$)', _appraisalValCtrl,
                      hint: '5000.00',
                      keyboardType: const TextInputType.numberWithOptions(
                          decimal: true)),
                  _sheetField('Certificate Number', _certNumCtrl,
                      hint: 'CERT-12345'),
                  const SizedBox(height: 8),
                  _label('Appraisal Date'),
                  const SizedBox(height: 6),
                  GestureDetector(
                    onTap: () async {
                      final picked = await showDatePicker(
                        context: context,
                        initialDate: _appraisalDate ?? DateTime.now(),
                        firstDate: DateTime(1950),
                        lastDate: DateTime.now(),
                        builder: (ctx, child) => Theme(
                            data: _estateTheme(ctx), child: child!),
                      );
                      if (picked != null && mounted) {
                        setState(() => _appraisalDate = picked);
                      }
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 14, vertical: 12),
                      decoration: BoxDecoration(
                        border: Border.all(color: _kCardBorder),
                        borderRadius: BorderRadius.circular(8),
                        color: _kNavy,
                      ),
                      child: Row(children: [
                        Icon(Icons.calendar_today_outlined,
                            size: 14, color: _kTextSecondary),
                        const SizedBox(width: 8),
                        Text(
                          _appraisalDate != null
                              ? DateFormat('MMMM d, yyyy')
                                  .format(_appraisalDate!)
                              : 'Select appraisal date',
                          style: TextStyle(
                            color: _appraisalDate != null
                                ? _kTextPrimary
                                : _kTextSecondary,
                            fontSize: 13,
                          ),
                        ),
                      ]),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Save
                  SizedBox(
                    width: double.infinity,
                    height: 48,
                    child: ElevatedButton(
                      onPressed: _saving ? null : _save,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _kNavy,
                        foregroundColor: _kGold,
                        side: const BorderSide(color: _kGold),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10)),
                      ),
                      child: _saving
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(
                                  color: _kGold, strokeWidth: 2))
                          : const Text('Save',
                              style: TextStyle(
                                  fontWeight: FontWeight.w700, fontSize: 14)),
                    ),
                  ),
                  const SizedBox(height: 32),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Sub-widgets
// ─────────────────────────────────────────────────────────────────────────────

class _SectionHeader extends StatelessWidget {
  final String title;
  final IconData icon;
  final Widget? trailing;
  const _SectionHeader(
      {required this.title, required this.icon, this.trailing});

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 8),
        child: Row(children: [
          Icon(icon, size: 14, color: _kGold),
          const SizedBox(width: 6),
          Text(title,
              style: const TextStyle(
                  color: _kGold,
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 0.8)),
          if (trailing != null) ...[
            const SizedBox(width: 6),
            trailing!,
          ],
        ]),
      );
}

class _EstateCard extends StatelessWidget {
  final List<Widget> children;
  const _EstateCard({required this.children});

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: _kCard,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: _kCardBorder),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withAlpha(60),
                blurRadius: 8,
                offset: const Offset(0, 2)),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: children,
        ),
      );
}

class _InfoBanner extends StatelessWidget {
  final Color color;
  final IconData icon;
  final String title;
  final String body;
  const _InfoBanner(
      {required this.color,
      required this.icon,
      required this.title,
      required this.body});

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: color.withAlpha(18),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withAlpha(80)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              Icon(icon, size: 14, color: color),
              const SizedBox(width: 6),
              Expanded(
                child: Text(title,
                    style: TextStyle(
                        color: color,
                        fontSize: 12,
                        fontWeight: FontWeight.w700)),
              ),
            ]),
            const SizedBox(height: 6),
            Text(body,
                style: const TextStyle(
                    color: _kTextSecondary, fontSize: 11, height: 1.5)),
          ],
        ),
      );
}

class _SegmentedPicker extends StatelessWidget {
  final List<String> options;
  final String value;
  final ValueChanged<String> onChanged;
  const _SegmentedPicker(
      {required this.options, required this.value, required this.onChanged});

  @override
  Widget build(BuildContext context) => Wrap(
        spacing: 6,
        runSpacing: 6,
        children: options.map((o) {
          final active = o == value;
          return GestureDetector(
            onTap: () => onChanged(o),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 150),
              padding:
                  const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: active ? _kGold.withAlpha(25) : Colors.transparent,
                borderRadius: BorderRadius.circular(6),
                border: Border.all(
                    color: active ? _kGold : _kCardBorder,
                    width: active ? 1.5 : 1),
              ),
              child: Text(o,
                  style: TextStyle(
                    color: active ? _kGold : _kTextSecondary,
                    fontSize: 12,
                    fontWeight:
                        active ? FontWeight.w600 : FontWeight.normal,
                  )),
            ),
          );
        }).toList(),
      );
}

class _BeneficiaryListEditor extends StatelessWidget {
  final List<EstateBeneficiary> beneficiaries;
  final bool showNjClass;
  final ValueChanged<List<EstateBeneficiary>> onChanged;

  const _BeneficiaryListEditor({
    required this.beneficiaries,
    required this.showNjClass,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        if (beneficiaries.isEmpty)
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: _kCard,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: _kCardBorder),
            ),
            child: Column(
              children: [
                Icon(Icons.people_outline,
                    size: 32, color: _kTextSecondary.withAlpha(120)),
                const SizedBox(height: 8),
                Text('No beneficiaries added yet.',
                    style: TextStyle(color: _kTextSecondary, fontSize: 12)),
              ],
            ),
          )
        else
          ...beneficiaries.asMap().entries.map((entry) {
            final i = entry.key;
            final b = entry.value;
            return _BeneficiaryRow(
              beneficiary: b,
              showNjClass: showNjClass,
              onUpdate: (updated) {
                final list = List<EstateBeneficiary>.from(beneficiaries);
                list[i] = updated;
                onChanged(list);
              },
              onDelete: () {
                final list = List<EstateBeneficiary>.from(beneficiaries);
                list.removeAt(i);
                onChanged(list);
              },
            );
          }),
        const SizedBox(height: 10),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: () {
              final newB = EstateBeneficiary(
                id: const Uuid().v4(),
                name: '',
              );
              onChanged([...beneficiaries, newB]);
            },
            icon: const Icon(Icons.add, size: 16, color: _kGold),
            label: const Text('Add Beneficiary',
                style: TextStyle(color: _kGold, fontSize: 13)),
            style: OutlinedButton.styleFrom(
              side: const BorderSide(color: _kGold, width: 1),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8)),
              padding: const EdgeInsets.symmetric(vertical: 10),
            ),
          ),
        ),
      ],
    );
  }
}

class _BeneficiaryRow extends StatefulWidget {
  final EstateBeneficiary beneficiary;
  final bool showNjClass;
  final ValueChanged<EstateBeneficiary> onUpdate;
  final VoidCallback onDelete;

  const _BeneficiaryRow({
    required this.beneficiary,
    required this.showNjClass,
    required this.onUpdate,
    required this.onDelete,
  });

  @override
  State<_BeneficiaryRow> createState() => _BeneficiaryRowState();
}

class _BeneficiaryRowState extends State<_BeneficiaryRow> {
  late final _nameCtrl = TextEditingController(text: widget.beneficiary.name);
  late String _relationship = widget.beneficiary.relationship;
  late String _njClass = widget.beneficiary.njClass;

  @override
  void dispose() { _nameCtrl.dispose(); super.dispose(); }

  void _emit() {
    widget.onUpdate(widget.beneficiary.copyWith(
      name: _nameCtrl.text.trim(),
      relationship: _relationship,
      njClass: _njClass,
    ));
  }

  @override
  Widget build(BuildContext context) => Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: _kCard,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: _kCardBorder),
        ),
        child: Column(
          children: [
            Row(children: [
              Expanded(
                flex: 3,
                child: TextField(
                  controller: _nameCtrl,
                  onChanged: (_) => _emit(),
                  style: const TextStyle(color: _kTextPrimary, fontSize: 13),
                  decoration: _inputDecoration(hint: 'Full Name').copyWith(
                    contentPadding: const EdgeInsets.symmetric(
                        horizontal: 10, vertical: 8),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                flex: 2,
                child: DropdownButtonFormField<String>(
                  // ignore: deprecated_member_use — `value` drives selected item on a controlled dropdown
                  value: _relationship,
                  decoration: _inputDecoration(hint: 'Rel.').copyWith(
                    contentPadding: const EdgeInsets.symmetric(
                        horizontal: 8, vertical: 8),
                  ),
                  dropdownColor: _kCard,
                  style: const TextStyle(color: _kTextPrimary, fontSize: 12),
                  items: const [
                    'Spouse', 'Child', 'Sibling',
                    'Friend', 'Charity', 'Other',
                  ].map((r) => DropdownMenuItem(
                        value: r,
                        child: Text(r,
                            style: const TextStyle(color: _kTextPrimary)),
                      )).toList(),
                  onChanged: (v) {
                    if (v != null) {
                      setState(() => _relationship = v);
                      _emit();
                    }
                  },
                ),
              ),
              IconButton(
                icon: const Icon(Icons.delete_outline,
                    size: 18, color: _kRed),
                onPressed: widget.onDelete,
              ),
            ]),
            if (widget.showNjClass) ...[
              const SizedBox(height: 8),
              Row(children: [
                Text('NJ Class: ',
                    style: TextStyle(
                        color: _kTextSecondary, fontSize: 11)),
                ...['A', 'C', 'D', 'E'].map((cls) {
                  final active = _njClass == cls;
                  return GestureDetector(
                    onTap: () {
                      setState(() => _njClass = cls);
                      _emit();
                    },
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 120),
                      margin: const EdgeInsets.only(right: 6),
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: active
                            ? const Color(0xFFEF4444).withAlpha(25)
                            : Colors.transparent,
                        borderRadius: BorderRadius.circular(4),
                        border: Border.all(
                            color: active
                                ? const Color(0xFFEF4444)
                                : _kCardBorder),
                      ),
                      child: Text(cls,
                          style: TextStyle(
                              color: active
                                  ? const Color(0xFFEF4444)
                                  : _kTextSecondary,
                              fontSize: 11,
                              fontWeight: active
                                  ? FontWeight.w700
                                  : FontWeight.normal)),
                    ),
                  );
                }),
              ]),
            ],
          ],
        ),
      );
}

class _ModeCard extends StatelessWidget {
  final bool selected;
  final String icon;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const _ModeCard({
    required this.selected,
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) => GestureDetector(
        onTap: onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: selected ? _kGold.withAlpha(15) : _kCard,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
              color: selected ? _kGold : _kCardBorder,
              width: selected ? 1.5 : 1,
            ),
          ),
          child: Row(children: [
            Text(icon, style: const TextStyle(fontSize: 24)),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title,
                      style: TextStyle(
                          color: selected ? _kGold : _kTextPrimary,
                          fontSize: 13,
                          fontWeight: FontWeight.w700)),
                  const SizedBox(height: 2),
                  Text(subtitle,
                      style: TextStyle(
                          color: _kTextSecondary, fontSize: 11)),
                ],
              ),
            ),
            if (selected)
              const Icon(Icons.check_circle_rounded,
                  color: _kGold, size: 20)
            else
              Icon(Icons.radio_button_unchecked_rounded,
                  color: _kTextSecondary.withAlpha(120), size: 20),
          ]),
        ),
      );
}

class _ChecklistCard extends StatelessWidget {
  final EstateProfile? profile;
  final int coinCount;
  const _ChecklistCard({required this.profile, required this.coinCount});

  @override
  Widget build(BuildContext context) {
    final p = profile;
    final items = [
      _ChecklistItem(
        label: 'Owner name set',
        ok: p != null && p.ownerName.isNotEmpty,
        required: true,
      ),
      _ChecklistItem(
        label: 'Jurisdiction selected',
        ok: p != null && p.jurisdiction.isNotEmpty,
        required: true,
      ),
      _ChecklistItem(
        label: 'Attorney info provided',
        ok: p != null && p.attorneyName.isNotEmpty,
        required: false,
      ),
      _ChecklistItem(
        label: 'Executor info provided',
        ok: p != null && p.executorName.isNotEmpty,
        required: false,
      ),
      _ChecklistItem(
        label: 'Beneficiaries added',
        ok: p != null && p.beneficiaries.isNotEmpty,
        required: false,
        warnIfMissing: true,
      ),
      _ChecklistItem(
        label: '$coinCount coin${coinCount == 1 ? '' : 's'} in collection',
        ok: coinCount > 0,
        required: true,
      ),
    ];

    return _EstateCard(
      children: items
          .map((item) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(children: [
                  Icon(
                    item.ok
                        ? Icons.check_circle_rounded
                        : (item.required || item.warnIfMissing)
                            ? Icons.warning_amber_rounded
                            : Icons.radio_button_unchecked_rounded,
                    size: 16,
                    color: item.ok
                        ? const Color(0xFF10B981)
                        : item.required
                            ? _kRed
                            : item.warnIfMissing
                                ? const Color(0xFFF59E0B)
                                : _kTextSecondary,
                  ),
                  const SizedBox(width: 8),
                  Text(item.label,
                      style: TextStyle(
                          color: item.ok
                              ? _kTextPrimary
                              : _kTextSecondary,
                          fontSize: 12)),
                ]),
              ))
          .toList(),
    );
  }
}

class _ChecklistItem {
  final String label;
  final bool ok;
  final bool required;
  final bool warnIfMissing;
  const _ChecklistItem({
    required this.label,
    required this.ok,
    this.required = false,
    this.warnIfMissing = false,
  });
}

class _GenerateButton extends StatelessWidget {
  final bool canGenerate;
  final bool generating;
  final int progressStep;
  final String progressMsg;
  final VoidCallback onGenerate;

  const _GenerateButton({
    required this.canGenerate,
    required this.generating,
    required this.progressStep,
    required this.progressMsg,
    required this.onGenerate,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        SizedBox(
          width: double.infinity,
          height: 60,
          child: GestureDetector(
            onTap: canGenerate ? onGenerate : null,
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              decoration: BoxDecoration(
                gradient: canGenerate
                    ? const LinearGradient(
                        colors: [_kNavy, _kDeepPurple],
                        begin: Alignment.centerLeft,
                        end: Alignment.centerRight,
                      )
                    : null,
                color: canGenerate ? null : _kCard,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: canGenerate ? _kGold : _kCardBorder,
                  width: canGenerate ? 1.5 : 1,
                ),
                boxShadow: canGenerate
                    ? [
                        BoxShadow(
                            color: _kGold.withAlpha(40),
                            blurRadius: 16,
                            spreadRadius: 1)
                      ]
                    : [],
              ),
              child: Center(
                child: generating
                    ? Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const SizedBox(
                            width: 18,
                            height: 18,
                            child: CircularProgressIndicator(
                                color: _kGold, strokeWidth: 2),
                          ),
                          const SizedBox(width: 12),
                          Text(progressMsg,
                              style: const TextStyle(
                                  color: _kGold,
                                  fontSize: 13,
                                  fontWeight: FontWeight.w600)),
                        ],
                      )
                    : Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.description_outlined,
                              color: canGenerate
                                  ? _kGold
                                  : _kTextSecondary,
                              size: 18),
                          const SizedBox(width: 10),
                          Text(
                            'Generate Estate Report',
                            style: TextStyle(
                              color: canGenerate
                                  ? _kGold
                                  : _kTextSecondary,
                              fontSize: 16,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 0.5,
                            ),
                          ),
                        ],
                      ),
              ),
            ),
          ),
        ),
        if (!canGenerate && !generating) ...[
          const SizedBox(height: 6),
          Text(
            'Complete required fields above to generate',
            style: TextStyle(color: _kTextSecondary, fontSize: 11),
            textAlign: TextAlign.center,
          ),
        ],
        if (generating && progressStep < 4) ...[
          const SizedBox(height: 10),
          LinearProgressIndicator(
            value: (progressStep + 1) / 5.0,
            backgroundColor: _kCardBorder,
            valueColor: const AlwaysStoppedAnimation<Color>(_kGold),
            borderRadius: BorderRadius.circular(4),
          ),
        ],
      ],
    );
  }
}

class _StatChip extends StatelessWidget {
  final String label;
  final String value;
  final bool highlight;
  final bool warn;
  const _StatChip(this.label, this.value,
      {this.highlight = false, this.warn = false});

  @override
  Widget build(BuildContext context) => Expanded(
        child: Container(
          margin: const EdgeInsets.only(right: 6),
          padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 6),
          decoration: BoxDecoration(
            color: _kCard,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(
              color: highlight
                  ? _kGold.withAlpha(80)
                  : warn
                      ? _kRed.withAlpha(80)
                      : _kCardBorder,
            ),
          ),
          child: Column(
            children: [
              Text(value,
                  style: TextStyle(
                      color: highlight
                          ? _kGold
                          : warn
                              ? _kRed
                              : _kTextPrimary,
                      fontSize: 13,
                      fontWeight: FontWeight.w700)),
              const SizedBox(height: 2),
              Text(label,
                  style: TextStyle(
                      color: _kTextSecondary, fontSize: 9),
                  textAlign: TextAlign.center),
            ],
          ),
        ),
      );
}

class _CoinEstateRow extends StatelessWidget {
  final CoinModel coin;
  final CoinEstateData? estateData;
  final double fmv;
  final bool needsAppraisal;
  final VoidCallback onTap;

  const _CoinEstateRow({
    required this.coin,
    required this.estateData,
    required this.fmv,
    required this.needsAppraisal,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final title =
        '${coin.year}${coin.mintMark.isNotEmpty ? coin.mintMark : ''} '
        '${coin.denomination}';
    final hasPhoto = coin.imageUrlObverse.isNotEmpty;
    final beneAssigned = estateData?.beneficiaryName != null;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: _kCard,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: needsAppraisal
                ? _kGold.withAlpha(80)
                : _kCardBorder,
          ),
        ),
        child: Row(children: [
          // Thumbnail
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(4),
              color: _kNavy,
              image: hasPhoto
                  ? DecorationImage(
                      image: NetworkImage(coin.imageUrlObverse),
                      fit: BoxFit.cover,
                    )
                  : null,
            ),
            child: hasPhoto
                ? null
                : const Icon(Icons.monetization_on_outlined,
                    color: _kTextSecondary, size: 18),
          ),
          const SizedBox(width: 10),

          // Coin info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: const TextStyle(
                        color: _kTextPrimary,
                        fontSize: 12,
                        fontWeight: FontWeight.w600)),
                if (coin.condition.isNotEmpty)
                  Text(coin.condition,
                      style: TextStyle(
                          color: _kTextSecondary, fontSize: 10)),
              ],
            ),
          ),

          // FMV
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                fmv > 0 ? _dollarFmt.format(fmv) : '–',
                style: TextStyle(
                  color: needsAppraisal ? _kGold : _kTextPrimary,
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                ),
              ),
              if (needsAppraisal)
                Text('Appraise',
                    style: TextStyle(
                        color: _kGold.withAlpha(180), fontSize: 9)),
            ],
          ),
          const SizedBox(width: 8),

          // Beneficiary chip
          if (beneAssigned)
            Container(
              padding: const EdgeInsets.symmetric(
                  horizontal: 7, vertical: 3),
              decoration: BoxDecoration(
                color: const Color(0xFF10B981).withAlpha(25),
                borderRadius: BorderRadius.circular(4),
                border: Border.all(
                    color: const Color(0xFF10B981).withAlpha(80)),
              ),
              child: Text(
                estateData!.beneficiaryName!.split(' ').first,
                style: const TextStyle(
                    color: Color(0xFF10B981),
                    fontSize: 9,
                    fontWeight: FontWeight.w600),
              ),
            )
          else
            Container(
              padding: const EdgeInsets.symmetric(
                  horizontal: 7, vertical: 3),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(4),
                border: Border.all(
                    color: _kTextSecondary.withAlpha(60),
                    style: BorderStyle.solid),
              ),
              child: Text('+Assign',
                  style: TextStyle(
                      color: _kTextSecondary, fontSize: 9)),
            ),
        ]),
      ),
    );
  }
}

class _ReportHistoryRow extends StatelessWidget {
  final EstateReportRecord record;
  final VoidCallback onReopen;

  const _ReportHistoryRow({required this.record, required this.onReopen});

  @override
  Widget build(BuildContext context) => Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: _kCard,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: _kCardBorder),
        ),
        child: Row(children: [
          const Icon(Icons.description_outlined,
              size: 20, color: _kTextSecondary),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(record.modeLabel,
                    style: const TextStyle(
                        color: _kTextPrimary,
                        fontSize: 12,
                        fontWeight: FontWeight.w600)),
                Text(
                  '${record.state} • ${record.totalCoins} coins • '
                  '${_dollarFmt.format(record.totalFmv)} FMV',
                  style: TextStyle(color: _kTextSecondary, fontSize: 10),
                ),
                Text(
                  DateFormat('MMM d, yyyy – h:mm a').format(record.generatedAt),
                  style:
                      TextStyle(color: _kTextSecondary.withAlpha(140), fontSize: 9),
                ),
              ],
            ),
          ),
          TextButton(
            onPressed: onReopen,
            style: TextButton.styleFrom(foregroundColor: _kGold),
            child: const Text('Re-open', style: TextStyle(fontSize: 11)),
          ),
        ]),
      );
}

// ── NY-Specific Warning Card ─────────────────────────────────────────────────
class _NyWarningCard extends StatelessWidget {
  final double? totalFmv; // if known, shows proximity to cliff
  const _NyWarningCard({this.totalFmv});

  static const _kCliffExemption = 7_350_000.0;
  static const _kCliffThreshold = 7_350_000.0 * 1.05; // $7,717,500

  @override
  Widget build(BuildContext context) {
    final double? fmv = totalFmv;
    final bool overCliff = fmv != null && fmv > _kCliffThreshold;
    final bool nearCliff = fmv != null && !overCliff && fmv > _kCliffExemption;
    final Color borderColor = overCliff
        ? _kRed
        : nearCliff
            ? const Color(0xFFFF9800)
            : const Color(0xFFE3B04B); // amber for informational
    final Color bgColor = overCliff
        ? _kRed.withAlpha(18)
        : nearCliff
            ? const Color(0xFFFF9800).withAlpha(15)
            : const Color(0xFFE3B04B).withAlpha(12);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: borderColor.withAlpha(120)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.account_balance_outlined,
                  size: 16, color: borderColor),
              const SizedBox(width: 8),
              Text(
                'New York Estate Planning — Key Alerts',
                style: TextStyle(
                    color: borderColor,
                    fontSize: 13,
                    fontWeight: FontWeight.w700),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Cliff rule
          _NyAlert(
            icon: Icons.warning_amber_rounded,
            title: 'Estate Tax Cliff Rule',
            body: 'If gross estate exceeds \$7,717,500 (105% of the '
                '\$7,350,000 exemption), the ENTIRE estate is taxed — '
                'not just the excess. This coin collection alone does not '
                'trigger the cliff, but combined with real estate, retirement '
                'accounts, and life insurance it may.',
          ),
          const SizedBox(height: 10),

          // 3-year gift clawback
          _NyAlert(
            icon: Icons.history_toggle_off_rounded,
            title: '3-Year Gift Clawback',
            body: 'Gifts made within 3 years of death are added back to the '
                'gross estate for purposes of the cliff calculation. '
                'Any coins gifted recently should be disclosed to your '
                'estate attorney.',
          ),
          const SizedBox(height: 10),

          // ET-706 / filing deadline
          _NyAlert(
            icon: Icons.schedule_rounded,
            title: 'ET-706 Filing Deadline',
            body: 'If the gross estate exceeds \$7,350,000, a NY estate '
                'tax return (ET-706) must be filed within 9 months of death — '
                'the same deadline as the Surrogate\'s Court inventory '
                '(SCPA §2102 / 22 NYCRR §207.20).',
          ),

          if (fmv != null) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: const Color(0xFF0E1117),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Text('Collection FMV',
                      style: TextStyle(
                          color: _kTextSecondary, fontSize: 12)),
                  const Spacer(),
                  Text(
                    '\$${fmv.toStringAsFixed(0).replaceAllMapped(RegExp(r"(\d{1,3})(?=(\d{3})+(?!\d))"), (m) => "${m[1]},")}',
                    style: TextStyle(
                        color: overCliff ? _kRed : _kGold,
                        fontSize: 13,
                        fontWeight: FontWeight.w700),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    overCliff
                        ? '⚠ OVER CLIFF'
                        : nearCliff
                            ? '⚡ Near cliff'
                            : '\$${(_kCliffThreshold - fmv).toStringAsFixed(0).replaceAllMapped(RegExp(r"(\d{1,3})(?=(\d{3})+(?!\d))"), (m) => "${m[1]},")} below cliff',
                    style: TextStyle(
                        color: overCliff
                            ? _kRed
                            : nearCliff
                                ? const Color(0xFFFF9800)
                                : _kTextSecondary,
                        fontSize: 11),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _NyAlert extends StatelessWidget {
  final IconData icon;
  final String title;
  final String body;
  const _NyAlert({required this.icon, required this.title, required this.body});

  @override
  Widget build(BuildContext context) => Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Icon(icon, size: 15, color: const Color(0xFFE3B04B)),
      const SizedBox(width: 8),
      Expanded(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title,
                style: const TextStyle(
                    color: _kTextPrimary,
                    fontSize: 12,
                    fontWeight: FontWeight.w600)),
            const SizedBox(height: 2),
            Text(body,
                style: const TextStyle(
                    color: _kTextSecondary, fontSize: 11, height: 1.5)),
          ],
        ),
      ),
    ],
  );
}

// ── Premium Gate ─────────────────────────────────────────────────────────────
class _PremiumGate extends StatelessWidget {

  final VoidCallback onUpgrade;
  const _PremiumGate({required this.onUpgrade});

  @override
  Widget build(BuildContext context) => Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text('👑', style: TextStyle(fontSize: 48)),
              const SizedBox(height: 16),
              const Text('Estate Planning',
                  style: TextStyle(
                      color: _kGold,
                      fontSize: 22,
                      fontWeight: FontWeight.w700)),
              const SizedBox(height: 8),
              Text(
                'Premium Feature',
                style: TextStyle(color: _kTextSecondary, fontSize: 14),
              ),
              const SizedBox(height: 16),
              Text(
                'Generate court-ready estate reports, assign beneficiaries, '
                'track formal appraisals, and share a secure attorney portal — '
                'all with one click.',
                style: TextStyle(
                    color: _kTextSecondary, fontSize: 13, height: 1.6),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 28),
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton(
                  onPressed: onUpgrade,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _kGold,
                    foregroundColor: _kNavy,
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10)),
                    textStyle: const TextStyle(
                        fontSize: 15, fontWeight: FontWeight.w700),
                  ),
                  child: const Text('Upgrade to Estate Tier'),
                ),
              ),
            ],
          ),
        ),
      );
}

class _ToggleTile extends StatelessWidget {
  final String label;
  final bool value;
  final ValueChanged<bool> onChanged;
  const _ToggleTile(
      {required this.label, required this.value, required this.onChanged});

  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: _kNavy,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: _kCardBorder),
        ),
        child: Row(children: [
          Expanded(
            child: Text(label,
                style: const TextStyle(
                    color: _kTextPrimary, fontSize: 12)),
          ),
          Switch(
            value: value,
            onChanged: onChanged,
            activeThumbColor: _kGold,
            activeTrackColor: _kGold.withAlpha(80),
            inactiveTrackColor: _kCardBorder,
            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
          ),
        ]),
      );
}

// ─────────────────────────────────────────────────────────────────────────────
// Helper: Sheet text field
// ─────────────────────────────────────────────────────────────────────────────
Widget _sheetField(String label, TextEditingController ctrl,
    {String hint = '', TextInputType? keyboardType}) {
  return Padding(
    padding: const EdgeInsets.only(bottom: 10),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label,
            style: TextStyle(
                color: _kTextSecondary,
                fontSize: 10,
                fontWeight: FontWeight.w600)),
        const SizedBox(height: 4),
        TextFormField(
          controller: ctrl,
          keyboardType: keyboardType,
          style: const TextStyle(color: _kTextPrimary, fontSize: 13),
          decoration: _inputDecoration(hint: hint),
        ),
      ],
    ),
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Helper: form field with label
// ─────────────────────────────────────────────────────────────────────────────
Widget _formField(
  String label,
  TextEditingController ctrl, {
  String hint = '',
  bool required = false,
  int maxLines = 1,
  TextInputType? keyboardType,
}) {
  return Padding(
    padding: const EdgeInsets.only(bottom: 12),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(children: [
          Text(label,
              style: TextStyle(
                  color: _kTextSecondary,
                  fontSize: 10,
                  fontWeight: FontWeight.w600)),
          if (required)
            const Text(' *',
                style: TextStyle(color: _kRed, fontSize: 10)),
        ]),
        const SizedBox(height: 4),
        TextFormField(
          controller: ctrl,
          maxLines: maxLines,
          keyboardType: keyboardType,
          style: const TextStyle(color: _kTextPrimary, fontSize: 14),
          decoration: _inputDecoration(hint: hint),
          validator: required
              ? (v) =>
                  (v == null || v.trim().isEmpty) ? 'Required' : null
              : null,
        ),
      ],
    ),
  );
}

Widget _label(String text) => Text(text,
    style: TextStyle(
        color: _kTextSecondary,
        fontSize: 10,
        fontWeight: FontWeight.w600));

InputDecoration _inputDecoration({String hint = ''}) => InputDecoration(
      hintText: hint,
      hintStyle: TextStyle(color: _kTextSecondary.withAlpha(120), fontSize: 13),
      filled: true,
      fillColor: _kNavy,
      contentPadding:
          const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: _kCardBorder),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: _kCardBorder),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: _kGold, width: 1.5),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: _kRed),
      ),
    );

// ─────────────────────────────────────────────────────────────────────────────
// _ShareOption — tappable card for the share bottom sheet
// ─────────────────────────────────────────────────────────────────────────────
class _ShareOption extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String title;
  final String subtitle;
  final VoidCallback onTap;

  const _ShareOption({
    required this.icon,
    required this.color,
    required this.title,
    required this.subtitle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: _kNavy,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: _kCardBorder),
        ),
        child: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: color.withAlpha(20),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: color.withAlpha(50)),
              ),
              child: Icon(icon, color: color, size: 20),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title,
                      style: const TextStyle(
                          color: _kTextPrimary,
                          fontSize: 13,
                          fontWeight: FontWeight.w600)),
                  const SizedBox(height: 2),
                  Text(subtitle,
                      style: const TextStyle(
                          color: _kTextSecondary, fontSize: 11)),
                ],
              ),
            ),
            const Icon(Icons.chevron_right_rounded,
                color: _kTextSecondary, size: 18),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Estate-specific dark theme
// ─────────────────────────────────────────────────────────────────────────────
ThemeData _estateTheme(BuildContext context) => ThemeData.dark().copyWith(
      scaffoldBackgroundColor: _kNavy,
      colorScheme: const ColorScheme.dark(
        primary: _kGold,
        secondary: _kGold,
        surface: _kCard,
        error: _kRed,
      ),
      dialogTheme: const DialogThemeData(backgroundColor: _kCard),
      cardColor: _kCard,
    );

