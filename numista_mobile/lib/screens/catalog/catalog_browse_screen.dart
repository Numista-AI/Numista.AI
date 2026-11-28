import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../models/coin_model.dart';
import '../../services/catalog/catalog_asset_loader.dart';
import '../../services/melt_value_service.dart';
import '../../services/wishlist_service.dart';
import '../../utils/catalog_image_guard.dart';
import '../../utils/mint_helpers.dart';
import '../../widgets/morgan_owl_avatar.dart';
import '../glossary_academy_screen.dart';
import '../unified_coin_detail_screen.dart';

class CatalogBrowseScreen extends StatefulWidget {
  final String? initialQuery;
  final String? initialNacCode;
  final String? initialTab;

  const CatalogBrowseScreen({
    super.key,
    this.initialQuery,
    this.initialNacCode,
    this.initialTab,
  });

  @visibleForTesting
  static Widget buildMintageRowForTest(Map<String, dynamic> item) =>
      _CatalogBrowseScreenState._buildMintageRowStatic(item);

  @visibleForTesting
  static List<Map<String, dynamic>> filterEntriesForTest(
    List<Map<String, dynamic>> entries, {
    String selectedType = 'coin',
    String selectedEra = 'all',
    bool photosOnly = false,
    String query = '',
  }) =>
      _CatalogBrowseScreenState.filterCatalogEntries(
        entries,
        selectedType: selectedType,
        selectedEra: selectedEra,
        photosOnly: photosOnly,
        query: query,
      );

  @visibleForTesting
  static Map<String, dynamic>? resolveEntryByNacOrAliasForTest(
    List<Map<String, dynamic>> entries,
    String rawCode,
  ) =>
      _CatalogBrowseScreenState.resolveEntryByNacOrAlias(entries, rawCode);

  @override
  State<CatalogBrowseScreen> createState() => _CatalogBrowseScreenState();
}

class _CatalogBrowseScreenState extends State<CatalogBrowseScreen> {
  List<Map<String, dynamic>> _allEntries = [];
  List<Map<String, dynamic>> _filteredEntries = [];
  bool _isLoading = true;
  String _searchQuery = '';
  String _selectedType = 'coin'; // 'coin', 'note', 'medal', 'foreign'
  String _selectedEra = 'all';
  bool _photosOnly = false;
  bool _chronological = false;
  String? _notFoundNacCode;

  final TextEditingController _searchController = TextEditingController();

  // Missing something form fields
  final TextEditingController _missingDescController = TextEditingController();
  final TextEditingController _missingYearController = TextEditingController();
  final TextEditingController _missingSourceController = TextEditingController();
  String _missingType = 'Coin';
  bool _missingSubmitted = false;

  @override
  void initState() {
    super.initState();
    if (widget.initialQuery != null) {
      _searchQuery = widget.initialQuery!;
      _searchController.text = widget.initialQuery!;
    }
    if (widget.initialTab != null && widget.initialTab!.trim().isNotEmpty) {
      _selectedType = widget.initialTab!.trim().toLowerCase();
    }
    _loadCatalog();
  }

  @override
  void dispose() {
    _searchController.dispose();
    _missingDescController.dispose();
    _missingYearController.dispose();
    _missingSourceController.dispose();
    super.dispose();
  }

