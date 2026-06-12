import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:intl/intl.dart' as intl;
import '../services/auth_service.dart';
import '../services/morgan_prefs.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';
import 'dart:convert';
import '../services/melt_value_service.dart';
import '../constants.dart';

class HomeDashboard extends StatefulWidget {
  /// Called when the user taps "Ask Morgan" — routes to 'AI Deepdive'.
  final VoidCallback? onAskMorgan;
  const HomeDashboard({super.key, this.onAskMorgan});

  @override
  State<HomeDashboard> createState() => _HomeDashboardState();
}

class _HomeDashboardState extends State<HomeDashboard> {
  Map<String, double> _spotPrices = {};
  bool _isLoadingPrices = true;
  DateTime? _pricesLastUpdated;
  List<dynamic> _news = [];
  bool _isLoadingNews = true;

  @override
  void initState() {
    super.initState();
    _fetchSpotPrices();
    _fetchNews();
  }

  Future<void> _fetchNews() async {
    try {
      final response = await http.get(
          Uri.parse('$kApiBaseUrl/api/mint_news'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (!mounted) return;
        setState(() {
          _news = data['news'] ?? [];
          _isLoadingNews = false;
        });
      } else {
        if (!mounted) return;
        setState(() => _isLoadingNews = false);
      }
    } catch (e) {
      if (!mounted) return;
      setState(() => _isLoadingNews = false);
    }
  }

  Future<void> _fetchSpotPrices() async {
    try {
      final response = await http.get(
          Uri.parse('$kApiBaseUrl/api/spot_prices'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (!mounted) return;
        setState(() {
          _spotPrices = {
            'Gold':      (data['Gold']      ?? 0).toDouble(),
            'Silver':    (data['Silver']    ?? 0).toDouble(),
            'Platinum':  (data['Platinum']  ?? 0).toDouble(),
            'Palladium': (data['Palladium'] ?? 0).toDouble(),
          };
          _isLoadingPrices = false;
          _pricesLastUpdated = DateTime.now();
        });
      } else {
        if (!mounted) return;
        setState(() => _isLoadingPrices = false);
      }
    } catch (e) {
      if (!mounted) return;
      setState(() => _isLoadingPrices = false);
    }
  }

  double _parseCurrency(dynamic value) {
    if (value == null) return 0.0;
    final raw = value.toString();
    if (raw.contains(' - ')) {
      final parts = raw.split(' - ');
      final a = double.tryParse(parts[0].replaceAll(RegExp(r'[^\d.]'), '')) ?? 0.0;
      final b = double.tryParse(parts[1].replaceAll(RegExp(r'[^\d.]'), '')) ?? 0.0;
      return (a + b) / 2;
    }
    return double.tryParse(raw.replaceAll(RegExp(r'[^\d.]'), '')) ?? 0.0;
  }

  static double _computeFaceValue(String denom) {
    final s = denom.toLowerCase().trim();
    // ── Word-based matches (unambiguous) ─────────────────────────────────────
    if (s.contains('penny')   || s.contains('cent')   || s.contains('1c'))  return 0.01;
    if (s.contains('nickel')  || s.contains('5c'))                           return 0.05;
    if (s.contains('dime')    || s.contains('10c'))                          return 0.10;
    if (s.contains('quarter') || s.contains('25c'))                          return 0.25;
    if (s.contains('half')    || s.contains('50c'))                          return 0.50;
    // ── Dollar-sign matches: MUST go largest → smallest to prevent
    // ── substring collisions (e.g. "$10" contains "$1" → wrong match) ────────
    if (s.contains(r'$500'))  return 500.00;  // 1oz gold bar / commemorative
    if (s.contains(r'$100'))  return 100.00;  // high-denomination gold
    if (s.contains(r'$50'))   return 50.00;   // $50 Buffalo / gold eagle
    if (s.contains(r'$25'))   return 25.00;   // $25 half-oz gold eagle
    if (s.contains(r'$20'))   return 20.00;   // Saint-Gaudens / Liberty double eagle
    if (s.contains(r'$10'))   return 10.00;   // Liberty / Indian Head gold eagle
    if (s.contains(r'$5'))    return 5.00;    // Half eagle
    if (s.contains(r'$2.50')) return 2.50;    // Quarter eagle
    if (s.contains(r'$3'))    return 3.00;    // Three-dollar gold piece
    if (s.contains(r'$2'))    return 2.00;    // Two-dollar note / $2 gold
    if (s.contains('dollar')  || s.contains(r'$1')) return 1.00;
    // ── Numeric fallback: "1" → 1.00, "0.25" → 0.25 ─────────────────────────
    // Handles plain-number denominations stored by PCGS import or legacy CSV.
    final n = double.tryParse(s.replaceAll(r'$', '').trim());
    if (n != null) return n;
    return 0.00;
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, outerConstraints) {
        return StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
          stream: FirebaseFirestore.instance
              .collection(AuthService.coinsPath)
              .limit(200)
              .snapshots(),
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(
                  child: CircularProgressIndicator(color: Color(0xFFF63366)));
            }
            if (snapshot.hasError) {
              return Center(
                child: Padding(
                  padding: const EdgeInsets.all(32),
                  child: Column(mainAxisSize: MainAxisSize.min, children: const [
                    Icon(Icons.cloud_off_rounded, size: 48, color: Color(0xFFE53935)),
                    SizedBox(height: 16),
                    Text('Dashboard unavailable',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700,
                            color: Color(0xFF31333F))),
                    SizedBox(height: 8),
                    Text('Check your connection and refresh the page.',
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Color(0xFF5A5C69))),
                  ]),
                ),
              );
            }

