import 'dart:async';
import 'package:flutter/material.dart';
import '../services/coin_search_service.dart';
import '../services/wishlist_service.dart';
import '../services/epn_service.dart';
import '../models/coin_model.dart';
import 'package:url_launcher/url_launcher.dart';


/// Full-screen Vertex AI-powered coin reference library search.
///
/// Route name: 'Coin Search'
/// Features:
///   - Debounced live search as the user types
///   - AI-generated summary banner above results
///   - Animated result cards with mint mark chips
///   - Category filter chips (Circulating, Commemorative, etc.)
///   - Pagination (Load More)
///   - Empty state with suggested queries
class CoinSearchScreen extends StatefulWidget {
  /// Pre-populate the search bar when navigating from another screen.
  final String? initialQuery;
  const CoinSearchScreen({super.key, this.initialQuery});

  @override
  State<CoinSearchScreen> createState() => _CoinSearchScreenState();
}

class _CoinSearchScreenState extends State<CoinSearchScreen>
    with SingleTickerProviderStateMixin {
  final TextEditingController _ctrl = TextEditingController();
  final ScrollController _scroll = ScrollController();
  late final AnimationController _fadeCtrl;
  late final Animation<double> _fadeAnim;

  Timer? _debounce;
  bool _loading = false;
  bool _loadingMore = false;
  CoinSearchResponse? _response;
  String _activeCategory = 'All';

  // Pagination
  static const int _pageSize = 10;
  int _offset = 0;
  bool _hasMore = false;

  static const List<String> _categories = [
    'All',
    'Circulating',
    'Commemorative',
    'Bullion',
    'Proof',
  ];

  static const List<String> _suggestions = [
    'Morgan silver dollar Carson City',
    'Walking Liberty half dollar',
    'Buffalo nickel 1913',
    'Lincoln wheat cent',
    'Sacagawea golden dollar',
    'American Silver Eagle',
    'Mercury dime',
    'Saint-Gaudens double eagle',
  ];

  @override
  void initState() {
    super.initState();
    _fadeCtrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 350));
    _fadeAnim =
        CurvedAnimation(parent: _fadeCtrl, curve: Curves.easeOut);

    if (widget.initialQuery != null && widget.initialQuery!.isNotEmpty) {
      _ctrl.text = widget.initialQuery!;
      WidgetsBinding.instance.addPostFrameCallback((_) => _doSearch());
    }
  }

  @override
  void dispose() {
    _debounce?.cancel();
    _ctrl.dispose();
    _scroll.dispose();
    _fadeCtrl.dispose();
    super.dispose();
  }

  // ── Search logic ──────────────────────────────────────────────────────────

  void _onQueryChanged(String value) {
    _debounce?.cancel();
    if (value.trim().isEmpty) {
      setState(() {
        _response = null;
        _loading = false;
      });
      return;
    }
    _debounce = Timer(const Duration(milliseconds: 480), _doSearch);
  }

  Future<void> _doSearch({bool append = false}) async {
    final q = _ctrl.text.trim();
    if (q.isEmpty) return;

    setState(() {
      if (append) {
        _loadingMore = true;
      } else {
        _loading = true;
        _offset = 0;
      }
    });

    final resp = await CoinSearchService.search(
      query: q,
      pageSize: _pageSize,
      offset: _offset,
    );

    if (!mounted) return;
    setState(() {
      _loading = false;
      _loadingMore = false;
      if (append && _response != null) {
        // Merge results
        _response = CoinSearchResponse(
          query:   resp.query,
          total:   resp.total,
          offset:  resp.offset,
          results: [..._response!.results, ...resp.results],
          summary: _response!.summary.isNotEmpty
              ? _response!.summary
              : resp.summary,
          error:   resp.error,
        );
      } else {
        _response = resp;
      }
      _hasMore = (_response!.results.length < resp.total) &&
          resp.results.length == _pageSize;
    });

    if (!append) {
      _fadeCtrl.forward(from: 0);
    }
  }

  Future<void> _loadMore() async {
    if (_loadingMore || !_hasMore) return;
    _offset += _pageSize;
    await _doSearch(append: true);
  }

  // ── UI helpers ────────────────────────────────────────────────────────────

  List<CoinSearchResult> get _filteredResults {
    if (_response == null) return [];
    if (_activeCategory == 'All') return _response!.results;
    return _response!.results
        .where((r) =>
            r.category.toLowerCase().contains(_activeCategory.toLowerCase()))
        .toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0E1117),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0E1117),
        elevation: 0,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [Color(0xFFF63366), Color(0xFFFF6B9D)],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.search, color: Colors.white, size: 16),
            ),
            const SizedBox(width: 10),
            const Text(
              'Coin Reference Search',
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 12, top: 8, bottom: 8),
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: const Color(0xFF1A1D27),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFFF63366).withAlpha(60)),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.auto_awesome,
                    color: Color(0xFFF63366), size: 12),
                const SizedBox(width: 4),
                Text(
                  'Powered by Vertex AI',
                  style: TextStyle(
                      color: Colors.white.withAlpha(180),
                      fontSize: 10,
                      fontWeight: FontWeight.w500),
                ),
              ],
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          // ── Search bar ──────────────────────────────────────────────────
          _SearchBar(controller: _ctrl, onChanged: _onQueryChanged),

          // ── Category filter chips ───────────────────────────────────────
          if (_response != null && _response!.results.isNotEmpty)
            _CategoryChips(
              categories: _categories,
              active: _activeCategory,
              onSelect: (c) => setState(() => _activeCategory = c),
            ),

          // ── Body ────────────────────────────────────────────────────────
          Expanded(
            child: _loading
                ? const _LoadingShimmer()
                : _response == null
                    ? _SuggestionsPane(
                        suggestions: _suggestions,
                        onTap: (s) {
                          _ctrl.text = s;
                          _doSearch();
                        },
                      )
                    : _response!.error != null &&
                            _response!.results.isEmpty
                        ? _ErrorPane(message: _response!.error!)
                        : _ResultsPane(
                            response: _response!,
                            results: _filteredResults,
                            hasMore: _hasMore,
                            loadingMore: _loadingMore,
                            fadeAnim: _fadeAnim,
                            onLoadMore: _loadMore,
                          ),
          ),
        ],
      ),
    );
  }
}

