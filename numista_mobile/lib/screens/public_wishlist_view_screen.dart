import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/epn_service.dart';

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
  Set<int> _reservedIndices = {};

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

      final data = doc.data();
      final reservedList = List<int>.from(data?['reserved_items'] ?? []);

      if (mounted) {
        setState(() {
          _wishlistData = data;
          _reservedIndices = reservedList.toSet();
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

  Future<void> _toggleReservation(int index, {String? buyerName}) async {
    final isReserved = _reservedIndices.contains(index);
    setState(() {
      if (isReserved) {
        _reservedIndices.remove(index);
      } else {
        _reservedIndices.add(index);
      }
    });

    try {
      final docRef = FirebaseFirestore.instance.collection('public_wishlists').doc(widget.token);
      final payload = <String, dynamic>{
        'reserved_items': _reservedIndices.toList(),
      };
      if (!isReserved && buyerName != null && buyerName.isNotEmpty) {
        payload['reservation_details.${index}'] = {
          'reserved_by': buyerName,
          'reserved_at': DateTime.now().toIso8601String(),
        };
      }
      await docRef.update(payload);
    } catch (e) {
      debugPrint('Error toggling reservation: $e');
    }
  }

  void _showReservationDialog(int index, bool currentlyReserved) {
    if (currentlyReserved) {
      // Toggle off directly if already reserved
      _toggleReservation(index);
      return;
    }

    final nameController = TextEditingController();
    showDialog(
      context: context,
      builder: (dctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        title: const Row(
          children: [
            Icon(Icons.card_giftcard, color: Color(0xFF10B981)),
            SizedBox(width: 10),
            Text("Reserve Gift", style: TextStyle(color: Colors.white)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "Mark this item as reserved to prevent duplicate gift purchases by other family members.",
              style: TextStyle(color: Colors.white70, fontSize: 13),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: nameController,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                labelText: "Your Name (Optional)",
                labelStyle: const TextStyle(color: Colors.white54),
                hintText: "e.g. Aunt Sarah",
                hintStyle: const TextStyle(color: Colors.white30),
                filled: true,
                fillColor: const Color(0xFF0F172A),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dctx),
            child: const Text("Cancel", style: TextStyle(color: Colors.white54)),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(dctx);
              _toggleReservation(index, buyerName: nameController.text.trim());
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF10B981),
              foregroundColor: Colors.white,
            ),
            child: const Text("Confirm Reservation ✓"),
          ),
        ],
      ),
    );
  }

  Future<void> _openEbaySearch(String query, {double? estimatedValue, String? programId}) async {
    final ownerEmail = _wishlistData?['owner_email'] ?? 'guest';
    final userHash = ownerEmail.split('@').first;
    final customId = '${userHash}_${programId ?? "gift_list"}';

    final urlString = EpnService.buildSearchUrlFromQuery(
      query,
      estimatedValue: estimatedValue,
      customId: customId,
    );

    final url = Uri.parse(urlString);
    if (await canLaunchUrl(url)) {
      await launchUrl(url, mode: LaunchMode.externalApplication);
    }
  }

  @override
  Widget build(BuildContext context) {
    final alias = _wishlistData?['owner_alias'] ?? "Numista Collector";
    return Scaffold(
      backgroundColor: const Color(0xFF0E1117),
      appBar: AppBar(
        backgroundColor: const Color(0xFF161B27),
        elevation: 0,
        title: Row(
          children: [
            const Icon(Icons.card_giftcard, color: Color(0xFF10B981)),
            const SizedBox(width: 10),
            Text("$alias's Wish List", style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
          ],
        ),
      ),
      body: _buildBody(alias),
    );
  }

  Widget _buildBody(String alias) {
    if (_loading) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: Color(0xFF10B981)),
            SizedBox(height: 16),
            Text("Loading Gift Wish List...", style: TextStyle(color: Colors.white70)),
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
            border: Border.all(color: Colors.redAccent.withAlpha(120)),
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

    return LayoutBuilder(
      builder: (context, constraints) {
        final isDesktop = constraints.maxWidth >= 900;
        final horizontalPadding = isDesktop ? 48.0 : 16.0;

        return SingleChildScrollView(
          padding: EdgeInsets.symmetric(horizontal: horizontalPadding, vertical: 20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Top Banner
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF10B981).withAlpha(30),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF10B981).withAlpha(80)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.stars_rounded, color: Color(0xFF10B981), size: 28),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "Gift List for $alias",
                            style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            "Snapshot updated on $dateDisplay • Tap 'Find on eBay' to view verified listings.",
                            style: const TextStyle(color: Color(0xFF10B981), fontSize: 13),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Buyer Safety Warning Box
              _buildBuyerSafetyBox(),

              const SizedBox(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    "Missing Coins & Wanted Items",
                    style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  Text(
                    "${items.length} items total",
                    style: const TextStyle(color: Colors.white54, fontSize: 13),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Items Grid / List
              if (items.isEmpty)
                const Center(
                  child: Padding(
                    padding: EdgeInsets.all(40),
                    child: Text(
                      "No items currently in this wish list.",
                      style: TextStyle(color: Colors.white54, fontSize: 16),
                    ),
                  ),
                )
              else if (isDesktop)
                GridView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                    crossAxisCount: 2,
                    crossAxisSpacing: 16,
                    mainAxisSpacing: 16,
                    childAspectRatio: 2.2,
                  ),
                  itemCount: items.length,
                  itemBuilder: (context, index) => _buildGiftCard(items[index], index),
                )
              else
                ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: items.length,
                  itemBuilder: (context, index) => _buildGiftCard(items[index], index),
                ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildBuyerSafetyBox() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFF59E0B).withAlpha(100)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.shield_outlined, color: Color(0xFFF59E0B), size: 24),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  "🛡️ Numista Safety Tips for Gift Buyers",
                  style: TextStyle(color: Color(0xFFF59E0B), fontSize: 14, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                const Text(
                  "• Prefer eBay sellers with 99%+ positive feedback and 100+ sales.\n"
                  "• For items over \$200, links automatically search for PCGS or NGC slabbed/certified coins.\n"
                  "• Check listing photos carefully to ensure they are actual coin photos, not stock images.",
                  style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12, height: 1.5),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGiftCard(Map<String, dynamic> item, int index) {
    final title = item['title'] ?? item['name'] ?? 'Numismatic Coin Item';
    final targetGrade = item['target_grade'] ?? item['grade'] ?? 'Any Grade';
    final maxPrice = item['max_price'] != null ? "\$${item['max_price']}" : "Market";
    final programId = item['program_id'] as String?;
    final estimatedValue = item['estimated_value'] != null ? (item['estimated_value'] as num).toDouble() : null;

    final isReserved = _reservedIndices.contains(index);

    return Card(
      color: isReserved ? const Color(0xFF16231C) : const Color(0xFF161B27),
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: isReserved ? const Color(0xFF10B981) : const Color(0xFF2A3045),
          width: isReserved ? 1.5 : 1.0,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            CircleAvatar(
              backgroundColor: isReserved
                  ? const Color(0xFF10B981).withAlpha(40)
                  : const Color(0xFF3B82F6).withAlpha(40),
              radius: 22,
              child: Icon(
                isReserved ? Icons.check_circle : Icons.monetization_on_outlined,
                color: isReserved ? const Color(0xFF10B981) : const Color(0xFF3B82F6),
              ),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      color: isReserved ? const Color(0xFF10B981) : Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    "Target Grade: $targetGrade • Est. Budget: $maxPrice",
                    style: const TextStyle(color: Colors.white70, fontSize: 12),
                  ),
                  if (isReserved)
                    const Padding(
                      padding: EdgeInsets.only(top: 4),
                      child: Text(
                        "✓ Marked as Gifted / Reserved",
                        style: TextStyle(color: Color(0xFF10B981), fontSize: 11, fontWeight: FontWeight.w600),
                      ),
                    ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton.icon(
                  onPressed: isReserved
                      ? null
                      : () => _openEbaySearch("$title $targetGrade", estimatedValue: estimatedValue, programId: programId),
                  icon: Icon(isReserved ? Icons.check_circle : Icons.open_in_new, size: 14),
                  label: Text(
                    isReserved ? "Reserved ✓" : "Find on eBay",
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: isReserved ? Colors.grey.withAlpha(50) : const Color(0xFF3B82F6),
                    foregroundColor: isReserved ? Colors.white38 : Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                ),
                const SizedBox(height: 6),
                OutlinedButton(
                  onPressed: () => _showReservationDialog(index, isReserved),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    minimumSize: Size.zero,
                    tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    side: BorderSide(color: isReserved ? const Color(0xFF10B981) : Colors.white38),
                  ),
                  child: Text(
                    isReserved ? "Reserved ✓" : "I Bought This",
                    style: TextStyle(
                      fontSize: 10,
                      color: isReserved ? const Color(0xFF10B981) : Colors.white70,
                    ),
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
