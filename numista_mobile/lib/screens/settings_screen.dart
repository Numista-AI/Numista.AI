import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/auth_service.dart';
import '../services/guest_seed_service.dart';
import 'package:flutter/foundation.dart';
import 'dart:convert';

import 'dart:io' as io;

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
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    
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
          
          // Data Export Card
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
          const Divider(color: const Color(0xFFE2E6E9)),
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
      
      if (kIsWeb) {
        // Web download logic via blob URL (requires no manual dart:html import in modern Flutter if handled carefully)
        // or we simply acknowledge this is a pending feature for pure-web.
        if (!context.mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Web export currently requires dart:html - pending cross-platform fix.')));
      } else {
        final String currentDir = io.Directory.current.path;
        final file = io.File('$currentDir/$filename');
        await file.writeAsBytes(bytes);
        if (!context.mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Exported to $currentDir/$filename')));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Export failed: $e'), backgroundColor: Colors.red));
      }
    }
  }
}
