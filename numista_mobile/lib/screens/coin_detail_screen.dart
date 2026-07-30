// coin_detail_screen.dart
//
// Full-screen coin detail modal for Numista.AI.
// Opens as a bottom sheet (mobile) or centered dialog (desktop ≥ 800px).
//
// Design decisions:
//   - Edit flow   : inline form inside the detail view (no screen switch)
//   - AI Insights : direct Gemini 3.5 Flash call via firebase_ai (no backend hop)
//
// Usage:
//   CoinDetailScreen.show(context, coin: coin, spotPrices: _spotPrices,
//     onNavigateToAiChat: (query) => ...,
//     onDeleted: () => ...,
//   );

import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_ai/firebase_ai.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';
import '../models/coin_model.dart';
import '../constants.dart';
import '../services/auth_service.dart';
import '../services/inspector_service.dart';
import '../services/melt_value_service.dart';
import '../services/wishlist_service.dart';
import '../services/coin_image_service.dart';
import '../services/mint_error_service.dart';
import '../widgets/grade_badge_widget.dart';
import '../widgets/glossary_tooltip_wrapper.dart';
import '../models/mint_error.dart';
import 'mint_error_detail_screen.dart';
import '../widgets/coin_set_viewer.dart';
import '../widgets/set_contents_panel.dart';

// ─── Design tokens (match app-wide palette) ────────────────────────────────────
const _kBg       = Color(0xFF0B1120);
const _kSurface  = Color(0xFF1E2937);
const _kDark     = Color(0xFF0B1120);
const _kText     = Color(0xFFE8EAF0);
const _kSubtext  = Color(0xFF8B92B4);
const _kAccent   = Color(0xFFC9A227);
const _kBrand    = Color(0xFFF63366);
const _kGreen    = Color(0xFF28A745);
const _kRed      = Color(0xFFDC3545);
const _kGold     = Color(0xFFC9A227);
const _kBorder   = Color(0xFF2D3143);

// ─── Helpers ──────────────────────────────────────────────────────────────────

/// Formats a raw denomination string for display.
/// "5"  → "$5"   |  "25" → "$25"  |  "$5" → "$5"  |  "Half Dollar" → "Half Dollar"
String _fmtDenomination(String raw) {
  final s = raw.trim();
  if (s.isEmpty) return s;
  // Already has a currency symbol or is non-numeric — pass through
  if (s.startsWith(r'$') || s.startsWith('£') || s.startsWith('€') ||
      s.startsWith('¥') || s.contains('¢') || s.contains('Cent') ||
      s.contains('Dollar') || s.contains('Eagle') || s.contains('Mill')) {
    return s;
  }
  // Pure number (int or decimal) → prepend $, strip trailing .0
  final num? parsed = num.tryParse(s);
  if (parsed != null) {
    final intVal = parsed.toInt();
    final formatted = (parsed - intVal == 0)
        ? '\$$intVal'
        : '\$$parsed';
    return formatted;
  }
  return s;
}

// ─── Entry point ──────────────────────────────────────────────────────────────
class CoinDetailScreen extends StatefulWidget {
  final CoinModel coin;
  final Map<String, double> spotPrices;
  final void Function(String query)? onNavigateToAiChat;
  final VoidCallback? onDeleted;
  final VoidCallback? onEdited;

  const CoinDetailScreen({
    super.key,
    required this.coin,
    this.spotPrices = const {},
    this.onNavigateToAiChat,
    this.onDeleted,
    this.onEdited,
  });

  /// Convenience: opens the right modal depending on screen width.
  static Future<void> show(
    BuildContext context, {
    required CoinModel coin,
    Map<String, double> spotPrices = const {},
    void Function(String query)? onNavigateToAiChat,
    VoidCallback? onDeleted,
    VoidCallback? onEdited,
  }) {
    final width = MediaQuery.of(context).size.width;
    final widget = CoinDetailScreen(
      coin: coin,
      spotPrices: spotPrices,
      onNavigateToAiChat: onNavigateToAiChat,
      onDeleted: onDeleted,
      onEdited: onEdited,
    );

    if (width >= 800) {
      // Desktop: centered dialog
      return showDialog<void>(
        context: context,
        barrierColor: Colors.black54,
        builder: (_) => Dialog(
          backgroundColor: Colors.transparent,
          insetPadding: const EdgeInsets.symmetric(horizontal: 40, vertical: 32),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 860, maxHeight: 760),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: widget,
            ),
          ),
        ),
      );
    } else {
      // Mobile: draggable bottom sheet
      return showModalBottomSheet<void>(
        context: context,
        isScrollControlled: true,
        backgroundColor: Colors.transparent,
        builder: (_) => DraggableScrollableSheet(
          initialChildSize: 0.92,
          minChildSize: 0.5,
          maxChildSize: 1.0,
          builder: (_, ctrl) => ClipRRect(
            borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
            child: widget,
          ),
        ),
      );
    }
  }

  @override
  State<CoinDetailScreen> createState() => _CoinDetailScreenState();
}

