import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:url_launcher/url_launcher.dart';

class PublicWishlistViewScreen extends StatefulWidget {
  final String token;

  const PublicWishlistViewScreen({super.key, required this.token});

  @override
  State<PublicWishlistViewScreen> createState() => _PublicWishlistViewScreenState();
}

class _PublicWishlistViewScreenState extends State<PublicWishlistViewScreen> {
  bool _loading = true;
  String? _error;
  Map<String, dynamic>? _wishlistData;

  @override
  void initState() {
    super.initState();
    _fetchSnapshot();
  }

  Future<void> _fetchSnapshot() async {
    try {
      final doc = await FirebaseFirestore.instance
          .collection('public_wishlists')
          .doc(widget.token)
          .get();

      if (!doc.exists) {
        if (mounted) {
          setState(() {
            _error = "Wish list link not found or expired.";
            _loading = false;
          });
        }
        return;
      }

      if (mounted) {
        setState(() {
          _wishlistData = doc.data();
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = "Unable to load wish list: $e";
          _loading = false;
        });
      }
    }
  }

  Future<void> _openEbaySearch(String query) async {
    final cleanQuery = Uri.encodeComponent(query);
    // EPN Affiliate Link structure targeting campaign 5339148752
    final url = Uri.parse(
      'https://www.ebay.com/sch/i.html?_nkw=$cleanQuery&mkcid=1&mkrid=711-53200-19255-0&siteid=0&campid=5339148752&customid=public_wishlist'
    );
    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0E1117),
      appBar: AppBar(
        backgroundColor: const Color(0xFF161B27),
        title: Row(
          children: [
            const Icon(Icons.card_giftcard, color: Color(0xFF10B981)),
            const SizedBox(width: 10),
            Text(
              _wishlistData?['owner_alias'] != null
                  ? "${_wishlistData!['owner_alias']}'s Wish List"
                  : "Public Wish List",
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_loading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: Color(0xFF10B981)),
            SizedBox(height: 16),
            Text("Loading Wish List...", style: TextStyle(color: Colors.white70)),
          ],
        ),
      );
    }

    if (_error != null) {
      return Center(
        child: Container(
          margin: const EdgeInsets.all(24),
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: const Color(0xFF161B27),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.redAccent.withOpacity(0.5)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline, size: 48, color: Colors.redAccent),
              const SizedBox(height: 16),
              Text(
                _error!,
                style: const TextStyle(color: Colors.white, fontSize: 16),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      );
    }

    final items = List<Map<String, dynamic>>.from(_wishlistData?['items'] ?? []);
    final dateDisplay = _wishlistData?['snapshot_date_display'] ?? "Recent";

    return Column(
      children: [
        // Top Banner
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
          color: const Color(0xFF10B981).withOpacity(0.15),
          child: Row(
            children: [
              const Icon(Icons.info_outline, color: Color(0xFF10B981), size: 20),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  "Read-Only Gift List — Snapshot taken on $dateDisplay",
                  style: const TextStyle(color: Color(0xFF10B981), fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
        ),

        // Items List
        Expanded(
          child: items.isEmpty
              ? const Center(
                  child: Text(
                    "No items currently in this wish list.",
                    style: TextStyle(color: Colors.white54, fontSize: 16),
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: items.length,
                  itemBuilder: (context, index) {
                    final item = items[index];
                    final title = item['title'] ?? item['name'] ?? 'Numismatic Coin Item';
                    final targetGrade = item['target_grade'] ?? item['grade'] ?? 'Any Grade';
                    final maxPrice = item['max_price'] != null ? "\$${item['max_price']}" : "Market";

                    return Card(
                      color: const Color(0xFF161B27),
                      margin: const EdgeInsets.only(bottom: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                        side: const BorderSide(color: Color(0xFF2A3045)),
                      ),
                      child: ListTile(
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        leading: CircleAvatar(
                          backgroundColor: const Color(0xFF10B981).withOpacity(0.2),
                          child: const Icon(Icons.monetization_on, color: Color(0xFF10B981)),
                        ),
                        title: Text(
                          title,
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                        subtitle: Padding(
                          padding: const EdgeInsets.only(top: 4),
                          child: Text(
                            "Target Grade: $targetGrade • Budget: $maxPrice",
                            style: const TextStyle(color: Colors.white70),
                          ),
                        ),
                        trailing: ElevatedButton.icon(
                          onPressed: () => _openEbaySearch("$title $targetGrade"),
                          icon: const Icon(Icons.open_in_new, size: 16),
                          label: const Text("Find on eBay"),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF3B82F6),
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(6),
                            ),
                          ),
                        ),
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }
}
