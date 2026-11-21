import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import '../services/analytics_calculator.dart';

enum BreakdownDimension { metal, denomination, series, grading }

class AnalyticsBreakdownCharts extends StatefulWidget {
  final AnalyticsSummary summary;

  const AnalyticsBreakdownCharts({super.key, required this.summary});

  @override
  State<AnalyticsBreakdownCharts> createState() =>
      _AnalyticsBreakdownChartsState();
}

class _AnalyticsBreakdownChartsState extends State<AnalyticsBreakdownCharts> {
  BreakdownDimension _dimension = BreakdownDimension.metal;

  static const _palette = [
    Color(0xFF4F46E5),
    Color(0xFFD97706),
    Color(0xFF059669),
    Color(0xFFDB2777),
    Color(0xFF0284C7),
    Color(0xFF7C3AED),
  ];

  Map<String, double> _aggregate() {
    final map = <String, double>{};
    for (final r in widget.summary.records) {
      final String key;
      switch (_dimension) {
        case BreakdownDimension.metal:
          key = r.normalizedMetal;
          break;
        case BreakdownDimension.denomination:
          key = r.canonicalDenom;
          break;
        case BreakdownDimension.series:
          key = r.coin.programSeries.trim().isEmpty
              ? 'Other'
              : r.coin.programSeries.trim();
          break;
        case BreakdownDimension.grading:
          key = r.normalizedGrading;
          break;
      }
      map[key] = (map[key] ?? 0.0) + r.totalPrimary;
    }
    final sorted = map.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));
    if (sorted.length <= 6) {
      return Map.fromEntries(sorted);
    }
    final top5 = sorted.take(5).toList();
    final otherSum =
        sorted.skip(5).fold<double>(0.0, (sum, e) => sum + e.value);
    return {
      for (final e in top5) e.key: e.value,
      'Other': otherSum,
    };
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final groups = _aggregate();
    final total = groups.values.fold<double>(0.0, (s, v) => s + v);
    final entries = groups.entries.toList();

    final crownJewels = [...widget.summary.records]
      ..sort((a, b) => b.totalPrimary.compareTo(a.totalPrimary));
    final top5 = crownJewels.take(5).toList();
    final top3Sum = crownJewels.take(3).fold<double>(0.0, (s, r) => s + r.totalPrimary);
    final top3Share = widget.summary.totalPrimaryValue > 0
        ? (top3Sum / widget.summary.totalPrimaryValue) * 100.0
        : 0.0;

    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Wrap(
              alignment: WrapAlignment.spaceBetween,
              crossAxisAlignment: WrapCrossAlignment.center,
              spacing: 12,
              runSpacing: 8,
              children: [
                Text(
                  'Portfolio Breakdown',
                  style: theme.textTheme.titleMedium
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: SegmentedButton<BreakdownDimension>(
                    segments: const [
                      ButtonSegment(
                          value: BreakdownDimension.metal, label: Text('Metal')),
                      ButtonSegment(
                          value: BreakdownDimension.denomination,
                          label: Text('Denom')),
                      ButtonSegment(
                          value: BreakdownDimension.series, label: Text('Series')),
                      ButtonSegment(
                          value: BreakdownDimension.grading, label: Text('Grade')),
                    ],
                    selected: {_dimension},
                    onSelectionChanged: (s) =>
                        setState(() => _dimension = s.first),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (total <= 0)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 24),
                child: Center(
                    child: Text('No priced coins available for chart.')),
              )
            else
              LayoutBuilder(
                builder: (context, constraints) {
                  final isWide = constraints.maxWidth >= 520;
                  final chart = SizedBox(
                    height: 180,
                    width: 180,
                    child: PieChart(
                      PieChartData(
                        centerSpaceRadius: 42,
                        sectionsSpace: 2,
                        sections: [
                          for (int i = 0; i < entries.length; i++)
                            PieChartSectionData(
                              value: entries[i].value,
                              color: _palette[i % _palette.length],
                              radius: 42,
                              title:
                                  '${((entries[i].value / total) * 100).toStringAsFixed(0)}%',
                              titleStyle: const TextStyle(
                                color: Colors.white,
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                        ],
                      ),
                    ),
                  );
                  final legend = Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      for (int i = 0; i < entries.length; i++)
                        Padding(
                          padding: const EdgeInsets.symmetric(vertical: 4),
                          child: Row(
                            children: [
                              Container(
                                width: 10,
                                height: 10,
                                decoration: BoxDecoration(
                                  color: _palette[i % _palette.length],
                                  shape: BoxShape.circle,
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  entries[i].key,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              Text(
                                '\$${entries[i].value.toStringAsFixed(0)}',
                                style: const TextStyle(
                                    fontWeight: FontWeight.w600),
                              ),
                            ],
                          ),
                        ),
                    ],
                  );
                  if (isWide) {
                    return Row(
                      children: [
                        chart,
                        const SizedBox(width: 24),
                        Expanded(child: legend),
                      ],
                    );
                  }
                  return Column(
                    children: [
                      Center(child: chart),
                      const SizedBox(height: 12),
                      legend,
                    ],
                  );
                },
              ),
            const Divider(height: 28),
            Wrap(
              alignment: WrapAlignment.spaceBetween,
              crossAxisAlignment: WrapCrossAlignment.center,
              spacing: 8,
              runSpacing: 6,
              children: [
                Text(
                  'Top 5 Crown Jewels',
                  style: theme.textTheme.titleSmall
                      ?.copyWith(fontWeight: FontWeight.bold),
                ),
                if (top3Share >= 40.0)
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: Colors.amber.withValues(alpha: 0.16),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      'Concentration: Top 3 = ${top3Share.toStringAsFixed(0)}%',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.w600,
                        color: Colors.amber[900],
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 8),
            for (final r in top5)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        '${r.coin.year} ${r.coin.mintMark} ${r.canonicalDenom} ${r.coin.programSeries}'
                            .trim(),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '\$${r.totalPrimary.toStringAsFixed(2)}',
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