class _CoinDetailScreenState extends State<CoinDetailScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabCtrl;
  late CoinModel _coin;

  bool _inEditMode = false;
  bool _isOnWishlist = false;
  bool _wishlistLoading = false;
  bool _aiLoading = false;
  bool _aiLoaded = false;
  String _aiInsight = '';
  String? _aiError;
  bool _isInspectorMode = false;

  // Edit-mode controllers
  final Map<String, TextEditingController> _editCtrl = {};

  @override
  void initState() {
    super.initState();
    _coin = widget.coin;
    _tabCtrl = TabController(length: 6, vsync: this);
    _tabCtrl.addListener(() {
      if (_tabCtrl.index == 3 && !_aiLoaded && !_aiLoading) {
        _loadAiInsight();
      }
    });
    _loadInspectorMode();
  }

  void _loadInspectorMode() async {
    final enabled = await InspectorService.isEnabled();
    if (mounted) {
      setState(() {
        _isInspectorMode = enabled;
      });
    }
  }

  void _showDiscrepancyDialog(String fieldName, String currentValue) {
    final commentCtrl = TextEditingController();
    final reportedCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Row(
          children: const [
            Icon(Icons.bug_report, color: _kAccent),
            SizedBox(width: 8),
            Text('Report Discrepancy'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Field: $fieldName',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            const SizedBox(height: 6),
            Text('Current value: "$currentValue"',
                style: const TextStyle(fontSize: 13, color: _kSubtext)),
            const SizedBox(height: 16),
            TextField(
              controller: reportedCtrl,
              decoration: const InputDecoration(
                labelText: 'Corrected Value (Optional)',
                border: OutlineInputBorder(),
                isDense: true,
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: commentCtrl,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'Notes / Reason for discrepancy',
                border: OutlineInputBorder(),
                isDense: true,
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: _kAccent),
            onPressed: () async {
              final comment = commentCtrl.text.trim();
              final corrected = reportedCtrl.text.trim();
              if (comment.isEmpty && corrected.isEmpty) return;

              // Save to Firestore
              await FirebaseFirestore.instance.collection('tester_feedback').add({
                'coin_id': _coin.id,
                'user_email': AuthService.userEmail,
                'target_field': fieldName,
                'reported_value': corrected,
                'user_comment': comment,
                'associated_image': _coin.imageUrlObverse,
                'timestamp': FieldValue.serverTimestamp(),
              });

              // Flag the coin's status in Firestore
              await FirebaseFirestore.instance
                  .doc('${AuthService.coinsPath}/${_coin.id}')
                  .update({
                'image_verification_status': 'flagged',
                'image_verification_reason': 'Tester metadata discrepancy on $fieldName: $comment',
              });

              if (ctx.mounted) Navigator.pop(ctx);
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Thank you! Feedback logged successfully.')),
                );
              }
            },
            child: const Text('Submit Report', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _tabCtrl.dispose();
    for (final c in _editCtrl.values) { c.dispose(); }
    super.dispose();
  }

  // ── AI Insight (Gemini 3.5 Flash — direct via firebase_ai) ────────────────
  Future<void> _loadAiInsight() async {
    if (_aiLoading || _aiLoaded) return;
    setState(() { _aiLoading = true; _aiError = null; _aiInsight = ''; });

    try {
      final model = FirebaseAI.googleAI().generativeModel(
        model: 'gemini-3.5-flash',
        generationConfig: GenerationConfig(temperature: 0.7),
      );

      // Build parts list — text prompt only (Vertex AI FileData requires GCS URIs,
      // not public HTTP URLs; image URL is referenced in prompt text instead)
      final parts = <Part>[TextPart(_buildAiPrompt())];

      // Stream the response for a live typing feel
      final stream = model.generateContentStream([Content.multi(parts)]);
      final buffer = StringBuffer();
      await for (final chunk in stream) {
        final text = chunk.text ?? '';
        if (text.isNotEmpty) {
          buffer.write(text);
          if (mounted) {
            setState(() { _aiInsight = buffer.toString(); });
          }
        }
      }

      if (!mounted) return;
      setState(() { _aiLoaded = true; _aiLoading = false; });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _aiInsight = _localInsightFallback();
        _aiLoaded = true;
        _aiLoading = false;
        _aiError = 'Live AI unavailable — showing local summary.';
      });
    }
  }

  String _buildAiPrompt() {
    final c = _coin;
    final denom = _fmtDenomination(c.denomination);
    final coinId = [
      if (c.year.isNotEmpty) c.year.replaceAll(RegExp(r'\.0$'), ''),
      if (c.mintMark.isNotEmpty) '(${c.mintMark})',
      if (denom.isNotEmpty) denom,
      if (c.programSeries.isNotEmpty) c.programSeries,
    ].join(' ');
    final hasImages = c.imageUrlObverse.isNotEmpty || c.imageUrlReverse.isNotEmpty;

    return '''
You are an expert numismatist and coin historian. A collector wants a comprehensive analysis of the following coin in their collection:

**Coin:** $coinId
**Condition/Grade:** ${c.condition.isNotEmpty ? c.condition : 'Unknown'}
**Metal Content:** ${c.metalContent.isNotEmpty ? c.metalContent : 'Unknown'}
**Variety:** ${c.variety.isNotEmpty ? c.variety : 'None noted'}
**Estimated Value:** ${c.aiEstimatedValue}
${hasImages ? '\nCoin images are attached. Please include observations on strike quality, luster, and surface preservation based on the photos.\n' : ''}
Provide a comprehensive numismatic analysis using these exact section headers:

## History & Background
When and why this coin was minted. Its place in US (or world) coinage history. Any notable legislation, acts of Congress, or historical events that shaped it.

## The Iconic Design
Describe the obverse and reverse designs in detail. Name the designer(s) and the artistic inspiration. Note symbolic significance.

## Specifications & Mintage
Key specs: weight, diameter, metal composition, edge. Mintage figures for **this specific year and mint mark**. Compare to other years in the series — is this a high or low mintage year?

## ${c.condition.isNotEmpty ? '${c.condition} — ' : ''}Grade & Collector Value
What this grade means for this specific coin type. Current market value range. Any notable recent auction results. Investment outlook compared to the series average.

## ${hasImages ? 'Visual Assessment\nBased on the attached photos: describe what you observe about the coin\'s strike quality, luster, and any notable surface characteristics.\n\n## ' : ''}Collector Tips
Key dates and varieties to know. Common counterfeits to watch for. Storage recommendations for this metal type. Why this coin is (or isn't) a standout in its series. What a collector should look for when grading up.

Write in an engaging, authoritative style like a respected numismatic reference. Be specific — use real mintage numbers, designer names, and current dollar values where you know them.''';
  }

  String _localInsightFallback() {
    final c = _coin;
    final denom = _fmtDenomination(c.denomination);
    final series = c.programSeries.isNotEmpty ? c.programSeries : 'US coinage';
    final parts = <String>[
      if (c.year.isNotEmpty && denom.isNotEmpty)
        'This ${c.year} $denom is part of the $series.',
      if (c.condition.isNotEmpty && c.condition != 'Ungraded')
        'Graded ${c.condition}, it represents ${_gradeDescription(c.condition)}.',
      if (c.metalContent.isNotEmpty && c.metalContent != 'Unknown')
        'Struck in ${c.metalContent}.',
      'Tap "Ask follow-up in AI Chat" for a full numismatic deepdive — history, design, mintage, and current market value.',
    ];
    return parts.join(' ');
  }

  String _gradeDescription(String grade) {
    final g = grade.toUpperCase();
    if (g.contains('MS-7') || g.contains('MS-6')) return 'exceptional mint-state preservation';
    if (g.contains('MS')) return 'mint-state condition';
    if (g.contains('PROOF') || g.contains('PR') || g.contains('PF')) return 'premium proof quality';
    if (g.contains('AU')) return 'about-uncirculated quality with minimal wear';
    if (g.contains('VF')) return 'very fine condition';
    return 'collectible circulated condition';
  }

  // ── Edit mode ──────────────────────────────────────────────────────────────
  void _enterEditMode() {
    _editCtrl.clear();
    final fields = {
      'Year': _coin.year,
      'Mint Mark': _coin.mintMark,
      'Denomination': _coin.denomination,
      'Program/Series': _coin.programSeries,
      'Theme/Subject': _coin.themeSubject,
      'Variety': _coin.variety,
      'Condition': _coin.condition,
      'Strike Type': _coin.strikeType,
      'Holder Type': _coin.holderType,
      'Grading Service': _coin.gradingService,
      'Certification Number': _coin.certificationNumber,
      'Metal Content': _coin.metalContent,
      'Purchase Cost': _coin.purchaseCost,
      'Purchase Date': _coin.purchaseDate,
      'Retailer/Website': _coin.retailer,
      'Storage Location': _coin.storageLocation,
      'Personal Notes': _coin.personalNotes,
    };
    for (final e in fields.entries) {
      _editCtrl[e.key] = TextEditingController(text: e.value);
    }
    setState(() => _inEditMode = true);
  }

  Future<void> _saveEdits() async {
    final updates = <String, dynamic>{};
    _editCtrl.forEach((key, ctrl) {
      final fsKey = _fieldToFirestore(key);
      if (fsKey != null) updates[fsKey] = ctrl.text;
    });

    // ── Auto-split combined Year+Mint (e.g. "2006D" typed into Year field) ────
    final ymRe = RegExp(r'^(\d{4}(?:-\d{4})?)\s*([A-WY-Z])$', caseSensitive: false);
    final rawYear = (updates['Year'] as String? ?? '').trim();
    final rawMint = (updates['Mint Mark'] as String? ?? '').trim();
    bool yearMintSplit = false;
    if (rawYear.isNotEmpty && rawMint.isEmpty) {
      final m = ymRe.firstMatch(rawYear);
      if (m != null) {
        updates['Year']      = m.group(1)!;
        updates['Mint Mark'] = m.group(2)!.toUpperCase();
        // Also update the in-memory controllers so the UI reflects the split
        _editCtrl['Year']?.text      = m.group(1)!;
        _editCtrl['Mint Mark']?.text = m.group(2)!.toUpperCase();
        yearMintSplit = true;
      }
    }

    try {
      await FirebaseFirestore.instance
          .collection(AuthService.coinsPath)
          .doc(_coin.id)
          .update(updates);
      // Optimistically update local model
      final updated = CoinModel.fromMap({
        ..._coin.toFirestore(),
        ...updates,
        'timestamp': _coin.timestamp,
      }, _coin.id);
      if (!mounted) return;
      setState(() { _coin = updated; _inEditMode = false; });
      widget.onEdited?.call();
      if (mounted) {
        final msg = yearMintSplit
            ? 'Changes saved ✓ (Year & Mint Mark split automatically)'
            : 'Changes saved ✓';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(msg), backgroundColor: _kGreen),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Save failed: $e'), backgroundColor: _kRed),
        );
      }
    }
  }


  String? _fieldToFirestore(String label) {
    const map = {
      'Year': 'Year',
      'Mint Mark': 'Mint Mark',
      'Denomination': 'Denomination',
      'Program/Series': 'Program/Series',
      'Theme/Subject': 'Theme/Subject',
      'Variety': 'Variety',
      'Condition': 'Condition',
      'Strike Type': 'Strike Type',
      'Holder Type': 'Holder Type',
      'Grading Service': 'Grading Service',
      'Certification Number': 'Certification Number',
      'Metal Content': 'Metal Content',
      'Purchase Cost': 'Purchase Cost',
      'Purchase Date': 'Purchase Date',
      'Retailer/Website': 'Retailer/Website',
      'Storage Location': 'Storage Location',
      'Personal Notes': 'Personal Notes I',
    };
    return map[label];
  }

  // ── Delete ─────────────────────────────────────────────────────────────────
  Future<void> _confirmDelete() async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1A1D27),
        title: const Text('Delete Coin', style: TextStyle(color: Colors.white)),
        content: Text(
          'Remove "${_coin.year} ${_coin.denomination}" from your collection? This cannot be undone.',
          style: const TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Cancel', style: TextStyle(color: Colors.white54))),
          TextButton(onPressed: () => Navigator.pop(ctx, true),
              child: const Text('Delete', style: TextStyle(color: _kBrand))),
        ],
      ),
    );
    if (ok != true || !mounted) return;
    await FirebaseFirestore.instance
        .collection(AuthService.coinsPath)
        .doc(_coin.id)
        .delete();
    if (mounted) {
      Navigator.of(context).pop();
      widget.onDeleted?.call();
    }
  }

  // ── Wishlist toggle ────────────────────────────────────────────────────────
  Future<void> _toggleWishlist() async {
    setState(() => _wishlistLoading = true);
    try {
      if (_isOnWishlist) {
        // Find and remove
        final snap = await FirebaseFirestore.instance
            .collection('users')
            .doc(AuthService.userEmail)
            .collection('wishlist')
            .where('type', isEqualTo: 'individual')
            .get();
        for (final doc in snap.docs) {
          final data = doc.data();
          final c = data['coin'] as Map<String, dynamic>?;
          if (c != null &&
              c['Year'] == _coin.year &&
              c['Denomination'] == _coin.denomination &&
              c['Mint Mark'] == _coin.mintMark) {
            await doc.reference.delete();
          }
        }
        if (mounted) setState(() { _isOnWishlist = false; _wishlistLoading = false; });
      } else {
        await WishlistService.addToWishlist(_coin);
        if (mounted) setState(() { _isOnWishlist = true; _wishlistLoading = false; });
      }
    } catch (_) {
      if (mounted) setState(() => _wishlistLoading = false);
    }
  }

  // ── Manual Verification ────────────────────────────────────────────────────
  Future<void> _verifyManually() async {
    final email = AuthService.userEmail;
    if (email.isEmpty) return;

    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Verify Manually?', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        content: const Text(
          'This will submit the coin to the Human AI Trainer Review Board for manual verification by a numismatic expert.\n\nContinue?',
          style: TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel', style: TextStyle(color: Colors.white54)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFF59E0B),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Submit'),
          ),
        ],
      ),
    );

    if (confirm != true) return;
    if (!mounted) return;

    try {
      await FirebaseFirestore.instance
          .collection('users')
          .doc(email)
          .collection('coins')
          .doc(_coin.id)
          .update({'grade_review_status': 'pending'});


      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅ Coin successfully submitted for manual verification!'),
          backgroundColor: Color(0xFF16A34A),
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('❌ Submission failed: $e'),
          backgroundColor: Colors.red[700],
        ),
      );
    }
  }

  Future<void> _updateCac(bool value) async {
    try {
      await FirebaseFirestore.instance
          .collection(AuthService.coinsPath)
          .doc(_coin.id)
          .update({'hasCac': value});
      
      // Trigger a refresh call on the backend in the background
      http.post(
        Uri.parse('$kApiBaseUrl/api/greysheet/refresh'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'user_id': AuthService.userEmail,
          'coin_id': _coin.id,
        }),
      );
      
      final updated = CoinModel.fromMap({
        ..._coin.toFirestore(),
        'hasCac': value,
        'timestamp': _coin.timestamp,
      }, _coin.id);
      if (!mounted) return;
      setState(() {
        _coin = updated;
      });
      widget.onEdited?.call();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to update CAC sticker status: $e'), backgroundColor: _kRed),
        );
      }
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // BUILD
  // ─────────────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _kBg,
      body: _inEditMode ? _buildEditForm() : _buildDetailView(),
    );
  }

  // ── Detail view ────────────────────────────────────────────────────────────
  Widget _buildDetailView() {
    return Column(
      children: [
        _HeroHeader(
          coin: _coin,
          isOnWishlist: _isOnWishlist,
          wishlistLoading: _wishlistLoading,
          onClose: () => Navigator.of(context).pop(),
          onWishlist: _toggleWishlist,
          onEdit: _enterEditMode,
          onVerifyManually: _verifyManually,
          onAiChat: () {
            Navigator.of(context).pop();
            final denom = _fmtDenomination(_coin.denomination);
            final coinId = [
              if (_coin.year.isNotEmpty) _coin.year.replaceAll(RegExp(r'\.0$'), ''),
              if (_coin.mintMark.isNotEmpty) '(${_coin.mintMark})',
              if (denom.isNotEmpty) denom,
              if (_coin.programSeries.isNotEmpty) _coin.programSeries,
              if (_coin.condition.isNotEmpty) _coin.condition,
            ].join(' ');
            widget.onNavigateToAiChat?.call(
              'Tell me about the $coinId. '
              'Please cover: history & background, obverse and reverse design, '
              'mintage figures, current market value, and collector tips.',
            );
          },
          onPcgs: _coin.certificationNumber.isNotEmpty
              ? () => launchUrl(Uri.parse(
                    'https://www.pcgs.com/cert/${_coin.certificationNumber.replaceAll(RegExp(r'[^0-9]'), '')}'),
                  mode: LaunchMode.externalApplication)
              : null,
          onDelete: _confirmDelete,
        ),
        // Tab bar
        Container(
          color: _kSurface,
          child: TabBar(
            controller: _tabCtrl,
            labelColor: _kAccent,
            unselectedLabelColor: _kSubtext,
            indicatorColor: _kAccent,
            indicatorWeight: 2.5,
            labelStyle: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
            tabs: const [
              Tab(text: 'Details'),
              Tab(text: 'Financials'),
              Tab(text: 'Provenance'),
              Tab(text: 'AI Insights'),
              Tab(text: 'History'),
              Tab(text: 'Known Errors'),
            ],
          ),
        ),
        // Tab content
        Expanded(
          child: TabBarView(
            controller: _tabCtrl,
            children: [
              _DetailsTab(
                coin: _coin,
                isInspectorMode: _isInspectorMode,
                onInspectField: _showDiscrepancyDialog,
              ),
              _FinancialsTab(coin: _coin, spotPrices: widget.spotPrices, onCacToggled: _updateCac),
              _ProvenanceTab(coin: _coin),
              _AiInsightsTab(
                loading: _aiLoading,
                loaded: _aiLoaded,
                insight: _aiInsight,
                error: _aiError,
                onRetry: _loadAiInsight,
                onOpenChat: () {
                  Navigator.of(context).pop();
                  widget.onNavigateToAiChat?.call(
                    'Tell me more about this coin: ${_coin.year} ${_coin.mintMark} '
                    '${_coin.denomination} — ${_coin.programSeries} ${_coin.themeSubject}',
                  );
                },
              ),
              _HistoryTab(coin: _coin),
              _KnownErrorsTab(coin: _coin),
            ],
          ),
        ),
      ],
    );
  }

  // ── Inline Edit form ───────────────────────────────────────────────────────
  Widget _buildEditForm() {
    return Column(
      children: [
        // Edit header
        Container(
          color: _kDark,
          padding: const EdgeInsets.fromLTRB(16, 12, 8, 12),
          child: Row(children: [
            const Icon(Icons.edit, color: _kBrand, size: 18),
            const SizedBox(width: 10),
            const Expanded(
              child: Text('Edit Coin', style: TextStyle(
                color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
            ),
            TextButton(
              onPressed: () => setState(() => _inEditMode = false),
              child: const Text('Cancel', style: TextStyle(color: Colors.white54)),
            ),
            const SizedBox(width: 8),
            ElevatedButton(
              onPressed: _saveEdits,
              style: ElevatedButton.styleFrom(
                backgroundColor: _kGreen, foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              ),
              child: const Text('Save'),
            ),
            const SizedBox(width: 8),
          ]),
        ),
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Wrap(
              spacing: 16,
              runSpacing: 16,
              children: _editCtrl.entries.map((e) => _EditField(
                label: e.key,
                controller: e.value,
                multiline: e.key == 'Personal Notes',
              )).toList(),
            ),
          ),
        ),
      ],
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// HERO HEADER
// ─────────────────────────────────────────────────────────────────────────────
class _HeroHeader extends StatelessWidget {
  final CoinModel coin;
  final bool isOnWishlist;
  final bool wishlistLoading;
  final VoidCallback onClose;
  final VoidCallback onWishlist;
  final VoidCallback onEdit;
  final VoidCallback onAiChat;
  final Future<void> Function()? onPcgs;
  final VoidCallback onDelete;
  final VoidCallback? onVerifyManually;

  const _HeroHeader({
    required this.coin,
    required this.isOnWishlist,
    required this.wishlistLoading,
    required this.onClose,
    required this.onWishlist,
    required this.onEdit,
    required this.onAiChat,
    this.onPcgs,
    required this.onDelete,
    this.onVerifyManually,
  });

  @override
  Widget build(BuildContext context) {
    final title = _buildTitle();
    final subtitle = _buildSubtitle();

    final isSetItem = coin.isSet || (coin.setId != null && coin.setId!.isNotEmpty);

    return Container(
      color: _kDark,
      padding: const EdgeInsets.fromLTRB(20, 14, 12, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Close + title row
          Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            // Coin images or Set icon
            if (isSetItem)
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  color: const Color(0xFF0F172A),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFFC9A227).withAlpha(80)),
                ),
                child: const Icon(Icons.folder_open, color: Color(0xFFC9A227), size: 48),
              )
            else
              _CoinImagePair(coin: coin),
            const SizedBox(width: 20),
            // Identity
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 4),
                  // Grade badge
                  if (coin.condition.isNotEmpty && coin.condition != 'Ungraded')
                    _GradeBadge(grade: coin.condition),
                  const SizedBox(height: 6),
                  Text(title,
                    style: const TextStyle(
                      color: Colors.white, fontSize: 18,
                      fontWeight: FontWeight.bold, height: 1.3),
                  ),
                  const SizedBox(height: 4),
                  Text(subtitle,
                    style: const TextStyle(color: Colors.white60, fontSize: 12)),
                ],
              ),
            ),
            // Close button
            IconButton(
              onPressed: onClose,
              icon: const Icon(Icons.close, color: Colors.white54, size: 20),
              tooltip: 'Close',
            ),
          ]),

          const SizedBox(height: 14),

          // Quick-action buttons
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(children: [
              _ActionBtn(
                icon: isOnWishlist ? Icons.favorite : Icons.favorite_outline,
                label: isOnWishlist ? 'Wishlisted' : 'Wishlist',
                color: isOnWishlist ? _kBrand : const Color(0xFFC9A227),
                onTap: wishlistLoading ? null : onWishlist,
                loading: wishlistLoading,
              ),
              const SizedBox(width: 8),
              _ActionBtn(
                icon: Icons.edit_outlined,
                label: 'Edit',
                color: const Color(0xFFC9A227),
                onTap: onEdit,
              ),
              const SizedBox(width: 8),
              _ActionBtn(
                icon: Icons.psychology_outlined,
                label: 'AI Chat',
                color: const Color(0xFFC9A227),
                onTap: onAiChat,
              ),
              if (onPcgs != null) ...[
                const SizedBox(width: 8),
                _ActionBtn(
                  icon: Icons.open_in_new,
                  label: 'PCGS',
                  color: const Color(0xFFC9A227),
                  onTap: onPcgs,
                ),
              ],
              if (onVerifyManually != null) ...[
                const SizedBox(width: 8),
                _ActionBtn(
                  icon: Icons.assignment_turned_in_outlined,
                  label: 'Verify Manually',
                  color: const Color(0xFFC9A227),
                  onTap: onVerifyManually,
                ),
              ],
              const SizedBox(width: 8),
              _ActionBtn(
                icon: Icons.delete_outline,
                label: 'Delete',
                color: const Color(0xFFDC3545),
                onTap: onDelete,
              ),
            ]),
          ),
        ],
      ),
    );
  }

  String _buildTitle() {
    final denom = _fmtDenomination(coin.denomination);
    final parts = <String>[
      if (coin.year.isNotEmpty) coin.year.replaceAll(RegExp(r'\.0$'), ''),
      if (coin.mintMark.isNotEmpty) '(${coin.mintMark})',
      if (denom.isNotEmpty) denom,
    ];
    final base = parts.join(' ');
    // Only show themeSubject if it adds new info (not a variant of programSeries)
    final theme = coin.themeSubject.trim();
    final series = coin.programSeries.trim().toLowerCase();
    final themeNorm = theme.toLowerCase();
    final isRedundant = series.isNotEmpty && themeNorm.contains(series.split(' ').first);
    if (theme.isNotEmpty && !isRedundant) return '$base — $theme';
    if (coin.programSeries.isNotEmpty) return '$base — ${coin.programSeries}';
    return base.isEmpty ? 'Coin' : base;
  }

  String _buildSubtitle() {
    final parts = <String>[
      if (coin.programSeries.isNotEmpty) coin.programSeries,
      if (coin.metalContent.isNotEmpty && coin.metalContent != 'Unknown')
        coin.metalContent,
      if (coin.country.isNotEmpty && coin.country != 'USA') coin.country,
      if (coin.strikeType.isNotEmpty) coin.strikeType,
    ];
    return parts.join(' · ');
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// COIN IMAGE PAIR
// ─────────────────────────────────────────────────────────────────────────────
// Tries personal photo first (image_url_obverse / image_url_reverse stored on
// the Firestore coin doc). If empty, falls back to CoinImageService which
// looks up a reference image from the coin_image_index collection.
class _CoinImagePair extends StatefulWidget {
  final CoinModel coin;
  const _CoinImagePair({required this.coin});

  @override
  State<_CoinImagePair> createState() => _CoinImagePairState();
}

class _CoinImagePairState extends State<_CoinImagePair> {
  String _obvUrl = '';
  String _revUrl = '';
  String? _attribution;
  bool _loadingRef = false;

  @override
  void initState() {
    super.initState();
    // gs:// URIs are not displayable by Image.network() — treat as empty
    // so CoinImageService can fill in a public HTTPS URL from coin_image_index.
    _obvUrl = _toHttpsUrl(widget.coin.imageUrlObverse);
    _revUrl = _toHttpsUrl(widget.coin.imageUrlReverse);
    // Fetch reference images for any side that doesn't have a personal photo
    if (_obvUrl.isEmpty || _revUrl.isEmpty) {
      _fetchReferenceImages();
    }
  }

  /// Returns the URL if it is a loadable HTTPS URL, otherwise empty string.
  static String _toHttpsUrl(String url) {
    if (url.isEmpty) return '';
    if (url.startsWith('gs://')) return '';  // GCS internal path — not displayable
    return url;
  }

  Future<void> _fetchReferenceImages() async {
    if (_loadingRef) return;
    setState(() => _loadingRef = true);
    try {
      final result = await CoinImageService.fetchReferenceImages(
        year:         widget.coin.year,
        mint:         widget.coin.mintMark.isEmpty ? null : widget.coin.mintMark,
        denomination: widget.coin.denomination.isEmpty ? null : widget.coin.denomination,
        series:       widget.coin.programSeries.isEmpty ? null : widget.coin.programSeries,
        subject:      widget.coin.themeSubject.isEmpty ? null : widget.coin.themeSubject,
      );
      if (mounted && result.hasAny) {
        setState(() {
          // Only fill in sides that don't already have a personal photo
          if (_obvUrl.isEmpty) _obvUrl = result.obverseUrl ?? '';
          if (_revUrl.isEmpty) _revUrl = result.reverseUrl ?? '';
          _attribution = result.attribution;
        });
      }
    } catch (_) {
      // Silent fail — image is non-critical
    } finally {
      if (mounted) setState(() => _loadingRef = false);
    }
  }

  void _reportImageError(BuildContext context, String side) {
    final commentCtrl = TextEditingController();
    final denom = widget.coin.denomination.toLowerCase();
    final series = widget.coin.programSeries.toLowerCase();
    final isCurrency = denom.contains('note') || denom.contains('bill') || denom.contains('certificate') || series.contains('note') || series.contains('currency');
    final isMedal = denom.contains('medal') || series.contains('medal');

    final String assetType = isCurrency ? 'Currency' : isMedal ? 'Medal' : 'Coin';

    final List<(String, String)> options = isCurrency
        ? [
            ('wrong_catalog_no', 'Wrong Friedberg/Catalog Number'),
            ('mismatched_denom_year', 'Mismatched Denomination/Series Year'),
            ('signature_discrepancy', 'Signature discrepancy'),
            ('swapped_sides', 'Swapped Obverse/Reverse'),
            ('other', 'Other'),
          ]
        : isMedal
            ? [
                ('mismatched_medal_design', 'Mismatched Medal design'),
                ('wrong_metal_composition', 'Wrong metal composition indicator'),
                ('other', 'Other'),
              ]
            : [
                ('mismatched_design', 'Mismatched Design'),
                ('wrong_mint_mark', 'Wrong Mint Mark position'),
                ('swapped_sides', 'Swapped Obverse/Reverse'),
                ('render_artifact', 'AI Render Artifact (garbled text, etc.)'),
                ('other', 'Other'),
              ];

    String selectedType = options.first.$1;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          title: Row(
            children: const [
              Icon(Icons.warning_amber_rounded, color: _kRed),
              SizedBox(width: 8),
              Text('Report Image Error'),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Reporting error on $side image for this $assetType.',
                  style: const TextStyle(fontSize: 13, color: _kSubtext)),
              const SizedBox(height: 16),
              const Text('What is wrong with this image?',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
              const SizedBox(height: 8),
              DropdownButtonFormField<String>(
                initialValue: selectedType,
                decoration: const InputDecoration(
                  border: OutlineInputBorder(),
                  isDense: true,
                  contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                ),
                items: options
                    .map((opt) => DropdownMenuItem(
                          value: opt.$1,
                          child: Text(opt.$2, style: const TextStyle(fontSize: 13)),
                        ))
                    .toList(),
                onChanged: (val) {
                  if (val != null) {
                    setDialogState(() {
                      selectedType = val;
                    });
                  }
                },
              ),
              const SizedBox(height: 16),
              TextField(
                controller: commentCtrl,
                maxLines: 3,
                decoration: const InputDecoration(
                  labelText: 'Optional comments / details',
                  border: OutlineInputBorder(),
                  isDense: true,
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: _kRed),
              onPressed: () async {
                final comment = commentCtrl.text.trim();
                final issueLabel = options.firstWhere((o) => o.$1 == selectedType).$2;

                await FirebaseFirestore.instance.collection('tester_image_reports').add({
                  'coin_id': widget.coin.id,
                  'user_email': AuthService.userEmail,
                  'image_side': side,
                  'issue_type': selectedType,
                  'user_comment': comment.isEmpty ? issueLabel : '$issueLabel: $comment',
                  'timestamp': FieldValue.serverTimestamp(),
                });

                await FirebaseFirestore.instance
                    .doc('${AuthService.coinsPath}/${widget.coin.id}')
                    .update({
                  'image_verification_status': 'flagged',
                  'image_verification_reason': 'Tester reported $side image: $issueLabel. $comment',
                });

                if (ctx.mounted) Navigator.pop(ctx);
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Thank you! Image flag logged successfully.'),
                      backgroundColor: _kRed,
                    ),
                  );
                }
              },
              child: const Text('Submit Flag', style: TextStyle(color: Colors.white)),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final showFlag = AuthService.isBetaTester;
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _CoinImageTile(
          url: _obvUrl,
          label: 'OBV',
          heroTag: 'coin_obv_${widget.coin.id}',
          isLoading: _loadingRef,
          attribution: _attribution,
          onFlag: showFlag ? () => _reportImageError(context, 'obverse') : null,
        ),
        const SizedBox(width: 8),
        _CoinImageTile(
          url: _revUrl,
          label: 'REV',
          heroTag: 'coin_rev_${widget.coin.id}',
          isLoading: _loadingRef,
          attribution: _attribution,
          onFlag: showFlag ? () => _reportImageError(context, 'reverse') : null,
        ),
      ],
    );
  }
}