            final docs = snapshot.data?.docs ?? <QueryDocumentSnapshot<Map<String, dynamic>>>[];

            // ── Compute portfolio metrics ──────────────────────────────────
            int totalCoins = docs.length;
            double portfolioValue  = 0;
            double acquisitionCost = 0;
            double meltValue       = 0;
            double faceValue       = 0;

            for (final doc in docs) {
              final data = doc.data();
              portfolioValue  += _parseCurrency(data['AI Estimated Value']);
              acquisitionCost += _parseCurrency(data['Cost']);
              // Live melt value: compute from spot prices + Metal Content
              // Falls back to stored Firestore value if spot prices not loaded yet.
              final liveMelt = _spotPrices.isNotEmpty
                  ? (MeltValueService.compute(
                        metalContent: data['Metal Content']?.toString() ?? '',
                        denomination: data['Denomination']?.toString() ?? '',
                        spotPrices: _spotPrices,
                      ) ?? 0.0)
                  : _parseCurrency(data['Melt Value']);
              meltValue       += liveMelt;
              faceValue       += _computeFaceValue(data['Denomination']?.toString() ?? '');
            }

            // ── Last 3 added ───────────────────────────────────────────────
            final sorted = List<QueryDocumentSnapshot<Map<String, dynamic>>>.from(docs);
            sorted.sort((a, b) {
              final ad = a.data();
              final bd = b.data();
              // Check all three timestamp field names used across import methods
              final aTs = ad['Added'] ?? ad['timestamp'] ?? ad['created_at'];
              final bTs = bd['Added'] ?? bd['timestamp'] ?? bd['created_at'];

              final aHas = aTs is Timestamp;
              final bHas = bTs is Timestamp;

              if (aHas && bHas) return bTs.compareTo(aTs); // both: newest first
              // Mixed: the timestamped coin is the newer one — put it first
              if (aHas && !bHas) return -1;   // a has timestamp → a first
              if (!aHas && bHas) return 1;    // b has timestamp → b first
              // Neither: stable fallback by doc ID
              return b.id.compareTo(a.id);
            });
            final last5 = sorted.take(5).toList();

            final fmt = intl.NumberFormat.currency(symbol: '\$');