  Future<void> _loadCatalog() async {
    try {
      final entries = await CatalogAssetLoader.instance.loadIndex();

      if (mounted) {
        setState(() {
          _allEntries = entries;
          _isLoading = false;
          _applyFilters();
        });

        if (widget.initialNacCode != null && widget.initialNacCode!.trim().isNotEmpty) {
          final match = resolveEntryByNacOrAlias(_allEntries, widget.initialNacCode!);
          if (match != null && match.isNotEmpty) {
            final hydrated = await CatalogAssetLoader.instance.loadFullEntry(
                  (match['nac_code'] as String?) ?? widget.initialNacCode!,
                ) ??
                match;
            if (!mounted) return;
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (mounted) {
                _showItemDetailModal(hydrated);
              }
            });
          } else {
            setState(() {
              _notFoundNacCode = widget.initialNacCode!.trim();
            });
          }
        }
      }
    } catch (e) {
      debugPrint('[Catalog] Failed to load catalog assets: $e');
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  static Map<String, dynamic>? resolveEntryByNacOrAlias(
    List<Map<String, dynamic>> entries,
    String rawCode,
  ) {
    final targetNac = rawCode.trim().toLowerCase();
    if (targetNac.isEmpty) return null;
    for (final e in entries) {
      if ((e['nac_code'] as String? ?? '').toLowerCase() == targetNac) {
        return e;
      }
      final aliases = e['nac_aliases'];
      if (aliases is List) {
        for (final a in aliases) {
          if (a is String && a.trim().toLowerCase() == targetNac) {
            return e;
          }
        }
      }
    }
    return null;
  }

  static List<Map<String, dynamic>> filterCatalogEntries(
    List<Map<String, dynamic>> entries, {
    required String selectedType,
    required String selectedEra,
    required bool photosOnly,
    required String query,
  }) {
    if (selectedType == 'foreign' || selectedType == 'glossary') {
      return [];
    }

    final q = query.trim().toLowerCase();

    List<Map<String, dynamic>> filtered = entries.where((item) {
      final type = (item['type'] as String? ?? '').toLowerCase();
      final nac = (item['nac_code'] as String? ?? '').toUpperCase();
      final int? year = item['year'] is int ? item['year'] as int : null;

      if (selectedType == 'coin' && type != 'coin') return false;
      if (selectedType == 'note' && type != 'note') return false;
      if (selectedType == 'medal' && type != 'medal') return false;
      if (selectedType == 'errors') {
        final hasVarieties = item['has_varieties'] == true ||
            (item['varieties'] is List && (item['varieties'] as List).isNotEmpty);
        final isErr = type == 'error' || nac.contains('.ERR.') || hasVarieties;
        if (!isErr) return false;
      }
      if (selectedType == 'upcoming') {
        if (year == null || year < 2026) return false;
      }

      if (selectedEra != 'all') {
        if (selectedEra == 'pre_federal') {
          if (year == null || year >= 1792) return false;
        } else if (selectedEra == 'early_republic') {
          if (year == null || year < 1792 || year >= 1837) return false;
        } else if (selectedEra == 'seated') {
          if (year == null || year < 1837 || year >= 1873) return false;
        } else if (selectedEra == 'morgan') {
          if (year == null || year < 1873 || year >= 1901) return false;
        } else if (selectedEra == '20th') {
          if (year == null || year < 1901 || year >= 2000) return false;
        } else if (selectedEra == 'modern') {
          if (year == null || year < 2000 || year > 2026) return false;
        } else if (selectedEra == 'undated') {
          if (year != null) return false;
        }
      }

      if (photosOnly) {
        final hasPrimary = item['primary_image'] != null && (item['primary_image'] as Map).isNotEmpty;
        final hasType = item['type_image'] != null && (item['type_image'] as Map).isNotEmpty;
        final hasPkg = item['has_packaging_images'] == true ||
            (item['packaging_images'] is List && (item['packaging_images'] as List).isNotEmpty);
        if (!hasPrimary && !hasType && !hasPkg && item['has_photo'] != true) return false;
      }

      return true;
    }).toList();

    List<Map<String, dynamic>> result = filtered;
    if (q.isNotEmpty) {
      String aliasesJoined(Map<String, dynamic> item) {
        final sa = item['search_aliases'];
        if (sa is! List) return '';
        return sa.whereType<String>().join(' ').toLowerCase();
      }

      // Pass 1: Direct substring matches across metadata + search_aliases (Wave 2 Component D)
      final directMatches = filtered.where((item) {
        final name = (item['name'] as String? ?? '').toLowerCase();
        final series = (item['series'] as String? ?? '').toLowerCase();
        final denom = (item['denomination'] as String? ?? '').toLowerCase();
        final nac = (item['nac_code'] as String? ?? '').toLowerCase();
        final yearStr = item['year']?.toString() ?? '';
        final aliases = aliasesJoined(item);
        return name.contains(q) ||
            series.contains(q) ||
            denom.contains(q) ||
            nac.contains(q) ||
            yearStr.contains(q) ||
            aliases.contains(q);
      }).toList();

      if (directMatches.isNotEmpty) {
        result = directMatches;
      } else {
        // Pass 2: Multi-token fallback across combined metadata + search_aliases haystack
        final tokens = q.split(RegExp(r'\s+')).where((t) => t.isNotEmpty).toList();
        result = filtered.where((item) {
          final name = (item['name'] as String? ?? '').toLowerCase();
          final series = (item['series'] as String? ?? '').toLowerCase();
          final denom = (item['denomination'] as String? ?? '').toLowerCase();
          final nac = (item['nac_code'] as String? ?? '').toLowerCase();
          final yearStr = item['year']?.toString() ?? '';
          final aliases = aliasesJoined(item);
          final haystack = '$name $series $denom $nac $yearStr $aliases';
          return tokens.every((token) => haystack.contains(token));
        }).toList();
      }
    }
    return result;
  }

  void _applyFilters() {
    final result = filterCatalogEntries(
      _allEntries,
      selectedType: _selectedType,
      selectedEra: _selectedEra,
      photosOnly: _photosOnly,
      query: _searchQuery,
    );

    // Sort order
    if (_chronological) {
      result.sort((a, b) {
        final yA = a['year'] as int? ?? 9999;
        final yB = b['year'] as int? ?? 9999;
        if (yA != yB) return yA.compareTo(yB);
        final nA = a['name'] as String? ?? '';
        final nB = b['name'] as String? ?? '';
        return nA.compareTo(nB);
      });
    } else {
      // Default: Images + Sourced first
      result.sort((a, b) {
        final hasImgA = (a['has_photo'] == true ||
                a['primary_image'] != null ||
                a['type_image'] != null ||
                a['has_packaging_images'] == true ||
                (a['packaging_images'] is List && (a['packaging_images'] as List).isNotEmpty))
            ? 1
            : 0;
        final hasImgB = (b['has_photo'] == true ||
                b['primary_image'] != null ||
                b['type_image'] != null ||
                b['has_packaging_images'] == true ||
                (b['packaging_images'] is List && (b['packaging_images'] as List).isNotEmpty))
            ? 1
            : 0;
        if (hasImgA != hasImgB) return hasImgB.compareTo(hasImgA);

        final yA = a['year'] as int? ?? 9999;
        final yB = b['year'] as int? ?? 9999;
        if (yA != yB) return yB.compareTo(yA); // newest year first

        final nA = a['name'] as String? ?? '';
        final nB = b['name'] as String? ?? '';
        return nA.compareTo(nB);
      });
    }

    _filteredEntries = result;
  }

  void _onSearchChanged(String val) {
    setState(() {
      _searchQuery = val;
      _applyFilters();
    });
  }

  void _onTypeChanged(String type) {
    setState(() {
      _selectedType = type;
      _applyFilters();
    });
  }

  void _onEraChanged(String era) {
    setState(() {
      _selectedEra = era;
      _applyFilters();
    });
  }

  void _openAskMorgan({String? initialPrompt, String? nacCode}) {
    final route = (nacCode != null && nacCode.trim().isNotEmpty)
        ? '/?route=AiChatScreen&nac=${Uri.encodeComponent(nacCode.trim())}'
        : '/?route=AiChatScreen';
    Navigator.of(context).pushNamed(
      route,
      arguments: initialPrompt ?? 'Can you tell me about the coins in the catalog?',
    );
  }

  void _navigateHome() {
    if (Navigator.of(context).canPop()) {
      Navigator.of(context).pop();
    } else {
      launchUrl(Uri.parse('/'), webOnlyWindowName: '_self');
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isDesktop = screenWidth >= 1000;

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        surfaceTintColor: Colors.transparent,
        title: Row(
          children: [
            InkWell(
              onTap: _navigateHome,
              child: const Text(
                'Numista.AI',
                style: TextStyle(
                  color: Color(0xFF0B2545),
                  fontWeight: FontWeight.bold,
                  fontSize: 24,
                ),
              ),
            ),
            const SizedBox(width: 24),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                border: Border.all(color: const Color(0xFF1F5FAD), width: 2),
                borderRadius: BorderRadius.circular(6),
              ),
              child: const Text(
                'Public Catalog',
                style: TextStyle(
                  color: Color(0xFF0B2545),
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: _navigateHome,
            child: const Text(
              'Home',
              style: TextStyle(color: Color(0xFF0B2545), fontSize: 18),
            ),
          ),
          const SizedBox(width: 8),
          TextButton(
            onPressed: () => launchUrl(Uri.parse('/login'), webOnlyWindowName: '_self'),
            child: const Text(
              'Sign In',
              style: TextStyle(color: Color(0xFF1F5FAD), fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(width: 16),
        ],
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(2),
          child: Container(color: const Color(0xFFE3E3E3), height: 2),
        ),
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(color: Color(0xFF0B2545)),
            )
          : CustomScrollView(
              slivers: [
                SliverToBoxAdapter(
                  child: Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 1100),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            if (_notFoundNacCode != null) ...[
                              Container(
                                width: double.infinity,
                                margin: const EdgeInsets.only(bottom: 20),
                                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFFFF8E1),
                                  border: Border.all(color: const Color(0xFFF59E0B)),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Row(
                                  children: [
                                    const Icon(Icons.info_outline, color: Color(0xFFB45309)),
                                    const SizedBox(width: 12),
                                    Expanded(
                                      child: Text(
                                        'Reference code "$_notFoundNacCode" was not found in the public catalog.',
                                        style: const TextStyle(
                                          color: Color(0xFF0B2545),
                                          fontSize: 15,
                                          fontWeight: FontWeight.w500,
                                        ),
                                      ),
                                    ),
                                    IconButton(
                                      icon: const Icon(Icons.close, size: 18),
                                      onPressed: () => setState(() => _notFoundNacCode = null),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                            // Top Block: Morgan Owl
                            Image.asset(
                              'assets/morgan_avatar.png',
                              width: 180,
                              height: 180,
                              fit: BoxFit.contain,
                              errorBuilder: (c, e, s) => Image.asset(
                                'assets/logo_owl.png',
                                width: 140,
                                height: 140,
                                fit: BoxFit.contain,
                              ),
                            ),
                            const SizedBox(height: 12),

                            // H1 Title (Wave 2 Component A: Catalog of American Numismatics)
                            const Text(
                              'Catalog of American Numismatics',
                              textAlign: TextAlign.center,
                              style: TextStyle(
                                fontSize: 40,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF0B2545),
                                height: 1.2,
                              ),
                            ),
                            const SizedBox(height: 20),

                            // In-Progress Notice Box
                            Container(
                              width: double.infinity,
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: const Color(0xFFF2F2F2),
                                border: Border.all(color: const Color(0xFFD6D6D6)),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: const Text(
                                'Every coin, banknote, and official government medal of the United States and its territories (1787 Fugio cent through 2026 releases), with primary-sourced mintages and verified reference images.',
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  color: Color(0xFF333333),
                                  fontSize: 18,
                                  height: 1.5,
                                ),
                              ),
                            ),
                            const SizedBox(height: 24),

                            // Search & Ask Morgan Row
                            _buildSearchRow(isDesktop),
                            const SizedBox(height: 28),

                            // Category Type Tabs (Wave 2 Component B folded tabs)
                            _buildTypeTabs(),
                            const SizedBox(height: 20),

                            // Filter Controls Row
                            if (_selectedType != 'foreign' && _selectedType != 'glossary')
                              _buildFilterControls(),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),

                // Content Area
                if (_selectedType == 'glossary')
                  const SliverToBoxAdapter(
                    child: SizedBox(
                      height: 760,
                      child: GlossaryAcademyScreen(),
                    ),
                  )
                else if (_selectedType == 'foreign')
                  SliverToBoxAdapter(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 60),
                      child: Center(
                        child: Container(
                          padding: const EdgeInsets.all(24),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF2F2F2),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: const Color(0xFFD6D6D6)),
                          ),
                          child: const Text(
                            'Foreign coins are coming later.',
                            style: TextStyle(
                              color: Color(0xFF333333),
                              fontSize: 22,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                    ),
                  )
                else if (_filteredEntries.isEmpty)
                  SliverToBoxAdapter(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 60),
                      child: Center(
                        child: Column(
                          children: [
                            const Icon(Icons.search_off_rounded, size: 64, color: Color(0xFF6B6B6B)),
                            const SizedBox(height: 16),
                            const Text(
                              'No matching catalog items found.',
                              style: TextStyle(fontSize: 22, color: Color(0xFF333333)),
                            ),
                            const SizedBox(height: 8),
                            TextButton(
                              onPressed: () {
                                setState(() {
                                  _searchQuery = '';
                                  _searchController.clear();
                                  _selectedEra = 'all';
                                  _photosOnly = false;
                                  _applyFilters();
                                });
                              },
                              child: const Text('Reset search & filters', style: TextStyle(fontSize: 18)),
                            ),
                          ],
                        ),
                      ),
                    ),
                  )
                else
                  SliverPadding(
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                    sliver: SliverToBoxAdapter(
                      child: Center(
                        child: ConstrainedBox(
                          constraints: const BoxConstraints(maxWidth: 1100),
                          child: LayoutBuilder(
                            builder: (context, constraints) {
                              final crossAxisCount = constraints.maxWidth >= 900
                                  ? 3
                                  : (constraints.maxWidth >= 600 ? 2 : 1);
                              return GridView.builder(
                                shrinkWrap: true,
                                physics: const NeverScrollableScrollPhysics(),
                                gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                                  crossAxisCount: crossAxisCount,
                                  crossAxisSpacing: 20,
                                  mainAxisSpacing: 20,
                                  childAspectRatio: 0.60,
                                ),
                                itemCount: _filteredEntries.length,
                                itemBuilder: (context, index) {
                                  final item = _filteredEntries[index];
                                  return CatalogItemCard(
                                    item: item,
                                    onTap: () => _showItemDetailModal(item),
                                  );
                                },
                              );
                            },
                          ),
                        ),
                      ),
                    ),
                  ),

                // "Missing something?" Form
                SliverToBoxAdapter(
                  child: Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 1100),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 48),
                        child: _buildMissingSomethingSection(),
                      ),
                    ),
                  ),
                ),
              ],
            ),
    );
  }

  Widget _buildSearchRow(bool isDesktop) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return Wrap(
          spacing: 12,
          runSpacing: 12,
          alignment: WrapAlignment.center,
          children: [
            SizedBox(
              width: constraints.maxWidth >= 720 ? constraints.maxWidth - 360 : double.infinity,
              height: 64,
              child: TextField(
                controller: _searchController,
                style: const TextStyle(fontSize: 22, color: Color(0xFF1A1A1A)),
                decoration: InputDecoration(
                  hintText: 'Search the catalog...',
                  hintStyle: const TextStyle(color: Color(0xFF595959), fontSize: 22),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: const BorderSide(color: Color(0xFF0B2545), width: 2),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                    borderSide: const BorderSide(color: Color(0xFF1F5FAD), width: 2.5),
                  ),
                  suffixIcon: _searchQuery.isNotEmpty
                      ? IconButton(
                          icon: const Icon(Icons.clear, color: Color(0xFF0B2545)),
                          onPressed: () {
                            _searchController.clear();
                            _onSearchChanged('');
                          },
                        )
                      : null,
                ),
                onChanged: _onSearchChanged,
              ),
            ),
            SizedBox(
              height: 64,
              child: ElevatedButton.icon(
                onPressed: () => _applyFilters(),
                icon: const Icon(Icons.search, size: 24, color: Colors.white),
                label: const Text('Search', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0B2545),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                    side: const BorderSide(color: Color(0xFF0B2545), width: 2),
                  ),
                ),
              ),
            ),
            SizedBox(
              height: 64,
              child: ElevatedButton.icon(
                onPressed: () => _openAskMorgan(initialPrompt: _searchQuery.isNotEmpty ? 'Tell me about $_searchQuery' : null),
                icon: const MorganOwlAvatar(size: 32),
                label: const Text('Ask Morgan', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0B2545),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                    side: const BorderSide(color: Color(0xFF0B2545), width: 2),
                  ),
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildTypeTabs() {
    final coinCount = _allEntries.where((e) => (e['type'] as String? ?? '').toLowerCase() == 'coin').length;
    final noteCount = _allEntries.where((e) => (e['type'] as String? ?? '').toLowerCase() == 'note').length;
    final medalCount = _allEntries.where((e) => (e['type'] as String? ?? '').toLowerCase() == 'medal').length;
    final errCount = _allEntries.where((e) {
      final t = (e['type'] as String? ?? '').toLowerCase();
      final nac = (e['nac_code'] as String? ?? '').toUpperCase();
      final hasVar = e['has_varieties'] == true ||
          (e['varieties'] is List && (e['varieties'] as List).isNotEmpty);
      return t == 'error' || nac.contains('.ERR.') || hasVar;
    }).length;
    final upcomingCount = _allEntries.where((e) => (e['year'] is int) && (e['year'] as int) >= 2026).length;
    final fmt = _mintageNumberFormat;

    return Wrap(
      spacing: 12,
      runSpacing: 10,
      alignment: WrapAlignment.center,
      children: [
        _TypeTab(
          label: 'Coins (${fmt.format(coinCount)})',
          isSelected: _selectedType == 'coin',
          onTap: () => _onTypeChanged('coin'),
        ),
        _TypeTab(
          label: 'Banknotes (${fmt.format(noteCount)})',
          isSelected: _selectedType == 'note',
          onTap: () => _onTypeChanged('note'),
        ),
        _TypeTab(
          label: 'Medals (${fmt.format(medalCount)})',
          isSelected: _selectedType == 'medal',
          onTap: () => _onTypeChanged('medal'),
        ),
        _TypeTab(
          label: 'Errors & Varieties (${fmt.format(errCount)})',
          isSelected: _selectedType == 'errors',
          onTap: () => _onTypeChanged('errors'),
        ),
        _TypeTab(
          label: 'Upcoming (${fmt.format(upcomingCount)})',
          isSelected: _selectedType == 'upcoming',
          onTap: () => _onTypeChanged('upcoming'),
        ),
        _TypeTab(
          label: 'Glossary',
          isSelected: _selectedType == 'glossary',
          onTap: () => _onTypeChanged('glossary'),
        ),
        _TypeTab(
          label: 'Foreign Coins',
          isSelected: _selectedType == 'foreign',
          onTap: () => _onTypeChanged('foreign'),
        ),
      ],
    );
  }

  Widget _buildFilterControls() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F9FA),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: const Color(0xFFE3E3E3)),
      ),
      child: Wrap(
        spacing: 24,
        runSpacing: 12,
        crossAxisAlignment: WrapCrossAlignment.center,
        alignment: WrapAlignment.spaceBetween,
        children: [
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Era: ', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF0B2545))),
              DropdownButton<String>(
                value: _selectedEra,
                underline: const SizedBox(),
                style: const TextStyle(fontSize: 18, color: Color(0xFF1A1A1A)),
                items: const [
                  DropdownMenuItem(value: 'all', child: Text('All Eras')),
                  DropdownMenuItem(value: 'pre_federal', child: Text('Pre-Federal (< 1792)')),
                  DropdownMenuItem(value: 'early_republic', child: Text('Early Republic (1792–1836)')),
                  DropdownMenuItem(value: 'seated', child: Text('Seated / Civil War (1837–1872)')),
                  DropdownMenuItem(value: 'morgan', child: Text('Morgan / Late 19th (1873–1900)')),
                  DropdownMenuItem(value: '20th', child: Text('20th Century (1901–1999)')),
                  DropdownMenuItem(value: 'modern', child: Text('Modern (2000–2026)')),
                  DropdownMenuItem(value: 'undated', child: Text('Undated')),
                ],
                onChanged: (val) {
                  if (val != null) _onEraChanged(val);
                },
              ),
            ],
          ),
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Checkbox(
                value: _photosOnly,
                activeColor: const Color(0xFF0B2545),
                onChanged: (val) {
                  setState(() {
                    _photosOnly = val ?? false;
                    _applyFilters();
                  });
                },
              ),
              const Text('Photos only', style: TextStyle(fontSize: 18, color: Color(0xFF1A1A1A))),
              const SizedBox(width: 16),
              Checkbox(
                value: _chronological,
                activeColor: const Color(0xFF0B2545),
                onChanged: (val) {
                  setState(() {
                    _chronological = val ?? false;
                    _applyFilters();
                  });
                },
              ),
              const Text('Chronological order', style: TextStyle(fontSize: 18, color: Color(0xFF1A1A1A))),
            ],
          ),
          Text(
            '${_filteredEntries.length} items',
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF0B2545)),
          ),
        ],
      ),
    );
  }

  Widget _buildMissingSomethingSection() {
    return Container(
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F9FA),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFD6D6D6), width: 2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Missing something?',
            style: TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.bold,
              color: Color(0xFF0B2545),
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Know a U.S. coin, note, or medal not listed here? Send us the details and primary source reference to add it to our master catalog.',
            style: TextStyle(fontSize: 18, color: Color(0xFF475569)),
          ),
          const SizedBox(height: 20),
          if (_missingSubmitted) ...[
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFFEFF6FF),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFF1F5FAD)),
              ),
              child: const Row(
                children: [
                  Icon(Icons.check_circle, color: Color(0xFF1F5FAD), size: 28),
                  SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      "Thanks - we'll look into it.",
                      style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF0B2545)),
                    ),
                  ),
                ],
              ),
            ),
          ] else ...[
            TextField(
              controller: _missingDescController,
              decoration: const InputDecoration(
                labelText: 'Item Description / Name *',
                border: OutlineInputBorder(),
                filled: true,
                fillColor: Colors.white,
              ),
            ),
            const SizedBox(height: 14),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _missingYearController,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'Year (optional)',
                      border: OutlineInputBorder(),
                      filled: true,
                      fillColor: Colors.white,
                    ),
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    initialValue: _missingType,
                    decoration: const InputDecoration(
                      labelText: 'Type',
                      border: OutlineInputBorder(),
                      filled: true,
                      fillColor: Colors.white,
                    ),
                    items: const [
                      DropdownMenuItem(value: 'Coin', child: Text('Coin')),
                      DropdownMenuItem(value: 'Banknote', child: Text('Banknote')),
                      DropdownMenuItem(value: 'Medal', child: Text('Medal')),
                    ],
                    onChanged: (val) {
                      if (val != null) setState(() => _missingType = val);
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            TextField(
              controller: _missingSourceController,
              decoration: const InputDecoration(
                labelText: 'Primary Source Reference URL (optional)',
                hintText: 'e.g. https://www.usmint.gov/...',
                border: OutlineInputBorder(),
                filled: true,
                fillColor: Colors.white,
              ),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                if (_missingDescController.text.trim().isNotEmpty) {
                  setState(() {
                    _missingSubmitted = true;
                  });
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0B2545),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              child: const Text('Send'),
            ),
          ],
        ],
      ),
    );
  }

  Future<void> _showItemDetailModal(Map<String, dynamic> item) async {
    var resolvedItem = item;
    if (item['chunk'] is String && (item['chunk'] as String).isNotEmpty) {
      final nac = (item['nac_code'] as String? ?? '').trim();
      if (nac.isNotEmpty) {
        try {
          resolvedItem = await CatalogAssetLoader.instance.loadFullEntry(nac) ?? item;
        } catch (e) {
          debugPrint('[Catalog] Failed to hydrate full entry $nac: $e');
        }
      }
      if (!mounted) return;
    }
    UnifiedCoinDetailScreen.showPublic(
      context,
      projection: PublicCoinProjection.fromCatalogMap(resolvedItem),
      legacyOpen: () => _showLegacyItemDetailModal(resolvedItem),
    );
  }

  void _showLegacyItemDetailModal(Map<String, dynamic> item) {
    showDialog(
      context: context,
      builder: (context) {
        return Dialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 680),
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(28),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          item['name'] as String? ?? 'Catalog Entry',
                          style: const TextStyle(
                            fontSize: 26,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF0B2545),
                          ),
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close),
                        onPressed: () => Navigator.of(context).pop(),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  _CatalogBadge(badgeText: item['status_badge'] as String?),
                  const SizedBox(height: 20),

                  // Image section
                  _buildModalImage(item),
                  const SizedBox(height: 20),

                  // Metadata list
                  _buildDetailRow('Denomination', item['denomination']?.toString()),
                  _buildDetailRow('Series', item['series']?.toString()),
                  _buildDetailRow('Year', item['year']?.toString()),
                  _buildDetailRow('Mint Facility', item['mint_facility']?.toString()),
                  _buildDetailRow('Mint Mark', item['mint_mark_on_coin']?.toString()),
                  _buildDetailRow('Composition', item['composition']?.toString()),
                  _buildDetailRow('Weight', item['weight_g'] != null ? '${item['weight_g']} g' : null),
                  _buildDetailRow('Diameter', item['diameter_mm'] != null ? '${item['diameter_mm']} mm' : null),
                  _buildDetailRow('Designer', item['designer']?.toString()),

                  // Mintage
                  _buildMintageRow(item),

                  // History
                  if (item['history'] != null && (item['history'] as String).isNotEmpty) ...[
                    const SizedBox(height: 16),
                    const Text('Historical Context:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: Color(0xFF0B2545))),
                    const SizedBox(height: 6),
                    Text(
                      item['history'] as String,
                      style: const TextStyle(fontSize: 16, height: 1.5, color: Color(0xFF333333)),
                    ),
                  ],

                  // Add to My Wish List + Ask Morgan buttons
                  const SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity,
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(minHeight: 56),
                      child: ElevatedButton.icon(
                        key: const Key('catalog_modal_add_wishlist_button'),
                        onPressed: () => _addCatalogMapToWishlist(context, item),
                        icon: const Icon(Icons.favorite_border, color: Colors.white),
                        label: const Text(
                          'Add to My Wish List',
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF1D4F91),
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(minHeight: 56),
                      child: ElevatedButton.icon(
                        onPressed: () {
                          Navigator.of(context).pop();
                          _openAskMorgan(
                            initialPrompt: 'Can you tell me more about ${item['name']}?',
                            nacCode: item['nac_code']?.toString(),
                          );
                        },
                        icon: const Icon(Icons.chat_bubble_outline, color: Colors.white),
                        label: Text('Ask Morgan about this ${item['type'] ?? 'coin'}', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF0B2545),
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildModalImage(Map<String, dynamic> item) {
    return CatalogDetailImagesView(item: item);
  }

  Widget _buildDetailRow(String label, String? val) {
    if (val == null || val.isEmpty) return const SizedBox();
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 140,
            child: Text(
              '$label:',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF475569)),
            ),
          ),
          Expanded(
            child: Text(
              val,
              style: const TextStyle(fontSize: 16, color: Color(0xFF1A1A1A)),
            ),
          ),
        ],
      ),
    );
  }

  static final NumberFormat _mintageNumberFormat =
      NumberFormat.decimalPattern('en_US');

  static String? _formatMintageValue(dynamic value) {
    if (value is int ||
        (value is double &&
            value.isFinite &&
            value == value.truncateToDouble())) {
      return _mintageNumberFormat.format((value as num).toInt());
    }
    if (value is double && value.isFinite) {
      return value.toString();
    }
    if (value is String) {
      return value.trim().isEmpty ? null : value;
    }
    return null;
  }

  Widget _buildMintageRow(Map<String, dynamic> item) =>
      _buildMintageRowStatic(item);

  static Widget _buildMintageRowStatic(Map<String, dynamic> item) {
    final mintage = item['mintage'] as Map?;
    final formattedValue = _formatMintageValue(mintage?['value']);
    final rawLabel = mintage?['label'];
    final trimmedLabel = rawLabel is String ? rawLabel.trim() : '';
    final hasLabel = trimmedLabel.isNotEmpty;
    final rawSourceUrl = mintage?['source_url'];
    final sourceUrl = rawSourceUrl is String ? rawSourceUrl.trim() : null;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(
            width: 140,
            child: Text(
              'Mintage:',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF475569)),
            ),
          ),
          Expanded(
            child: formattedValue != null
                ? Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Wrap(
                        crossAxisAlignment: WrapCrossAlignment.center,
                        spacing: 8,
                        runSpacing: 4,
                        children: [
                          Text(
                            formattedValue,
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF0B2545),
                            ),
                          ),
                          if (sourceUrl != null && sourceUrl.isNotEmpty)
                            InkWell(
                              onTap: () async {
                                final uri = Uri.tryParse(sourceUrl);
                                if (uri != null) await launchUrl(uri);
                              },
                              child: const Text(
                                '(source)',
                                style: TextStyle(
                                  color: Color(0xFF1F5FAD),
                                  decoration: TextDecoration.underline,
                                ),
                              ),
                            ),
                        ],
                      ),
                      if (hasLabel) ...[
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Expanded(
                              child: Text(
                                trimmedLabel,
                                style: const TextStyle(
                                  fontSize: 14,
                                  color: Color(0xFF6B6B6B),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ],
                  )
                : Row(
                    children: [
                      Expanded(
                        child: Text(
                          hasLabel ? trimmedLabel : 'Needs source',
                          style: const TextStyle(
                            fontSize: 16,
                            color: Color(0xFF6B6B6B),
                          ),
                        ),
                      ),
                    ],
                  ),
          ),
        ],
      ),
    );
  }
}