class _CoinImageTile extends StatelessWidget {
  final String url;
  final String label;
  final String heroTag;
  final bool isLoading;
  final String? attribution;
  final VoidCallback? onFlag;
  const _CoinImageTile({
    required this.url,
    required this.label,
    required this.heroTag,
    this.isLoading = false,
    this.attribution,
    this.onFlag,
  });

  @override
  Widget build(BuildContext context) {
    const size = 120.0;
    return Stack(
      children: [
        GestureDetector(
          onTap: url.isNotEmpty ? () => _openZoom(context) : null,
          child: Hero(
            tag: heroTag,
            child: Container(
              width: size,
              height: size,
              decoration: BoxDecoration(
                color: const Color(0xFF0B1120), // Dark background canvas
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                  color: url.isNotEmpty ? const Color(0xFFC9A227).withAlpha(80) : Colors.white.withAlpha(30),
                  width: url.isNotEmpty ? 1.5 : 1.0,
                ),
                boxShadow: url.isNotEmpty
                    ? [
                        BoxShadow(
                          color: const Color(0xFFC9A227).withAlpha(50),
                          blurRadius: 14, // Subtle 12-16px blur radius glow
                          spreadRadius: 1,
                        )
                      ]
                    : null,
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(9),
                child: isLoading && url.isEmpty
                    ? _skeleton()
                    : url.isNotEmpty
                        ? Image.network(
                            url,
                            fit: BoxFit.contain, // BoxFit.contain to prevent clipping rim
                            errorBuilder: (ctx, err, st) => _placeholder(),
                            loadingBuilder: (ctx, child, progress) =>
                              progress == null ? child : _skeleton(),
                          )
                        : _placeholder(),
              ),
            ),
          ),
        ),
        if (onFlag != null && url.isNotEmpty)
          Positioned(
            bottom: 4,
            right: 4,
            child: GestureDetector(
              onTap: onFlag,
              child: Container(
                padding: const EdgeInsets.all(4),
                decoration: const BoxDecoration(
                  color: Colors.black54,
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.flag,
                  color: Color(0xFFDC3545),
                  size: 14,
                ),
              ),
            ),
          ),
      ],
    );
  }

  Widget _placeholder() => Center(
    child: Column(mainAxisSize: MainAxisSize.min, children: [
      Icon(Icons.monetization_on_outlined, size: 36, color: _kAccent.withAlpha(150)),
      const SizedBox(height: 4),
      Text(label, style: const TextStyle(color: Colors.white38, fontSize: 10)),
    ]),
  );

  Widget _skeleton() => Container(
    decoration: BoxDecoration(
      gradient: LinearGradient(
        colors: [Colors.white.withAlpha(8), Colors.white.withAlpha(20), Colors.white.withAlpha(8)],
        stops: const [0.0, 0.5, 1.0],
      ),
    ),
  );

  void _openZoom(BuildContext context) {
    Navigator.of(context).push(PageRouteBuilder(
      opaque: false,
      barrierColor: Colors.black87,
      barrierDismissible: true,
      pageBuilder: (ctx, anim, secondAnim) => GestureDetector(
        onTap: () => Navigator.of(context).pop(),
        child: Scaffold(
          backgroundColor: Colors.transparent,
          body: Center(
            child: Hero(
              tag: heroTag,
              child: InteractiveViewer(
                panEnabled: true,
                minScale: 0.5,
                maxScale: 5.0,
                child: Image.network(url, fit: BoxFit.contain),
              ),
            ),
          ),
        ),
      ),
    ));
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// GRADE BADGE
// ─────────────────────────────────────────────────────────────────────────────
class _GradeBadge extends StatelessWidget {
  final String grade;
  const _GradeBadge({required this.grade});

  @override
  Widget build(BuildContext context) {
    return GradeBadgeWidget(gradeCode: grade);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// ACTION BUTTON
// ─────────────────────────────────────────────────────────────────────────────
class _ActionBtn extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final dynamic onTap; // VoidCallback or Future Function()
  final bool loading;

  const _ActionBtn({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
    this.loading = false,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap == null ? null : () {
        final result = onTap();
        // Handle both sync and async taps
        if (result is Future) result.catchError((_) {});
      },
      borderRadius: BorderRadius.circular(8),
      hoverColor: color.withAlpha(25),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
        decoration: BoxDecoration(
          color: color.withAlpha(15),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withAlpha(60), width: 1.0),
        ),
        child: loading
            ? SizedBox(width: 14, height: 14,
                child: CircularProgressIndicator(strokeWidth: 2, color: color))
            : Row(mainAxisSize: MainAxisSize.min, children: [
                Icon(icon, size: 14, color: color),
                const SizedBox(width: 5),
                Text(label, style: TextStyle(color: color, fontSize: 12,
                    fontWeight: FontWeight.w600)),
              ]),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// DETAILS TAB
// ─────────────────────────────────────────────────────────────────────────────
class _DetailsTab extends StatelessWidget {
  final CoinModel coin;
  final bool isInspectorMode;
  final Function(String fieldName, String currentValue) onInspectField;

  const _DetailsTab({
    required this.coin,
    this.isInspectorMode = false,
    required this.onInspectField,
  });

  @override
  Widget build(BuildContext context) {
    final fields = <(String, String)>[
      ('Year', coin.year.replaceAll(RegExp(r'\.0$'), '')),
      ('Mint Mark', coin.mintMark),
      ('Denomination', _fmtDenomination(coin.denomination)),
      ('Program / Series', coin.programSeries),
      ('Theme / Subject', coin.themeSubject),
      ('Variety / Error', coin.variety),
      ('Condition', coin.condition),
      ('Strike Type', coin.strikeType),
      ('Holder Type', coin.holderType),
      ('Grading Service', coin.gradingService),
      ('Metal Content', coin.metalContent),
      ('Country', coin.country),
      ('Storage Location', coin.storageLocation),
      ('Quantity', coin.quantity == '1' || coin.quantity.isEmpty ? '' : coin.quantity),
    ].where((f) => f.$2.trim().isNotEmpty &&
        f.$2 != 'null' && f.$2 != 'N/A' && f.$2 != 'Ungraded').toList();

    if (fields.isEmpty) {
      return _emptyState('No details recorded yet.\nTap Edit to add information.');
    }

    final isSetItem = coin.isSet || (coin.setId != null && coin.setId!.isNotEmpty);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: fields.map((f) {
              final isAuditable = const ['Year', 'Mint Mark', 'Variety / Error', 'Denomination'].contains(f.$1);
              return _DetailTile(
                label: f.$1,
                value: f.$2,
                onInspect: (isInspectorMode && isAuditable)
                    ? () => onInspectField(f.$1, f.$2)
                    : null,
              );
            }).toList(),
          ),
          if (isSetItem) ...[
            const SizedBox(height: 24),
            const Divider(color: Colors.white12),
            const SizedBox(height: 16),
            if (coin.setContents != null && coin.setContents!.isNotEmpty)
              SetContentsPanel(data: coin.toFirestore())
            else if (coin.setId != null && coin.setId!.isNotEmpty)
              CoinSetViewer(setId: coin.setId!),
          ],
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// FINANCIALS TAB
// ─────────────────────────────────────────────────────────────────────────────
class _FinancialsTab extends StatelessWidget {
  final CoinModel coin;
  final Map<String, double> spotPrices;
  final Function(bool) onCacToggled;
  const _FinancialsTab({required this.coin, required this.spotPrices, required this.onCacToggled});

  @override
  Widget build(BuildContext context) {
    // ── Melt value: live-compute from spot prices when available ─────────────
    final liveMelt = spotPrices.isNotEmpty
        ? MeltValueService.compute(
            metalContent: coin.metalContent,
            denomination: coin.denomination,
            spotPrices: spotPrices,
          )
        : null;
    final meltVal = liveMelt != null
        ? '\$${liveMelt.toStringAsFixed(2)}'
        : (spotPrices.isNotEmpty
            ? 'N/A'           // spot prices loaded but no precious metal
            : coin.meltValue); // no spot prices yet — show stored value
    final meltDisplay = meltVal.isEmpty ? 'Pending' : meltVal;

    // ── Melt formula breakdown ──────────────────────────────────────────────
    // Build human-readable formula: "1 oz coin, 99.9% silver × $60.30/oz = $60.30"
    String meltFormula = '';
    if (liveMelt != null && spotPrices.isNotEmpty) {
      final mc    = coin.metalContent.trim().toLowerCase();
      final denom = coin.denomination.trim().toLowerCase();
      final ag    = spotPrices['Silver'] ?? 0;
      final au    = spotPrices['Gold']   ?? 0;

      if (mc.contains('silver (99') || mc.contains('silver (999') ||
          (mc.contains('silver') && RegExp(r'9[0-9]\.\d+%').hasMatch(mc))) {
        meltFormula = ag > 0
            ? '1 troy oz coin, 99.9% silver × (silver spot \$${ag.toStringAsFixed(2)}/oz) = \$${liveMelt.toStringAsFixed(2)}'
            : '';
      } else if (mc.startsWith('90% silver')) {
        final ozMap = {'dime': 0.07234, 'quarter': 0.18084, 'half': 0.36169, 'half dollar': 0.36169, 'dollar': 0.77344};
        double? oz;
        for (final e in ozMap.entries) { if (denom.contains(e.key)) { oz = e.value; break; } }
        if (oz != null && ag > 0) {
          meltFormula = '${oz.toStringAsFixed(5)} troy oz Ag (90% silver) × (silver spot \$${ag.toStringAsFixed(2)}/oz) = \$${liveMelt.toStringAsFixed(2)}';
        }
      } else if (mc.startsWith('40% silver')) {
        const oz = 0.14792;
        if (ag > 0) meltFormula = '${oz.toStringAsFixed(5)} troy oz Ag (40% silver) × (silver spot \$${ag.toStringAsFixed(2)}/oz) = \$${liveMelt.toStringAsFixed(2)}';
      } else if (mc.startsWith('35% silver')) {
        const oz = 0.05626;
        if (ag > 0) meltFormula = '${oz.toStringAsFixed(5)} troy oz Ag (35% silver) × (silver spot \$${ag.toStringAsFixed(2)}/oz) = \$${liveMelt.toStringAsFixed(2)}';
      } else if (mc.contains('gold')) {
        meltFormula = au > 0
            ? 'Gold content × (gold spot \$${au.toStringAsFixed(2)}/oz) = \$${liveMelt.toStringAsFixed(2)}'
            : '';
      }
    }

    // ── Spot prices: only show metals relevant to this coin ─────────────────
    // Silver coins → Silver only.  Gold coins → Gold only.  Others → all.
    final mc = coin.metalContent.trim().toLowerCase();
    final bool hasSilver = mc.contains('silver');
    final bool hasGold   = mc.contains('gold');
    final filteredSpot = Map<String, double>.fromEntries(
      spotPrices.entries.where((e) {
        final k = e.key.toLowerCase();
        if (hasSilver && !hasGold) return k == 'silver';
        if (hasGold && !hasSilver) return k == 'gold';
        return k == 'silver' || k == 'gold'; // mixed or unknown: silver + gold only
      }),
    );


    // ── EST. VALUE: same greysheet-first priority as the collection grid ─────
    // EST. VALUE: CPG Retail (collector/market price) first, then greysheet bid
    // (dealer wholesale floor), then raw AI Estimated Value string.
    // This matches what Greysheet.com labels as "CPG Value (Retail)".
    final gBid = coin.greysheetBid;
    final gCpg = coin.cpgRetail;
    final greysheetVal = gCpg > 0 ? gCpg : (gBid > 0 ? gBid : 0.0);
    final aiDisplay = greysheetVal > 0
        ? '\$${greysheetVal.toStringAsFixed(2)}'
        : (coin.aiEstimatedValue.isEmpty || coin.aiEstimatedValue == 'Pending'
            ? 'Pending'
            : coin.aiEstimatedValue);

    // Use the best numeric value for P&L calculation
    final purchaseAmt = _parseDollar(coin.purchaseCost);
    final estAmt      = greysheetVal > 0 ? greysheetVal : _parseAiValue(coin.aiEstimatedValue);
    final profit      = estAmt - purchaseAmt;
    final profitPct   = purchaseAmt > 0 ? (profit / purchaseAmt * 100) : null;
    final canCalcPL   = purchaseAmt > 0 && estAmt > 0;

    final costDisplay = (coin.purchaseCost.isEmpty || coin.purchaseCost == r'$0.00')
        ? 'UKN' : coin.purchaseCost;

    final plDolStr = canCalcPL
        ? '${profit >= 0 ? '+' : '-'}\$${profit.abs().toStringAsFixed(2)}' : '—';
    final plPctStr = (canCalcPL && profitPct != null)
        ? '${profitPct >= 0 ? '+' : ''}${profitPct.toStringAsFixed(1)}%' : '—';
    final plColor  = canCalcPL ? (profit >= 0 ? _kGreen : _kRed) : _kSubtext;

    Widget metricBox(String label, String value, Color valueColor) => Expanded(
      child: Semantics(
        label: '$label: $value',
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 10),
          decoration: BoxDecoration(
            color: _kSurface,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: _kBorder),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: const TextStyle(
                  fontSize: 12, color: _kSubtext, letterSpacing: 0.5)),
              const SizedBox(height: 4),
              Text(value, style: TextStyle(
                  fontSize: 15, fontWeight: FontWeight.w600, color: valueColor),
                maxLines: 1, overflow: TextOverflow.ellipsis),
            ],
          ),
        ),
      ),
    );

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Always-visible 4-metric summary ─────────────────────────────
          const Text('Financial Summary',
              style: TextStyle(
                  fontSize: 12,
                  color: _kSubtext,
                  letterSpacing: 0.8,
                  fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          Row(children: [
            metricBox('ACQUISITION COST', costDisplay, _kText),
            const SizedBox(width: 8),
            metricBox('EST. VALUE', aiDisplay,
                aiDisplay == 'Pending' ? _kSubtext : _kAccent),
          ]),
          const SizedBox(height: 6),
          // ── Greysheet CPG attribution (per §4.4 & §4.5 of API license) ──
          GestureDetector(
            onTap: () async {
              final uri = Uri.parse('https://www.greysheet.com');
              if (await canLaunchUrl(uri)) launchUrl(uri, mode: LaunchMode.externalApplication);
            },
            child: RichText(
              text: TextSpan(
                style: const TextStyle(fontSize: 10, color: _kSubtext),
                children: [
                  TextSpan(text: 'Coin, note & medal value estimate based on CPG data from '),
                  const TextSpan(
                    text: 'Greysheet',
                    style: TextStyle(
                      color: Color(0xFF60A5FA),
                      decoration: TextDecoration.underline,
                      decorationColor: Color(0xFF60A5FA),
                    ),
                  ),
                  if (coin.priceLastUpdated != null)
                    TextSpan(
                      text: ' (${_fmtPriceMonth(coin.priceLastUpdated!)})',
                    ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),
          Row(children: [
            metricBox('PROFIT / LOSS', plDolStr, plColor),
            const SizedBox(width: 8),
            metricBox('PROFIT / LOSS %', plPctStr, plColor),
          ]),
          const SizedBox(height: 16),

          // ── Detail tiles ─────────────────────────────────────────────────
          Wrap(spacing: 12, runSpacing: 12, children: [
            if (coin.purchaseDate.isNotEmpty)
              _DetailTile(label: 'Purchase Date',  value: coin.purchaseDate),
            if (coin.retailer.isNotEmpty)
              _DetailTile(label: 'Retailer',        value: coin.retailer),
            if (coin.retailerItemNo.isNotEmpty)
              _DetailTile(label: 'Item No.',        value: coin.retailerItemNo),
          if (coin.retailerInvoiceNo.isNotEmpty)
              _DetailTile(label: 'Invoice No.',     value: coin.retailerInvoiceNo),
          ]),

          // ── Melt Value card with formula ─────────────────────────────────
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            decoration: BoxDecoration(
              color: _kSurface,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: _kBorder),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Melt Value',
                  style: TextStyle(fontSize: 11, color: _kSubtext, letterSpacing: 0.4),
                ),
                const SizedBox(height: 4),
                Text(
                  meltDisplay,
                  style: const TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w700,
                    color: _kText,
                    letterSpacing: -0.5,
                  ),
                ),
                if (meltFormula.isNotEmpty) ...[
                  const SizedBox(height: 5),
                  Text(
                    '($meltFormula)',
                    style: TextStyle(
                      fontSize: 11,
                      color: _kSubtext,
                      height: 1.4,
                    ),
                  ),
                ],
              ],
            ),
          ),

          if (filteredSpot.isNotEmpty) ...[
            const SizedBox(height: 16),
            _SpotPriceRow(spotPrices: filteredSpot),
          ],
          
          if (coin.gradingService.isNotEmpty) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: _kSurface,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: _kBorder),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'CAC Verification Check',
                          style: TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Does this physical NGC/PCGS holder have a green or gold CAC sticker? (Adds a 20%-50%+ premium to market Bid/Retail values).',
                          style: TextStyle(
                            fontSize: 12,
                            color: _kSubtext,
                            height: 1.4,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 16),
                  Switch.adaptive(
                    value: coin.hasCac,
                    activeTrackColor: const Color(0xFF10B981).withValues(alpha: 0.5),
                    activeThumbColor: const Color(0xFF10B981),
                    onChanged: onCacToggled,
                  ),
                ],
              ),
            ),
          ],
          
          if (coin.greysheetGsid.isNotEmpty)
            _GreysheetPricingTable(
              gsid: coin.greysheetGsid,
              currentGrade: coin.condition,
              priceLastUpdated: coin.priceLastUpdated,
            ),
        ],
      ),
    );
  }

  double _parseDollar(String raw) {
    if (raw.isEmpty) return 0;
    return double.tryParse(raw.replaceAll(RegExp(r'[^\d.]'), '')) ?? 0;
  }

  double _parseAiValue(String raw) {
    if (raw.isEmpty || raw == 'Pending') return 0;
    // Normalise all dash variants and strip commas
    final norm = raw
        .replaceAll(',', '')
        .replaceAll('\u2013', '-')   // en-dash
        .replaceAll('\u2014', '-')   // em-dash
        .replaceAll('\u2012', '-');  // figure dash
    // Match any range: "$15-$25", "$15 - $25", "15-25", etc. allowing optional leading $ or non-digits on second part
    final rangeMatch = RegExp(r'(\d+\.?\d*)\s*-\s*[^0-9]*(\d+\.?\d*)').firstMatch(norm);
    if (rangeMatch != null) {
      final a = double.tryParse(rangeMatch.group(1)!) ?? 0.0;
      final b = double.tryParse(rangeMatch.group(2)!) ?? 0.0;
      final mid = (a + b) / 2;
      return mid > 100000 ? 0.0 : mid;   // sanity cap
    }
    final v = double.tryParse(norm.replaceAll(RegExp(r'[^\d.]'), '')) ?? 0.0;
    return v > 100000 ? 0.0 : v;          // sanity cap
  }
}