            return SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // ── Beta banner ──────────────────────────────────────────
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(vertical: 6),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFF7DD),
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(color: const Color(0xFFFFD54F)),
                    ),
                    child: const Text('🚧  BETA TESTING MODE',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                            color: Color(0xFF8B6B00))),
                  ),
                  const SizedBox(height: 20),

                  // ── Header: title + portfolio value ──────────────────────
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      const Flexible(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('DASHBOARD',
                                style: TextStyle(
                                    fontSize: 26,
                                    fontWeight: FontWeight.w900,
                                    fontStyle: FontStyle.italic,
                                    color: Color(0xFF31333F))),
                            Text('AI POWERED COLLECTION MANAGER',
                                style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.w600,
                                    color: Color(0xFF5A5C69))),
                          ],
                        ),
                      ),
                      const SizedBox(width: 12),
                      Flexible(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            const Text('EST. PORTFOLIO VALUE',
                                style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.w600,
                                    color: Color(0xFF5A5C69))),
                            Text(fmt.format(portfolioValue),
                                style: const TextStyle(
                                    fontSize: 28,
                                    fontWeight: FontWeight.w900,
                                    color: Color(0xFF0F9D58))),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),

                   // ── Metric cards ──────────────────────────────────────────
                  LayoutBuilder(builder: (ctx, bc) {
                    final profit = portfolioValue - acquisitionCost;
                    final profitFmt = (profit >= 0 ? '+' : '') + fmt.format(profit);
                    final profitColor = profit >= 0
                        ? const Color(0xFF0F9D58)
                        : const Color(0xFFE53935);
                    final narrow = bc.maxWidth < 480;
                    if (narrow) {
                      return Column(children: [
                        Row(children: [
                          Expanded(child: _metricCard('Total Coins', totalCoins.toString())),
                          const SizedBox(width: 10),
                          Expanded(child: _metricCard('Acq. Cost', fmt.format(acquisitionCost))),
                        ]),
                        const SizedBox(height: 10),
                        Row(children: [
                          Expanded(child: _metricCard('Melt Value', fmt.format(meltValue))),
                          const SizedBox(width: 10),
                          Expanded(child: _metricCard('Face Value', fmt.format(faceValue))),
                        ]),
                        const SizedBox(height: 10),
                        _metricCard('Profit / Loss', profitFmt,
                            valueColor: profitColor),
                      ]);
                    }
                    return Wrap(
                      spacing: 12,
                      runSpacing: 12,
                      children: [
                        _metricCardFlex('Total Coins', totalCoins.toString()),
                        _metricCardFlex('Acquisition Cost', fmt.format(acquisitionCost)),
                        _metricCardFlex('Melt Value', fmt.format(meltValue)),
                        _metricCardFlex('Face Value', fmt.format(faceValue)),
                        _metricCardFlex('Profit / Loss', profitFmt,
                            valueColor: profitColor),
                      ],
                    );
                  }),
                  const SizedBox(height: 24),

                  // ── Recently Added ────────────────────────────────────────
                  const Text('Recently Added',
                      style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF31333F))),
                  const SizedBox(height: 10),
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: const Color(0xFFE2E6E9)),
                    ),
                    child: last5.isEmpty
                        ? const Padding(
                            padding: EdgeInsets.all(16),
                            child: Text('No coins yet — add your first coin!',
                                style: TextStyle(color: Color(0xFF5A5C69))))
                        : Column(
                            children: last5.asMap().entries.map((entry) {
                              final data = entry.value.data();
                              final year   = data['Year']?.toString().replaceAll(RegExp(r'\.0$'), '') ?? '';
                              final mint   = data['Mint Mark']?.toString() ?? '';
                              final denom  = data['Denomination']?.toString() ?? '';
                              final series = data['Program/Series']?.toString() ?? '';
                              final theme  = data['Theme/Subject']?.toString() ?? '';
                              final estVal = data['AI Estimated Value']?.toString() ?? '—';

                              // Build a human-readable coin name
                              // Priority: Program/Series > Theme/Subject > Denomination > fallback
                              final denomFallback = denom.isNotEmpty && denom != 'Multiple'
                                  ? (denom[0].toUpperCase() + denom.substring(1))
                                      .replaceAll(r'$', '')
                                      .trim()
                                  : 'Coin';
                              final coinName = series.isNotEmpty && series != 'Multiple'
                                  ? series
                                  : theme.isNotEmpty && theme != 'Multiple'
                                      ? theme
                                      : denomFallback;

                              // Build year-mint label, normalise "Multiple" to "Various"
                              final yearLabel = (year.isEmpty || year == 'Multiple') ? 'Various' : year;
                              final mintLabel = (mint.isEmpty || mint == 'Multiple') ? '' : '-$mint';
                              // Build denomination label — only prepend '$' if the
                              // value is numeric (e.g. "1" → "$1") or already has it.
                              // Word-form denominations (penny, nickel, dime, quarter) stay as-is.
                              String fmtDenom(String d) {
                                if (d.isEmpty || d == 'Multiple') return '';
                                if (d.startsWith(r'$')) return d;              // already has $
                                final numeric = double.tryParse(
                                    d.replaceAll(RegExp(r'[^\d.]'), ''));
                                if (numeric != null && d.contains(RegExp(r'^[\d]'))) {
                                  return '\$$d';                              // numeric → add $
                                }
                                return d[0].toUpperCase() + d.substring(1);   // word → capitalise
                              }
                              final denomLabel = fmtDenom(denom);
                              final condition = data['Condition']?.toString() ?? '';

                              // When year is known → "2025-W  $1"
                              // When year is Various (sets/lots) → use Theme + Condition to differentiate
                              final String subtitle;
                              if (yearLabel != 'Various') {
                                final parts = [
                                  '$yearLabel$mintLabel',
                                  if (denomLabel.isNotEmpty) denomLabel,
                                ].where((s) => s.isNotEmpty).toList();
                                subtitle = parts.join(' · ');
                              } else {
                                // Year unknown — use theme + condition to distinguish
                                final themeStr = theme.isNotEmpty && theme != 'Multiple' ? theme : '';
                                final condStr = (condition.isNotEmpty && condition != 'Ungraded') ? condition : '';
                                final parts = [
                                  if (themeStr.isNotEmpty) themeStr,
                                  if (condStr.isNotEmpty) condStr,
                                  if (denomLabel.isNotEmpty) denomLabel,
                                ];
                                subtitle = parts.isEmpty ? 'Set / Lot' : parts.join(' · ');
                              }

                              return Column(children: [
                                if (entry.key > 0)
                                  const Divider(height: 1, color: Color(0xFFE2E6E9)),
                                ListTile(
                                  dense: true,
                                  contentPadding: const EdgeInsets.symmetric(
                                      horizontal: 16, vertical: 4),
                                  leading: Container(
                                    width: 36, height: 36,
                                    decoration: BoxDecoration(
                                      color: const Color(0xFFF0F2F6),
                                      borderRadius: BorderRadius.circular(18),
                                    ),
                                    child: const Icon(Icons.toll,
                                        size: 18, color: Color(0xFF5A5C69)),
                                  ),
                                  title: Text(coinName,
                                      overflow: TextOverflow.ellipsis,
                                      style: const TextStyle(
                                          fontSize: 13,
                                          fontWeight: FontWeight.w600,
                                          color: Color(0xFF31333F))),
                                  subtitle: Text(subtitle,
                                      style: const TextStyle(
                                          fontSize: 11,
                                          color: Color(0xFF64748B))),
                                  trailing: Text(estVal,
                                      style: const TextStyle(
                                          fontSize: 13,
                                          fontWeight: FontWeight.w700,
                                          color: Color(0xFF0F9D58))),
                                ),
                              ]);
                            }).toList(),
                          ),
                  ),
                  const SizedBox(height: 16),

                  // ── Morgan Widget ─────────────────────────────────────────
                  _MorganDashboardCard(
                    totalCoins: totalCoins,
                    onAskMorgan: widget.onAskMorgan,
                  ),
                  const SizedBox(height: 24),

                  // ── Live Spot Prices ──────────────────────────────────────
                  Row(children: [
                    const Icon(Icons.show_chart, size: 14, color: Color(0xFF0F9D58)),
                    const SizedBox(width: 6),
                    const Text('LIVE SPOT PRICES',
                        style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF64748B),
                            letterSpacing: 0.5)),
                    const SizedBox(width: 10),
                    if (_pricesLastUpdated != null)
                      Text(
                        'Last updated: ${intl.DateFormat("dd MMM yyyy @ HHmm").format(_pricesLastUpdated!.toLocal())} · Source: metals-api.com',
                        style: const TextStyle(
                            fontSize: 9,
                            color: Color(0xFF94A3B8)),
                      ),
                  ]),
                  const SizedBox(height: 8),
                  if (_isLoadingPrices)
                    const SizedBox(height: 4,
                        child: LinearProgressIndicator(color: Color(0xFF0F9D58)))
                  else if (_spotPrices.isNotEmpty)
                    SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: _spotPrices.entries.map((e) =>
                          Container(
                            margin: const EdgeInsets.only(right: 10),
                            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: const Color(0xFFE2E6E9)),
                              boxShadow: [BoxShadow(
                                  color: Colors.black.withValues(alpha: 0.04),
                                  blurRadius: 4, offset: const Offset(0, 2))],
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(e.key,
                                    style: const TextStyle(
                                        fontSize: 10,
                                        fontWeight: FontWeight.w600,
                                        color: Color(0xFF64748B))),
                                const SizedBox(height: 2),
                                Text(fmt.format(e.value),
                                    style: const TextStyle(
                                        fontSize: 15,
                                        fontWeight: FontWeight.w800,
                                        color: Color(0xFF0F172A))),
                              ],
                            ),
                          ),
                        ).toList(),
                      ),
                    ),
                  const SizedBox(height: 24),

                  // ── System Updates & Release Notes ────────────────────────
                  _ReleaseNotesPanel(),
                  const SizedBox(height: 24),

                  // ── Market Intel / News feed (bottom) ─────────────────────
                  Row(
                    children: [
                      const Icon(Icons.newspaper,
                          size: 15, color: Color(0xFF3B82F6)),
                      const SizedBox(width: 6),
                      const Text('MARKET INTEL',
                          style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF64748B),
                              letterSpacing: 0.5)),
                      const Spacer(),
                      if (!_isLoadingNews)
                        IconButton(
                          icon: const Icon(Icons.refresh,
                              size: 16, color: Color(0xFF94A3B8)),
                          tooltip: 'Refresh news',
                          visualDensity: VisualDensity.compact,
                          onPressed: () {
                            setState(() => _isLoadingNews = true);
                            _fetchNews();
                          },
                        ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  if (_isLoadingNews)
                    const SizedBox(
                      height: 4,
                      child: LinearProgressIndicator(
                          color: Color(0xFF3B82F6)))
                  else if (_news.isEmpty)
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(
                          vertical: 20, horizontal: 16),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF8FAFC),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: const Color(0xFFE2E6E9)),
                      ),
                      child: Column(children: const [
                        Icon(Icons.wifi_off_outlined,
                            size: 28, color: Color(0xFFCBD5E1)),
                        SizedBox(height: 8),
                        Text('Market news unavailable right now — check back shortly.',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                                fontSize: 12, color: Color(0xFF94A3B8))),
                      ]),
                    )
                  else
                    SizedBox(
                      height: 158,
                      child: ListView.builder(
                        scrollDirection: Axis.horizontal,
                        itemCount: _news.length,
                        itemBuilder: (ctx, i) {
                          final item = _news[i] as Map<String, dynamic>;
                          final link = item['link']?.toString() ?? '';
                          return GestureDetector(
                            onTap: link.isNotEmpty
                                ? () async {
                                    final uri = Uri.parse(link);
                                    if (await canLaunchUrl(uri)) {
                                      await launchUrl(uri,
                                          mode: LaunchMode
                                              .externalApplication);
                                    }
                                  }
                                : null,
                            child: MouseRegion(
                              cursor: link.isNotEmpty
                                  ? SystemMouseCursors.click
                                  : MouseCursor.defer,
                              child: Container(
                                width: 270,
                                margin: const EdgeInsets.only(right: 12),
                                padding: const EdgeInsets.all(14),
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(
                                      color: const Color(0xFFE2E6E9)),
                                  boxShadow: [
                                    BoxShadow(
                                      color: Colors.black.withValues(alpha: 0.03),
                                      blurRadius: 4,
                                      offset: const Offset(0, 2),
                                    )
                                  ],
                                ),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(children: [
                                      Expanded(
                                        child: Text(
                                          item['source']?.toString() ?? 'News',
                                          overflow: TextOverflow.ellipsis,
                                          style: const TextStyle(
                                              fontSize: 10,
                                              fontWeight: FontWeight.bold,
                                              color: Color(0xFF3B82F6)),
                                        ),
                                      ),
                                      const SizedBox(width: 4),
                                      Text(
                                        item['published']?.toString() ?? '',
                                        style: const TextStyle(
                                            fontSize: 10,
                                            color: Color(0xFF94A3B8)),
                                      ),
                                    ]),
                                    const SizedBox(height: 5),
                                    Text(
                                      item['title']?.toString() ?? '',
                                      maxLines: 2,
                                      overflow: TextOverflow.ellipsis,
                                      style: const TextStyle(
                                          fontSize: 13,
                                          fontWeight: FontWeight.w700,
                                          color: Color(0xFF1E293B)),
                                    ),
                                    const SizedBox(height: 5),
                                    Expanded(
                                      child: Text(
                                        item['summary']?.toString() ?? '',
                                        maxLines: 3,
                                        overflow: TextOverflow.ellipsis,
                                        style: const TextStyle(
                                            fontSize: 11,
                                            color: Color(0xFF64748B),
                                            height: 1.4),
                                      ),
                                    ),
                                    if (link.isNotEmpty)
                                      Align(
                                        alignment: Alignment.centerRight,
                                        child: Row(
                                          mainAxisSize: MainAxisSize.min,
                                          children: const [
                                            Text('Read more',
                                                style: TextStyle(
                                                    fontSize: 10,
                                                    color: Color(0xFF3B82F6),
                                                    fontWeight: FontWeight.w600)),
                                            SizedBox(width: 2),
                                            Icon(Icons.arrow_forward_ios,
                                                size: 9,
                                                color: Color(0xFF3B82F6)),
                                          ],
                                        ),
                                      ),
                                  ],
                                ),
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  const SizedBox(height: 32),
                ],
              ),
            );
          },
        );
      },
    );
  }

  Widget _metricCard(String label, String value, {Color? valueColor}) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFE2E6E9)),
        boxShadow: [BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 4,
            offset: const Offset(0, 2))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Text(label,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 11, color: Color(0xFF5A5C69))),
          const SizedBox(height: 6),
          FittedBox(
            fit: BoxFit.scaleDown,
            child: Text(value,
                style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w800,
                    color: valueColor ?? const Color(0xFF31333F))),
          ),
        ],
      ),
    );
  }

  /// Fixed-width card for use inside a Wrap row (5-card wide layout).
  Widget _metricCardFlex(String label, String value, {Color? valueColor}) {
    return SizedBox(
      width: 160,
      child: _metricCard(label, value, valueColor: valueColor),
    );
  }
}

