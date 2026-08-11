import 'dart:async';
import 'dart:convert';
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
  String _sortBy = 'year';
  bool _isDark = false; // Default is Light Theme!

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
    } else {
      _ctrl.text = '';
    }
    WidgetsBinding.instance.addPostFrameCallback((_) => _doSearch());
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
    _debounce = Timer(const Duration(milliseconds: 480), _doSearch);
  }

  Future<void> _doSearch({bool append = false}) async {
    final q = _ctrl.text.trim();

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
      sortBy: _sortBy,
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
    final scaffoldBg = _isDark ? const Color(0xFF0E1117) : const Color(0xFFF8FAFC);
    final cardColor = _isDark ? const Color(0xFF1A1D27) : Colors.white;
    final textDark = _isDark ? Colors.white : const Color(0xFF0F172A);
    final borderCol = _isDark ? Colors.white.withAlpha(20) : const Color(0xFFE2E8F0);

    return Scaffold(
      backgroundColor: scaffoldBg,
      appBar: AppBar(
        backgroundColor: scaffoldBg,
        elevation: 0,
        iconTheme: IconThemeData(color: textDark),
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
            Text(
              'Coin Reference Search',
              style: TextStyle(
                color: textDark,
                fontSize: 16,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(_isDark ? Icons.light_mode : Icons.dark_mode, color: textDark),
            tooltip: _isDark ? 'Switch to Light Theme' : 'Switch to Dark Theme',
            onPressed: () {
              setState(() {
                _isDark = !_isDark;
              });
            },
          ),
          Container(
            margin: const EdgeInsets.only(right: 12, top: 8, bottom: 8),
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: cardColor,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: borderCol),
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
                      color: textDark.withAlpha(180),
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
          _SearchBar(controller: _ctrl, onChanged: _onQueryChanged, isDark: _isDark),

          // ── Sort & Statistics Bar ────────────────────────────────────────
          _SortAndStatsBar(
            totalCount: _response?.total ?? 11906,
            sortBy: _sortBy,
            isDark: _isDark,
            onSortChanged: (val) {
              setState(() {
                _sortBy = val;
              });
              _doSearch();
            },
          ),

          // ── Category filter chips ───────────────────────────────────────
          if (_response != null && _response!.results.isNotEmpty)
            _CategoryChips(
              categories: _categories,
              active: _activeCategory,
              isDark: _isDark,
              onSelect: (c) => setState(() => _activeCategory = c),
            ),
          const SizedBox(height: 8),

          // ── Body ────────────────────────────────────────────────────────
          Expanded(
            child: _loading
                ? _LoadingShimmer(isDark: _isDark)
                : _response == null
                    ? _SuggestionsPane(
                        suggestions: _suggestions,
                        isDark: _isDark,
                        onTap: (s) {
                          _ctrl.text = s;
                          _doSearch();
                        },
                      )
                    : _response!.error != null &&
                            _response!.results.isEmpty
                        ? _ErrorPane(message: _response!.error!, isDark: _isDark)
                        : _ResultsPane(
                            response: _response!,
                            results: _filteredResults,
                            hasMore: _hasMore,
                            loadingMore: _loadingMore,
                            fadeAnim: _fadeAnim,
                            isDark: _isDark,
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
  final bool isDark;
  const _SearchBar({required this.controller, required this.onChanged, required this.isDark});

  @override
  Widget build(BuildContext context) {
    final bg = isDark ? const Color(0xFF1A1D27) : Colors.white;
    final border = isDark ? Colors.white.withAlpha(20) : const Color(0xFFE2E8F0);
    final textCol = isDark ? Colors.white : const Color(0xFF0F172A);
    final hintCol = isDark ? Colors.white.withAlpha(60) : const Color(0xFF94A3B8);

    return Container(
      margin: const EdgeInsets.fromLTRB(16, 0, 16, 12),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: border),
        boxShadow: [
          BoxShadow(
              color: const Color(0xFFF63366).withAlpha(isDark ? 25 : 10),
              blurRadius: 12,
              offset: const Offset(0, 2)),
        ],
      ),
      child: TextField(
        controller: controller,
        onChanged: onChanged,
        autofocus: false,
        style: TextStyle(color: textCol, fontSize: 15),
        decoration: InputDecoration(
          hintText: 'Search coins, series, years, mint marks…',
          hintStyle: TextStyle(color: hintCol, fontSize: 14),
          prefixIcon: const Icon(Icons.search, color: Color(0xFFF63366), size: 20),
          suffixIcon: ValueListenableBuilder<TextEditingValue>(
            valueListenable: controller,
            builder: (context, val, child) => val.text.isNotEmpty
                ? IconButton(
                    icon: Icon(Icons.close,
                        color: isDark ? Colors.white.withAlpha(100) : const Color(0xFF94A3B8), size: 18),
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

// ─── Sort and Stats Bar ──────────────────────────────────────────────────────

class _SortAndStatsBar extends StatelessWidget {
  final int totalCount;
  final String sortBy;
  final bool isDark;
  final ValueChanged<String> onSortChanged;

  const _SortAndStatsBar({
    required this.totalCount,
    required this.sortBy,
    required this.isDark,
    required this.onSortChanged,
  });

  @override
  Widget build(BuildContext context) {
    final textLight = isDark ? Colors.white54 : const Color(0xFF64748B);
    final textDark = isDark ? Colors.white : const Color(0xFF0F172A);
    final bg = isDark ? const Color(0xFF1A1D27) : Colors.white;
    final border = isDark ? Colors.white.withAlpha(15) : const Color(0xFFE2E8F0);

    return Container(
      margin: const EdgeInsets.fromLTRB(16, 0, 16, 12),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: border),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Icon(Icons.library_books_outlined, size: 14, color: const Color(0xFFF63366).withAlpha(200)),
              const SizedBox(width: 6),
              Text(
                'Definitive Registry: $totalCount records',
                style: TextStyle(
                  color: textLight,
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          Row(
            children: [
              Text(
                'Sort: ',
                style: TextStyle(color: textLight, fontSize: 11),
              ),
              const SizedBox(width: 4),
              DropdownButtonHideUnderline(
                child: DropdownButton<String>(
                  value: sortBy,
                  dropdownColor: isDark ? const Color(0xFF1E293B) : Colors.white,
                  icon: Icon(Icons.arrow_drop_down, size: 16, color: textLight),
                  style: TextStyle(color: textDark, fontSize: 11, fontWeight: FontWeight.bold),
                  onChanged: (val) {
                    if (val != null) onSortChanged(val);
                  },
                  items: const [
                    DropdownMenuItem(
                      value: 'year',
                      child: Text('Chronological'),
                    ),
                    DropdownMenuItem(
                      value: 'alphabetical',
                      child: Text('Alphabetical'),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// ─── Category Chips ───────────────────────────────────────────────────────────

class _CategoryChips extends StatelessWidget {
  final List<String> categories;
  final String active;
  final bool isDark;
  final ValueChanged<String> onSelect;
  const _CategoryChips(
      {required this.categories,
      required this.active,
      required this.isDark,
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
                      color: isActive ? Colors.white : (isDark ? Colors.white54 : const Color(0xFF64748B)),
                      fontWeight: isActive
                          ? FontWeight.w600
                          : FontWeight.normal)),
              selected: isActive,
              onSelected: (_) => onSelect(cat),
              backgroundColor: isDark ? const Color(0xFF1A1D27) : const Color(0xFFF1F5F9),
              selectedColor: const Color(0xFFF63366).withAlpha(200),
              checkmarkColor: Colors.white,
              side: BorderSide(
                  color: isActive
                      ? const Color(0xFFF63366)
                      : (isDark ? Colors.white.withAlpha(20) : const Color(0xFFE2E8F0))),
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

class _RegistryHeaderBanner extends StatelessWidget {
  final bool isDark;
  const _RegistryHeaderBanner({required this.isDark});

  @override
  Widget build(BuildContext context) {
    final textLight = isDark ? Colors.white54 : const Color(0xFF64748B);
    final textDark = isDark ? Colors.white : const Color(0xFF0F172A);
    final bg = isDark ? const Color(0xFF131722) : const Color(0xFFF1F5F9);
    final border = isDark ? const Color(0xFFF63366).withAlpha(40) : const Color(0xFFF63366).withAlpha(20);

    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: border, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: const Color(0xFFF63366).withAlpha(20),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.verified, color: Color(0xFFF63366), size: 18),
              ),
              const SizedBox(width: 8),
              Text(
                'DEFINITIVE US COINS & CURRENCY REGISTRY',
                style: TextStyle(
                  color: textLight,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            '11,906 Active Reference Entries',
            style: TextStyle(
              color: textDark,
              fontSize: 20,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'The absolute authority on US Mint programs, banknotes, and historical pattern coinage. Search using natural language or filter chronologically.',
            style: TextStyle(
              color: textLight,
              fontSize: 12,
              height: 1.45,
            ),
          ),
        ],
      ),
    );
  }
}

class _ResultsPane extends StatelessWidget {
  final CoinSearchResponse response;
  final List<CoinSearchResult> results;
  final bool hasMore;
  final bool loadingMore;
  final Animation<double> fadeAnim;
  final bool isDark;
  final VoidCallback onLoadMore;

  const _ResultsPane({
    required this.response,
    required this.results,
    required this.hasMore,
    required this.loadingMore,
    required this.fadeAnim,
    required this.isDark,
    required this.onLoadMore,
  });

  @override
  Widget build(BuildContext context) {
    if (results.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search_off, color: isDark ? Colors.white.withAlpha(60) : const Color(0xFF94A3B8), size: 48),
            const SizedBox(height: 12),
            Text(
              'No results for "${response.query}"',
              style: TextStyle(color: isDark ? Colors.white.withAlpha(120) : const Color(0xFF475569), fontSize: 14),
            ),
            const SizedBox(height: 6),
            Text(
              'Try a different search term or remove filters.',
              style: TextStyle(color: isDark ? Colors.white.withAlpha(60) : const Color(0xFF94A3B8), fontSize: 12),
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
            1 + // For the Registry Header Banner
            (response.summary.isNotEmpty ? 1 : 0) +
            (hasMore ? 1 : 0),
        itemBuilder: (context, index) {
          // Registry Header Banner is always at the top (index == 0)
          if (index == 0) {
            return _RegistryHeaderBanner(isDark: isDark);
          }

          final summaryOffset = response.summary.isNotEmpty ? 1 : 0;
          final cardIndex = index - 1; // Subtract 1 for the Registry Header Banner

          // AI Summary banner right under the Registry Header if summary exists
          if (response.summary.isNotEmpty && cardIndex == 0) {
            return _AISummaryBanner(summary: response.summary, isDark: isDark);
          }

          final resultIndex = cardIndex - summaryOffset;

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
                        foregroundColor: isDark ? Colors.white70 : const Color(0xFF475569),
                        side: BorderSide(
                            color: isDark ? Colors.white.withAlpha(30) : const Color(0xFFCBD5E1)),
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
            isDark: isDark,
          );
        },
      ),
    );
  }
}

// ─── AI Summary Banner ────────────────────────────────────────────────────────

class _AISummaryBanner extends StatelessWidget {
  final String summary;
  final bool isDark;
  const _AISummaryBanner({required this.summary, required this.isDark});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isDark
              ? [
                  const Color(0xFF1A1D27),
                  const Color(0xFF0B3D6E).withAlpha(80),
                ]
              : [
                  Colors.white,
                  const Color(0xFFE0F2FE),
                ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: isDark ? const Color(0xFF2DD4BF).withAlpha(60) : const Color(0xFF0EA5E9).withAlpha(60)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF2DD4BF).withAlpha(30) : const Color(0xFF0EA5E9).withAlpha(20),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(Icons.auto_awesome,
                color: isDark ? const Color(0xFF2DD4BF) : const Color(0xFF0284C7), size: 14),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              summary,
              style: TextStyle(
                  color: isDark ? Colors.white.withAlpha(200) : const Color(0xFF334155),
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
  final bool isDark;
  const _CoinResultCard({required this.result, required this.index, required this.isDark});

  @override
  Widget build(BuildContext context) {
    final mints = result.mintMarks
        .split(',')
        .map((s) => s.trim())
        .where((s) => s.isNotEmpty)
        .toList();

    final cardCol = isDark ? const Color(0xFF1A1D27) : Colors.white;
    final textDark = isDark ? Colors.white : const Color(0xFF1E293B);
    final textLight = isDark ? Colors.white54 : const Color(0xFF64748B);
    final border = isDark ? Colors.white.withAlpha(12) : const Color(0xFFE2E8F0);

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: cardCol,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: border),
        boxShadow: [
          BoxShadow(
              color: isDark ? Colors.black.withAlpha(60) : Colors.black.withAlpha(10),
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
          hoverColor: isDark ? Colors.white.withAlpha(8) : Colors.black.withAlpha(12),
          splashColor: const Color(0xFFF63366).withAlpha(20),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Coin image thumbnail (obverse)
                Container(
                  width: 50,
                  height: 50,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isDark ? Colors.white.withAlpha(10) : const Color(0xFFF1F5F9),
                    border: Border.all(
                      color: isDark ? Colors.white.withAlpha(30) : const Color(0xFFCBD5E1),
                      width: 1,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withAlpha(20),
                        blurRadius: 3,
                        offset: const Offset(0, 1),
                      ),
                    ],
                  ),
                  child: ClipOval(
                    child: result.imageUrlObverse.isNotEmpty
                        ? Image.network(
                            result.imageUrlObverse,
                            fit: BoxFit.cover,
                            errorBuilder: (context, error, stackTrace) =>
                                Icon(Icons.image, size: 20, color: textLight),
                          )
                        : Icon(Icons.image, size: 20, color: textLight),
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
                        style: TextStyle(
                          color: textDark,
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
                              color: textLight,
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
                              color: isDark ? Colors.white.withAlpha(100) : const Color(0xFF475569),
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
                              .map((m) => _MintChip(label: m, isDark: isDark))
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
      builder: (_) => _CoinDetailSheet(result: result, isDark: isDark),
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
  final bool isDark;
  const _MintChip({required this.label, required this.isDark});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: isDark ? Colors.white.withAlpha(12) : const Color(0xFFE2E8F0),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: isDark ? Colors.white.withAlpha(30) : const Color(0xFFCBD5E1)),
      ),
      child: Text(
        label,
        style: TextStyle(
            color: isDark ? Colors.white.withAlpha(160) : const Color(0xFF475569),
            fontSize: 10,
            fontWeight: FontWeight.w500),
      ),
    );
  }
}

// ─── Detail Bottom Sheet ──────────────────────────────────────────────────────

class _CoinDetailSheet extends StatelessWidget {
  final CoinSearchResult result;
  final bool isDark;
  const _CoinDetailSheet({required this.result, required this.isDark});

  @override
  Widget build(BuildContext context) {
    final bg = isDark ? const Color(0xFF1A1D27) : Colors.white;
    final textCol = isDark ? Colors.white : const Color(0xFF0F172A);
    final textSubCol = isDark ? Colors.white.withAlpha(140) : const Color(0xFF64748B);
    final border = isDark ? Colors.white.withAlpha(15) : const Color(0xFFE2E8F0);

    return DraggableScrollableSheet(
      initialChildSize: 0.75, // larger child size for rich details
      maxChildSize: 0.95,
      minChildSize: 0.4,
      builder: (_, controller) => Container(
        decoration: BoxDecoration(
          color: bg,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
          border: Border.all(color: border),
        ),
        child: Column(
          children: [
            // Handle
            Container(
              margin: const EdgeInsets.only(top: 12),
              width: 36,
              height: 4,
              decoration: BoxDecoration(
                  color: isDark ? Colors.white.withAlpha(40) : const Color(0xFFCBD5E1),
                  borderRadius: BorderRadius.circular(2)),
            ),
            Expanded(
              child: ListView(
                controller: controller,
                padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
                children: [
                  // Obverse & Reverse images side-by-side if available
                  if (result.imageUrlObverse.isNotEmpty || result.imageUrlReverse.isNotEmpty) ...[
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        if (result.imageUrlObverse.isNotEmpty)
                          _DetailImage(url: result.imageUrlObverse, label: 'Obverse', isDark: isDark),
                        if (result.imageUrlObverse.isNotEmpty && result.imageUrlReverse.isNotEmpty)
                          const SizedBox(width: 16),
                        if (result.imageUrlReverse.isNotEmpty)
                          _DetailImage(url: result.imageUrlReverse, label: 'Reverse', isDark: isDark),
                      ],
                    ),
                    const SizedBox(height: 20),
                  ],
                  // Title
                  Text(
                    result.displayTitle,
                    style: TextStyle(
                        color: textCol,
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
                          color: textSubCol,
                          fontSize: 13),
                    ),
                  ],
                  const SizedBox(height: 16),
                  // Info grid
                  _DetailGrid(result: result, isDark: isDark),
                  // Price Guide
                  if (result.priceGuide.isNotEmpty) ...[
                    const SizedBox(height: 20),
                    _SectionLabel(label: 'Price Guide (USD)', isDark: isDark),
                    const SizedBox(height: 8),
                    _PriceGuideTable(priceGuideJson: result.priceGuide, isDark: isDark),
                  ],
                  // Content / description
                  if (result.notes.isNotEmpty) ...[
                    const SizedBox(height: 20),
                    _SectionLabel(label: 'Notes', isDark: isDark),
                    const SizedBox(height: 8),
                    Text(
                      result.notes,
                      style: TextStyle(
                          color: isDark ? Colors.white.withAlpha(160) : const Color(0xFF475569),
                          fontSize: 13,
                          height: 1.5),
                    ),
                  ],
                  // APR History
                  if (result.aprHistory.isNotEmpty) ...[
                    const SizedBox(height: 20),
                    _SectionLabel(label: 'Auction Results', isDark: isDark),
                    const SizedBox(height: 8),
                    _AprHistoryList(aprHistoryJson: result.aprHistory, isDark: isDark),
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

class _DetailImage extends StatelessWidget {
  final String url;
  final String label;
  final bool isDark;
  const _DetailImage({required this.url, required this.label, required this.isDark});

  @override
  Widget build(BuildContext context) {
    final bg = isDark ? Colors.white.withAlpha(5) : const Color(0xFFF1F5F9);
    final border = isDark ? Colors.white.withAlpha(20) : const Color(0xFFCBD5E1);
    final textLight = isDark ? Colors.white54 : const Color(0xFF64748B);

    return Column(
      children: [
        Container(
          width: 110,
          height: 110,
          decoration: BoxDecoration(
            color: bg,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: border),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withAlpha(15),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(9),
            child: url.isNotEmpty
                ? Image.network(url, fit: BoxFit.cover)
                : Icon(Icons.image_not_supported, size: 28, color: textLight),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(color: textLight, fontSize: 10, fontWeight: FontWeight.bold),
        ),
      ],
    );
  }
}

class _PriceGuideTable extends StatelessWidget {
  final String priceGuideJson;
  final bool isDark;
  const _PriceGuideTable({required this.priceGuideJson, required this.isDark});

  @override
  Widget build(BuildContext context) {
    try {
      final Map<String, dynamic> prices = jsonDecode(priceGuideJson);
      if (prices.isEmpty) return const Text('No price data available.', style: TextStyle(color: Colors.grey, fontSize: 13));

      return Wrap(
        spacing: 8,
        runSpacing: 8,
        children: prices.entries.map((e) {
          final val = e.value as num;
          final displayVal = val > 0 ? '\$${val.toStringAsFixed(2)}' : '—';
          return Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
            decoration: BoxDecoration(
              color: isDark ? Colors.white.withAlpha(8) : const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: isDark ? Colors.white.withAlpha(15) : const Color(0xFFE2E8F0)),
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(e.key, style: TextStyle(color: isDark ? Colors.white70 : const Color(0xFF475569), fontSize: 10, fontWeight: FontWeight.bold)),
                const SizedBox(height: 2),
                Text(displayVal, style: TextStyle(color: isDark ? const Color(0xFF2DD4BF) : const Color(0xFF0F172A), fontSize: 13, fontWeight: FontWeight.bold)),
              ],
            ),
          );
        }).toList(),
      );
    } catch (e) {
      return const Text('Invalid price data format.', style: TextStyle(color: Colors.redAccent, fontSize: 12));
    }
  }
}

class _AprHistoryList extends StatelessWidget {
  final String aprHistoryJson;
  final bool isDark;
  const _AprHistoryList({required this.aprHistoryJson, required this.isDark});

  @override
  Widget build(BuildContext context) {
    try {
      final List<dynamic> history = jsonDecode(aprHistoryJson);
      if (history.isEmpty) return const Text('No auction records available.', style: TextStyle(color: Colors.grey, fontSize: 13));

      return Column(
        children: history.map((item) {
          final pRaw = item['price'];
          final price = pRaw is num ? pRaw.toDouble() : (double.tryParse(pRaw?.toString() ?? '') ?? 0.0);
          final ah = item['auction_house']?.toString() ?? 'Auction';
          final date = item['date']?.toString() ?? '';
          return Container(
            margin: const EdgeInsets.only(bottom: 6),
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: isDark ? Colors.white.withAlpha(5) : const Color(0xFFF8FAFC),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: isDark ? Colors.white.withAlpha(10) : const Color(0xFFE2E8F0)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(ah, style: TextStyle(color: isDark ? Colors.white : const Color(0xFF1E293B), fontSize: 12, fontWeight: FontWeight.w600)),
                    if (date.isNotEmpty)
                      Text(date, style: TextStyle(color: isDark ? Colors.white54 : const Color(0xFF64748B), fontSize: 10)),
                  ],
                ),
                Text('\$${price.toStringAsFixed(2)}', style: const TextStyle(color: Color(0xFF00C853), fontSize: 13, fontWeight: FontWeight.bold)),
              ],
            ),
          );
        }).toList(),
      );
    } catch (e) {
      return const Text('Invalid auction history format.', style: TextStyle(color: Colors.redAccent, fontSize: 12));
    }
  }
}

class _SectionLabel extends StatelessWidget {
  final String label;
  final bool isDark;
  const _SectionLabel({required this.label, required this.isDark});
  @override
  Widget build(BuildContext context) {
    final textLight = isDark ? Colors.white.withAlpha(80) : const Color(0xFF64748B);
    return Text(
      label.toUpperCase(),
      style: TextStyle(
          color: textLight,
          fontSize: 10,
          fontWeight: FontWeight.w600,
          letterSpacing: 1.2),
    );
  }
}

class _DetailGrid extends StatelessWidget {
  final CoinSearchResult result;
  final bool isDark;
  const _DetailGrid({required this.result, required this.isDark});

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
      if (result.populationTotal > 0)
        MapEntry('Population', '${result.populationTotal} graded'),
    ];

    if (items.isEmpty) return const SizedBox.shrink();

    return Wrap(
      spacing: 10,
      runSpacing: 10,
      children: items
          .map((e) => _DetailTile(label: e.key, value: e.value, isDark: isDark))
          .toList(),
    );
  }
}

class _DetailTile extends StatelessWidget {
  final String label;
  final String value;
  final bool isDark;
  const _DetailTile({required this.label, required this.value, required this.isDark});

  @override
  Widget build(BuildContext context) {
    final bg = isDark ? Colors.white.withAlpha(8) : const Color(0xFFF1F5F9);
    final border = isDark ? Colors.white.withAlpha(15) : const Color(0xFFE2E8F0);
    final textDark = isDark ? Colors.white : const Color(0xFF1E293B);
    final textLight = isDark ? Colors.white.withAlpha(80) : const Color(0xFF64748B);

    return Container(
      padding: const EdgeInsets.all(10),
      constraints: const BoxConstraints(minWidth: 100),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label.toUpperCase(),
            style: TextStyle(
                color: textLight,
                fontSize: 9,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.8),
          ),
          const SizedBox(height: 3),
          Text(
            value,
            style: TextStyle(
                color: textDark,
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
  final bool isDark;
  final ValueChanged<String> onTap;
  const _SuggestionsPane(
      {required this.suggestions, required this.isDark, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final border = isDark ? const Color(0xFF2DD4BF).withAlpha(50) : const Color(0xFFCBD5E1);
    final textDark = isDark ? Colors.white : const Color(0xFF0F172A);
    final textLight = isDark ? Colors.white.withAlpha(160) : const Color(0xFF475569);
    final labelColor = isDark ? Colors.white.withAlpha(80) : const Color(0xFF64748B);

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
      children: [
        // Hero banner
        Container(
          padding: const EdgeInsets.all(20),
          margin: const EdgeInsets.only(bottom: 20),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: isDark
                  ? [
                      const Color(0xFF0B3D6E).withAlpha(150),
                      const Color(0xFF1A0A2E).withAlpha(150),
                    ]
                  : [
                      const Color(0xFFE2E8F0),
                      const Color(0xFFF1F5F9),
                    ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: border),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.auto_awesome,
                      color: Color(0xFFF63366), size: 18),
                  const SizedBox(width: 8),
                  Text(
                    'AI Coin Reference Search',
                    style: TextStyle(
                        color: textDark,
                        fontSize: 15,
                        fontWeight: FontWeight.w700),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Text(
                'Search 11,900+ coin reference entries using natural language. '
                'Ask about specific dates, mint marks, series, or history — '
                'powered by Vertex AI Search.',
                style: TextStyle(
                    color: textLight,
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
                color: labelColor,
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
              .map((s) => _SuggestionChip(label: s, isDark: isDark, onTap: () => onTap(s)))
              .toList(),
        ),
      ],
    );
  }
}

class _SuggestionChip extends StatefulWidget {
  final String label;
  final bool isDark;
  final VoidCallback onTap;
  const _SuggestionChip({required this.label, required this.isDark, required this.onTap});

  @override
  State<_SuggestionChip> createState() => _SuggestionChipState();
}

class _SuggestionChipState extends State<_SuggestionChip> {
  bool _hovered = false;

  @override
  Widget build(BuildContext context) {
    final bg = widget.isDark ? const Color(0xFF1A1D27) : Colors.white;
    final hoverBg = widget.isDark ? const Color(0xFFF63366).withAlpha(30) : const Color(0xFFF63366).withAlpha(15);
    final border = widget.isDark ? Colors.white.withAlpha(25) : const Color(0xFFE2E8F0);
    final hoverBorder = widget.isDark ? const Color(0xFFF63366).withAlpha(120) : const Color(0xFFF63366).withAlpha(80);
    final textCol = widget.isDark ? Colors.white.withAlpha(160) : const Color(0xFF475569);
    final hoverTextCol = widget.isDark ? Colors.white.withAlpha(230) : const Color(0xFF0F172A);

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
            color: _hovered ? hoverBg : bg,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(
              color: _hovered ? hoverBorder : border,
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.search,
                  size: 13,
                  color: widget.isDark
                      ? Colors.white.withAlpha(_hovered ? 200 : 100)
                      : const Color(0xFFF63366).withAlpha(_hovered ? 200 : 120)),
              const SizedBox(width: 6),
              Text(
                widget.label,
                style: TextStyle(
                    color: _hovered ? hoverTextCol : textCol,
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
  final bool isDark;
  const _LoadingShimmer({required this.isDark});

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
    final shBg = widget.isDark ? const Color(0xFF1A1D27) : Colors.white;
    final shHighlight = widget.isDark ? const Color(0xFF252838) : const Color(0xFFF1F5F9);

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
                shBg,
                shHighlight,
                shBg,
              ],
            ),
            border: Border.all(color: widget.isDark ? Colors.transparent : const Color(0xFFE2E8F0)),
          ),
        ),
      ),
    );
  }
}

// ─── Error Pane ───────────────────────────────────────────────────────────────

class _ErrorPane extends StatelessWidget {
  final String message;
  final bool isDark;
  const _ErrorPane({required this.message, required this.isDark});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.cloud_off,
                color: isDark ? Colors.white.withAlpha(60) : const Color(0xFF94A3B8), size: 48),
            const SizedBox(height: 12),
            Text(
              message,
              textAlign: TextAlign.center,
              style:
                  TextStyle(color: isDark ? Colors.white.withAlpha(120) : const Color(0xFF475569), fontSize: 13),
            ),
          ],
        ),
      ),
    );
  }
}
