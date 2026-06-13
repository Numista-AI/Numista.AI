import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/auth_service.dart';
import '../services/guest_seed_service.dart';
import '../services/morgan_prefs.dart';
import '../widgets/morgan_settings_panel.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../constants.dart';

import '../utils/file_saver_stub.dart'
    if (dart.library.html) '../utils/file_saver_web.dart'
    if (dart.library.io) '../utils/file_saver_io.dart';

import '../services/epn_service.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _campIdController = TextEditingController();
  final _mkridController = TextEditingController();
  final _appIdController = TextEditingController();
  final _certIdController = TextEditingController();
  bool _isLoading = true;
  bool _dedupRunning = false;
  Map<String, dynamic>? _dedupResults;

  static const _apiUrl = kApiBaseUrl;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final settings = await EpnService.getSettings();
    setState(() {
      _campIdController.text = settings['campaignId'] ?? '';
      _mkridController.text = settings['rotationId'] ?? '';
      _appIdController.text = settings['appId'] ?? '';
      _certIdController.text = settings['certId'] ?? '';
      _isLoading = false;
    });
  }

  Future<void> _saveEpnSettings() async {
    await EpnService.saveSettings(
      _campIdController.text.trim(),
      _mkridController.text.trim(),
      appId: _appIdController.text.trim(),
      certId: _certIdController.text.trim(),
    );
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Affiliate settings saved!')),
      );
    }
  }

  @override
  void dispose() {
    _campIdController.dispose();
    _mkridController.dispose();
    _appIdController.dispose();
    _certIdController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator(color: Color(0xFFD4A843)));
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(32.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          const Text(
            'Settings & Backup',
            style: TextStyle(fontSize: 32, fontWeight: FontWeight.w900, fontStyle: FontStyle.italic, color: Color(0xFF31333F)),
          ),
          const SizedBox(height: 8),
          const Text('Manage your account preferences and export data.', style: TextStyle(color: Color(0xFF64748B), fontSize: 14)),
          const SizedBox(height: 32),
          
          // ── Morgan Settings Section ───────────────────────────────────
          _buildMorganCard(context),
          const SizedBox(height: 24),
          const Divider(color: Color(0xFFE2E6E9)),
          const SizedBox(height: 24),

          // ── Data Export Card ───────────────────────────────────────
          _buildSettingsCard(
            context,
            icon: Icons.download,
            title: 'Export Collection to CSV',
            description: 'Download a complete spreadsheet of your entire Numista.AI collection.',
            actionLabel: 'Download CSV',
            onAction: () {
              if (!GuestSeedService.canDownload) {
                showDialog(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    title: const Text('Create a Free Account'),
                    content: const Text(
                        'CSV export is available to registered users. Create a free account to download your collection — your current session will be saved automatically.'),
                    actions: [
                      TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Not Now')),
                      ElevatedButton(
                        style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF1565C0)),
                        onPressed: () => Navigator.pop(ctx),
                        child: const Text('Create Account', style: TextStyle(color: Colors.white)),
                      ),
                    ],
                  ),
                );
              } else {
                _exportToCsv(context);
              }
            },
            isPrimary: true,
          ),

          const SizedBox(height: 16),
          // ── Dedup Sweep card ───────────────────────────────────────────────
          _buildDedupCard(context),

          const SizedBox(height: 16),
          _buildSettingsCard(
            context,
            icon: Icons.feedback_outlined,
            title: 'Submit App Feedback',
            description: 'Found a bug or have a feature suggestion? Let us know!',
            actionLabel: 'Send Email',
            onAction: () async {
              final Uri emailLaunchUri = Uri(
                scheme: 'mailto',
                path: 'eric@numista.ai',
                queryParameters: {
                  'subject': 'Numista.AI Beta Feedback',
                  'body': 'Hi Numista.AI Team,\n\nHere is my feedback on the beta:\n\n',
                },
              );
              try {
                if (await canLaunchUrl(emailLaunchUri)) {
                  await launchUrl(emailLaunchUri, mode: LaunchMode.externalApplication);
                } else {
                  throw 'Could not launch email';
                }
              } catch (e) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Could not open email client. Please send feedback to eric@numista.ai.'),
                    ),
                  );
                }
              }
            },
            isPrimary: false,
          ),
          
          const SizedBox(height: 32),
          const Divider(color: Color(0xFFE2E6E9)),
          const SizedBox(height: 32),

          // EPN / Affiliate Section -- only visible to admin (eric@numista.ai)
          if (AuthService.userEmail.toLowerCase() == 'eric@numista.ai') ...[
          const Text('eBay Partner Network (EPN)', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
          const SizedBox(height: 8),
          const Text(
            'Monetize your shared wishlist. Enter your EPN credentials to earn commissions when others buy coins through your links.',
            style: TextStyle(color: Color(0xFF64748B), fontSize: 14),
          ),
          const SizedBox(height: 16),
          
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border.all(color: const Color(0xFFE2E6E9)),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                TextField(
                  controller: _campIdController,
                  decoration: const InputDecoration(
                    labelText: 'Campaign ID',
                    hintText: 'e.g. 5339055376',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _mkridController,
                  decoration: const InputDecoration(
                    labelText: 'Rotation ID (Marketplace)',
                    hintText: 'e.g. 711-53200-19255-0',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                InkWell(
                  onTap: () => launchUrl(Uri.parse('https://partner.ebay.com')),
                  child: const Text(
                    'What is a Campaign ID? Learn more at partner.ebay.com',
                    style: TextStyle(color: Color(0xFF3B82F6), fontSize: 13, decoration: TextDecoration.underline),
                  ),
                ),
                const SizedBox(height: 32),
                const Text('eBay Developer API (Optional)', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
                const SizedBox(height: 8),
                const Text(
                  'Enter these to enable live price lookups and current listings in your collection and wishlist.',
                  style: TextStyle(color: Color(0xFF64748B), fontSize: 13),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _appIdController,
                  decoration: const InputDecoration(
                    labelText: 'App ID (Client ID)',
                    hintText: 'e.g. SGroup-NumismaA-PRD-f18f0640-...',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _certIdController,
                  obscureText: true,
                  decoration: const InputDecoration(
                    labelText: 'Cert ID (Client Secret)',
                    hintText: 'PRD-118f0640b6a9-...',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                InkWell(
                  onTap: () => launchUrl(Uri.parse('https://developer.ebay.com/my/keys')),
                  child: const Text(
                    'Get your API keys at developer.ebay.com',
                    style: TextStyle(color: Color(0xFF3B82F6), fontSize: 13, decoration: TextDecoration.underline),
                  ),
                ),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: _saveEpnSettings,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF0F172A),
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: const Text('Save Affiliate Settings', style: TextStyle(color: Colors.white)),
                  ),
                ),
              ],
            ),
          ),
          ], // end admin-only EPN section
          
          const SizedBox(height: 32),
          const Divider(color: Color(0xFFE2E6E9)),
          const SizedBox(height: 32),
          
          // Account Settings
          const Text('Account Management', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
          const SizedBox(height: 16),
          
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white,
              border: Border.all(color: const Color(0xFFE2E6E9)),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                const CircleAvatar(
                  radius: 32,
                  backgroundColor: Color(0xFFF1F5F9),
                  child: Icon(Icons.person, size: 32, color: Color(0xFF94A3B8)),
                ),
                const SizedBox(width: 24),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(AuthService.displayName, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: Color(0xFF0F172A))),
                    Text(AuthService.userEmail, style: const TextStyle(color: Color(0xFF64748B), fontSize: 14)),
                  ],
                ),
                const Spacer(),
                OutlinedButton.icon(
                  onPressed: () => AuthService.resetPin(AuthService.userEmail),
                  icon: const Icon(Icons.lock_reset, size: 16),
                  label: const Text('Reset PIN'),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF31333F),
                  ),
                ),
              ],
            ),
          )
        ],
      ),
    );
  }

  // ─── Dedup Sweep ─────────────────────────────────────────────────────────

  Widget _buildDedupCard(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: const Color(0xFFE2E6E9)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFFFF7ED),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.find_replace_rounded,
                color: Color(0xFFF97316)),
          ),
          const SizedBox(width: 24),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Find & Merge Duplicates',
                    style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                        color: Color(0xFF0F172A))),
                const SizedBox(height: 4),
                Text(
                  _dedupResults == null
                      ? 'Scan your collection for coins that may have been imported more than once.'
                      : 'Found ${_dedupResults!["duplicate_groups"]} duplicate group(s) in ${_dedupResults!["total_coins"]} coins.',
                  style:
                      const TextStyle(color: Color(0xFF64748B), fontSize: 14),
                ),
              ],
            ),
          ),
          const SizedBox(width: 24),
          _dedupRunning
              ? const SizedBox(
                  width: 24,
                  height: 24,
                  child: CircularProgressIndicator(
                      strokeWidth: 2, color: Color(0xFFF97316)))
              : ElevatedButton(
                  onPressed: _runDedupSweep,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFF97316),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                        horizontal: 24, vertical: 16),
                  ),
                  child: Text(_dedupResults == null ? 'Scan Now' : 'Re-Scan'),
                ),
        ],
      ),
    );
  }

  Future<void> _runDedupSweep() async {
    if (!GuestSeedService.canDownload) {
      ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Sign in to use duplicate detection.')));
      return;
    }
    setState(() => _dedupRunning = true);
    try {
      final resp = await http.post(
        Uri.parse('$_apiUrl/api/dedup_sweep'),
        body: {'user_email': AuthService.userEmail},
      );
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as Map<String, dynamic>;
        setState(() => _dedupResults = data);
        if (mounted) _showDedupResultsDialog(data);
      } else {
        throw Exception('HTTP ${resp.statusCode}');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Sweep failed: $e'),
                backgroundColor: Colors.red));
      }
    } finally {
      if (mounted) setState(() => _dedupRunning = false);
    }
  }

  void _showDedupResultsDialog(Map<String, dynamic> data) {
    final groups =
        (data['duplicates'] as List).cast<Map<String, dynamic>>();
    showDialog<void>(
      context: context,
      builder: (ctx) => _DedupDialog(
        groups: groups,
        userEmail: AuthService.userEmail,
        onDeleted: (docId) async {
          await FirebaseFirestore.instance
              .collection(AuthService.coinsPath)
              .doc(docId)
              .delete();
          // Re-run sweep to refresh results
          if (mounted) _runDedupSweep();
        },
      ),
    );
  }

  // ── Morgan Settings Card ────────────────────────────────────────────────────
  Widget _buildMorganCard(BuildContext context) {
    return FutureBuilder<String?>(
      future: MorganPrefs.getPreferredName(),
      builder: (ctx, snap) {
        final name = (snap.data ?? '').isNotEmpty ? snap.data! : null;
        return Container(
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF0B1220), Color(0xFF112240)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
                color: const Color(0xFFD4A843).withAlpha(60), width: 1.5),
          ),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                // Avatar
                Container(
                  width: 52, height: 52,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: const LinearGradient(
                      colors: [Color(0xFFD4A843), Color(0xFF8B6914)],
                    ),
                    border: Border.all(
                        color: const Color(0xFFD4A843).withAlpha(120), width: 2),
                  ),
                  child: ClipOval(
                    child: Image.asset(
                      'assets/morgan_avatar.png',
                      fit: BoxFit.cover,
                      errorBuilder: (ctx2, err, stack) => const Icon(
                          Icons.smart_toy_rounded,
                          color: Colors.white, size: 26),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                // Text
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Morgan — Your AI Guide',
                          style: TextStyle(
                              color: Colors.white,
                              fontSize: 15,
                              fontWeight: FontWeight.bold)),
                      const SizedBox(height: 3),
                      Text(
                        name != null
                            ? 'Morgan knows you as "$name"'
                            : 'Tell Morgan your name to personalise your experience',
                        style: const TextStyle(
                            color: Color(0xFF94A3B8), fontSize: 12),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                // Button
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2DD4BF),
                    foregroundColor: Colors.black87,
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8)),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 12),
                    elevation: 0,
                  ),
                  onPressed: () async {
                    final changed = await showMorganSettings(context);
                    if (changed && mounted) setState(() {});
                  },
                  child: const Text('Personalise',
                      style: TextStyle(
                          fontWeight: FontWeight.bold, fontSize: 13)),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildSettingsCard(BuildContext context, {required IconData icon, required String title, required String description, required String actionLabel, required VoidCallback onAction, bool isPrimary = false}) {

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: const Color(0xFFE2E6E9)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: isPrimary ? const Color(0xFFEFF6FF) : const Color(0xFFF1F5F9),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: isPrimary ? const Color(0xFF3B82F6) : const Color(0xFF64748B)),
          ),
          const SizedBox(width: 24),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF0F172A))),
                const SizedBox(height: 4),
                Text(description, style: const TextStyle(color: Color(0xFF64748B), fontSize: 14)),
              ],
            ),
          ),
          const SizedBox(width: 24),
          ElevatedButton(
            onPressed: onAction,
            style: ElevatedButton.styleFrom(
              backgroundColor: isPrimary ? const Color(0xFF3B82F6) : Colors.white,
              foregroundColor: isPrimary ? Colors.white : const Color(0xFF0F172A),
              elevation: isPrimary ? 2 : 0,
              side: isPrimary ? null : const BorderSide(color: Color(0xFFE2E6E9)),
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
            ),
            child: Text(actionLabel),
          ),
        ],
      ),
    );
  }

  Future<void> _exportToCsv(BuildContext context) async {
    try {
      final snapshot = await FirebaseFirestore.instance.collection(AuthService.coinsPath).get();
      if (snapshot.docs.isEmpty) {
        if (!context.mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('No coins to export.')));
        return;
      }
      
      final Set<String> headersSet = {};
      for (var doc in snapshot.docs) {
        headersSet.addAll((doc.data()).keys);
      }
      final headers = headersSet.toList()..sort();
      
      final StringBuffer csv = StringBuffer();
      csv.writeln(headers.map((h) => '"$h"').join(','));
      
      for (var doc in snapshot.docs) {
        final data = doc.data();
        final row = headers.map((h) {
          final val = data[h]?.toString() ?? '';
          return '"${val.replaceAll("\"", "\"\"")}"';
        }).join(',');
        csv.writeln(row);
      }
      
      final bytes = utf8.encode(csv.toString());
      final filename = "numista_export_${DateTime.now().toIso8601String().split('T').first}.csv";

      final result = await downloadCsvFile(bytes, filename);
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Exported ${snapshot.docs.length} coins to $result'),
          backgroundColor: Colors.green.shade700,
        ),
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Export failed: $e'), backgroundColor: Colors.red));
      }
    }
  }
}