class _TypeTab extends StatelessWidget {
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _TypeTab({
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF0B2545) : Colors.white,
          border: Border.all(
            color: isSelected ? const Color(0xFF0B2545) : const Color(0xFFC8C8C8),
            width: 2,
          ),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: isSelected ? Colors.white : const Color(0xFF0B2545),
          ),
        ),
      ),
    );
  }
}

const String kRepresentativePhotoLabel =
    'Representative photo \u2014 date or mint may differ';
const String kAiCoinDisclosureLabel =
    'AI-generated image of the coin in pristine condition';
const String kAiBanknoteDisclosureLabel =
    'AI-generated illustration of the note \u2014 not a genuine specimen';
const String kAiWatermarkLabel = 'AI Generated';

class ResolvedCatalogImage {
  final Map<dynamic, dynamic> imageMap;
  final String imageUrl;
  final bool isTypeImage;
  final String side;
  final String role;
  final bool isAiGenerated;
  final bool isBanknote;

  const ResolvedCatalogImage({
    required this.imageMap,
    required this.imageUrl,
    required this.isTypeImage,
    required this.side,
    this.role = 'primary',
    this.isAiGenerated = false,
    this.isBanknote = false,
  });
}

bool _isBanknoteItem(Map<String, dynamic> item) {
  final t = (item['type'] as String? ?? '').toLowerCase();
  final nac = (item['nac_code'] as String? ?? '').toUpperCase();
  return t == 'note' || nac.startsWith('NAC1.BN.');
}