/// Formats a DateTime as "MMM yyyy" (e.g. "Jul 2026") for the Greysheet
/// CPG attribution line without requiring the intl package.
String _fmtPriceMonth(DateTime dt) {
  const months = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
  ];
  return '${months[dt.month - 1]} ${dt.year}';
}

class _GreysheetPricingTable extends StatefulWidget {
  final String gsid;
  final String currentGrade;
  final DateTime? priceLastUpdated;

  const _GreysheetPricingTable({
    required this.gsid,
    required this.currentGrade,
    this.priceLastUpdated,
  });

  @override
  State<_GreysheetPricingTable> createState() => _GreysheetPricingTableState();
}

class _GreysheetPricingTableState extends State<_GreysheetPricingTable> {
  bool _loading = true;
  List<dynamic> _pricing = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchPricing();
  }

  Future<void> _fetchPricing() async {
    try {
      final response = await http.get(Uri.parse('$kApiBaseUrl/api/greysheet/pricing/${widget.gsid}'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (mounted) {
          setState(() {
            _pricing = data['pricing'] ?? [];
            _loading = false;
          });
        }
      } else {
        if (mounted) {
          setState(() {
            _error = 'Failed to load pricing table';
            _loading = false;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.symmetric(vertical: 20),
          child: CircularProgressIndicator(),
        ),
      );
    }

    if (_error != null || _pricing.isEmpty) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 10),
        child: Text(
          'No Greysheet pricing table available.',
          style: TextStyle(fontSize: 12, color: _kSubtext, fontStyle: FontStyle.italic),
        ),
      );
    }

    // Parse numeric grade for comparison (e.g. "MS65" -> 65)
    final gradeReg = RegExp(r'\d+');
    final match = gradeReg.firstMatch(widget.currentGrade);
    final targetGradeNo = match != null ? int.tryParse(match.group(0)!) : null;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 24),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Greysheet Pricing Guide',
              style: TextStyle(
                fontSize: 12,
                color: _kSubtext,
                letterSpacing: 0.8,
                fontWeight: FontWeight.w600,
              ),
            ),
            Text(
              'GSID: #${widget.gsid}',
              style: const TextStyle(
                fontSize: 11,
                color: _kSubtext,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Container(
          width: double.infinity,
          decoration: BoxDecoration(
            color: _kSurface,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: _kBorder),
          ),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: DataTable(
              columnSpacing: 24,
              horizontalMargin: 12,
              headingRowHeight: 36,
              dataRowMinHeight: 32,
              dataRowMaxHeight: 36,
              columns: const [
                DataColumn(label: Text('Grade', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: _kText))),
                DataColumn(label: Text('Red Book (CPG® Retail)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: _kText))),
                DataColumn(label: Text('PCGS® Guide', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: _kText))),
                DataColumn(label: Text('NGC® Guide', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: _kText))),
                DataColumn(label: Text('Blue Book', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: _kText))),
              ],
              rows: _pricing.map<DataRow>((p) {
                final gradeLabel = p['GradeLabel'] ?? '—';
                final cpgVal = p['CpgVal'] ?? p['cpg_retail'] ?? '—';
                final pcgsVal = p['PcgsVal'] ?? p['pcgs_value'] ?? '—';
                final ngcVal = p['NgcVal'] ?? p['ngc_value'] ?? '—';
                final blueBookVal = p['BlueBookVal'] ?? p['blue_book_value'] ?? '—';
                final isCac = p['IsCac'] ?? p['cac_premium_flag'] ?? false;
                final gradeNo = p['Grade'] as int?;

                final isCurrent = gradeNo != null && gradeNo == targetGradeNo && !isCac;

                return DataRow(
                  selected: isCurrent,
                  color: WidgetStateProperty.resolveWith<Color?>((states) {
                    if (isCurrent) return _kAccent.withAlpha(20);
                    return null;
                  }),
                  cells: [
                    DataCell(Text(
                      '$gradeLabel${isCac ? " (CAC)" : ""}',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                        color: isCurrent ? _kAccent : _kText,
                      ),
                    )),
                    DataCell(Text(
                      cpgVal.toString().isEmpty || cpgVal.toString() == '0' ? '—' : '\$$cpgVal',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                        color: isCurrent ? _kAccent : _kText,
                      ),
                    )),
                    DataCell(Text(
                      pcgsVal.toString().isEmpty || pcgsVal.toString() == '0' ? '—' : '\$$pcgsVal',
                      style: TextStyle(
                        fontSize: 12,
                        color: _kText,
                      ),
                    )),
                    DataCell(Text(
                      ngcVal.toString().isEmpty || ngcVal.toString() == '0' ? '—' : '\$$ngcVal',
                      style: TextStyle(
                        fontSize: 12,
                        color: _kText,
                      ),
                    )),
                    DataCell(Text(
                      blueBookVal.toString().isEmpty || blueBookVal.toString() == '0' ? '—' : '\$$blueBookVal',
                      style: TextStyle(
                        fontSize: 12,
                        color: _kText,
                      ),
                    )),
                  ],
                );
              }).toList(),
            ),
          ),
        ),
        const SizedBox(height: 8),
        // ── Compliant Attribution Footnote (§4.4 / §4.5 of CDN API license) ──────
        GestureDetector(
          onTap: () async {
            final uri = Uri.parse('https://www.greysheet.com');
            if (await canLaunchUrl(uri)) launchUrl(uri, mode: LaunchMode.externalApplication);
          },
          child: RichText(
            text: TextSpan(
              style: const TextStyle(fontSize: 10, color: _kSubtext, fontStyle: FontStyle.italic),
              children: [
                const TextSpan(text: 'Coin, note & medal value estimates based on Red Book / CPG® Retail data from '),
                const TextSpan(
                  text: 'Greysheet.com',
                  style: TextStyle(
                    color: Color(0xFF60A5FA),
                    decoration: TextDecoration.underline,
                    decorationColor: Color(0xFF60A5FA),
                  ),
                ),
                if (widget.priceLastUpdated != null)
                  TextSpan(
                    text: ' (Refreshed ${_fmtPriceMonth(widget.priceLastUpdated!)})',
                  ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}


class _SpotPriceRow extends StatelessWidget {
  final Map<String, double> spotPrices;
  const _SpotPriceRow({required this.spotPrices});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: _kSurface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: _kBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Live Spot Prices', style: TextStyle(
            fontSize: 11, color: _kSubtext, fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          Wrap(spacing: 16, runSpacing: 6,
            children: spotPrices.entries.map((e) => Text(
              '${e.key}: \$${e.value.toStringAsFixed(2)}/oz',
              style: const TextStyle(fontSize: 12, color: _kText),
            )).toList(),
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// PROVENANCE TAB
// ─────────────────────────────────────────────────────────────────────────────
class _ProvenanceTab extends StatefulWidget {
  final CoinModel coin;
  const _ProvenanceTab({required this.coin});
  @override
  State<_ProvenanceTab> createState() => _ProvenanceTabState();
}

class _ProvenanceTabState extends State<_ProvenanceTab> {
  CoinModel? _freshCoin;

  @override
  void initState() {
    super.initState();
    _fetchFresh();
  }

  Future<void> _fetchFresh() async {
    try {
      final doc = await FirebaseFirestore.instance
          .collection(AuthService.coinsPath)
          .doc(widget.coin.id)
          .get(const GetOptions(source: Source.server)); // always from server
      if (mounted && doc.exists) {
        setState(() => _freshCoin = CoinModel.fromFirestore(doc));
      }
    } catch (_) {
      // fall through — use widget.coin as fallback
    }
  }

  @override
  Widget build(BuildContext context) {
    final coin = _freshCoin ?? widget.coin;
    final hasAcquisition = coin.retailer.isNotEmpty ||
        coin.retailerInvoiceNo.isNotEmpty ||
        coin.retailerItemNo.isNotEmpty ||
        coin.purchaseDate.isNotEmpty ||
        (coin.purchaseCost.isNotEmpty && coin.purchaseCost != r'$0.00');
    final hasCert = coin.certificationNumber.isNotEmpty ||
        coin.gradingService.isNotEmpty;
    final hasStorage = coin.storageLocation.isNotEmpty;
    final hasNotes = coin.personalNotes.isNotEmpty;
    final hasRef = coin.personalRef.isNotEmpty;
    final hasDesc = coin.originalDescription.isNotEmpty;
    // Show Record Source whenever source_file is non-empty (not just Binder Scan)
    final hasScanOrigin  = coin.source == 'Binder Scan' && coin.sourceFile.isNotEmpty;
    final hasImportSource = !hasScanOrigin && coin.sourceFile.isNotEmpty;
    final hasPaperTrail  = coin.receiptId.isNotEmpty;
    final hasAny = hasAcquisition || hasCert || hasStorage || hasNotes ||
        hasRef || hasDesc || hasScanOrigin || hasImportSource || hasPaperTrail;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [

          // ── Acquisition / Purchase Record ───────────────────────────────
          if (hasAcquisition) ...[
            _SectionHeader('Acquisition'),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: _kSurface,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: _kBorder),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  if (coin.retailer.isNotEmpty)
                    _ProvenanceRow(
                      icon: Icons.storefront_outlined,
                      label: 'Retailer',
                      value: coin.retailer,
                    ),
                  if (coin.purchaseDate.isNotEmpty)
                    _ProvenanceRow(
                      icon: Icons.calendar_today_outlined,
                      label: 'Purchase Date',
                      value: coin.purchaseDate,
                    ),
                  if (coin.purchaseCost.isNotEmpty && coin.purchaseCost != r'$0.00')
                    _ProvenanceRow(
                      icon: Icons.attach_money_outlined,
                      label: 'Purchase Cost',
                      value: coin.purchaseCost,
                    ),
                  if (coin.retailerInvoiceNo.isNotEmpty)
                    _ProvenanceRow(
                      icon: Icons.receipt_outlined,
                      label: 'Invoice No.',
                      value: coin.retailerInvoiceNo,
                    ),
                  if (coin.retailerItemNo.isNotEmpty)
                    _ProvenanceRow(
                      icon: Icons.tag_outlined,
                      label: 'Item No.',
                      value: coin.retailerItemNo,
                    ),
                ],
              ),
            ),
            const SizedBox(height: 16),
          ],

          // ── Certification ───────────────────────────────────────
          if (hasCert) ...[
            _SectionHeader('Certification'),
            const SizedBox(height: 8),
            _CertCard(coin: coin),
            const SizedBox(height: 16),
          ],

          // ── Storage ────────────────────────────────────────────
          if (hasStorage) ...[
            _SectionHeader('Storage'),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: _kSurface,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: _kBorder),
              ),
              child: _ProvenanceRow(
                icon: Icons.lock_outline,
                label: 'Location',
                value: coin.storageLocation,
              ),
            ),
            const SizedBox(height: 16),
          ],

          // ── Personal Notes ───────────────────────────────────
          if (hasNotes) ...[
            _SectionHeader('Personal Notes'),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: _kAccent.withAlpha(15),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: _kAccent.withAlpha(50)),
              ),
              child: GlossaryTooltipWrapper(
                text: coin.personalNotes,
                style: const TextStyle(fontSize: 13, color: _kText,
                    fontStyle: FontStyle.italic, height: 1.5),
              ),
            ),
            const SizedBox(height: 16),
          ],

          // ── Personal Reference ──────────────────────────────
          if (hasRef)
            Wrap(spacing: 12, runSpacing: 12, children: [
              _DetailTile(label: 'Personal Ref.', value: coin.personalRef),
            ]),

          // ── Original Seller Description ──────────────────────
          if (hasDesc) ...[
            const SizedBox(height: 16),
            _SectionHeader('Original Seller Description'),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: _kSurface,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: _kBorder),
              ),
              child: GlossaryTooltipWrapper(
                text: coin.originalDescription,
                style: const TextStyle(fontSize: 12, color: _kSubtext, height: 1.5),
              ),
            ),
          ],

          // ── Scan Origin (Binder Scan coins only) ─────────────────────────────
          if (hasScanOrigin) ...[
            const SizedBox(height: 16),
            _SectionHeader('Scan Origin'),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFF6366F1).withAlpha(12),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                    color: const Color(0xFF6366F1).withAlpha(50)),
              ),
              child: Column(children: [
                _ProvenanceRow(
                  icon: Icons.document_scanner_outlined,
                  label: 'Source',
                  value: coin.source,
                ),
                _ProvenanceRow(
                  icon: Icons.qr_code_outlined,
                  label: 'Scan ID',
                  value: coin.sourceFile.length > 16
                      ? '${coin.sourceFile.substring(0, 8)}…${coin.sourceFile.substring(coin.sourceFile.length - 4)}'
                      : coin.sourceFile,
                ),
                if (coin.binderDocId.isNotEmpty)
                  _ProvenanceRow(
                    icon: Icons.folder_outlined,
                    label: 'Binder Doc',
                    value: coin.binderDocId.length > 16
                        ? '${coin.binderDocId.substring(0, 8)}…${coin.binderDocId.substring(coin.binderDocId.length - 4)}'
                        : coin.binderDocId,
                  ),
              ]),
            ),
          ],

          // ── Import Source (PDF Invoice / Spreadsheet / Crosscheck) ───────────
          if (hasImportSource) ...[
            const SizedBox(height: 16),
            _SectionHeader('Record Source'),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFF6366F1).withAlpha(12),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFF6366F1).withAlpha(50)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                  _ProvenanceRow(
                    icon: Icons.insert_drive_file_outlined,
                    label: 'Source File',
                    // Show only the human-readable filename:
                    // 1. Strip GCS path prefix (everything up to last '/')
                    // 2. Strip UUID prefix if present (e.g. "uuid_Scan_..." → "Scan_...")
                    value: () {
                      final raw = coin.sourceFile;
                      final slash = raw.lastIndexOf('/');
                      String name = slash >= 0 ? raw.substring(slash + 1) : raw;
                      // Strip leading UUID pattern: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx_
                      final uuidRe = RegExp(
                          r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}_',
                          caseSensitive: false);
                      name = name.replaceFirst(uuidRe, '');
                      return name;
                    }(),
                  ),

                  if (coin.source.isNotEmpty)
                    _ProvenanceRow(
                      icon: Icons.input_outlined,
                      label: 'Import Type',
                      value: coin.source,
                    ),
                  if (coin.importBatch.isNotEmpty || coin.importSessionId.isNotEmpty)
                    _ProvenanceRow(
                      icon: Icons.tag_outlined,
                      label: 'Import Batch',
                      value: coin.importBatch.isNotEmpty
                          ? coin.importBatch
                          : coin.importSessionId,
                    ),
                ],
              ),
            ),
          ],

          // ── Paper Trail (Bulk Import / PDF Invoice) ──────────────────────────
          if (hasPaperTrail) ...[
            const SizedBox(height: 16),
            _SectionHeader('Paper Trail'),
            const SizedBox(height: 8),
            _PaperTrailCard(coin: coin),
          ],

          if (!hasAny)
            _emptyState(
              'No provenance information recorded yet.\n\n'
              'Add acquisition details via Edit — retailer, invoice number, '
              'purchase date and cost, storage location, and personal notes.'
            ),
        ],
      ),
    );
  }
}
// ─────────────────────────────────────────────────────────────────────────────
// PROVENANCE ROW HELPER
// ─────────────────────────────────────────────────────────────────────────────
class _ProvenanceRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  const _ProvenanceRow({required this.icon, required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Icon(icon, size: 15, color: _kAccent),
        const SizedBox(width: 8),
        SizedBox(
          width: 110,
          child: Text('$label:', style: const TextStyle(
            fontSize: 12, color: _kSubtext, fontWeight: FontWeight.w500)),
        ),
        Expanded(
          child: Text(value, style: const TextStyle(
            fontSize: 13, color: _kText, fontWeight: FontWeight.w600)),
        ),
      ]),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// CERT CARD