// ─── Duplicate Results Dialog ─────────────────────────────────────────────────

class _DedupDialog extends StatefulWidget {
  final List<Map<String, dynamic>> groups;
  final Future<void> Function(String docId) onDeleted;
  final String userEmail;

  const _DedupDialog({
    required this.groups,
    required this.onDeleted,
    required this.userEmail,
  });

  @override
  State<_DedupDialog> createState() => _DedupDialogState();
}

class _DedupDialogState extends State<_DedupDialog> {
  final Set<String> _deleting = {};
  bool _autoCleanRunning = false;

  static const _apiUrl = kApiBaseUrl;

  // Groups the auto-clean will process: invoice + attribute (NOT possible)
  int get _cleanableGroupCount =>
      widget.groups.where((g) =>
        g['match_type'] == 'invoice' || g['match_type'] == 'attribute').length;

  Future<void> _autoClean() async {
    final nav = Navigator.of(context);

    // Build cleanable groups: invoice + attribute matches (NOT possible)
    final cleanableGroups = widget.groups
        .where((g) =>
            g['match_type'] == 'invoice' || g['match_type'] == 'attribute')
        .toList();

    // Count how many coins would be deleted
    int willDelete = 0;
    for (final g in cleanableGroups) {
      final coins = (g['coins'] as List).cast<Map<String, dynamic>>();
      willDelete += coins.length - 1; // keep 1, delete rest
    }

    // Show detailed preview before committing
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => Dialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        insetPadding: const EdgeInsets.symmetric(horizontal: 32, vertical: 40),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 680, maxHeight: 560),
          child: Column(
            children: [
              // Header
              Container(
                padding: const EdgeInsets.fromLTRB(20, 18, 12, 14),
                decoration: const BoxDecoration(
                  color: Color(0xFFFFF1F2),
                  borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
                ),
                child: Row(children: [
                  const Icon(Icons.warning_amber_rounded,
                      color: Color(0xFFE11D48), size: 22),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Review: $willDelete coin${willDelete == 1 ? '' : 's'} will be deleted',
                          style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                              color: Color(0xFF0F172A)),
                        ),
                        const SizedBox(height: 3),
                        const Text(
                          'Invoice Match groups: same Invoice # + Item # imported twice.\n'
                          'Attribute Match groups: identical coin on the same purchase date.\n'
                          '🔵 Multiple Copies are NOT auto-cleaned — those need manual review.\n'
                          'One copy per group is always kept (shown in green).',
                          style: TextStyle(
                              color: Color(0xFF64748B), fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, size: 18),
                    onPressed: () => Navigator.pop(ctx, false),
                  ),
                ]),
              ),
              // Scrollable preview
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: cleanableGroups.length,
                  itemBuilder: (_, gi) {
                    final group = cleanableGroups[gi];
                    final coins = (group['coins'] as List)
                        .cast<Map<String, dynamic>>();
                    final isInvoice = (group['match_type'] as String? ?? '') == 'invoice';
                    final invLabel = isInvoice
                        ? 'Invoice ${coins.first['invoice']} · '
                        : '';
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Group label
                          Padding(
                            padding: const EdgeInsets.only(bottom: 4),
                            child: Text(
                              '$invLabel'
                              '${coins.first['year']} ${coins.first['denom']}'
                              '${((coins.first['theme'] as String?) ?? '').isNotEmpty ? ' · ${coins.first['theme']}' : ''}'
                              '${!isInvoice && ((coins.first['date'] as String?) ?? '').isNotEmpty ? ' · ${coins.first['date']}' : ''}',
                              style: const TextStyle(
                                  fontWeight: FontWeight.w600,
                                  fontSize: 13,
                                  color: Color(0xFF0F172A)),
                            ),
                          ),
                          ...coins.asMap().entries.map((e) {
                            final keep = e.key == 0;
                            return Container(
                              margin: const EdgeInsets.only(bottom: 3),
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 10, vertical: 6),
                              decoration: BoxDecoration(
                                color: keep
                                    ? const Color(0xFFF0FDF4)
                                    : const Color(0xFFFFF1F2),
                                border: Border.all(
                                    color: keep
                                        ? const Color(0xFFBBF7D0)
                                        : const Color(0xFFFFCDD2)),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Row(children: [
                                Icon(
                                  keep
                                      ? Icons.check_circle_outline
                                      : Icons.delete_outline,
                                  size: 14,
                                  color: keep
                                      ? const Color(0xFF16A34A)
                                      : const Color(0xFFE11D48),
                                ),
                                const SizedBox(width: 6),
                                Expanded(
                                  child: Text(
                                    [
                                      if (((e.value['year'] as String?) ?? '').isNotEmpty) e.value['year'],
                                      if (((e.value['mint'] as String?) ?? '').isNotEmpty) e.value['mint'],
                                      if (((e.value['cond'] as String?) ?? '').isNotEmpty) e.value['cond'],
                                      if (((e.value['date'] as String?) ?? '').isNotEmpty) 'Date: ${e.value['date']}',
                                    ].join(' · '),
                                    style: TextStyle(
                                        fontSize: 12,
                                        color: keep
                                            ? const Color(0xFF15803D)
                                            : const Color(0xFF9F1239)),
                                  ),
                                ),
                                Text(
                                  keep ? 'KEEP' : 'DELETE',
                                  style: TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.bold,
                                      color: keep
                                          ? const Color(0xFF16A34A)
                                          : const Color(0xFFE11D48)),
                                ),
                              ]),
                            );
                          }),
                          if (gi < cleanableGroups.length - 1)
                            const Divider(height: 16),
                        ],
                      ),
                    );
                  },
                ),
              ),
              // Footer buttons
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                child: Row(children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () => Navigator.pop(ctx, false),
                      child: const Text('Cancel — Keep Everything'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFE11D48),
                        foregroundColor: Colors.white,
                      ),
                      onPressed: () => Navigator.pop(ctx, true),
                      icon: const Icon(Icons.delete_sweep, size: 18),
                      label: Text('Delete $willDelete Duplicate${willDelete == 1 ? '' : 's'}'),
                    ),
                  ),
                ]),
              ),
            ],
          ),
        ),
      ),
    );
    if (confirm != true) return;

    setState(() => _autoCleanRunning = true);
    try {
      final resp = await http.post(
        Uri.parse('$_apiUrl/api/dedup_sweep/auto_clean'),
        body: {'user_email': widget.userEmail},
      );
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as Map<String, dynamic>;
        final deleted = data['coins_deleted'] as int;
        final cleaned = data['groups_cleaned'] as int;
        if (mounted) {
          nav.pop(); // close dedup dialog
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text(
              '✅ Cleaned $cleaned groups — $deleted duplicate coins removed. '
              'Run Scan Now again to verify.'),
            backgroundColor: const Color(0xFF16A34A),
            duration: const Duration(seconds: 6),
          ));
        }
      } else {
        throw Exception('HTTP ${resp.statusCode}');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Auto-clean failed: $e'),
          backgroundColor: Colors.red,
        ));
      }
    } finally {
      if (mounted) setState(() => _autoCleanRunning = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      insetPadding: const EdgeInsets.symmetric(horizontal: 32, vertical: 40),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 720, maxHeight: 620),
        child: Column(
          children: [
            // Header
            Container(
              padding: const EdgeInsets.fromLTRB(24, 20, 16, 16),
              decoration: const BoxDecoration(
                color: Color(0xFFFFF7ED),
                borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.find_replace_rounded,
                      color: Color(0xFFF97316), size: 24),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          widget.groups.isEmpty
                              ? '✅ No Duplicates Found'
                              : '${widget.groups.length} Duplicate Group${widget.groups.length == 1 ? '' : 's'} Found',
                          style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 18,
                              color: Color(0xFF0F172A)),
                        ),
                        if (widget.groups.isNotEmpty)
                          const Text(
                            'Tap Delete on the copy you want to remove. The first entry is suggested to keep.',
                            style: TextStyle(
                                color: Color(0xFF64748B), fontSize: 13),
                          ),
                        // Auto-clean prompt when cleanable groups exist
                        if (_cleanableGroupCount > 0) ...[
                          const SizedBox(height: 6),
                          Text(
                            '$_cleanableGroupCount group${_cleanableGroupCount == 1 ? '' : 's'} can be auto-cleaned.',
                            style: const TextStyle(
                                color: Color(0xFFEA580C),
                                fontSize: 12,
                                fontWeight: FontWeight.w600),
                          ),
                        ],
                      ],
                    ),
                  ),
                  // Auto-clean button
                  if (_cleanableGroupCount > 0)
                    _autoCleanRunning
                        ? const Padding(
                            padding: EdgeInsets.symmetric(horizontal: 12),
                            child: SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    color: Color(0xFFE11D48))),
                          )
                        : TextButton.icon(
                            onPressed: _autoClean,
                            icon: const Icon(Icons.auto_fix_high,
                                size: 16, color: Color(0xFFE11D48)),
                            label: const Text('Auto-Clean',
                                style: TextStyle(
                                    color: Color(0xFFE11D48),
                                    fontWeight: FontWeight.bold)),
                          ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
            ),
            // Body
            Expanded(
              child: widget.groups.isEmpty
                  ? const Center(
                      child: Padding(
                        padding: EdgeInsets.all(32),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.verified_outlined,
                                size: 56, color: Color(0xFF22C55E)),
                            SizedBox(height: 16),
                            Text('Your collection is clean!',
                                style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                    color: Color(0xFF0F172A))),
                            SizedBox(height: 8),
                            Text('No duplicate coins were detected.',
                                style: TextStyle(color: Color(0xFF64748B))),
                          ],
                        ),
                      ),
                    )
                  : ListView.separated(
                      padding: const EdgeInsets.all(16),
                      itemCount: widget.groups.length,
                      separatorBuilder: (_, i) => const Divider(height: 24),
                      itemBuilder: (_, gi) {
                        final group = widget.groups[gi];
                        final coins = (group['coins'] as List)
                            .cast<Map<String, dynamic>>();
                        return Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Group header
                            Padding(
                              padding: const EdgeInsets.only(bottom: 8),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(children: [
                                    // Match type badge — three tiers
                                    Builder(builder: (context) {
                                      final matchType = group['match_type'] as String? ?? 'attribute';
                                      Color bgColor;
                                      Color textColor;
                                      String label;
                                      switch (matchType) {
                                        case 'invoice':
                                          bgColor   = const Color(0xFFFEE2E2);
                                          textColor = const Color(0xFFDC2626);
                                          label     = '🔴 Invoice Match';
                                        case 'possible':
                                          bgColor   = const Color(0xFFEFF6FF);
                                          textColor = const Color(0xFF1D4ED8);
                                          label     = '🔵 Multiple Copies';
                                        default:
                                          bgColor   = const Color(0xFFFEF3C7);
                                          textColor = const Color(0xFFB45309);
                                          label     = '🟡 ${coins.length} copies';
                                      }
                                      return Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                        decoration: BoxDecoration(
                                          color: bgColor,
                                          borderRadius: BorderRadius.circular(4),
                                        ),
                                        child: Text(label,
                                          style: TextStyle(
                                            color: textColor,
                                            fontWeight: FontWeight.bold,
                                            fontSize: 12,
                                          ),
                                        ),
                                      );
                                    }),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Builder(builder: (context) {
                                        final theme = (coins.first['theme'] as String? ?? '').trim();
                                        final label = theme.isNotEmpty
                                            ? '${coins.first['year']} ${coins.first['denom']} · $theme'
                                            : '${coins.first['year']} ${coins.first['denom']} — ${coins.first['series']}';
                                        return Text(
                                          label,
                                          style: const TextStyle(
                                              fontWeight: FontWeight.w600,
                                              color: Color(0xFF0F172A)),
                                          overflow: TextOverflow.ellipsis,
                                        );
                                      }),
                                    ),
                                  ]),
                                  // Explanatory note for possible duplicates
                                  if ((group['match_type'] as String? ?? '') == 'possible')
                                    const Padding(
                                      padding: EdgeInsets.only(top: 4),
                                      child: Text(
                                         'Same coin type stored in multiple locations — '
                                         'may be intentional. Review manually.',
                                        style: TextStyle(
                                            fontSize: 11,
                                            color: Color(0xFF1D4ED8),
                                            fontStyle: FontStyle.italic),
                                      ),
                                    ),
                                ],
                              ),
                            ),
                            // Each coin in the group
                            ...coins.asMap().entries.map((entry) {
                              final idx = entry.key;
                              final coin = entry.value;
                              final docId = coin['id'] as String;
                              final isDeleting = _deleting.contains(docId);
                              return Container(
                                margin: const EdgeInsets.only(bottom: 6),
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 12, vertical: 10),
                                decoration: BoxDecoration(
                                  color: idx == 0
                                      ? const Color(0xFFF0FDF4)
                                      : const Color(0xFFFFF1F2),
                                  border: Border.all(
                                    color: idx == 0
                                        ? const Color(0xFFBBF7D0)
                                        : const Color(0xFFFFCDD2),
                                  ),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Row(
                                  children: [
                                    Icon(
                                      idx == 0
                                          ? Icons.check_circle_outline
                                          : Icons.content_copy_outlined,
                                      size: 16,
                                      color: idx == 0
                                          ? const Color(0xFF16A34A)
                                          : const Color(0xFFE11D48),
                                    ),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        [
                                          if ((coin['year'] as String).isNotEmpty)
                                            coin['year'],
                                          if ((coin['mint'] as String).isNotEmpty)
                                            coin['mint'],
                                          coin['denom'],
                                          if ((coin['cond'] as String).isNotEmpty)
                                            coin['cond'],
                                          if ((coin['invoice'] as String).isNotEmpty)
                                            'Inv: ${coin['invoice']}',
                                          if ((coin['date'] as String).isNotEmpty)
                                            coin['date'],
                                        ].join(' · '),
                                        style: TextStyle(
                                          fontSize: 13,
                                          color: idx == 0
                                              ? const Color(0xFF15803D)
                                              : const Color(0xFF9F1239),
                                        ),
                                      ),
                                    ),
                                    if (idx == 0)
                                      const Padding(
                                        padding:
                                            EdgeInsets.symmetric(horizontal: 8),
                                        child: Text('Keep',
                                            style: TextStyle(
                                                color: Color(0xFF16A34A),
                                                fontWeight: FontWeight.bold,
                                                fontSize: 12)),
                                      )
                                    else
                                      TextButton.icon(
                                        onPressed: isDeleting
                                            ? null
                                            : () async {
                                                final nav = Navigator.of(context);
                                                setState(() =>
                                                    _deleting.add(docId));
                                                await widget.onDeleted(docId);
                                                if (mounted) nav.pop();
                                              },
                                        icon: isDeleting
                                            ? const SizedBox(
                                                width: 14,
                                                height: 14,
                                                child:
                                                    CircularProgressIndicator(
                                                        strokeWidth: 2))
                                            : const Icon(Icons.delete_outline,
                                                size: 16),
                                        label: const Text('Delete'),
                                        style: TextButton.styleFrom(
                                          foregroundColor:
                                              const Color(0xFFE11D48),
                                        ),
                                      ),
                                  ],
                                ),
                              );
                            }),
                          ],
                        );
                      },
                    ),
            ),
            // Footer
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              child: SizedBox(
                width: double.infinity,
                child: OutlinedButton(
                  onPressed: () => Navigator.of(context).pop(),
                  child: const Text('Close'),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

