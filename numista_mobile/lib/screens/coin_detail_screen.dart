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
import '../services/auth_service.dart';
import '../services/melt_value_service.dart';
import '../services/wishlist_service.dart';

// ─── Design tokens (match app-wide palette) ────────────────────────────────────
const _kBg       = Color(0xFFF0F2F6);
const _kSurface  = Color(0xFFFFFFFF);
const _kDark     = Color(0xFF0E1117);
const _kText     = Color(0xFF31333F);
const _kSubtext  = Color(0xFF5A5C69);
const _kAccent   = Color(0xFF4C8CDA);
const _kBrand    = Color(0xFFF63366);
const _kGreen    = Color(0xFF28A745);
const _kRed      = Color(0xFFDC3545);
const _kGold     = Color(0xFFFFD700);
const _kBorder   = Color(0xFFE2E6E9);

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

  // Edit-mode controllers
  final Map<String, TextEditingController> _editCtrl = {};

  @override
  void initState() {
    super.initState();
    _coin = widget.coin;
    _tabCtrl = TabController(length: 4, vsync: this);
    _tabCtrl.addListener(() {
      if (_tabCtrl.index == 3 && !_aiLoaded && !_aiLoading) {
        _loadAiInsight();
      }
    });
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
            ],
          ),
        ),
        // Tab content
        Expanded(
          child: TabBarView(
            controller: _tabCtrl,
            children: [
              _DetailsTab(coin: _coin),
              _FinancialsTab(coin: _coin, spotPrices: widget.spotPrices),
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
  });

  @override
  Widget build(BuildContext context) {
    final title = _buildTitle();
    final subtitle = _buildSubtitle();

    return Container(
      color: _kDark,
      padding: const EdgeInsets.fromLTRB(20, 14, 12, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Close + title row
          Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
            // Coin images
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
                color: isOnWishlist ? _kBrand : Colors.white70,
                onTap: wishlistLoading ? null : onWishlist,
                loading: wishlistLoading,
              ),
              const SizedBox(width: 8),
              _ActionBtn(
                icon: Icons.edit_outlined,
                label: 'Edit',
                color: Colors.white70,
                onTap: onEdit,
              ),
              const SizedBox(width: 8),
              _ActionBtn(
                icon: Icons.psychology_outlined,
                label: 'AI Chat',
                color: Colors.white70,
                onTap: onAiChat,
              ),
              if (onPcgs != null) ...[
                const SizedBox(width: 8),
                _ActionBtn(
                  icon: Icons.open_in_new,
                  label: 'PCGS',
                  color: Colors.white70,
                  onTap: onPcgs,
                ),
              ],
              const SizedBox(width: 8),
              _ActionBtn(
                icon: Icons.delete_outline,
                label: 'Delete',
                color: _kRed.withAlpha(200),
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
class _CoinImagePair extends StatelessWidget {
  final CoinModel coin;
  const _CoinImagePair({required this.coin});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _CoinImageTile(
          url: coin.imageUrlObverse,
          label: 'OBV',
          heroTag: 'coin_obv_${coin.id}',
        ),
        const SizedBox(width: 8),
        _CoinImageTile(
          url: coin.imageUrlReverse,
          label: 'REV',
          heroTag: 'coin_rev_${coin.id}',
        ),
      ],
    );
  }
}

class _CoinImageTile extends StatelessWidget {
  final String url;
  final String label;
  final String heroTag;
  const _CoinImageTile({required this.url, required this.label, required this.heroTag});

  @override
  Widget build(BuildContext context) {
    const size = 120.0;
    return GestureDetector(
      onTap: url.isNotEmpty ? () => _openZoom(context) : null,
      child: Hero(
        tag: heroTag,
        child: Container(
          width: size,
          height: size,
          decoration: BoxDecoration(
            color: Colors.white.withAlpha(12),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: Colors.white.withAlpha(30), width: 1),
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(9),
            child: url.isNotEmpty
                ? Image.network(
                    url,
                    fit: BoxFit.cover,
                    errorBuilder: (ctx, err, st) => _placeholder(),
                    loadingBuilder: (ctx, child, progress) =>
                      progress == null ? child : _skeleton(),
                  )
                : _placeholder(),
          ),
        ),
      ),
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
    final colors = _gradeColors(grade);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
      decoration: BoxDecoration(
        color: colors.$1,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: colors.$1.withAlpha(200), width: 1),
      ),
      child: Text(
        grade.toUpperCase(),
        style: TextStyle(
          color: colors.$2,
          fontSize: 10,
          fontWeight: FontWeight.bold,
          letterSpacing: 0.8,
        ),
      ),
    );
  }

  (Color, Color) _gradeColors(String grade) {
    final g = grade.toUpperCase();
    if (RegExp(r'MS-7[0-9]|MS-6[5-9]').hasMatch(g)) return (_kGold, Colors.black87);
    if (RegExp(r'MS-6[0-4]').hasMatch(g)) return (const Color(0xFFDAA520), Colors.black87);
    if (g.contains('PROOF') || g.contains('PR-') || g.contains('PF-')) {
      return (const Color(0xFF7B68EE), Colors.white);
    }
    if (g.contains('AU')) return (const Color(0xFFB8860B), Colors.white);
    if (g.contains('EF') || g.contains('VF')) return (const Color(0xFF6C757D), Colors.white);
    if (g.contains('MS')) return (_kAccent, Colors.white);
    return (Colors.white.withAlpha(25), Colors.white70);
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
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
        decoration: BoxDecoration(
          color: Colors.white.withAlpha(14),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.white.withAlpha(25)),
        ),
        child: loading
            ? SizedBox(width: 14, height: 14,
                child: CircularProgressIndicator(strokeWidth: 2, color: color))
            : Row(mainAxisSize: MainAxisSize.min, children: [
                Icon(icon, size: 14, color: color),
                const SizedBox(width: 5),
                Text(label, style: TextStyle(color: color, fontSize: 12,
                    fontWeight: FontWeight.w500)),
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
  const _DetailsTab({required this.coin});

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

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Wrap(
        spacing: 12,
        runSpacing: 12,
        children: fields.map((f) => _DetailTile(label: f.$1, value: f.$2)).toList(),
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
  const _FinancialsTab({required this.coin, required this.spotPrices});

  @override
  Widget build(BuildContext context) {
    final meltVal = spotPrices.isNotEmpty
        ? MeltValueService.format(
            metalContent: coin.metalContent,
            denomination: coin.denomination,
            spotPrices: spotPrices,
          )
        : coin.meltValue;

    final purchaseAmt = _parseDollar(coin.purchaseCost);
    final aiAmt = _parseAiValue(coin.aiEstimatedValue);
    final profit = aiAmt - purchaseAmt;
    final profitPct = purchaseAmt > 0 ? (profit / purchaseAmt * 100) : null;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Profit / Loss card
          if (purchaseAmt > 0 && aiAmt > 0) ...[
            _ProfitLossCard(
              purchaseCost: purchaseAmt,
              aiValue: aiAmt,
              profit: profit,
              profitPct: profitPct,
            ),
            const SizedBox(height: 16),
          ],

          // Financial tiles
          Wrap(spacing: 12, runSpacing: 12, children: [
            if (coin.purchaseCost.isNotEmpty && coin.purchaseCost != r'$0.00')
              _DetailTile(label: 'Purchase Cost', value: coin.purchaseCost),
            if (coin.purchaseDate.isNotEmpty)
              _DetailTile(label: 'Purchase Date', value: coin.purchaseDate),
            if (coin.retailer.isNotEmpty)
              _DetailTile(label: 'Retailer', value: coin.retailer),
            if (coin.retailerItemNo.isNotEmpty)
              _DetailTile(label: 'Item No.', value: coin.retailerItemNo),
            if (coin.retailerInvoiceNo.isNotEmpty)
              _DetailTile(label: 'Invoice No.', value: coin.retailerInvoiceNo),
            if (coin.aiEstimatedValue.isNotEmpty && coin.aiEstimatedValue != 'Pending')
              _DetailTile(label: 'AI Est. Value', value: coin.aiEstimatedValue,
                accent: true),
            if (meltVal.isNotEmpty && meltVal != 'N/A')
              _DetailTile(label: 'Melt Value', value: meltVal),
          ]),

          if (spotPrices.isNotEmpty) ...[
            const SizedBox(height: 16),
            _SpotPriceRow(spotPrices: spotPrices),
          ],
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
    final clean = raw.replaceAll(',', '');
    if (clean.contains(' - ')) {
      final parts = clean.split(' - ');
      final a = double.tryParse(parts[0].replaceAll(RegExp(r'[^\d.]'), '')) ?? 0;
      final b = double.tryParse(parts[1].replaceAll(RegExp(r'[^\d.]'), '')) ?? 0;
      return (a + b) / 2;
    }
    return double.tryParse(clean.replaceAll(RegExp(r'[^\d.]'), '')) ?? 0;
  }
}

class _ProfitLossCard extends StatelessWidget {
  final double purchaseCost;
  final double aiValue;
  final double profit;
  final double? profitPct;

  const _ProfitLossCard({
    required this.purchaseCost,
    required this.aiValue,
    required this.profit,
    this.profitPct,
  });

  @override
  Widget build(BuildContext context) {
    final isGain = profit >= 0;
    final color = isGain ? _kGreen : _kRed;
    final sign = isGain ? '+' : '';
    String fmt(double v) => '\$${v.abs().toStringAsFixed(2)}';

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withAlpha(18),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withAlpha(60)),
      ),
      child: Row(children: [
        Icon(isGain ? Icons.trending_up : Icons.trending_down, color: color, size: 28),
        const SizedBox(width: 14),
        Expanded(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(isGain ? 'Unrealised Gain' : 'Unrealised Loss',
              style: const TextStyle(fontSize: 11, color: _kSubtext)),
            const SizedBox(height: 2),
            Text('$sign${fmt(profit)}',
              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: color)),
          ]),
        ),
        Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
          _FinRow('Paid', fmt(purchaseCost)),
          _FinRow('Est.', fmt(aiValue), bold: true),
          if (profitPct != null)
            _FinRow('%', '$sign${profitPct!.toStringAsFixed(1)}%', color: color),
        ]),
      ]),
    );
  }
}

