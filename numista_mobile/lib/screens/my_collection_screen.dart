import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

class MyCollectionScreen extends StatefulWidget {
  const MyCollectionScreen({super.key});

  @override
  State<MyCollectionScreen> createState() => _MyCollectionScreenState();
}

class _MyCollectionScreenState extends State<MyCollectionScreen> {
  String? _selectedCoinId;
  int _limit = 50;
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _searchController.addListener(() {
      setState(() {
        _searchQuery = _searchController.text.toLowerCase();
      });
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final baseQuery = FirebaseFirestore.instance
        .collection('users/eric@numista.ai/coins');
        
    Query<Map<String, dynamic>> finalQuery = baseQuery;
    if (_limit > 0) {
      finalQuery = finalQuery.limit(_limit);
    }

    return StreamBuilder<QuerySnapshot>(
      stream: finalQuery.snapshots(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator(color: Color(0xFFF63366)));
        }

        if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}', style: const TextStyle(color: Colors.red)));
        }

        final docs = snapshot.data?.docs ?? [];
        if (docs.isEmpty) {
          return const Center(child: Text('No coins found in your collection.', style: TextStyle(color: Color(0xFF31333F))));
        }

        // Set initial selection if none
        if (_selectedCoinId == null && docs.isNotEmpty) {
          _selectedCoinId = docs.first.id;
        }

        // Ensure the selected ID actually exists in the current list
        final selectedDoc = docs.any((doc) => doc.id == _selectedCoinId)
            ? docs.firstWhere((doc) => doc.id == _selectedCoinId)
            : docs.first;

        final data = selectedDoc.data() as Map<String, dynamic>;