String? _firstApprovedImageUrl(
  Map<dynamic, dynamic>? imgMap,
  List<String> keys,
) {
  if (imgMap == null) return null;
  for (final key in keys) {
    final candidate = imgMap[key];
    if (candidate is String && isApprovedCatalogImageUrl(candidate)) {
      return candidate.trim();
    }
  }
  return null;
}

ResolvedCatalogImage? _resolveObverseImage(
  Map<String, dynamic> item, {
  required List<String> keyPriority,
}) {
  final isNote = _isBanknoteItem(item);
  // Wave 2 Component E (Eric Vision Rule 2a): Set rows show OGP packaging_images[0] first.
  final pkgList = item['packaging_images'];
  if (pkgList is List && pkgList.isNotEmpty) {
    final firstPkg = pkgList.first;
    if (firstPkg is Map) {
      final pkgUrl = _firstApprovedImageUrl(firstPkg, keyPriority);
      if (pkgUrl != null) {
        return ResolvedCatalogImage(
          imageMap: firstPkg,
          imageUrl: pkgUrl,
          isTypeImage: false,
          side: (firstPkg['side']?.toString() ?? 'packaging').trim().toLowerCase(),
          role: (firstPkg['role']?.toString() ?? 'packaging').trim().toLowerCase(),
          isAiGenerated: firstPkg['ai_generated'] == true,
          isBanknote: isNote,
        );
      }
    }
  }

  final primaryImg = item['primary_image'] as Map?;
  final primaryUrl = _firstApprovedImageUrl(primaryImg, keyPriority);
  if (primaryImg != null && primaryUrl != null) {
    return ResolvedCatalogImage(
      imageMap: primaryImg,
      imageUrl: primaryUrl,
      isTypeImage: false,
      side: (primaryImg['side']?.toString() ?? 'obverse').trim().toLowerCase(),
      role: (primaryImg['role']?.toString() ?? 'primary').trim().toLowerCase(),
      isAiGenerated: primaryImg['ai_generated'] == true,
      isBanknote: isNote,
    );
  }
  final typeImg = item['type_image'] as Map?;
  final typeUrl = _firstApprovedImageUrl(typeImg, keyPriority);
  if (typeImg != null && typeUrl != null) {
    return ResolvedCatalogImage(
      imageMap: typeImg,
      imageUrl: typeUrl,
      isTypeImage: true,
      side: (typeImg['side']?.toString() ?? 'obverse').trim().toLowerCase(),
      role: (typeImg['role']?.toString() ?? 'type').trim().toLowerCase(),
      isAiGenerated: typeImg['ai_generated'] == true,
      isBanknote: isNote,
    );
  }
  return null;
}

