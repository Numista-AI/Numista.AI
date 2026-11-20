import 'dart:math' as math;
import '../constants/denomination_canon.dart';
import '../models/coin_model.dart';

/// Pre-aggregated, 60fps-ready record for a single vault lot/coin.
class AnalyticsCoinRecord {
  final CoinModel coin;
  final int qty;
  final double unitPrimary;
  final double totalPrimary;
  final double unitNetLiq;
  final double totalNetLiq;
  final double unitMelt;
  final double totalMelt;
  final double unitCost;
  final double totalCost;
  final bool hasPrice;
  final bool hasCost;
  final double fineAuOz;
  final double fineAgOz;
  final double finePtOz;
  final double finePdOz;
  final String canonicalDenom;
  final String normalizedGrading;
  final String normalizedMetal;

  const AnalyticsCoinRecord({
    required this.coin,
    required this.qty,
    required this.unitPrimary,
    required this.totalPrimary,
    required this.unitNetLiq,
    required this.totalNetLiq,
    required this.unitMelt,
    required this.totalMelt,
    required this.unitCost,
    required this.totalCost,
    required this.hasPrice,
    required this.hasCost,
    required this.fineAuOz,
    required this.fineAgOz,
    required this.finePtOz,
    required this.finePdOz,
    required this.canonicalDenom,
    required this.normalizedGrading,
    required this.normalizedMetal,
  });
}

class SpotSimulationResult {
  final double baselineTotal;
  final double simulatedTotal;
  final double deltaDollars;
  final double deltaPct;
  final double bullionPortion;
  final double numismaticPremium;
  final double totalFineAuOz;
  final double totalFineAgOz;
  final double totalFinePtOz;
  final double totalFinePdOz;
  final double? silverBreakevenPrice;

  const SpotSimulationResult({
    required this.baselineTotal,
    required this.simulatedTotal,
    required this.deltaDollars,
    required this.deltaPct,
    required this.bullionPortion,
    required this.numismaticPremium,
    required this.totalFineAuOz,
    required this.totalFineAgOz,
    required this.totalFinePtOz,
    required this.totalFinePdOz,
    this.silverBreakevenPrice,
  });
}

class DuplicateGroup {
  final String key;
  final String label;
  final int looseCount;
  final int setCount;
  final double recoverableValue;
  final List<String> coinIds;

  const DuplicateGroup({
    required this.key,
    required this.label,
    required this.looseCount,
    required this.setCount,
    required this.recoverableValue,
    required this.coinIds,
  });
}

class AnalyticsSummary {
  final List<AnalyticsCoinRecord> records;
  final int totalCoins;
  final int pricedCount;
  final int costBasisCount;
  final double totalPrimaryValue;
  final double totalNetLiquidation;
  final double totalMeltValue;
  final double totalCostBasis;
  final double totalFineAuOz;
  final double totalFineAgOz;
  final double totalFinePtOz;
  final double totalFinePdOz;
  final List<DuplicateGroup> duplicateGroups;
  final double totalDuplicateRecoverable;

  const AnalyticsSummary({
    required this.records,
    required this.totalCoins,
    required this.pricedCount,
    required this.costBasisCount,
    required this.totalPrimaryValue,
    required this.totalNetLiquidation,
    required this.totalMeltValue,
    required this.totalCostBasis,
    required this.totalFineAuOz,
    required this.totalFineAgOz,
    required this.totalFinePtOz,
    required this.totalFinePdOz,
    required this.duplicateGroups,
    required this.totalDuplicateRecoverable,
  });

  double get unrealizedGainDollars => totalPrimaryValue - totalCostBasis;
  double get unrealizedGainPct =>
      totalCostBasis > 0 ? (unrealizedGainDollars / totalCostBasis) * 100.0 : 0.0;
}

class AnalyticsCalculator {
  static const double defaultLiquidationFeePct = 0.13;

  static final RegExp _platedOrBaseRegex = RegExp(
    r'(plated|clad|nickel\s*silver|copper[-\s]?nickel|cupro[-\s]?nickel|brass|bronze|zinc|steel|aluminum)',
    caseSensitive: false,
  );

  static const Map<String, double> _ag90Oz = {
    'half dime': 0.03617,
    'dime': 0.07234,
    'quarter dollar': 0.18084,
    'half dollar': 0.36169,
    'dollar': 0.77344,
  };

