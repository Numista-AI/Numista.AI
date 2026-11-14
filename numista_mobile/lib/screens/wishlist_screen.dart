import 'dart:convert';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:share_plus/share_plus.dart';
import 'package:url_launcher/url_launcher.dart';

import '../constants.dart';
import '../models/coin_model.dart';
import '../models/program_model.dart';
import '../services/auth_service.dart';
import '../services/beta_checklist_service.dart';
import '../services/epn_service.dart';
import '../services/http_auth_client.dart';
import '../services/reference_service.dart';
import '../services/set_expansion_helper.dart';
import '../services/wishlist_service.dart';
import '../utils/mint_helpers.dart';
import '../utils/numista_error_helper.dart';
import '../utils/program_goal_helper.dart';

/// Senior-friendly Wish List screen (`SPEC_v2.1` daylight palette, >=18px text, >=56px touch targets).
class WishlistScreen extends StatefulWidget {
  final WishlistAutoFillPrefs? initialPrefsForTest;
  final List<AutoFilledProgramGroup>? initialAutoGroupsForTest;
  final List<WishlistItem>? initialManualItemsForTest;
  final bool? isGuestForTest;

  const WishlistScreen({
    super.key,
    this.initialPrefsForTest,
    this.initialAutoGroupsForTest,
    this.initialManualItemsForTest,
    this.isGuestForTest,
  });

  @override
  State<WishlistScreen> createState() => _WishlistScreenState();
}

class _WishlistScreenState extends State<WishlistScreen> {
  // SPEC_v2.1 Senior Daylight Palette
  static const Color _bg = Color(0xFFEEF3F8);
  static const Color _cardBg = Colors.white;
  static const Color _border = Color(0xFFD5DEEA);
  static const Color _ink = Color(0xFF0B1A2E);
  static const Color _inkMuted = Color(0xFF334155);
  static const Color _primaryBlue = Color(0xFF1D4F91);
  static const Color _gold = Color(0xFFC9A400);
  static const Color _emerald = Color(0xFF0F766E);

  final TextEditingController _recipientController = TextEditingController();
  final TextEditingController _noteController = TextEditingController();

  List<Map<String, dynamic>> _expandedCoins = [];
  Map<String, Map<String, dynamic>> _programPreferences = {};
  bool _inventoryLoaded = false;
  bool _isSendingEmail = false;
  bool _isCreatingShare = false;
  bool _recipientSeededFromPrefs = false;
  final Set<String> _markingSlotKeys = {};

  bool get _hasFirebaseApp =>
      widget.initialAutoGroupsForTest == null && Firebase.apps.isNotEmpty;

  bool get _isGuest {
    if (widget.isGuestForTest != null) return widget.isGuestForTest!;
    if (!_hasFirebaseApp) return true;
    return AuthService.isAnonymousUser ||
        AuthService.userEmail == 'guest' ||
        AuthService.userEmail.isEmpty;
  }

  @override
  void initState() {
    super.initState();
    if (widget.initialPrefsForTest != null &&
        widget.initialPrefsForTest!.lastRecipientEmail.isNotEmpty) {
      _recipientController.text =
          widget.initialPrefsForTest!.lastRecipientEmail;
      _recipientSeededFromPrefs = true;
    }
    if (_hasFirebaseApp) {
      _loadInventoryAndPrefs();
    } else {
      _inventoryLoaded = true;
    }
  }

  @override
  void dispose() {
    _recipientController.dispose();
    _noteController.dispose();
    super.dispose();
  }

  Future<void> _loadInventoryAndPrefs() async {
    if (!_hasFirebaseApp) {
      if (mounted) setState(() => _inventoryLoaded = true);
      return;
    }
    try {
      final db = FirebaseFirestore.instance;
      final primarySnap =
          await db.collection(AuthService.coinsPath).limit(2000).get();
      final Map<String, Map<String, dynamic>> mergedDocs = {};
      for (final d in primarySnap.docs) {
        mergedDocs[d.id] = d.data();
      }

      // Cross-path merge if primary email path is empty and user has a UID path.
      final authUser = FirebaseAuth.instance.currentUser;
      if (mergedDocs.isEmpty &&
          authUser != null &&
          !authUser.isAnonymous &&
          AuthService.coinsPath != 'users/${authUser.uid}/coins') {
        final uidSnap = await db
            .collection('users/${authUser.uid}/coins')
            .limit(2000)
            .get();
        for (final d in uidSnap.docs) {
          mergedDocs[d.id] = d.data();
        }
      }

      final docIds = mergedDocs.keys.toList();
      final docMaps = docIds.map((id) => mergedDocs[id]!).toList();
      final expansionResult = expandCollection(docMaps, docIds);

      final prefSnap = await db
          .doc(AuthService.userDocPath)
          .collection('program_preferences')
          .get();
      final prefsMap = <String, Map<String, dynamic>>{};
      for (final d in prefSnap.docs) {
        prefsMap[d.id] = d.data();
      }

      if (mounted) {
        setState(() {
          _expandedCoins = expansionResult.allItems;
          _programPreferences = prefsMap;
          _inventoryLoaded = true;
        });
      }
    } catch (_) {
      if (mounted) setState(() => _inventoryLoaded = true);
    }
  }

  String _userHash() {
    final id = _hasFirebaseApp ? AuthService.userIdentifier : 'guest';
    return id.hashCode.toUnsigned(32).toRadixString(16).padLeft(8, '0');
  }

