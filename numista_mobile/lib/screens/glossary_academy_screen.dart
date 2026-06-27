import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:cached_network_image/cached_network_image.dart';
import '../constants.dart';
import '../widgets/grade_badge_widget.dart';

class GlossaryAcademyScreen extends StatefulWidget {
  const GlossaryAcademyScreen({super.key});

  @override
  State<GlossaryAcademyScreen> createState() => _GlossaryAcademyScreenState();
}

class _GlossaryAcademyScreenState extends State<GlossaryAcademyScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _searchController = TextEditingController();
  
  bool _searching = false;
  Map<String, dynamic>? _searchResults;
  String? _searchError;

  List<Map<String, dynamic>> _grades = [];
  List<Map<String, dynamic>> _glossary = [];
  bool _loadingData = true;
  String? _dataError;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _fetchReferenceData();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _fetchReferenceData() async {
    try {
      // Fetch Glossary
      final glossaryRes = await http.get(Uri.parse('$kApiBaseUrl/api/reference/glossary'));
      
      // Fetch Sheldon Grades (We query local/static list or make a general endpoint. 
      // Since Sheldon Scale has fixed codes, we can load them or fetch details for key ones.
      // Let's populate the UI with a beautiful, comprehensive pre-seeded list,
      // and when clicked, it pulls detail or we show the list directly).
      // Wait, let's pull the full glossary first.
      if (glossaryRes.statusCode == 200) {
        final glossaryData = List<Map<String, dynamic>>.from(json.decode(glossaryRes.body));
        
        // Let's pre-load some sheldon scale codes to populate the sheldon tab
        final sheldonCodes = [
          'P-1', 'FR-2', 'AG-3', 'G-4', 'VG-8', 'F-12', 'VF-20', 
          'XF-40', 'AU-50', 'AU-58', 'MS-60', 'MS-63', 'MS-65', 'MS-70'
        ];
        
        final loadedGrades = <Map<String, dynamic>>[];
        for (final code in sheldonCodes) {
          try {
            final res = await http.get(Uri.parse('$kApiBaseUrl/api/reference/grade/$code'));
            if (res.statusCode == 200) {
              loadedGrades.add(json.decode(res.body));
            }
          } catch (e) {
            debugPrint('Error pre-fetching grade $code: $e');
          }
        }

        if (mounted) {
          setState(() {
            _glossary = glossaryData;
            _grades = loadedGrades;
            _loadingData = false;
          });
        }
      } else {
        if (mounted) {
          setState(() {
            _dataError = 'Failed to load glossary: Status ${glossaryRes.statusCode}';
            _loadingData = false;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _dataError = 'Error connecting to backend: $e';
          _loadingData = false;
        });
      }
    }
  }

  Future<void> _performSearch() async {
    final query = _searchController.text.trim();
    if (query.isEmpty) {
      setState(() {
        _searchResults = null;
        _searchError = null;
      });
      return;
    }

    setState(() {
      _searching = true;
      _searchResults = null;
      _searchError = null;
    });

    try {
      final response = await http.post(
        Uri.parse('$kApiBaseUrl/api/reference/search'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'query': query}),
      );

      if (response.statusCode == 200) {
        final result = json.decode(response.body);
        if (mounted) {
          setState(() {
            _searchResults = result;
            _searching = false;
          });
        }
      } else {
        if (mounted) {
          setState(() {
            _searchError = 'Search failed: Status ${response.statusCode}';
            _searching = false;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _searchError = 'Network error during search: $e';
          _searching = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0E1117), // Sleeek Dark Mode
      body: SafeArea(
        child: Column(
          children: [
            // ── AI Quest Search Header ────────────────────────────────────────
            _buildSearchHeader(),

            // If showing search results
            if (_searchResults != null || _searching || _searchError != null)
              Expanded(
                child: _buildSearchResultsView(),
              )
            else if (_loadingData)
              const Expanded(
                child: Center(
                  child: CircularProgressIndicator(color: Color(0xFFF63366)),
                ),
              )
            else if (_dataError != null)
              Expanded(
                child: Center(
                  child: Text(
                    _dataError!,
                    style: const TextStyle(color: Colors.redAccent),
                  ),
                ),
              )
            else
              // ── Tab Bar Navigation ──────────────────────────────────────────
              Expanded(
                child: Column(
                  children: [
                    TabBar(
                      controller: _tabController,
                      indicatorColor: const Color(0xFFF63366),
                      labelColor: Colors.white,
                      unselectedLabelColor: Colors.white38,
                      labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                      tabs: const [
                        Tab(text: 'Sheldon Scale', icon: Icon(Icons.line_weight_rounded, size: 20)),
                        Tab(text: 'Coin Anatomy', icon: Icon(Icons.blur_circular_rounded, size: 20)),
                        Tab(text: 'Known Errors', icon: Icon(Icons.bug_report_outlined, size: 20)),
                      ],
                    ),
                    Expanded(
                      child: TabBarView(
                        controller: _tabController,
                        children: [
                          _buildSheldonTab(),
                          _buildGlossaryTab(),
                          _buildErrorsTab(),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildSearchHeader() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: const BoxDecoration(
        color: Color(0xFF161B22),
        border: Border(bottom: BorderSide(color: Colors.white10)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Numista Academy',
            style: TextStyle(
              color: Colors.white,
              fontSize: 22,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 4),
          const Text(
            'Learn grading scale, terminology, and errors',
            style: TextStyle(color: Colors.white38, fontSize: 13),
          ),
          const SizedBox(height: 16),
          // Search input field
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _searchController,
                  onSubmitted: (_) => _performSearch(),
                  style: const TextStyle(color: Colors.white, fontSize: 14),
                  decoration: InputDecoration(
                    hintText: 'Ask anything... (e.g. "what is heads called?")',
                    hintStyle: const TextStyle(color: Colors.white24),
                    fillColor: const Color(0xFF0D1117),
                    filled: true,
                    prefixIcon: const Icon(Icons.search, color: Colors.white38),
                    suffixIcon: _searchController.text.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear, color: Colors.white38),
                            onPressed: () {
                              _searchController.clear();
                              setState(() {
                                _searchResults = null;
                                _searchError = null;
                              });
                            },
                          )
                        : null,
                    contentPadding: const EdgeInsets.symmetric(vertical: 0, horizontal: 16),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: Colors.white10),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: const BorderSide(color: Color(0xFFF63366)),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              ElevatedButton(
                onPressed: _performSearch,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFF63366),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                ),
                child: const Text('Ask AI', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSearchResultsView() {
    if (_searching) {
      return const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(color: Color(0xFFF63366)),
            SizedBox(height: 16),
            Text('AI Quest mapping query...', style: TextStyle(color: Colors.white38)),
          ],
        ),
      );
    }

    if (_searchError != null) {
      return Center(
        child: Text(_searchError!, style: const TextStyle(color: Colors.redAccent)),
      );
    }

    final data = _searchResults!;
    final bool matched = data['matched'] ?? false;
    final String source = data['source'] ?? 'none';
    final term = data['term'];

    return Container(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'AI Quest Search Result',
                style: TextStyle(color: Colors.white38, fontSize: 13, fontWeight: FontWeight.bold),
              ),
              IconButton(
                icon: const Icon(Icons.close, color: Colors.white54),
                onPressed: () {
                  _searchController.clear();
                  setState(() {
                    _searchResults = null;
                  });
                },
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (!matched)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.red.withAlpha(12),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.red.withAlpha(30)),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'No direct matches found',
                    style: TextStyle(color: Colors.redAccent, fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                  SizedBox(height: 6),
                  Text(
                    'The AI Quest mapping could not correlate your description to a known glossary term. Try using other terms like heads, tails, shine, or edge.',
                    style: TextStyle(color: Colors.white54, fontSize: 13, height: 1.4),
                  ),
                ],
              ),
            )
          else ...[
            // Found a term!
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: source == 'gemini' ? const Color(0xFF1E3A8A) : const Color(0xFF065F46),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                source == 'gemini' ? 'AI MAPPED SUCCESS' : 'DATABASE DIRECT MATCH',
                style: const TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              term['term'] ?? '',
              style: const TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 4),
            Text(
              'Category: ${term['category'] ?? 'General'}',
              style: const TextStyle(color: Colors.white38, fontSize: 12),
            ),
            const SizedBox(height: 16),
            Text(
              term['definition'] ?? '',
              style: const TextStyle(color: Colors.white, fontSize: 15, height: 1.5),
            ),
            const SizedBox(height: 12),
            if (term['colloquial_mappings'] != null && (term['colloquial_mappings'] as List).isNotEmpty) ...[
              const Text('Colloquial mappings:', style: TextStyle(color: Colors.white38, fontSize: 12)),
              const SizedBox(height: 4),
              Wrap(
                spacing: 8,
                children: (term['colloquial_mappings'] as List).map<Widget>((m) {
                  return Chip(
                    label: Text(m.toString(), style: const TextStyle(color: Colors.white70, fontSize: 11)),
                    backgroundColor: Colors.white10,
                  );
                }).toList(),
              ),
            ],
            const SizedBox(height: 24),
            // Illustration
            if (term['illustration_url'] != null && (term['illustration_url'] as String).isNotEmpty)
              Expanded(
                child: Center(
                  child: Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.white12),
                      color: Colors.white.withAlpha(5),
                    ),
                    clipBehavior: Clip.antiAlias,
                    child: CachedNetworkImage(
                      imageUrl: term['illustration_url'],
                      fit: BoxFit.contain,
                      placeholder: (context, url) => const Center(
                        child: CircularProgressIndicator(color: Color(0xFFF63366)),
                      ),
                      errorWidget: (context, url, error) => const Icon(Icons.broken_image, color: Colors.white24),
                    ),
                  ),
                ),
              ),
          ]
        ],
      ),
    );
  }

  Widget _buildSheldonTab() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _grades.length,
      itemBuilder: (context, index) {
        final grade = _grades[index];
        final code = grade['grade_code'] ?? '';
        final name = grade['grade_name'] ?? '';
        final wear = grade['wear_description'] ?? '';

        return Card(
          color: const Color(0xFF161B22),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          margin: const EdgeInsets.only(bottom: 12),
          child: ExpansionTile(
            collapsedIconColor: Colors.white38,
            iconColor: const Color(0xFFF63366),
            title: Row(
              children: [
                GradeBadgeWidget(
                  gradeCode: code,
                  onTap: () {}, // disable BottomSheet inside expansion card list
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    name,
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15),
                  ),
                ),
              ],
            ),
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Divider(color: Colors.white12),
                    const SizedBox(height: 8),
                    const Text('PRESERVATION & WEAR', style: TextStyle(color: Colors.white38, fontSize: 11, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 4),
                    Text(wear, style: const TextStyle(color: Colors.white, fontSize: 13, height: 1.4)),
                    const SizedBox(height: 12),
                    const Text('LUSTER STATUS', style: TextStyle(color: Colors.white38, fontSize: 11, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 4),
                    Text(grade['luster_description'] ?? '', style: const TextStyle(color: Colors.white, fontSize: 13, height: 1.4)),
                    const SizedBox(height: 12),
                    const Text('INSPECTION TIP', style: TextStyle(color: Colors.white38, fontSize: 11, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 4),
                    Text(
                      grade['inspection_tips'] ?? '',
                      style: const TextStyle(color: Color(0xFFFCD34D), fontSize: 13, height: 1.4, fontWeight: FontWeight.w500),
                    ),
                    const SizedBox(height: 16),
                    if (grade['illustration_url'] != null)
                      Container(
                        height: 140,
                        width: double.infinity,
                        decoration: BoxDecoration(
                          color: Colors.white.withAlpha(5),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        clipBehavior: Clip.antiAlias,
                        child: CachedNetworkImage(
                          imageUrl: grade['illustration_url'],
                          fit: BoxFit.contain,
                          placeholder: (context, url) => const Center(
                            child: SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)),
                          ),
                          errorWidget: (context, url, error) => const Icon(Icons.broken_image, color: Colors.white24),
                        ),
                      ),
                  ],
                ),
              )
            ],
          ),
        );
      },
    );
  }

  Widget _buildGlossaryTab() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _glossary.length,
      itemBuilder: (context, index) {
        final item = _glossary[index];
        final term = item['term'] ?? '';
        final definition = item['definition'] ?? '';
        final colloquial = List<String>.from(item['colloquial_mappings'] ?? []);
        final imgUrl = item['illustration_url'] as String?;

        return Card(
          color: const Color(0xFF161B22),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      term,
                      style: const TextStyle(color: Color(0xFFF63366), fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    Text(
                      item['category'] ?? 'General',
                      style: const TextStyle(color: Colors.white24, fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  definition,
                  style: const TextStyle(color: Colors.white, fontSize: 13, height: 1.4),
                ),
                if (colloquial.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  const Text('Colloquial mappings:', style: TextStyle(color: Colors.white38, fontSize: 11)),
                  const SizedBox(height: 4),
                  Wrap(
                    spacing: 8,
                    children: colloquial.map((c) {
                      return Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.white.withAlpha(8),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(c, style: const TextStyle(color: Colors.white54, fontSize: 10)),
                      );
                    }).toList(),
                  ),
                ],
                if (imgUrl != null && imgUrl.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  Container(
                    height: 140,
                    width: double.infinity,
                    decoration: BoxDecoration(
                      color: Colors.white.withAlpha(5),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    clipBehavior: Clip.antiAlias,
                    child: CachedNetworkImage(
                      imageUrl: imgUrl,
                      fit: BoxFit.contain,
                      placeholder: (context, url) => const Center(
                        child: SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)),
                      ),
                      errorWidget: (context, url, error) => const Icon(Icons.broken_image, color: Colors.white24),
                    ),
                  ),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildErrorsTab() {
    // Placeholder grid pre-wired for error taxonomy maps
    final mockErrors = [
      {
        "name": "Doubled Die Obverse",
        "slug": "doubled-die",
        "side": "obverse",
        "example": "1955 Lincoln Cent DDO",
        "gcs_path": "gs://studio-9101802118-8c9a8-uploads/assets/reference/error_doubled-die_obverse.jpg",
      },
      {
        "name": "Clipped Planchet",
        "slug": "clipped-planchet",
        "side": "obverse",
        "example": "Curved Clipped Nickel blank",
        "gcs_path": "gs://studio-9101802118-8c9a8-uploads/assets/reference/error_clipped-planchet_obverse.jpg",
      },
      {
        "name": "Die Crack / Cud",
        "slug": "die-crack",
        "side": "reverse",
        "example": "Morgan Dollar reverse die break",
        "gcs_path": "gs://studio-9101802118-8c9a8-uploads/assets/reference/error_die-crack_reverse.jpg",
      },
      {
        "name": "Off-Center Strike",
        "slug": "off-center",
        "side": "obverse",
        "example": "20% off-center Lincoln wheat cent",
        "gcs_path": "gs://studio-9101802118-8c9a8-uploads/assets/reference/error_off-center_obverse.jpg",
      }
    ];

    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        childAspectRatio: 0.85,
      ),
      itemCount: mockErrors.length,
      itemBuilder: (context, index) {
        final err = mockErrors[index];
        final resolvedImgUrl = _gcsToHttpUrl(err['gcs_path']?.toString());

        return Card(
          color: const Color(0xFF161B22),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          clipBehavior: Clip.antiAlias,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Container(
                  width: double.infinity,
                  color: Colors.white.withAlpha(5),
                  child: CachedNetworkImage(
                    imageUrl: resolvedImgUrl,
                    fit: BoxFit.cover,
                    placeholder: (context, url) => const Center(
                      child: SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)),
                    ),
                    errorWidget: (context, url, error) => Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.broken_image, color: Colors.white24, size: 32),
                          const SizedBox(height: 6),
                          Text(
                            '${err['slug']}_${err['side']}.jpg',
                            style: const TextStyle(color: Colors.white24, fontSize: 8),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(10),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      err['name']!,
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 2),
                    Text(
                      err['example']!,
                      style: const TextStyle(color: Colors.white38, fontSize: 10),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              )
            ],
          ),
        );
      },
    );
  }

  String _gcsToHttpUrl(String? gcsPath) {
    if (gcsPath == null) return '';
    if (gcsPath.startsWith('gs://')) {
      return gcsPath.replaceFirst('gs://', 'https://storage.googleapis.com/');
    }
    return gcsPath;
  }
}