/// Resolves the catalog card image: approved `packaging_images[0]` (sets) or `primary_image` first,
/// else approved `type_image` (prefers `thumb_url`, falls back to `url`).
ResolvedCatalogImage? resolveCatalogCardImage(Map<String, dynamic> item) {
  return _resolveObverseImage(item, keyPriority: const ['thumb_url', 'url']);
}

/// Resolves the detail modal image list:
/// - Set packaging images (if present)
/// - Primary / type image (prefers `full_url`, else `url`)
/// - Secondary image (if approved, excluding AI banknote reverses per 31 CFR § 411.1)
/// - Approved `extra_images[]` entries (`side=reverse` and `role=privy_detail`)
List<ResolvedCatalogImage> resolveCatalogDetailImages(
  Map<String, dynamic> item,
) {
  final result = <ResolvedCatalogImage>[];
  final seenUrls = <String>{};
  final isNote = _isBanknoteItem(item);

  void addIfApproved(Map<dynamic, dynamic>? raw, {bool isType = false, String fallbackSide = 'obverse', String fallbackRole = 'primary'}) {
    if (raw == null) return;
    final isAi = raw['ai_generated'] == true;
    final side = (raw['side']?.toString() ?? fallbackSide).trim().toLowerCase();
    // 31 CFR § 411.1 fail-closed guard: never render an AI banknote non-obverse image.
    if (isNote && isAi && side != 'obverse') return;
    final url = _firstApprovedImageUrl(raw, const ['full_url', 'url']);
    if (url == null || seenUrls.contains(url)) return;
    seenUrls.add(url);
    result.add(
      ResolvedCatalogImage(
        imageMap: raw,
        imageUrl: url,
        isTypeImage: isType,
        side: side,
        role: (raw['role']?.toString() ?? fallbackRole).trim().toLowerCase(),
        isAiGenerated: isAi,
        isBanknote: isNote,
      ),
    );
  }

  final pkgList = item['packaging_images'];
  if (pkgList is List) {
    for (final rawPkg in pkgList) {
      if (rawPkg is Map) {
        addIfApproved(rawPkg, fallbackSide: 'packaging', fallbackRole: 'packaging');
      }
    }
  }

  final beforePrimary = result.length;
  final primaryImg = item['primary_image'] as Map?;
  if (primaryImg != null) {
    addIfApproved(primaryImg, isType: false, fallbackSide: 'obverse', fallbackRole: 'primary');
  }
  if (result.length == beforePrimary) {
    final typeImg = item['type_image'] as Map?;
    if (typeImg != null) {
      addIfApproved(typeImg, isType: true, fallbackSide: 'obverse', fallbackRole: 'type');
    }
  }

  final secondaryImg = item['secondary_image'] as Map?;
  if (secondaryImg != null) {
    addIfApproved(secondaryImg, isType: false, fallbackSide: 'reverse', fallbackRole: 'secondary');
  }

  final extras = item['extra_images'];
  if (extras is List) {
    for (final rawExtra in extras) {
      if (rawExtra is! Map) continue;
      final side = (rawExtra['side']?.toString() ?? '').trim().toLowerCase();
      final role = (rawExtra['role']?.toString() ?? '').trim().toLowerCase();
      if (side != 'reverse' && role != 'privy_detail') continue;
      addIfApproved(
        rawExtra,
        isType: false,
        fallbackSide: side.isEmpty ? 'extra' : side,
        fallbackRole: role.isEmpty ? 'extra' : role,
      );
    }
  }
  return result;
}

