import 'dart:convert';
import 'package:flutter/material.dart';
import '../constants.dart';
import '../services/http_auth_client.dart';
import '../services/morgan_action_bus.dart';

class MorganAnalyticsMessage {
  final bool isUser;
  final String text;
  final List<Map<String, dynamic>>? table;
  final List<String> actionCoinIds;
  final String? actionLabel;
  final List<String> followups;

  const MorganAnalyticsMessage({
    required this.isUser,
    required this.text,
    this.table,
    this.actionCoinIds = const [],
    this.actionLabel,
    this.followups = const [],
  });
}

class MorganAnalyticsPanel extends StatefulWidget {
  final bool advancedMode;
  final double simGold;
  final double simSilver;
  final VoidCallback? onExpandToFullChat;
  final Future<Map<String, dynamic>> Function(String query)? onSubmitOverride;

  const MorganAnalyticsPanel({
    super.key,
    required this.advancedMode,
    required this.simGold,
    required this.simSilver,
    this.onExpandToFullChat,
    this.onSubmitOverride,
  });

  @override
  State<MorganAnalyticsPanel> createState() => _MorganAnalyticsPanelState();
}

class _MorganAnalyticsPanelState extends State<MorganAnalyticsPanel> {
  final TextEditingController _controller = TextEditingController();
  final List<MorganAnalyticsMessage> _messages = [];
  bool _loading = false;
  bool _collapsed = false;

  static const _starterChips = [
    'Silver \$50 / Gold \$3,500?',
    'Find my loose duplicates',
    'Break down by metal',
  ];

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _sendQuery(String raw) async {
    final q = raw.trim();
    if (q.isEmpty || _loading) return;
    _controller.clear();
    setState(() {
      _collapsed = false;
      _messages.add(MorganAnalyticsMessage(isUser: true, text: q));
      _loading = true;
    });

    try {
      Map<String, dynamic> data;
      if (widget.onSubmitOverride != null) {
        data = await widget.onSubmitOverride!(q);
      } else {
        final uri = Uri.parse('$kApiBaseUrl/api/analytics/morgan');
        final resp = await HttpAuthClient.post(
          uri,
          body: jsonEncode({
            'query': q,
            'advanced_mode': widget.advancedMode,
            'sim_gold': widget.simGold,
            'sim_silver': widget.simSilver,
          }),
        );
        if (resp.statusCode == 429) {
          throw Exception(
              'Monthly starter quota reached for Morgan Analytics. Upgrade to Pro for unlimited queries.');
        }
        if (resp.statusCode == 401) {
          throw Exception('Please sign in to ask Morgan Analytics.');
        }
        if (resp.statusCode >= 400) {
          throw Exception('Morgan Analytics returned HTTP ${resp.statusCode}.');
        }
        data = jsonDecode(resp.body) as Map<String, dynamic>;
      }

      final tableRaw = data['table'] as List<dynamic>?;
      final table = tableRaw
          ?.map((e) => Map<String, dynamic>.from(e as Map))
          .toList();
      final coinIds = (data['action_coin_ids'] as List<dynamic>? ?? const [])
          .map((e) => e.toString())
          .toList();
      final followups =
          (data['suggested_followups'] as List<dynamic>? ?? const [])
              .map((e) => e.toString())
              .toList();

      if (!mounted) return;
      setState(() {
        _messages.add(MorganAnalyticsMessage(
          isUser: false,
          text: (data['reply'] ?? 'Done.').toString(),
          table: table,
          actionCoinIds: coinIds,
          actionLabel: data['action_label']?.toString(),
          followups: followups,
        ));
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _messages.add(MorganAnalyticsMessage(
          isUser: false,
          text: e.toString().replaceFirst('Exception: ', ''),
        ));
      });
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      key: const Key('morgan_analytics_panel'),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              children: [
                Image.asset(
                  'assets/logo_owl.png',
                  height: 24,
                  errorBuilder: (context, error, stackTrace) => Icon(
                    Icons.auto_awesome,
                    color: theme.colorScheme.primary,
                    size: 22,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Ask Morgan Analytics',
                    style: theme.textTheme.titleMedium
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                ),
                if (widget.onExpandToFullChat != null)
                  IconButton(
                    tooltip: 'Expand to Full Chat',
                    icon: const Icon(Icons.open_in_full, size: 18),
                    onPressed: widget.onExpandToFullChat,
                  ),
                IconButton(
                  tooltip: _collapsed ? 'Expand' : 'Collapse',
                  icon: Icon(
                    _collapsed ? Icons.expand_less : Icons.expand_more,
                    size: 20,
                  ),
                  onPressed: () => setState(() => _collapsed = !_collapsed),
                ),
              ],
            ),
            if (!_collapsed) ...[
              const SizedBox(height: 8),
              if (_messages.isEmpty)
                Wrap(
                  spacing: 6,
                  runSpacing: 6,
                  children: _starterChips
                      .map((c) => ActionChip(
                            label: Text(c, style: const TextStyle(fontSize: 12)),
                            onPressed: () => _sendQuery(c),
                          ))
                      .toList(),
                )
              else
                ConstrainedBox(
                  constraints: const BoxConstraints(maxHeight: 280),
                  child: ListView.separated(
                    shrinkWrap: true,
                    itemCount: _messages.length,
                    separatorBuilder: (context, index) => const SizedBox(height: 8),
                    itemBuilder: (context, idx) {
                      final m = _messages[idx];
                      return Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: m.isUser
                              ? theme.colorScheme.primary.withValues(alpha: 0.1)
                              : theme.colorScheme.surfaceContainerHighest
                                  .withValues(alpha: 0.5),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              m.isUser ? 'You' : 'Morgan',
                              style: theme.textTheme.labelSmall
                                  ?.copyWith(fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(height: 4),
                            Text(m.text, style: theme.textTheme.bodyMedium),
                            if (m.actionCoinIds.isNotEmpty) ...[
                              const SizedBox(height: 8),
                              ActionChip(
                                avatar: const Icon(Icons.filter_list, size: 16),
                                label: Text(m.actionLabel ??
                                    'View ${m.actionCoinIds.length} coins in My Collection'),
                                onPressed: () {
                                  MorganActionBus.instance
                                          .pendingCollectionCoinIdsFilter =
                                      m.actionCoinIds.toSet();
                                  MorganActionBus.instance.onNavigateToRoute
                                      ?.call('My Collection');
                                },
                              ),
                            ],
                          ],
                        ),
                      );
                    },
                  ),
                ),
              if (_loading) ...[
                const SizedBox(height: 8),
                const LinearProgressIndicator(),
              ],
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      key: const Key('morgan_analytics_input'),
                      controller: _controller,
                      decoration: InputDecoration(
                        hintText: 'Ask about your vault, spot prices, duplicates...',
                        isDense: true,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(10),
                        ),
                      ),
                      onSubmitted: _sendQuery,
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton.filled(
                    key: const Key('morgan_analytics_send'),
                    onPressed: _loading
                        ? null
                        : () => _sendQuery(_controller.text),
                    icon: const Icon(Icons.send_rounded, size: 18),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}
