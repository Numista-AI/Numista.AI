import 'package:flutter/material.dart';
import '../../services/catalog/catalog_service.dart';
import '../../widgets/catalog/catalog_inspector_panel.dart';
import '../../widgets/catalog/dual_sided_catalog_card.dart';

/// U.S. Numismatics Master Catalog (1776 - 2026) Desktop/Tablet Web Screen.
///
/// Implements Plan.v2.1 §6:
/// - 1776-2026 Chronological Timeline Bar + Era quick-jump pills
/// - Pre-Federal State/Entity secondary facet (`CONTINENTAL`, `CT`, etc.)
/// - Category tabs (`ALL`, `CN`, `BN`, `MD`, `FS`)
/// - Mint / Facility filter bar (`P`, `D`, `S`, `W`, `DD` Dahlonega, `M` Mexico City, `BEP`, `XX`)
/// - Global `Flip All Cards` toggle + per-card Unique Identity Side default (`defaultFace`)
/// - 8-col Browse Grid + 4-col Sticky Specimen Inspector Panel
class UsNumismaticsCatalogScreen extends StatefulWidget {
  final List<CatalogItemModel>? initialItems;
  final bool isAuthenticated;

  const UsNumismaticsCatalogScreen({
    super.key,
    this.initialItems,
    this.isAuthenticated = false,
  });

  @override
  State<UsNumismaticsCatalogScreen> createState() =>
      _UsNumismaticsCatalogScreenState();
}