class _FinRow extends StatelessWidget {
  final String label;
  final String value;
  final Color? color;
  final bool bold;
  const _FinRow(this.label, this.value, {this.color, this.bold = false});

  @override
  Widget build(BuildContext context) => Row(children: [
    Text('$label ', style: const TextStyle(fontSize: 11, color: _kSubtext)),
    Text(value, style: TextStyle(
      fontSize: 11, fontWeight: bold ? FontWeight.bold : FontWeight.normal,
      color: color ?? _kText)),
  ]);
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
class _ProvenanceTab extends StatelessWidget {
  final CoinModel coin;
  const _ProvenanceTab({required this.coin});

  @override
  Widget build(BuildContext context) {
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
    final hasScanOrigin  = coin.source == 'Binder Scan' && coin.sourceFile.isNotEmpty;
    final hasPaperTrail  = coin.receiptId.isNotEmpty;
    final hasAny = hasAcquisition || hasCert || hasStorage || hasNotes ||
        hasRef || hasDesc || hasScanOrigin || hasPaperTrail;

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
              child: Text(coin.personalNotes,
                style: const TextStyle(fontSize: 13, color: _kText,
                    fontStyle: FontStyle.italic, height: 1.5)),
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
              child: Text(coin.originalDescription,
                style: const TextStyle(fontSize: 12, color: _kSubtext, height: 1.5)),
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
                    h1: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: _kDark, height: 2.0),
                    h2: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: _kDark, height: 2.0),
                    h3: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: _kText, height: 1.8),
                    strong: const TextStyle(fontWeight: FontWeight.bold, color: _kDark),
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
// SHARED SUB-WIDGETS
// ─────────────────────────────────────────────────────────────────────────────

class _DetailTile extends StatelessWidget {
  final String label;
  final String value;
  final bool accent;
  const _DetailTile({required this.label, required this.value, this.accent = false});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 180,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: accent ? _kAccent.withAlpha(18) : _kSurface,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: accent ? _kAccent.withAlpha(80) : _kBorder),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label, style: const TextStyle(fontSize: 10, color: _kSubtext,
              fontWeight: FontWeight.w600, letterSpacing: 0.2)),
          const SizedBox(height: 4),
          GestureDetector(
            onLongPress: () => Clipboard.setData(ClipboardData(text: value)),
            child: Text(value,
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold,
                  color: accent ? _kAccent : _kText)),
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
