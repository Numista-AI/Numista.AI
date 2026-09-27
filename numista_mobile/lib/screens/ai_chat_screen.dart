import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'dart:convert';
import 'dart:typed_data';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:http_parser/http_parser.dart';
import '../services/set_grouping_service.dart';
import '../services/auth_service.dart';
import '../services/morgan_prefs.dart';
import '../services/morgan_chat_context.dart';
import '../services/tts_voice_service.dart';
import '../widgets/morgan_settings_panel.dart';
import '../services/beta_checklist_service.dart';
import '../constants.dart';

// ══════════════════════════════════════════════════════════════════════════════
//  AiChatScreen — Phase 3: Collection-Aware Morgan Chat
//  ──────────────────────────────────────────────────────
//  Morgan now knows the user's entire collection from Firestore.
//  • Opens with a personalised greeting ("You've got 47 coins worth $2,450 …")
//  • Passes a system prompt + collection context to every API call
//  • Uses Morgan's dark navy + teal colour palette
//  • Large readable text (≥ 15px) with warm, patient tone
// ══════════════════════════════════════════════════════════════════════════════

class AiChatScreen extends StatefulWidget {
  /// Optional pre-populated query (from "AI Deep Dive" button on a coin).
  final String? initialQuery;
  final bool isPopout;
  final bool isMinimized;
  final VoidCallback? onClose;
  final VoidCallback? onMinimize;
  final ValueChanged<DragUpdateDetails>? onDragUpdate;
  final VoidCallback? onDragEnd;
  final VoidCallback? onNavigateToCollection;

  const AiChatScreen({
    super.key,
    this.initialQuery,
    this.isPopout = false,
    this.isMinimized = false,
    this.onClose,
    this.onMinimize,
    this.onDragUpdate,
    this.onDragEnd,
    this.onNavigateToCollection,
  });

  @override
  State<AiChatScreen> createState() => _AiChatScreenState();
}

