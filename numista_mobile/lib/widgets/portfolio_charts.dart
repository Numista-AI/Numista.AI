import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart' as intl;
import '../services/portfolio_snapshot_service.dart';

// ══════════════════════════════════════════════════════════════════════════════
//  PortfolioChartsPanel
//  ────────────────────
//  Three fl_chart visualizations for the HomeDashboard:
//    1. Value Composition Donut  (Melt vs. Numismatic Premium)
//    2. Top Programs Bar Chart   (top 5 series by AI Estimated Value)
//    3. Portfolio Value Over Time (line chart from daily snapshots)
//
//  All data is passed in from the parent — this widget is stateless except for
//  chart touch interactions.
// ══════════════════════════════════════════════════════════════════════════════

class PortfolioChartsPanel extends StatelessWidget {
  final double portfolioValue;
  final double meltValue;
  final double acquisitionCost;
  final Map<String, double> programValues; // program name → total AI Est. Value
  final List<PortfolioSnapshot> snapshots;

  const PortfolioChartsPanel({
    super.key,
    required this.portfolioValue,
    required this.meltValue,
    required this.acquisitionCost,
    required this.programValues,
    required this.snapshots,
  });

  // ── Shared styling constants ──────────────────────────────────────────────

  static const _cardColor = Colors.white;
  static const _borderColor = Color(0xFFE2E6E9);
  static const _titleColor = Color(0xFF31333F);
  static const _subtitleColor = Color(0xFF64748B);
  static const _meltColor = Color(0xFF94A3B8);      // silver-grey
  static const _premiumColor = Color(0xFF6C63FF);    // purple
  static const _lineColor = Color(0xFF0F9D58);       // green
  static const _barColors = [
    Color(0xFF6C63FF),  // purple
    Color(0xFF0F9D58),  // green
    Color(0xFF3B82F6),  // blue
    Color(0xFFF59E0B),  // amber
    Color(0xFFEF4444),  // red
  ];

