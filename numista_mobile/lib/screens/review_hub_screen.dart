import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:url_launcher/url_launcher.dart';
import '../constants.dart';
import '../widgets/grade_badge_widget.dart';


class ReviewHubScreen extends StatefulWidget {
  const ReviewHubScreen({super.key});

  @override
  State<ReviewHubScreen> createState() => _ReviewHubScreenState();
}

class _ReviewHubScreenState extends State<ReviewHubScreen> {
  final Set<String> _selectedIds = {};
  bool _isProcessing = false;

  // Backend API URL
  final String _apiUrl = kApiBaseUrl;

  // ─── item_type badge config ────────────────────────────────────────────────
  static const Map<String, _ItemTypeMeta> _typeMetaMap = {
    'paper_currency': _ItemTypeMeta(label: '📜 Currency', color: Color(0xFF0D9488)),
    'medal':          _ItemTypeMeta(label: '🎖️ Medal',    color: Color(0xFF7C3AED)),
    'stamp':          _ItemTypeMeta(label: '📬 Stamp',    color: Color(0xFFEA580C)),
    'set':            _ItemTypeMeta(label: '🗂️ Set',      color: Color(0xFF2563EB)),
    'other':          _ItemTypeMeta(label: '❓ Other',    color: Color(0xFF94A3B8)),
    'supply':         _ItemTypeMeta(label: '📦 Supply',   color: Color(0xFF64748B)),
  };

  // ─── Commit selected ──────────────────────────────────────────────────────
  Future<void> _commitSelected() async {
    if (_selectedIds.isEmpty) return;
    setState(() => _isProcessing = true);
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) return;

    try {
      final response = await http.post(
        Uri.parse("$_apiUrl/api/review/commit"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_email": user.email,
          "review_ids": _selectedIds.toList(),
        }),
      );