class _UsNumismaticsCatalogScreenState
    extends State<UsNumismaticsCatalogScreen> {
  late final List<CatalogItemModel> _allItems;
  String? _selectedKind;
  String? _selectedCc;
  String? _selectedEra;
  String? _selectedState;
  String? _selectedFacility;
  int _maxYear = 2026;
  String _searchQuery = '';
  bool _flipAllReverse = false;
  CatalogItemModel? _selectedItem;
  String? _statusBanner;

  final Map<String, CollectionEntryState> _collectionEntries = {};

  @override
  void initState() {
    super.initState();
    _allItems = widget.initialItems ?? UsNumismaticsCatalogService.seedItems;
    if (_allItems.isNotEmpty) {
      _selectedItem = _allItems.first;
    }
  }

  List<CatalogItemModel> get _filteredItems {
    return UsNumismaticsCatalogService.filterItems(
      _allItems,
      kind: _selectedKind,
      cc: _selectedCc,
      era: _selectedEra,
      facility: _selectedFacility,
      state: _selectedState,
      maxYear: _maxYear,
      query: _searchQuery,
    );
  }

  void _handleAddToCollection(CatalogItemModel item) {
    setState(() {
      final existing = _collectionEntries[item.nacCode];
      if (existing != null) {
        _statusBanner =
            'Already in Collection: users/{uid}/${existing.collection}/${existing.docId}';
        return;
      }
      final entry = CollectionEntryState(
        nacCode: item.nacCode,
        collection: item.targetCollection,
        docId: item.deterministicDocId,
        usePersonalPhoto: false,
        customObverseImageUrl: 'https://storage.numista.ai/user/specimen_obv.jpg',
        stockObverseImageUrl: item.obverseImageUrl,
        stockReverseImageUrl: item.reverseImageUrl,
      );
      _collectionEntries[item.nacCode] = entry;
      _statusBanner =
          'Added to /${entry.collection} as ${entry.docId} (Kind=${item.kind})';
    });
  }

  void _handleTogglePersonalPhoto(CatalogItemModel item, bool usePersonal) {
    setState(() {
      final existing = _collectionEntries[item.nacCode];
      if (existing == null) return;
      _collectionEntries[item.nacCode] = existing.copyWith(
        usePersonalPhoto: usePersonal,
      );
      _statusBanner = usePersonal
          ? 'Switched ${item.nacCode} to Personal Specimen Photo (Stock backup preserved)'
          : 'Switched ${item.nacCode} to Stock Catalog Photo';
    });
  }

  void _handleImageDownloadRequest(CatalogItemModel item) {
    final allowed = UsNumismaticsCatalogService.canDownloadImage(
      isAuthenticated: widget.isAuthenticated,
    );
    setState(() {
      if (!allowed) {
        _statusBanner =
            'IMAGE_DOWNLOAD_REQUIRES_ACCOUNT: Sign in to download hi-res catalog images.';
      } else {
        _statusBanner = 'Downloading hi-res plate for ${item.nacCode}...';
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final filtered = _filteredItems;
    final activeInspectorItem =
        (filtered.contains(_selectedItem) ? _selectedItem : null) ??
            (filtered.isNotEmpty ? filtered.first : _selectedItem);

    return Scaffold(
      backgroundColor: CatalogVaultPalette.obsidianBg,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 1. Top Header Bar: Brand, Search, and Flip All Cards toggle
              _buildTopHeaderBar(filtered.length),
              const SizedBox(height: 10),

              // 2. 1776-2026 Timeline & Era Quick-Jump Bar
              _buildEraAndYearBar(),
              if (_selectedEra == 'PRE_FEDERAL') ...[
                const SizedBox(height: 8),
                _buildPreFederalStateBar(),
              ],
              const SizedBox(height: 8),

              // 3. Category Tabs + Mint/Facility Filter Bar
              _buildCategoryAndFacilityFilters(),
              if (_statusBanner != null) ...[
                const SizedBox(height: 8),
                Container(
                  key: const Key('catalog_status_banner'),
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: const Color(0xFF17253B),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: CatalogVaultPalette.verifyCyan),
                  ),
                  child: Text(
                    _statusBanner!,
                    style: const TextStyle(
                      color: CatalogVaultPalette.verifyCyan,
                      fontSize: 11,
                      fontFamily: 'monospace',
                    ),
                  ),
                ),
              ],
              const SizedBox(height: 12),

              // 4. Main 12-Column Responsive Split (8-col Grid + 4-col Sticky Inspector)
              Expanded(
                child: LayoutBuilder(
                  builder: (context, constraints) {
                    final isWide = constraints.maxWidth >= 900;
                    if (isWide) {
                      return Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(
                            flex: 8,
                            child: _buildCatalogGrid(
                              filtered,
                              crossAxisCount:
                                  constraints.maxWidth >= 1280 ? 3 : 2,
                            ),
                          ),
                          const SizedBox(width: 16),
                          if (activeInspectorItem != null)
                            Expanded(
                              flex: 4,
                              child: CatalogInspectorPanel(
                                item: activeInspectorItem,
                                isAuthenticated: widget.isAuthenticated,
                                collectionEntry: _collectionEntries[
                                    activeInspectorItem.nacCode],
                                onAddToCollection: () =>
                                    _handleAddToCollection(activeInspectorItem),
                                onTogglePersonalPhoto: (val) =>
                                    _handleTogglePersonalPhoto(
                                      activeInspectorItem,
                                      val,
                                    ),
                                onRequestImageDownload: () =>
                                    _handleImageDownloadRequest(
                                      activeInspectorItem,
                                    ),
                              ),
                            ),
                        ],
                      );
                    }
                    // Tablet / compact split
                    return Column(
                      children: [
                        Expanded(
                          flex: 6,
                          child: _buildCatalogGrid(
                            filtered,
                            crossAxisCount: constraints.maxWidth >= 600 ? 2 : 1,
                          ),
                        ),
                        if (activeInspectorItem != null) ...[
                          const SizedBox(height: 12),
                          Expanded(
                            flex: 5,
                            child: CatalogInspectorPanel(
                              item: activeInspectorItem,
                              isAuthenticated: widget.isAuthenticated,
                              collectionEntry: _collectionEntries[
                                  activeInspectorItem.nacCode],
                              onAddToCollection: () =>
                                  _handleAddToCollection(activeInspectorItem),
                              onTogglePersonalPhoto: (val) =>
                                  _handleTogglePersonalPhoto(
                                    activeInspectorItem,
                                    val,
                                  ),
                              onRequestImageDownload: () =>
                                  _handleImageDownloadRequest(
                                    activeInspectorItem,
                                  ),
                            ),
                          ),
                        ],
                      ],
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTopHeaderBar(int count) {
    return Wrap(
      spacing: 12,
      runSpacing: 8,
      alignment: WrapAlignment.spaceBetween,
      crossAxisAlignment: WrapCrossAlignment.center,
      children: [
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(
              Icons.account_balance,
              color: CatalogVaultPalette.bullionGold,
              size: 22,
            ),
            const SizedBox(width: 8),
            const Text(
              'U.S. NUMISMATICS MASTER CATALOG (1776 – 2026)',
              style: TextStyle(
                color: CatalogVaultPalette.textPrimary,
                fontSize: 16,
                fontWeight: FontWeight.w800,
                letterSpacing: 0.5,
              ),
            ),
            const SizedBox(width: 10),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: CatalogVaultPalette.slateSurface,
                borderRadius: BorderRadius.circular(4),
                border: Border.all(color: CatalogVaultPalette.borderHairline),
              ),
              child: Text(
                '$count SPECIMENS',
                key: const Key('catalog_result_count'),
                style: const TextStyle(
                  color: CatalogVaultPalette.bullionGold,
                  fontSize: 11,
                  fontFamily: 'monospace',
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
          ],
        ),
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: 240,
              height: 36,
              child: TextField(
                key: const Key('catalog_search_input'),
                onChanged: (v) => setState(() => _searchQuery = v),
                style: const TextStyle(
                  color: CatalogVaultPalette.textPrimary,
                  fontSize: 12,
                ),
                decoration: InputDecoration(
                  hintText: 'Search NAC1, year, series, title...',
                  hintStyle: const TextStyle(
                    color: CatalogVaultPalette.textMuted,
                    fontSize: 11,
                  ),
                  prefixIcon: const Icon(
                    Icons.search,
                    size: 16,
                    color: CatalogVaultPalette.textMuted,
                  ),
                  filled: true,
                  fillColor: CatalogVaultPalette.slateSurface,
                  contentPadding: const EdgeInsets.symmetric(vertical: 0),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: const BorderSide(
                      color: CatalogVaultPalette.borderHairline,
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 10),
            OutlinedButton.icon(
              key: const Key('flip_all_cards_btn'),
              onPressed: () {
                setState(() {
                  _flipAllReverse = !_flipAllReverse;
                });
              },
              icon: const Icon(
                Icons.flip,
                size: 15,
                color: CatalogVaultPalette.bullionGold,
              ),
              label: Text(
                _flipAllReverse ? 'Showing Reverses' : 'Flip All Cards',
                style: const TextStyle(
                  color: CatalogVaultPalette.textPrimary,
                  fontSize: 11,
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildEraAndYearBar() {
    const eras = [
      (null, 'ALL ERAS (1776–2026)'),
      ('PRE_FEDERAL', 'PRE-FEDERAL / COLONIAL (CO)'),
      ('FOREIGN_CIRCULATING', 'FOREIGN SPECIE (FS ≤1857)'),
      ('FEDERAL', 'FEDERAL U.S. (US)'),
      ('US_PHILIPPINES', 'U.S. PHILIPPINES (PF)'),
    ];

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: CatalogVaultPalette.slateSurface,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: CatalogVaultPalette.borderHairline),
      ),
      child: Wrap(
        spacing: 8,
        runSpacing: 6,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          ...eras.map((entry) {
            final isActive = _selectedEra == entry.$1;
            return ChoiceChip(
              key: Key('era_chip_${entry.$1 ?? "ALL"}'),
              label: Text(
                entry.$2,
                style: TextStyle(
                  color: isActive
                      ? CatalogVaultPalette.obsidianBg
                      : CatalogVaultPalette.textPrimary,
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                ),
              ),
              selected: isActive,
              selectedColor: CatalogVaultPalette.bullionGold,
              backgroundColor: CatalogVaultPalette.elevatedWell,
              onSelected: (_) {
                setState(() {
                  _selectedEra = entry.$1;
                  if (_selectedEra != 'PRE_FEDERAL') {
                    _selectedState = null;
                  }
                });
              },
            );
          }),
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Year ≤ $_maxYear',
                style: const TextStyle(
                  color: CatalogVaultPalette.verifyCyan,
                  fontSize: 11,
                  fontFamily: 'monospace',
                ),
              ),
              SizedBox(
                width: 150,
                child: Slider(
                  key: const Key('catalog_year_slider'),
                  min: 1776,
                  max: 2026,
                  divisions: 250,
                  value: _maxYear.toDouble(),
                  activeColor: CatalogVaultPalette.bullionGold,
                  onChanged: (v) => setState(() => _maxYear = v.round()),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPreFederalStateBar() {
    const states = [
      (null, 'All Pre-Federal Entities'),
      ('CONTINENTAL', 'Continental Congress'),
      ('CT', 'Connecticut (CT)'),
      ('MA', 'Massachusetts (MA)'),
      ('VT', 'Vermont (VT)'),
      ('NJ', 'New Jersey (NJ)'),
    ];
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: states.map((st) {
          final isActive = _selectedState == st.$1;
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: ActionChip(
              key: Key('state_chip_${st.$1 ?? "ALL"}'),
              backgroundColor: isActive
                  ? CatalogVaultPalette.verifyCyan
                  : CatalogVaultPalette.elevatedWell,
              label: Text(
                st.$2,
                style: TextStyle(
                  color: isActive
                      ? CatalogVaultPalette.obsidianBg
                      : CatalogVaultPalette.textPrimary,
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                ),
              ),
              onPressed: () => setState(() => _selectedState = st.$1),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildCategoryAndFacilityFilters() {
    const kinds = [
      (null, null, 'ALL TYPES'),
      ('CN', null, 'COINS (CN)'),
      ('BN', null, 'BANK NOTES (BN)'),
      ('MD', null, 'MEDALS & TOKENS (MD/PRV)'),
      (null, 'FS', 'FOREIGN SPECIE (FS)'),
    ];

    const facilities = [
      (null, 'ALL MINTS/FAC'),
      ('P', 'P (Philadelphia)'),
      ('D', 'D (Denver)'),
      ('S', 'S (San Francisco)'),
      ('W', 'W (West Point)'),
      ('DD', 'DD (Dahlonega)'),
      ('M', 'M (Mexico City)'),
      ('BEP', 'BEP (Engraving & Printing)'),
      ('XX', 'XX (Private / Colonial)'),
    ];

    return Wrap(
      spacing: 8,
      runSpacing: 6,
      children: [
        ...kinds.map((k) {
          final isActive = _selectedKind == k.$1 && _selectedCc == k.$2;
          final keySuffix = k.$2 ?? k.$1 ?? 'ALL';
          return FilterChip(
            key: Key('kind_tab_$keySuffix'),
            selected: isActive,
            selectedColor: CatalogVaultPalette.bullionGold,
            backgroundColor: CatalogVaultPalette.slateSurface,
            label: Text(
              k.$3,
              style: TextStyle(
                color: isActive
                    ? CatalogVaultPalette.obsidianBg
                    : CatalogVaultPalette.textPrimary,
                fontSize: 11,
                fontWeight: FontWeight.w700,
              ),
            ),
            onSelected: (_) {
              setState(() {
                _selectedKind = k.$1;
                _selectedCc = k.$2;
              });
            },
          );
        }),
        const SizedBox(width: 8),
        ...facilities.map((f) {
          final isActive = _selectedFacility == f.$1;
          return ActionChip(
            key: Key('fac_chip_${f.$1 ?? "ALL"}'),
            backgroundColor: isActive
                ? CatalogVaultPalette.verifyCyan
                : CatalogVaultPalette.slateSurface,
            label: Text(
              f.$2,
              style: TextStyle(
                color: isActive
                    ? CatalogVaultPalette.obsidianBg
                    : CatalogVaultPalette.textMuted,
                fontSize: 10,
                fontFamily: 'monospace',
                fontWeight: FontWeight.w700,
              ),
            ),
            onPressed: () => setState(() => _selectedFacility = f.$1),
          );
        }),
      ],
    );
  }

  Widget _buildCatalogGrid(
    List<CatalogItemModel> items, {
    required int crossAxisCount,
  }) {
    if (items.isEmpty) {
      return const Center(
        child: Text(
          'No catalog specimens match the active filters.',
          style: TextStyle(color: CatalogVaultPalette.textMuted, fontSize: 14),
        ),
      );
    }
    return GridView.builder(
      key: const Key('catalog_browse_grid'),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: crossAxisCount,
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        childAspectRatio: 0.92,
      ),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final item = items[index];
        return DualSidedCatalogCard(
          item: item,
          isSelected: _selectedItem?.nacCode == item.nacCode,
          flipAllReverse: _flipAllReverse,
          collectionEntry: _collectionEntries[item.nacCode],
          onSelect: () => setState(() => _selectedItem = item),
          onAddToCollection: () => _handleAddToCollection(item),
          onTogglePersonalPhoto: (val) => _handleTogglePersonalPhoto(item, val),
        );
      },
    );
  }
}
