import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'storage_service.dart';

const _electricBlue = Color(0xFF4C8CDA);
const _neuralBronze = Color(0xFF8B6B00);
const _charcoal = Color(0xFF31333F);

class InventoryGalleryPage extends StatefulWidget {
  const InventoryGalleryPage({super.key});

  @override
  State<InventoryGalleryPage> createState() => _InventoryGalleryPageState();
}

class _InventoryGalleryPageState extends State<InventoryGalleryPage> {
  bool _isSyncing = false;

  Future<void> _runSync() async {
    setState(() => _isSyncing = true);
    try {
      await StorageService().syncLocalCaptures();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: _electricBlue,
            content: const Row(
              children: [
                Icon(Icons.check_circle, color: Colors.white),
                SizedBox(width: 10),
                Text('Sync complete! Check the debug console for details.',
                    style: TextStyle(color: Colors.white)),
              ],
            ),
            duration: const Duration(seconds: 4),
          ),
        );
      }
    } catch (e) {
      debugPrint('[SYNC] Top-level exception caught: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            backgroundColor: Colors.redAccent,
            content: Text('Sync error: $e',
                style: const TextStyle(color: Colors.white)),
            duration: const Duration(seconds: 6),
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isSyncing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Inventory Gallery'),
        centerTitle: true,
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _isSyncing ? null : _runSync,
        backgroundColor: _isSyncing
            ? _electricBlue.withValues(alpha: 0.5)
            : _electricBlue,
        icon: _isSyncing
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                    color: Colors.white, strokeWidth: 2.5))
            : const Icon(Icons.cloud_upload, color: Colors.white),
        label: Text(
          _isSyncing ? 'Syncing...' : 'Sync Captures',
          style: const TextStyle(
              color: Colors.white, fontWeight: FontWeight.bold),
        ),
      ),
      body: StreamBuilder<QuerySnapshot>(
        // Listen to the specific user's coins collection
        stream: FirebaseFirestore.instance
            .collection('users/eric@numista.ai/coins')
            .snapshots(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(
              child: CircularProgressIndicator(
                  color: _electricBlue),
            );
          }

          if (snapshot.hasError) {
            return Center(
              child: Text(
                'Error: ${snapshot.error}',
                style: const TextStyle(color: Colors.redAccent),
              ),
            );
          }

          if (!snapshot.hasData || snapshot.data!.docs.isEmpty) {
            return Center(
              child: Text(
                'No coins found in the vault.',
                style: TextStyle(
                  color: _electricBlue.withValues(alpha: 0.7),
                  fontStyle: FontStyle.italic,
                  fontSize: 18,
                ),
              ),
            );
          }

          final coins = snapshot.data!.docs;

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: coins.length,
            itemBuilder: (context, index) {
              final data = coins[index].data() as Map<String, dynamic>;

              final imageUrlObverse = data['image_url_obverse']?.toString();
              final imageUrlReverse = data['image_url_reverse']?.toString();

              // -------------------------------------------------------------
              // DATA MAPPING
              // -------------------------------------------------------------
              // Safely extract and clean values to prevent "null" or "NaN" strings
              final rawYear = data['Year']?.toString().trim() ?? '';
              final year = (rawYear.toLowerCase() == 'null' || rawYear.toLowerCase() == 'nan') ? '' : rawYear;

              final rawMint = data['Mint Mark']?.toString().trim() ?? '';
              final mintMark = (rawMint.toLowerCase() == 'null' || rawMint.toLowerCase() == 'nan') ? '' : rawMint;

              final rawDenom = data['Denomination']?.toString().trim() ?? '';
              final denomination = (rawDenom.toLowerCase() == 'null' || rawDenom.toLowerCase() == 'nan' || rawDenom.isEmpty)
                  ? 'Unknown Coin'
                  : rawDenom;

              final condition =
                  data['Condition']?.toString() ?? 'Unspecified Condition';
              final aiValue =
                  data['AI Estimated Value']?.toString() ?? 'Pending Value';
              final storageLocation =
                  data['Storage Location']?.toString() ?? 'Unassigned';

              final theme = data['Theme/Subject']?.toString().trim() ?? '';
              final program = data['Program/Series']?.toString().trim() ?? '';

              // Headline Logic: Skip missing Year/Mint Mark
              String titleText = '';
              if (year.isNotEmpty && mintMark.isNotEmpty) {
                titleText = '$year-$mintMark $denomination';
              } else if (year.isNotEmpty) {
                titleText = '$year $denomination';
              } else if (mintMark.isNotEmpty) {
                titleText = '$mintMark $denomination';
              } else {
                titleText = denomination;
              }
              titleText = titleText.trim();

              // Format subtitle: e.g., "New Jersey (50 State Quarters)"
              String subtitleText = '';
              if (theme.isNotEmpty && program.isNotEmpty) {
                subtitleText = '$theme ($program)';
              } else if (theme.isNotEmpty) {
                subtitleText = theme;
              } else if (program.isNotEmpty) {
                subtitleText = program;
              }

              // -------------------------------------------------------------
              // UI LAYOUT: COIN CARD
              // -------------------------------------------------------------
              return _buildCoinCard(
                title: titleText,
                subtitle: subtitleText,
                condition: condition,
                value: aiValue,
                storage: storageLocation,
                imageUrlObverse: imageUrlObverse,
                imageUrlReverse: imageUrlReverse,
              );
            },
          );
        },
      ),
    );
  }

  Widget _buildCoinCard({
    required String title,
    required String subtitle,
    required String condition,
    required String value,
    required String storage,
    String? imageUrlObverse,
    String? imageUrlReverse,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      decoration: BoxDecoration(
        color: const Color(0xFF2A2A2A), // Dark museum background
        borderRadius: BorderRadius.circular(15),
        // No-Line Rule: Borders are prohibited for sectioning.
        // Ambient Shadow Formula with a subtle AI-Blue tint for thematic consistency.
        boxShadow: [
          BoxShadow(
            color: _electricBlue.withValues(alpha: 0.12),
            offset: const Offset(0, 8),
            blurRadius: 24,
            spreadRadius: 0,
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Title Header: Neural Bronze
            Text(
              title,
              style: const TextStyle(
                color: _neuralBronze, // "Neural Bronze"
                fontSize: 22,
                fontWeight: FontWeight.bold,
                letterSpacing: 0.5,
              ),
            ),
            if (subtitle.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(
                subtitle,
                style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 14,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
            const Divider(color: Colors.white24, height: 24, thickness: 1),
            
            // Image Section (Flip / Side-by-Side UI)
            _buildImageSection(imageUrlObverse, imageUrlReverse),
            
            const SizedBox(height: 16),
            
            // Details Row
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildDetailColumn('Condition', condition),
                _buildDetailColumn('AI Est. Value', value),
              ],
            ),
            const SizedBox(height: 16),
            
            // Storage Location Tag
            Align(
              alignment: Alignment.centerRight,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: _charcoal,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.white12),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(
                      Icons.inventory_2_outlined,
                      size: 14,
                      color: Colors.white70,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      storage,
                      style: const TextStyle(
                        color: Colors.white70,
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildImageSection(String? obverse, String? reverse) {
    if (obverse == null && reverse == null) {
      // Placeholder Scenario B
      return Container(
        height: 120,
        width: double.infinity,
        decoration: BoxDecoration(
          color: Colors.white10,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: _electricBlue.withValues(alpha: 0.5)),
        ),
        child: const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.image_not_supported_outlined, color: _electricBlue, size: 32),
              SizedBox(height: 8),
              Text('No Images Found', style: TextStyle(color: Colors.white60, fontStyle: FontStyle.italic, fontSize: 12)),
            ],
          ),
        ),
      );
    }
    
    return Row(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        if (obverse != null) _buildImage(obverse, 'Obverse'),
        if (reverse != null) _buildImage(reverse, 'Reverse'),
      ],
    );
  }

  Widget _buildImage(String url, String label) {
    return Expanded(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 4.0),
        child: Column(
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.network(
                url,
                height: 120,
                fit: BoxFit.cover,
                errorBuilder: (ctx, err, stack) => Container(
                  height: 120,
                  decoration: BoxDecoration(color: Colors.white10, borderRadius: BorderRadius.circular(8)),
                  child: const Center(child: Icon(Icons.error, color: Colors.redAccent)),
                ),
              ),
            ),
            const SizedBox(height: 4),
            Text(label, style: const TextStyle(color: Colors.white54, fontSize: 10, fontWeight: FontWeight.bold)),
          ],
        ),
      ),
    );
  }

  Widget _buildDetailColumn(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label.toUpperCase(),
          style: const TextStyle(
            color: Colors.white54,
            fontSize: 10,
            fontWeight: FontWeight.w600,
            letterSpacing: 1.2,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }
}