  List<Map<String, dynamic>> _buildUnifiedSharePayload(
    List<AutoFilledProgramGroup> autoGroups,
    List<WishlistItem> manualItems,
  ) {
    final items = <Map<String, dynamic>>[];

    for (final group in autoGroups) {
      for (final slot in group.missingSlots) {
        final year = slot.coinSlot.year ?? '';
        items.add({
          'title':
              '${group.program.name}: ${slot.coinSlot.name}${year.isNotEmpty ? " ($year)" : ""} - ${slot.varietyLabel}',
          'program_id': group.program.id,
          'program_name': group.program.name,
          'coin_id': slot.coinSlot.id,
          'coin_name': slot.coinSlot.name,
          'year': year,
          'mint_mark': slot.mintMark,
          'variety_id': slot.variety.id,
          'variety_label': slot.varietyLabel,
          'target_grade': 'Uncirculated / AU',
          'max_price': 'Market Value',
          'ebay_query': slot.ebayQuery,
          'ebay_url': slot.ebayUrl,
        });
      }
    }

    for (int i = 0; i < manualItems.length; i++) {
      final item = manualItems[i];
      if (item.type != 'individual' || item.coin == null) continue;
      final c = item.coin!;
      final mm = MintHelpers.readMintMark({'mint_mark': c.mintMark});
      final titleName =
          c.themeSubject.isNotEmpty ? c.themeSubject : c.denomination;
      final queryParts = [
        if (c.year.isNotEmpty) c.year,
        if (mm.isNotEmpty) mm,
        if (c.programSeries.isNotEmpty) c.programSeries,
        if (titleName.isNotEmpty) titleName,
        'coin',
      ];
      final ebayQuery = queryParts.join(' ').trim();
      final ebayUrl = EpnService.buildSearchUrlFromQuery(
        ebayQuery,
        customId: '${_userHash()}_manual_$i',
      );
      items.add({
        'title': '${c.year} $titleName'.trim(),
        'program_id': '',
        'program_name': 'Individual Wanted Coins',
        'coin_id': item.id,
        'coin_name': titleName,
        'year': c.year,
        'mint_mark': mm,
        'variety_id': mm,
        'variety_label':
            MintHelpers.formatMintFacilityAndMark(c.mint, mm).isNotEmpty
                ? MintHelpers.formatMintFacilityAndMark(c.mint, mm)
                : 'Any Mint',
        'target_grade': c.condition.isNotEmpty ? c.condition : 'Any Grade',
        'max_price': 'Market Value',
        'ebay_query': ebayQuery,
        'ebay_url': ebayUrl,
      });
    }

    return items;
  }