  BoxDecoration get _cardDecoration => BoxDecoration(
    color: _cardColor,
    borderRadius: BorderRadius.circular(8),
    border: Border.all(color: _borderColor),
    boxShadow: [
      BoxShadow(
        color: Colors.black.withValues(alpha: 0.04),
        blurRadius: 4,
        offset: const Offset(0, 2),
      ),
    ],
  );

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Section header
        Row(
          children: const [
            Icon(Icons.insights, size: 15, color: Color(0xFF6C63FF)),
            SizedBox(width: 6),
            Text(
              'PORTFOLIO INSIGHTS',
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w700,
                color: _subtitleColor,
                letterSpacing: 0.5,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        // Charts in a responsive layout
        LayoutBuilder(
          builder: (context, constraints) {
            final isWide = constraints.maxWidth >= 640;
            if (isWide) {
              // Side-by-side: donut + bar chart, then line chart full width
              return Column(
                children: [
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(child: _buildDonutChart()),
                      const SizedBox(width: 12),
                      Expanded(child: _buildBarChart()),
                    ],
                  ),
                  const SizedBox(height: 12),
                  _buildLineChart(),
                ],
              );
            }
            // Stacked on narrow screens
            return Column(
              children: [
                _buildDonutChart(),
                const SizedBox(height: 12),
                _buildBarChart(),
                const SizedBox(height: 12),
                _buildLineChart(),
              ],
            );
          },
        ),
      ],
    );
  }

  // ── Chart 1: Value Composition Donut ──────────────────────────────────────

  Widget _buildDonutChart() {
    final premium = (portfolioValue - meltValue).clamp(0.0, double.infinity);
    final fmt = intl.NumberFormat.currency(symbol: '\$');
    final hasMelt = meltValue > 0;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: _cardDecoration,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Value Composition',
              style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: _titleColor)),
          const SizedBox(height: 4),
          Text(
            hasMelt
                ? 'Precious metal melt value vs. numismatic premium'
                : 'Add silver or gold coins to see melt breakdown',
            style: const TextStyle(fontSize: 10, color: _subtitleColor),
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 180,
            child: hasMelt
                ? Stack(
                    alignment: Alignment.center,
                    children: [
                      PieChart(
                        PieChartData(
                          sectionsSpace: 3,
                          centerSpaceRadius: 48,
                          sections: [
                            PieChartSectionData(
                              value: meltValue,
                              color: _meltColor,
                              title: 'Melt',
                              titleStyle: const TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.white),
                              radius: 32,
                            ),
                            PieChartSectionData(
                              value: premium,
                              color: _premiumColor,
                              title: 'Premium',
                              titleStyle: const TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.white),
                              radius: 32,
                            ),
                          ],
                        ),
                      ),
                      // Center label
                      Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Text('TOTAL',
                              style: TextStyle(
                                  fontSize: 8,
                                  fontWeight: FontWeight.w600,
                                  color: _subtitleColor)),
                          FittedBox(
                            fit: BoxFit.scaleDown,
                            child: Text(fmt.format(portfolioValue),
                                style: const TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.w800,
                                    color: _titleColor)),
                          ),
                        ],
                      ),
                    ],
                  )
                : Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.donut_large,
                            size: 40, color: Colors.grey.shade300),
                        const SizedBox(height: 8),
                        const Text('No precious metal data yet',
                            style: TextStyle(
                                fontSize: 11, color: _subtitleColor)),
                      ],
                    ),
                  ),
          ),
          if (hasMelt) ...[
            const SizedBox(height: 12),
            _legend(_meltColor, 'Melt Value', fmt.format(meltValue)),
            const SizedBox(height: 4),
            _legend(_premiumColor, 'Numismatic Premium', fmt.format(premium)),
          ],
        ],
      ),
    );
  }

  Widget _legend(Color color, String label, String value) {
    return Row(
      children: [
        Container(
          width: 10, height: 10,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(width: 6),
        Expanded(
          child: Text(label,
              style: const TextStyle(fontSize: 11, color: _subtitleColor)),
        ),
        Text(value,
            style: const TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color: _titleColor)),
      ],
    );
  }

  // ── Chart 2: Top Programs Bar Chart ───────────────────────────────────────

  Widget _buildBarChart() {
    // Sort programs by value descending, take top 5
    final sorted = programValues.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));
    final top = sorted.take(5).toList();
    final fmt = intl.NumberFormat.currency(symbol: '\$', decimalDigits: 0);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: _cardDecoration,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Top Programs by Value',
              style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: _titleColor)),
          const SizedBox(height: 4),
          Text(
            top.isEmpty
                ? 'Add coins to see program breakdown'
                : 'Top ${top.length} series by AI estimated value',
            style: const TextStyle(fontSize: 10, color: _subtitleColor),
          ),
          const SizedBox(height: 16),
          if (top.isEmpty)
            SizedBox(
              height: 180,
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.bar_chart, size: 40, color: Colors.grey.shade300),
                    const SizedBox(height: 8),
                    const Text('No program data yet',
                        style: TextStyle(fontSize: 11, color: _subtitleColor)),
                  ],
                ),
              ),
            )
          else
            ...top.asMap().entries.map((entry) {
              final i = entry.key;
              final program = entry.value;
              final maxVal = top.first.value;
              final pct = maxVal > 0 ? (program.value / maxVal) : 0.0;
              final color = _barColors[i % _barColors.length];

              return Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            program.key,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: _titleColor),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(fmt.format(program.value),
                            style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w700,
                                color: color)),
                      ],
                    ),
                    const SizedBox(height: 4),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(3),
                      child: LinearProgressIndicator(
                        value: pct,
                        minHeight: 8,
                        backgroundColor: const Color(0xFFF0F2F6),
                        valueColor: AlwaysStoppedAnimation<Color>(color),
                      ),
                    ),
                  ],
                ),
              );
            }),
        ],
      ),
    );
  }

  // ── Chart 3: Portfolio Value Over Time ─────────────────────────────────────

  Widget _buildLineChart() {
    final hasData = snapshots.length >= 2;
    final fmt = intl.NumberFormat.currency(symbol: '\$', decimalDigits: 0);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: _cardDecoration,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Portfolio Value Over Time',
                        style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w700,
                            color: _titleColor)),
                    SizedBox(height: 4),
                    Text('Daily snapshots from each visit',
                        style: TextStyle(fontSize: 10, color: _subtitleColor)),
                  ],
                ),
              ),
              if (hasData)
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF0FDF4),
                    borderRadius: BorderRadius.circular(4),
                    border: Border.all(color: const Color(0xFF86EFAC)),
                  ),
                  child: Text(
                    '${snapshots.length} days tracked',
                    style: const TextStyle(
                        fontSize: 9,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF166534)),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 200,
            child: hasData ? _buildLineChartContent(fmt) : _buildLineChartPlaceholder(),
          ),
        ],
      ),
    );
  }

  Widget _buildLineChartPlaceholder() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.timeline, size: 40, color: Colors.grey.shade300),
          const SizedBox(height: 8),
          const Text(
            'Not enough data yet',
            style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: _subtitleColor),
          ),
          const SizedBox(height: 4),
          Text(
            snapshots.isEmpty
                ? 'Your first snapshot was just recorded — check back tomorrow!'
                : 'One snapshot recorded so far — the chart appears after your next visit.',
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 10, color: _subtitleColor),
          ),
        ],
      ),
    );
  }

  Widget _buildLineChartContent(intl.NumberFormat fmt) {
    // Build spots from snapshots
    final spots = snapshots.asMap().entries.map((e) {
      return FlSpot(e.key.toDouble(), e.value.portfolioValue);
    }).toList();

    // Y-axis range with padding
    final values = snapshots.map((s) => s.portfolioValue).toList();
    final minY = values.reduce((a, b) => a < b ? a : b);
    final maxY = values.reduce((a, b) => a > b ? a : b);
    final range = maxY - minY;
    final yPad = range > 0 ? range * 0.15 : maxY * 0.1;
    final chartMinY = (minY - yPad).clamp(0.0, double.infinity);
    final chartMaxY = maxY + yPad;

    // X-axis labels: show up to 5 date labels
    final labelCount = snapshots.length < 5 ? snapshots.length : 5;
    final step = (snapshots.length - 1) / (labelCount - 1);

    return LineChart(
      LineChartData(
        minY: chartMinY,
        maxY: chartMaxY,
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          horizontalInterval: range > 0 ? range / 4 : maxY / 4,
          getDrawingHorizontalLine: (_) => FlLine(
            color: const Color(0xFFE2E6E9),
            strokeWidth: 0.8,
          ),
        ),
        titlesData: FlTitlesData(
          topTitles: const AxisTitles(
              sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(
              sideTitles: SideTitles(showTitles: false)),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 52,
              getTitlesWidget: (value, meta) {
                if (value == meta.min || value == meta.max) {
                  return const SizedBox.shrink();
                }
                return Padding(
                  padding: const EdgeInsets.only(right: 4),
                  child: Text(
                    fmt.format(value),
                    style: const TextStyle(
                        fontSize: 9, color: _subtitleColor),
                  ),
                );
              },
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 28,
              getTitlesWidget: (value, meta) {
                final idx = value.round();
                if (idx < 0 || idx >= snapshots.length) {
                  return const SizedBox.shrink();
                }
                // Only show labels at evenly spaced intervals
                bool showLabel = false;
                for (int i = 0; i < labelCount; i++) {
                  if ((i * step).round() == idx) {
                    showLabel = true;
                    break;
                  }
                }
                if (!showLabel) return const SizedBox.shrink();

                final date = snapshots[idx].date;
                // Format "2026-06-15" → "Jun 15"
                final parts = date.split('-');
                final month = _shortMonth(int.tryParse(parts[1]) ?? 1);
                final day = parts.length > 2 ? parts[2] : '';
                return Padding(
                  padding: const EdgeInsets.only(top: 6),
                  child: Text(
                    '$month $day',
                    style: const TextStyle(
                        fontSize: 9, color: _subtitleColor),
                  ),
                );
              },
            ),
          ),
        ),
        borderData: FlBorderData(show: false),
        lineBarsData: [
          LineChartBarData(
            spots: spots,
            isCurved: true,
            curveSmoothness: 0.25,
            color: _lineColor,
            barWidth: 2.5,
            dotData: FlDotData(
              show: snapshots.length <= 30,
              getDotPainter: (spot, percent, bar, index) =>
                  FlDotCirclePainter(
                radius: 3,
                color: _lineColor,
                strokeWidth: 1.5,
                strokeColor: Colors.white,
              ),
            ),
            belowBarData: BarAreaData(
              show: true,
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  _lineColor.withValues(alpha: 0.25),
                  _lineColor.withValues(alpha: 0.0),
                ],
              ),
            ),
          ),
        ],
        lineTouchData: LineTouchData(
          touchTooltipData: LineTouchTooltipData(
            getTooltipColor: (_) => const Color(0xFF1E293B),
            getTooltipItems: (touchedSpots) {
              return touchedSpots.map((spot) {
                final idx = spot.spotIndex;
                final snap = snapshots[idx];
                return LineTooltipItem(
                  '${snap.date}\n${fmt.format(snap.portfolioValue)}',
                  const TextStyle(
                    color: Colors.white,
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                );
              }).toList();
            },
          ),
        ),
      ),
    );
  }

  static String _shortMonth(int month) {
    const months = [
      '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
    ];
    return months[month.clamp(1, 12)];
  }
}
