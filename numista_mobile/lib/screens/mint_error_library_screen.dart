// mint_error_library_screen.dart
//
// The Mint Error Library — a public reference encyclopedia for US coin and
// currency errors. Accessible to both authenticated and guest users.
//
// Features:
//   - Dataset filter tabs: All / Most Collectible / Most Common / Recent / Best Photos
//   - Category filter chips: All / Die / Striking / Planchet / Off-Metal / Currency
//   - Search bar with client-side filtering
//   - Error card grid with thumbnail, category badge, rarity badge, value range
//   - Navigates to MintErrorDetailScreen on tap

import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/mint_error.dart';
import '../services/mint_error_service.dart';
import 'mint_error_detail_screen.dart';

// ─── Design tokens (match app-wide palette) ───────────────────────────────────
const _kBg      = Color(0xFFF0F2F6);
const _kDark    = Color(0xFF0E1117);
const _kAccent  = Color(0xFF4C8CDA);
const _kBrand   = Color(0xFFF63366);
const _kGold    = Color(0xFFFFD700);
const _kSurface = Color(0xFFFFFFFF);
const _kText    = Color(0xFF31333F);
const _kSubtext = Color(0xFF5A5C69);
const _kBorder  = Color(0xFFE2E6E9);

class MintErrorLibraryScreen extends StatefulWidget {
  const MintErrorLibraryScreen({super.key});

  @override
  State<MintErrorLibraryScreen> createState() => _MintErrorLibraryScreenState();
}

