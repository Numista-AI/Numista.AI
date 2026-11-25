import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../models/coin_model.dart';
import '../services/analytics_calculator.dart';
import '../services/auth_service.dart';
import '../utils/sold_item.dart';
import '../services/guest_seed_service.dart';
import '../services/morgan_action_bus.dart';
import '../services/morgan_screen_state_registry.dart';
import '../services/valuation_mode_service.dart';
import '../widgets/analytics_breakdown_charts.dart';
import '../widgets/analytics_spot_simulator_card.dart';
import '../widgets/morgan_analytics_panel.dart';

class AnalyticsScreen extends StatefulWidget {
  final List<CoinModel>? initialCoins;
  final bool? initialAdvancedMode;
  final VoidCallback? onExpandMorganToFullChat;
  final void Function(List<String> coinIds)? onOpenCoinsInCollection;
  final Future<Map<String, dynamic>> Function(String query)?
      onMorganSubmitOverride;

  const AnalyticsScreen({
    super.key,
    this.initialCoins,
    this.initialAdvancedMode,
    this.onExpandMorganToFullChat,
    this.onOpenCoinsInCollection,
    this.onMorganSubmitOverride,
  });

  @override
  State<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen> {
  bool _loading = true;
  String? _error;
  bool _advancedMode = false;
  AnalyticsSummary? _summary;

  final double _liveGold = 2650.0;
  final double _liveSilver = 31.50;
  double _simGold = 2650.0;
  double _simSilver = 31.50;

  @override
  void initState() {
    super.initState();
    MorganScreenStateRegistry.instance.currentRoute = 'Analytics';
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final adv = widget.initialAdvancedMode ??
          await ValuationModeService.isAdvancedMode();

      List<CoinModel> coins;
      if (widget.initialCoins != null) {
        coins = widget.initialCoins!;
      } else {
        final user = FirebaseAuth.instance.currentUser;
        if (user == null ||
            user.isAnonymous ||
            GuestSeedService.isBrowseDemoMode ||
            AuthService.coinsPath.contains('unknown')) {
          coins = const [];
        } else {
          final snap =
              await FirebaseFirestore.instance.collection(AuthService.coinsPath).get();
          coins = snap.docs
              .where((d) {
                final data = d.data();
                final itemType =
                    (data['item_type'] ?? '').toString().toLowerCase().trim();
                return data['is_supply'] != true && itemType != 'supply' && !isSoldItem(data);
              })
              .map((d) => CoinModel.fromMap(d.data(), d.id))
              .toList();
        }
      }

      final summary =
          AnalyticsCalculator.buildSummary(coins, advancedMode: adv);
      if (!mounted) return;
      setState(() {
        _advancedMode = adv;
        _summary = summary;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = 'Unable to load Analytics: $e';
        _loading = false;
      });
    }
  }