// ─── Search Bar ───────────────────────────────────────────────────────────────

class _SearchBar extends StatelessWidget {
  final TextEditingController controller;
  final ValueChanged<String> onChanged;
  const _SearchBar({required this.controller, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 0, 16, 12),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1D27),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.white.withAlpha(20)),
        boxShadow: [
          BoxShadow(
              color: const Color(0xFFF63366).withAlpha(25),
              blurRadius: 12,
              offset: const Offset(0, 2)),
        ],
      ),
      child: TextField(
        controller: controller,
        onChanged: onChanged,
        autofocus: false,
        style: const TextStyle(color: Colors.white, fontSize: 15),
        decoration: InputDecoration(
          hintText: 'Search coins, series, years, mint marks…',
          hintStyle: TextStyle(color: Colors.white.withAlpha(60), fontSize: 14),
          prefixIcon: const Icon(Icons.search, color: Color(0xFFF63366), size: 20),
          suffixIcon: ValueListenableBuilder<TextEditingValue>(
            valueListenable: controller,
            builder: (context, val, child) => val.text.isNotEmpty
                ? IconButton(
                    icon: Icon(Icons.close,
                        color: Colors.white.withAlpha(100), size: 18),
                    onPressed: () {
                      controller.clear();
                      onChanged('');
                    },
                  )
                : const SizedBox.shrink(),
          ),
          border: InputBorder.none,
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        ),
      ),
    );
  }
}

// ─── Category Chips ───────────────────────────────────────────────────────────

class _CategoryChips extends StatelessWidget {
  final List<String> categories;
  final String active;
  final ValueChanged<String> onSelect;
  const _CategoryChips(
      {required this.categories,
      required this.active,
      required this.onSelect});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 36,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: categories.length,
        separatorBuilder: (context, idx) => const SizedBox(width: 8),
        itemBuilder: (context, i) {
          final cat = categories[i];
          final isActive = cat == active;
          return AnimatedContainer(
            duration: const Duration(milliseconds: 180),
            child: FilterChip(
              label: Text(cat,
                  style: TextStyle(
                      fontSize: 12,
                      color: isActive ? Colors.white : Colors.white54,
                      fontWeight: isActive
                          ? FontWeight.w600
                          : FontWeight.normal)),
              selected: isActive,
              onSelected: (_) => onSelect(cat),
              backgroundColor: const Color(0xFF1A1D27),
              selectedColor: const Color(0xFFF63366).withAlpha(200),
              checkmarkColor: Colors.white,
              side: BorderSide(
                  color: isActive
                      ? const Color(0xFFF63366)
                      : Colors.white.withAlpha(20)),
              padding:
                  const EdgeInsets.symmetric(horizontal: 8, vertical: 0),
            ),
          );
        },
      ),
    );
  }
}