// ─── Release Notes Data ────────────────────────────────────────────────────────

class _Release {
  final String version;
  final String date;
  final String description;
  final List<String> changes;
  final bool isLatest;
  final bool isLegacy;

  const _Release({
    required this.version,
    required this.date,
    required this.description,
    required this.changes,
    this.isLatest = false,
    this.isLegacy = false,
  });
}

const _versionHistory = <_Release>[
  _Release(
    version: 'v3.6 Beta',
    date: '2026-06-10',
    description: 'Vertex AI Coin Reference Search',
    isLatest: true,
    changes: [
      'New Coin Search screen: semantic search over 1,913 coin reference entries powered by Vertex AI Search Enterprise tier.',
      'Natural language queries: ask about dates, mint marks, designers, metal content, or coin history.',
      'AI-generated summary banner surfaces key facts above results.',
      'Category filter chips (Circulating, Commemorative, Bullion, Proof) narrow results instantly.',
      'Mint mark chips and draggable detail sheet for every result card.',
      'AI Reference Search button added to My Collection toolbar for quick cross-reference.',
      'GET /api/coin_search open endpoint on Cloud Run — no authentication required (public reference data).',
    ],
  ),
  _Release(
    version: 'v3.5 Beta',
    date: '2026-06-09',
    description: 'Universal Item Routing & Supplies Tracking',
    isLatest: false,
    changes: [
      'Invoice AI now classifies every line item: coins, sets, stamps, currency, medals, and supplies.',
      'Coin sets create a single Set Record in Review Hub — choose Break Up or Keep as Set.',
      'Break Up Set expands a set into individual coins, each inheriting set provenance.',
      'Supplies (binders, pages, capsules) automatically routed to the new Inventory screen.',
      'Stamps and non-numismatic items held in Pending Items for future module support.',
      'Firestore security rules hardened: pending_items, supplies_log, admin_grade_flags, reference_library all covered.',
      'Fixed backend startup crash (Request import NameError in break_up_set endpoint).',
    ],
  ),
  _Release(
    version: 'v3.2 Beta',
    date: '2026-04-25',
    description: 'PCGS Import Wizard',
    isLatest: false,
    changes: [
      'Import graded coins directly from PCGS by certification number.',
      'Paste cert numbers manually or upload a PCGS registry CSV export.',
      'Automatic schema mapping: Year, Mint Mark, Grade, PCGS#, images, and price guide value.',
      'Duplicate detection prevents double-importing slabs.',
      'Bearer token saved to your account — no re-entry needed each session.',
      'API called client-side (Flutter Web) to bypass Cloudflare restrictions.',
    ],
  ),
  _Release(
    version: 'v3.1 Beta',
    date: '2026-04-23',
    description: 'AI Checklist Scanner',
    changes: [
      'Photograph a printed coin checklist — AI reads it and syncs your collection.',
      'Supports all 31 coin programs (Morgan Dollars, State Quarters, Lincoln Cents, etc.).',
      'QTY and notes column now captured from the checklist (e.g. "MS-65", "stored in binder").',
      'Unchecked coins auto-populate your Wish List in one scan.',
      'Page-aware chunking: Gemini processes one page at a time to prevent token overflow.',
      'SDK migrated from vertexai → google-genai ahead of June 24, 2026 shutdown.',
    ],
  ),
  _Release(
    version: 'v3 Beta',
    date: '2026-04-08',
    description: 'Flutter Platform Launch',
    changes: [
      'Rebuilt entire frontend on Flutter for true cross-platform support.',
      'Real-time Firestore streaming on all collection screens.',
      'Hardware agent bridge via Firestore command pattern.',
      'Full collection data grid with sortable columns and inline editing.',
      'Live Microscope Scan screen with sharpness meter and countdown rings.',
      'AI-driven obverse/reverse identification via Gemini.',
      'Enhanced Gemini prompt for precise mint mark detection.',
    ],
  ),
  _Release(
    version: 'v2.7',
    date: '2026-03-07',
    description: 'Improved UI Labels & Professional ID System',
    isLegacy: true,
    changes: [
      'Replaced cryptic hex IDs with professional Year-Mint-Denomination labels.',
      'Enhanced visual scannability for large collections.',
    ],
  ),
  _Release(
    version: 'v2.6',
    date: '2026-02-23',
    description: 'Checklist Logic Fixes & Strict Ingestion Rules',
    isLegacy: true,
    changes: [
      'Fixed Program Checklist matching to avoid false positives.',
      'Added Face Value and Melt Value to Dashboard & Database view.',
    ],
  ),
  _Release(
    version: 'v1.0',
    date: '2026-01-20',
    description: 'Initial Launch of Numista.AI',
    isLegacy: true,
    changes: [
      'Core Collection Management.',
      'AI Scan & Valuation.',
      'Market Data Integration.',
    ],
  ),
];

