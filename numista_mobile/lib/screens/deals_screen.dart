import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:url_launcher/url_launcher.dart';
import 'package:intl/intl.dart' as intl;
import '../constants.dart';

class DealsScreen extends StatefulWidget {
  const DealsScreen({super.key});

  @override
  State<DealsScreen> createState() => _DealsScreenState();
}

class _DealsScreenState extends State<DealsScreen> {
  bool _loading = true;
  String? _error;
  List<dynamic> _deals = [];
  final _dollarFmt = intl.NumberFormat.currency(symbol: '\$', decimalDigits: 2);

  @override
  void initState() {
    super.initState();
    _fetchDeals();
  }

  Future<void> _fetchDeals() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final response = await http.get(Uri.parse('$kApiBaseUrl/api/greysheet/deals'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        if (mounted) {
          setState(() {
            _deals = data['deals'] ?? [];
            _loading = false;
          });
        }
      } else {
        throw Exception('Failed to fetch deals from server (code: ${response.statusCode})');
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  Future<void> _triggerRefresh() async {
    setState(() {
      _loading = true;
    });
    try {
      final response = await http.post(Uri.parse('$kApiBaseUrl/api/greysheet/deals/refresh'));
      if (response.statusCode == 200) {
        await _fetchDeals();
      } else {
        throw Exception('Failed to refresh deals');
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString();
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final headerColor = isDark ? Colors.white : const Color(0xFF31333F);
    final cardBg = isDark ? const Color(0xFF1E293B) : Colors.white;
    final descColor = isDark ? const Color(0xFF94A3B8) : const Color(0xFF64748B);
    final borderColor = isDark ? const Color(0xFF374151) : const Color(0xFFE2E6E9);

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text('Arbitrage Deal Spotter', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: headerColor,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Scan for new deals',
            onPressed: _triggerRefresh,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFFF63366)))
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisAlignment: MainAxisSize.center,
                      children: [
                        const Icon(Icons.error_outline, size: 48, color: Colors.red),
                        const SizedBox(height: 16),
                        Text('Error loading deals: $_error', textAlign: TextAlign.center),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _fetchDeals,
                          style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFF63366)),
                          child: const Text('Try Again'),
                        ),
                      ],
                    ),
                  ),
                )
              : _deals.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.shopping_bag_outlined, size: 64, color: Colors.grey),
                          const SizedBox(height: 16),
                          Text('No arbitrage opportunities detected.', style: TextStyle(color: descColor)),
                          const SizedBox(height: 8),
                          ElevatedButton.icon(
                            icon: const Icon(Icons.search),
                            label: const Text('Scan Listings Now'),
                            onPressed: _triggerRefresh,
                            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFF63366)),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _deals.length,
                      itemBuilder: (ctx, idx) {
                        final deal = _deals[idx];
                        final price = (deal['price'] as num?)?.toDouble() ?? 0.0;
                        final bid = (deal['greysheet_bid'] as num?)?.toDouble() ?? 0.0;
                        final margin = (deal['net_margin'] as num?)?.toDouble() ?? 0.0;
                        final marginPct = (deal['margin_percent'] as num?)?.toDouble() ?? 0.0;

                        return Container(
                          margin: const EdgeInsets.bottom(16),
                          decoration: BoxDecoration(
                            color: cardBg,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(color: borderColor),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withAlpha(10),
                                blurRadius: 10,
                                offset: const Offset(0, 4),
                              ),
                            ],
                          ),
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                      decoration: BoxDecoration(
                                        color: const Color(0xFF0F9D58).withAlpha(20),
                                        borderRadius: BorderRadius.circular(20),
                                      ),
                                      child: Row(
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          const Icon(Icons.trending_up, color: Color(0xFF0F9D58), size: 14),
                                          const SizedBox(width: 4),
                                          Text(
                                            '+${marginPct.toStringAsFixed(1)}% Arbitrage',
                                            style: const TextStyle(
                                              fontSize: 12,
                                              fontWeight: FontWeight.bold,
                                              color: Color(0xFF0F9D58),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                    Text(
                                      'Spread: ${_dollarFmt.format(margin)}',
                                      style: const TextStyle(
                                        fontSize: 13,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 12),
                                Text(
                                  deal['title'] ?? 'Coin Listing',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.w700,
                                    color: headerColor,
                                  ),
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                const SizedBox(height: 14),
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text('Listing Price', style: TextStyle(fontSize: 12, color: descColor)),
                                        const SizedBox(height: 2),
                                        Text(_dollarFmt.format(price), style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                                      ],
                                    ),
                                    Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text('Greysheet Bid', style: TextStyle(fontSize: 12, color: descColor)),
                                        const SizedBox(height: 2),
                                        Text(_dollarFmt.format(bid), style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF4C8CDA))),
                                      ],
                                    ),
                                    ElevatedButton(
                                      onPressed: () async {
                                        final url = Uri.parse(deal['url'] ?? '');
                                        if (await canLaunchUrl(url)) {
                                          await launchUrl(url, mode: LaunchMode.externalApplication);
                                        }
                                      },
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: const Color(0xFFF63366),
                                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                                      ),
                                      child: const Text('View Deal'),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
    );
  }
}