      if (response.statusCode == 200) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Successfully committed ${_selectedIds.length} items!')),
        );
        setState(() => _selectedIds.clear());
      } else {
        throw Exception("Failed to commit items: ${response.body}");
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Couldn\'t commit items — please check your connection and try again.'),
          backgroundColor: Colors.red[700],
        ),
      );
    } finally {
      setState(() => _isProcessing = false);
    }
  }

  // ─── Commit 100% AI Confidence items ──────────────────────────────────────
  Future<void> _commitHighConfidence(List<QueryDocumentSnapshot<Map<String, dynamic>>> docs) async {
    final highConfIds = docs
        .where((d) {
          final data = d.data();
          double conf = 1.0;
          try {
            final raw = data['confidence_score'];
            if (raw != null) conf = (raw as num).toDouble();
          } catch (_) {}
          return conf >= 0.999;
        })
        .map((d) => d.id)
        .toList();

    if (highConfIds.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No items with 100% AI Confidence found in queue.')),
      );
      return;
    }

    setState(() => _isProcessing = true);
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) return;

    try {
      final response = await http.post(
        Uri.parse("$_apiUrl/api/review/commit"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_email": user.email,
          "review_ids": highConfIds,
        }),
      );

      if (response.statusCode == 200) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✅ Successfully committed ${highConfIds.length} items with 100% AI Confidence!'),
            backgroundColor: const Color(0xFF10B981),
          ),
        );
        setState(() => _selectedIds.removeWhere((id) => highConfIds.contains(id)));
      } else {
        throw Exception("Failed to commit items: ${response.body}");
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error committing items: $e'),
          backgroundColor: Colors.red[700],
        ),
      );
    } finally {
      if (mounted) setState(() => _isProcessing = false);
    }
  }

  // ─── View Paper Trail Dialog ─────────────────────────────────────────────
  Future<void> _showPaperTrailDialog() async {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) return;

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1A1D27),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: const [
            Icon(Icons.receipt_long_outlined, color: Color(0xFFFFD700), size: 22),
            SizedBox(width: 10),
            Text('Paper Trail — Ingested Documents', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
        content: SizedBox(
          width: 600,
          child: FutureBuilder<http.Response>(
            future: http.get(Uri.parse("$_apiUrl/api/receipts/${Uri.encodeComponent(user.email!)}")),
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: Padding(padding: EdgeInsets.all(32), child: CircularProgressIndicator(color: Color(0xFFFFD700))));
              }
              List<dynamic> receipts = [];
              if (snapshot.hasData && snapshot.data!.statusCode == 200) {
                try {
                  final body = jsonDecode(snapshot.data!.body);
                  receipts = body['receipts'] ?? [];
                } catch (_) {}
              }

              if (receipts.isEmpty) {
                return Padding(
                  padding: const EdgeInsets.symmetric(vertical: 24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: const [
                      Icon(Icons.inventory_2_outlined, color: Colors.white38, size: 40),
                      SizedBox(height: 12),
                      Text('No uploaded scans or receipts found for this session.', style: TextStyle(color: Colors.white70)),
                    ],
                  ),
                );
              }

              return ListView.separated(
                shrinkWrap: true,
                itemCount: receipts.length,
                separatorBuilder: (context, index) => const Divider(color: Colors.white10),
                itemBuilder: (context, idx) {
                  final r = receipts[idx] as Map<String, dynamic>;
                  final name = r['original_filename'] ?? r['receipt_id'] ?? 'Document ${idx + 1}';
                  final date = r['invoice_date'] ?? 'Recent';
                  final linked = (r['linked_coin_ids'] as List?)?.length ?? 0;
                  return ListTile(
                    contentPadding: EdgeInsets.zero,
                    leading: const Icon(Icons.picture_as_pdf, color: Color(0xFF60A5FA), size: 28),
                    title: Text(name, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14)),
                    subtitle: Text('Ingested: $date • Linked: $linked coins', style: const TextStyle(color: Colors.white54, fontSize: 12)),
                    trailing: TextButton.icon(
                      onPressed: () async {
                        final messenger = ScaffoldMessenger.of(context);
                        try {
                          final res = await http.get(Uri.parse("$_apiUrl/api/receipts/${Uri.encodeComponent(user.email!)}/${r['receipt_id']}/view_url"));
                          if (res.statusCode == 200) {
                            final data = jsonDecode(res.body);
                            final url = data['signed_url'] ?? data['url'];
                            if (url != null) {
                              launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
                            }
                          }
                        } catch (e) {
                          messenger.showSnackBar(SnackBar(content: Text('Error opening file: $e')));
                        }
                      },
                      icon: const Icon(Icons.open_in_new, size: 14, color: Color(0xFFFFD700)),
                      label: const Text('View Scan', style: TextStyle(color: Color(0xFFFFD700), fontSize: 12)),
                    ),
                  );
                },
              );
            },
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Close', style: TextStyle(color: Colors.white70)),
          ),
        ],
      ),
    );
  }

  // ─── Bulk update ──────────────────────────────────────────────────────────
  Future<void> _bulkUpdateItems(Map<String, dynamic> updates) async {
    if (_selectedIds.isEmpty) return;
    setState(() => _isProcessing = true);
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) return;

    try {
      final response = await http.post(
        Uri.parse("$_apiUrl/api/review/bulk_update"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({
          "user_email": user.email,
          "review_ids": _selectedIds.toList(),
          "updates": updates,
        }),
      );

      if (response.statusCode == 200) {
        if (!mounted) return;
        setState(() => _selectedIds.clear());
        Navigator.pop(context);
      } else {
        throw Exception("Bulk update failed: ${response.body}");
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('Update failed — please check your connection and try again.'),
          backgroundColor: Colors.red[700],
        ),
      );
    } finally {
      setState(() => _isProcessing = false);
    }
  }

  // ─── Keep Set as-is ───────────────────────────────────────────────────────
  Future<void> _keepSetAsIs(String docId, String setName) async {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) return;

    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1A1D27),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Keep as Set?', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        content: Text(
          'Commit "$setName" to your collection as a single set item.\n\nYou can still view its contents later.',
          style: const TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel', style: TextStyle(color: Colors.white54)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF2563EB),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Keep as Set'),
          ),
        ],
      ),
    );

    if (confirm != true) return;
    if (!mounted) return;

    setState(() => _isProcessing = true);
    try {
      final resp = await http.post(
        Uri.parse("$_apiUrl/api/review/keep_set_as_is"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"user_email": user.email, "set_doc_id": docId}),
      );
      if (!mounted) return;
      if (resp.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('🗂️ Set committed to your collection!')),
        );
      } else {
        throw Exception(resp.body);
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red[700]),
      );
    } finally {
      if (mounted) setState(() => _isProcessing = false);
    }
  }

  // ─── Break Up Set ─────────────────────────────────────────────────────────
  Future<void> _breakUpSet(String docId, String setName, int setSize) async {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) return;

    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1A1D27),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Break Up Set?', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        content: Text(
          'This will expand "$setName" into $setSize individual coin records in the Review Hub.\n\nYou can then review and commit each coin separately.',
          style: const TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel', style: TextStyle(color: Colors.white54)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFF63366),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Break Up Set'),
          ),
        ],
      ),
    );

    if (confirm != true) return;
    if (!mounted) return;

    setState(() => _isProcessing = true);
    try {
      final resp = await http.post(
        Uri.parse("$_apiUrl/api/review/break_up_set"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"user_email": user.email, "set_doc_id": docId}),
      );
      if (!mounted) return;
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body);
        final created = data['created'] ?? setSize;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('✅ Set expanded into $created individual coin records!')),
        );
      } else {
        throw Exception(resp.body);
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red[700]),
      );
    } finally {
      if (mounted) setState(() => _isProcessing = false);
    }
  }

  // ─── Per-card edit dialog ─────────────────────────────────────────────────
  void _showCoinEditDialog(String docId, Map<String, dynamic> data) {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) return;

    // Pre-populate all controllers
    final controllers = <String, TextEditingController>{
      'Year':                    TextEditingController(text: data['Year']?.toString() ?? ''),
      'Denomination':            TextEditingController(text: data['Denomination']?.toString() ?? ''),
      'Mint Mark':               TextEditingController(text: data['Mint Mark']?.toString() ?? ''),
      'Country':                 TextEditingController(text: data['Country']?.toString() ?? 'USA'),
      'Program/Series':          TextEditingController(text: data['Program/Series']?.toString() ?? ''),
      'Theme/Subject':           TextEditingController(text: data['Theme/Subject']?.toString() ?? ''),
      'Variety':                 TextEditingController(text: data['Variety']?.toString() ?? ''),
      'Condition':               TextEditingController(text: data['Condition']?.toString() ?? ''),
      'Strike Type':             TextEditingController(text: data['Strike Type']?.toString() ?? ''),
      'Metal Content':           TextEditingController(text: data['Metal Content']?.toString() ?? ''),
      'Purchase Cost':           TextEditingController(text: (data['Purchase Cost'] ?? data['Cost'] ?? '').toString()),
      'Purchase Date':           TextEditingController(text: data['Purchase Date']?.toString() ?? ''),
      'Retailer/Website':        TextEditingController(text: data['Retailer/Website']?.toString() ?? ''),
      'Retailer Invoice #':      TextEditingController(text: data['Retailer Invoice #']?.toString() ?? ''),
      'Retailer Item No.':       TextEditingController(text: data['Retailer Item No.']?.toString() ?? ''),
      'Storage Location':        TextEditingController(text: data['Storage Location']?.toString() ?? ''),
    };

    bool isSaving = false;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (dialogContext) => StatefulBuilder(
        builder: (dialogContext, setDialogState) {
          Widget field(String key, String label, IconData icon,
              {TextInputType keyboardType = TextInputType.text,
              TextCapitalization capitalization = TextCapitalization.none}) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 14),
              child: TextField(
                controller: controllers[key],
                style: const TextStyle(color: Colors.white, fontSize: 14),
                keyboardType: keyboardType,
                textCapitalization: capitalization,
                decoration: InputDecoration(
                  prefixIcon: Icon(icon, color: Colors.white38, size: 18),
                  labelText: label,
                  labelStyle: const TextStyle(color: Colors.white38, fontSize: 13),
                  enabledBorder: OutlineInputBorder(
                    borderSide: const BorderSide(color: Colors.white12),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderSide: const BorderSide(color: Color(0xFFF63366)),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  filled: true,
                  fillColor: Colors.white.withAlpha(8),
                  contentPadding: const EdgeInsets.symmetric(vertical: 12, horizontal: 12),
                ),
              ),
            );
          }

          Widget sectionHeader(String title) => Padding(
            padding: const EdgeInsets.only(top: 8, bottom: 10),
            child: Text(
              title,
              style: const TextStyle(
                color: Color(0xFFF63366),
                fontSize: 11,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.4,
              ),
            ),
          );

          return Dialog(
            backgroundColor: const Color(0xFF1A1D27),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
            child: ConstrainedBox(
              constraints: BoxConstraints(
                maxWidth: 640,
                maxHeight: MediaQuery.of(dialogContext).size.height * 0.88,
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // ── Header ────────────────────────────────────────────
                  Container(
                    padding: const EdgeInsets.fromLTRB(24, 20, 12, 16),
                    decoration: const BoxDecoration(
                      border: Border(bottom: BorderSide(color: Colors.white10)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.edit_note, color: Color(0xFFF63366), size: 22),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Edit Coin',
                                style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                              ),
                              Text(
                                '${data['Year'] ?? ''} ${data['Denomination'] ?? 'Review Item'}',
                                style: const TextStyle(color: Colors.white54, fontSize: 13),
                              ),
                            ],
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.close, color: Colors.white38),
                          onPressed: () => Navigator.pop(dialogContext),
                        ),
                      ],
                    ),
                  ),

                  // ── Scrollable form body ───────────────────────────────
                  Flexible(
                    child: SingleChildScrollView(
                      padding: const EdgeInsets.fromLTRB(24, 16, 24, 0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          sectionHeader('IDENTITY'),
                          Row(children: [
                            Expanded(child: field('Year', 'Year', Icons.calendar_today,
                                keyboardType: TextInputType.number)),
                            const SizedBox(width: 12),
                            Expanded(child: field('Mint Mark', 'Mint Mark', Icons.location_pin,
                                capitalization: TextCapitalization.characters)),
                          ]),
                          field('Denomination', 'Denomination', Icons.monetization_on_outlined),
                          field('Country', 'Country', Icons.flag_outlined),
                          field('Program/Series', 'Program / Series', Icons.collections_bookmark_outlined),
                          field('Theme/Subject', 'Theme / Subject', Icons.image_outlined),
                          field('Variety', 'Variety / Error', Icons.warning_amber_outlined),

                          sectionHeader('CONDITION'),
                          Row(children: [
                            Expanded(child: field('Condition', 'Grade / Condition', Icons.grade_outlined)),
                            const SizedBox(width: 12),
                            Expanded(child: field('Strike Type', 'Strike Type', Icons.auto_fix_high_outlined)),
                          ]),
                          field('Metal Content', 'Metal Content', Icons.diamond_outlined),

                          sectionHeader('PURCHASE'),
                          Row(children: [
                            Expanded(child: field('Purchase Cost', 'Purchase Cost', Icons.attach_money,
                                keyboardType: TextInputType.number)),
                            const SizedBox(width: 12),
                            Expanded(child: field('Purchase Date', 'Purchase Date', Icons.calendar_month_outlined)),
                          ]),
                          field('Retailer/Website', 'Retailer / Website', Icons.storefront_outlined),
                          Row(children: [
                            Expanded(child: field('Retailer Invoice #', 'Invoice #', Icons.receipt_outlined)),
                            const SizedBox(width: 12),
                            Expanded(child: field('Retailer Item No.', 'Item #', Icons.tag)),
                          ]),
                          field('Storage Location', 'Storage Location', Icons.inventory_2_outlined),
                          const SizedBox(height: 8),
                        ],
                      ),
                    ),
                  ),

                  // ── Footer buttons ─────────────────────────────────────
                  Container(
                    padding: const EdgeInsets.fromLTRB(24, 16, 24, 20),
                    decoration: const BoxDecoration(
                      border: Border(top: BorderSide(color: Colors.white10)),
                    ),
                    child: Row(
                      children: [
                        // Save only
                        Expanded(
                          child: OutlinedButton(
                            style: OutlinedButton.styleFrom(
                              foregroundColor: Colors.white,
                              side: const BorderSide(color: Colors.white24),
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                            onPressed: isSaving ? null : () async {
                              setDialogState(() => isSaving = true);
                              final messenger = ScaffoldMessenger.of(context);
                              final dialogMessenger = ScaffoldMessenger.of(dialogContext);
                              final nav = Navigator.of(dialogContext);
                              try {
                                final updates = <String, dynamic>{};
                                controllers.forEach((key, ctrl) {
                                  if (ctrl.text.isNotEmpty) updates[key] = ctrl.text;
                                });
                                // Auto-split combined Year+Mint (e.g. "2006D" → Year="2006" Mint="D")
                                final ymRe = RegExp(r'^(\d{4}(?:-\d{4})?)\s*([A-WY-Z])$', caseSensitive: false);
                                final ry = (updates['Year'] as String? ?? '').trim();
                                final rm = (updates['Mint Mark'] as String? ?? '').trim();
                                if (ry.isNotEmpty && rm.isEmpty) {
                                  final ym = ymRe.firstMatch(ry);
                                  if (ym != null) {
                                    updates['Year'] = ym.group(1)!;
                                    updates['Mint Mark'] = ym.group(2)!.toUpperCase();
                                    controllers['Year']?.text = ym.group(1)!;
                                    controllers['Mint Mark']?.text = ym.group(2)!.toUpperCase();
                                  }
                                }
                                await FirebaseFirestore.instance
                                    .collection('users')
                                    .doc(user.email!)
                                    .collection('review_queue')
                                    .doc(docId)
                                    .update(updates);
                                if (!mounted) return;
                                nav.pop();
                                messenger.showSnackBar(
                                  const SnackBar(content: Text('Changes saved to Review Queue.')),
                                );
                              } catch (e) {
                                setDialogState(() => isSaving = false);
                                dialogMessenger.showSnackBar(
                                  SnackBar(content: Text('Save failed: $e'), backgroundColor: Colors.red[700]),
                                );
                              }
                            },
                            child: const Text('Save'),
                          ),
                        ),
                        const SizedBox(width: 12),
                        // Save + Commit
                        Expanded(
                          flex: 2,
                          child: ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFFF63366),
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                            onPressed: isSaving ? null : () async {
                              setDialogState(() => isSaving = true);
                              final messenger = ScaffoldMessenger.of(context);
                              final dialogMessenger = ScaffoldMessenger.of(dialogContext);
                              final nav = Navigator.of(dialogContext);
                              try {
                                final updates = <String, dynamic>{};
                                controllers.forEach((key, ctrl) {
                                  if (ctrl.text.isNotEmpty) updates[key] = ctrl.text;
                                });
                                // Auto-split combined Year+Mint (e.g. "2006D" → Year="2006" Mint="D")
                                final ymRe2 = RegExp(r'^(\d{4}(?:-\d{4})?)\s*([A-WY-Z])$', caseSensitive: false);
                                final ry2 = (updates['Year'] as String? ?? '').trim();
                                final rm2 = (updates['Mint Mark'] as String? ?? '').trim();
                                if (ry2.isNotEmpty && rm2.isEmpty) {
                                  final ym2 = ymRe2.firstMatch(ry2);
                                  if (ym2 != null) {
                                    updates['Year'] = ym2.group(1)!;
                                    updates['Mint Mark'] = ym2.group(2)!.toUpperCase();
                                    controllers['Year']?.text = ym2.group(1)!;
                                    controllers['Mint Mark']?.text = ym2.group(2)!.toUpperCase();
                                  }
                                }
                                // Save edits first
                                await FirebaseFirestore.instance
                                    .collection('users')
                                    .doc(user.email!)
                                    .collection('review_queue')
                                    .doc(docId)
                                    .update(updates);

                                // Then commit to main collection
                                final response = await http.post(
                                  Uri.parse("$_apiUrl/api/review/commit"),
                                  headers: {"Content-Type": "application/json"},
                                  body: jsonEncode({
                                    "user_email": user.email,
                                    "review_ids": [docId],
                                  }),
                                );
                                if (!mounted) return;
                                nav.pop();
                                if (response.statusCode == 200) {
                                  messenger.showSnackBar(
                                    const SnackBar(content: Text('Coin saved and committed to collection!')),
                                  );
                                } else {
                                  messenger.showSnackBar(
                                    const SnackBar(content: Text('Saved, but commit failed — try committing from the hub.')),
                                  );
                                }
                              } catch (e) {
                                setDialogState(() => isSaving = false);
                                dialogMessenger.showSnackBar(
                                  SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red[700]),
                                );
                              }
                            },
                            icon: isSaving
                                ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                                : const Icon(Icons.check_circle_outline, size: 18),
                            label: const Text('Save & Commit', style: TextStyle(fontWeight: FontWeight.bold)),
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
    ).then((_) {
      // Dispose controllers when dialog closes
      for (final c in controllers.values) {
        c.dispose();
      }
    });
  }

  // ─── Bulk edit bottom sheet ───────────────────────────────────────────────
  void _showBulkEditDialog() {
    final TextEditingController locationController = TextEditingController();
    final TextEditingController costController = TextEditingController();
    final TextEditingController dateController = TextEditingController();

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF1A1D27),
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (context) => Padding(
        padding: EdgeInsets.only(bottom: MediaQuery.of(context).viewInsets.bottom, left: 24, right: 24, top: 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Bulk Edit Metadata', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text('Applying to ${_selectedIds.length} selected items.', style: const TextStyle(color: Colors.white54)),
            const SizedBox(height: 24),
            _buildDialogField('Storage Location', locationController, Icons.inventory_2_outlined),
            _buildDialogField('Cost per Item', costController, Icons.attach_money),
            _buildDialogField('Purchase Date', dateController, Icons.calendar_today),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFF63366),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                onPressed: () {
                  final updates = <String, dynamic>{};
                  if (locationController.text.isNotEmpty) updates['Storage Location'] = locationController.text;
                  if (costController.text.isNotEmpty) updates['Cost'] = costController.text;
                  if (dateController.text.isNotEmpty) updates['Purchase Date'] = dateController.text;
                  if (updates.isNotEmpty) _bulkUpdateItems(updates);
                },
                child: const Text('Apply Changes', style: TextStyle(fontWeight: FontWeight.bold)),
              ),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  Widget _buildDialogField(String label, TextEditingController controller, IconData icon) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: TextField(
        controller: controller,
        style: const TextStyle(color: Colors.white),
        decoration: InputDecoration(
          prefixIcon: Icon(icon, color: Colors.white38, size: 20),
          labelText: label,
          labelStyle: const TextStyle(color: Colors.white38),
          enabledBorder: OutlineInputBorder(borderSide: const BorderSide(color: Colors.white10), borderRadius: BorderRadius.circular(12)),
          focusedBorder: OutlineInputBorder(borderSide: const BorderSide(color: Color(0xFFF63366)), borderRadius: BorderRadius.circular(12)),
          filled: true,
          fillColor: Colors.white.withAlpha(10),
        ),
      ),
    );
  }

  // ─── Build ────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) return const Center(child: Text("Please sign in."));

    return Scaffold(
      backgroundColor: const Color(0xFFF0F2F6),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: Row(
          children: [
            const Text('Review Hub', style: TextStyle(color: Color(0xFF31333F), fontWeight: FontWeight.w900, fontStyle: FontStyle.italic)),
            const Spacer(),
            StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
                stream: FirebaseFirestore.instance
                    .collection('users')
                    .doc(user.email!)
                    .collection('review_queue')
                    .snapshots(),
                builder: (context, snapshot) {
                  final rawDocs = snapshot.data?.docs ?? [];
                  final docs = rawDocs.where((d) {
                    final status = (d.data()['status'] ?? 'staged').toString().toLowerCase();
                    return status != 'aborted' && status != 'superseded' && status != 'committed';
                  }).toList();
                  if (docs.isEmpty) return const SizedBox.shrink();

                  final allSelected = _selectedIds.length == docs.length && docs.isNotEmpty;
                  return Row(
                    children: [
                      const Text('Select All', style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                      Checkbox(
                        value: allSelected,
                        activeColor: const Color(0xFFF63366),
                        onChanged: (val) {
                          setState(() {
                            if (val == true) {
                              _selectedIds.addAll(docs.map((d) => d.id));
                            } else {
                              _selectedIds.clear();
                            }
                          });
                        },
                      ),
                    ],
                  );
                },
              ),
          ],
        ),
        actions: [
          IconButton(
            tooltip: 'View Paper Trail (Scans & Invoices)',
            icon: const Icon(Icons.receipt_long_outlined, color: Color(0xFF475569)),
            onPressed: _showPaperTrailDialog,
          ),
          StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
            stream: FirebaseFirestore.instance
                .collection('users')
                .doc(user.email!)
                .collection('review_queue')
                .snapshots(),
            builder: (context, snapshot) {
              final rawDocs = snapshot.data?.docs ?? [];
              final docs = rawDocs.where((d) {
                final status = (d.data()['status'] ?? 'staged').toString().toLowerCase();
                return status != 'aborted' && status != 'superseded' && status != 'committed';
              }).toList();
              final highConfCount = docs.where((d) {
                final data = d.data();
                double conf = 1.0;
                try {
                  final raw = data['confidence_score'];
                  if (raw != null) conf = (raw as num).toDouble();
                } catch (_) {}
                return conf >= 0.999;
              }).length;

              if (highConfCount == 0) return const SizedBox.shrink();

              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 8),
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF0F172A),
                    foregroundColor: const Color(0xFFFFD700),
                    side: const BorderSide(color: Color(0xFFC9A227)),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                  ),
                  icon: const Icon(Icons.auto_awesome, size: 16, color: Color(0xFFFFD700)),
                  label: Text('Add All with 100% AI Confidence ($highConfCount)', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  onPressed: () => _commitHighConfidence(docs),
                ),
              );
            },
          ),
          if (_selectedIds.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(right: 16, left: 8),
              child: Center(
                child: Text('${_selectedIds.length} Selected', style: const TextStyle(color: Color(0xFFF63366), fontWeight: FontWeight.bold)),
              ),
            ),
        ],
      ),
      body: Stack(
        children: [
          StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
            stream: FirebaseFirestore.instance
                .collection('users')
                .doc(user.email!)
                .collection('review_queue')
                .snapshots(),
            builder: (context, snapshot) {
              if (snapshot.hasError) {
                return Center(
                  child: Column(mainAxisSize: MainAxisSize.min, children: const [
                    Icon(Icons.cloud_off_rounded, size: 40, color: Colors.red),
                    SizedBox(height: 12),
                    Text('Couldn\'t load review queue.',
                        style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16, color: Color(0xFF1E293B))),
                    SizedBox(height: 4),
                    Text('Check your connection and try again.',
                        style: TextStyle(color: Color(0xFF64748B))),
                  ]),
                );
              }
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator(color: Color(0xFFD4A843)));
              }

              final rawDocs = (snapshot.data?.docs.toList() ?? []);
              final docs = rawDocs.where((d) {
                final status = (d.data()['status'] ?? 'staged').toString().toLowerCase();
                return status != 'aborted' && status != 'superseded';
              }).toList();
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
                            color: const Color(0xFF22C55E).withAlpha(20),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(Icons.check_circle_outline_rounded,
                              size: 48, color: Color(0xFF22C55E)),
                        ),
                        const SizedBox(height: 20),
                        const Text('All Caught Up!',
                            style: TextStyle(
                                fontSize: 22,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF1E293B))),
                        const SizedBox(height: 8),
                        const Text(
                          'No items waiting for review.\nScan an invoice or photograph a coin to add coins here.',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                              color: Color(0xFF64748B),
                              height: 1.5,
                              fontSize: 14),
                        ),
                      ],
                    ),
                  ),
                );
              }

              return ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: docs.length + 1,
                itemBuilder: (context, index) {
                  if (index == 0) {
                    return _buildMorganGuideBanner();
                  }
                  try {
                    final doc = docs[index - 1];
                    final data = doc.data();
                    final id = doc.id;
                    final isSelected = _selectedIds.contains(id);
                    final itemType = (data['item_type'] ?? 'coin').toString().toLowerCase();
                    final isSet = itemType == 'set';

                    // Safe confidence parsing
                    double confidence = 1.0;
                    try {
                      final raw = data['confidence_score'];
                      if (raw != null) confidence = (raw as num).toDouble();
                    } catch (_) {}

                    if (isSet) {
                      return _buildSetCard(id, data, isSelected);
                    }

                    return _buildCoinCard(id, data, isSelected, confidence, itemType);
                  } catch (e) {
                    return Card(
                      color: Colors.red.shade50,
                      margin: const EdgeInsets.only(bottom: 12),
                      child: ListTile(
                        leading: const Icon(Icons.error_outline, color: Colors.red),
                        title: const Text('Item Rendering Warning', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.red)),
                        subtitle: Text(e.toString(), style: const TextStyle(fontSize: 12)),
                      ),
                    );
                  }
                },
              );
            },
          ),

          // ── Floating action bar (shown when items are selected) ───────────
          if (_selectedIds.isNotEmpty)
            Positioned(
              bottom: 24,
              left: 24,
              right: 24,
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E1E1E),
                  borderRadius: BorderRadius.circular(100),
                  boxShadow: [BoxShadow(color: Colors.black.withAlpha(40), blurRadius: 10, offset: const Offset(0, 4))],
                ),
                child: Row(
                  children: [
                    IconButton(
                      icon: const Icon(Icons.edit_outlined, color: Colors.white),
                      onPressed: _showBulkEditDialog,
                      tooltip: 'Bulk Edit',
                    ),
                    IconButton(
                      icon: const Icon(Icons.delete_outline, color: Colors.white54),
                      onPressed: () {
                        final user = FirebaseAuth.instance.currentUser;
                        if (user == null) return;
                        for (var sid in _selectedIds) {
                          FirebaseFirestore.instance
                              .collection('users')
                              .doc(user.email!)
                              .collection('review_queue')
                              .doc(sid)
                              .delete();
                        }
                        setState(() => _selectedIds.clear());
                      },
                      tooltip: 'Discard',
                    ),
                    const Spacer(),
                    ElevatedButton.icon(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFF63366),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(100)),
                      ),
                      onPressed: _isProcessing ? null : _commitSelected,
                      icon: _isProcessing
                        ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                        : const Icon(Icons.check_circle_outline),
                      label: Text(_isProcessing ? 'Processing...' : 'Commit Selected'),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }

  // ─── Set Card ─────────────────────────────────────────────────────────────
  Widget _buildSetCard(String id, Map<String, dynamic> data, bool isSelected) {
    final setName = data['Original Description from source']
        ?? data['Theme/Subject']
        ?? data['Denomination']
        ?? 'Coin Set';
    final setSize    = (data['set_size'] as num?)?.toInt() ?? 0;
    final costLabel  = data['set_cost_label'] ?? data['Purchase Cost'] ?? 'N/A';
    final retailer   = data['Retailer/Website'] ?? 'Unknown';
    final srcFile    = data['source_file']?.toString() ?? '';

    // Expand set_contents for the preview list
    final rawContents = data['set_contents'];
    final List<dynamic> contents = (rawContents is List) ? rawContents : [];

    return Card(
      margin: const EdgeInsets.only(bottom: 14),
      elevation: isSelected ? 4 : 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: isSelected ? const Color(0xFFF63366) : const Color(0xFF2563EB).withAlpha(120),
          width: isSelected ? 2 : 1.5,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Title row ──────────────────────────────────────────────
            Row(
              children: [
                Checkbox(
                  value: isSelected,
                  activeColor: const Color(0xFFF63366),
                  onChanged: (val) {
                    setState(() {
                      if (val == true) { _selectedIds.add(id); }
                      else { _selectedIds.remove(id); }
                    });
                  },
                ),
                const SizedBox(width: 4),
                _buildBadge('🗂️ SET', const Color(0xFF2563EB)),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    setName.toString(),
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: Color(0xFF1E293B),
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 4),
            Padding(
              padding: const EdgeInsets.only(left: 48),
              child: Text(
                '$costLabel  •  $retailer',
                style: const TextStyle(color: Color(0xFF64748B), fontSize: 13),
              ),
            ),

            // ── Contents preview ───────────────────────────────────────
            if (contents.isNotEmpty) ...[
              const SizedBox(height: 10),
              Container(
                margin: const EdgeInsets.only(left: 16),
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: const Color(0xFF2563EB).withAlpha(12),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFF2563EB).withAlpha(40)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Contains $setSize coins:',
                      style: const TextStyle(
                        fontSize: 11,
                        color: Color(0xFF2563EB),
                        fontWeight: FontWeight.bold,
                        letterSpacing: 0.6,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Wrap(
                      spacing: 6,
                      runSpacing: 4,
                      children: contents.take(12).map((c) {
                        final coin = c as Map<String, dynamic>? ?? {};
                        final yr = coin['Year']?.toString() ?? '';
                        final mm = coin['Mint Mark']?.toString() ?? '';
                        final dn = coin['Denomination']?.toString() ?? '';
                        final label = [yr + (mm.isNotEmpty ? '-$mm' : ''), dn]
                            .where((s) => s.isNotEmpty).join(' ');
                        return Container(
                          padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(4),
                            border: Border.all(color: const Color(0xFFCBD5E1)),
                          ),
                          child: Text(label, style: const TextStyle(fontSize: 11, color: Color(0xFF475569))),
                        );
                      }).toList()
                        ..addAll(contents.length > 12 ? [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                            decoration: BoxDecoration(
                              color: const Color(0xFF2563EB).withAlpha(20),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text('+${contents.length - 12} more',
                              style: const TextStyle(fontSize: 11, color: Color(0xFF2563EB), fontWeight: FontWeight.bold)),
                          )
                        ] : []),
                    ),
                  ],
                ),
              ),
            ],

            // ── Source file ────────────────────────────────────────────
            if (srcFile.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 8, left: 16),
                child: Row(children: [
                  const Icon(Icons.insert_drive_file_outlined, size: 11, color: Color(0xFFF63366)),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(srcFile,
                      style: const TextStyle(color: Color(0xFFF63366), fontSize: 11, fontWeight: FontWeight.w500),
                      overflow: TextOverflow.ellipsis),
                  ),
                ]),
              ),

            const Divider(height: 20),

            // ── Action buttons ─────────────────────────────────────────
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(
                      foregroundColor: const Color(0xFF2563EB),
                      side: const BorderSide(color: Color(0xFF2563EB)),
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    onPressed: _isProcessing ? null : () {
                      final name = data['Original Description from source']
                          ?? data['Theme/Subject']
                          ?? data['Denomination']
                          ?? 'This Set';
                      _keepSetAsIs(id, name.toString());
                    },
                    icon: const Icon(Icons.collections_bookmark_outlined, size: 16),
                    label: const Text('Keep as Set', style: TextStyle(fontWeight: FontWeight.w600)),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFF63366),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    onPressed: _isProcessing ? null : () {
                      final name = data['Original Description from source']
                          ?? data['Theme/Subject']
                          ?? data['Denomination']
                          ?? 'This Set';
                      _breakUpSet(id, name.toString(), setSize);
                    },
                    icon: const Icon(Icons.call_split_rounded, size: 16),
                    label: const Text('Break Up Set →', style: TextStyle(fontWeight: FontWeight.w600)),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMorganGuideBanner() {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFC9A227).withAlpha(140)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: const Color(0xFFC9A227).withAlpha(30),
              shape: BoxShape.circle,
            ),
            child: ClipOval(
              child: Image.asset(
                'assets/logo_owl.png',
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) => const Icon(Icons.psychology_outlined, color: Color(0xFFFFD700), size: 24),
              ),
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: const [
                Text(
                  'Morgan Ingestion Assistant',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Color(0xFFFFD700),
                    fontSize: 14,
                    letterSpacing: 0.5,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  'Hoo! I\'ve scanned your checklist or invoice. Verify the extracted subjects below, set your collection condition, and commit them directly to your vault!',
                  style: TextStyle(
                    color: Color(0xFFCBD5E1),
                    fontSize: 13,
                    height: 1.45,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ─── Coin Card (standard + paper_currency / medal / stamp / other) ────────
  Widget _buildCoinCard(String id, Map<String, dynamic> data, bool isSelected, double confidence, String itemType) {
    final isFromSet = data['from_set'] == true;
    final typeMeta  = _typeMetaMap[itemType];
    final condStr = (data['Condition'] ?? '').toString().trim();
    final hasCondition = condStr.isNotEmpty && condStr != 'Unspecified / Raw';
    final storageLoc = (data['Storage Location'] ?? data['storage_location'] ?? '').toString().trim();

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: isSelected ? 4 : 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(
          color: isSelected ? const Color(0xFFF63366) : const Color(0xFFE2E6E9),
          width: isSelected ? 2 : 1,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Checkbox(
              value: isSelected,
              activeColor: const Color(0xFFF63366),
              onChanged: (val) {
                setState(() {
                  if (val == true) {
                    _selectedIds.add(id);
                  } else {
                    _selectedIds.remove(id);
                  }
                });
              },
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        '${data['Year'] ?? 'Unknown'} ${data['Denomination'] ?? 'Item'}${data['Mint Mark'] != null && data['Mint Mark'].toString().isNotEmpty ? ' (${data['Mint Mark']})' : ''}',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: Color(0xFFC9A227)),
                      ),
                      const SizedBox(width: 8),
                      if (hasCondition)
                        GradeBadgeWidget(gradeCode: condStr)
                      else
                        InkWell(
                          onTap: () => _showCoinEditDialog(id, data),
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: Colors.orange.withAlpha(25),
                              borderRadius: BorderRadius.circular(6),
                              border: Border.all(color: Colors.orange.withAlpha(160)),
                            ),
                            child: const Text('Set Condition', style: TextStyle(color: Colors.orange, fontSize: 11, fontWeight: FontWeight.bold)),
                          ),
                        ),
                      if (storageLoc.isNotEmpty)
                        Padding(
                          padding: const EdgeInsets.only(left: 6),
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: const Color(0xFF3B82F6).withAlpha(20),
                              borderRadius: BorderRadius.circular(6),
                              border: Border.all(color: const Color(0xFF3B82F6).withAlpha(120)),
                            ),
                            child: Text('📍 $storageLoc', style: const TextStyle(color: Color(0xFF2563EB), fontSize: 11, fontWeight: FontWeight.w600)),
                          ),
                        ),
                      const Spacer(),
                      // item_type badge (only shown for non-coin types)
                      if (typeMeta != null) ...[
                        _buildBadge(typeMeta.label, typeMeta.color),
                        const SizedBox(width: 6),
                      ],
                      _buildBadge(
                        'Conf: ${(confidence * 100).toInt()}%',
                        confidence < 0.85 ? Colors.orange : Colors.green),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    data['Theme/Subject'] ?? data['theme_subject'] ?? data['title'] ?? 'Numismatic Item',
                    style: const TextStyle(color: Color(0xFF475569), fontSize: 14, fontWeight: FontWeight.w500),
                  ),

                  // "From Set" amber chip
                  if (isFromSet) ...[
                    const SizedBox(height: 6),
                    Row(children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: Colors.amber.withAlpha(30),
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(color: Colors.amber.withAlpha(120)),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const Icon(Icons.collections_bookmark_outlined, size: 12, color: Colors.amber),
                            const SizedBox(width: 4),
                            Text(
                              'From Set: ${data['set_name'] ?? 'Unknown Set'}',
                              style: const TextStyle(color: Colors.amber, fontSize: 11, fontWeight: FontWeight.w600),
                            ),
                          ],
                        ),
                      ),
                    ]),
                    if ((data['set_cost_label'] ?? '').isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(top: 3),
                        child: Text(
                          'Cost: ${data['set_cost_label']}',
                          style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                        ),
                      ),
                  ],

                  if ((data['Variety'] ?? '').isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(color: const Color(0xFFF63366).withAlpha(10), borderRadius: BorderRadius.circular(4)),
                        child: Text(
                          'Variety: ${data['Variety']}',
                          style: const TextStyle(color: Color(0xFFF63366), fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                      ),
                    ),
                  const Divider(height: 24),
                  () {
                    final rawCost = data['Purchase Cost'] ?? data['Cost'];
                    final costStr = rawCost != null
                        ? (rawCost is num ? '\$${rawCost.toStringAsFixed(2)}' : rawCost.toString())
                        : 'N/A';
                    return Wrap(
                      spacing: 24,
                      runSpacing: 12,
                      children: [
                        _buildMetaItem('Retailer', (data['Retailer/Website'] ?? 'N/A').toString(), Icons.storefront),
                        _buildMetaItem('Invoice #', (data['Retailer Invoice #'] ?? 'N/A').toString(), Icons.receipt),
                        _buildMetaItem('Cost', costStr, Icons.attach_money),
                        _buildMetaItem('Item #', (data['Retailer Item No.'] ?? 'N/A').toString(), Icons.tag),
                        _buildMetaItem('QTY', (data['Quantity'] ?? '1').toString(), Icons.numbers),
                        _buildMetaItem('Date', (data['Purchase Date'] ?? 'N/A').toString(), Icons.calendar_today),
                      ],
                    );
                  }(),
                  const SizedBox(height: 16),
                  Text(
                    'Source Desc: "${data['Original Description from source'] ?? 'N/A'}"',
                    style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12, fontStyle: FontStyle.italic),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  if ((data['source_file'] ?? '').toString().isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(top: 6),
                      child: Row(
                        children: [
                          const Icon(Icons.insert_drive_file_outlined, size: 13, color: Color(0xFF64748B)),
                          const SizedBox(width: 4),
                          Expanded(
                            child: Text(
                              'Scan File: ${data['source_file']}',
                              style: const TextStyle(color: Color(0xFF64748B), fontSize: 12, fontWeight: FontWeight.w500),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),
            // ── Edit button ──────────
            Tooltip(
              message: 'Edit this coin',
              child: IconButton(
                icon: const Icon(Icons.edit_note, color: Color(0xFF64748B)),
                onPressed: () => _showCoinEditDialog(id, data),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetaItem(String label, String value, IconData icon) {
    return SizedBox(
      width: 140,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: const Color(0xFF94A3B8)),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: const TextStyle(fontSize: 10, color: Color(0xFF94A3B8), fontWeight: FontWeight.bold)),
                Text(value, style: const TextStyle(fontSize: 12, color: Color(0xFF475569), fontWeight: FontWeight.w500, overflow: TextOverflow.ellipsis)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBadge(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withAlpha(20),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color.withAlpha(60)),
      ),
      child: Text(
        text,
        style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold),
      ),
    );
  }
}

// ─── Helper data class ────────────────────────────────────────────────────────

class _ItemTypeMeta {
  final String label;
  final Color  color;
  const _ItemTypeMeta({required this.label, required this.color});
}