// ─── Release Notes Panel Widget ───────────────────────────────────────────────

class _ReleaseNotesPanel extends StatelessWidget {
  const _ReleaseNotesPanel();

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: const Color(0xFFE2E6E9)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Theme(
        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          iconColor: const Color(0xFF31333F),
          collapsedIconColor: const Color(0xFF31333F),
          title: const Text('🚀 System Updates & Release Notes',
              style: TextStyle(
                  color: Color(0xFF31333F),
                  fontWeight: FontWeight.w500,
                  fontSize: 14)),
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  'Track the latest features deployed to Numista.AI',
                  style: TextStyle(
                      color: const Color(0xFF5A5C69).withValues(alpha: 0.8),
                      fontSize: 12),
                ),
              ),
            ),
            const Divider(height: 1, indent: 16, endIndent: 16),
            ..._versionHistory.map((r) => _buildEntry(r)),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }

  Widget _buildEntry(_Release r) {
    final vColor = r.isLatest
        ? const Color(0xFF1967D2)
        : r.isLegacy
            ? const Color(0xFF9AA0A6)
            : const Color(0xFF34A853);
    final vBg = r.isLatest
        ? const Color(0xFFE8F0FE)
        : r.isLegacy
            ? const Color(0xFFF1F3F4)
            : const Color(0xFFE6F4EA);

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
            decoration: BoxDecoration(
                color: vBg, borderRadius: BorderRadius.circular(12)),
            child: Text(r.version,
                style: TextStyle(
                    color: vColor,
                    fontWeight: FontWeight.w700,
                    fontSize: 12,
                    letterSpacing: 0.5)),
          ),
          const SizedBox(width: 8),
          Text(r.date,
              style: const TextStyle(color: Color(0xFF9AA0A6), fontSize: 12)),
          if (r.isLatest) ...[
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                  color: const Color(0xFF34A853),
                  borderRadius: BorderRadius.circular(4)),
              child: const Text('LATEST',
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold)),
            ),
          ],
          if (r.isLegacy) ...[
            const SizedBox(width: 8),
            Text('Streamlit',
                style: TextStyle(
                    color: const Color(0xFF9AA0A6).withValues(alpha: 0.7),
                    fontSize: 10,
                    fontStyle: FontStyle.italic)),
          ],
        ]),
        const SizedBox(height: 6),
        Text(r.description,
            style: TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 13,
                color: r.isLegacy
                    ? const Color(0xFF9AA0A6)
                    : const Color(0xFF31333F))),
        const SizedBox(height: 4),
        ...r.changes.map((c) => Padding(
              padding: const EdgeInsets.only(bottom: 3),
              child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text('• ',
                    style: TextStyle(
                        color: r.isLegacy
                            ? const Color(0xFF9AA0A6)
                            : const Color(0xFF5A5C69),
                        fontSize: 13)),
                Expanded(
                    child: Text(c,
                        style: TextStyle(
                            color: r.isLegacy
                                ? const Color(0xFF9AA0A6)
                                : const Color(0xFF5A5C69),
                            fontSize: 13))),
              ]),
            )),
        const SizedBox(height: 12),
        const Divider(height: 1, color: Color(0xFFE2E6E9)),
      ]),
    );
  }
}