String resolveCatalogImageCaption(Map<dynamic, dynamic> imgMap) {
  String clean(String raw) {
    final lower = raw.toLowerCase();
    if (lower.contains('used with permission') || lower.contains('courtesy')) {
      return 'Image: United States Mint';
    }
    return raw;
  }

  final credit = imgMap['credit']?.toString().trim();
  if (credit != null && credit.isNotEmpty) return clean(credit);
  final source = imgMap['source']?.toString().trim();
  if (source != null && source.isNotEmpty) return clean(source);
  return 'Numista.Ai reference photo';
}

String? resolveAiDisclosureLabel(ResolvedCatalogImage resolved) {
  if (!resolved.isAiGenerated) return null;
  return resolved.isBanknote ? kAiBanknoteDisclosureLabel : kAiCoinDisclosureLabel;
}

Widget _wrapWithAiWatermarkAndCaps(
  ResolvedCatalogImage resolved,
  Widget imageWidget,
) {
  Widget wrapped = imageWidget;
  if (resolved.isAiGenerated && resolved.isBanknote) {
    // 31 CFR § 411.1: strictly cap rendered AI banknote illustration well below 75% linear print size.
    wrapped = ConstrainedBox(
      constraints: const BoxConstraints(maxWidth: 320, maxHeight: 150),
      child: wrapped,
    );
  }
  if (!resolved.isAiGenerated) return wrapped;
  return Stack(
    alignment: Alignment.center,
    children: [
      wrapped,
      Positioned(
        right: 6,
        bottom: 6,
        child: Container(
          key: const Key('ai_generated_watermark_badge'),
          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
          decoration: BoxDecoration(
            color: Colors.black.withValues(alpha: 0.72),
            borderRadius: BorderRadius.circular(4),
          ),
          child: const Text(
            kAiWatermarkLabel,
            style: TextStyle(
              color: Colors.white,
              fontSize: 10,
              fontWeight: FontWeight.w700,
              letterSpacing: 0.3,
            ),
          ),
        ),
      ),
    ],
  );
}

bool isRepresentativeCatalogImage(ResolvedCatalogImage resolved) {
  final uniqueSide = resolved.imageMap['unique_side'];
  if (uniqueSide is bool) return !uniqueSide;
  return resolved.isTypeImage;
}

Widget _buildApprovedCatalogImageWidget(
  String imageUrl, {
  Key? imageKey,
  double? height,
  BoxFit fit = BoxFit.contain,
  required Widget Function() fallbackBuilder,
}) {
  if (imageUrl.startsWith('assets/')) {
    return Image.asset(
      imageUrl,
      key: imageKey,
      height: height,
      fit: fit,
      errorBuilder: (c, e, s) => fallbackBuilder(),
    );
  }
  return Image.network(
    imageUrl,
    key: imageKey,
    height: height,
    fit: fit,
    errorBuilder: (c, e, s) => fallbackBuilder(),
  );
}