  /// Parses aiEstimatedValue while rejecting <= 0.0 zero sentinels ('$0.00', '0', 'Pending').
  static double parseAiValue(String raw) {
    final trimmed = raw.trim();
    if (trimmed.isEmpty ||
        trimmed.toLowerCase() == 'pending' ||
        trimmed.toLowerCase() == 'n/a' ||
        trimmed.toLowerCase() == 'null') {
      return 0.0;
    }
    final norm = trimmed
        .replaceAll(',', '')
        .replaceAll('\u2013', '-')
        .replaceAll('\u2014', '-')
        .replaceAll('\u2012', '-');
    final rangeMatch =
        RegExp(r'(\d+\.?\d*)\s*-\s*[^0-9]*(\d+\.?\d*)').firstMatch(norm);
    double v = 0.0;
    if (rangeMatch != null) {
      v = double.tryParse(rangeMatch.group(1)!) ?? 0.0;
    } else {
      v = double.tryParse(norm.replaceAll(RegExp(r'[^\d.]'), '')) ?? 0.0;
    }
    if (v <= 0.0 || v > 100000.0 || !v.isFinite) return 0.0;
    return v;
  }

  static double parseMoney(String raw) {
    final cleaned = raw.replaceAll(',', '').replaceAll(RegExp(r'[^\d.]'), '');
    final v = double.tryParse(cleaned) ?? 0.0;
    return (v > 0.0 && v.isFinite) ? v : 0.0;
  }

  static ({double au, double ag, double pt, double pd}) inferFineOz(
      CoinModel coin, String canonicalDenom) {
    final metal = coin.metalContent.trim();
    if (_platedOrBaseRegex.hasMatch(metal)) {
      return (au: 0.0, ag: 0.0, pt: 0.0, pd: 0.0);
    }

    final ml = metal.toLowerCase();
    final denomLower = canonicalDenom.toLowerCase();
    final seriesLower = coin.programSeries.toLowerCase();

    if (ml.contains('999') ||
        ml.contains('fine silver') ||
        seriesLower.contains('silver eagle')) {
      if (ml.contains('silver') || seriesLower.contains('silver eagle')) {
        return (au: 0.0, ag: 1.0, pt: 0.0, pd: 0.0);
      }
    }
    if (ml.contains('90%') ||
        (ml.contains('silver') && _ag90Oz.containsKey(denomLower))) {
      return (au: 0.0, ag: _ag90Oz[denomLower] ?? 0.0, pt: 0.0, pd: 0.0);
    }
    if (ml.contains('gold') ||
        seriesLower.contains('gold eagle') ||
        seriesLower.contains('buffalo')) {
      if (ml.contains('1 oz') || denomLower.contains('50')) {
        return (au: 1.0, ag: 0.0, pt: 0.0, pd: 0.0);
      }
      if (ml.contains('1/2') || denomLower.contains('25')) {
        return (au: 0.5, ag: 0.0, pt: 0.0, pd: 0.0);
      }
      if (ml.contains('1/4') || denomLower.contains('10')) {
        return (au: 0.25, ag: 0.0, pt: 0.0, pd: 0.0);
      }
      if (ml.contains('1/10') || denomLower.contains('5')) {
        return (au: 0.1, ag: 0.0, pt: 0.0, pd: 0.0);
      }
    }
    return (au: 0.0, ag: 0.0, pt: 0.0, pd: 0.0);
  }