// ─────────────────────────────────────────────────────────────────────────────
class _CertCard extends StatelessWidget {
  final CoinModel coin;
  const _CertCard({required this.coin});

  @override
  Widget build(BuildContext context) {
    final certNum = coin.certificationNumber.replaceAll(RegExp(r'[^0-9]'), '');
    final pcgsUrl = certNum.isNotEmpty
        ? 'https://www.pcgs.com/cert/$certNum'
        : null;

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: _kSurface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: _kBorder),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        if (coin.gradingService.isNotEmpty)
          Row(children: [
            const Icon(Icons.verified_outlined, size: 16, color: _kAccent),
            const SizedBox(width: 6),
            Text(coin.gradingService,
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold, color: _kText)),
          ]),
        if (coin.certificationNumber.isNotEmpty) ...[
          const SizedBox(height: 6),
          Row(children: [
            Text('Cert #: ', style: const TextStyle(fontSize: 12, color: _kSubtext)),
            Text(coin.certificationNumber,
              style: const TextStyle(fontSize: 12, color: _kText, fontWeight: FontWeight.w600)),
            const Spacer(),
            if (pcgsUrl != null)
              GestureDetector(
                onTap: () => launchUrl(Uri.parse(pcgsUrl),
                    mode: LaunchMode.externalApplication),
                child: const Row(children: [
                  Text('Verify →', style: TextStyle(
                    fontSize: 11, color: _kAccent, fontWeight: FontWeight.w600)),
                  SizedBox(width: 2),
                  Icon(Icons.open_in_new, size: 12, color: _kAccent),
                ]),
              ),
          ]),
        ],
      ]),
    );
  }
}