  Future<void> _sendWishlistEmail(
    List<AutoFilledProgramGroup> autoGroups,
    List<WishlistItem> manualItems,
  ) async {
    if (_isGuest) return;
    final recipient = _recipientController.text.trim();
    if (!RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$').hasMatch(recipient)) {
      _showSnack('Please enter a valid family email address.');
      return;
    }

    final items = _buildUnifiedSharePayload(autoGroups, manualItems);
    if (items.isEmpty) {
      _showSnack('Add at least one coin to your Wish List first.');
      return;
    }

    setState(() => _isSendingEmail = true);
    try {
      await WishlistService.saveRecipientEmail(recipient);
      final userEmail = AuthService.userEmail;
      final alias = AuthService.displayName.isNotEmpty
          ? AuthService.displayName
          : userEmail.split('@').first;

      final response = await HttpAuthClient.post(
        Uri.parse('$kApiBaseUrl/api/wishlist/send-email'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_email': userEmail,
          'owner_alias': alias,
          'recipient_email': recipient,
          'personal_note': _noteController.text.trim(),
          'items': items,
        }),
      );

      if (!mounted) return;
      if (response.statusCode == 200) {
        BetaChecklistService.autoCompleteTask('task_15_public_wishlist');
        _showSnack(
          'Sent! Your Wish List of ${items.length} coins was emailed to $recipient.',
          backgroundColor: _emerald,
        );
      } else if (response.statusCode == 503) {
        _showSnack(
          'Email service is currently unavailable — please tap Copy / Share Link instead.',
        );
      } else {
        _showSnack(NumistaErrorHelper.toUserFriendly(response.body, statusCode: response.statusCode));
      }
    } catch (_) {
      if (mounted) {
        _showSnack(
          'Could not send email right now. Try Copy / Share Link instead.',
        );
      }
    } finally {
      if (mounted) setState(() => _isSendingEmail = false);
    }
  }

  Future<void> _handleCopyShareLink(
    List<AutoFilledProgramGroup> autoGroups,
    List<WishlistItem> manualItems,
  ) async {
    if (_isGuest) {
      _showSnack('Please sign in to create a shareable Wish List link.');
      return;
    }
    final items = _buildUnifiedSharePayload(autoGroups, manualItems);
    if (items.isEmpty) {
      _showSnack('Add at least one coin before sharing.');
      return;
    }

    setState(() => _isCreatingShare = true);
    try {
      final userEmail = AuthService.userEmail;
      final alias = AuthService.displayName.isNotEmpty
          ? AuthService.displayName
          : userEmail.split('@').first;

      final response = await HttpAuthClient.post(
        Uri.parse('$kApiBaseUrl/api/wishlist/create-share'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_email': userEmail,
          'owner_alias': alias,
          'items': items,
        }),
      );

      if (!mounted) return;
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final shareUrl = data['share_url']?.toString() ?? '';
        BetaChecklistService.autoCompleteTask('task_15_public_wishlist');
        if (shareUrl.isNotEmpty) {
          await Clipboard.setData(ClipboardData(text: shareUrl));
          if (!mounted) return;
          await showDialog<void>(
            context: context,
            builder: (ctx) => AlertDialog(
              backgroundColor: Colors.white,
              title: const Text(
                'Share Wish List Link',
                style: TextStyle(
                  color: _ink,
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Link copied to your clipboard! Send this link to family or friends:',
                    style: TextStyle(color: _inkMuted, fontSize: 18),
                  ),
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: _bg,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: _border),
                    ),
                    child: SelectableText(
                      shareUrl,
                      style: const TextStyle(
                        color: _primaryBlue,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
              actions: [
                ConstrainedBox(
                  constraints: const BoxConstraints(minHeight: 56),
                  child: TextButton(
                    onPressed: () => Navigator.of(ctx).pop(),
                    child: const Text('Close', style: TextStyle(fontSize: 18)),
                  ),
                ),
                ConstrainedBox(
                  constraints: const BoxConstraints(minHeight: 56),
                  child: ElevatedButton.icon(
                    onPressed: () {
                      Navigator.of(ctx).pop();
                      Share.share(
                        'Here is my coin Wish List: $shareUrl',
                        subject: 'My Coin Wish List',
                      );
                    },
                    icon: const Icon(Icons.share),
                    label: const Text(
                      'Share',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _primaryBlue,
                      foregroundColor: Colors.white,
                      minimumSize: const Size(0, 56),
                    ),
                  ),
                ),
              ],
            ),
          );
        }
      } else {
        _showSnack(NumistaErrorHelper.toUserFriendly(response.body, statusCode: response.statusCode));
      }
    } catch (_) {
      if (mounted) _showSnack('Unable to create share link right now.');
    } finally {
      if (mounted) setState(() => _isCreatingShare = false);
    }
  }

  Future<void> _markAutoSlotAsGotIt(MissingProgramSlot slot) async {
    if (!_hasFirebaseApp) return;
    setState(() => _markingSlotKeys.add(slot.slotKey));
    try {
      final rawYear = slot.coinSlot.year ?? '';
      final upperVar = slot.variety.id.toUpperCase();
      final resolvedMint = MintHelpers.resolveTwoFieldMint(
        rawMintMark: slot.mintMark,
        year: rawYear,
        series: slot.program.name,
        denomination: slot.program.category,
        variety: upperVar == 'EU' ? 'Enhanced Uncirculated' : '',
        strikeType: upperVar.contains('REVERSE-PROOF')
            ? 'Reverse Proof'
            : (upperVar.contains('PROOF') || upperVar == 'S-CLAD'
                ? 'Proof'
                : ''),
        metalContent: upperVar.contains('SILVER') ? '90% Silver' : '',
      );

      final payload = {
        'idempotency_key':
            '${slot.slotKey}_${DateTime.now().millisecondsSinceEpoch}',
        'program_id': slot.program.id,
        'program_name': slot.program.name,
        'user_email': AuthService.userEmail,
        'slots': [
          {
            'coin_name': slot.coinSlot.name,
            'year': rawYear,
            'mint': resolvedMint.mint,
            'mint_mark': resolvedMint.mintMark,
            'denomination': slot.program.category,
            'variety_id': slot.variety.id,
            'quantity': 1,
            'Quantity': 1,
          }
        ],
      };

      final response = await HttpAuthClient.post(
        Uri.parse('$kApiBaseUrl/api/checklist/add_coins'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(payload),
      );
      if (response.statusCode == 200) {
        await _loadInventoryAndPrefs();
        if (mounted) {
          _showSnack(
            'Added ${slot.coinSlot.name} to your Collection!',
            backgroundColor: _emerald,
          );
        }
      } else if (mounted) {
        _showSnack(NumistaErrorHelper.toUserFriendly(response.body, statusCode: response.statusCode));
      }
    } catch (_) {
      if (mounted) {
        _showSnack('Could not mark coin as collected right now.');
      }
    } finally {
      if (mounted) setState(() => _markingSlotKeys.remove(slot.slotKey));
    }
  }

  Future<void> _markManualItemAsGotIt(WishlistItem item) async {
    if (item.coin == null) return;
    final coin = item.coin!;
    try {
      await FirebaseFirestore.instance.collection(AuthService.coinsPath).add({
        ...coin.toFirestore(),
        'Timestamp': FieldValue.serverTimestamp(),
      });
      await WishlistService.removeFromWishlist(item.id);
      await _loadInventoryAndPrefs();
      if (mounted) {
        _showSnack(
          'Moved ${coin.themeSubject.isNotEmpty ? coin.themeSubject : coin.denomination} to your Collection!',
          backgroundColor: _emerald,
        );
      }
    } catch (_) {
      if (mounted) _showSnack('Could not save coin to Collection.');
    }
  }

  Future<void> _openUrl(String rawUrl) async {
    final uri = Uri.tryParse(rawUrl);
    if (uri != null && await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }

  void _showSnack(String message, {Color backgroundColor = _primaryBlue}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: backgroundColor,
        content: Text(
          message,
          style: const TextStyle(
            fontSize: 18,
            color: Colors.white,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }

  Future<void> _openAddCoinModal() async {
    List<Map<String, dynamic>> catalogItems = [];
    try {
      final rawJson =
          await rootBundle.loadString('assets/catalog/catalog_public_v1.json');
      final decoded = jsonDecode(rawJson);
      if (decoded is Map && decoded['items'] is List) {
        catalogItems = List<Map<String, dynamic>>.from(decoded['items'] as List);
      } else if (decoded is List) {
        catalogItems = List<Map<String, dynamic>>.from(decoded);
      }
    } catch (_) {
      catalogItems = [];
    }
    if (!mounted) return;

    final searchCtrl = TextEditingController();
    final nameCtrl = TextEditingController();
    final yearCtrl = TextEditingController();
    final notesCtrl = TextEditingController();
    String selectedMint = '';
    int activeTab = 0; // 0 = Type by hand, 1 = Search Catalog

    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setModalState) {
          final q = searchCtrl.text.trim().toLowerCase();
          final filteredCatalog = catalogItems
              .where((it) {
                final name = (it['name'] ?? '').toString().toLowerCase();
                final year = (it['year'] ?? '').toString().toLowerCase();
                final series = (it['series'] ?? '').toString().toLowerCase();
                return q.isEmpty ||
                    name.contains(q) ||
                    year.contains(q) ||
                    series.contains(q);
              })
              .take(25)
              .toList();

          return Padding(
            padding: EdgeInsets.fromLTRB(
              20,
              20,
              20,
              MediaQuery.of(ctx).viewInsets.bottom + 24,
            ),
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Add a Coin to My Wish List',
                    style: TextStyle(
                      color: _ink,
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 10,
                    runSpacing: 10,
                    children: [
                      ConstrainedBox(
                        constraints: const BoxConstraints(minHeight: 56),
                        child: ElevatedButton(
                          onPressed: () => setModalState(() => activeTab = 0),
                          style: ElevatedButton.styleFrom(
                            minimumSize: const Size(0, 56),
                            backgroundColor:
                                activeTab == 0 ? _primaryBlue : _bg,
                            foregroundColor:
                                activeTab == 0 ? Colors.white : _ink,
                          ),
                          child: const Text(
                            'Type Coin by Hand',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                      ConstrainedBox(
                        constraints: const BoxConstraints(minHeight: 56),
                        child: ElevatedButton(
                          onPressed: () => setModalState(() => activeTab = 1),
                          style: ElevatedButton.styleFrom(
                            minimumSize: const Size(0, 56),
                            backgroundColor:
                                activeTab == 1 ? _primaryBlue : _bg,
                            foregroundColor:
                                activeTab == 1 ? Colors.white : _ink,
                          ),
                          child: const Text(
                            'Search Catalog',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  if (activeTab == 0) ...[
                    TextField(
                      controller: nameCtrl,
                      style: const TextStyle(fontSize: 20, color: _ink),
                      decoration: const InputDecoration(
                        labelText: 'Coin Name (e.g. Morgan Silver Dollar)',
                        labelStyle: TextStyle(fontSize: 18),
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: yearCtrl,
                      keyboardType: TextInputType.number,
                      style: const TextStyle(fontSize: 20, color: _ink),
                      decoration: const InputDecoration(
                        labelText: 'Year (optional)',
                        labelStyle: TextStyle(fontSize: 18),
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    const Text(
                      'Mint Mark',
                      style: TextStyle(
                        color: _ink,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: ['Any', 'P', 'D', 'S', 'W', 'CC', 'O'].map((m) {
                        final val = m == 'Any' ? '' : m;
                        return ChoiceChip(
                          label: Padding(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 6,
                              vertical: 8,
                            ),
                            child: Text(
                              m,
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          selected: selectedMint == val,
                          onSelected: (_) =>
                              setModalState(() => selectedMint = val),
                        );
                      }).toList(),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: notesCtrl,
                      style: const TextStyle(fontSize: 18, color: _ink),
                      decoration: const InputDecoration(
                        labelText: 'Notes (optional)',
                        labelStyle: TextStyle(fontSize: 18),
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      child: ConstrainedBox(
                        constraints: const BoxConstraints(minHeight: 56),
                        child: ElevatedButton.icon(
                          onPressed: () async {
                            final coinName = nameCtrl.text.trim();
                            if (coinName.isEmpty) return;
                            final resolved = MintHelpers.resolveTwoFieldMint(
                              rawMintMark: selectedMint,
                              year: yearCtrl.text.trim(),
                              series: coinName,
                            );
                            final coin = CoinModel(
                              id: 'wish_${DateTime.now().millisecondsSinceEpoch}',
                              year: yearCtrl.text.trim(),
                              mint: resolved.mint,
                              mintMark: resolved.mintMark,
                              themeSubject: coinName,
                              programSeries: coinName,
                              personalNotes: notesCtrl.text.trim(),
                            );
                            await WishlistService.addToWishlist(coin);
                            if (ctx.mounted) Navigator.of(ctx).pop();
                            _showSnack('Added "$coinName" to your Wish List!');
                          },
                          icon: const Icon(Icons.favorite),
                          label: const Text(
                            'Save to My Wish List',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          style: ElevatedButton.styleFrom(
                            minimumSize: const Size(0, 56),
                            backgroundColor: _primaryBlue,
                            foregroundColor: Colors.white,
                          ),
                        ),
                      ),
                    ),
                  ] else ...[
                    TextField(
                      controller: searchCtrl,
                      onChanged: (_) => setModalState(() {}),
                      style: const TextStyle(fontSize: 20, color: _ink),
                      decoration: const InputDecoration(
                        labelText: 'Search catalog coins...',
                        labelStyle: TextStyle(fontSize: 18),
                        prefixIcon: Icon(Icons.search),
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    if (filteredCatalog.isEmpty)
                      const Text(
                        'No catalog matches found. Try typing by hand instead.',
                        style: TextStyle(fontSize: 18, color: _inkMuted),
                      )
                    else
                      ...filteredCatalog.map((item) {
                        final title =
                            '${item['year'] ?? ''} ${item['name'] ?? ''}'.trim();
                        return Card(
                          margin: const EdgeInsets.only(bottom: 10),
                          child: Padding(
                            padding: const EdgeInsets.all(12),
                            child: Row(
                              children: [
                                Expanded(
                                  child: Text(
                                    title,
                                    style: const TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                      color: _ink,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 10),
                                ConstrainedBox(
                                  constraints:
                                      const BoxConstraints(minHeight: 56),
                                  child: ElevatedButton.icon(
                                    onPressed: () async {
                                      final resolved =
                                          MintHelpers.resolveTwoFieldMint(
                                        rawMintMark:
                                            item['mint_mark']?.toString() ?? '',
                                        year: item['year']?.toString() ?? '',
                                        series:
                                            item['series']?.toString() ?? '',
                                        denomination:
                                            item['denomination']?.toString() ??
                                                '',
                                      );
                                      await WishlistService.addToWishlist(
                                        CoinModel(
                                          id: 'cat_${DateTime.now().millisecondsSinceEpoch}',
                                          year: item['year']?.toString() ?? '',
                                          mint: resolved.mint,
                                          mintMark: resolved.mintMark,
                                          denomination:
                                              item['denomination']?.toString() ??
                                                  '',
                                          programSeries:
                                              item['series']?.toString() ?? '',
                                          themeSubject:
                                              item['name']?.toString() ?? '',
                                        ),
                                      );
                                      if (ctx.mounted) Navigator.of(ctx).pop();
                                      _showSnack(
                                          'Added "$title" to your Wish List!');
                                    },
                                    icon: const Icon(Icons.add),
                                    label: const Text(
                                      'Add',
                                      style: TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                    style: ElevatedButton.styleFrom(
                                      minimumSize: const Size(0, 56),
                                      backgroundColor: _primaryBlue,
                                      foregroundColor: Colors.white,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      }),
                  ],
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (widget.initialAutoGroupsForTest != null) {
      return _buildScaffold(
        prefs: widget.initialPrefsForTest ?? const WishlistAutoFillPrefs(),
        autoGroups: widget.initialAutoGroupsForTest!,
        manualItems: widget.initialManualItemsForTest ?? const [],
      );
    }

    if (!_hasFirebaseApp) {
      return _buildScaffold(
        prefs: widget.initialPrefsForTest ?? const WishlistAutoFillPrefs(),
        autoGroups: const [],
        manualItems: const [],
      );
    }

    return StreamBuilder<WishlistAutoFillPrefs>(
      stream: WishlistService.getWishlistPrefsStream(),
      builder: (context, prefsSnap) {
        final prefs = prefsSnap.data ?? const WishlistAutoFillPrefs();
        if (!_recipientSeededFromPrefs &&
            prefs.lastRecipientEmail.isNotEmpty &&
            _recipientController.text.isEmpty) {
          _recipientSeededFromPrefs = true;
          WidgetsBinding.instance.addPostFrameCallback((_) {
            if (mounted && _recipientController.text.isEmpty) {
              _recipientController.text = prefs.lastRecipientEmail;
            }
          });
        }

        return StreamBuilder<Map<String, List<CoinProgram>>>(
          stream: ReferenceService.getGroupedProgramsStream(),
          builder: (context, progSnap) {
            final allProgramsMap = progSnap.data ?? const {};
            final autoGroups = _inventoryLoaded
                ? WishlistService.computeAutoMissingPrograms(
                    allProgramsMap: allProgramsMap,
                    expandedCoins: _expandedCoins,
                    programPreferences: _programPreferences,
                    wishlistPrefs: prefs,
                    userHash: _userHash(),
                  )
                : <AutoFilledProgramGroup>[];

            return StreamBuilder<List<WishlistItem>>(
              stream: WishlistService.getWishlistStream(),
              builder: (context, wishSnap) {
                final manualItems = wishSnap.data ?? const <WishlistItem>[];
                return _buildScaffold(
                  prefs: prefs,
                  autoGroups: autoGroups,
                  manualItems: manualItems,
                );
              },
            );
          },
        );
      },
    );
  }

  Widget _buildScaffold({
    required WishlistAutoFillPrefs prefs,
    required List<AutoFilledProgramGroup> autoGroups,
    required List<WishlistItem> manualItems,
  }) {
    final individualItems = manualItems
        .where((i) => i.type == 'individual' && i.coin != null)
        .toList();
    final hasHidden =
        prefs.dismissedSlots.isNotEmpty || prefs.dismissedPrograms.isNotEmpty;

    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        backgroundColor: Colors.white,
        foregroundColor: _ink,
        elevation: 0,
        toolbarHeight: 68,
        title: const Text(
          'My Wish List',
          style: TextStyle(
            color: _ink,
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
        ),
        bottom: const PreferredSize(
          preferredSize: Size.fromHeight(1),
          child: Divider(height: 1, color: _border),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 960),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _buildSendToFamilyCard(prefs, autoGroups, manualItems),
                const SizedBox(height: 16),
                if (!_isGuest && _hasFirebaseApp) ...[
                  _buildGiftActivityBanner(),
                  const SizedBox(height: 16),
                ],
                ConstrainedBox(
                  constraints: const BoxConstraints(minHeight: 56),
                  child: ElevatedButton.icon(
                    key: const Key('wishlist_add_coin_button'),
                    onPressed: _hasFirebaseApp ? _openAddCoinModal : null,
                    icon: const Icon(Icons.add_circle_outline, size: 24),
                    label: const Text(
                      '+ Add a Coin to My Wish List',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size(0, 56),
                      backgroundColor: _primaryBlue,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                const Text(
                  'Coins Needed to Complete My Sets (Auto-Added)',
                  style: TextStyle(
                    color: _ink,
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                if (autoGroups.isEmpty)
                  _buildEmptyAutoCard()
                else
                  ...autoGroups.map(_buildProgramGroupCard),
                const SizedBox(height: 24),
                const Text(
                  "Individual Coins I'm Wishing For",
                  style: TextStyle(
                    color: _ink,
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                if (individualItems.isEmpty)
                  _buildEmptyManualCard()
                else
                  ...individualItems.map(_buildManualCoinCard),
                if (hasHidden) ...[
                  const SizedBox(height: 16),
                  ConstrainedBox(
                    constraints: const BoxConstraints(minHeight: 56),
                    child: ElevatedButton.icon(
                      key: const Key('wishlist_restore_hidden_button'),
                      onPressed: _hasFirebaseApp
                          ? () => WishlistService.restoreAllHidden()
                          : null,
                      icon: const Icon(Icons.restore),
                      label: const Text(
                        'Restore Hidden Coins / Programs',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      style: ElevatedButton.styleFrom(
                        minimumSize: const Size(0, 56),
                        backgroundColor: Colors.white,
                        foregroundColor: _primaryBlue,
                        side: const BorderSide(color: _primaryBlue, width: 1.5),
                      ),
                    ),
                  ),
                ],
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSendToFamilyCard(
    WishlistAutoFillPrefs prefs,
    List<AutoFilledProgramGroup> autoGroups,
    List<WishlistItem> manualItems,
  ) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: _border, width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Send My Wish List to Family',
            style: TextStyle(
              color: _ink,
              fontSize: 22,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          if (_isGuest) ...[
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFFEF3C7),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: _gold, width: 1.5),
              ),
              child: const Text(
                'Please sign in with your email account to email your Wish List to family.',
                style: TextStyle(
                  color: _ink,
                  fontSize: 20,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
            const SizedBox(height: 14),
          ] else ...[
            if (prefs.savedRecipientEmails.isNotEmpty) ...[
              const Text(
                'Saved Family Emails:',
                style: TextStyle(
                  color: _inkMuted,
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: prefs.savedRecipientEmails.map((email) {
                  return ConstrainedBox(
                    constraints: const BoxConstraints(minHeight: 56),
                    child: ActionChip(
                      backgroundColor: _bg,
                      side: const BorderSide(color: _primaryBlue),
                      label: Text(
                        email,
                        style: const TextStyle(
                          color: _ink,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      onPressed: () {
                        setState(() => _recipientController.text = email);
                      },
                    ),
                  );
                }).toList(),
              ),
              const SizedBox(height: 12),
            ],
            TextField(
              controller: _recipientController,
              keyboardType: TextInputType.emailAddress,
              style: const TextStyle(fontSize: 20, color: _ink),
              decoration: const InputDecoration(
                labelText: 'Family Member Email',
                hintText: 'eric@example.com',
                labelStyle: TextStyle(fontSize: 18, color: _inkMuted),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _noteController,
              style: const TextStyle(fontSize: 18, color: _ink),
              decoration: const InputDecoration(
                labelText: 'Personal Note (Optional)',
                hintText: 'Ideas for Christmas or my Birthday!',
                labelStyle: TextStyle(fontSize: 18, color: _inkMuted),
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 14),
          ],
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              ConstrainedBox(
                constraints: const BoxConstraints(minHeight: 56),
                child: ElevatedButton.icon(
                  key: const Key('wishlist_send_email_button'),
                  onPressed: (_isGuest || _isSendingEmail)
                      ? null
                      : () => _sendWishlistEmail(autoGroups, manualItems),
                  icon: _isSendingEmail
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.5,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.email_outlined, size: 22),
                  label: Text(
                    _isSendingEmail ? 'Sending...' : 'Send Wish List Email',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(0, 56),
                    backgroundColor: _primaryBlue,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 14,
                    ),
                  ),
                ),
              ),
              ConstrainedBox(
                constraints: const BoxConstraints(minHeight: 56),
                child: ElevatedButton.icon(
                  key: const Key('wishlist_copy_share_button'),
                  onPressed: (_isGuest || _isCreatingShare)
                      ? null
                      : () => _handleCopyShareLink(autoGroups, manualItems),
                  icon: const Icon(Icons.link, size: 22),
                  label: Text(
                    _isCreatingShare ? 'Creating Link...' : 'Copy / Share Link',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(0, 56),
                    backgroundColor: Colors.white,
                    foregroundColor: _primaryBlue,
                    side: const BorderSide(color: _primaryBlue, width: 1.5),
                    padding: const EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 14,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildProgramGroupCard(AutoFilledProgramGroup group) {
    final bool isCirculationOnly =
        group.effectiveGoal == ProgramGoalHelper.defaultAutoFillGoal;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: _border, width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            group.program.name,
            style: const TextStyle(
              color: _ink,
              fontSize: 22,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'You have ${group.ownedCount} of ${group.targetCount} coins • ${group.missingSlots.length} missing',
            style: const TextStyle(
              color: _inkMuted,
              fontSize: 18,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              ConstrainedBox(
                constraints: const BoxConstraints(minHeight: 56),
                child: ElevatedButton(
                  onPressed: _hasFirebaseApp
                      ? () => WishlistService.setProgramGoalOverride(
                            group.program.id,
                            ProgramGoalHelper.defaultAutoFillGoal,
                          )
                      : null,
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(0, 56),
                    backgroundColor: isCirculationOnly ? _primaryBlue : _bg,
                    foregroundColor: isCirculationOnly ? Colors.white : _ink,
                  ),
                  child: const Text(
                    'P & D Circulation Strikes',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ),
              ),
              ConstrainedBox(
                constraints: const BoxConstraints(minHeight: 56),
                child: ElevatedButton(
                  onPressed: _hasFirebaseApp
                      ? () => WishlistService.setProgramGoalOverride(
                            group.program.id,
                            'Full Master Set',
                          )
                      : null,
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(0, 56),
                    backgroundColor: !isCirculationOnly ? _primaryBlue : _bg,
                    foregroundColor: !isCirculationOnly ? Colors.white : _ink,
                  ),
                  child: const Text(
                    'All Mint Marks (Include S Proofs)',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ),
              ),
              ConstrainedBox(
                constraints: const BoxConstraints(minHeight: 56),
                child: ElevatedButton.icon(
                  onPressed: _hasFirebaseApp
                      ? () => WishlistService.dismissAutoProgram(group.program.id)
                      : null,
                  icon: const Icon(Icons.visibility_off_outlined),
                  label: const Text(
                    'Hide Program',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(0, 56),
                    backgroundColor: Colors.white,
                    foregroundColor: _inkMuted,
                    side: const BorderSide(color: _border, width: 1.5),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          ...group.missingSlots.map(_buildMissingSlotRow),
        ],
      ),
    );
  }

  Widget _buildMissingSlotRow(MissingProgramSlot slot) {
    final isMarking = _markingSlotKeys.contains(slot.slotKey);
    final yearText = (slot.coinSlot.year ?? '').trim();
    final title = yearText.isNotEmpty
        ? '$yearText ${slot.coinSlot.name}'
        : slot.coinSlot.name;

    return Container(
      margin: const EdgeInsets.only(top: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: _bg,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: _border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              color: _ink,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 6),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: _gold, width: 1.5),
            ),
            child: Text(
              slot.varietyLabel,
              style: const TextStyle(
                color: _ink,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              ConstrainedBox(
                constraints: const BoxConstraints(minHeight: 56),
                child: ElevatedButton.icon(
                  onPressed: () => _openUrl(slot.ebayUrl),
                  icon: const Icon(Icons.open_in_new),
                  label: const Text(
                    'Buy on eBay',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(0, 56),
                    backgroundColor: _primaryBlue,
                    foregroundColor: Colors.white,
                  ),
                ),
              ),
              ConstrainedBox(
                constraints: const BoxConstraints(minHeight: 56),
                child: ElevatedButton.icon(
                  onPressed: isMarking || !_hasFirebaseApp
                      ? null
                      : () => _markAutoSlotAsGotIt(slot),
                  icon: const Icon(Icons.check_circle_outline),
                  label: Text(
                    isMarking ? 'Saving...' : 'I Got It!',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(0, 56),
                    backgroundColor: _emerald,
                    foregroundColor: Colors.white,
                  ),
                ),
              ),
              ConstrainedBox(
                constraints: const BoxConstraints(minHeight: 56),
                child: ElevatedButton.icon(
                  onPressed: _hasFirebaseApp
                      ? () => WishlistService.dismissAutoSlot(slot.slotKey)
                      : null,
                  icon: const Icon(Icons.close),
                  label: const Text(
                    'Remove',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(0, 56),
                    backgroundColor: Colors.white,
                    foregroundColor: _inkMuted,
                    side: const BorderSide(color: _border, width: 1.5),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildManualCoinCard(WishlistItem item) {
    final coin = item.coin!;
    final title = [
      if (coin.year.trim().isNotEmpty) coin.year.trim(),
      coin.themeSubject.isNotEmpty ? coin.themeSubject : coin.denomination,
    ].join(' ');
    final mintText =
        MintHelpers.formatMintFacilityAndMark(coin.mint, coin.mintMark);
    final query = [
      if (coin.year.isNotEmpty) coin.year,
      if (coin.mintMark.isNotEmpty) coin.mintMark,
      if (coin.programSeries.isNotEmpty) coin.programSeries,
      coin.themeSubject.isNotEmpty ? coin.themeSubject : coin.denomination,
      'coin',
    ].join(' ');
    final ebayUrl = EpnService.buildSearchUrlFromQuery(
      query,
      customId: '${_userHash()}_${item.id}',
    );

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _border, width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title.isEmpty ? 'Wanted Coin' : title,
            style: const TextStyle(
              color: _ink,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          if (mintText.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(
              mintText,
              style: const TextStyle(
                color: _inkMuted,
                fontSize: 18,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
          const SizedBox(height: 12),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              ConstrainedBox(
                constraints: const BoxConstraints(minHeight: 56),
                child: ElevatedButton.icon(
                  onPressed: () => _openUrl(ebayUrl),
                  icon: const Icon(Icons.open_in_new),
                  label: const Text(
                    'Buy on eBay',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(0, 56),
                    backgroundColor: _primaryBlue,
                    foregroundColor: Colors.white,
                  ),
                ),
              ),
              ConstrainedBox(
                constraints: const BoxConstraints(minHeight: 56),
                child: ElevatedButton.icon(
                  onPressed: _hasFirebaseApp
                      ? () => _markManualItemAsGotIt(item)
                      : null,
                  icon: const Icon(Icons.check_circle_outline),
                  label: const Text(
                    'I Got It!',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(0, 56),
                    backgroundColor: _emerald,
                    foregroundColor: Colors.white,
                  ),
                ),
              ),
              ConstrainedBox(
                constraints: const BoxConstraints(minHeight: 56),
                child: ElevatedButton.icon(
                  onPressed: _hasFirebaseApp
                      ? () => WishlistService.removeFromWishlist(item.id)
                      : null,
                  icon: const Icon(Icons.delete_outline),
                  label: const Text(
                    'Remove',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(0, 56),
                    backgroundColor: Colors.white,
                    foregroundColor: _inkMuted,
                    side: const BorderSide(color: _border, width: 1.5),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyAutoCard() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _border),
      ),
      child: const Text(
        'Missing coins from your coin sets will appear here automatically once you add a coin from any program.',
        style: TextStyle(color: _inkMuted, fontSize: 18),
      ),
    );
  }

  Widget _buildEmptyManualCard() {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: _cardBg,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _border),
      ),
      child: const Text(
        'Tap "+ Add a Coin to My Wish List" above or tap Wish List from the Catalog, Coin Search, or Ask Morgan.',
        style: TextStyle(color: _inkMuted, fontSize: 18),
      ),
    );
  }

  Widget _buildGiftActivityBanner() {
    final userEmail = AuthService.userEmail;
    if (userEmail.isEmpty) return const SizedBox.shrink();

    return StreamBuilder<QuerySnapshot>(
      stream: FirebaseFirestore.instance
          .collection('public_wishlists')
          .where('owner_email', isEqualTo: userEmail)
          .snapshots(),
      builder: (context, snapshot) {
        if (!snapshot.hasData || snapshot.data!.docs.isEmpty) {
          return _buildBannerCard(0, const []);
        }
        final doc = snapshot.data!.docs.first.data() as Map<String, dynamic>;
        final reservedIndices = List<int>.from(doc['reserved_items'] ?? []);
        final detailsMap =
            Map<String, dynamic>.from(doc['reservation_details'] ?? {});
        final items = List<Map<String, dynamic>>.from(doc['items'] ?? []);
        final reservedDetailsList = <Map<String, String>>[];

        for (final idx in reservedIndices) {
          final title = idx < items.length
              ? (items[idx]['title']?.toString() ?? 'Coin Item')
              : 'Wishlist Item';
          final detail = detailsMap[idx.toString()] as Map<String, dynamic>?;
          final by = detail?['reserved_by']?.toString() ?? 'Family Member';
          reservedDetailsList.add({'title': title, 'reserved_by': by});
        }
        return _buildBannerCard(reservedIndices.length, reservedDetailsList);
      },
    );
  }

  Widget _buildBannerCard(
    int reservedCount,
    List<Map<String, String>> details,
  ) {
    final isReserved = reservedCount > 0;
    return Container(
      decoration: BoxDecoration(
        color: isReserved ? const Color(0xFFDCFCE7) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isReserved ? _emerald : _border,
          width: 1.5,
        ),
      ),
      child: ExpansionTile(
        tilePadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Icon(
          isReserved ? Icons.card_giftcard : Icons.card_giftcard_outlined,
          color: isReserved ? _emerald : _inkMuted,
          size: 28,
        ),
        title: Text(
          isReserved
              ? '$reservedCount Wish List Items Reserved by Relatives'
              : '0 items currently reserved by family members',
          style: TextStyle(
            color: isReserved ? _emerald : _ink,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        subtitle: Text(
          isReserved
              ? 'Tap to view gift items family members marked as bought'
              : 'Email or share your Wish List so family can mark gifts they buy',
          style: const TextStyle(color: _inkMuted, fontSize: 18),
        ),
        children: details
            .map(
              (d) => ListTile(
                leading: const Icon(Icons.check_circle_outline, color: _emerald),
                title: Text(
                  d['title']!,
                  style: const TextStyle(
                    color: _ink,
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                subtitle: Text(
                  'Reserved by ${d['reserved_by']}',
                  style: const TextStyle(color: _emerald, fontSize: 18),
                ),
              ),
            )
            .toList(),
      ),
    );
  }
}
