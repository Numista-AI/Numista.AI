import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../services/melt_value_service.dart';

class CatalogBrowseScreen extends StatefulWidget {
  final String? initialQuery;
  final String? initialNacCode;

  const CatalogBrowseScreen({
    super.key,
    this.initialQuery,
    this.initialNacCode,
  });

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
      final jsonString = await rootBundle.loadString('assets/catalog/catalog_public_v1.json');
      final List<dynamic> raw = json.decode(jsonString);
      final List<Map<String, dynamic>> entries = raw.map((e) => Map<String, dynamic>.from(e as Map)).toList();

      if (mounted) {
        setState(() {
          _allEntries = entries;
          _isLoading = false;
          _applyFilters();
        });

        if (widget.initialNacCode != null && widget.initialNacCode!.trim().isNotEmpty) {
          final targetNac = widget.initialNacCode!.trim().toLowerCase();
          final match = _allEntries.firstWhere(
            (e) => (e['nac_code'] as String? ?? '').toLowerCase() == targetNac,
            orElse: () => <String, dynamic>{},
          );
          if (match.isNotEmpty) {
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (mounted) {
                _showItemDetailModal(match);
              }
            });
          } else {
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(
                      'We don\'t have item "${widget.initialNacCode}" in our reference catalog yet.',
                      style: const TextStyle(fontSize: 16),
                    ),
                    backgroundColor: const Color(0xFF0B2545),
                    duration: const Duration(seconds: 4),
                  ),
                );
              }
            });
          }
        }
      }
    } catch (e) {
      debugPrint('[Catalog] Failed to load catalog_public_v1.json: $e');
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  void _applyFilters() {
    if (_selectedType == 'foreign') {
      _filteredEntries = [];
      return;
    }

    final query = _searchQuery.trim().toLowerCase();

    List<Map<String, dynamic>> filtered = _allEntries.where((item) {
      // Type filter
      final type = (item['type'] as String? ?? '').toLowerCase();
      if (_selectedType == 'coin' && type != 'coin') return false;
      if (_selectedType == 'note' && type != 'note') return false;
      if (_selectedType == 'medal' && type != 'medal') return false;

      // Era filter
      final int? year = item['year'] is int ? item['year'] as int : null;
      if (_selectedEra != 'all') {
        if (_selectedEra == 'pre_federal') {
          if (year == null || year >= 1792) return false;
        } else if (_selectedEra == 'early_republic') {
          if (year == null || year < 1792 || year >= 1837) return false;
        } else if (_selectedEra == 'seated') {
          if (year == null || year < 1837 || year >= 1873) return false;
        } else if (_selectedEra == 'morgan') {
          if (year == null || year < 1873 || year >= 1901) return false;
        } else if (_selectedEra == '20th') {
          if (year == null || year < 1901 || year >= 2000) return false;
        } else if (_selectedEra == 'modern') {
          if (year == null || year < 2000 || year > 2026) return false;
        } else if (_selectedEra == 'undated') {
          if (year != null) return false;
        }
      }

      // Photos only filter
      if (_photosOnly) {
        final hasPrimary = item['primary_image'] != null && (item['primary_image'] as Map).isNotEmpty;
        final hasType = item['type_image'] != null && (item['type_image'] as Map).isNotEmpty;
        if (!hasPrimary && !hasType) return false;
      }

      return true;
    }).toList();

    // 2. Two-pass list-level search resolution
    List<Map<String, dynamic>> result = filtered;
    if (query.isNotEmpty) {
      // Pass 1: Direct substring matches across metadata fields
      final directMatches = filtered.where((item) {
        final name = (item['name'] as String? ?? '').toLowerCase();
        final series = (item['series'] as String? ?? '').toLowerCase();
        final denom = (item['denomination'] as String? ?? '').toLowerCase();
        final nac = (item['nac_code'] as String? ?? '').toLowerCase();
        final yearStr = item['year']?.toString() ?? '';
        return name.contains(query) ||
            series.contains(query) ||
            denom.contains(query) ||
            nac.contains(query) ||
            yearStr.contains(query);
      }).toList();

      if (directMatches.isNotEmpty) {
        result = directMatches;
      } else {
        // Pass 2: Multi-token fallback across combined metadata haystack
        final tokens = query.split(RegExp(r'\s+')).where((t) => t.isNotEmpty).toList();
        result = filtered.where((item) {
          final name = (item['name'] as String? ?? '').toLowerCase();
          final series = (item['series'] as String? ?? '').toLowerCase();
          final denom = (item['denomination'] as String? ?? '').toLowerCase();
          final nac = (item['nac_code'] as String? ?? '').toLowerCase();
          final yearStr = item['year']?.toString() ?? '';
          final haystack = '$name $series $denom $nac $yearStr';
          return tokens.every((token) => haystack.contains(token));
        }).toList();
      }
    }

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
        final hasImgA = (a['primary_image'] != null || a['type_image'] != null) ? 1 : 0;
        final hasImgB = (b['primary_image'] != null || b['type_image'] != null) ? 1 : 0;
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

  void _openAskMorgan({String? initialPrompt}) {
    Navigator.of(context).pushNamed(
      '/?route=AiChatScreen',
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

                            // H1 Title
                            const Text(
                              'U.S. Numismatics Catalog',
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
                                'We are actively cataloging every U.S. coin, banknote, and medal. Sourced mintages and high-resolution reference images are added daily.',
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

                            // Category Type Tabs
                            _buildTypeTabs(),
                            const SizedBox(height: 20),

                            // Filter Controls Row
                            if (_selectedType != 'foreign') _buildFilterControls(),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),

                // Content Area
                if (_selectedType == 'foreign')
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
                                  childAspectRatio: 0.72,
                                ),
                                itemCount: _filteredEntries.length,
                                itemBuilder: (context, index) {
                                  final item = _filteredEntries[index];
                                  return _CatalogCard(
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
                icon: Image.asset(
                  'assets/morgan_avatar.png',
                  width: 32,
                  height: 32,
                  errorBuilder: (c, e, s) => const Icon(Icons.psychology, color: Colors.white, size: 28),
                ),
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
    return Wrap(
      spacing: 12,
      runSpacing: 10,
      alignment: WrapAlignment.center,
      children: [
        _TypeTab(
          label: 'Coins (2,965)',
          isSelected: _selectedType == 'coin',
          onTap: () => _onTypeChanged('coin'),
        ),
        _TypeTab(
          label: 'Banknotes (181)',
          isSelected: _selectedType == 'note',
          onTap: () => _onTypeChanged('note'),
        ),
        _TypeTab(
          label: 'Medals (56)',
          isSelected: _selectedType == 'medal',
          onTap: () => _onTypeChanged('medal'),
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

  void _showItemDetailModal(Map<String, dynamic> item) {
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

                  // Ask Morgan button
                  const SizedBox(height: 28),
                  SizedBox(
                    width: double.infinity,
                    height: 52,
                    child: ElevatedButton.icon(
                      onPressed: () {
                        Navigator.of(context).pop();
                        _openAskMorgan(initialPrompt: 'Can you tell me more about ${item['name']}?');
                      },
                      icon: const Icon(Icons.chat_bubble_outline, color: Colors.white),
                      label: Text('Ask Morgan about this ${item['type'] ?? 'coin'}', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF0B2545),
                        foregroundColor: Colors.white,
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
    final primaryImg = item['primary_image'] as Map?;
    final typeImg = item['type_image'] as Map?;

    final imgMap = primaryImg ?? typeImg;
    final isTypeImage = primaryImg == null && typeImg != null;

    if (imgMap != null && imgMap['url'] != null) {
      final url = imgMap['url'] as String;
      return Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Center(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(10),
              child: Image.network(
                url,
                height: 220,
                fit: BoxFit.contain,
                errorBuilder: (c, e, s) => _buildNoPhotoBox(),
              ),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            imgMap['source'] as String? ?? 'Numista.Ai reference photo',
            style: const TextStyle(fontSize: 14, color: Color(0xFF6B6B6B)),
          ),
          if (isTypeImage)
            const Text(
              'Representative photo — date may differ',
              style: TextStyle(fontSize: 13, fontStyle: FontStyle.italic, color: Color(0xFF1F5FAD)),
            ),
        ],
      );
    }
    return _buildNoPhotoBox();
  }

  Widget _buildNoPhotoBox() {
    return Center(
      child: Container(
        width: 120,
        height: 120,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          border: Border.all(color: const Color(0xFF8A8A8A), width: 2.5, style: BorderStyle.solid),
        ),
        child: const Center(
          child: Text(
            'No photo yet',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 15, color: Color(0xFF6B6B6B), fontWeight: FontWeight.w500),
          ),
        ),
      ),
    );
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

  Widget _buildMintageRow(Map<String, dynamic> item) {
    final mintage = item['mintage'] as Map?;
    final val = mintage?['value']?.toString();
    final label = mintage?['label'] as String?;
    final sourceUrl = mintage?['source_url'] as String?;

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
            child: val != null && val.isNotEmpty
                ? Row(
                    children: [
                      Text(val, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0B2545))),
                      if (sourceUrl != null && sourceUrl.isNotEmpty) ...[
                        const SizedBox(width: 8),
                        InkWell(
                          onTap: () async {
                            final uri = Uri.tryParse(sourceUrl);
                            if (uri != null) await launchUrl(uri);
                          },
                          child: const Text('(source)', style: TextStyle(color: Color(0xFF1F5FAD), decoration: TextDecoration.underline)),
                        ),
                      ],
                    ],
                  )
                : Text(label ?? 'Needs source', style: const TextStyle(fontSize: 16, color: Color(0xFF6B6B6B))),
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

class _CatalogCard extends StatelessWidget {
  final Map<String, dynamic> item;
  final VoidCallback onTap;

  const _CatalogCard({
    required this.item,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final primaryImg = item['primary_image'] as Map?;
    final typeImg = item['type_image'] as Map?;
    final imgMap = primaryImg ?? typeImg;
    final isTypeImage = primaryImg == null && typeImg != null;

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
                child: imgMap != null && imgMap['url'] != null
                    ? Image.network(
                        imgMap['url'] as String,
                        fit: BoxFit.contain,
                        errorBuilder: (c, e, s) => _buildPlaceholder(),
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

            if (isTypeImage)
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
