import 'package:flutter/material.dart';
import 'package:intl/intl.dart' as intl;
import 'package:numista_ai/constants/denomination_canon.dart';
import 'package:numista_ai/services/melt_value_service.dart';
import 'package:numista_ai/widgets/grade_badge_widget.dart';

/// Production valuation row extracted for testability and WCAG contrast compliance.
///
/// Implements B05N-8 valuation precedence and MF-C2'/MF-C3' requirements:
/// 1. CPG Retail override (`valCpg > 0`) -> Formatted currency (`$12.50`), no pending chip
///    (intentional B05N-8 change vs shipped `:3170`: verified CPG retail is authoritative
///    even when `enrichment_status == 'pending'`).
/// 2. AI Estimate (`data['AI Estimated Value'] ?? data['ai_estimated_value'] ?? data['ai_value'] ?? data['aiValue']`) ->
///    Filtered against sentinels (`Pending`, `null`, `—`, `none`, `nan`, empty).
///    Supports range strings (`12.00 - 15.00` -> `$12.00 - $15.00`) matching table column `:3345-3355`.
///    Shows `'Value pending AI estimate'` chip iff `enrichment_status == 'pending'`.
/// 3. Fallback -> Face value from denomination via `resolveFaceValue` + `MeltValueService.parseFaceValue`.
///    If `faceValue > 0` -> formatted face value with `'Value pending AI estimate'` chip.
///    If `faceValue <= 0` -> `'—'` with `'Value pending AI estimate'` chip (never `'$0.00'`).
///
/// WCAG Contrast across themes (MF-C6'):
/// - Dark Mode (v2.2): `#E0BC4A` against `#1E2937` (8.03:1) and `#0D1520` (10.01:1; also the opaque dark chip fill) -> PASSES AAA (>= 7.0:1).
/// - Light Mode: `#856404` against `#FFFFFF` (5.49:1), `#F5F5F0` (5.02:1), and light chip fill `#FFF3CD` (4.96:1) -> PASSES AA (>= 4.5:1).
class CollectionCardValuationRow extends StatelessWidget {
  final Map<String, dynamic> data;
  final String condition;

  const CollectionCardValuationRow({
    super.key,
    required this.data,
    this.condition = '',
  });

  static double _parseNumber(dynamic val) {
    if (val == null) return 0.0;
    if (val is num) return val.toDouble();
    final s = val.toString().trim();
    final m = RegExp(r'^\$?\s*(\d+(?:,\d{3})*(?:\.\d+)?)$').firstMatch(s);
    if (m == null) return 0.0;
    return double.tryParse(m.group(1)!.replaceAll(',', '')) ?? 0.0;
  }

  /// Reads AI value across the canonical Firestore key `'AI Estimated Value'` (`_F.aiValue` at `:72`)
  /// and snake_case / camelCase aliases, filtering out sentinel strings per `:3346`.
  static String? extractValidAiValue(Map<String, dynamic> data) {
    final raw = data['AI Estimated Value'] ??
        data['ai_estimated_value'] ??
        data['ai_value'] ??
        data['aiValue'];
    if (raw == null) return null;
    final trimmed = raw.toString().trim();
    if (trimmed.isEmpty) return null;
    final lower = trimmed.toLowerCase();
    if (lower == 'pending' ||
        lower == 'valuation pending' ||
        lower == 'null' ||
        lower == 'none' ||
        lower == 'nan' ||
        trimmed == '—' ||
        trimmed == '-') {
      return null;
    }
    return trimmed;
  }

  /// Exact US origin allowlist matching `my_collection_screen.dart` (`usAllowList`).
  static const Set<String> _usAllowList = {
    'united states', 'usa', 'us', 'united states of america', 'u.s.', 'u.s.a.',
    'united states mint', 'puerto rico', 'guam', 'u.s. virgin islands', 'usvi',
    'american samoa', 'northern mariana islands', 'confederate states', 'csa', 'us philippines',
  };

  static const Set<String> _usDenoms = {
    'quarter dollar', 'quarter', 'dime', 'half dime', 'five cents', 'nickel',
    'three cent nickel', 'three cent silver', 'three cents', 'two cents',
    'half cent', 'one cent', 'cent', 'penny', '1c', '1¢', '5c', '5¢',
    '10c', '10¢', '25c', '25¢', '50c', '50¢', 'lincoln cent',
    'jefferson nickel', 'half dollar', 'dollar',
    'five dollars (half eagle)', 'half eagle', 'eagle', 'double eagle',
  };

