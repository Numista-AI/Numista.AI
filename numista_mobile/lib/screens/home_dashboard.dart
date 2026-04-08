import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:intl/intl.dart' as intl;

class HomeDashboard extends StatefulWidget {
  const HomeDashboard({super.key});

  @override
  State<HomeDashboard> createState() => _HomeDashboardState();
}

class _HomeDashboardState extends State<HomeDashboard> {
  final TextEditingController _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  double _parseCurrency(dynamic value) {
    if (value == null) return 0.0;
    final String str = value.toString().replaceAll('\$', '').replaceAll(',', '').trim();
    return double.tryParse(str) ?? 0.0;
  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<QuerySnapshot>(
      stream: FirebaseFirestore.instance
          .collection('users/eric@numista.ai/coins')
          .snapshots(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator(color: Color(0xFFF63366)));
        }

        if (snapshot.hasError) {
          return Center(child: Text('Error: ${snapshot.error}', style: const TextStyle(color: Colors.red)));
        }

        final docs = snapshot.data?.docs ?? [];
        
        // Calculate Metrics
        int totalCoins = docs.length;
        double portfolioValue = 0.0;
        double acquisitionCost = 0.0;
        double meltValue = 0.0;
        double faceValue = 0.0;

        for (var doc in docs) {
          final data = doc.data() as Map<String, dynamic>;
          portfolioValue += _parseCurrency(data['AI Estimated Value']);
          acquisitionCost += _parseCurrency(data['Acquisition Cost']);
          meltValue += _parseCurrency(data['Melt Value']);
          faceValue += _parseCurrency(data['Face Value']);
        }

        // Sorting Logic for "Last 5 Coins"
        final sortedDocs = List<QueryDocumentSnapshot>.from(docs);
        sortedDocs.sort((a, b) {
          final aData = a.data() as Map<String, dynamic>;
          final bData = b.data() as Map<String, dynamic>;
          
          final aTs = aData['timestamp'] ?? aData['created_at'];
          final bTs = bData['timestamp'] ?? bData['created_at'];
          if (aTs is Timestamp && bTs is Timestamp) {
            return bTs.compareTo(aTs);
          }
          
          final aDate = aData['Date']?.toString() ?? '';
          final bDate = bData['Date']?.toString() ?? '';
          if (aDate.isNotEmpty && bDate.isNotEmpty) {
            return bDate.compareTo(aDate);
          }
          
          return b.id.compareTo(a.id);
        });

        final last5 = sortedDocs.take(5).toList();

        final currencyFormatter = intl.NumberFormat.currency(symbol: '\$');

        return SingleChildScrollView(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Beta Testing Banner
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0xFFFFF7DD),
                  borderRadius: BorderRadius.circular(4),
                  border: Border.all(color: const Color(0xFFFFD54F), width: 1),
                ),
                child: const Text(
                  '🚧 BETA TESTING MODE 🚧',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                    color: Color(0xFF8B6B00),
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'DASHBOARD',
                        style: TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.w900,
                          fontStyle: FontStyle.italic,
                          color: Color(0xFF31333F),
                        ),
                      ),
                      const Text(
                        'AI POWERED COIN COLLECTION MANAGER',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF5A5C69),
                        ),
                      ),
                    ],
                  ),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      const Text(
                        'AI ESTIMATED PORTFOLIO VALUE',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF5A5C69),
                        ),
                      ),
                      Text(
                        currencyFormatter.format(portfolioValue),
                        style: const TextStyle(
                          fontSize: 36,
                          fontWeight: FontWeight.w900,
                          color: Color(0xFF0F9D58),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 32),

              // Expander: System Updates
              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  border: Border.all(color: const Color(0xFFE2E6E9)),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Theme(
                  data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
                  child: ExpansionTile(
                    iconColor: const Color(0xFF31333F),
                    collapsedIconColor: const Color(0xFF31333F),
                    title: const Row(
                      children: [
                        Text('🚀 System Updates & Release Notes', style: TextStyle(color: Color(0xFF31333F), fontWeight: FontWeight.w500)),
                      ],
                    ),
                    children: const [
                      Padding(
                        padding: EdgeInsets.all(16.0),
                        child: Align(
                          alignment: Alignment.centerLeft,
                          child: Text('Track the latest features deployed to Numista.AI', style: TextStyle(color: Color(0xFF5A5C69))),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 32),

              // Metric Cards Row
              Row(
                children: [
                  Expanded(child: _buildMetricCard('Total Coins', totalCoins.toString())),
                  const SizedBox(width: 16),
                  Expanded(child: _buildMetricCard('Acquisition Cost', currencyFormatter.format(acquisitionCost))),
                  const SizedBox(width: 16),
                  Expanded(child: _buildMetricCard('Melt Value', currencyFormatter.format(meltValue))),
                  const SizedBox(width: 16),
                  Expanded(child: _buildMetricCard('Face Value', currencyFormatter.format(faceValue))),
                ],
              ),
              const SizedBox(height: 48),

              // Two Columns Layout
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Analytics Message Board
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Analytics Message Board',
                          style: TextStyle(fontSize: 24, fontWeight: FontWeight.w600, color: Color(0xFF31333F)),
                        ),
                        const SizedBox(height: 16),
                        Container(
                          padding: const EdgeInsets.all(16.0),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            border: Border.all(color: const Color(0xFFE2E6E9)),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('Recently Added Coins:', style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF31333F))),
                              const SizedBox(height: 16),
                              // Simple Table
                              Table(
                                border: TableBorder(horizontalInside: BorderSide(color: Colors.grey.shade200)),
                                columnWidths: const {
                                  0: FlexColumnWidth(1),
                                  1: FlexColumnWidth(2),
                                  2: FlexColumnWidth(1.5),
                                },
                                children: [
                                  _buildTableRow('Year', 'Denomination', 'AI Estimated Value', isHeader: true),
                                  ...last5.map((doc) {
                                    final data = doc.data() as Map<String, dynamic>;
                                    return _buildTableRow(
                                      data['Year']?.toString() ?? '????',
                                      data['Denomination']?.toString() ?? 'Unknown',
                                      data['AI Estimated Value']?.toString() ?? '--',
                                    );
                                  }),
                                  if (last5.isEmpty)
                                    _buildTableRow('', 'No coins found', ''),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 32),
                  
                  // AI Numismatic Deepdive
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'AI Numismatic Deepdive',
                          style: TextStyle(fontSize: 24, fontWeight: FontWeight.w600, color: Color(0xFF31333F)),
                        ),
                        const SizedBox(height: 16),
                        Container(
                          padding: const EdgeInsets.all(24.0),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF8F9FB), // Slightly darker gray for input area
                            border: Border.all(color: const Color(0xFFE2E6E9)),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('Suggested Questions:', style: TextStyle(color: Color(0xFF5A5C69), fontSize: 12)),
                              const SizedBox(height: 16),
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  _buildSuggestionPill('Most Valuable?'),
                                  _buildSuggestionPill('Coins from 2025?'),
                                  _buildSuggestionPill('Next Purchase?'),
                                ],
                              ),
                              const SizedBox(height: 24),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  borderRadius: BorderRadius.circular(24),
                                  border: Border.all(color: const Color(0xFFE2E6E9)),
                                ),
                                child: Row(
                                  children: [
                                    Expanded(
                                      child: TextField(
                                        controller: _searchController,
                                        style: const TextStyle(color: Color(0xFF31333F)),
                                        decoration: const InputDecoration(
                                          hintText: 'Ask about your collection...',
                                          hintStyle: TextStyle(color: Color(0xFFA0A3AB)),
                                          border: InputBorder.none,
                                        ),
                                        onSubmitted: (_) {
                                          ScaffoldMessenger.of(context).showSnackBar(
                                            const SnackBar(content: Text('AI Deepdive logic coming soon in the next phase!')),
                                          );
                                        },
                                      ),
                                    ),
                                    IconButton(
                                      icon: const Icon(Icons.send, color: Color(0xFFF63366)),
                                      onPressed: () {
                                        ScaffoldMessenger.of(context).showSnackBar(
                                          const SnackBar(content: Text('AI Deepdive logic coming soon in the next phase!')),
                                        );
                                      },
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildMetricCard(String label, String value) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 24.0, horizontal: 16.0),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
        border: Border.all(color: const Color(0xFFE2E6E9)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Text(
            label,
            style: const TextStyle(
              fontSize: 14,
              color: Color(0xFF5A5C69),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              fontSize: 28,
              fontWeight: FontWeight.w800,
              color: Color(0xFF31333F),
            ),
          ),
        ],
      ),
    );
  }

  TableRow _buildTableRow(String col1, String col2, String col3, {bool isHeader = false}) {
    return TableRow(
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 12.0),
          child: Text(
            col1,
            style: TextStyle(
              fontWeight: isHeader ? FontWeight.bold : FontWeight.normal,
              color: isHeader ? const Color(0xFFA0A3AB) : const Color(0xFF31333F),
              fontSize: 14,
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 12.0),
          child: Text(
            col2,
            style: TextStyle(
              fontWeight: isHeader ? FontWeight.bold : FontWeight.normal,
              color: isHeader ? const Color(0xFFA0A3AB) : const Color(0xFF31333F),
              fontSize: 14,
            ),
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 12.0),
          child: Text(
            col3,
            style: TextStyle(
              fontWeight: isHeader ? FontWeight.bold : FontWeight.normal,
              color: isHeader ? const Color(0xFFA0A3AB) : const Color(0xFF31333F),
              fontSize: 14,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSuggestionPill(String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE2E6E9)),
      ),
      child: Text(
        label,
        style: const TextStyle(
          color: Color(0xFF31333F),
          fontSize: 12,
        ),
      ),
    );
  }
}
