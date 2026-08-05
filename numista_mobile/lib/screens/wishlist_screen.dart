import 'dart:convert';
import 'package:http/http.dart' as http;
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
import 'deals_screen.dart';

class WishlistScreen extends StatefulWidget {
  const WishlistScreen({super.key});

  @override
  State<WishlistScreen> createState() => _WishlistScreenState();
}

class _WishlistScreenState extends State<WishlistScreen> {
  // ── Auto-wishlist from collection ────────────────────────────────────────
  List<Map<String, dynamic>> _userCoins = [];
  bool _coinsLoaded = false;
  String? _expandedProgramId; // which program card is open

  @override
  void initState() {
    super.initState();
    _loadUserCoins();
  }

  Future<void> _loadUserCoins() async {
    try {
      final snapshot = await FirebaseFirestore.instance
          .collection(AuthService.coinsPath)
          .limit(2000)
          .get();
      if (mounted) {
        setState(() {
          _userCoins = snapshot.docs
              .map((d) => d.data())
              .toList();
          _coinsLoaded = true;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _coinsLoaded = true);
    }
  }

  /// Returns true if a Firestore coin doc belongs to the given program.
  bool _coinBelongsToProgram(Map<String, dynamic> coin, CoinProgram program) {
    final series = (coin['Program/Series']?.toString() ?? '');
    return program.matchesDbSeries(series);
  }

  /// Returns true if the user already owns at least one coin matching [pc] in [program].
  bool _userHasProgramCoin(CoinProgram program, ProgramCoin pc) {
    final pcName = pc.name.toLowerCase();
    return _userCoins.any((c) {
      if (!_coinBelongsToProgram(c, program)) return false;
      final theme = (c['Theme/Subject']?.toString() ?? '').toLowerCase();
      final year  = c['Year']?.toString() ?? '';
      return theme.contains(pcName) ||
             pcName.contains(theme) ||
             (pc.year != null && pc.year!.isNotEmpty && pc.year == year);
    });
  }

  /// Programs where the user has collected ≥1 coin.
  List<CoinProgram> _getTrackedPrograms(Map<String, List<CoinProgram>> allProgramsMap) {
    final result = <CoinProgram>[];
    for (final list in allProgramsMap.values) {
      for (final program in list) {
        if (_userCoins.any((c) => _coinBelongsToProgram(c, program))) {
          result.add(program);
        }
      }
    }
    return result;
  }

  // ── Program Tracker UI ────────────────────────────────────────────────────

  Future<void> _handleShareWishlist(BuildContext context) async {
    try {
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (_) => const Center(child: CircularProgressIndicator(color: Color(0xFF10B981))),
      );

      final userEmail = AuthService.userEmail;
      final items = <Map<String, dynamic>>[];

      // Export missing coins from tracked in-progress programs
      final trackedPrograms = _getTrackedPrograms(CoinProgramsData.usPrograms);
      for (final prog in trackedPrograms) {
        for (final pc in prog.coins) {
          if (!_userHasProgramCoin(prog, pc)) {
            items.add({
              'title': '${prog.name}: ${pc.name}${pc.year != null && pc.year!.isNotEmpty ? " (${pc.year})" : ""}',
              'program_id': prog.id,
              'program_name': prog.name,
              'coin_id': pc.id,
              'coin_name': pc.name,
              'year': pc.year ?? '',
              'target_grade': 'Uncirculated / AU',
              'max_price': 'Market Value',
            });
          }
        }
      }

      if (items.isEmpty) {
        items.add({
          'title': '1921 Morgan Silver Dollar',
          'target_grade': 'MS65',
          'max_price': 'Market',
        });
      }

      final response = await http.post(
        Uri.parse('https://numista-backend-568985927038.us-central1.run.app/api/wishlist/create-share'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_email': userEmail,
          'owner_alias': userEmail.split('@').first,
          'items': items,
        }),
      );

      if (context.mounted) Navigator.pop(context);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final shareUrl = data['share_url'] as String;

        if (context.mounted) {
          showDialog(
            context: context,
            builder: (_) => AlertDialog(
              backgroundColor: const Color(0xFF161B27),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              title: const Row(
                children: [
                  Icon(Icons.share, color: Color(0xFF10B981)),
                  SizedBox(width: 10),
                  Text("Share Wish List", style: TextStyle(color: Colors.white)),
                ],
              ),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text("Your read-only public wish list link is ready:", style: TextStyle(color: Colors.white70)),
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFF0E1117),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: const Color(0xFF2A3045)),
                    ),
                    child: SelectableText(shareUrl, style: const TextStyle(color: Color(0xFF10B981), fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text("Close", style: TextStyle(color: Colors.white54)),
                ),
                ElevatedButton.icon(
                  onPressed: () {
                    Share.share("Check out my Numista.AI coin wish list: $shareUrl");
                  },
                  icon: const Icon(Icons.send, size: 16),
                  label: const Text("Share Link"),
                  style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF10B981)),
                ),
              ],
            ),
          );
        }
      }
    } catch (e) {
      if (context.mounted) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Failed to share wish list: $e")),
        );
      }
    }
  }

  Widget _buildAutoMissingSection(Map<String, List<CoinProgram>> allProgramsMap) {
    if (!_coinsLoaded) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 24),
        child: Center(child: CircularProgressIndicator(color: Color(0xFFF63366))),
      );
    }
    final programs = _getTrackedPrograms(allProgramsMap);
    if (programs.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildGiftActivityBanner(),
        const SizedBox(height: 20),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text('Coin Programs',
                style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w900,
                    color: Color(0xFF1E293B))),
            ElevatedButton.icon(
              onPressed: () => _handleShareWishlist(context),
              icon: const Icon(Icons.share, size: 15),
              label: const Text('Share Wish List'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF10B981),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        const Text(
          'Tap a program to see your full checklist and shop for missing coins.',
          style: TextStyle(color: Color(0xFF64748B), fontSize: 13, height: 1.4),
        ),
        const SizedBox(height: 16),
        ...programs.map((p) => _buildProgramRow(p)),
        const SizedBox(height: 32),
      ],
    );
  }

  Widget _buildProgramRow(CoinProgram program) {
    final isExpanded = _expandedProgramId == program.id;
    final total = program.coins.length;
    final ownedCount =
        program.coins.where((pc) => _userHasProgramCoin(program, pc)).length;
    final missingCount = total - ownedCount;
    final progress = total > 0 ? ownedCount / total : 0.0;

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(7),
            blurRadius: 10,
            offset: const Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        children: [
          // ── Collapsed header ──
          InkWell(
            borderRadius: BorderRadius.vertical(
              top: const Radius.circular(14),
              bottom: isExpanded ? Radius.zero : const Radius.circular(14),
            ),
            onTap: () => setState(() =>
                _expandedProgramId = isExpanded ? null : program.id),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
              child: Row(
                children: [
                  _buildMiniProgress(progress, ownedCount, total),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(program.name,
                            style: const TextStyle(
                                fontWeight: FontWeight.w700,
                                fontSize: 15,
                                color: Color(0xFF1E293B))),
                        const SizedBox(height: 2),
                        Text(
                          missingCount == 0
                              ? 'Complete! All $total coins collected ✓'
                              : '$ownedCount of $total collected · $missingCount missing',
                          style: TextStyle(
                              fontSize: 12,
                              color: missingCount == 0
                                  ? const Color(0xFF22C55E)
                                  : const Color(0xFF64748B)),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 8),
                  Icon(
                    isExpanded ? Icons.keyboard_arrow_up_rounded : Icons.keyboard_arrow_down_rounded,
                    color: const Color(0xFF94A3B8),
                    size: 22,
                  ),
                ],
              ),
            ),
          ),

          // ── Expanded coin list ──
          if (isExpanded) ...[
            const Divider(height: 1, color: Color(0xFFF1F5F9)),
            ...program.coins.asMap().entries.map((entry) {
              final isLast = entry.key == program.coins.length - 1;
              return _buildCoinRow(program, entry.value, isLast: isLast);
            }),
            const SizedBox(height: 4),
          ],
        ],
      ),
    );
  }

  Widget _buildCoinRow(CoinProgram program, ProgramCoin pc, {bool isLast = false}) {
    final isOwned = _userHasProgramCoin(program, pc);
    final query =
        '${program.name} ${pc.name}${pc.year != null && pc.year!.isNotEmpty ? " ${pc.year}" : ""}';
    final url = EpnService.buildSearchUrlFromQuery(query);

    return Container(
      decoration: BoxDecoration(
        color: isOwned ? const Color(0xFFF0FDF4) : Colors.white,
        border: isLast
            ? null
            : const Border(bottom: BorderSide(color: Color(0xFFF1F5F9))),
        borderRadius: isLast
            ? const BorderRadius.vertical(bottom: Radius.circular(14))
            : null,
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 11),
        child: Row(
          children: [
            Icon(
              isOwned ? Icons.check_circle_rounded : Icons.radio_button_unchecked_rounded,
              color: isOwned ? const Color(0xFF22C55E) : const Color(0xFFCBD5E1),
              size: 20,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    pc.name,
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight:
                          isOwned ? FontWeight.w600 : FontWeight.normal,
                      color: isOwned
                          ? const Color(0xFF166534)
                          : const Color(0xFF1E293B),
                    ),
                  ),
                  if (pc.year != null && pc.year!.isNotEmpty)
                    Text(pc.year!,
                        style: const TextStyle(
                            fontSize: 11, color: Color(0xFF94A3B8))),
                ],
              ),
            ),
            if (isOwned)
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: const Color(0xFFDCFCE7),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: const Text('Collected',
                    style: TextStyle(
                        fontSize: 11,
                        color: Color(0xFF16A34A),
                        fontWeight: FontWeight.w600)),
              )
            else
              TextButton.icon(
                onPressed: () async {
                  final uri = Uri.parse(url);
                  if (await canLaunchUrl(uri)) {
                    await launchUrl(uri,
                        mode: LaunchMode.externalApplication);
                  }
                },
                icon: const Icon(Icons.open_in_new_rounded,
                    size: 13, color: Color(0xFFE65100)),
                label: const Text('Buy on eBay',
                    style: TextStyle(
                        fontSize: 12,
                        color: Color(0xFFE65100),
                        fontWeight: FontWeight.w600)),
                style: TextButton.styleFrom(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  minimumSize: Size.zero,
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildMiniProgress(double progress, int owned, int total) {
    return SizedBox(
      width: 44,
      height: 44,
      child: Stack(
        fit: StackFit.expand,
        children: [
          CircularProgressIndicator(
            value: progress,
            strokeWidth: 4,
            backgroundColor: const Color(0xFFF1F5F9),
            valueColor: AlwaysStoppedAnimation<Color>(
              progress >= 1.0
                  ? const Color(0xFF22C55E)
                  : const Color(0xFF3B82F6),
            ),
          ),
          Center(
            child: Text(
              '${(progress * 100).toInt()}%',
              style: const TextStyle(
                  fontSize: 9,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1E293B)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildArbitrageDealsCard(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardBg = isDark ? const Color(0xFF1E293B) : Colors.white;
    final headerColor = isDark ? Colors.white : const Color(0xFF31333F);
    final descColor = isDark ? const Color(0xFF94A3B8) : const Color(0xFF64748B);
    final borderColor = isDark ? const Color(0xFF374151) : const Color(0xFFE2E6E9);

    return Container(
      margin: const EdgeInsets.only(bottom: 24),
      decoration: BoxDecoration(
        color: cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(15),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const DealsScreen()),
            );
          },
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: const Color(0xFF0F9D58).withAlpha(20),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.shopping_bag_outlined,
                      color: Color(0xFF0F9D58), size: 24),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            'Wishlist Deal Spotter',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: headerColor,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: const Color(0xFF0F9D58).withValues(alpha: 0.15),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Text(
                              '2 Active Deals',
                              style: TextStyle(color: Color(0xFF0F9D58), fontSize: 11, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '1881-S Morgan & 1909-S VDB listed 22% below wholesale bid',
                        style: TextStyle(fontSize: 12, color: descColor),
                      ),
                    ],
                  ),
                ),
                const Icon(Icons.chevron_right, color: Color(0xFFF63366)),
              ],
            ),
          ),
        ),
      ),
    );
  }

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
              final items = snapshot.data ?? [];
              final individualItems = items.where((i) => i.type == 'individual').toList();
              final programs = items.where((i) => i.type == 'program').toList();
              final trackedPrograms = _getTrackedPrograms(allProgramsMap);

              if (items.isEmpty && trackedPrograms.isEmpty && _coinsLoaded) {
                return _buildEmptyState();
              }

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
                              _buildArbitrageDealsCard(context),
                              _buildAutoMissingSection(allProgramsMap),
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
                        _buildArbitrageDealsCard(context),
                        _buildAutoMissingSection(allProgramsMap),
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
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 80, height: 80,
              decoration: BoxDecoration(
                color: const Color(0xFFF63366).withAlpha(20),
                shape: BoxShape.circle,
              ),
              child: Icon(Icons.favorite_border_rounded,
                  size: 44, color: const Color(0xFFF63366).withAlpha(200)),
            ),
            const SizedBox(height: 20),
            const Text('Your Wish List is Empty',
                style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: Colors.white)),
            const SizedBox(height: 8),
            const Text(
              'Tap ♥ Wish List on any coin in\nMy Collection to save it here.',
              textAlign: TextAlign.center,
              style: TextStyle(
                  color: Color(0xFF94A3B8), fontSize: 14, height: 1.5),
            ),
            const SizedBox(height: 6),
            const Text(
              'Or browse Programs to track full sets.',
              textAlign: TextAlign.center,
              style: TextStyle(color: Color(0xFF64748B), fontSize: 13),
            ),
          ],
        ),
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
            subtitle: Text('${coin.country} • ${coin.condition}${coin.purchaseCost != '\$0.00' && coin.purchaseCost.isNotEmpty ? ' • Target: ${coin.purchaseCost}' : ''}'),
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
    final url = await EpnService.generateSearchUrl(coin, soldOnly: false);
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

  Widget _buildGiftActivityBanner() {
    final userEmail = AuthService.userEmail;
    if (userEmail.isEmpty) return const SizedBox.shrink();

    return StreamBuilder<QuerySnapshot>(
      stream: FirebaseFirestore.instance
          .collection('public_wishlists')
          .where('owner_email', isEqualTo: userEmail)
          .snapshots(),
      builder: (context, snapshot) {
        if (!snapshot.hasData || snapshot.data!.docs.isEmpty) {
          return _buildBannerCard(0, []);
        }

        final doc = snapshot.data!.docs.first.data() as Map<String, dynamic>;
        final reservedIndices = List<int>.from(doc['reserved_items'] ?? []);
        final detailsMap = Map<String, dynamic>.from(doc['reservation_details'] ?? {});
        final items = List<Map<String, dynamic>>.from(doc['items'] ?? []);

        final reservedCount = reservedIndices.length;
        final reservedDetailsList = <Map<String, String>>[];

        for (var idx in reservedIndices) {
          final title = idx < items.length ? (items[idx]['title'] ?? 'Coin Item') : 'Wishlist Item';
          final detail = detailsMap[idx.toString()] as Map<String, dynamic>?;
          final by = detail?['reserved_by'] ?? 'Family Member';
          reservedDetailsList.add({
            'title': title,
            'reserved_by': by,
          });
        }

        return _buildBannerCard(reservedCount, reservedDetailsList);
      },
    );
  }

  Widget _buildBannerCard(int reservedCount, List<Map<String, String>> details) {
    final isReserved = reservedCount > 0;
    return Container(
      decoration: BoxDecoration(
        color: isReserved ? const Color(0xFF064E3B) : const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isReserved ? const Color(0xFF10B981) : const Color(0xFF334155),
        ),
      ),
      child: ExpansionTile(
        tilePadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        leading: Icon(
          isReserved ? Icons.card_giftcard : Icons.card_giftcard_outlined,
          color: isReserved ? const Color(0xFF34D399) : Colors.white54,
        ),
        title: Text(
          isReserved
              ? "🎁 $reservedCount Wish List Items Reserved by Relatives ✓"
              : "🎁 0 items currently reserved by family members",
          style: TextStyle(
            color: isReserved ? Colors.white : Colors.white70,
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
        ),
        subtitle: Text(
          isReserved
              ? "Tap to view gift items family members marked as bought"
              : "Share your gift list to let family members reserve items for holidays",
          style: const TextStyle(color: Colors.white54, fontSize: 11),
        ),
        children: details.isEmpty
            ? []
            : details.map((d) => ListTile(
                  dense: true,
                  leading: const Icon(Icons.check_circle_outline, color: Color(0xFF34D399), size: 18),
                  title: Text(d['title']!, style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600)),
                  subtitle: Text("Reserved by ${d['reserved_by']}", style: const TextStyle(color: Color(0xFF34D399), fontSize: 11)),
                )).toList(),
      ),
    );
  }
}
