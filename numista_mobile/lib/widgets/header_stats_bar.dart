import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';
import '../services/melt_value_service.dart';
import '../services/batch_valuation_service.dart';

/// 4-Fact Responsive Header Stats Bar for Desktop Web
/// Displays:
/// 1. Count (with dynamic filter context)
/// 2. US Face Value (isolated from foreign currencies)
/// 3. Melt Value (live precious metals calculation)
/// 4. Valuation Block (completeness + Bid coverage + CPG coverage, never merged)
class HeaderStatsBar extends StatefulWidget {
  final List<QueryDocumentSnapshot> docs;
  final int totalCoinsCount;
  final Map<String, double> spotPrices;
  final BatchValuationProgress valuation;
  final VoidCallback onRunValuation;
  final bool isFiltered;

  const HeaderStatsBar({
    super.key,
    required this.docs,
    required this.totalCoinsCount,
    required this.spotPrices,
    required this.valuation,
    required this.onRunValuation,
    required this.isFiltered,
  });

  @override
  State<HeaderStatsBar> createState() => _HeaderStatsBarState();
}

class _HeaderStatsBarState extends State<HeaderStatsBar> {
  // Screen-only viewing preference for narrow screens (<1100px)
  bool _showWholesaleOnMobile = true;

  static const _kGold = Color(0xFFC9A227);
  static const _kTeal = Color(0xFF0D9488);
  static const _kSubtext = Color(0xFF8B92B4);

  bool _computeIsForeign(Map<String, dynamic> m) {
    if (m['is_foreign'] == false) return false;
    if (m['is_foreign'] == true) return true;

    final country = (m['country'] ?? m['Country'] ?? '').toString().toLowerCase().trim();
    const usAllowList = {'united states', 'us', 'usa', 'u.s.', 'u.s.a.', 'united states of america'};
    if (usAllowList.contains(country)) return false;

    return true;
  }

