import 'package:flutter/material.dart';
import 'package:share_plus/share_plus.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/wishlist_service.dart';
import '../services/epn_service.dart';
import '../services/coin_programs_data.dart';
import '../services/reference_service.dart';
import '../services/reference_seed_service.dart';
import '../services/auth_service.dart';
import '../models/coin_model.dart';
import '../models/program_model.dart';
import '../widgets/common/ref_image_widget.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

class WishlistScreen extends StatefulWidget {
  const WishlistScreen({super.key});

  @override
  State<WishlistScreen> createState() => _WishlistScreenState();
}

class _WishlistScreenState extends State<WishlistScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F2F6),
      appBar: AppBar(
        title: const Text('My Wishlist', style: TextStyle(fontWeight: FontWeight.w900, color: Color(0xFF31333F))),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.share, color: Color(0xFFF63366)),
            onPressed: _shareWishlist,
            tooltip: 'Share Gift List',
          ),
          IconButton(
            icon: const Icon(Icons.cloud_upload_outlined, color: Color(0xFF64748B)),
            onPressed: () async {
              final messenger = ScaffoldMessenger.of(context);
              await ReferenceSeedService.seedGlobalPrograms();
              if (mounted) {
                messenger.showSnackBar(
                  const SnackBar(content: Text('Expert Reference Library Migrated to Cloud')),
                );
              }
            },
            tooltip: 'Professional Migration',
          ),
        ],
      ),
      body: StreamBuilder<Map<String, List<CoinProgram>>>(
        stream: ReferenceService.getGroupedProgramsStream(),
        builder: (context, refSnapshot) {
          final allProgramsMap = refSnapshot.data ?? CoinProgramsData.usPrograms;
          
          return StreamBuilder<List<WishlistItem>>(
            stream: WishlistService.getWishlistStream(),
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              }
              if (!snapshot.hasData || snapshot.data!.isEmpty) {
                return _buildEmptyState();
              }

              final items = snapshot.data!;
              final individualItems = items.where((i) => i.type == 'individual').toList();
              final programs = items.where((i) => i.type == 'program').toList();

              return LayoutBuilder(
                builder: (context, constraints) {
                  if (constraints.maxWidth > 900) {
                    // PREMIUM WEB LAYOUT: Two columns
                    return Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(
                          flex: 2,
                          child: ListView(
                            padding: const EdgeInsets.all(24),
                            children: [
                              if (programs.isNotEmpty) ...[
                                const Text('Collector Programs', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: Color(0xFF1E293B))),
                                const SizedBox(height: 24),
                                ...programs.map((item) => _buildExpertProgramCard(item, allProgramsMap)),
                              ],
                            ],
                          ),
                        ),
                        const VerticalDivider(width: 1),
                        Expanded(
                          flex: 1,
                          child: ListView(
                            padding: const EdgeInsets.all(24),
                            children: [
                              if (individualItems.isNotEmpty) ...[
                                const Text('Watchlist Specimens', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF1E293B))),
                                const SizedBox(height: 16),
                                ...individualItems.map(_buildIndividualCard),
                              ],
                            ],
                          ),
                        ),
                      ],
                    );
                  } else {
                    // MOBILE LAYOUT: Single column
                    return ListView(
                      padding: const EdgeInsets.all(24),
                      children: [
                        if (programs.isNotEmpty) ...[
                          const Text('Collector Programs', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF1E293B))),
                          const SizedBox(height: 16),
                          ...programs.map((item) => _buildExpertProgramCard(item, allProgramsMap)),
                          const SizedBox(height: 32),
                        ],
                        if (individualItems.isNotEmpty) ...[
                          const Text('Individual Specimens', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF1E293B))),
                          const SizedBox(height: 16),
                          ...individualItems.map(_buildIndividualCard),
                        ],
                      ],
                    );
                  }
                },
              );
            },
          );
        },
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.favorite_border, size: 64, color: Colors.grey.withAlpha(100)),
          const SizedBox(height: 16),
          const Text('Your Wish List is empty', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF1E293B))),
          const SizedBox(height: 8),
          const Text(
            'Tap \u2665 Wish List on any coin in\nMy Collection to add it here.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Color(0xFF64748B), fontSize: 14),
          ),
          const SizedBox(height: 8),
          const Text(
            'Or browse Programs to track full sets.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Color(0xFF64748B), fontSize: 13),
          ),
        ],
      ),
    );
  }

  Widget _buildExpertProgramCard(WishlistItem item, Map<String, List<CoinProgram>> allProgramsMap) {
    CoinProgram? program;
    for (var list in allProgramsMap.values) {
      for (var p in list) {
        if (p.id == item.programId) {
          program = p;
          break;
        }
      }
    }

    if (program == null) return const SizedBox.shrink();

    final activeProgram = program; // Promotion for null-safety inside closures

    // Expertise Progress Calculation
    int totalVarieties = 0;
    int foundTotal = 0;
    for (var coin in program.coins) {
      totalVarieties += coin.varieties.length;
      foundTotal += (item.foundVarieties[coin.id]?.length ?? 0);
    }
    
    final progress = totalVarieties > 0 ? foundTotal / totalVarieties : 0.0;

    return Container(
      margin: const EdgeInsets.only(bottom: 24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(10),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF63366).withAlpha(20),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.stars, color: Color(0xFFF63366)),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(program.name, style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 18, color: Color(0xFF31333F))),
                      const SizedBox(height: 4),
                      Text('$foundTotal of $totalVarieties varieties found', style: const TextStyle(color: Color(0xFF64748B))),
                    ],
                  ),
                ),
                _buildProgressDonut(progress),
              ],
            ),
          ),
          const Divider(height: 1),
          // Scrollable List of Coins (Sub-checklist)
          ConstrainedBox(
            constraints: const BoxConstraints(maxHeight: 400),
            child: ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: program.coins.length,
              separatorBuilder: (context, index) => const Divider(height: 1, indent: 20, endIndent: 20),
              itemBuilder: (context, index) {
                final coin = activeProgram.coins[index];
                final coinFoundVarieties = item.foundVarieties[coin.id] ?? [];
                final isYearComplete = coinFoundVarieties.length == coin.varieties.length;

                return ExpansionTile(
                  key: PageStorageKey(coin.id),
                  leading: isYearComplete 
                    ? const Icon(Icons.check_circle, color: Color(0xFF00C853))
                    : const Icon(Icons.circle_outlined, color: Colors.grey),
                  title: Text(coin.name, style: TextStyle(
                    fontWeight: isYearComplete ? FontWeight.bold : FontWeight.normal,
                    color: const Color(0xFF1E293B)
                  )),
                  subtitle: Text('${coinFoundVarieties.length}/${coin.varieties.length} varieties', style: const TextStyle(fontSize: 12)),
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                      color: const Color(0xFFF8FAFC),
                      child: GridView.builder(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 3,
                          childAspectRatio: 2.2,
                          crossAxisSpacing: 8,
                          mainAxisSpacing: 8,
                        ),
                        itemCount: coin.varieties.length,
                        itemBuilder: (context, vIndex) {
                          final v = coin.varieties[vIndex];
                          final isVFound = coinFoundVarieties.contains(v.id);
                          
                          return Container(
                            decoration: BoxDecoration(
                              color: isVFound ? const Color(0xFF00C853).withAlpha(20) : Colors.white,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(
                                color: isVFound ? const Color(0xFF00C853) : Colors.grey.withAlpha(50),
                              ),
                            ),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                RefImageWidget(
                                  variety: v,
                                  programCoin: coin,
                                  width: 14,
                                  height: 14,
                                  shape: BoxShape.circle,
                                ),
                                const SizedBox(width: 4),
                                Text(v.id, style: TextStyle(
                                  fontSize: 10, 
                                  fontWeight: FontWeight.bold,
                                  color: isVFound ? const Color(0xFF00C853) : const Color(0xFF64748B)
                                )),
                                if (isVFound) ...[
                                  const SizedBox(width: 2),
                                  const Icon(Icons.check_circle, size: 8, color: Color(0xFF00C853)),
                                ],
                              ],
                            ),
                          );
                        },
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
          const SizedBox(height: 12),
        ],
      ),
    );
  }

  Widget _buildProgressDonut(double percent) {
    return Container(
      width: 48,
      height: 48,
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: const Color(0xFFF1F5F9),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Stack(
        fit: StackFit.expand,
        children: [
          CircularProgressIndicator(
            value: percent,
            strokeWidth: 4,
            backgroundColor: Colors.white,
            color: const Color(0xFFF63366),
          ),
          Center(
            child: Text('${(percent * 100).toInt()}%', style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  Widget _buildIndividualCard(WishlistItem item) {
    final coin = item.coin!;
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Column(
        children: [
          ListTile(
            contentPadding: const EdgeInsets.all(16),
            title: Text('${coin.year} ${coin.denomination}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            subtitle: Text('${coin.country} • ${coin.condition}'),
            trailing: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                IconButton(
                  icon: const Icon(Icons.shopping_cart_outlined, color: Color(0xFFF63366)),
                  onPressed: () => _launchEbaySearch(coin),
                  tooltip: 'Search eBay',
                ),
                IconButton(
                  icon: const Icon(Icons.delete_outline, color: Colors.grey),
                  onPressed: () => _confirmRemove(item),
                  tooltip: 'Remove from Wish List',
                ),
              ],
            ),
          ),
          // "I Found It!" action row
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
            child: SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                icon: const Icon(Icons.check_circle_outline, size: 16),
                label: const Text('I Found It! → Add to Collection'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF22C55E),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  padding: const EdgeInsets.symmetric(vertical: 10),
                ),
                onPressed: () => _onFoundIt(item),
              ),
            ),
          ),
          FutureBuilder<List<Map<String, dynamic>>>(
            future: EpnService.fetchEbayResults(coin),
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Padding(
                  padding: EdgeInsets.symmetric(vertical: 8),
                  child: Center(child: SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2))),
                );
              }
              if (!snapshot.hasData || snapshot.data!.isEmpty) {
                return const SizedBox.shrink();
              }
              final results = snapshot.data!;
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 16),
                    child: Text('Live Listings on eBay:', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF64748B))),
                  ),
                  SizedBox(
                    height: 120,
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      padding: const EdgeInsets.all(12),
                      itemCount: results.length,
                      itemBuilder: (context, index) {
                        final res = results[index];
                        final img = res['image']?['imageUrl'] ?? res['thumbnailImages']?[0]?['imageUrl'] ?? '';
                        final price = '${res['price']['currency']} ${res['price']['value']}';
                        return GestureDetector(
                          onTap: () async {
                            final settings = await EpnService.getSettings();
                            final mkrid = settings['rotationId'] ?? '711-53200-19255-0';
                            final campId = settings['campaignId'] ?? '';
                            final url = '${res['itemWebUrl']}&mkevt=1&mkcid=1&mkrid=$mkrid&campid=$campId&toolid=10001';
                            if (await canLaunchUrl(Uri.parse(url))) { await launchUrl(Uri.parse(url)); }
                          },
                          child: Container(
                            width: 100,
                            margin: const EdgeInsets.only(right: 12),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              border: Border.all(color: Colors.grey.withAlpha(50)),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Column(
                              children: [
                                Expanded(
                                  child: ClipRRect(
                                    borderRadius: const BorderRadius.vertical(top: Radius.circular(8)),
                                    child: img.isNotEmpty
                                      ? Image.network(img, fit: BoxFit.cover, width: double.infinity)
                                      : const Icon(Icons.image_not_supported, size: 20),
                                  ),
                                ),
                                Padding(
                                  padding: const EdgeInsets.symmetric(vertical: 4),
                                  child: Text(price, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF00C853))),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                ],
              );
            },
          ),
        ],
      ),
    );
  }

  /// Confirm remove dialog.
  void _confirmRemove(WishlistItem item) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Remove from Wish List?'),
        content: Text('${item.coin?.year ?? ''} ${item.coin?.denomination ?? ''} will be removed.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () { Navigator.pop(context); WishlistService.removeFromWishlist(item.id); },
            child: const Text('Remove', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  /// "I Found It!" — prompts for condition, then moves coin to collection and removes from wish list.
  Future<void> _onFoundIt(WishlistItem item) async {
    if (item.coin == null) return;
    String condition = 'Circulated';
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setSt) => AlertDialog(
          title: const Text('Add to My Collection'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('${item.coin!.year} ${item.coin!.denomination}', style: const TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                initialValue: condition,
                decoration: const InputDecoration(labelText: 'Condition', border: OutlineInputBorder()),
                items: ['Poor','Good','Fine','Very Fine','Extremely Fine','About Unc.','MS-60','MS-63','MS-65','MS-67','Proof','Circulated','Uncirculated']
                  .map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
                onChanged: (v) => setSt(() => condition = v ?? condition),
              ),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF22C55E)),
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('Add to Collection', style: TextStyle(color: Colors.white)),
            ),
          ],
        ),
      ),
    );
    if (confirmed != true || !mounted) return;
    try {
      final coin = item.coin!;
      final email = AuthService.userEmail;
      await FirebaseFirestore.instance
        .collection('users').doc(email).collection('coins')
        .add({
          ...coin.toFirestore(),
          'Condition': condition,
          'source': 'wish_list_found',
          'added_at': DateTime.now().toIso8601String(),
        });
      await WishlistService.removeFromWishlist(item.id);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('\u2705 Moved to My Collection!'),
        backgroundColor: Color(0xFF22C55E),
      ));
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Couldn\'t move coin to collection. Please try again.'),
        backgroundColor: Colors.red));
    }
  }

  Future<void> _launchEbaySearch(CoinModel coin) async {
    final url = await EpnService.generateSearchUrl(coin);
    if (await canLaunchUrl(Uri.parse(url))) {
      await launchUrl(Uri.parse(url));
    }
  }


  void _shareWishlist() {
    // Dynamically generate the share text from the current stream snapshot.
    // We read it once synchronously from the last known state.
    WishlistService.getWishlistStream().first.then((items) {
      final buffer = StringBuffer('My Numista.AI Coin Wish List:\n\n');
      for (final item in items) {
        if (item.type == 'individual' && item.coin != null) {
          buffer.writeln('• ${item.coin!.year} ${item.coin!.denomination} (${item.coin!.mintMark.isEmpty ? 'P' : item.coin!.mintMark}-mint)');
        } else if (item.type == 'program' && item.programId != null) {
          buffer.writeln('• Program: ${item.programId}');
        }
      }
      buffer.writeln('\nTracked with Numista.AI — the smart coin collection app.');
      Share.share(buffer.toString(), subject: 'My Coin Wish List');
    });
  }
}
