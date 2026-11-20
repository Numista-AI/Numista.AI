import 'package:flutter/material.dart';
import '../services/analytics_calculator.dart';

class AnalyticsSpotSimulatorCard extends StatelessWidget {
  final double liveGold;
  final double liveSilver;
  final double simGold;
  final double simSilver;
  final SpotSimulationResult simResult;
  final ValueChanged<double> onGoldChanged;
  final ValueChanged<double> onSilverChanged;
  final VoidCallback onReset;
  final void Function(double gold, double silver) onApplyPreset;

  const AnalyticsSpotSimulatorCard({
    super.key,
    required this.liveGold,
    required this.liveSilver,
    required this.simGold,
    required this.simSilver,
    required this.simResult,
    required this.onGoldChanged,
    required this.onSilverChanged,
    required this.onReset,
    required this.onApplyPreset,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final total = simResult.simulatedTotal;
    final bullionFrac =
        total > 0 ? (simResult.bullionPortion / total).clamp(0.0, 1.0) : 0.0;
    final numismaticFrac = (1.0 - bullionFrac).clamp(0.0, 1.0);
    final isPositive = simResult.deltaDollars >= 0;

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
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.tune_rounded,
                        color: theme.colorScheme.primary, size: 20),
                    const SizedBox(width: 8),
                    Flexible(
                      child: Text(
                        'Spot-Price "What-If" Simulator',
                        overflow: TextOverflow.ellipsis,
                        style: theme.textTheme.titleMedium
                            ?.copyWith(fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
                TextButton.icon(
                  onPressed: onReset,
                  icon: const Icon(Icons.refresh, size: 16),
                  label: const Text('Reset to Live Spot'),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 6,
              children: [
                ActionChip(
                  label: const Text('Live Spot'),
                  onPressed: () => onApplyPreset(liveGold, liveSilver),
                ),
                ActionChip(
                  label: const Text('Silver \$50 / Gold \$3,500'),
                  onPressed: () => onApplyPreset(3500.0, 50.0),
                ),
                ActionChip(
                  label: const Text('-20% Pullback'),
                  onPressed: () =>
                      onApplyPreset(liveGold * 0.8, liveSilver * 0.8),
                ),
              ],
            ),
            const SizedBox(height: 14),
            Wrap(
              alignment: WrapAlignment.spaceBetween,
              crossAxisAlignment: WrapCrossAlignment.center,
              spacing: 12,
              runSpacing: 8,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Simulated Vault Value',
                      style: theme.textTheme.labelMedium
                          ?.copyWith(color: theme.hintColor),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '\$${total.toStringAsFixed(2)}',
                      key: const Key('sim_total_value'),
                      style: theme.textTheme.headlineSmall
                          ?.copyWith(fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: (isPositive ? Colors.green : Colors.red)
                        .withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    '${isPositive ? '+' : ''}\$${simResult.deltaDollars.toStringAsFixed(2)} (${simResult.deltaPct.toStringAsFixed(1)}%)',
                    style: TextStyle(
                      color: isPositive ? Colors.green[700] : Colors.red[700],
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            // Gold Slider
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text('Gold (Au): \$${simGold.toStringAsFixed(0)}/oz',
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.bodyMedium
                          ?.copyWith(fontWeight: FontWeight.w600)),
                ),
                const SizedBox(width: 8),
                Text('${simResult.totalFineAuOz.toStringAsFixed(3)} oz',
                    style: theme.textTheme.bodySmall),
              ],
            ),
            Slider(
              key: const Key('sim_gold_slider'),
              value: simGold.clamp(1000.0, 6000.0),
              min: 1000.0,
              max: 6000.0,
              divisions: 100,
              onChanged: onGoldChanged,
            ),
            // Silver Slider
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                      'Silver (Ag): \$${simSilver.toStringAsFixed(2)}/oz',
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.bodyMedium
                          ?.copyWith(fontWeight: FontWeight.w600)),
                ),
                const SizedBox(width: 8),
                Text('${simResult.totalFineAgOz.toStringAsFixed(3)} oz',
                    style: theme.textTheme.bodySmall),
              ],
            ),
            Slider(
              key: const Key('sim_silver_slider'),
              value: simSilver.clamp(10.0, 150.0),
              min: 10.0,
              max: 150.0,
              divisions: 140,
              onChanged: onSilverChanged,
            ),
            const SizedBox(height: 8),
            // Bullion vs Numismatic Split Bar
            Text(
              'Bullion (${(bullionFrac * 100).toStringAsFixed(0)}%) vs. Numismatic Premium (${(numismaticFrac * 100).toStringAsFixed(0)}%)',
              style: theme.textTheme.bodySmall,
            ),
            const SizedBox(height: 6),
            ClipRRect(
              borderRadius: BorderRadius.circular(6),
              child: SizedBox(
                height: 10,
                child: Row(
                  children: [
                    if (bullionFrac > 0)
                      Expanded(
                        flex: (bullionFrac * 1000).round().clamp(1, 1000),
                        child: Container(color: Colors.amber[700]),
                      ),
                    if (numismaticFrac > 0)
                      Expanded(
                        flex: (numismaticFrac * 1000).round().clamp(1, 1000),
                        child: Container(color: theme.colorScheme.primary),
                      ),
                  ],
                ),
              ),
            ),
            if (simResult.silverBreakevenPrice != null) ...[
              const SizedBox(height: 10),
              Text(
                'Cost-Basis Breakeven: Vault exceeds recorded cost basis above \$${simResult.silverBreakevenPrice!.toStringAsFixed(2)}/oz Silver.',
                style: theme.textTheme.bodySmall
                    ?.copyWith(color: theme.colorScheme.secondary),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