// ─── Results Pane ─────────────────────────────────────────────────────────────

class _ResultsPane extends StatelessWidget {
  final CoinSearchResponse response;
  final List<CoinSearchResult> results;
  final bool hasMore;
  final bool loadingMore;
  final Animation<double> fadeAnim;
  final VoidCallback onLoadMore;

  const _ResultsPane({
    required this.response,
    required this.results,
    required this.hasMore,
    required this.loadingMore,
    required this.fadeAnim,
    required this.onLoadMore,
  });

  @override
  Widget build(BuildContext context) {
    if (results.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search_off, color: Colors.white.withAlpha(60), size: 48),
            const SizedBox(height: 12),
            Text(
              'No results for "${response.query}"',
              style: TextStyle(color: Colors.white.withAlpha(120), fontSize: 14),
            ),
            const SizedBox(height: 6),
            Text(
              'Try a different search term or remove filters.',
              style: TextStyle(color: Colors.white.withAlpha(60), fontSize: 12),
            ),
          ],
        ),
      );
    }

    return FadeTransition(
      opacity: fadeAnim,
      child: ListView.builder(
        padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
        itemCount: results.length +
            (response.summary.isNotEmpty ? 1 : 0) +
            (hasMore ? 1 : 0),
        itemBuilder: (context, index) {
          // AI Summary banner at the top
          if (response.summary.isNotEmpty && index == 0) {
            return _AISummaryBanner(summary: response.summary);
          }

          final resultIndex =
              index - (response.summary.isNotEmpty ? 1 : 0);

          // Load More button at the bottom
          if (resultIndex == results.length) {
            return Padding(
              padding: const EdgeInsets.only(top: 16),
              child: loadingMore
                  ? const Center(
                      child: SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Color(0xFFF63366))))
                  : OutlinedButton(
                      onPressed: onLoadMore,
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.white70,
                        side: BorderSide(
                            color: Colors.white.withAlpha(30)),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10)),
                      ),
                      child: const Text('Load More Results'),
                    ),
            );
          }

          return _CoinResultCard(
            result: results[resultIndex],
            index: resultIndex,
          );
        },
      ),
    );
  }
}

// ─── AI Summary Banner ────────────────────────────────────────────────────────

class _AISummaryBanner extends StatelessWidget {
  final String summary;
  const _AISummaryBanner({required this.summary});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            const Color(0xFF1A1D27),
            const Color(0xFF0B3D6E).withAlpha(80),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF2DD4BF).withAlpha(60)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: const Color(0xFF2DD4BF).withAlpha(30),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.auto_awesome,
                color: Color(0xFF2DD4BF), size: 14),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              summary,
              style: TextStyle(
                  color: Colors.white.withAlpha(200),
                  fontSize: 13,
                  height: 1.45),
            ),
          ),
        ],
      ),
    );
  }
}

// ─── Individual Coin Result Card ──────────────────────────────────────────────

class _CoinResultCard extends StatelessWidget {
  final CoinSearchResult result;
  final int index;
  const _CoinResultCard({required this.result, required this.index});

