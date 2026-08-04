import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';

class SuppliesScreen extends StatelessWidget {
  const SuppliesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) {
      return const Scaffold(
        body: Center(child: Text('Please sign in.')),
      );
    }

    return Scaffold(
      backgroundColor: const Color(0xFFF0F2F6),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: const Text(
          'Supplies & Inventory',
          style: TextStyle(
            color: Color(0xFF31333F),
            fontWeight: FontWeight.w900,
            fontStyle: FontStyle.italic,
          ),
        ),
      ),
      body: StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
        stream: FirebaseFirestore.instance
            .collection('users')
            .doc(user.email!)
            .collection('supplies_log')
            .snapshots(),
        builder: (context, snapshot) {
          if (snapshot.hasError) {
            return Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: const [
                  Icon(Icons.cloud_off_rounded, size: 40, color: Colors.red),
                  SizedBox(height: 12),
                  Text(
                    'Could not load supplies.',
                    style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16, color: Color(0xFF1E293B)),
                  ),
                ],
              ),
            );
          }
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator(color: Color(0xFFD4A843)));
          }

          final docs = (snapshot.data?.docs.toList() ?? []);
          docs.sort((a, b) {
            final aData = a.data();
            final bData = b.data();
            final aTime = aData['created_at'];
            final bTime = bData['created_at'];
            if (aTime == null && bTime == null) return 0;
            if (aTime == null) return 1;
            if (bTime == null) return -1;
            if (aTime is Timestamp && bTime is Timestamp) {
              return bTime.compareTo(aTime);
            }
            return 0;
          });

          if (docs.isEmpty) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(40),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      width: 80, height: 80,
                      decoration: BoxDecoration(
                        color: const Color(0xFF2DD4BF).withAlpha(20),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.inventory_2_outlined,
                          size: 44, color: Color(0xFF2DD4BF)),
                    ),
                    const SizedBox(height: 20),
                    const Text(
                      'No Supplies Logged Yet',
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1E293B),
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Supply items detected in invoices\nappear here automatically.',
                      style: TextStyle(
                          color: Color(0xFF64748B),
                          fontSize: 14,
                          height: 1.5),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            );
          }

          // Compute total cost
          double totalCost = 0;
          for (final doc in docs) {
            final data = doc.data();
            final costStr = (data['Purchase Cost'] ?? data['Cost'] ?? '0').toString();
            try {
              totalCost +=
                  double.parse(costStr.replaceAll(r'$', '').replaceAll(',', '').trim());
            } catch (_) {}
          }

          return Column(
            children: [
              // Total cost header
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                color: Colors.white,
                child: Row(
                  children: [
                    const Icon(Icons.receipt_long_outlined,
                        color: Color(0xFFF63366), size: 20),
                    const SizedBox(width: 10),
                    Text(
                      '${docs.length} supply items',
                      style: const TextStyle(color: Color(0xFF64748B), fontSize: 14),
                    ),
                    const Spacer(),
                    Text(
                      'Total: \$${totalCost.toStringAsFixed(2)}',
                      style: const TextStyle(
                        color: Color(0xFF1E293B),
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              const Divider(height: 1),
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: docs.length,
                  itemBuilder: (context, index) {
                    final data = docs[index].data();
                    final description =
                        data['Original Description from source'] ??
                        data['Theme/Subject'] ??
                        data['Denomination'] ??
                        'Supply Item';
                    final cost     = data['Purchase Cost'] ?? data['Cost'] ?? 'N/A';
                    final date     = data['Purchase Date'] ?? 'N/A';
                    final retailer = data['Retailer/Website'] ?? 'N/A';
                    final invoice  = data['Retailer Invoice #'] ?? 'N/A';
                    final srcFile  = data['source_file']?.toString() ?? '';

                    return Card(
                      margin: const EdgeInsets.only(bottom: 10),
                      elevation: 1,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                        side: const BorderSide(color: Color(0xFFE2E6E9), width: 1),
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(14),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                const Icon(Icons.inventory_2_outlined,
                                    size: 16, color: Color(0xFF94A3B8)),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    description.toString(),
                                    style: const TextStyle(
                                      fontWeight: FontWeight.w600,
                                      fontSize: 14,
                                      color: Color(0xFF1E293B),
                                    ),
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  cost.toString(),
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF1E293B),
                                    fontSize: 15,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Wrap(
                              spacing: 16,
                              runSpacing: 6,
                              children: [
                                _metaChip(Icons.storefront_outlined, retailer.toString()),
                                _metaChip(Icons.receipt_outlined, 'Inv: $invoice'),
                                _metaChip(Icons.calendar_today_outlined, date.toString()),
                              ],
                            ),
                            if (srcFile.isNotEmpty)
                              Padding(
                                padding: const EdgeInsets.only(top: 6),
                                child: Row(
                                  children: [
                                    const Icon(Icons.insert_drive_file_outlined,
                                        size: 11, color: Color(0xFFF63366)),
                                    const SizedBox(width: 4),
                                    Expanded(
                                      child: Text(
                                        srcFile,
                                        style: const TextStyle(
                                          color: Color(0xFFF63366),
                                          fontSize: 11,
                                          fontWeight: FontWeight.w500,
                                        ),
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ),
                                  ],
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
          );
        },
      ),
    );
  }

  Widget _metaChip(IconData icon, String label) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 12, color: const Color(0xFF94A3B8)),
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontSize: 11, color: Color(0xFF64748B))),
      ],
    );
  }
}
