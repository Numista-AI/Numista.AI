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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text(
          'Admin Beta Dashboard',
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
    return StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
      stream: BetaFeedbackService.getFeedbackStream(),
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

        final docs = snapshot.data!.docs;

        // Compute averages
        double totalEase = 0;
        double totalFun = 0;
        double totalUtil = 0;
        int count = docs.length;

        for (final doc in docs) {
          final ratings = doc.data()['ratings'] as Map<String, dynamic>? ?? {};
          totalEase += (ratings['ease_of_use'] ?? 5) as int;
          totalFun += (ratings['fun_value'] ?? 5) as int;
          totalUtil += (ratings['utility_value'] ?? 5) as int;
        }

        final avgEase = count > 0 ? (totalEase / count).toStringAsFixed(1) : '5.0';
        final avgFun = count > 0 ? (totalFun / count).toStringAsFixed(1) : '5.0';
        final avgUtil = count > 0 ? (totalUtil / count).toStringAsFixed(1) : '5.0';

        return Column(
          children: [
            // Analytics Header Card
            Container(
              margin: const EdgeInsets.all(16),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.2)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildMetricStat('Total Feedback', '$count', Colors.blueAccent),
                  _buildMetricStat('Ease of Use', '⭐ $avgEase / 5', Colors.amber),
                  _buildMetricStat('Fun Value', '⭐ $avgFun / 5', Colors.purpleAccent),
                  _buildMetricStat('Utility', '⭐ $avgUtil / 5', Colors.green),
                ],
              ),
            ),

            // Feedback Cards Stream List
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: docs.length,
                itemBuilder: (context, index) {
                  final data = docs[index].data();
                  final id = docs[index].id;
                  final route = data['route'] ?? 'Unknown Route';
                  final email = data['user_email'] ?? 'Anonymous';
                  final category = data['category'] ?? 'General';
                  final comment = data['comment'] ?? '';
                  final status = data['status'] ?? 'OPEN';
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
                        crossAxisAlignment: CrossAlignment.start,
                        children: [
                          // Header Row
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 8, vertical: 4),
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
                                    BetaFeedbackService.updateFeedbackStatus(
                                        id, newStatus);
                                  }
                                },
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),

                          // Route & Email
                          Text(
                            'User: $email | Route: $route',
                            style: const TextStyle(
                                color: Colors.grey, fontSize: 12),
                          ),
                          const SizedBox(height: 8),

                          // Ratings
                          Text(
                            'Ratings: Ease ⭐${ratings['ease_of_use'] ?? 5} | Fun ⭐${ratings['fun_value'] ?? 5} | Utility ⭐${ratings['utility_value'] ?? 5}',
                            style: const TextStyle(
                              color: Colors.amber,
                              fontSize: 13,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(height: 10),

                          // Comment
                          if (comment.isNotEmpty)
                            Text(
                              comment,
                              style: const TextStyle(
                                  color: Colors.white, fontSize: 14),
                            ),

                          // Screenshot Link
                          if (screenshotUrl != null && screenshotUrl.isNotEmpty) ...[
                            const SizedBox(height: 10),
                            OutlinedButton.icon(
                              onPressed: () async {
                                final uri = Uri.parse(screenshotUrl);
                                if (await canLaunchUrl(uri)) {
                                  await launchUrl(uri);
                                }
                              },
                              icon: const Icon(Icons.image,
                                  size: 16, color: Colors.blueAccent),
                              label: const Text(
                                'View Screenshot',
                                style: TextStyle(
                                    color: Colors.blueAccent, fontSize: 12),
                              ),
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
            crossAlignment: CrossAlignment.start,
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
                        label: const Text('Add Beta Tester',
                            style: TextStyle(color: Colors.white)),
                        onPressed: () async {
                          final email = _testerEmailController.text.trim();
                          if (email.isNotEmpty) {
                            await FirebaseFirestore.instance
                                .collection('users')
                                .doc(email)
                                .set({'isBetaTester': true}, SetOptions(merge: true));
                            _testerEmailController.clear();
                            if (mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                    content: Text(
                                        'Granted Beta Tester status to $email')),
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
                style: TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold),
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
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8)),
                      title: Text(email,
                          style: const TextStyle(color: Colors.white)),
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