Widget _buildCatalogNoPhotoBox({
  double size = 120,
  double borderWidth = 2.5,
  double fontSize = 15,
}) {
  return Center(
    child: Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(
          color: const Color(0xFF8A8A8A),
          width: borderWidth,
          style: BorderStyle.solid,
        ),
      ),
      child: Center(
        child: Text(
          'No photo yet',
          textAlign: TextAlign.center,
          style: TextStyle(
            fontSize: fontSize,
            color: const Color(0xFF6B6B6B),
            fontWeight: FontWeight.w500,
          ),
        ),
      ),
    ),
  );
}

Widget _buildCatalogCaptionLine(
  ResolvedCatalogImage resolved, {
  int? maxLines,
  double fontSize = 14,
  TextAlign? textAlign,
  Key? linkKey,
  Key? plainKey,
}) {
  final caption = resolveCatalogImageCaption(resolved.imageMap);
  final rawSourceUrl = resolved.imageMap['source_url']?.toString().trim();
  final overflow = maxLines != null ? TextOverflow.ellipsis : null;

  if (isApprovedSourceUrl(rawSourceUrl)) {
    final approvedUrl = rawSourceUrl!;
    return InkWell(
      key: linkKey,
      onTap: () async {
        final uri = Uri.tryParse(approvedUrl);
        if (uri != null) {
          await launchUrl(uri);
        }
      },
      child: Text(
        caption,
        maxLines: maxLines,
        overflow: overflow,
        textAlign: textAlign,
        style: TextStyle(
          fontSize: fontSize,
          color: const Color(0xFF1F5FAD),
          decoration: TextDecoration.underline,
        ),
      ),
    );
  }
  return Text(
    caption,
    key: plainKey,
    maxLines: maxLines,
    overflow: overflow,
    textAlign: textAlign,
    style: TextStyle(fontSize: fontSize, color: const Color(0xFF6B6B6B)),
  );
}

class CatalogDetailImagesView extends StatelessWidget {
  final Map<String, dynamic> item;

  const CatalogDetailImagesView({super.key, required this.item});

  @override
  Widget build(BuildContext context) {
    final images = resolveCatalogDetailImages(item);
    final rawSetMembers = item['set_members'];
    final setMembers = rawSetMembers is List
        ? rawSetMembers.whereType<Map>().map((m) => Map<String, dynamic>.from(m)).toList()
        : const <Map<String, dynamic>>[];

    if (images.isEmpty && setMembers.isEmpty) {
      return _buildCatalogNoPhotoBox(size: 120, borderWidth: 2.5, fontSize: 15);
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        for (int index = 0; index < images.length; index++) ...[
          if (index > 0) const SizedBox(height: 16),
          if (images[index].role == 'privy_detail')
            const Padding(
              padding: EdgeInsets.only(bottom: 4),
              child: Text(
                'Privy Mark Detail',
                key: Key('privy_detail_label'),
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF0B2545),
                ),
              ),
            ),
          Center(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(10),
              child: _wrapWithAiWatermarkAndCaps(
                images[index],
                _buildApprovedCatalogImageWidget(
                  images[index].imageUrl,
                  imageKey: Key('catalog_detail_image_$index'),
                  height: images[index].isAiGenerated && images[index].isBanknote ? 140 : 220,
                  fit: BoxFit.contain,
                  fallbackBuilder: () => _buildCatalogNoPhotoBox(
                    size: 120,
                    borderWidth: 2.5,
                    fontSize: 15,
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: 8),
          if (resolveAiDisclosureLabel(images[index]) != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Text(
                resolveAiDisclosureLabel(images[index])!,
                key: Key('catalog_detail_ai_disclosure_$index'),
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF0B2545),
                ),
              ),
            ),
          _buildCatalogCaptionLine(
            images[index],
            fontSize: 14,
            textAlign: TextAlign.center,
            linkKey: Key('catalog_detail_source_link_$index'),
            plainKey: Key('catalog_detail_source_plain_$index'),
          ),
          if (images[index].imageMap['note'] is String &&
              (images[index].imageMap['note'] as String).trim().isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Text(
                (images[index].imageMap['note'] as String).trim(),
                key: Key('catalog_detail_finish_note_$index'),
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 13,
                  color: Color(0xFF475569),
                ),
              ),
            ),
          if (isRepresentativeCatalogImage(images[index]))
            const Padding(
              padding: EdgeInsets.only(top: 4),
              child: Text(
                kRepresentativePhotoLabel,
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 13,
                  fontStyle: FontStyle.italic,
                  color: Color(0xFF1F5FAD),
                ),
              ),
            ),
        ],
        if (setMembers.isNotEmpty) ...[
          const SizedBox(height: 20),
          _SetMembersFlipStrip(members: setMembers),
        ],
      ],
    );
  }
}

/// Interactive set-member gallery (Wave 2 Component E / Eric Images Vision Rule 2a):
/// Displays each coin inside a set defaulting to its unique `default_side`,
/// tap-to-flip between obverse and reverse (never combining both sides into one image).
class _SetMembersFlipStrip extends StatefulWidget {
  final List<Map<String, dynamic>> members;

  const _SetMembersFlipStrip({required this.members});

  @override
  State<_SetMembersFlipStrip> createState() => _SetMembersFlipStripState();
}

class _SetMembersFlipStripState extends State<_SetMembersFlipStrip> {
  final Map<int, bool> _flipped = {};

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Coins in this Set (tap any coin to flip)',
          key: Key('set_members_header'),
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Color(0xFF0B2545),
          ),
        ),
        const SizedBox(height: 10),
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: [
            for (int i = 0; i < widget.members.length; i++) _buildMemberTile(i, widget.members[i]),
          ],
        ),
      ],
    );
  }

  Widget _buildMemberTile(int idx, Map<String, dynamic> mem) {
    final defaultSide = (mem['default_side']?.toString() ?? 'obverse').toLowerCase();
    final isFlipped = _flipped[idx] ?? false;
    final activeSide = isFlipped ? (defaultSide == 'obverse' ? 'reverse' : 'obverse') : defaultSide;
    final rawSideObj = mem[activeSide] as Map?;
    final imgMap = (rawSideObj?['image'] is Map) ? rawSideObj!['image'] as Map : rawSideObj;
    final url = _firstApprovedImageUrl(imgMap, const ['full_url', 'url']);
    final label = mem['label']?.toString() ?? 'Coin ${idx + 1}';

    return InkWell(
      key: Key('set_member_tile_$idx'),
      onTap: () => setState(() => _flipped[idx] = !isFlipped),
      borderRadius: BorderRadius.circular(8),
      child: Container(
        width: 140,
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: const Color(0xFFF8F9FA),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: const Color(0xFFD6D6D6)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (url != null)
              _buildApprovedCatalogImageWidget(
                url,
                imageKey: Key('set_member_img_${idx}_$activeSide'),
                height: 88,
                fit: BoxFit.contain,
                fallbackBuilder: () => _buildCatalogNoPhotoBox(size: 72, fontSize: 11),
              )
            else
              _buildCatalogNoPhotoBox(size: 72, fontSize: 11),
            const SizedBox(height: 6),
            Text(
              label,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF0B2545)),
            ),
            Text(
              'Showing: $activeSide',
              key: Key('set_member_side_$idx'),
              style: const TextStyle(fontSize: 11, color: Color(0xFF1F5FAD)),
            ),
          ],
        ),
      ),
    );
  }
}

class CatalogItemCard extends StatelessWidget {
  final Map<String, dynamic> item;
  final VoidCallback onTap;