// ─────────────────────────────────────────────────────────────────────────────
// PAPER TRAIL CARD
// ─────────────────────────────────────────────────────────────────────────────
class _PaperTrailCard extends StatefulWidget {
  final CoinModel coin;
  const _PaperTrailCard({required this.coin});
  @override
  State<_PaperTrailCard> createState() => _PaperTrailCardState();
}

class _PaperTrailCardState extends State<_PaperTrailCard> {
  bool _loading = false;
  String? _error;

  static const _kAmber = Color(0xFFF59E0B);
  static const _kAmberBg = Color(0xFFFFFBEB);
  static const _kAmberBorder = Color(0xFFFDE68A);

  Future<void> _viewOriginal() async {
    if (_loading) return;
    setState(() { _loading = true; _error = null; });

    try {
      final userEmail = AuthService.userEmail;
      final receiptId = widget.coin.receiptId;
      const apiBase = 'https://backend-studio-9101802118-8c9a8.a.run.app';
      final url = Uri.parse(
        '$apiBase/api/receipts/${Uri.encodeComponent(userEmail)}/$receiptId/view_url',
      );

      final resp = await http.get(url);
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as Map<String, dynamic>;
        final signedUrl = data['signed_url'] as String?;
        if (signedUrl != null && signedUrl.isNotEmpty) {
          await launchUrl(Uri.parse(signedUrl),
              mode: LaunchMode.externalApplication);
        } else {
          setState(() => _error = 'No URL returned from server.');
        }
      } else {
        setState(() => _error = 'Server error ${resp.statusCode}.');
      }
    } catch (e) {
      setState(() => _error = 'Could not open receipt: $e');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final shortId = widget.coin.receiptId.length > 16
        ? '${widget.coin.receiptId.substring(0, 8)}…'
        : widget.coin.receiptId;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: _kAmberBg,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: _kAmberBorder),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          const Icon(Icons.receipt_long_outlined, size: 16, color: _kAmber),
          const SizedBox(width: 8),
          Expanded(
            child: Text('Original Invoice on File',
              style: const TextStyle(
                fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF92400E))),
          ),
        ]),
        const SizedBox(height: 6),
        Text('Receipt ID: $shortId',
          style: const TextStyle(fontSize: 11, color: Color(0xFF78350F),
              fontFamily: 'monospace')),
        const SizedBox(height: 10),
        if (_error != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(_error!, style: const TextStyle(fontSize: 11, color: _kRed)),
          ),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: _loading ? null : _viewOriginal,
            icon: _loading
                ? const SizedBox(
                    width: 14, height: 14,
                    child: CircularProgressIndicator(strokeWidth: 2, color: _kAmber))
                : const Icon(Icons.open_in_new, size: 14, color: _kAmber),
            label: Text(_loading ? 'Opening…' : 'View Original Receipt',
              style: const TextStyle(fontSize: 12, color: _kAmber,
                  fontWeight: FontWeight.w600)),
            style: OutlinedButton.styleFrom(
              side: const BorderSide(color: _kAmber),
              padding: const EdgeInsets.symmetric(vertical: 8),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(6)),
            ),
          ),
        ),
      ]),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// AI INSIGHTS TAB