  @override
  Widget build(BuildContext context) {
    final mints = result.mintMarks
        .split(',')
        .map((s) => s.trim())
        .where((s) => s.isNotEmpty)
        .toList();

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1D27),
        borderRadius: BorderRadius.circular(12),
        border:
            Border.all(color: Colors.white.withAlpha(12)),
        boxShadow: [
          BoxShadow(
              color: Colors.black.withAlpha(60),
              blurRadius: 6,
              offset: const Offset(0, 2)),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(12),
        child: InkWell(
          borderRadius: BorderRadius.circular(12),
          onTap: () => _showDetail(context),
          hoverColor: Colors.white.withAlpha(8),
          splashColor: const Color(0xFFF63366).withAlpha(20),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Index badge
                Container(
                  width: 28,
                  height: 28,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: const Color(0xFFF63366).withAlpha(30),
                    border: Border.all(
                        color: const Color(0xFFF63366).withAlpha(80),
                        width: 1),
                  ),
                  child: Center(
                    child: Text(
                      '${index + 1}',
                      style: const TextStyle(
                          color: Color(0xFFF63366),
                          fontSize: 11,
                          fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Title
                      Text(
                        result.displayTitle,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          height: 1.3,
                        ),
                      ),
                      const SizedBox(height: 3),
                      // Subtitle
                      if (result.displaySubtitle.isNotEmpty)
                        Text(
                          result.displaySubtitle,
                          style: TextStyle(
                              color: Colors.white.withAlpha(120),
                              fontSize: 12),
                        ),
                      // Snippet
                      if (result.snippet.isNotEmpty) ...[
                        const SizedBox(height: 6),
                        Text(
                          result.snippet,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                              color: Colors.white.withAlpha(100),
                              fontSize: 11,
                              height: 1.4),
                        ),
                      ],
                      // Mint mark chips
                      if (mints.isNotEmpty) ...[
                        const SizedBox(height: 8),
                        Wrap(
                          spacing: 6,
                          runSpacing: 4,
                          children: mints
                              .take(6)
                              .map((m) => _MintChip(label: m))
                              .toList(),
                        ),
                      ],
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    if (result.category.isNotEmpty) ...[
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 7, vertical: 3),
                        decoration: BoxDecoration(
                          color: _categoryColor(result.category).withAlpha(40),
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(
                              color: _categoryColor(result.category).withAlpha(80)),
                        ),
                        child: Text(
                          result.category,
                          style: TextStyle(
                              color: _categoryColor(result.category),
                              fontSize: 9,
                              fontWeight: FontWeight.w600),
                        ),
                      ),
                      const SizedBox(height: 8),
                    ],
                    if (result.isOwned)
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFF22C55E).withAlpha(20),
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(color: const Color(0xFF22C55E).withAlpha(50)),
                        ),
                        child: const Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.check_circle, color: Color(0xFF22C55E), size: 12),
                            SizedBox(width: 4),
                            Text(
                              'Owned',
                              style: TextStyle(color: Color(0xFF22C55E), fontSize: 9, fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      )
                    else
                      IconButton(
                        icon: const Icon(Icons.add_circle_outline, color: Color(0xFFF63366), size: 22),
                        padding: EdgeInsets.zero,
                        constraints: const BoxConstraints(),
                        onPressed: () => _addToWishlistWithEbay(context),
                      ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Color _categoryColor(String cat) {
    switch (cat.toLowerCase()) {
      case 'circulating':
        return const Color(0xFF2DD4BF);
      case 'commemorative':
        return const Color(0xFFFFD700);
      case 'bullion':
        return const Color(0xFFC0C0C0);
      case 'proof':
        return const Color(0xFFAB47BC);
      default:
        return const Color(0xFF90CAF9);
    }
  }

  void _showDetail(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => _CoinDetailSheet(result: result),
    );
  }

  void _addToWishlistWithEbay(BuildContext context) {
    showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (dialogCtx) => _AddToWishlistDialog(result: result),
    ).then((added) {
      if (added == true && context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✅ Added ${result.displayTitle} to your Wish List!'),
            backgroundColor: const Color(0xFF00C853),
          ),
        );
      }
    });
  }
}

class _AddToWishlistDialog extends StatefulWidget {
  final CoinSearchResult result;
  const _AddToWishlistDialog({required this.result});

  @override
  State<_AddToWishlistDialog> createState() => _AddToWishlistDialogState();
}

class _AddToWishlistDialogState extends State<_AddToWishlistDialog> {
  bool _loading = true;
  List<Map<String, dynamic>> _ebayResults = [];
  final TextEditingController _priceCtrl = TextEditingController(text: '\$0.00');
  String? _error;

  @override
  void initState() {
    super.initState();
    _fetchPrices();
  }

  @override
  void dispose() {
    _priceCtrl.dispose();
    super.dispose();
  }

  Future<void> _fetchPrices() async {
    try {
      final coin = CoinModel(
        id: widget.result.id,
        year: widget.result.coinYear,
        mintMark: widget.result.mintMarks,
        denomination: widget.result.denomination,
        programSeries: widget.result.programName,
        variety: widget.result.coinName,
        personalNotes: widget.result.notes,
      );

      final results = await EpnService.fetchEbayResults(coin);
      if (!mounted) return;

      double sum = 0;
      int count = 0;
      for (final res in results) {
        final priceMap = res['price'] as Map<String, dynamic>?;
        if (priceMap != null) {
          final valStr = priceMap['value']?.toString() ?? '';
          final val = double.tryParse(valStr);
          if (val != null) {
            sum += val;
            count++;
          }
        }
      }

      setState(() {
        _ebayResults = results;
        _loading = false;
        if (count > 0) {
          final avg = sum / count;
          _priceCtrl.text = '\$${avg.toStringAsFixed(2)}';
        }
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = e.toString();
      });
    }
  }