class _AiChatScreenState extends State<AiChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollCtrl = ScrollController();
  final List<Map<String, dynamic>> _messages = [];
  late final FocusNode _focusNode;

  bool _isLoading = false;
  bool _isLoadingHistory = true;
  bool _isLoadingContext = true;
  String? _sessionId;
  MorganCollectionContext? _ctx;
  String _displayName = 'there';

  // Group photo state
  Uint8List? _pendingPhotoBytes;
  String? _pendingPhotoName;
  bool _isIdentifyingPhoto = false;

  // ── Morgan colour palette ────────────────────────────────────────────────
  Color get _bg => Theme.of(context).brightness == Brightness.dark ? Color(0xFF0B1220) : Color(0xFFF4F4F2);
  Color get _surf => Theme.of(context).brightness == Brightness.dark ? Color(0xFF162033) : Colors.white;
  Color get _teal => Color(0xFF2DD4BF);
  static const _gold  = Color(0xFFD4A843);   // Morgan gold
  Color get _sub => Theme.of(context).brightness == Brightness.dark ? Color(0xFF94A3B8) : Color(0xFF5A5C69);
  Color get _userBubble => Theme.of(context).brightness == Brightness.dark ? Color(0xFF1E4D4D) : Color(0xFFE0F2F1);
  Color get _aiBubble => Theme.of(context).brightness == Brightness.dark ? Color(0xFF162033) : Color(0xFFF0F4F8);
  Color get _textPrimary => Theme.of(context).brightness == Brightness.dark ? Colors.white : Color(0xFF0F172A);

  // ── Firestore session path (Keyed strictly by Auth UID) ────────────────────
  CollectionReference? get _sessionsRef {
    final user = FirebaseAuth.instance.currentUser;
    if (user == null) return null;
    final uid = user.uid.isNotEmpty ? user.uid : (user.email ?? 'guest_uid');
    return FirebaseFirestore.instance
        .collection('users')
        .doc(uid)
        .collection('ai_chat_sessions');
  }

  DocumentReference? get _currentSessionRef =>
      _sessionId == null ? null : _sessionsRef?.doc(_sessionId);

  @override
  void initState() {
    super.initState();
    _focusNode = FocusNode();
    _loadEverything();
    if (widget.isPopout) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) _focusNode.requestFocus();
      });
    }
  }

  Future<void> _loadEverything() async {
    // Load user name and collection context in parallel with session history
    final nameF = MorganPrefs.getDisplayName();
    final ctxF  = MorganChatContextService.load();

    _displayName = await nameF;
    _ctx = await ctxF;
    if (mounted) setState(() => _isLoadingContext = false);

    await _loadOrCreateSession();
  }

  Future<void> _loadOrCreateSession() async {
    if (AuthService.isGuest) {
      if (mounted) setState(() => _isLoadingHistory = false);
      _sendMorganOpener();
      _maybeSendInitialQuery();
      return;
    }

    try {
      final ref = _sessionsRef;
      if (ref == null) {
        if (mounted) setState(() => _isLoadingHistory = false);
        return;
      }

      final snap = await ref
          .orderBy('updated_at', descending: true)
          .limit(1)
          .get();

      if (snap.docs.isNotEmpty && widget.initialQuery == null) {
        final doc = snap.docs.first;
        _sessionId = doc.id;
        final raw = (doc.data() as Map<String, dynamic>)['messages'] as List? ?? [];
        final loaded = raw
            .whereType<Map>()
            .map((m) => {
                  'role':    m['role']?.toString() ?? 'user',
                  'content': m['content']?.toString() ?? '',
                })
            .toList();
        if (mounted) {
          setState(() {
            _messages.addAll(loaded.cast<Map<String, dynamic>>());
            _isLoadingHistory = false;
          });
        }
        _scrollToBottom();
      } else {
        await _startNewSession();
        _sendMorganOpener();
      }
    } catch (e) {
      debugPrint('[AiChat] Failed to load session: $e');
      if (mounted) setState(() => _isLoadingHistory = false);
      _sendMorganOpener();
    }
    _maybeSendInitialQuery();
  }

  Future<void> _startNewSession() async {
    final id = DateTime.now().toUtc().toIso8601String().replaceAll(':', '-');
    _sessionId = id;
    await _sessionsRef?.doc(id).set({
      'created_at': FieldValue.serverTimestamp(),
      'updated_at': FieldValue.serverTimestamp(),
      'messages':   [],
    });
    if (mounted) {
      setState(() {
        _messages.clear();
        _isLoadingHistory = false;
      });
    }
  }

  /// Insert Morgan's personalised opening message (no API call — generated locally).
  void _sendMorganOpener() {
    if (_ctx == null || _messages.isNotEmpty) return;
    final openerMsg = {
      'role': 'assistant',
      'content': _ctx!.openingMessage,
    };
    if (mounted) setState(() => _messages.add(openerMsg));
    _persistMessages([openerMsg]);
    _scrollToBottom();
  }

  void _maybeSendInitialQuery() {
    if (widget.initialQuery != null && widget.initialQuery!.isNotEmpty) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _send(widget.initialQuery!);
      });
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _scrollCtrl.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  Future<void> _pickGroupPhoto() async {
    final isMobile = Theme.of(context).platform == TargetPlatform.android ||
        Theme.of(context).platform == TargetPlatform.iOS;

    Uint8List? bytes;
    String? name;

    if (isMobile) {
      final picked = await ImagePicker().pickImage(
        source: ImageSource.gallery,
        maxWidth: 2048,
        imageQuality: 90,
      );
      if (picked == null) return;
      bytes = await picked.readAsBytes();
      name = picked.name;
    } else {
      final result = await FilePicker.pickFiles(
        type: FileType.image,
        withData: true,
        allowMultiple: false,
      );
      if (result == null || result.files.isEmpty) return;
      bytes = result.files.first.bytes;
      name = result.files.first.name;
    }

    if (bytes == null) return;
    setState(() {
      _pendingPhotoBytes = bytes;
      _pendingPhotoName = name ?? 'photo.jpg';
    });
  }

  Future<void> _sendGroupPhoto() async {
    final bytes = _pendingPhotoBytes!;
    final name = _pendingPhotoName ?? 'photo.jpg';
    final userMessage = _controller.text.trim().isNotEmpty
        ? _controller.text.trim()
        : 'I\'d like to add these coins to my collection.';

    setState(() {
      _pendingPhotoBytes = null;
      _pendingPhotoName = null;
      _controller.clear();
      _isIdentifyingPhoto = true;
      // Add user message with photo
      _messages.add({
        'role': 'user',
        'content': userMessage,
        'photo_bytes': bytes,
      });
      // Add Morgan thinking
      _messages.add({
        'role': 'assistant',
        'content': 'Let me take a look at your coins...',
        'is_loading': true,
      });
    });
    _scrollToBottom();

    try {
      final idToken = await FirebaseAuth.instance.currentUser?.getIdToken();
      final uri = Uri.parse('$kApiBaseUrl/api/identify_group_photo');
      final request = http.MultipartRequest('POST', uri);
      request.headers['Authorization'] = 'Bearer $idToken';
      request.fields['user_email'] = AuthService.userEmail;
      request.fields['message'] = userMessage;
      request.files.add(http.MultipartFile.fromBytes(
        'image',
        bytes,
        filename: name,
        contentType: MediaType('image', name.split('.').last.toLowerCase()),
      ));

      final streamedResponse = await request.send().timeout(const Duration(seconds: 90));
      final responseBody = await streamedResponse.stream.bytesToString();
      final data = jsonDecode(responseBody) as Map<String, dynamic>;

      if (!mounted) return;

      setState(() {
        _isIdentifyingPhoto = false;
        // Remove the loading message
        _messages.removeWhere((m) => m['is_loading'] == true);

        if (data['error'] != null) {
          _messages.add({
            'role': 'assistant',
            'content': 'I had trouble reading that photo. Could you try again with better lighting?',
          });
        } else {
          final coinCount = data['coin_count'] ?? 0;
          final grouped = data['appears_grouped'] == true;
          final groupName = data['suggested_group_name'] ?? 'Coin Set';

          String morganText;
          if (coinCount == 0) {
            morganText = 'I couldn\'t make out any coins in that photo. Could you try a clearer image?';
          } else if (coinCount == 1) {
            final coin = data['coins'][0];
            morganText = 'I found one coin — a ${coin["year"]}${coin["mint_mark"]?.isNotEmpty == true ? "-" + coin["mint_mark"] : ""} ${coin["denomination"]}. Would you like to add it to your collection?';
          } else if (grouped) {
            morganText = 'I found $coinCount coins in your photo! They look like they\'re together in one holder.\n\nSave as "$groupName"?';
          } else {
            morganText = 'I found $coinCount coins in your photo. Would you like to save them?';
          }

          _messages.add({
            'role': 'assistant',
            'content': morganText,
            'action_payload': {
              'action': 'group_photo_proposal',
              ...data,
            },
          });
        }
      });
      _scrollToBottom();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isIdentifyingPhoto = false;
        _messages.removeWhere((m) => m['is_loading'] == true);
        _messages.add({
          'role': 'assistant',
          'content': 'Something went wrong while scanning your photo. Please try again.',
        });
      });
    }
  }

  Future<void> _send(String query) async {
    final rawQuery = query.trim();
    if (rawQuery.isEmpty) return;

    // Check if previous assistant message was a clarifying question (e.g., asking for mint mark)
    String effectiveQuery = rawQuery;
    if (_messages.isNotEmpty && _messages.last['role'] == 'assistant') {
      final lastAssistantText = _messages.last['content'] ?? '';
      if (rawQuery.length <= 4 && (lastAssistantText.contains('mint') || lastAssistantText.contains('grade') || lastAssistantText.contains('year'))) {
        effectiveQuery = 'Clarification response: "$rawQuery" (in response to: "$lastAssistantText")';
      }
    }

    final userMsg = {'role': 'user', 'content': rawQuery};
    setState(() {
      _messages.add(userMsg);
      _isLoading = true;
    });
    _controller.clear();
    _scrollToBottom();

    final recentHistory = _messages.length > 6 ? _messages.sublist(_messages.length - 6) : _messages;

    final user = FirebaseAuth.instance.currentUser;
    if (user == null) {
      setState(() {
        _messages.add({
          'role': 'assistant',
          'content': 'You need to sign in again to chat with me. Please sign in and try again.',
        });
        _isLoading = false;
      });
      return;
    }

    final idToken = await user.getIdToken();
    if (idToken == null) {
      setState(() {
        _messages.add({
          'role': 'assistant',
          'content': 'Your session has expired. Please sign in again.',
        });
        _isLoading = false;
      });
      return;
    }

    try {
      final response = await http.post(
        Uri.parse('$kApiBaseUrl/api/deep_dive'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $idToken',
        },
        body: jsonEncode({
          'user_email':          AuthService.userEmail,
          'query':               effectiveQuery,
          'chat_history':        recentHistory,
          'collection_context':  _ctx?.systemPrompt ?? '',
          'user_name':           _displayName,
        }),
      );
      if (!mounted) return;

      String replyText;
      String? actionPayloadJson;
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        replyText = data['response'] ?? 'No response.';
        if (data['action_payload'] != null) {
          actionPayloadJson = jsonEncode(data['action_payload']);
        }
        if (data is Map &&
            data['error'] == null &&
            replyText.trim().isNotEmpty &&
            replyText != 'No response.') {
          BetaChecklistService.autoCompleteTask('task_18_ai_chat');
        }
      } else {
        replyText = 'Error ${response.statusCode}: please try again.';
      }

      final aiMsg = {
        'role': 'assistant',
        'content': replyText,
        // ignore: use_null_aware_elements
        if (actionPayloadJson != null) 'action_payload': actionPayloadJson,
      };
      setState(() {
        _messages.add(aiMsg);
        _isLoading = false;
      });
      _persistMessages([userMsg, aiMsg]);
    } catch (e) {
      if (!mounted) return;
      final errorMsg = {
        'role': 'assistant',
        'content':
            'I couldn\'t reach the server just now — please check your connection and try again.',
      };
      setState(() {
        _messages.add(errorMsg);
        _isLoading = false;
      });
      _persistMessages([userMsg, errorMsg]);
    }
    _scrollToBottom();
  }

  void _persistMessages(List<Map<String, dynamic>> newMsgs) {
    if (AuthService.isGuest || _currentSessionRef == null) return;
    _currentSessionRef!.update({
      'messages':     FieldValue.arrayUnion(newMsgs),
      'updated_at':   FieldValue.serverTimestamp(),
      'last_preview': newMsgs.last['content']?.toString().substring(
              0, newMsgs.last['content'].toString().length.clamp(0, 80)) ??
          '',
    }).catchError((e) => debugPrint('[AiChat] Persist error: $e'));
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollCtrl.hasClients) {
        _scrollCtrl.animateTo(
          _scrollCtrl.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _onNewChat() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: _surf,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('Start a new chat?',
            style: TextStyle(color: _textPrimary, fontWeight: FontWeight.bold)),
        content: Text(
          'I\'ll remember your collection, but this conversation will start fresh.',
          style: TextStyle(color: _sub, fontSize: 14, height: 1.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text('Cancel', style: TextStyle(color: _sub)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: _teal,
              foregroundColor: Colors.black87,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10)),
            ),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('New Chat'),
          ),
        ],
      ),
    );
    if (confirm == true && mounted) {
      setState(() => _isLoadingHistory = true);
      await _startNewSession();
      _sendMorganOpener();
    }
  }

  // ── Context-aware suggestion pills ───────────────────────────────────────
  List<String> get _suggestions {
    if (_ctx == null || _ctx!.isEmpty) {
      return [
        'How do I add my first coin?',
        'What makes coins valuable?',
        'What is a Morgan Silver Dollar?',
        'How does the Microscope work?',
      ];
    }
    final topCoin = _ctx!.topCoinsByValue.isNotEmpty
        ? _ctx!.topCoinsByValue.first.split(' — ').first
        : null;
    return [
      'What is my most valuable coin?',
      if (topCoin != null) 'Tell me more about my $topCoin',
      'How much profit have I made?',
      if (_ctx!.metals.isNotEmpty) 'How much ${_ctx!.metals.first.toLowerCase()} do I own?',
      'What should I add next to my collection?',
      'Which of my coins should I sell?',
      'Summarise my whole collection',
    ];
  }

  // ── Build ─────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return Container(
      color: _bg,
      child: Column(
        children: [
          _buildHeader(),
          if (!widget.isMinimized) ...[
            if (_isLoadingHistory || _isLoadingContext)
              LinearProgressIndicator(
                color: _teal, backgroundColor: _surf, minHeight: 2),

            // Suggestion pills (empty state)
            if (_messages.isEmpty && !_isLoadingHistory && !_isLoadingContext)
              _buildSuggestions(),

            // Message list
            Expanded(child: _buildMessageList()),

            // Input bar
            _buildInputBar(),
          ],
        ],
      ),
    );
  }

  // ── Header ────────────────────────────────────────────────────────────────
  Widget _buildHeader() {
    final dragHandle = Expanded(
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onPanUpdate: widget.onDragUpdate,
        onPanEnd: (_) => widget.onDragEnd?.call(),
        child: Row(
          children: [
            if (widget.isPopout)
              Padding(
                padding: EdgeInsets.only(right: 8),
                child: Icon(Icons.drag_indicator_rounded, color: _teal, size: 18),
              ),
            // Morgan owl avatar
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: const LinearGradient(
                  colors: [Color(0xFFD4A843), Color(0xFF8B6914)],
                ),
                border: Border.all(color: _teal.withAlpha(100), width: 1.5),
              ),
              child: ClipOval(
                child: Image.asset(
                  'assets/morgan_avatar.png',
                  fit: BoxFit.cover,
                  errorBuilder: (ctx, err, stack) => const Icon(
                      Icons.smart_toy_rounded,
                      color: Color(0xFF2DD4BF),
                      size: 20),
                ),
              ),
            ),
            SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Ask Morgan',
                    style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: _textPrimary),
                  ),
                  Text(
                    _isLoadingContext
                        ? 'Loading your collection…'
                        : _ctx == null || _ctx!.isEmpty
                            ? 'Your personal numismatic guide'
                            : '${_ctx!.totalCoins} coins · \$${_ctx!.portfolioValue.toStringAsFixed(2)}',
                    style: TextStyle(color: _sub, fontSize: 11),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );

    return Container(
      padding: const EdgeInsets.fromLTRB(16, 14, 8, 10),
      decoration: BoxDecoration(
        color: _surf,
        border: Border(bottom: BorderSide(color: _gold.withAlpha(50))),
      ),
      child: Row(
        children: [
          dragHandle,
          // Settings
          if (!widget.isMinimized)
            IconButton(
              icon: Icon(Icons.tune_rounded, color: _sub, size: 20),
              tooltip: 'Morgan settings',
              onPressed: () async {
                final changed = await showMorganSettings(context);
                if (changed && mounted) {
                  final name = await MorganPrefs.getDisplayName();
                  final ctx  = await MorganChatContextService.load(forceRefresh: true);
                  setState(() {
                    _displayName = name;
                    _ctx = ctx;
                  });
                }
              },
            ),
          // Refresh context
          if (!widget.isMinimized)
            IconButton(
              icon: Icon(Icons.refresh_rounded, color: _sub, size: 20),
              tooltip: 'Refresh collection data',
              onPressed: () async {
                MorganChatContextService.invalidate();
                final ctx = await MorganChatContextService.load(forceRefresh: true);
                if (mounted) setState(() => _ctx = ctx);
              },
            ),
          // New chat
          if (!widget.isMinimized)
            IconButton(
              icon: Icon(Icons.add_comment_outlined, color: _sub, size: 20),
              tooltip: 'New chat',
              onPressed: _isLoading ? null : _onNewChat,
            ),
          if (widget.isPopout && widget.onMinimize != null)
            IconButton(
              icon: Icon(
                widget.isMinimized ? Icons.open_in_full_rounded : Icons.remove_rounded,
                color: _sub,
                size: 20,
              ),
              tooltip: widget.isMinimized ? 'Restore chat' : 'Minimize chat',
              onPressed: widget.onMinimize,
            ),
          if (widget.isPopout && widget.onClose != null)
            IconButton(
              icon: Icon(Icons.close_rounded, color: _sub, size: 20),
              tooltip: 'Close chat',
              onPressed: widget.onClose,
            ),
        ],
      ),
    );
  }

  // ── Suggestion pills ──────────────────────────────────────────────────────
  Widget _buildSuggestions() {
    return Container(
      color: _bg,
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            _ctx != null && !_ctx!.isEmpty
                ? 'Hi $_displayName! Try asking:'
                : 'Try asking:',
            style: TextStyle(
                color: _sub, fontSize: 13, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _suggestions.map(_pill).toList(),
          ),
        ],
      ),
    );
  }

  // ── Message list ──────────────────────────────────────────────────────────
  Widget _buildMessageList() {
    return ListView.builder(
      controller: _scrollCtrl,
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
      itemCount: _messages.length + (_isLoading ? 1 : 0),
      itemBuilder: (ctx, i) {
        // Typing indicator
        if (_isLoading && i == _messages.length) {
          return _typingIndicator();
        }
        final msg    = _messages[i];
        final isUser = msg['role'] == 'user';
        return _messageBubble(msg: msg, isUser: isUser);
      },
    );
  }

  Widget _buildConfirmationCard(Map<String, dynamic> payload) {
    final year = payload['year'] ?? '';
    final denom = payload['denomination'] ?? '';
    final mint = payload['mint_mark'] ?? '';
    final storage = payload['storage_location'] ?? 'Binder';
    final condition = payload['condition'] ?? 'Ungraded';
    final coinId = payload['coin_id'] ?? '';
    final isDupe = payload['is_duplicate'] == true;
    final promptExtra = payload['prompt_extra_details'] == true;

    return Container(
      margin: const EdgeInsets.only(top: 10, bottom: 4),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).brightness == Brightness.dark ? const Color(0xFF0F172A) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _teal.withAlpha(120), width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.check_circle_rounded, color: _teal, size: 20),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Added to Binder: $year${mint.isNotEmpty ? "-$mint" : ""} $denom',
                  style: TextStyle(
                      color: _textPrimary, fontWeight: FontWeight.bold, fontSize: 13),
                ),
              ),
              if (isDupe)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                      color: Colors.amber.withAlpha(50),
                      borderRadius: BorderRadius.circular(4)),
                  child: const Text('Duplicate',
                      style: TextStyle(
                          color: Colors.amber, fontSize: 10, fontWeight: FontWeight.bold)),
                ),
            ],
          ),
          SizedBox(height: 6),
          Text('Storage: $storage  •  Condition: $condition',
              style: TextStyle(color: _sub, fontSize: 11)),
          SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              TextButton.icon(
                onPressed: () => _send('INTERNAL_UNDO:$coinId'),
                icon: const Icon(Icons.undo, size: 14, color: Colors.redAccent),
                label: const Text('Undo',
                    style: TextStyle(color: Colors.redAccent, fontSize: 12)),
              ),
              Row(
                children: [
                  if (promptExtra) ...[
                    OutlinedButton(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: _teal,
                        side: BorderSide(color: _teal),
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        textStyle: const TextStyle(fontSize: 11),
                      ),
                      onPressed: () {
                        final targetId = coinId.isNotEmpty ? " for coin_id:$coinId" : "";
                        _send("I'd like to add details now$targetId");
                      },
                      child: const Text('Add Details Now'),
                    ),
                    const SizedBox(width: 6),
                  ],
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _teal,
                      foregroundColor: Colors.black,
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      textStyle:
                          const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                    onPressed: () {
                      if (widget.onNavigateToCollection != null) {
                        widget.onNavigateToCollection!();
                      } else if (Navigator.canPop(context)) {
                        Navigator.pop(context);
                      }
                    },
                    icon: const Icon(Icons.collections_bookmark, size: 14),
                    label: const Text('View Binder'),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _messageBubble({required Map<String, dynamic> msg, required bool isUser}) {
    final content = msg['content']?.toString() ?? '';
    final Uint8List? photoBytes = msg['photo_bytes'] as Uint8List?;
    
    Map<String, dynamic>? payload;
    if (msg['action_payload'] != null) {
      try {
        if (msg['action_payload'] is String) {
          payload = jsonDecode(msg['action_payload']) as Map<String, dynamic>;
        } else {
          payload = msg['action_payload'] as Map<String, dynamic>;
        }
      } catch (_) {}
    }

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(top: 6, bottom: 4),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        constraints:
            BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.80),
        decoration: BoxDecoration(
          color: isUser ? _userBubble : _aiBubble,
          borderRadius: BorderRadius.only(
            topLeft:     const Radius.circular(16),
            topRight:    const Radius.circular(16),
            bottomLeft:  Radius.circular(isUser ? 16 : 4),
            bottomRight: Radius.circular(isUser ? 4  : 16),
          ),
          border: isUser
              ? Border.all(color: _teal.withAlpha(60), width: 1)
              : Border.all(color: _textPrimary.withAlpha(15), width: 1),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (!isUser)
              Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Container(
                          width: 16, height: 16,
                          decoration: const BoxDecoration(
                            shape: BoxShape.circle,
                            gradient: LinearGradient(
                              colors: [Color(0xFFD4A843), Color(0xFF8B6914)],
                            ),
                          ),
                          child: const Icon(Icons.smart_toy_rounded,
                              color: Colors.white, size: 9),
                        ),
                        const SizedBox(width: 5),
                        const Text('Morgan',
                            style: TextStyle(
                                color: _gold,
                                fontSize: 11,
                                fontWeight: FontWeight.w600)),
                      ],
                    ),
                    InkWell(
                      onTap: () {
                        TtsVoiceService.toggleSpeak(content, onStateChange: () {
                          if (mounted) setState(() {});
                        });
                      },
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              TtsVoiceService.isPlaying && TtsVoiceService.currentlySpeakingText == content
                                  ? Icons.stop_circle_outlined
                                  : Icons.volume_up_outlined,
                              color: _teal,
                              size: 15,
                            ),
                            SizedBox(width: 3),
                            Text(
                              TtsVoiceService.isPlaying && TtsVoiceService.currentlySpeakingText == content
                                  ? 'Stop'
                                  : 'Listen',
                              style: TextStyle(
                                  color: _teal, fontSize: 11, fontWeight: FontWeight.w500),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            if (photoBytes != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.memory(
                    photoBytes,
                    width: 200,
                    height: 200,
                    fit: BoxFit.cover,
                  ),
                ),
              ),
            Text(
              content,
              style: TextStyle(
                  fontSize: 15,
                  color: isUser ? _textPrimary : _textPrimary.withAlpha(230),
                  height: 1.55),
            ),
            if (payload != null && payload['action'] == 'add_coin')
              _buildConfirmationCard(payload),
            if (payload != null && payload['action'] == 'group_photo_proposal')
              _buildGroupProposalCard(payload),
            if (payload != null && payload['action'] == 'group_photo_success')
              _buildGroupSuccessCard(payload),
          ],
        ),
      ),
    );
  }

  Widget _buildGroupSuccessCard(Map<String, dynamic> payload) {
    final coinIds = List<String>.from(payload['coin_ids'] ?? []);
    final isSet = payload['is_set'] == true;
    final setId = payload['set_id'];
    final photoUrl = payload['photo_url'];

    return Container(
      margin: const EdgeInsets.only(top: 10, bottom: 4),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).brightness == Brightness.dark ? const Color(0xFF0F172A) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _teal.withAlpha(120), width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.check_circle_rounded, color: _teal, size: 20),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  isSet ? 'Saved as Set (${coinIds.length} coins)' : 'Saved ${coinIds.length} coins separately',
                  style: TextStyle(
                      color: _textPrimary, fontWeight: FontWeight.bold, fontSize: 13),
                ),
              ),
            ],
          ),
          SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              TextButton.icon(
                onPressed: () => _undoGroupPhoto(coinIds, isSet ? setId : null, photoUrl),
                icon: const Icon(Icons.undo, size: 14, color: Colors.redAccent),
                label: const Text('Undo All',
                    style: TextStyle(color: Colors.redAccent, fontSize: 12)),
              ),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: _teal,
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  textStyle:
                      const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                ),
                onPressed: () {
                  if (widget.onNavigateToCollection != null) {
                    widget.onNavigateToCollection!();
                  } else if (Navigator.canPop(context)) {
                    Navigator.pop(context);
                  }
                },
                icon: const Icon(Icons.collections_bookmark, size: 14),
                label: const Text('View Binder'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Future<void> _undoGroupPhoto(List<String> coinIds, String? setId, String? photoUrl) async {
    setState(() {
      _messages.add({
        'role': 'assistant',
        'content': 'Undoing...',
        'is_loading': true,
      });
    });
    _scrollToBottom();

    // 1. Ungroup Set (with preservePhotosOnChildren: false to clean up GCS)
    if (setId != null) {
      try {
        await SetGroupingService.ungroupSet(
          parentSetDocId: setId, 
          deleteOwnerPhotos: true,
          preservePhotosOnChildren: false,
        );
      } catch (e) {
        debugPrint('Ungroup set failed or already deleted: $e');
      }
    }

    // 2. Delete individual coin docs
    final userEmail = AuthService.userEmail;
    for (final cid in coinIds) {
      try {
        await FirebaseFirestore.instance
            .collection('users')
            .doc(userEmail)
            .collection('coins')
            .doc(cid)
            .delete();
      } catch (e) {
        debugPrint('Failed to delete child coin $cid: $e');
      }
    }

    // 3. Delete the GCS group photo
    if (photoUrl != null && photoUrl.toString().isNotEmpty) {
      try {
        if (photoUrl.startsWith('gs://') || photoUrl.startsWith('http')) {
          await FirebaseStorage.instance.refFromURL(photoUrl).delete();
        } else {
          // It's a storage path like 'users/email/group_photos/uuid.jpg'
          await FirebaseStorage.instance.ref(photoUrl).delete();
        }
      } on FirebaseException catch (e) {
        if (e.code == 'object-not-found') {
          debugPrint('Group photo already deleted or not found (treated as success).');
        } else {
          debugPrint('FirebaseException deleting group photo: $e');
        }
      } catch (e) {
        debugPrint('Error deleting group photo: $e');
      }
    }

    if (!mounted) return;
    setState(() {
      _messages.removeWhere((m) => m['is_loading'] == true);
      _messages.add({
        'role': 'assistant',
        'content': 'Undo complete. Removed ${coinIds.length} coins and the set.',
      });
    });
    _scrollToBottom();
  }

  Widget _buildGroupProposalCard(Map<String, dynamic> payload) {
    final coins = payload['coins'] as List? ?? [];
    if (coins.isEmpty) return const SizedBox.shrink();

    final groupName = payload['suggested_group_name'] ?? 'Coin Set';
    final grouped = payload['appears_grouped'] == true;

    return Container(
      margin: const EdgeInsets.only(top: 10, bottom: 4),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).brightness == Brightness.dark ? const Color(0xFF0F172A) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _teal.withAlpha(120), width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.collections, color: _teal, size: 20),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Identified ${coins.length} coins',
                  style: TextStyle(
                      color: _textPrimary, fontWeight: FontWeight.bold, fontSize: 13),
                ),
              ),
            ],
          ),
          SizedBox(height: 10),
          ...coins.map((c) => Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Text('• ${c["year"]}${c["mint_mark"]?.isNotEmpty == true ? "-" + c["mint_mark"] : ""} ${c["denomination"]}',
                style: TextStyle(color: _sub, fontSize: 12)),
          )).toList(),
          SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              if (grouped)
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _teal,
                    foregroundColor: Colors.black,
                    textStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                  ),
                  onPressed: () => _showGroupInfoForm(payload, true, groupName),
                  child: Text('Save as "$groupName"'),
                ),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: grouped ? _surf : _teal,
                  foregroundColor: grouped ? _teal : Colors.black,
                  side: grouped ? BorderSide(color: _teal) : null,
                  textStyle: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                ),
                onPressed: () => _showGroupInfoForm(payload, false, null),
                child: const Text('Save separately'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  void _showGroupInfoForm(Map<String, dynamic> payload, bool saveAsSet, String? defaultSetName) {
    String price = '';
    String date = '';
    String wherePurchased = '';
    String storage = '';
    bool enterPerCoin = false;

    final List coins = payload['coins'] ?? [];
    final bool anyMissingMintMark = coins.any((c) => c['mint_mark_visible'] == false);
    final visibleMintMarkCoin = coins.cast<Map<String,dynamic>>().firstWhere(
      (c) => c['mint_mark_visible'] == true && (c['mint_mark'] ?? '').toString().isNotEmpty, 
      orElse: () => <String, dynamic>{}
    );
    final String visibleMm = visibleMintMarkCoin.isNotEmpty ? (visibleMintMarkCoin['mint_mark']?.toString() ?? '') : '';
    final String visibleDenom = visibleMintMarkCoin.isNotEmpty ? (visibleMintMarkCoin['denomination']?.toString() ?? 'coin') : '';
    
    String mintMarkQuestion = "Your photo shows the fronts.";
    if (visibleMm.isNotEmpty) {
      String mmName = visibleMm == 'D' ? ' (Denver)' : (visibleMm == 'S' ? ' (San Francisco)' : (visibleMm == 'P' ? ' (Philadelphia)' : (visibleMm == 'W' ? ' (West Point)' : '')));
      mintMarkQuestion += " The $visibleDenom shows a $visibleMm. Are all ${coins.length} coins $visibleMm$mmName?";
    } else {
      mintMarkQuestion += " We couldn't see the mint marks. Are they all the same?";
    }

    List<String> mmOptions = [];
    if (visibleMm.isNotEmpty) mmOptions.add('All $visibleMm');
    mmOptions.add('Let me set each');
    mmOptions.add('Not sure / Skip');
    String bulkMintMarkOption = 'Not sure / Skip';

    showDialog(
      context: context,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              backgroundColor: _surf,
              title: const Text('Collection Details'),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    if (anyMissingMintMark) ...[
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.amber.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.amber),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(mintMarkQuestion, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                            const SizedBox(height: 8),
                            DropdownButton<String>(
                              value: bulkMintMarkOption,
                              isExpanded: true,
                              items: mmOptions.map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(),
                              onChanged: (val) {
                                if (val != null) {
                                  setDialogState(() => bulkMintMarkOption = val);
                                }
                              },
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),
                    ],
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            decoration: const InputDecoration(labelText: 'Total Price Paid (\$)'),
                            keyboardType: TextInputType.number,
                            onChanged: (val) => price = val,
                          ),
                        ),
                        if (saveAsSet) ...[
                          const SizedBox(width: 8),
                          Column(
                            children: [
                              const Text('Per coin?', style: TextStyle(fontSize: 10)),
                              Switch(
                                value: enterPerCoin,
                                onChanged: (val) => setDialogState(() => enterPerCoin = val),
                                activeColor: _teal,
                              ),
                            ],
                          )
                        ],
                      ],
                    ),
                    TextField(
                      decoration: const InputDecoration(labelText: 'Purchase Date (YYYY-MM-DD)'),
                      onChanged: (val) => date = val,
                    ),
                    TextField(
                      decoration: const InputDecoration(labelText: 'Where Purchased (Optional)'),
                      onChanged: (val) => wherePurchased = val,
                    ),
                    TextField(
                      decoration: const InputDecoration(
                        labelText: 'Storage Location',
                        hintText: 'Where will your family find these?',
                      ),
                      onChanged: (val) => storage = val,
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () {
                    Navigator.pop(ctx);
                    _commitGroupPhoto(payload, saveAsSet, defaultSetName, {}, skip: true);
                  },
                  child: const Text('Skip All'),
                ),
                ElevatedButton(
                  onPressed: () {
                    Navigator.pop(ctx);
                    if (bulkMintMarkOption.startsWith('All ') && visibleMm.isNotEmpty) {
                      for (var c in payload['coins']) {
                        c['mint_mark'] = visibleMm;
                      }
                    }
                    final formDetails = {
                      'price': price,
                      'date': date,
                      'where_purchased': wherePurchased,
                      'storage': storage,
                      'per_coin_price': enterPerCoin,
                    };
                    _commitGroupPhoto(payload, saveAsSet, defaultSetName, formDetails, skip: false);
                  },
                  child: const Text('Save'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _commitGroupPhoto(
    Map<String, dynamic> payload,
    bool saveAsSet,
    String? setName,
    Map<String, dynamic> formDetails, {
    required bool skip
  }) async {
    setState(() {
      _messages.add({
        'role': 'assistant',
        'content': 'Saving your coins...',
        'is_loading': true,
      });
    });
    _scrollToBottom();

    try {
      final idToken = await FirebaseAuth.instance.currentUser?.getIdToken();
      
      final response = await http.post(
        Uri.parse('$kApiBaseUrl/api/commit_group_photo'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $idToken',
        },
        body: jsonEncode({
          'user_email': AuthService.userEmail,
          'coins': (payload['coins'] as List).map((c) => {
            'year': c['year']?.toString() ?? '',
            'denomination': c['denomination']?.toString() ?? '',
            'mint_mark': c['mint_mark']?.toString() ?? '',
            'program_series': c['program_series']?.toString() ?? '',
            'theme_subject': c['theme_subject']?.toString() ?? '',
            'condition': c['condition']?.toString() ?? '',
            'metal_content': c['metal_content']?.toString() ?? '',
          }).toList(),
          'set_title': setName,
          'cost_total': formDetails['cost'] ?? '',
          'cost_per_coin': formDetails['cost_per_coin'] == true,
          'purchase_date': formDetails['date'] ?? '',
          'where_purchased': formDetails['where_purchased'] ?? '',
          'storage_location': formDetails['storage_location'] ?? '',
          'original_photo_gcs_path': payload['original_photo_gcs_path'] ?? '',
          'original_photo_url': payload['original_photo_url'] ?? '',
        }),
      );

      if (!mounted) return;
      setState(() => _messages.removeWhere((m) => m['is_loading'] == true));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final coinIds = List<String>.from(data['coin_ids'] ?? []);
        final photoUrl = data['original_photo_url']?.toString() ?? '';
        final gcsPath = data['original_photo_gcs_path']?.toString() ?? '';
        String? setId;

        if (saveAsSet && coinIds.length >= 2 && setName != null) {
          setId = await SetGroupingService.linkCoinsAsSet(
            coinIds: coinIds,
            setTitle: setName,
            storageLocation: formDetails['storage_location']?.toString(),
          );
          // Attach original photo as owner photo on the set parent doc (L8)
          if (setId.isNotEmpty && photoUrl.isNotEmpty) {
            final userEmail = AuthService.userEmail;
            final docRef = FirebaseFirestore.instance
                .collection('users').doc(userEmail).collection('coins').doc(setId);
            await docRef.update({
              'owner_photos': [
                {
                  'id': DateTime.now().millisecondsSinceEpoch.toRadixString(36),
                  'url': photoUrl,
                  'storage_path': gcsPath,
                  'caption': setName,
                  'added_at': DateTime.now().toIso8601String(),
                }
              ],
            });
          }
        }
        
        setState(() {
          _messages.add({
            'role': 'assistant',
            'content': 'Successfully saved ${coinIds.length} coins!',
            'action_payload': {
              'action': 'group_photo_success',
              'coin_ids': coinIds,
              'set_id': setId,
              'is_set': saveAsSet,
              'photo_url': photoUrl,
            },
          });
        });
      } else {
        setState(() {
          _messages.add({
            'role': 'assistant',
            'content': 'Sorry, there was an error saving your coins.',
          });
        });
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _messages.removeWhere((m) => m['is_loading'] == true);
        _messages.add({
          'role': 'assistant',
          'content': 'Network error while saving coins.',
        });
      });
    }
  }

  Widget _typingIndicator() {
    return Align(
      alignment: Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(top: 6, bottom: 4),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
        decoration: BoxDecoration(
          color: _aiBubble,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: _textPrimary.withAlpha(15)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Morgan is thinking',
                style: TextStyle(color: _sub, fontSize: 13)),
            SizedBox(width: 8),
            SizedBox(
              width: 32, height: 10,
              child: LinearProgressIndicator(
                  color: _teal,
                  backgroundColor: _surf,
                  borderRadius: BorderRadius.circular(4)),
            ),
          ],
        ),
      ),
    );
  }

  // ── Input bar ─────────────────────────────────────────────────────────────
  Widget _buildInputBar() {
    return Container(
      padding: const EdgeInsets.fromLTRB(12, 8, 12, 8),
      decoration: BoxDecoration(
        color: _surf,
        border: Border(top: BorderSide(color: _gold.withAlpha(40))),
      ),
      child: SafeArea(
        top: false,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Tap-friendly Mint Mark Chips
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  Text('Mint Marks: ', style: TextStyle(color: _sub, fontSize: 11, fontWeight: FontWeight.w600)),
                  const SizedBox(width: 4),
                  _mintChip('Philadelphia (P)', 'P'),
                  _mintChip('Denver (D)', 'D'),
                  _mintChip('San Francisco (S)', 'S'),
                  _mintChip('Carson City (CC)', 'CC'),
                  _mintChip('New Orleans (O)', 'O'),
                ],
              ),
            ),
            if (_pendingPhotoBytes != null)
              Container(
                margin: const EdgeInsets.only(bottom: 8),
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: _bg,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: _teal.withAlpha(60)),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: Image.memory(
                        _pendingPhotoBytes!,
                        width: 40,
                        height: 40,
                        fit: BoxFit.cover,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _pendingPhotoName ?? 'Photo attached',
                        style: TextStyle(color: _textPrimary, fontSize: 13),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    IconButton(
                      icon: Icon(Icons.close, color: _sub, size: 18),
                      onPressed: () {
                        setState(() {
                          _pendingPhotoBytes = null;
                          _pendingPhotoName = null;
                        });
                      },
                    ),
                  ],
                ),
              ),
            Row(children: [
              IconButton(
                icon: Icon(Icons.attach_file, color: _sub),
                onPressed: _isLoading || _isIdentifyingPhoto ? null : _pickGroupPhoto,
              ),
              Expanded(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  decoration: BoxDecoration(
                    color: _bg,
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: _teal.withAlpha(60)),
                  ),
                  child: TextField(
                    controller: _controller,
                    focusNode: _focusNode,
                    spellCheckConfiguration: const SpellCheckConfiguration(),
                    autocorrect: true,
                    enableSuggestions: true,
                    style: TextStyle(color: _textPrimary, fontSize: 15),
                    decoration: InputDecoration(
                      hintText: 'Ask Morgan about your collection…',
                      hintStyle: TextStyle(color: _sub.withAlpha(160), fontSize: 14),
                      border: InputBorder.none,
                      contentPadding: const EdgeInsets.symmetric(vertical: 13),
                    ),
                    onSubmitted: (val) {
                      if (_pendingPhotoBytes != null) {
                        _sendGroupPhoto();
                      } else {
                        _send(val);
                      }
                    },
                    textInputAction: TextInputAction.send,
                    maxLines: null,
                    textCapitalization: TextCapitalization.sentences,
                  ),
                ),
              ),
              SizedBox(width: 8),
              GestureDetector(
                onTap: _isLoading || _isIdentifyingPhoto
                    ? null
                    : () {
                        if (_pendingPhotoBytes != null) {
                          _sendGroupPhoto();
                        } else {
                          _send(_controller.text);
                        }
                      },
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 150),
                  width: 48, height: 48,
                  decoration: BoxDecoration(
                    color: _isLoading || _isIdentifyingPhoto ? _surf : _teal,
                    shape: BoxShape.circle,
                    border: Border.all(
                        color: _isLoading || _isIdentifyingPhoto
                            ? Colors.transparent
                            : _teal.withAlpha(200),
                        width: 1.5),
                  ),
                  child: Icon(
                    _isLoading || _isIdentifyingPhoto ? Icons.hourglass_bottom_rounded : Icons.send_rounded,
                    color: _isLoading || _isIdentifyingPhoto ? _sub : Colors.black87,
                    size: 20,
                  ),
                ),
              ),
            ]),
          ],
        ),
      ),
    );
  }

  Widget _mintChip(String label, String code) => Padding(
    padding: const EdgeInsets.only(right: 6),
    child: InkWell(
      onTap: () {
        _controller.text = code;
        _send(code);
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(
          color: _bg,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: _teal.withAlpha(80)),
        ),
        child: Text(label, style: TextStyle(color: _teal, fontSize: 11, fontWeight: FontWeight.bold)),
      ),
    ),
  );

  Widget _pill(String label) => GestureDetector(
    onTap: () => _send(label),
    child: Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
      decoration: BoxDecoration(
        color: _surf,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _teal.withAlpha(80)),
      ),
      child: Text(label,
          style: TextStyle(
              fontSize: 13,
              color: _textPrimary)),
    ),
  );
}