  /// Pre-aggregates all coins once on page load for 0ms 60fps slider drags.
  static AnalyticsSummary buildSummary(
    List<CoinModel> coins, {
    required bool advancedMode,
    double feePct = defaultLiquidationFeePct,
  }) {
    final parentIdsWithChildren = coins
        .where((c) => (c.parentSetId ?? '').trim().isNotEmpty)
        .map((c) => c.parentSetId!.trim())
        .toSet();

    final records = <AnalyticsCoinRecord>[];
    int totalCoins = 0;
    int pricedCount = 0;
    int costBasisCount = 0;
    double totalPrimary = 0.0;
    double totalNetLiq = 0.0;
    double totalMelt = 0.0;
    double totalCost = 0.0;
    double fineAu = 0.0;
    double fineAg = 0.0;
    double finePt = 0.0;
    double finePd = 0.0;

    for (final c in coins) {
      // Anti-double-count guard: skip parent set if its child coins are present
      if (c.isSet && parentIdsWithChildren.contains(c.id)) {
        continue;
      }

      final qty = c.isSet ? 1 : math.max(1, int.tryParse(c.quantity.trim()) ?? 1);
      final aiVal = parseAiValue(c.aiEstimatedValue);

      final double unitPrimary;
      if (advancedMode) {
        unitPrimary = c.cpgRetail > 0
            ? c.cpgRetail
            : (c.pcgsValue > 0
                ? c.pcgsValue
                : (c.ngcValue > 0 ? c.ngcValue : aiVal));
      } else {
        unitPrimary = c.greysheetBid > 0
            ? c.greysheetBid
            : (c.blueBookValue > 0
                ? c.blueBookValue
                : (aiVal > 0 ? aiVal : c.cpgRetail));
      }

      final canonicalDenom = DenominationCanon.normalize(c.denomination);
      final oz = inferFineOz(c, canonicalDenom);
      final hasFineOz = (oz.au + oz.ag + oz.pt + oz.pd) > 0.0;
      final unitMelt = parseMoney(c.meltValue);

      double unitNetLiq = c.greysheetBid > 0
          ? c.greysheetBid
          : (unitPrimary > 0 ? unitPrimary * (1.0 - feePct) : 0.0);
      if (hasFineOz && unitMelt > 0) {
        unitNetLiq = math.max(unitNetLiq, 0.95 * unitMelt);
      }

      final unitCost = parseMoney(c.purchaseCost);
      final hasPrice = unitPrimary > 0.0;
      final hasCost = unitCost > 0.0;

      final r = AnalyticsCoinRecord(
        coin: c,
        qty: qty,
        unitPrimary: unitPrimary,
        totalPrimary: unitPrimary * qty,
        unitNetLiq: unitNetLiq,
        totalNetLiq: unitNetLiq * qty,
        unitMelt: unitMelt,
        totalMelt: unitMelt * qty,
        unitCost: unitCost,
        totalCost: unitCost * qty,
        hasPrice: hasPrice,
        hasCost: hasCost,
        fineAuOz: oz.au * qty,
        fineAgOz: oz.ag * qty,
        finePtOz: oz.pt * qty,
        finePdOz: oz.pd * qty,
        canonicalDenom: canonicalDenom.isEmpty ? 'Other' : canonicalDenom,
        normalizedGrading:
            c.gradingService.trim().isEmpty ? 'Raw' : c.gradingService.trim(),
        normalizedMetal:
            c.metalContent.trim().isEmpty ? 'Unknown' : c.metalContent.trim(),
      );

      records.add(r);
      totalCoins += qty;
      if (hasPrice) pricedCount += qty;
      if (hasCost) {
        costBasisCount += qty;
        totalCost += r.totalCost;
      }
      totalPrimary += r.totalPrimary;
      totalNetLiq += r.totalNetLiq;
      totalMelt += r.totalMelt;
      fineAu += r.fineAuOz;
      fineAg += r.fineAgOz;
      finePt += r.finePtOz;
      finePd += r.finePdOz;
    }

    final dups = computeDuplicates(records);
    final totalRecoverable =
        dups.fold<double>(0.0, (sum, g) => sum + g.recoverableValue);

    return AnalyticsSummary(
      records: records,
      totalCoins: totalCoins,
      pricedCount: pricedCount,
      costBasisCount: costBasisCount,
      totalPrimaryValue: totalPrimary,
      totalNetLiquidation: totalNetLiq,
      totalMeltValue: totalMelt,
      totalCostBasis: totalCost,
      totalFineAuOz: fineAu,
      totalFineAgOz: fineAg,
      totalFinePtOz: finePt,
      totalFinePdOz: finePd,
      duplicateGroups: dups,
      totalDuplicateRecoverable: totalRecoverable,
    );
  }