  Future<void> _save() async {
    final targetPrice = _priceCtrl.text.trim();
    final coin = CoinModel(
      id: widget.result.id,
      year: widget.result.coinYear,
      mintMark: widget.result.mintMarks,
      denomination: widget.result.denomination,
      programSeries: widget.result.programName,
      variety: widget.result.coinName,
      personalNotes: widget.result.notes,
      purchaseCost: targetPrice.isNotEmpty ? targetPrice : '\$0.00',
    );

    try {
      await WishlistService.addToWishlist(coin);
      if (!mounted) return;
      Navigator.pop(context, true);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to add to wishlist: $e'), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: const Color(0xFF1E293B),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: const Text(
        'Add to Wish List',
        style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
      ),
      content: SizedBox(
        width: 320,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                widget.result.displayTitle,
                style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
              ),
              if (widget.result.displaySubtitle.isNotEmpty) ...[
                const SizedBox(height: 4),
                Text(
                  widget.result.displaySubtitle,
                  style: const TextStyle(color: Colors.white70, fontSize: 12),
                ),
              ],
              const SizedBox(height: 16),
              const Text(
                'Target Price',
                style: TextStyle(color: Colors.white70, fontSize: 13, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 6),
              TextField(
                controller: _priceCtrl,
                style: const TextStyle(color: Colors.white),
                decoration: InputDecoration(
                  fillColor: const Color(0xFF0F172A),
                  filled: true,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                  hintText: '\$0.00',
                  hintStyle: const TextStyle(color: Colors.white30),
                ),
              ),
              const SizedBox(height: 16),
              if (_loading) ...[
                const Center(
                  child: Padding(
                    padding: EdgeInsets.symmetric(vertical: 16),
                    child: CircularProgressIndicator(color: Color(0xFFF63366)),
                  ),
                ),
                const Center(
                  child: Text(
                    'Fetching live eBay market value...',
                    style: TextStyle(color: Colors.white70, fontSize: 12),
                  ),
                ),
              ] else if (_error != null) ...[
                Text(
                  'Error fetching eBay prices: $_error',
                  style: const TextStyle(color: Colors.redAccent, fontSize: 12),
                ),
              ] else if (_ebayResults.isEmpty) ...[
                const Text(
                  'No active listings found on eBay. Target price defaulted.',
                  style: TextStyle(color: Colors.white54, fontSize: 12, fontStyle: FontStyle.italic),
                ),
              ] else ...[
                const Text(
                  'Live Reference Listings on eBay:',
                  style: TextStyle(color: Color(0xFF2DD4BF), fontSize: 12, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                SizedBox(
                  height: 90,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    itemCount: _ebayResults.length,
                    itemBuilder: (context, idx) {
                      final item = _ebayResults[idx];
                      final img = item['image']?['imageUrl'] ?? item['thumbnailImages']?[0]?['imageUrl'] ?? '';
                      final price = '${item['price']['currency']} ${item['price']['value']}';
                      return GestureDetector(
                        onTap: () async {
                          final settings = await EpnService.getSettings();
                          final mkrid = settings['rotationId'] ?? '711-53200-19255-0';
                          final campId = settings['campaignId'] ?? '';
                          final url = '${item['itemWebUrl']}&mkevt=1&mkcid=1&mkrid=$mkrid&campid=$campId&toolid=10001';
                          if (await canLaunchUrl(Uri.parse(url))) { await launchUrl(Uri.parse(url)); }
                        },
                        child: Container(
                          width: 80,
                          margin: const EdgeInsets.only(right: 8),
                          decoration: BoxDecoration(
                            color: const Color(0xFF0F172A),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.white10),
                          ),
                          child: Column(
                            children: [
                              Expanded(
                                child: ClipRRect(
                                  borderRadius: const BorderRadius.vertical(top: Radius.circular(8)),
                                  child: img.isNotEmpty
                                      ? Image.network(img, fit: BoxFit.cover, width: double.infinity)
                                      : const Icon(Icons.image_not_supported, size: 20, color: Colors.white24),
                                ),
                              ),
                              Padding(
                                padding: const EdgeInsets.symmetric(vertical: 4),
                                child: Text(
                                  price,
                                  style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF00C853)),
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context, false),
          child: const Text('Cancel', style: TextStyle(color: Colors.white70)),
        ),
        ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFFF63366),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          ),
          onPressed: _save,
          child: const Text('Add to Wish List', style: TextStyle(color: Colors.white)),
        ),
      ],
    );
  }
}

// ─── Mint Mark Chip ───────────────────────────────────────────────────────────

class _MintChip extends StatelessWidget {
  final String label;
  const _MintChip({required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: Colors.white.withAlpha(12),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: Colors.white.withAlpha(30)),
      ),
      child: Text(
        label,
        style: TextStyle(
            color: Colors.white.withAlpha(160),
            fontSize: 10,
            fontWeight: FontWeight.w500),
      ),
    );
  }
}