  double _parseNumber(dynamic val) {
    if (val == null) return 0.0;
    if (val is num) return val.toDouble();
    final s = val.toString().replaceAll(r'$', '').replaceAll(',', '').trim();
    return double.tryParse(s) ?? 0.0;
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardBg = isDark ? const Color(0xFF1E2937) : Colors.white;
    final borderCol = isDark ? const Color(0xFF2D3143) : const Color(0xFFE2E8F0);
    final textCol = isDark ? const Color(0xFFE8EAF0) : const Color(0xFF0F172A);

    // -- 1. Calculate Aggregations
    double wholesaleGuideSum = 0.0;
    int wholesaleGuideCount = 0;

    double retailGuideSum = 0.0;
    int retailGuideCount = 0;

    // Completeness: coins with ANY price estimate (AI Estimated Value, Bid, or CPG)
    int estimatedCount = 0;

    double usdFaceSum = 0.0;
    int worldTenderCount = 0;

    double meltTotal = 0.0;

    for (final doc in widget.docs) {
      final m = doc.data() as Map<String, dynamic>;
      final qtyRaw = _parseNumber(m['Quantity'] ?? m['qty']).toInt();
      final qty = qtyRaw > 0 ? qtyRaw : 1;

      // Wholesale (Greysheet Bid)
      final rawBid = m['greysheetBid'] ?? m['greysheet_bid'];
      final bidVal = _parseNumber(rawBid);
      if (rawBid != null) {
        wholesaleGuideSum += bidVal * qty;
        wholesaleGuideCount++;
      }

      // Retail (CPG)
      final rawCpg = m['cpgRetail'] ?? m['cpg_retail'];
      final cpgVal = _parseNumber(rawCpg);
      if (rawCpg != null) {
        retailGuideSum += cpgVal * qty;
        retailGuideCount++;
      }

      // Completeness: has ANY estimate
      final rawAi = m['AI Estimated Value'] ?? m['ai_estimated_value'];
      final aiVal = _parseNumber(rawAi);
      if (aiVal > 0 || bidVal > 0 || cpgVal > 0) {
        estimatedCount++;
      }

      // Face Value (Strictly US Legal Tender)
      final isForeign = _computeIsForeign(m);
      final denom = m['Denomination']?.toString() ?? m['denomination']?.toString() ?? '';
      if (!isForeign) {
        usdFaceSum += MeltValueService.parseFaceValue(denom, qty: qty);
      } else if (denom.isNotEmpty) {
        worldTenderCount++;
      }

      // Melt Value
      final liveMelt = widget.spotPrices.isNotEmpty
          ? (MeltValueService.compute(
                metalContent: m['Metal Content']?.toString() ?? m['metal_content']?.toString() ?? '',
                denomination: denom,
                spotPrices: widget.spotPrices,
                programSeries: m['Program/Series']?.toString() ?? m['program_series']?.toString() ?? '',
                themeSubject: m['Theme/Subject']?.toString() ?? m['theme_subject']?.toString() ?? '',
                qty: qty,
                coinData: m,
              ) ?? 0.0)
          : () {
              final meltRaw = m['Melt Value']?.toString() ?? m['melt_value']?.toString() ?? '';
              final match = RegExp(r'\d+\.?\d*').firstMatch(meltRaw.replaceAll(',', ''));
              return match != null ? ((double.tryParse(match.group(0)!) ?? 0.0) * qty) : 0.0;
            }();
      meltTotal += liveMelt;
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth > 1400;
        final isMedium = constraints.maxWidth > 1000 && !isWide;
        final isOffline = widget.spotPrices.isEmpty;

        // Fact 1: Count Chip
        final countChip = _buildStatChip(
          label: widget.isFiltered ? 'FILTERED COINS' : 'TOTAL COINS',
          value: widget.isFiltered
              ? '${widget.docs.length} of ${widget.totalCoinsCount}'
              : '${widget.docs.length} coins',
          subtext: widget.isFiltered ? 'for current filter settings' : null,
          cardBg: cardBg,
          borderCol: borderCol,
          textCol: textCol,
        );

        // Fact 2: USD Face Value Chip
        final faceChip = _buildStatChip(
          label: 'USD FACE VALUE',
          value: '\$${usdFaceSum.toStringAsFixed(2)}',
          badge: worldTenderCount > 0 ? '+$worldTenderCount World' : null,
          badgeTooltip: worldTenderCount > 0 ? '$worldTenderCount foreign coin(s) excluded from USD Face' : null,
          cardBg: cardBg,
          borderCol: borderCol,
          textCol: _kGold,
        );

        // Fact 3: Melt Value Chip
        final meltChip = _buildStatChip(
          label: 'MELT VALUE',
          value: isOffline
              ? '⚠️ \$${meltTotal.toStringAsFixed(2)} (offline)'
              : '🥈 \$${meltTotal.toStringAsFixed(2)}',
          cardBg: cardBg,
          borderCol: borderCol,
          textCol: _kGold,
        );

        // Fact 4: Valuation Block
        final valChip = _buildValuationBlock(
          wholesaleSum: wholesaleGuideSum,
          wholesaleCount: wholesaleGuideCount,
          retailSum: retailGuideSum,
          retailCount: retailGuideCount,
          estimatedCount: estimatedCount,
          totalDocs: widget.docs.length,
          cardBg: cardBg,
          borderCol: borderCol,
          textCol: textCol,
          isWide: isWide || isMedium,
        );

        final chips = [
          countChip,
          const SizedBox(width: 8),
          faceChip,
          const SizedBox(width: 8),
          meltChip,
          const SizedBox(width: 8),
          valChip,
        ];

        return SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          physics: const BouncingScrollPhysics(),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: chips,
          ),
        );
      },
    );
  }

  Widget _buildStatChip({
    required String label,
    required String value,
    String? subtext,
    String? badge,
    String? badgeTooltip,
    required Color cardBg,
    required Color borderCol,
    required Color textCol,
  }) {
    return Container(
      height: 48,
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: cardBg,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: borderCol),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontSize: 9,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 0.5,
                  color: _kSubtext,
                ),
              ),
              if (badge != null) ...[
                const SizedBox(width: 4),
                Tooltip(
                  message: badgeTooltip ?? badge,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                    decoration: BoxDecoration(
                      color: _kTeal.withAlpha(40),
                      borderRadius: BorderRadius.circular(3),
                    ),
                    child: Text(
                      badge,
                      style: const TextStyle(fontSize: 8, color: _kTeal, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              ],
            ],
          ),
          const SizedBox(height: 2),
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                value,
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: textCol,
                ),
              ),
              if (subtext != null) ...[
                const SizedBox(width: 4),
                Text(
                  subtext,
                  style: const TextStyle(fontSize: 8, color: _kSubtext, fontStyle: FontStyle.italic),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildValuationBlock({
    required double wholesaleSum,
    required int wholesaleCount,
    required double retailSum,
    required int retailCount,
    required int estimatedCount,
    required int totalDocs,
    required Color cardBg,
    required Color borderCol,
    required Color textCol,
    required bool isWide,
  }) {
    const disclaimer =
        'Numismatic estimates powered by CDN Greysheet Wholesale Bid & CPG Retail Price Guides. '
        'Bullion values calculated using live spot market feeds. '
        'CDN does not endorse this collection. For asset reference only; not a certified USPAP appraisal.';

    final v = widget.valuation;

    return Container(
      // Slightly taller on desktop to hold three rows cleanly without crowding
      height: isWide ? 56 : 48,
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: cardBg,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: borderCol),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (isWide) ...[
            // ── Desktop: three distinct labeled facts ─────────────────────────
            //   ESTIMATED  N/Total  — completeness (any AI/Bid/CPG value)
            //   BID GUIDE  N/Total  — Greysheet Wholesale Bid coverage
            //   CPG RETAIL N/Total  — CPG Retail guide coverage
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              mainAxisSize: MainAxisSize.min,
              children: [
                // Row A — Completeness
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text(
                      'ESTIMATED',
                      style: TextStyle(
                        fontSize: 8,
                        fontWeight: FontWeight.w700,
                        color: _kSubtext,
                        letterSpacing: 0.3,
                      ),
                    ),
                    const SizedBox(width: 5),
                    Text(
                      '$estimatedCount/$totalDocs',
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        color: _kTeal,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                // Row B — Greysheet Bid coverage
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text(
                      'BID GUIDE',
                      style: TextStyle(
                        fontSize: 8,
                        fontWeight: FontWeight.w700,
                        color: _kSubtext,
                        letterSpacing: 0.3,
                      ),
                    ),
                    const SizedBox(width: 5),
                    Text(
                      '$wholesaleCount/$totalDocs',
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        color: _kGold,
                      ),
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '(\$${wholesaleSum.toStringAsFixed(2)})',
                      style: const TextStyle(fontSize: 8, color: _kSubtext),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                // Row C — CPG Retail coverage
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text(
                      'CPG RETAIL',
                      style: TextStyle(
                        fontSize: 8,
                        fontWeight: FontWeight.w700,
                        color: _kSubtext,
                        letterSpacing: 0.3,
                      ),
                    ),
                    const SizedBox(width: 5),
                    Text(
                      '$retailCount/$totalDocs',
                      style: const TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF60A5FA),
                      ),
                    ),
                    const SizedBox(width: 4),
                    Text(
                      '(\$${retailSum.toStringAsFixed(2)})',
                      style: const TextStyle(fontSize: 8, color: _kSubtext),
                    ),
                  ],
                ),
              ],
            ),
          ] else ...[
            // ── Narrow / Mobile: segmented toggle (unchanged) ─────────────────
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    GestureDetector(
                      onTap: () => setState(() => _showWholesaleOnMobile = true),
                      child: Text(
                        'Wholesale (Bid)',
                        style: TextStyle(
                          fontSize: 9,
                          fontWeight: _showWholesaleOnMobile ? FontWeight.bold : FontWeight.normal,
                          color: _showWholesaleOnMobile ? _kGold : _kSubtext,
                          decoration: _showWholesaleOnMobile ? TextDecoration.underline : TextDecoration.none,
                        ),
                      ),
                    ),
                    const Text(' | ', style: TextStyle(fontSize: 9, color: _kSubtext)),
                    GestureDetector(
                      onTap: () => setState(() => _showWholesaleOnMobile = false),
                      child: Text(
                        'Retail (CPG)',
                        style: TextStyle(
                          fontSize: 9,
                          fontWeight: !_showWholesaleOnMobile ? FontWeight.bold : FontWeight.normal,
                          color: !_showWholesaleOnMobile ? const Color(0xFF60A5FA) : _kSubtext,
                          decoration: !_showWholesaleOnMobile ? TextDecoration.underline : TextDecoration.none,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 2),
                Text(
                  _showWholesaleOnMobile
                      ? '\$${wholesaleSum.toStringAsFixed(2)} ($wholesaleCount/$totalDocs)'
                      : '\$${retailSum.toStringAsFixed(2)} ($retailCount/$totalDocs)',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w700,
                    color: _showWholesaleOnMobile ? _kGold : const Color(0xFF60A5FA),
                  ),
                ),
              ],
            ),
          ],
          const SizedBox(width: 8),
          const Tooltip(
            message: disclaimer,
            child: Icon(Icons.info_outline, size: 14, color: _kSubtext),
          ),
          const SizedBox(width: 8),
          // In-Place Valuation Action / Progress
          if (v.isRunning)
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const SizedBox(
                  width: 12,
                  height: 12,
                  child: CircularProgressIndicator(strokeWidth: 2, color: _kTeal),
                ),
                const SizedBox(width: 4),
                Text(
                  '${v.completed}/${v.total}',
                  style: const TextStyle(fontSize: 9, color: _kTeal, fontWeight: FontWeight.bold),
                ),
              ],
            )
          else
            ElevatedButton(
              onPressed: widget.onRunValuation,
              style: ElevatedButton.styleFrom(
                backgroundColor: _kTeal,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 0),
                minimumSize: const Size(0, 22),
                tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
              ),
              child: const Text('Est.', style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold)),
            ),
        ],
      ),
    );
  }
}