  /// Reuses the exact US origin discriminator from `my_collection_screen.dart` (`_F.country`, `is_foreign`).
  /// Returns `false` when `is_foreign == true` or when a non-empty `Country`/`country` is not in `_usAllowList`.
  static bool isUsOrigin(Map<String, dynamic> data) {
    if (data['is_foreign'] == true) return false;
    if (data['is_foreign'] == false) return true;
    final countryClean = (data['Country'] ?? data['country'] ?? '').toString().toLowerCase().trim();
    if (_usAllowList.contains(countryClean)) return true;
    if (countryClean.isEmpty || countryClean == 'none') {
      final denomClean = (data['Denomination'] ?? data['denomination'] ?? '').toString().toLowerCase().trim();
      if (denomClean.contains('centime') ||
          denomClean.contains('centavo') ||
          denomClean.contains('centesim') ||
          denomClean.contains('euro')) {
        return false;
      }
      final isUSDenom = _usDenoms.contains(denomClean) ||
          denomClean.contains('quarter') ||
          denomClean.contains('dime');
      return isUSDenom || denomClean.isEmpty;
    }
    return false;
  }

  /// Resolves face value in USD for canonical (`DenominationCanon`), colloquial,
  /// and historical US denominations (`Half Dime`, `Three Cent Nickel`).
  static double resolveFaceValue(String rawDenom) {
    final trimmed = rawDenom.trim();
    if (trimmed.isEmpty) return 0.0;

    // 1. Exact check against DenominationCanon constants
    switch (trimmed) {
      case DenominationCanon.cent:
        return 0.01;
      case DenominationCanon.fiveCents:
        return 0.05;
      case DenominationCanon.dime:
        return 0.10;
      case DenominationCanon.quarterDollar:
        return 0.25;
      case DenominationCanon.halfDollar:
        return 0.50;
      case DenominationCanon.dollar:
        return 1.00;
    }

    // 2. Delegate to MeltValueService.parseFaceValue (patched for multi-word order)
    return MeltValueService.parseFaceValue(trimmed, qty: 1);
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    // v2.2 MF-SAG-C3: dark text #E0BC4A (#D4AF37 was 6.9956:1 on #1E2937); dark chip fill opaque #0D1520 (:3031)
    final chipTextColor = isDark ? const Color(0xFFE0BC4A) : const Color(0xFF856404);
    final chipBgColor = isDark ? const Color(0xFF0D1520) : const Color(0xFFFFF3CD);
    final chipBorderColor = isDark ? const Color(0xFFD4AF37).withAlpha(120) : const Color(0xFFFFEEBA);

    final valCpg = _parseNumber(data['cpgRetail']);
    final validAiStr = extractValidAiValue(data);
    final enrichmentStatus = data['enrichment_status']?.toString().toLowerCase().trim() ?? '';
    final rawDenom = (data['Denomination'] ?? data['denomination'] ?? '').toString();

    final fmt = intl.NumberFormat.currency(symbol: '\$');

    String displayValue;
    bool showPendingChip = false;

    if (valCpg > 0) {
      // 1. CPG Retail override takes top precedence and suppresses pending chip
      displayValue = fmt.format(valCpg);
      showPendingChip = false;
    } else if (validAiStr != null) {
      // 2. Valid AI Estimate present (supports range strings per :3347-3355)
      final rangeMatch = RegExp(r'^\$?(\d+(?:\.\d+)?)\s*[-–]\s*\$?(\d+(?:\.\d+)?)$').firstMatch(validAiStr);
      if (rangeMatch != null) {
        final v1 = double.tryParse(rangeMatch.group(1)!);
        final v2 = double.tryParse(rangeMatch.group(2)!);
        if (v1 != null && v2 != null) {
          displayValue = '\$${v1.toStringAsFixed(2)} - \$${v2.toStringAsFixed(2)}';
        } else {
          displayValue = validAiStr;
        }
      } else {
        final parsedAi = _parseNumber(validAiStr);
        displayValue = parsedAi > 0
            ? fmt.format(parsedAi)
            : (validAiStr.startsWith('\$') ? validAiStr : '\$$validAiStr');
      }
      showPendingChip = (enrichmentStatus == 'pending');
    } else {
      // 3. Fallback to face value (US-scoped per MF-3; closing B05N-8 & MF-C3')
      final faceValue = isUsOrigin(data) ? resolveFaceValue(rawDenom) : 0.0;
      displayValue = faceValue > 0 ? fmt.format(faceValue) : '—';
      showPendingChip = true;
    }

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        if (showPendingChip)
          Flexible(
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  displayValue,
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                    color: chipTextColor,
                  ),
                ),
                const SizedBox(width: 6),
                Flexible(
                  child: Container(
                    key: const Key('valuation_pending_chip'), // v2.1 MF-SAG-C3
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: chipBgColor,
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(color: chipBorderColor),
                    ),
                    child: Text(
                      'Value pending AI estimate',
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: 10,
                        color: chipTextColor,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          )
        else
          Text(
            displayValue,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.bold,
              color: chipTextColor,
            ),
          ),
        if (condition.isNotEmpty)
          GradeBadgeWidget(gradeCode: condition),
      ],
    );
  }
}
