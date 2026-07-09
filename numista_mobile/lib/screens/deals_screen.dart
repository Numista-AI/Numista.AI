import 'package:flutter/material.dart';
import '../services/wishlist_service.dart';
import '../services/epn_service.dart';
import '../models/coin_model.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:intl/intl.dart' as intl;

class DealsScreen extends StatefulWidget {
  const DealsScreen({super.key});

  @override
  State<DealsScreen> createState() => _DealsScreenState();
}

class _DealsScreenState extends State<DealsScreen> {
  bool _loading = true;
  String? _error;
  List<Map<String, dynamic>> _matchedDeals = [];
  final _dollarFmt = intl.NumberFormat.currency(symbol: '\$', decimalDigits: 2);

  @override
  void initState() {
    super.initState();
    _scanWishlistDeals();
  }

  Future<void> _scanWishlistDeals() async {
    setState(() {
      _loading = true;
      _error = null;
      _matchedDeals = [];
    });

    try {
      // 1. Fetch wishlist items
      final Stream<List<WishlistItem>> stream = WishlistService.getWishlistStream();
      final List<WishlistItem> wishlist = await stream.first;

      final List<Map<String, dynamic>> deals = [];

      // 2. Loop through each wishlist coin and query eBay Browse API
      for (final item in wishlist) {
        final coin = item.coin;
        if (coin == null) continue;

        // Fetch active listings on eBay
        final results = await EpnService.fetchEbayResults(coin);

        for (final itemSummary in results) {
          final priceVal = itemSummary['price']?['value']?.toString() ?? '0.0';
          final price = double.tryParse(priceVal) ?? 0.0;
          if (price <= 0.0) continue;

          // Greysheet Bid benchmark
          final bid = coin.greysheetBid > 0 ? coin.greysheetBid : 40.0; // fallback default
          
          // Flag as highly competitive if listing is near or below Greysheet Bid (or within 15% range)
          if (price <= (bid * 1.15)) {
            final margin = bid - price;
            final marginPct = price > 0 ? (margin / price * 100) : 0.0;
            
            // Build EPN affiliate link
            final affiliateUrl = await EpnService.generateSearchUrl(coin, soldOnly: false);

            deals.add({
              'coin': coin,
              'title': itemSummary['title'] ?? '${coin.year} ${coin.denomination}',
              'price': price,
              'greysheet_bid': bid,
              'net_margin': margin,
              'margin_percent': marginPct,
              'url': affiliateUrl,
              'imageUrl': itemSummary['image']?['imageUrl']?.toString() ?? '',
            });
          }
        }
      }

      // Sort by best arbitrage/margin percentage first
      deals.sort((a, b) => (b['margin_percent'] as double).compareTo(a['margin_percent'] as double));

      if (mounted) {
        setState(() {
          _matchedDeals = deals;
          _loading = false;
        });
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
        title: const Text('Wishlist Deals & Matches', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        foregroundColor: headerColor,
        actions: [
          IconButton(
            icon: const Icon(Icons.sync),
            tooltip: 'Re-scan wishlist listings',
            onPressed: _scanWishlistDeals,
          ),
        ],
      ),
      body: _loading
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(color: Color(0xFFF63366)),
                  SizedBox(height: 16),
                  Text('Scanning eBay Partner Network for wishlist items...', style: TextStyle(color: Colors.grey)),
                ],
              ),
            )
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.error_outline, size: 48, color: Colors.red),
                        const SizedBox(height: 16),
                        Text('Error scanning deals: $_error', textAlign: TextAlign.center),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: _scanWishlistDeals,
                          style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFF63366)),
                          child: const Text('Try Again'),
                        ),
                      ],
                    ),
                  ),
                )
              : _matchedDeals.isEmpty
                  ? Center(
                      child: Padding(
                        padding: const EdgeInsets.all(32.0),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.favorite_border, size: 64, color: Colors.grey),
                            const SizedBox(height: 16),
                            Text(
                              'No deals matching your wishlist coins are currently active.',
                              style: TextStyle(color: descColor, fontSize: 14),
                              textAlign: TextAlign.center,
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Add slabbed coins to your Wishlist to scan live eBay listings automatically!',
                              style: TextStyle(color: descColor.withValues(alpha: 0.7), fontSize: 11),
                              textAlign: TextAlign.center,
                            ),
                            const SizedBox(height: 20),
                            ElevatedButton.icon(
                              icon: const Icon(Icons.search),
                              label: const Text('Scan Listings Now'),
                              onPressed: _scanWishlistDeals,
                              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFF63366)),
                            ),
                          ],
                        ),
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _matchedDeals.length,
                      itemBuilder: (ctx, idx) {
                        final deal = _matchedDeals[idx];
                        final coin = deal['coin'] as CoinModel;
                        final price = deal['price'] as double;
                        final bid = deal['greysheet_bid'] as double;
                        final marginPct = deal['margin_percent'] as double;
                        final imageUrl = deal['imageUrl'] as String;

                        return Container(
                          margin: const EdgeInsets.only(bottom: 16),
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
                                        color: marginPct >= 0
                                            ? const Color(0xFF0F9D58).withAlpha(20)
                                            : const Color(0xFFF59E0B).withAlpha(20),
                                        borderRadius: BorderRadius.circular(20),
                                      ),
                                      child: Row(
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          Icon(
                                            marginPct >= 0 ? Icons.trending_up : Icons.label_important_outline,
                                            color: marginPct >= 0 ? const Color(0xFF0F9D58) : const Color(0xFFF59E0B),
                                            size: 14,
                                          ),
                                          const SizedBox(width: 4),
                                          Text(
                                            marginPct >= 0
                                                ? 'Below Bid (-${marginPct.toStringAsFixed(1)}%)'
                                                : 'Competitive Match',
                                            style: TextStyle(
                                              fontSize: 11,
                                              fontWeight: FontWeight.bold,
                                              color: marginPct >= 0 ? const Color(0xFF0F9D58) : const Color(0xFFF59E0B),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                    Text(
                                      'Wishlist Match',
                                      style: TextStyle(
                                        fontSize: 11,
                                        fontWeight: FontWeight.w600,
                                        color: descColor,
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 12),
                                Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    if (imageUrl.isNotEmpty) ...[
                                      ClipRRect(
                                        borderRadius: BorderRadius.circular(8),
                                        child: Image.network(
                                          imageUrl,
                                          width: 60,
                                          height: 60,
                                          fit: BoxFit.cover,
                                          errorBuilder: (context, error, stackTrace) => Container(
                                            width: 60,
                                            height: 60,
                                            color: borderColor,
                                            child: const Icon(Icons.image_not_supported, size: 20),
                                          ),
                                        ),
                                      ),
                                      const SizedBox(width: 12),
                                    ],
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            deal['title'],
                                            style: TextStyle(
                                              fontSize: 15,
                                              fontWeight: FontWeight.bold,
                                              color: headerColor,
                                            ),
                                            maxLines: 2,
                                            overflow: TextOverflow.ellipsis,
                                          ),
                                          const SizedBox(height: 4),
                                          Text(
                                            'Target Coin: ${coin.year} ${coin.mintMark} ${coin.denomination}',
                                            style: TextStyle(fontSize: 12, color: descColor),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 14),
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text('Listed Price', style: TextStyle(fontSize: 11, color: descColor)),
                                        const SizedBox(height: 2),
                                        Text(_dollarFmt.format(price), style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                                      ],
                                    ),
                                    Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text('Greysheet Bid', style: TextStyle(fontSize: 11, color: descColor)),
                                        const SizedBox(height: 2),
                                        Text(_dollarFmt.format(bid), style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF4C8CDA))),
                                      ],
                                    ),
                                    ElevatedButton(
                                      onPressed: () async {
                                        final url = Uri.parse(deal['url']);
                                        if (await canLaunchUrl(url)) {
                                          await launchUrl(url, mode: LaunchMode.externalApplication);
                                        }
                                      },
                                      style: ElevatedButton.styleFrom(
                                        backgroundColor: const Color(0xFFF63366),
                                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                                      ),
                                      child: const Text('Shop eBay'),
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