class _MintErrorLibraryScreenState extends State<MintErrorLibraryScreen>
    with SingleTickerProviderStateMixin {
  // ── State ──────────────────────────────────────────────────────────────────
  String _selectedDataset = '';          // '' = All
  String _selectedCategory = '';         // '' = All categories
  String _searchQuery = '';
  bool _isSearching = false;
  List<MintError> _searchResults = [];
  bool _searchLoading = false;

  final TextEditingController _searchCtrl = TextEditingController();
  final FocusNode _searchFocus = FocusNode();

  // ── Dataset tab definitions ───────────────────────────────────────────────
  static const _datasets = [
    {'label': 'All',         'value': '',            'icon': Icons.apps_outlined},
    {'label': 'Collectible', 'value': 'collectible', 'icon': Icons.star_outline},
    {'label': 'Common',      'value': 'common',      'icon': Icons.search},
    {'label': 'Recent',      'value': 'recent',      'icon': Icons.schedule_outlined},
    {'label': 'Best Photos', 'value': 'photographed','icon': Icons.photo_camera_outlined},
  ];

  // ── Category chip definitions ─────────────────────────────────────────────
  static const _categories = [
    {'label': 'All',        'value': ''},
    {'label': 'Die Errors', 'value': 'Doubled Die'},
    {'label': 'Striking',   'value': 'Striking'},
    {'label': 'Planchet',   'value': 'Planchet'},
    {'label': 'Off-Metal',  'value': 'Off-Metal'},
    {'label': 'Currency',   'value': 'Currency'},
    {'label': 'Die Variety','value': 'Die Variety'},
    {'label': 'Overdate',   'value': 'Overdate'},
    {'label': 'Missing MM', 'value': 'Missing Mintmark'},
  ];

  @override
  void dispose() {
    _searchCtrl.dispose();
    _searchFocus.dispose();
    super.dispose();
  }

  // ── Search ─────────────────────────────────────────────────────────────────
  Future<void> _runSearch(String q) async {
    if (q.trim().isEmpty) {
      setState(() { _searchResults = []; _searchLoading = false; });
      return;
    }
    setState(() => _searchLoading = true);
    final results = await MintErrorService.searchErrors(q);
    setState(() { _searchResults = results; _searchLoading = false; });
  }

  // ─────────────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _kBg,
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          _buildDatasetTabs(),
          _buildCategoryChips(),
          _buildSearchBar(),
          const Divider(height: 1, color: _kBorder),
          Expanded(child: _isSearching ? _buildSearchResults() : _buildErrorStream()),
        ],
      ),
    );
  }

  // ── Header ────────────────────────────────────────────────────────────────
  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 20, 20, 12),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: _kBrand.withAlpha(20),
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Icon(Icons.error_outline, color: _kBrand, size: 22),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Error Library',
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w700,
                    color: _kText,
                  ),
                ),
                Text(
                  'US coin & currency mint errors — reference encyclopedia',
                  style: TextStyle(fontSize: 12, color: _kSubtext),
                ),
              ],
            ),
          ),
          // Stats badge
          StreamBuilder<List<MintError>>(
            stream: MintErrorService.streamErrors(),
            builder: (context, snap) {
              final count = snap.data?.length ?? 0;
              if (count == 0) return const SizedBox.shrink();
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: _kDark,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  '$count errors',
                  style: const TextStyle(
                    color: Colors.white70,
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  // ── Dataset tabs ─────────────────────────────────────────────────────────
  Widget _buildDatasetTabs() {
    return SizedBox(
      height: 40,
      child: ListView.separated(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        scrollDirection: Axis.horizontal,
        itemCount: _datasets.length,
        separatorBuilder: (_, _) => const SizedBox(width: 6),
        itemBuilder: (_, i) {
          final tab = _datasets[i];
          final selected = _selectedDataset == tab['value'];
          return GestureDetector(
            onTap: () => setState(() {
              _selectedDataset = tab['value'] as String;
              _isSearching = false;
              _searchCtrl.clear();
              _searchQuery = '';
            }),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 180),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
              decoration: BoxDecoration(
                color: selected ? _kBrand : _kSurface,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: selected ? _kBrand : _kBorder,
                ),
                boxShadow: selected
                    ? [BoxShadow(color: _kBrand.withAlpha(40), blurRadius: 8, offset: const Offset(0, 2))]
                    : [],
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    tab['icon'] as IconData,
                    size: 13,
                    color: selected ? Colors.white : _kSubtext,
                  ),
                  const SizedBox(width: 5),
                  Text(
                    tab['label'] as String,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: selected ? Colors.white : _kText,
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  // ── Category chips ────────────────────────────────────────────────────────
  Widget _buildCategoryChips() {
    return SizedBox(
      height: 36,
      child: ListView.separated(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 2),
        scrollDirection: Axis.horizontal,
        itemCount: _categories.length,
        separatorBuilder: (_, _) => const SizedBox(width: 6),
        itemBuilder: (_, i) {
          final cat = _categories[i];
          final selected = _selectedCategory == cat['value'];
          return GestureDetector(
            onTap: () => setState(() => _selectedCategory = cat['value'] as String),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: selected ? _kAccent.withAlpha(30) : Colors.transparent,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: selected ? _kAccent : _kBorder,
                ),
              ),
              child: Text(
                cat['label'] as String,
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w500,
                  color: selected ? _kAccent : _kSubtext,
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  // ── Search bar ────────────────────────────────────────────────────────────
  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
      child: TextField(
        controller: _searchCtrl,
        focusNode: _searchFocus,
        onChanged: (v) {
          setState(() {
            _searchQuery = v;
            _isSearching = v.isNotEmpty;
          });
          _runSearch(v);
        },
        decoration: InputDecoration(
          hintText: 'Search errors by name, year, denomination…',
          hintStyle: TextStyle(fontSize: 13, color: _kSubtext),
          prefixIcon: const Icon(Icons.search, size: 18, color: _kSubtext),
          suffixIcon: _searchQuery.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.clear, size: 16),
                  onPressed: () {
                    _searchCtrl.clear();
                    setState(() { _searchQuery = ''; _isSearching = false; _searchResults = []; });
                  },
                )
              : null,
          filled: true,
          fillColor: _kSurface,
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: _kBorder),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: _kBorder),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: _kAccent, width: 1.5),
          ),
        ),
      ),
    );
  }

  // ── Stream-backed error list ───────────────────────────────────────────────
  Widget _buildErrorStream() {
    return StreamBuilder<List<MintError>>(
      stream: MintErrorService.streamErrors(
        dataset: _selectedDataset.isNotEmpty ? _selectedDataset : null,
        category: _selectedCategory.isNotEmpty ? _selectedCategory : null,
      ),
      builder: (context, snap) {
        if (snap.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snap.hasError) {
          return Center(
            child: Text('Error loading library: ${snap.error}',
                style: const TextStyle(color: Colors.red)),
          );
        }
        final errors = snap.data ?? [];
        if (errors.isEmpty) {
          return _buildEmptyState();
        }
        return _buildErrorGrid(errors);
      },
    );
  }

  // ── Search results ────────────────────────────────────────────────────────
  Widget _buildSearchResults() {
    if (_searchLoading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_searchResults.isEmpty) {
      return _buildEmptyState(message: 'No errors match "$_searchQuery"');
    }
    return _buildErrorGrid(_searchResults);
  }

  // ── Empty state ───────────────────────────────────────────────────────────
  Widget _buildEmptyState({String? message}) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.search_off_outlined, size: 48, color: _kSubtext.withAlpha(120)),
          const SizedBox(height: 12),
          Text(
            message ?? 'No errors found in this category.',
            style: TextStyle(color: _kSubtext, fontSize: 14),
          ),
          const SizedBox(height: 6),
          Text(
            'More errors being added regularly.',
            style: TextStyle(color: _kSubtext.withAlpha(150), fontSize: 12),
          ),
        ],
      ),
    );
  }

  // ── Error grid / list ─────────────────────────────────────────────────────
  Widget _buildErrorGrid(List<MintError> errors) {
    final isWide = MediaQuery.of(context).size.width > 900;
    if (isWide) {
      return GridView.builder(
        padding: const EdgeInsets.all(16),
        gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
          maxCrossAxisExtent: 340,
          childAspectRatio: 0.75,
          crossAxisSpacing: 12,
          mainAxisSpacing: 12,
        ),
        itemCount: errors.length,
        itemBuilder: (_, i) => _ErrorCard(error: errors[i], onTap: () => _openDetail(errors[i])),
      );
    }
    return ListView.separated(
      padding: const EdgeInsets.all(12),
      itemCount: errors.length,
      separatorBuilder: (_, _) => const SizedBox(height: 8),
      itemBuilder: (_, i) => _ErrorCard(error: errors[i], onTap: () => _openDetail(errors[i])),
    );
  }

  void _openDetail(MintError error) {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => MintErrorDetailScreen(error: error)),
    );
  }
}