// ─── Detail Bottom Sheet ──────────────────────────────────────────────────────

class _CoinDetailSheet extends StatelessWidget {
  final CoinSearchResult result;
  const _CoinDetailSheet({required this.result});

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.55,
      maxChildSize: 0.92,
      minChildSize: 0.3,
      builder: (_, controller) => Container(
        decoration: const BoxDecoration(
          color: Color(0xFF1A1D27),
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          children: [
            // Handle
            Container(
              margin: const EdgeInsets.only(top: 12),
              width: 36,
              height: 4,
              decoration: BoxDecoration(
                  color: Colors.white.withAlpha(40),
                  borderRadius: BorderRadius.circular(2)),
            ),
            Expanded(
              child: ListView(
                controller: controller,
                padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
                children: [
                  // Title
                  Text(
                    result.displayTitle,
                    style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.w700,
                        height: 1.25),
                  ),
                  if (result.programName.isNotEmpty &&
                      result.programName != result.displayTitle) ...[
                    const SizedBox(height: 4),
                    Text(
                      result.programName,
                      style: TextStyle(
                          color: Colors.white.withAlpha(140),
                          fontSize: 13),
                    ),
                  ],
                  const SizedBox(height: 16),
                  // Info grid
                  _DetailGrid(result: result),
                  // Content / description
                  if (result.notes.isNotEmpty) ...[
                    const SizedBox(height: 16),
                    _SectionLabel(label: 'Notes'),
                    const SizedBox(height: 6),
                    Text(
                      result.notes,
                      style: TextStyle(
                          color: Colors.white.withAlpha(160),
                          fontSize: 13,
                          height: 1.5),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionLabel extends StatelessWidget {
  final String label;
  const _SectionLabel({required this.label});
  @override
  Widget build(BuildContext context) => Text(
        label.toUpperCase(),
        style: TextStyle(
            color: Colors.white.withAlpha(80),
            fontSize: 10,
            fontWeight: FontWeight.w600,
            letterSpacing: 1.2),
      );
}

class _DetailGrid extends StatelessWidget {
  final CoinSearchResult result;
  const _DetailGrid({required this.result});

  @override
  Widget build(BuildContext context) {
    final items = <MapEntry<String, String>>[
      if (result.coinYear.isNotEmpty)
        MapEntry('Year', result.coinYear),
      if (result.denomination.isNotEmpty)
        MapEntry('Denomination', result.denomination),
      if (result.category.isNotEmpty)
        MapEntry('Category', result.category),
      if (result.metal.isNotEmpty)
        MapEntry('Metal', result.metal),
      if (result.designer.isNotEmpty)
        MapEntry('Designer', result.designer),
      if (result.mintMarks.isNotEmpty)
        MapEntry('Mint Marks', result.mintMarks),
    ];

    if (items.isEmpty) return const SizedBox.shrink();

    return Wrap(
      spacing: 10,
      runSpacing: 10,
      children: items
          .map((e) => _DetailTile(label: e.key, value: e.value))
          .toList(),
    );
  }
}

class _DetailTile extends StatelessWidget {
  final String label;
  final String value;
  const _DetailTile({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(10),
      constraints: const BoxConstraints(minWidth: 100),
      decoration: BoxDecoration(
        color: Colors.white.withAlpha(8),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.white.withAlpha(15)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label.toUpperCase(),
            style: TextStyle(
                color: Colors.white.withAlpha(80),
                fontSize: 9,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.8),
          ),
          const SizedBox(height: 3),
          Text(
            value,
            style: const TextStyle(
                color: Colors.white,
                fontSize: 13,
                fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }
}

// ─── Suggestions Pane (empty state) ──────────────────────────────────────────

class _SuggestionsPane extends StatelessWidget {
  final List<String> suggestions;
  final ValueChanged<String> onTap;
  const _SuggestionsPane(
      {required this.suggestions, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
      children: [
        // Hero banner
        Container(
          padding: const EdgeInsets.all(20),
          margin: const EdgeInsets.only(bottom: 20),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                const Color(0xFF0B3D6E).withAlpha(150),
                const Color(0xFF1A0A2E).withAlpha(150),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
                color: const Color(0xFF2DD4BF).withAlpha(50)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.auto_awesome,
                      color: Color(0xFF2DD4BF), size: 18),
                  const SizedBox(width: 8),
                  const Text(
                    'AI Coin Reference Search',
                    style: TextStyle(
                        color: Colors.white,
                        fontSize: 15,
                        fontWeight: FontWeight.w700),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Text(
                'Search 1,913+ coin reference entries using natural language. '
                'Ask about specific dates, mint marks, series, or history — '
                'powered by Vertex AI Search.',
                style: TextStyle(
                    color: Colors.white.withAlpha(160),
                    fontSize: 12,
                    height: 1.5),
              ),
            ],
          ),
        ),
        // Suggestions header
        Padding(
          padding: const EdgeInsets.only(bottom: 12),
          child: Text(
            'TRY SEARCHING FOR',
            style: TextStyle(
                color: Colors.white.withAlpha(80),
                fontSize: 10,
                fontWeight: FontWeight.w600,
                letterSpacing: 1.2),
          ),
        ),
        // Suggestion chips
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: suggestions
              .map((s) => _SuggestionChip(label: s, onTap: () => onTap(s)))
              .toList(),
        ),
      ],
    );
  }
}

class _SuggestionChip extends StatefulWidget {
  final String label;
  final VoidCallback onTap;
  const _SuggestionChip({required this.label, required this.onTap});

  @override
  State<_SuggestionChip> createState() => _SuggestionChipState();
}

class _SuggestionChipState extends State<_SuggestionChip> {
  bool _hovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _hovered = true),
      onExit: (_) => setState(() => _hovered = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          padding:
              const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          decoration: BoxDecoration(
            color: _hovered
                ? const Color(0xFFF63366).withAlpha(30)
                : const Color(0xFF1A1D27),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: _hovered
                  ? const Color(0xFFF63366).withAlpha(120)
                  : Colors.white.withAlpha(25),
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.search,
                  size: 13,
                  color: Colors.white.withAlpha(_hovered ? 200 : 100)),
              const SizedBox(width: 6),
              Text(
                widget.label,
                style: TextStyle(
                    color:
                        Colors.white.withAlpha(_hovered ? 230 : 160),
                    fontSize: 12),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─── Loading Shimmer ──────────────────────────────────────────────────────────

class _LoadingShimmer extends StatefulWidget {
  const _LoadingShimmer();

  @override
  State<_LoadingShimmer> createState() => _LoadingShimmerState();
}

class _LoadingShimmerState extends State<_LoadingShimmer>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  late final Animation<double> _anim;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 1200));
    _anim = Tween<double>(begin: -1.0, end: 2.0)
        .animate(CurvedAnimation(parent: _ctrl, curve: Curves.easeInOut));
    _ctrl.repeat();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _anim,
      builder: (context, child) => ListView.builder(
        padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
        itemCount: 5,
        itemBuilder: (ctx, idx) => Container(
          margin: const EdgeInsets.only(bottom: 10),
          height: 90,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            gradient: LinearGradient(
              begin: Alignment(_anim.value - 1, 0),
              end: Alignment(_anim.value, 0),
              colors: [
                const Color(0xFF1A1D27),
                const Color(0xFF252838),
                const Color(0xFF1A1D27),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ─── Error Pane ───────────────────────────────────────────────────────────────

class _ErrorPane extends StatelessWidget {
  final String message;
  const _ErrorPane({required this.message});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.cloud_off,
                color: Colors.white.withAlpha(60), size: 48),
            const SizedBox(height: 12),
            Text(
              message,
              textAlign: TextAlign.center,
              style:
                  TextStyle(color: Colors.white.withAlpha(120), fontSize: 13),
            ),
          ],
        ),
      ),
    );
  }
}