// ─────────────────────────────────────────────────────────────────────────────
class _AiInsightsTab extends StatelessWidget {
  final bool loading;
  final bool loaded;
  final String insight;
  final String? error;
  final VoidCallback onRetry;
  final VoidCallback onOpenChat;

  const _AiInsightsTab({
    required this.loading,
    required this.loaded,
    required this.insight,
    this.error,
    required this.onRetry,
    required this.onOpenChat,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [

          if (!loaded && !loading) ...[
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [_kAccent.withAlpha(25), _kBrand.withAlpha(15)],
                ),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: _kAccent.withAlpha(60)),
              ),
              child: Column(children: [
                const Icon(Icons.psychology_outlined, size: 40, color: _kAccent),
                const SizedBox(height: 10),
                const Text('AI Insights', style: TextStyle(
                  fontSize: 16, fontWeight: FontWeight.bold, color: _kText)),
                const SizedBox(height: 6),
                const Text(
                  'Get a Gemini-powered collector\'s analysis of this coin — '
                  'historical context, rarity, and what makes it special.',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 13, color: _kSubtext, height: 1.5),
                ),
                const SizedBox(height: 14),
                ElevatedButton.icon(
                  onPressed: onRetry,
                  icon: const Icon(Icons.auto_awesome, size: 16),
                  label: const Text('Generate Insight'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _kAccent,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                  ),
                ),
              ]),
            ),
          ],

          if (loading) ...[
            const SizedBox(height: 40),
            const Center(child: Column(children: [
              CircularProgressIndicator(color: _kAccent),
              SizedBox(height: 16),
              Text('Analysing this coin...', style: TextStyle(color: _kSubtext)),
            ])),
          ],

          if (loaded && insight.isNotEmpty) ...[
            if (error != null)
              Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: _kRed.withAlpha(20),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(error!, style: const TextStyle(fontSize: 11, color: _kRed)),
              ),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: _kSurface,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: _kBorder),
                boxShadow: [BoxShadow(
                  color: Colors.black.withAlpha(15), blurRadius: 8, offset: const Offset(0, 2)
                )],
              ),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Row(children: const [
                  Icon(Icons.auto_awesome, size: 14, color: _kAccent),
                  SizedBox(width: 6),
                  Text('Gemini 3.5 Flash • AI Numismatic Deepdive',
                    style: TextStyle(fontSize: 11, color: _kAccent, fontWeight: FontWeight.w600)),
                ]),
                const SizedBox(height: 12),
                // Render as markdown — gives bold headers, bullets, numbered lists
                MarkdownBody(
                  data: insight,
                  styleSheet: MarkdownStyleSheet(
                    p: const TextStyle(fontSize: 14, color: _kText, height: 1.7),
                    h1: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white, height: 2.0),
                    h2: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white, height: 2.0),
                    h3: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: _kText, height: 1.8),
                    strong: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
                    listBullet: const TextStyle(fontSize: 14, color: _kText, height: 1.7),
                    blockquoteDecoration: BoxDecoration(
                      color: _kAccent.withAlpha(20),
                      borderRadius: BorderRadius.circular(4),
                      border: Border(left: BorderSide(color: _kAccent, width: 3)),
                    ),
                    code: TextStyle(fontSize: 13, backgroundColor: _kBg, color: _kText),
                  ),
                  onTapLink: (text, href, title) {
                    if (href != null) {
                      launchUrl(Uri.parse(href), mode: LaunchMode.externalApplication);
                    }
                  },
                ),
              ]),
            ),
            const SizedBox(height: 16),
            Row(children: [
              OutlinedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh, size: 14),
                label: const Text('Regenerate'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: _kSubtext,
                  side: const BorderSide(color: _kBorder),
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                  textStyle: const TextStyle(fontSize: 12),
                ),
              ),
              const SizedBox(width: 10),
              ElevatedButton.icon(
                onPressed: onOpenChat,
                icon: const Icon(Icons.psychology_outlined, size: 14),
                label: const Text('Ask follow-up in AI Chat'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _kBrand,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                  textStyle: const TextStyle(fontSize: 12),
                ),
              ),
            ]),
          ],
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// HISTORY TAB — Founding Legislation via Congress.gov API
// ─────────────────────────────────────────────────────────────────────────────
class _HistoryTab extends StatefulWidget {
  final CoinModel coin;
  const _HistoryTab({required this.coin});

  @override
  State<_HistoryTab> createState() => _HistoryTabState();
}