// ══════════════════════════════════════════════════════════════════════════════
//  _MorganDashboardCard
//  ────────────────────
//  Contextual "Ask Morgan" card shown on the home dashboard.
//  Shows a personalised greeting, coin count, and one-tap access to Morgan chat.
// ══════════════════════════════════════════════════════════════════════════════
class _MorganDashboardCard extends StatelessWidget {
  final int totalCoins;
  final VoidCallback? onAskMorgan;

  const _MorganDashboardCard({
    required this.totalCoins,
    this.onAskMorgan,
  });

  static const _teal = Color(0xFF2DD4BF);
  static const _gold = Color(0xFFD4A843);
  static const _sub  = Color(0xFF94A3B8);

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<String>(
      future: MorganPrefs.getDisplayName(),
      builder: (context, snap) {
        final name = snap.data ?? '';
        final greeting = name.isNotEmpty ? 'Hi $name! ' : '';
        final coinLine = totalCoins == 0
            ? 'Your collection is ready to grow.'
            : 'I\'ve reviewed your $totalCoins coin${totalCoins == 1 ? '' : 's'}.';

        return Container(
          width: double.infinity,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF0B1220), Color(0xFF112240)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: _gold.withAlpha(60), width: 1.5),
            boxShadow: [
              BoxShadow(
                color: _teal.withAlpha(20),
                blurRadius: 16,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Header row ──────────────────────────────────────────────
                Row(
                  children: [
                    // Morgan avatar
                    Container(
                      width: 48, height: 48,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: const LinearGradient(
                          colors: [Color(0xFFD4A843), Color(0xFF8B6914)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        border: Border.all(color: _gold.withAlpha(120), width: 2),
                      ),
                      child: ClipOval(
                        child: Image.asset(
                          'assets/morgan_avatar.png',
                          fit: BoxFit.cover,
                          errorBuilder: (ctx, err, stack) => const Icon(
                              Icons.smart_toy_rounded,
                              color: Colors.white, size: 24),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Text('Morgan',
                                  style: TextStyle(
                                      color: Colors.white,
                                      fontSize: 15,
                                      fontWeight: FontWeight.bold)),
                              const SizedBox(width: 6),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: _teal.withAlpha(30),
                                  borderRadius: BorderRadius.circular(4),
                                  border: Border.all(
                                      color: _teal.withAlpha(80), width: 1),
                                ),
                                child: const Text('AI Guide',
                                    style: TextStyle(
                                        color: _teal,
                                        fontSize: 9,
                                        fontWeight: FontWeight.w700,
                                        letterSpacing: 0.5)),
                              ),
                            ],
                          ),
                          const SizedBox(height: 2),
                          Text('$greeting$coinLine',
                              style: const TextStyle(
                                  color: _sub, fontSize: 12)),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),

                // ── Suggestion chips ─────────────────────────────────────────
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: [
                      _chip(totalCoins == 0
                          ? 'How do I add my first coin?'
                          : 'What\'s my most valuable coin?'),
                      const SizedBox(width: 8),
                      _chip(totalCoins == 0
                          ? 'What can Morgan help me with?'
                          : 'Give me a collection summary'),
                    ],
                  ),
                ),
                const SizedBox(height: 14),

                // ── Ask Morgan button ────────────────────────────────────────
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: onAskMorgan,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _teal,
                      foregroundColor: Colors.black87,
                      padding: const EdgeInsets.symmetric(vertical: 13),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10)),
                      elevation: 0,
                    ),
                    icon: const Icon(Icons.chat_bubble_rounded, size: 16),
                    label: const Text('Ask Morgan',
                        style: TextStyle(
                            fontWeight: FontWeight.bold, fontSize: 14)),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _chip(String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white.withAlpha(10),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white.withAlpha(30)),
      ),
      child: Text(label,
          style: const TextStyle(color: _sub, fontSize: 11)),
    );
  }
}