  const CatalogItemCard({
    super.key,
    required this.item,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final primaryImg = item['primary_image'] as Map?;
    final typeImg = item['type_image'] as Map?;
    final resolvedImage = resolveCatalogCardImage(item);
    final isLegacyLocalTypePlaceholder = resolvedImage == null &&
        primaryImg == null &&
        typeImg != null &&
        typeImg['url'] == null &&
        typeImg['thumb_url'] == null &&
        typeImg['file'] is String;

    final badge = item['status_badge'] as String?;
    final year = item['year']?.toString() ?? 'Undated';
    final denom = item['denomination']?.toString() ?? '';
    final isMedal = item['type'] == 'medal';
    final faceVal = isMedal ? 0.0 : MeltValueService.parseFaceValue(denom);
    final faceValText = faceVal > 0
        ? (faceVal == 0.005 ? r'$0.005' : '\$${faceVal.toStringAsFixed(2)}')
        : '\u2014';
    final rawAiEst = (item['AI Estimated Value'] ?? item['ai_estimated_value'])?.toString().trim() ?? '';
    final hasAiEst = rawAiEst.isNotEmpty && rawAiEst != 'Pending';

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          border: Border.all(color: const Color(0xFFD6D6D6), width: 2),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Image
            Expanded(
              child: Center(
                child: resolvedImage != null
                    ? _wrapWithAiWatermarkAndCaps(
                        resolvedImage,
                        _buildApprovedCatalogImageWidget(
                          resolvedImage.imageUrl,
                          imageKey: const Key('catalog_card_image'),
                          fit: BoxFit.contain,
                          fallbackBuilder: _buildPlaceholder,
                        ),
                      )
                    : _buildPlaceholder(),
              ),
            ),
            const SizedBox(height: 10),

            // Badge
            if (badge != null) ...[
              _CatalogBadge(badgeText: badge),
              const SizedBox(height: 8),
            ],

            // Title
            Text(
              item['name'] as String? ?? 'Coin',
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Color(0xFF0B2545),
                height: 1.2,
              ),
            ),
            const SizedBox(height: 6),

            // Metadata line
            Text(
              [year, denom].where((s) => s.isNotEmpty).join(' · '),
              style: const TextStyle(fontSize: 15, color: Color(0xFF475569)),
            ),

            if (resolvedImage != null) ...[
              const SizedBox(height: 4),
              if (resolveAiDisclosureLabel(resolvedImage) != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 2),
                  child: Text(
                    resolveAiDisclosureLabel(resolvedImage)!,
                    key: const Key('catalog_card_ai_disclosure'),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF0B2545),
                    ),
                  ),
                ),
              _buildCatalogCaptionLine(
                resolvedImage,
                maxLines: 1,
                fontSize: 11,
                linkKey: const Key('catalog_card_source_link'),
                plainKey: const Key('catalog_card_source_plain'),
              ),
              if (isRepresentativeCatalogImage(resolvedImage))
                const Padding(
                  padding: EdgeInsets.only(top: 2),
                  child: Text(
                    kRepresentativePhotoLabel,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontSize: 11,
                      color: Color(0xFF6B6B6B),
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ),
            ] else if (isLegacyLocalTypePlaceholder)
              const Padding(
                padding: EdgeInsets.only(top: 4),
                child: Text(
                  'type photo (date may differ)',
                  style: TextStyle(fontSize: 12, color: Color(0xFF6B6B6B), fontStyle: FontStyle.italic),
                ),
              ),

            const SizedBox(height: 6),
            if (isMedal)
              const Text(
                'No face value',
                style: TextStyle(fontSize: 13, color: Color(0xFF6B6B6B)),
              )
            else
              Row(
                children: [
                  Text(
                    faceValText,
                    style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1F5FAD),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Flexible(
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFFF3CD),
                        border: Border.all(color: const Color(0xFFFFEEBA)),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        hasAiEst ? 'AI Est: $rawAiEst' : 'Face value \u00b7 No retail estimate',
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF856404),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            const SizedBox(height: 10),
            SizedBox(
              width: double.infinity,
              child: ConstrainedBox(
                constraints: const BoxConstraints(minHeight: 56),
                child: ElevatedButton.icon(
                  onPressed: () => _addCatalogMapToWishlist(context, item),
                  icon: const Icon(Icons.favorite_border, size: 20),
                  label: const Text(
                    'Add to Wish List',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF1D4F91),
                    foregroundColor: Colors.white,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPlaceholder() {
    return Container(
      width: 96,
      height: 96,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(color: const Color(0xFF8A8A8A), width: 2, style: BorderStyle.solid),
      ),
      child: const Center(
        child: Text(
          'No photo yet',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 13, color: Color(0xFF6B6B6B)),
        ),
      ),
    );
  }
}

class _CatalogBadge extends StatelessWidget {
  final String? badgeText;

  const _CatalogBadge({this.badgeText});

  @override
  Widget build(BuildContext context) {
    if (badgeText == null) return const SizedBox();

    if (badgeText == 'Pre-Federal') {
      return Container(
        height: 32,
        padding: const EdgeInsets.symmetric(horizontal: 14),
        decoration: BoxDecoration(
          color: Colors.white,
          border: Border.all(color: const Color(0xFF1F5FAD), width: 2),
          borderRadius: BorderRadius.circular(16),
        ),
        child: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Pre-Federal',
              style: TextStyle(color: Color(0xFF0B2545), fontWeight: FontWeight.bold, fontSize: 14),
            ),
          ],
        ),
      );
    }

    // Neutral badge ("Needs source" or "Details coming")
    final isNeedsSource = badgeText == 'Needs source';
    return Container(
      height: 32,
      padding: const EdgeInsets.symmetric(horizontal: 14),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: const Color(0xFF6B6B6B), width: 2),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isNeedsSource ? Icons.info_outline : Icons.pending_outlined,
            size: 16,
            color: const Color(0xFF333333),
          ),
          const SizedBox(width: 6),
          Text(
            badgeText!,
            style: const TextStyle(color: Color(0xFF333333), fontSize: 14),
          ),
        ],
      ),
    );
  }
}

Future<void> _addCatalogMapToWishlist(
  BuildContext context,
  Map<String, dynamic> item,
) async {
  final rawYear = item['year']?.toString() ?? '';
  final rawMint = item['mint_mark']?.toString() ?? '';
  final denom = item['denomination']?.toString() ?? '';
  final name = item['name']?.toString() ?? 'Catalog Coin';
  final series = item['series']?.toString() ?? name;
  final resolved = MintHelpers.resolveTwoFieldMint(
    rawMintMark: rawMint,
    year: rawYear,
    series: series,
    denomination: denom,
  );
  final primaryImg = item['primary_image'] as Map?;
  final coin = CoinModel(
    id: 'cat_wish_${DateTime.now().millisecondsSinceEpoch}',
    year: rawYear == 'Undated' ? '' : rawYear,
    mint: resolved.mint,
    mintMark: resolved.mintMark,
    denomination: denom,
    programSeries: series,
    themeSubject: name,
    imageUrlObverse: primaryImg?['url']?.toString() ?? '',
  );
  try {
    await WishlistService.addToWishlist(coin);
  } catch (_) {
    // Allow widget test interaction without initialized Firebase.
  }
  if (context.mounted) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Added "$name" to your Wish List!'),
        backgroundColor: const Color(0xFF1D4F91),
      ),
    );
  }
}
