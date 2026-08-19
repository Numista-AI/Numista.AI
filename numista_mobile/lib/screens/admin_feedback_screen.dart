import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/beta_feedback_service.dart';

class AdminFeedbackScreen extends StatefulWidget {
  const AdminFeedbackScreen({super.key});

  @override
  State<AdminFeedbackScreen> createState() => _AdminFeedbackScreenState();
}

class _AdminFeedbackScreenState extends State<AdminFeedbackScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _testerEmailController = TextEditingController();
  String _selectedCategoryFilter = 'ALL';
  String _selectedStatusFilter = 'ALL';

  final List<String> _categories = [
    'ALL',
    'Bug Report',
    'UI / Layout Suggestion',
    'Confusing / Hard to Use',
    'Feature Request',
    'Praise / What Works Well',
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _testerEmailController.dispose();
    super.dispose();
  }

  void _openLightboxModal(BuildContext context, String imageUrl) {
    showDialog(
      context: context,
      builder: (ctx) => Dialog(
        backgroundColor: Colors.transparent,
        insetPadding: const EdgeInsets.all(16),
        child: Stack(
          alignment: Alignment.center,
          children: [
            Container(
              constraints: const BoxConstraints(maxHeight: 700, maxWidth: 900),
              decoration: BoxDecoration(
                color: const Color(0xFF0F172A),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.3)),
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.network(
                  imageUrl,
                  fit: BoxFit.contain,
                  loadingBuilder: (_, child, progress) {
                    if (progress == null) return child;
                    return const Center(child: CircularProgressIndicator());
                  },
                  errorBuilder: (_, __, ___) => const Center(
                    child: Padding(
                      padding: EdgeInsets.all(32.0),
                      child: Text('Failed to load screenshot image.', style: TextStyle(color: Colors.redAccent)),
                    ),
                  ),
                ),
              ),
            ),
            Positioned(
              top: 10,
              right: 10,
              child: CircleAvatar(
                backgroundColor: Colors.black54,
                child: IconButton(
                  icon: const Icon(Icons.close, color: Colors.white),
                  onPressed: () => Navigator.of(ctx).pop(),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _promptResolutionNote(String feedbackId, String currentStatus) {
    final noteController = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('Update Status & Log Note', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Change status to: $currentStatus', style: const TextStyle(color: Colors.lightBlueAccent, fontWeight: FontWeight.w600)),
            const SizedBox(height: 12),
            TextField(
              controller: noteController,
              maxLines: 2,
              style: const TextStyle(color: Colors.white),
              decoration: InputDecoration(
                hintText: 'Optional resolution or triage notes...',
                hintStyle: const TextStyle(color: Colors.grey),
                filled: true,
                fillColor: const Color(0xFF0F172A),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent),
            onPressed: () async {
              Navigator.of(ctx).pop();
              final note = noteController.text.trim();
              // Route through ADMIN_RESOLVE callable — server enforces
              // resolution_note requirement for DATA_INTEGRITY tickets.
              await BetaFeedbackService.adminResolve(
                docId: feedbackId,
                resolutionNote: note,
                newStatus: currentStatus,
              );
            },
            child: const Text('Save Status', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          'Admin Beta Feedback Portal',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.blueAccent,
          labelColor: Colors.blueAccent,
          unselectedLabelColor: Colors.grey,
          tabs: const [
            Tab(icon: Icon(Icons.rate_review), text: 'Feedback Submissions'),
            Tab(icon: Icon(Icons.people), text: 'Manage Testers'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildFeedbackSubmissionsTab(),
          _buildManageTestersTab(),
        ],
      ),
    );
  }

  // ─── TAB 1: Feedback Submissions ──────────────────────────────────────────

  Widget _buildFeedbackSubmissionsTab() {
    // Admin reads go directly to Firestore (only writes are callable-gated).
    final feedbackStream = FirebaseFirestore.instance
        .collection('beta_feedback')
        .orderBy('created_at', descending: true)
        .snapshots();
    return StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
      stream: feedbackStream,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        if (!snapshot.hasData || snapshot.data!.docs.isEmpty) {
          return const Center(
            child: Text(
              'No feedback submissions received yet.',
              style: TextStyle(color: Colors.grey, fontSize: 16),
            ),
          );
        }

        final allDocs = snapshot.data!.docs;

        // Apply Status and Category Filtering
        final docs = allDocs.where((doc) {
          final data = doc.data();
          final cat = data['category']?.toString() ?? 'General';
          final st = data['status']?.toString() ?? 'OPEN';

          final catMatch = _selectedCategoryFilter == 'ALL' || cat == _selectedCategoryFilter;
          final statusMatch = _selectedStatusFilter == 'ALL' || st == _selectedStatusFilter;
          return catMatch && statusMatch;
        }).toList();

        // Compute averages across all submissions
        double totalEase = 0;
        double totalAesthetics = 0;
        double totalUtil = 0;
        int count = allDocs.length;

        for (final doc in allDocs) {
          final ratings = doc.data()['ratings'] as Map<String, dynamic>? ?? {};
          totalEase += (ratings['ease_of_use'] ?? 5) as int;
          totalAesthetics += (ratings['design_aesthetics'] ?? 5) as int;
          totalUtil += (ratings['utility_value'] ?? 5) as int;
        }

        final avgEase = count > 0 ? (totalEase / count).toStringAsFixed(1) : '5.0';
        final avgAesthetics = count > 0 ? (totalAesthetics / count).toStringAsFixed(1) : '5.0';
        final avgUtil = count > 0 ? (totalUtil / count).toStringAsFixed(1) : '5.0';

        final openCount = allDocs.where((d) => (d.data()['status'] ?? 'OPEN') == 'OPEN').length;

        return Column(
          children: [
            // Analytics Header Card
            Container(
              margin: const EdgeInsets.fromLTRB(16, 16, 16, 8),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.2)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildMetricStat('Open Feedback', '$openCount of $count', Colors.blueAccent),
                  _buildMetricStat('Ease of Use', '⭐ $avgEase / 5', Colors.amber),
                  _buildMetricStat('Aesthetics', '⭐ $avgAesthetics / 5', Colors.purpleAccent),
                  _buildMetricStat('Utility', '⭐ $avgUtil / 5', Colors.green),
                ],
              ),
            ),

            // Category & Status Filters Toolbar
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 6.0),
              child: Row(
                children: [
                  const Text('Category: ', style: TextStyle(color: Colors.grey, fontSize: 13, fontWeight: FontWeight.bold)),
                  Expanded(
                    child: SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        children: _categories.map((cat) {
                          final isSelected = _selectedCategoryFilter == cat;
                          return Padding(
                            padding: const EdgeInsets.only(right: 6.0),
                            child: FilterChip(
                              selected: isSelected,
                              label: Text(cat, style: TextStyle(fontSize: 11, color: isSelected ? Colors.white : Colors.grey)),
                              selectedColor: Colors.blueAccent,
                              backgroundColor: const Color(0xFF1E293B),
                              onSelected: (val) {
                                setState(() {
                                  _selectedCategoryFilter = cat;
                                });
                              },
                            ),
                          );
                        }).toList(),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Feedback Cards Stream List
            Expanded(
              child: docs.isEmpty
                  ? const Center(
                      child: Text(
                        'No submissions match the selected filters.',
                        style: TextStyle(color: Colors.grey, fontSize: 14),
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                      itemCount: docs.length,
                      itemBuilder: (context, index) {
                        final data = docs[index].data();
                        final id = docs[index].id;
                        final route = data['route'] ?? 'Unknown Route';
                        final email = data['user_email'] ?? 'Anonymous';
                        final category = data['category'] ?? 'General';
                        final comment = data['comment'] ?? '';
                        final status = data['status'] ?? 'OPEN';
                        final resolutionNote = data['resolution_note'] as String?;
                        final screenshotUrl = data['screenshot_url'] as String?;
                        final ratings = data['ratings'] as Map<String, dynamic>? ?? {};

                        Color statusColor = Colors.orange;
                        if (status == 'TRIAGED') statusColor = Colors.blueAccent;
                        if (status == 'RESOLVED') statusColor = Colors.green;

                        return Card(
                          color: const Color(0xFF1E293B),
                          margin: const EdgeInsets.only(bottom: 12),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                            side: BorderSide(
                              color: statusColor.withValues(alpha: 0.3),
                            ),
                          ),
                          child: Padding(
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                // Header Row
                                Row(
                                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                  children: [
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                      decoration: BoxDecoration(
                                        color: Colors.blue.withValues(alpha: 0.15),
                                        borderRadius: BorderRadius.circular(6),
                                      ),
                                      child: Text(
                                        category,
                                        style: const TextStyle(
                                          color: Colors.lightBlueAccent,
                                          fontSize: 12,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                    ),
                                    DropdownButton<String>(
                                      value: status,
                                      dropdownColor: const Color(0xFF0F172A),
                                      underline: const SizedBox.shrink(),
                                      items: ['OPEN', 'TRIAGED', 'RESOLVED']
                                          .map((s) => DropdownMenuItem(
                                                value: s,
                                                child: Text(
                                                  s,
                                                  style: TextStyle(
                                                    color: s == 'RESOLVED'
                                                        ? Colors.green
                                                        : s == 'TRIAGED'
                                                            ? Colors.blueAccent
                                                            : Colors.orange,
                                                    fontSize: 12,
                                                    fontWeight: FontWeight.bold,
                                                  ),
                                                ),
                                              ))
                                          .toList(),
                                      onChanged: (newStatus) {
                                        if (newStatus != null) {
                                          _promptResolutionNote(id, newStatus);
                                        }
                                      },
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 8),

                                // Route & Email
                                Text(
                                  'User: $email | Route: $route',
                                  style: const TextStyle(color: Colors.grey, fontSize: 12),
                                ),
                                const SizedBox(height: 8),

                                // Ratings
                                Text(
                                  'Ratings: Ease ⭐${ratings['ease_of_use'] ?? 5} | Aesthetics ⭐${ratings['design_aesthetics'] ?? 5} | Utility ⭐${ratings['utility_value'] ?? 5}',
                                  style: const TextStyle(
                                    color: Colors.amber,
                                    fontSize: 13,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                                const SizedBox(height: 10),

                                // Comment
                                if (comment.isNotEmpty)
                                  Container(
                                    padding: const EdgeInsets.all(10),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFF0F172A),
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                    child: Text(
                                      comment,
                                      style: const TextStyle(color: Colors.white, fontSize: 14),
                                    ),
                                  ),

                                // Resolution Note if present
                                if (resolutionNote != null && resolutionNote.isNotEmpty) ...[
                                  const SizedBox(height: 8),
                                  Text(
                                    'Resolution Note: $resolutionNote',
                                    style: const TextStyle(color: Colors.greenAccent, fontSize: 12, fontStyle: FontStyle.italic),
                                  ),
                                ],

                                // Inline Screenshot Thumbnail Preview
                                if (screenshotUrl != null && screenshotUrl.isNotEmpty) ...[
                                  const SizedBox(height: 12),
                                  Row(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      GestureDetector(
                                        onTap: () => _openLightboxModal(context, screenshotUrl),
                                        child: Container(
                                          width: 160,
                                          height: 100,
                                          decoration: BoxDecoration(
                                            borderRadius: BorderRadius.circular(8),
                                            border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.4)),
                                          ),
                                          child: ClipRRect(
                                            borderRadius: BorderRadius.circular(8),
                                            child: Stack(
                                              fit: StackFit.expand,
                                              children: [
                                                Image.network(
                                                  screenshotUrl,
                                                  fit: BoxFit.cover,
                                                  errorBuilder: (_, __, ___) => const Center(
                                                    child: Text('Invalid Image', style: TextStyle(color: Colors.grey, fontSize: 11)),
                                                  ),
                                                ),
                                                Positioned(
                                                  bottom: 4,
                                                  right: 4,
                                                  child: Container(
                                                    padding: const EdgeInsets.all(4),
                                                    decoration: BoxDecoration(
                                                      color: Colors.black54,
                                                      borderRadius: BorderRadius.circular(4),
                                                    ),
                                                    child: const Icon(Icons.zoom_in, color: Colors.white, size: 14),
                                                  ),
                                                ),
                                              ],
                                            ),
                                          ),
                                        ),
                                      ),
                                      const SizedBox(width: 12),
                                      Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: [
                                          const Text(
                                            'Attached Screenshot',
                                            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13),
                                          ),
                                          const SizedBox(height: 4),
                                          const Text(
                                            'Tap image to enlarge',
                                            style: TextStyle(color: Colors.grey, fontSize: 12),
                                          ),
                                          const SizedBox(height: 8),
                                          OutlinedButton.icon(
                                            onPressed: () async {
                                              final uri = Uri.parse(screenshotUrl);
                                              if (await canLaunchUrl(uri)) {
                                                await launchUrl(uri);
                                              }
                                            },
                                            icon: const Icon(Icons.open_in_new, size: 14, color: Colors.blueAccent),
                                            label: const Text('Open External', style: TextStyle(fontSize: 11, color: Colors.blueAccent)),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ],
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
    );
  }

  Widget _buildMetricStat(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            color: color,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(color: Colors.grey, fontSize: 12),
        ),
      ],
    );
  }

  // ─── TAB 2: Manage Testers ────────────────────────────────────────────────

  Widget _buildManageTestersTab() {
    return StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
      stream: FirebaseFirestore.instance.collection('users').snapshots(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }

        final users = snapshot.data?.docs ?? [];

        return Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Add Tester Card
              Card(
                color: const Color(0xFF1E293B),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _testerEmailController,
                          style: const TextStyle(color: Colors.white),
                          decoration: const InputDecoration(
                            hintText: 'Enter tester email address...',
                            hintStyle: TextStyle(color: Colors.grey),
                            border: InputBorder.none,
                          ),
                        ),
                      ),
                      ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blueAccent,
                        ),
                        icon: const Icon(Icons.person_add, color: Colors.white),
                        label: const Text('Add Beta Tester', style: TextStyle(color: Colors.white)),
                        onPressed: () async {
                          final email = _testerEmailController.text.trim();
                          if (email.isNotEmpty) {
                            final messenger = ScaffoldMessenger.of(context);
                            await FirebaseFirestore.instance
                                .collection('users')
                                .doc(email)
                                .set({'isBetaTester': true}, SetOptions(merge: true));
                            _testerEmailController.clear();
                            if (mounted) {
                              messenger.showSnackBar(
                                SnackBar(content: Text('Granted Beta Tester status to $email')),
                              );
                            }
                          }
                        },
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              const Text(
                'Active Testers List',
                style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),

              Expanded(
                child: ListView.builder(
                  itemCount: users.length,
                  itemBuilder: (context, index) {
                    final doc = users[index];
                    final email = doc.id;
                    final isBeta = (doc.data()['isBetaTester'] ?? false) as bool;

                    return ListTile(
                      tileColor: const Color(0xFF1E293B),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      title: Text(email, style: const TextStyle(color: Colors.white)),
                      trailing: Switch(
                        value: isBeta,
                        activeColor: Colors.blueAccent,
                        onChanged: (val) async {
                          await FirebaseFirestore.instance
                              .collection('users')
                              .doc(email)
                              .set({'isBetaTester': val}, SetOptions(merge: true));
                        },
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}