// ─── Error Card ───────────────────────────────────────────────────────────────
class _ErrorCard extends StatelessWidget {
  final MintError error;
  final VoidCallback onTap;

  const _ErrorCard({required this.error, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final img = error.primaryImage;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: _kSurface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: _kBorder),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withAlpha(12),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Thumbnail ──────────────────────────────────────────────────
            ClipRRect(
              borderRadius: const BorderRadius.vertical(top: Radius.circular(12)),
              child: AspectRatio(
                aspectRatio: 16 / 9,
                child: img != null && img.url.isNotEmpty
                    ? CachedNetworkImage(
                        imageUrl: img.url,
                        fit: BoxFit.cover,
                        placeholder: (_, _) => _ImagePlaceholder(error: error),
                        errorWidget: (_, _, _) => _ImagePlaceholder(error: error),
                      )
                    : _ImagePlaceholder(error: error),
              ),
            ),
            // ── Info ───────────────────────────────────────────────────────
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Category + Rarity badges
                  Row(
                    children: [
                      _Badge(label: error.category, color: _categoryColor(error.category)),
                      const SizedBox(width: 6),
                      _Badge(label: error.rarity, color: _rarityColor(error.rarity)),
                    ],
                  ),
                  const SizedBox(height: 6),
                  // Name
                  Text(
                    error.name,
                    style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w700,
                      color: _kText,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  // Year + denomination
                  Text(
                    '${error.yearDisplay} · ${error.denominations.map(_fmtDenom).join(', ')}',
                    style: const TextStyle(fontSize: 11, color: _kSubtext),
                  ),
                  const SizedBox(height: 6),
                  // Value range
                  Row(
                    children: [
                      const Icon(Icons.attach_money, size: 13, color: _kGold),
                      Expanded(
                        child: Text(
                          error.valueRange,
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: _kGold,
                          ),
                        ),
                      ),
                      const Icon(Icons.chevron_right, size: 16, color: _kSubtext),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─── Image Placeholder (shown when image is pending) ─────────────────────────
class _ImagePlaceholder extends StatelessWidget {
  final MintError error;
  const _ImagePlaceholder({required this.error});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: const Color(0xFF1A1D2E),
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              _categoryIcon(error.category),
              size: 32,
              color: _categoryColor(error.category).withAlpha(180),
            ),
            const SizedBox(height: 6),
            Text(
              error.shortName.isNotEmpty ? error.shortName : error.category,
              style: const TextStyle(
                color: Colors.white54,
                fontSize: 10,
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),
            const Text(
              'Image Pending',
              style: TextStyle(color: Colors.white30, fontSize: 9),
            ),
          ],
        ),
      ),
    );
  }
}