  void _exportCsv() {
    if (_summary == null) return;
    final csv = AnalyticsCalculator.exportSummaryCsv(_summary!);
    Clipboard.setData(ClipboardData(text: csv));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'Copied Analytics CSV (${_summary!.records.length} rows) to clipboard.',
        ),
      ),
    );
  }

  void _openInCollection(List<String> coinIds) {
    if (widget.onOpenCoinsInCollection != null) {
      widget.onOpenCoinsInCollection!(coinIds);
      return;
    }
    MorganActionBus.instance.pendingCollectionCoinIdsFilter = coinIds.toSet();
    MorganActionBus.instance.onNavigateToRoute?.call('My Collection');
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Text(_error!, style: TextStyle(color: theme.colorScheme.error)),
        ),
      );
    }

    final summary = _summary!;
    final simResult = AnalyticsCalculator.simulateSpot(
      summary,
      simGold: _simGold,
      simSilver: _simSilver,
    );

    return LayoutBuilder(
      builder: (context, constraints) {
        final isDesktop = constraints.maxWidth >= 1024;
        final kpiCols = constraints.maxWidth >= 900 ? 4 : 2;
        final cardWidth =
            ((constraints.maxWidth - 32 - ((kpiCols - 1) * 12)) / kpiCols)
                .clamp(140.0, 420.0);

        final kpiCards = [
          _KpiCard(
            width: cardWidth,
            title: _advancedMode ? 'Est. Retail Value' : 'Est. Vault Value',
            value: '\$${summary.totalPrimaryValue.toStringAsFixed(2)}',
            pill: '${summary.pricedCount}/${summary.totalCoins} priced',
            icon: Icons.account_balance_wallet_outlined,
          ),
          _KpiCard(
            width: cardWidth,
            title: 'Net Liquidation',
            value: '\$${summary.totalNetLiquidation.toStringAsFixed(2)}',
            pill: 'Bid or -13% (95% melt floor)',
            tooltip:
                'Uses Greysheet Bid if > \$0; otherwise Primary Value minus 13% friction, floored at 95% of melt for bullion.',
            icon: Icons.sell_outlined,
          ),
          _KpiCard(
            width: cardWidth,
            title: 'Total Melt Value',
            value: '\$${summary.totalMeltValue.toStringAsFixed(2)}',
            pill:
                '${summary.totalFineAuOz.toStringAsFixed(2)} Au / ${summary.totalFineAgOz.toStringAsFixed(2)} Ag oz',
            icon: Icons.toll_outlined,
          ),
          _KpiCard(
            width: cardWidth,
            title: 'Cost Basis & Gain',
            value: '\$${summary.totalCostBasis.toStringAsFixed(2)}',
            pill:
                '${summary.costBasisCount}/${summary.totalCoins} with cost (${summary.unrealizedGainPct.toStringAsFixed(1)}%)',
            icon: Icons.trending_up_rounded,
          ),
        ];

        final mainAnalyticsColumn = Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            AnalyticsSpotSimulatorCard(
              liveGold: _liveGold,
              liveSilver: _liveSilver,
              simGold: _simGold,
              simSilver: _simSilver,
              simResult: simResult,
              onGoldChanged: (v) => setState(() => _simGold = v),
              onSilverChanged: (v) => setState(() => _simSilver = v),
              onReset: () => setState(() {
                _simGold = _liveGold;
                _simSilver = _liveSilver;
              }),
              onApplyPreset: (g, s) => setState(() {
                _simGold = g;
                _simSilver = s;
              }),
            ),
            const SizedBox(height: 16),
            AnalyticsBreakdownCharts(summary: summary),
            const SizedBox(height: 16),
            _DuplicateFinderCard(
              summary: summary,
              onViewCoins: _openInCollection,
            ),
          ],
        );

        final morganPanel = MorganAnalyticsPanel(
          advancedMode: _advancedMode,
          simGold: _simGold,
          simSilver: _simSilver,
          onExpandToFullChat: widget.onExpandMorganToFullChat,
          onSubmitOverride: widget.onMorganSubmitOverride,
        );

        return SingleChildScrollView(
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
                  Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.insights_rounded,
                          color: theme.colorScheme.primary, size: 26),
                      const SizedBox(width: 10),
                      Flexible(
                        child: Text(
                          'Vault Analytics',
                          overflow: TextOverflow.ellipsis,
                          style: theme.textTheme.headlineSmall
                              ?.copyWith(fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                  OutlinedButton.icon(
                    key: const Key('export_analytics_csv_btn'),
                    onPressed: _exportCsv,
                    icon: const Icon(Icons.download_rounded, size: 18),
                    label: const Text('Export Summary (CSV)'),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: kpiCards,
              ),
              const SizedBox(height: 16),
              if (isDesktop)
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(flex: 65, child: mainAnalyticsColumn),
                    const SizedBox(width: 16),
                    Expanded(flex: 35, child: morganPanel),
                  ],
                )
              else ...[
                morganPanel,
                const SizedBox(height: 16),
                mainAnalyticsColumn,
              ],
            ],
          ),
        );
      },
    );
  }
}

class _KpiCard extends StatelessWidget {
  final double width;
  final String title;
  final String value;
  final String pill;
  final String? tooltip;
  final IconData icon;

  const _KpiCard({
    required this.width,
    required this.title,
    required this.value,
    required this.pill,
    this.tooltip,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return SizedBox(
      width: width,
      child: Card(
        elevation: 1,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(icon, size: 18, color: theme.colorScheme.primary),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      title,
                      style: theme.textTheme.labelMedium
                          ?.copyWith(color: theme.hintColor),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  if (tooltip != null)
                    Tooltip(
                      message: tooltip!,
                      child: Icon(Icons.info_outline,
                          size: 15, color: theme.hintColor),
                    ),
                ],
              ),
              const SizedBox(height: 6),
              Text(
                value,
                style: theme.textTheme.titleLarge
                    ?.copyWith(fontWeight: FontWeight.bold),
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: theme.colorScheme.surfaceContainerHighest
                      .withValues(alpha: 0.6),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  pill,
                  style: theme.textTheme.labelSmall,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _DuplicateFinderCard extends StatelessWidget {
  final AnalyticsSummary summary;
  final void Function(List<String> coinIds) onViewCoins;

  const _DuplicateFinderCard({
    required this.summary,
    required this.onViewCoins,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final groups = summary.duplicateGroups;

    return Card(
      key: const Key('duplicate_finder_card'),
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
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.content_copy_rounded,
                        color: theme.colorScheme.primary, size: 20),
                    const SizedBox(width: 8),
                    Flexible(
                      child: Text(
                        'Smart Duplicate Finder',
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.titleMedium
                            ?.copyWith(fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
                if (groups.isNotEmpty)
                  Chip(
                    label: Text(
                      'Recoverable: \$${summary.totalDuplicateRecoverable.toStringAsFixed(2)}',
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 10),
            if (groups.isEmpty)
              const Text('No loose duplicate coins detected in your vault.')
            else
              Column(
                children: [
                  for (final g in groups.take(8))
                    ListTile(
                      dense: true,
                      contentPadding: EdgeInsets.zero,
                      title: Text(g.label, overflow: TextOverflow.ellipsis),
                      subtitle: Text(
                        '${g.looseCount} loose${g.setCount > 0 ? ', ${g.setCount} in sets' : ''} • ~\$${g.recoverableValue.toStringAsFixed(2)} recoverable',
                      ),
                      trailing: TextButton(
                        onPressed: () => onViewCoins(g.coinIds),
                        child: const Text('View in Vault'),
                      ),
                    ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