        return SingleChildScrollView(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              const Text(
                'My Collection',
                style: TextStyle(
                  fontSize: 36,
                  fontWeight: FontWeight.w900,
                  color: Color(0xFF31333F),
                ),
              ),
              const SizedBox(height: 16),
              
              // BETA TESTING banner
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 16),
                decoration: BoxDecoration(
                  color: const Color(0xFF4C8CDA),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: const Text(
                  'BETA TESTING',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 10,
                    color: Colors.white,
                    letterSpacing: 1.0,
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Show & Search Filters Row
              Row(
                children: [
                  Expanded(
                    flex: 1,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Show:', style: TextStyle(color: Color(0xFF31333F), fontSize: 14)),
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF0F2F6),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: DropdownButtonHideUnderline(
                            child: DropdownButton<String>(
                              value: _limit == 0 ? 'All' : (_limit == 100 ? 'Last 100' : 'Last 50'),
                              isExpanded: true,
                              icon: const Icon(Icons.keyboard_arrow_down, color: Color(0xFF31333F)),
                              items: const [
                                DropdownMenuItem(value: 'Last 50', child: Text('Last 50', style: TextStyle(color: Color(0xFF31333F)))),
                                DropdownMenuItem(value: 'Last 100', child: Text('Last 100', style: TextStyle(color: Color(0xFF31333F)))),
                                DropdownMenuItem(value: 'All', child: Text('All', style: TextStyle(color: Color(0xFF31333F)))),
                              ],
                              onChanged: (val) {
                                setState(() {
                                  if (val == 'Last 50') {
                                    _limit = 50;
                                  } else if (val == 'Last 100') {
                                    _limit = 100;
                                  } else {
                                    _limit = 0; // Use 0 for "All" (no limit)
                                  }
                                });
                              },
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 24),
                  Expanded(
                    flex: 1,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Row(
                          children: [
                            Icon(Icons.search, size: 16, color: Color(0xFF31333F)),
                            SizedBox(width: 4),
                            Text('Search', style: TextStyle(color: Color(0xFF31333F), fontSize: 14)),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Container(
                          height: 48,
                          decoration: BoxDecoration(
                            color: const Color(0xFFF0F2F6),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: TextField(
                            controller: _searchController,
                            style: const TextStyle(color: Color(0xFF31333F)),
                            decoration: const InputDecoration(
                              border: InputBorder.none,
                              contentPadding: EdgeInsets.symmetric(horizontal: 12),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 24),
                  Expanded(
                    flex: 2,
                    child: Container(
                      margin: const EdgeInsets.only(top: 24),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFFD4EED8),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.check_box, color: Color(0xFF28A745), size: 20),
                          SizedBox(width: 8),
                          Text(
                            'All estimated.',
                            style: TextStyle(color: Color(0xFF155724), fontSize: 14),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 32),
              const Divider(color: Color(0xFFE2E6E9)),
              const SizedBox(height: 32),

              // Select Coin to Inspect Dropdown
              const Text('Select Coin to Inspect:', style: TextStyle(color: Color(0xFF31333F), fontSize: 14)),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                decoration: BoxDecoration(
                  color: const Color(0xFFF0F2F6),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: DropdownButtonHideUnderline(
                  child: DropdownButton<String>(
                    value: docs.any((doc) => doc.id == _selectedCoinId) ? _selectedCoinId : null,
                    isExpanded: true,
                    icon: const Icon(Icons.keyboard_arrow_down, color: Color(0xFF31333F)),
                    items: docs.where((doc) {
                      final item = doc.data() as Map<String, dynamic>;
                      final year = item['Year']?.toString().toLowerCase() ?? '';
                      final mint = item['Mint Mark']?.toString().toLowerCase() ?? '';
                      final denom = item['Denomination']?.toString().toLowerCase() ?? '';
                      final fullName = '$year $mint $denom';
                      return fullName.contains(_searchQuery);
                    }).map((doc) {
                      final item = doc.data() as Map<String, dynamic>;
                      final year = item['Year']?.toString() ?? '????';
                      final mint = item['Mint Mark']?.toString() ?? '';
                      final denom = item['Denomination']?.toString() ?? 'Coin';
                      final name = '$year${mint.isNotEmpty ? '-$mint' : ''} $denom';
                      return DropdownMenuItem(
                        value: doc.id,
                        child: Text(name, style: const TextStyle(color: Color(0xFF31333F))),
                      );
                    }).toList(),
                    onChanged: (val) {
                      setState(() {
                        _selectedCoinId = val;
                      });
                    },
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Streamlit Expander: Coin Inspector
              _buildCoinInspector(data),
            ],
          ),
        );
      },
    );
  }

  Widget _buildCoinInspector(Map<String, dynamic> data) {
    final imageUrlObverse = data['image_url_obverse']?.toString();
    final imageUrlReverse = data['image_url_reverse']?.toString();
    final value = data['AI Estimated Value']?.toString() ?? '--';
    final melt = data['Melt Value']?.toString() ?? '—';
    final grade = data['Condition']?.toString() ?? 'N/A';
    final notes = data['Notes'] ?? data['Theme/Subject'] ?? 'No additional info.';

    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFFF8F9FB),
        border: Border.all(color: const Color(0xFFE2E6E9)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Theme(
        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          initiallyExpanded: true,
          iconColor: const Color(0xFF31333F),
          collapsedIconColor: const Color(0xFF31333F),
          title: const Row(
            children: [
              Icon(Icons.book_outlined, color: Color(0xFF31333F), size: 18),
              SizedBox(width: 8),
              Text('Coin Inspector', style: TextStyle(color: Color(0xFF31333F), fontSize: 14)),
            ],
          ),
          children: [
            Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Metrics Column
                      Expanded(
                        flex: 2,
                        child: Column(
                          children: [
                            Row(
                              children: [
                                Expanded(child: _buildInspectorMetric('Value', value)),
                                Expanded(child: _buildInspectorMetric('Melt', melt)),
                                Expanded(child: _buildInspectorMetric('Grade', grade)),
                              ],
                            ),
                            const SizedBox(height: 24),
                            // Info Box
                            Container(
                              width: double.infinity,
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: const Color(0xFFD3E3FD),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                notes.toString(),
                                style: const TextStyle(color: Color(0xFF003884)),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 48),
                      // Action/Image Column
                      Expanded(
                        flex: 1,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            OutlinedButton.icon(
                              onPressed: () {},
                              icon: const Icon(Icons.search, size: 18),
                              label: const Text('Search Google'),
                              style: OutlinedButton.styleFrom(
                                foregroundColor: const Color(0xFF31333F),
                                side: const BorderSide(color: Color(0xFFE2E6E9)),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                              ),
                            ),
                            const SizedBox(height: 24),
                            if (imageUrlObverse != null && imageUrlObverse.isNotEmpty) ...[
                              const Text('Obverse View', style: TextStyle(color: Color(0xFF31333F), fontSize: 12)),
                              const SizedBox(height: 8),
                              _buildImageContainer(imageUrlObverse),
                            ] else ...[
                              const Text('No Front Image', style: TextStyle(color: Color(0xFF31333F), fontSize: 12)),
                              const SizedBox(height: 8),
                              _buildPlaceholderImage(),
                            ],
                            const SizedBox(height: 16),
                            if (imageUrlReverse != null && imageUrlReverse.isNotEmpty) ...[
                              const Text('Reverse View', style: TextStyle(color: Color(0xFF31333F), fontSize: 12)),
                              const SizedBox(height: 8),
                              _buildImageContainer(imageUrlReverse),
                            ],
                          ],
                        ),
                      ),
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

  Widget _buildInspectorMetric(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 14,
            color: Color(0xFF5A5C69),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            fontSize: 28,
            fontWeight: FontWeight.normal,
            color: Color(0xFF31333F),
          ),
        ),
      ],
    );
  }

  Widget _buildImageContainer(String url) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(4),
      child: Image.network(
        url,
        height: 150,
        width: double.infinity,
        fit: BoxFit.contain,
        errorBuilder: (context, error, stackTrace) => _buildPlaceholderImage(),
      ),
    );
  }

  Widget _buildPlaceholderImage() {
    return Container(
      height: 150,
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: const Color(0xFFE2E6E9)),
        borderRadius: BorderRadius.circular(4),
      ),
      child: const Center(
        child: Icon(Icons.image_not_supported_outlined, color: Color(0xFF6B8DB5), size: 32),
      ),
    );
  }
}