  /// O(N) spot simulation executed on every slider drag.
  static SpotSimulationResult simulateSpot(
    AnalyticsSummary summary, {
    required double simGold,
    required double simSilver,
    double simPlatinum = 960.0,
    double simPalladium = 1020.0,
  }) {
    double simTotal = 0.0;
    double bullionPortion = 0.0;
    double numismaticPremium = 0.0;

    for (final r in summary.records) {
      final simMelt = (r.fineAuOz * simGold) +
          (r.fineAgOz * simSilver) +
          (r.finePtOz * simPlatinum) +
          (r.finePdOz * simPalladium);
      final coinSimTotal = math.max(r.totalPrimary, simMelt);
      simTotal += coinSimTotal;
      bullionPortion += math.min(simMelt, coinSimTotal);
      numismaticPremium += math.max(0.0, coinSimTotal - simMelt);
    }

    final baseline = summary.totalPrimaryValue;
    final delta = simTotal - baseline;
    final deltaPct = baseline > 0 ? (delta / baseline) * 100.0 : 0.0;

    // Cost-Basis Breakeven for Silver (holding Gold/Pt/Pd at current slider values)
    double? silverBreakeven;
    if (summary.totalCostBasis > 0 && summary.totalFineAgOz > 0.01) {
      double lo = 0.0;
      double hi = 500.0;
      for (int i = 0; i < 24; i++) {
        final mid = (lo + hi) / 2.0;
        double testTotal = 0.0;
        for (final r in summary.records) {
          final m = (r.fineAuOz * simGold) +
              (r.fineAgOz * mid) +
              (r.finePtOz * simPlatinum) +
              (r.finePdOz * simPalladium);
          testTotal += math.max(r.totalPrimary, m);
        }
        if (testTotal < summary.totalCostBasis) {
          lo = mid;
        } else {
          hi = mid;
        }
      }
      silverBreakeven = (lo + hi) / 2.0;
    }

    return SpotSimulationResult(
      baselineTotal: baseline,
      simulatedTotal: simTotal,
      deltaDollars: delta,
      deltaPct: deltaPct,
      bullionPortion: bullionPortion,
      numismaticPremium: numismaticPremium,
      totalFineAuOz: summary.totalFineAuOz,
      totalFineAgOz: summary.totalFineAgOz,
      totalFinePtOz: summary.totalFinePtOz,
      totalFinePdOz: summary.totalFinePdOz,
      silverBreakevenPrice: silverBreakeven,
    );
  }

  static String duplicateKey(CoinModel c) => [
        c.country.trim().toUpperCase(),
        c.year.trim(),
        c.mintMark.trim().toUpperCase(),
        DenominationCanon.normalize(c.denomination).toLowerCase(),
        c.variety.trim().toLowerCase(),
      ].join('|');

  static List<DuplicateGroup> computeDuplicates(
    List<AnalyticsCoinRecord> records, {
    bool includeSets = false,
  }) {
    final buckets = <String, List<AnalyticsCoinRecord>>{};
    for (final r in records) {
      if (!includeSets && (r.coin.isSet || (r.coin.parentSetId ?? '').isNotEmpty)) {
        continue;
      }
      final key = duplicateKey(r.coin);
      buckets.putIfAbsent(key, () => []).add(r);
    }

    final groups = <DuplicateGroup>[];
    for (final entry in buckets.entries) {
      final items = entry.value;
      final totalUnits = items.fold<int>(0, (s, r) => s + r.qty);
      if (totalUnits <= 1) continue;

      final looseCount = items
          .where((r) => !r.coin.isSet && (r.coin.parentSetId ?? '').isEmpty)
          .fold<int>(0, (s, r) => s + r.qty);
      final setCount = totalUnits - looseCount;
      final totalVal = items.fold<double>(0.0, (s, r) => s + r.totalPrimary);
      final avgVal = totalVal / totalUnits;
      final recoverable = math.max(0, totalUnits - 1) * avgVal;

      final sample = items.first.coin;
      final parts = [
        sample.year.trim(),
        sample.mintMark.trim(),
        DenominationCanon.normalize(sample.denomination),
        sample.variety.trim(),
      ].where((p) => p.isNotEmpty).toList();

      groups.add(DuplicateGroup(
        key: entry.key,
        label: parts.isEmpty ? entry.key : parts.join(' '),
        looseCount: looseCount,
        setCount: setCount,
        recoverableValue: recoverable,
        coinIds: items.map((r) => r.coin.id).toList(),
      ));
    }

    groups.sort((a, b) => b.recoverableValue.compareTo(a.recoverableValue));
    return groups;
  }

  /// Generates an RFC-4180 CSV summary for tax/insurance export.
  static String exportSummaryCsv(AnalyticsSummary summary) {
    String esc(String s) {
      if (s.contains(',') || s.contains('"') || s.contains('\n')) {
        return '"${s.replaceAll('"', '""')}"';
      }
      return s;
    }

    final buf = StringBuffer();
    buf.writeln(
      'Year,Mint,Denomination,Series,Grading,Qty,PrimaryValue,NetLiquidation,MeltValue,CostBasis,StorageLocation',
    );
    for (final r in summary.records) {
      final c = r.coin;
      buf.writeln([
        esc(c.year),
        esc(c.mintMark),
        esc(r.canonicalDenom),
        esc(c.programSeries),
        esc(r.normalizedGrading),
        r.qty.toString(),
        r.totalPrimary.toStringAsFixed(2),
        r.totalNetLiq.toStringAsFixed(2),
        r.totalMelt.toStringAsFixed(2),
        r.hasCost ? r.totalCost.toStringAsFixed(2) : '',
        esc(c.storageLocation),
      ].join(','));
    }
    return buf.toString();
  }
}
