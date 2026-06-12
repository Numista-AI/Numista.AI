import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'dart:convert';
import '../services/auth_service.dart';
import '../services/morgan_prefs.dart';
import '../services/morgan_chat_context.dart';
import '../widgets/morgan_settings_panel.dart';
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
  const AiChatScreen({super.key, this.initialQuery});

  @override
  State<AiChatScreen> createState() => _AiChatScreenState();
}

class _AiChatScreenState extends State<AiChatScreen> {
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollCtrl = ScrollController();
  final List<Map<String, String>> _messages = [];

  bool _isLoading = false;
  bool _isLoadingHistory = true;
  bool _isLoadingContext = true;
  String? _sessionId;
  MorganCollectionContext? _ctx;
  String _displayName = 'there';

  // ── Morgan colour palette ────────────────────────────────────────────────
  static const _bg    = Color(0xFF0B1220);   // deep navy
  static const _surf  = Color(0xFF162033);   // surface
  static const _teal  = Color(0xFF2DD4BF);   // Morgan teal
  static const _gold  = Color(0xFFD4A843);   // Morgan gold
  static const _sub   = Color(0xFF94A3B8);   // slate sub-text
  static const _userBubble = Color(0xFF1E4D4D); // dark teal for user
  static const _aiBubble   = Color(0xFF162033); // surface for Morgan

  // ── Firestore session path ───────────────────────────────────────────────
  CollectionReference? get _sessionsRef {
    final user = FirebaseAuth.instance.currentUser;
    if (user?.email == null) return null;
    return FirebaseFirestore.instance
        .collection('users')
        .doc(user!.email)
        .collection('ai_chat_sessions');
  }

  DocumentReference? get _currentSessionRef =>
      _sessionId == null ? null : _sessionsRef?.doc(_sessionId);

  @override
  void initState() {
    super.initState();
    _loadEverything();
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
            _messages.addAll(loaded.cast<Map<String, String>>());
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
    super.dispose();
  }

  Future<void> _send(String query) async {
    if (query.trim().isEmpty) return;

    final userMsg = {'role': 'user', 'content': query.trim()};
    setState(() {
      _messages.add(userMsg);
      _isLoading = true;
    });
    _controller.clear();
    _scrollToBottom();

    try {
      final response = await http.post(
        Uri.parse(
            '$kApiBaseUrl/api/deep_dive'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_email':          AuthService.userEmail,
          'query':               query.trim(),
          'collection_context':  _ctx?.systemPrompt ?? '',
          'user_name':           _displayName,
        }),
      );
      if (!mounted) return;

      String replyText;
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        replyText = data['response'] ?? 'No response.';
      } else {
        replyText = 'Error ${response.statusCode}: please try again.';
      }

      final aiMsg = {'role': 'assistant', 'content': replyText};
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

  void _persistMessages(List<Map<String, String>> newMsgs) {
    if (AuthService.isGuest || _currentSessionRef == null) return;
    _currentSessionRef!.update({
      'messages':     FieldValue.arrayUnion(newMsgs),
      'updated_at':   FieldValue.serverTimestamp(),
      'last_preview': newMsgs.last['content']?.substring(
              0, newMsgs.last['content']!.length.clamp(0, 80)) ??
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
        title: const Text('Start a new chat?',
            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        content: const Text(
          'I\'ll remember your collection, but this conversation will start fresh.',
          style: TextStyle(color: _sub, fontSize: 14, height: 1.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel', style: TextStyle(color: _sub)),
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
      ),
    );
  }

  // ── Header ────────────────────────────────────────────────────────────────
  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 14, 8, 10),
      decoration: BoxDecoration(
        color: _surf,
        border: Border(bottom: BorderSide(color: _gold.withAlpha(50))),
      ),
      child: Row(
        children: [
          // Morgan owl avatar
          Container(
            width: 40,
            height: 40,
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
                    size: 22),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Ask Morgan',
                  style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.white),
                ),
                Text(
                  _isLoadingContext
                      ? 'Loading your collection…'
                      : _ctx == null || _ctx!.isEmpty
                          ? 'Your personal numismatic guide'
                          : '${_ctx!.totalCoins} coins · \$${_ctx!.portfolioValue.toStringAsFixed(2)} portfolio',
                  style: const TextStyle(color: _sub, fontSize: 12),
                ),
              ],
            ),
          ),
          // Settings
          IconButton(
            icon: const Icon(Icons.tune_rounded, color: _sub, size: 20),
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
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: _sub, size: 20),
            tooltip: 'Refresh collection data',
            onPressed: () async {
              MorganChatContextService.invalidate();
              final ctx = await MorganChatContextService.load(forceRefresh: true);
              if (mounted) setState(() => _ctx = ctx);
            },
          ),
          // New chat
          IconButton(
            icon: const Icon(Icons.add_comment_outlined, color: _sub, size: 20),
            tooltip: 'New chat',
            onPressed: _isLoading ? null : _onNewChat,
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
            style: const TextStyle(
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
        return _messageBubble(
            content: msg['content'] ?? '', isUser: isUser);
      },
    );
  }

  Widget _messageBubble({required String content, required bool isUser}) {
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
              : Border.all(color: Colors.white.withAlpha(15), width: 1),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (!isUser)
              Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Row(
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
              ),
            Text(
              content,
              style: TextStyle(
                  fontSize: 15,
                  color: isUser ? Colors.white : Colors.white.withAlpha(230),
                  height: 1.55),
            ),
          ],
        ),
      ),
    );
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
          border: Border.all(color: Colors.white.withAlpha(15)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('Morgan is thinking',
                style: TextStyle(color: _sub, fontSize: 13)),
            const SizedBox(width: 8),
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
        child: Row(children: [
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
                style: const TextStyle(color: Colors.white, fontSize: 15),
                decoration: InputDecoration(
                  hintText: 'Ask Morgan about your collection…',
                  hintStyle: TextStyle(color: _sub.withAlpha(160), fontSize: 14),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(vertical: 13),
                ),
                onSubmitted: _send,
                textInputAction: TextInputAction.send,
                maxLines: null,
                textCapitalization: TextCapitalization.sentences,
              ),
            ),
          ),
          const SizedBox(width: 8),
          GestureDetector(
            onTap: _isLoading ? null : () => _send(_controller.text),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 150),
              width: 48, height: 48,
              decoration: BoxDecoration(
                color: _isLoading ? _surf : _teal,
                shape: BoxShape.circle,
                border: Border.all(
                    color: _isLoading
                        ? Colors.transparent
                        : _teal.withAlpha(200),
                    width: 1.5),
              ),
              child: Icon(
                _isLoading ? Icons.hourglass_bottom_rounded : Icons.send_rounded,
                color: _isLoading ? _sub : Colors.black87,
                size: 20,
              ),
            ),
          ),
        ]),
      ),
    );
  }

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
          style: const TextStyle(
              fontSize: 13,
              color: Colors.white)),
    ),
  );
}