// ─── Badge widget ─────────────────────────────────────────────────────────────
class _Badge extends StatelessWidget {
  final String label;
  final Color color;
  const _Badge({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
      decoration: BoxDecoration(
        color: color.withAlpha(25),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withAlpha(80)),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w600,
          color: color,
        ),
      ),
    );
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
String _fmtDenom(String d) {
  switch (d.toLowerCase()) {
    case 'cent': return 'Cent';
    case 'nickel': return 'Nickel';
    case 'dime': return 'Dime';
    case 'quarter': return 'Quarter';
    case 'half dollar': return 'Half Dollar';
    case 'dollar': return 'Dollar';
    case 'silver eagle': return 'Silver Eagle';
    case 'gold eagle': return 'Gold Eagle';
    case 'currency': return 'Currency';
    default: return d;
  }
}

Color _categoryColor(String category) {
  switch (category) {
    case 'Doubled Die': return const Color(0xFFF63366);
    case 'Off-Metal':   return const Color(0xFFFF9500);
    case 'Planchet':    return const Color(0xFF34C759);
    case 'Striking':    return const Color(0xFF4C8CDA);
    case 'Die Variety': return const Color(0xFF9B59B6);
    case 'Overdate':    return const Color(0xFFFF6B35);
    case 'Missing Mintmark': return const Color(0xFFE74C3C);
    case 'Die Gouge':   return const Color(0xFF1ABC9C);
    case 'Currency':    return const Color(0xFF2ECC71);
    default:            return const Color(0xFF5A5C69);
  }
}

Color _rarityColor(String rarity) {
  switch (rarity) {
    case 'Legendary':  return const Color(0xFFFFD700);
    case 'Rare':       return const Color(0xFFF63366);
    case 'Uncommon':   return const Color(0xFF4C8CDA);
    case 'Common':     return const Color(0xFF5A5C69);
    default:           return const Color(0xFF5A5C69);
  }
}

IconData _categoryIcon(String category) {
  switch (category) {
    case 'Doubled Die': return Icons.layers_outlined;
    case 'Off-Metal':   return Icons.science_outlined;
    case 'Planchet':    return Icons.circle_outlined;
    case 'Striking':    return Icons.architecture;
    case 'Die Variety': return Icons.difference_outlined;
    case 'Currency':    return Icons.account_balance_wallet_outlined;
    default:            return Icons.error_outline;
  }
}