class _HistoryTabState extends State<_HistoryTab> {
  Map<String, dynamic>? _laws;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _fetch();
  }

  Future<void> _fetch() async {
    try {
      final snap = await FirebaseFirestore.instance
          .collection('metadata')
          .doc('coin_legislation')
          .get();
      if (mounted) {
        setState(() {
          _laws = snap.data()?['laws'] as Map<String, dynamic>?;
          _loading = false;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _loading = false);
    }
  }

  /// Maps a coin's programSeries + denomination to a founding law key.
  /// Returns the key string (e.g. '105-124') or null if not matched.
  String? _matchLawKey() {
    final series = widget.coin.programSeries.toLowerCase();
    final denom  = widget.coin.denomination.toLowerCase();
    final theme  = widget.coin.themeSubject.toLowerCase();

    if (series.contains('state quarter') || series.contains('50 state') ||
        series.contains('statehood quarter')) {
      return '105-124';
    }
    if (series.contains('america') && series.contains('beautiful'))    return '110-456';
    if (series.contains('presidential dollar') || series.contains('president dollar')) {
      return '109-145';
    }
    if (series.contains('silver eagle') || series.contains('american silver eagle') ||
        series.contains('gold eagle')) {
      return '99-61';
    }
    if (series.contains('susan b') || series.contains('anthony'))      return '95-447';
    if (series.contains('eisenhower'))                                 return '91-607';
    if (series.contains('march of dimes') || theme.contains('march of dimes')) {
      return '112-209';
    }
    if (series.contains('sacagawea') || series.contains('native american dollar')) {
      return '106-445';
    }
    // Coinage Act 1965: affected all silver coins — halves, quarters, dimes
    if (denom.contains('half dollar') || denom.contains('quarter') ||
        denom.contains('dime')) {
      return '89-81';
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(40),
          child: CircularProgressIndicator(color: _kAccent),
        ),
      );
    }

    final lawKey = _matchLawKey();
    final law    = (lawKey != null && _laws != null) ? _laws![lawKey] as Map<String, dynamic>? : null;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Section header ──────────────────────────────────────────────
          Row(children: const [
            Icon(Icons.account_balance, size: 16, color: _kAccent),
            SizedBox(width: 8),
            Text('Founding Legislation',
                style: TextStyle(fontSize: 13, color: _kSubtext,
                    letterSpacing: 0.8, fontWeight: FontWeight.w600)),
          ]),
          const SizedBox(height: 12),

          if (law != null) ...[
            // ── Law card ──────────────────────────────────────────────────
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(18),
              decoration: BoxDecoration(
                color: _kSurface,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: _kBorder),
                boxShadow: [BoxShadow(
                  color: Colors.black.withAlpha(15),
                  blurRadius: 8, offset: const Offset(0, 2),
                )],
              ),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                // Public Law badge
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: _kAccent.withAlpha(22),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: _kAccent.withAlpha(60)),
                  ),
                  child: Text('Public Law ${law['public_law'] ?? lawKey}',
                      style: const TextStyle(fontSize: 11, color: _kAccent,
                          fontWeight: FontWeight.w700, letterSpacing: 0.4)),
                ),
                const SizedBox(height: 12),

                // Law title
                Text(law['name'] ?? '',
                    style: const TextStyle(fontSize: 16,
                        fontWeight: FontWeight.bold, color: _kText, height: 1.4)),
                const SizedBox(height: 12),

                // Metadata rows
                _HistoryRow(Icons.calendar_today_outlined, 'Enacted',
                    law['enacted'] ?? ''),
                _HistoryRow(Icons.forum_outlined, 'Congress',
                    law['congress'] ?? ''),
                _HistoryRow(Icons.gavel_outlined, 'Chamber',
                    law['chamber'] ?? 'Congress'),
                if ((law['actions_count'] ?? 0) > 0)
                  _HistoryRow(Icons.rule_outlined, 'Legislative Actions',
                      '${law['actions_count']} recorded actions'),

                // Congress.gov link button
                if ((law['congress_url'] ?? '').isNotEmpty) ...[
                  const SizedBox(height: 16),
                  OutlinedButton.icon(
                    onPressed: () => launchUrl(
                      Uri.parse(law['congress_url']),
                      mode: LaunchMode.externalApplication,
                    ),
                    icon: const Icon(Icons.open_in_new, size: 14),
                    label: const Text('View on Congress.gov'),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: _kAccent,
                      side: const BorderSide(color: _kAccent),
                      padding: const EdgeInsets.symmetric(
                          horizontal: 14, vertical: 8),
                      textStyle: const TextStyle(fontSize: 12,
                          fontWeight: FontWeight.w600),
                    ),
                  ),
                ],
              ]),
            ),
            const SizedBox(height: 16),

            // ── Context blurb ─────────────────────────────────────────────
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: _kAccent.withAlpha(10),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: _kAccent.withAlpha(30)),
              ),
              child: Row(crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                const Icon(Icons.info_outline, size: 16, color: _kAccent),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(law['description'] ?? '',
                      style: const TextStyle(fontSize: 13, color: _kSubtext,
                          height: 1.5)),
                ),
              ]),
            ),
          ] else ...[
            // ── No legislation found ──────────────────────────────────────
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: _kSurface,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: _kBorder),
              ),
              child: Column(children: [
                Icon(Icons.history_edu_outlined, size: 40,
                    color: _kSubtext.withAlpha(100)),
                const SizedBox(height: 12),
                const Text('No Legislation Matched',
                    style: TextStyle(fontSize: 15,
                        fontWeight: FontWeight.bold, color: _kText)),
                const SizedBox(height: 6),
                Text(
                  'Legislation data for "${widget.coin.programSeries.isEmpty ? widget.coin.denomination : widget.coin.programSeries}" '
                  'is not yet in our database.\n\n'
                  'The AI Insights tab can provide historical context about this coin.',
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 13, color: _kSubtext,
                      height: 1.5),
                ),
              ]),
            ),
          ],

          // ── Source credit ──────────────────────────────────────────────
          const SizedBox(height: 20),
          Row(mainAxisAlignment: MainAxisAlignment.center, children: const [
            Icon(Icons.verified_outlined, size: 11, color: _kSubtext),
            SizedBox(width: 4),
            Text('Legislation data via Congress.gov API',
                style: TextStyle(fontSize: 10, color: _kSubtext)),
          ]),
        ],
      ),
    );
  }
}

/// Single row in the History tab law card.
class _HistoryRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  const _HistoryRow(this.icon, this.label, this.value);

  @override
  Widget build(BuildContext context) {
    if (value.isEmpty) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Icon(icon, size: 14, color: _kSubtext),
        const SizedBox(width: 8),
        Text('$label: ', style: const TextStyle(
            fontSize: 13, color: _kSubtext, fontWeight: FontWeight.w500)),
        Expanded(
          child: Text(value,
              style: const TextStyle(fontSize: 13, color: _kText)),
        ),
      ]),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// SHARED SUB-WIDGETS
// ─────────────────────────────────────────────────────────────────────────────

class _DetailTile extends StatelessWidget {
  final String label;
  final String value;
  final VoidCallback? onInspect;
  const _DetailTile({required this.label, required this.value, this.onInspect});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 180,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: _kSurface,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: _kBorder),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(label, style: const TextStyle(fontSize: 10, color: _kSubtext,
                  fontWeight: FontWeight.w600, letterSpacing: 0.2)),
              if (onInspect != null)
                GestureDetector(
                  onTap: onInspect,
                  child: const Icon(Icons.comment_outlined, size: 12, color: _kAccent),
                ),
            ],
          ),
          const SizedBox(height: 4),
          GestureDetector(
            onLongPress: () => Clipboard.setData(ClipboardData(text: value)),
            child: Text(value,
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold,
                  color: _kText)),
          ),
        ]),
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String text;
  const _SectionHeader(this.text);

  @override
  Widget build(BuildContext context) => Text(text,
    style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold,
        color: _kSubtext, letterSpacing: 0.3));
}

class _EditField extends StatelessWidget {
  final String label;
  final TextEditingController controller;
  final bool multiline;
  const _EditField({required this.label, required this.controller, this.multiline = false});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: multiline ? double.infinity : 220,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(label, style: const TextStyle(fontSize: 11, color: _kSubtext,
            fontWeight: FontWeight.w600)),
        const SizedBox(height: 4),
        TextField(
          controller: controller,
          maxLines: multiline ? 4 : 1,
          style: const TextStyle(fontSize: 14, color: _kText),
          decoration: InputDecoration(
            filled: true,
            fillColor: _kSurface,
            contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: const BorderSide(color: _kBorder),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: const BorderSide(color: _kBorder),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(6),
              borderSide: const BorderSide(color: _kAccent, width: 2),
            ),
          ),
        ),
      ]),
    );
  }
}

Widget _emptyState(String message) => Center(
  child: Padding(
    padding: const EdgeInsets.all(40),
    child: Column(mainAxisSize: MainAxisSize.min, children: [
      Icon(Icons.info_outline, size: 36, color: _kSubtext.withAlpha(120)),
      const SizedBox(height: 12),
      Text(message,
        textAlign: TextAlign.center,
        style: const TextStyle(color: _kSubtext, fontSize: 14, height: 1.5)),
    ]),
  ),
);

// ─── Known Errors Tab ─────────────────────────────────────────────────────────
// Lazy-loads related mint errors from MintErrorService when the tab is first
// opened. Shows a scrollable list of matching errors with a link to the full
// Error Library detail screen.

class _KnownErrorsTab extends StatefulWidget {
  final CoinModel coin;
  const _KnownErrorsTab({required this.coin});

  @override
  State<_KnownErrorsTab> createState() => _KnownErrorsTabState();
}

class _KnownErrorsTabState extends State<_KnownErrorsTab>
    with AutomaticKeepAliveClientMixin {
  @override
  bool get wantKeepAlive => true;

  bool _loaded = false;
  bool _loading = false;
  List<MintError> _errors = [];

  @override
  void initState() {
    super.initState();
    _loadErrors();
  }

  Future<void> _loadErrors() async {
    if (_loading) return;
    setState(() {
      _loading = true;
      _loaded = false;
    });
    try {
      final denom = widget.coin.denomination.toLowerCase();
      final year = int.tryParse(widget.coin.year) ?? 0;
      final results = await MintErrorService.getErrorsForCoin(
        denomination: denom,
        year: year,
      ).timeout(
        const Duration(seconds: 6),
        onTimeout: () {
          // Timeout gracefully
          return [];
        },
      );
      if (mounted) {
        setState(() {
          _errors = results;
          _loaded = true;
          _loading = false;
        });
      }
    } catch (e) {
      // Log error silently or delegate to logger
      if (mounted) {
        setState(() {
          _errors = [];
          _loaded = true;
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);

    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_loaded && _errors.isEmpty) {
      return _emptyState(
        'No known errors on record for this coin.\n\n'
        'Check the Error Library for general error types\n'
        'or search by denomination.',
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header strip
        Container(
          padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
          child: Row(
            children: [
              const Icon(Icons.error_outline, size: 16, color: _kBrand),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  '${_errors.length} known error${_errors.length == 1 ? '' : 's'} for '
                  '${widget.coin.year} ${widget.coin.denomination}',
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: _kText,
                  ),
                ),
              ),
            ],
          ),
        ),
        const Divider(height: 1, color: _kBorder),
        Expanded(
          child: ListView.separated(
            padding: const EdgeInsets.all(12),
            itemCount: _errors.length,
            separatorBuilder: (_, _) => const SizedBox(height: 8),
            itemBuilder: (context, i) {
              final err = _errors[i];
              return GestureDetector(
                onTap: () => Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => MintErrorDetailScreen(error: err),
                  ),
                ),
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: _kSurface,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: _kBorder),
                  ),
                  child: Row(
                    children: [
                      // Category color bar
                      Container(
                        width: 4,
                        height: 48,
                        decoration: BoxDecoration(
                          color: _errorCategoryColor(err.category),
                          borderRadius: BorderRadius.circular(2),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              err.name,
                              style: const TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w700,
                                color: _kText,
                              ),
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 3),
                            Row(
                              children: [
                                _ErrorBadge(err.category, _errorCategoryColor(err.category)),
                                const SizedBox(width: 6),
                                _ErrorBadge(err.rarity, _errorRarityColor(err.rarity)),
                                const Spacer(),
                                Text(
                                  err.valueRange,
                                  style: const TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                    color: _kGold,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      const Icon(Icons.chevron_right, size: 18, color: _kSubtext),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}

// ─── Mini badge for Known Errors tab ─────────────────────────────────────────
class _ErrorBadge extends StatelessWidget {
  final String label;
  final Color color;
  const _ErrorBadge(this.label, this.color);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withAlpha(25),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withAlpha(70)),
      ),
      child: Text(
        label,
        style: TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: color),
      ),
    );
  }
}

Color _errorCategoryColor(String category) {
  switch (category) {
    case 'Doubled Die': return const Color(0xFFF63366);
    case 'Off-Metal':   return const Color(0xFFFF9500);
    case 'Planchet':    return const Color(0xFF34C759);
    case 'Striking':    return const Color(0xFF4C8CDA);
    case 'Die Variety': return const Color(0xFF9B59B6);
    case 'Overdate':    return const Color(0xFFFF6B35);
    case 'Missing Mintmark': return const Color(0xFFE74C3C);
    case 'Currency':    return const Color(0xFF2ECC71);
    default:            return const Color(0xFF5A5C69);
  }
}

Color _errorRarityColor(String rarity) {
  switch (rarity) {
    case 'Legendary': return const Color(0xFFFFD700);
    case 'Rare':      return const Color(0xFFF63366);
    case 'Uncommon':  return const Color(0xFF4C8CDA);
    default:          return const Color(0xFF5A5C69);
  }
}
