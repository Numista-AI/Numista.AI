import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'dart:convert';
import '../services/auth_service.dart';

class AiChatScreen extends StatefulWidget {
  /// Optional pre-populated query. When provided, the chatbot auto-submits
  /// this question on load (e.g. from the "AI Deep Dive" button on a coin).
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
  String? _sessionId;

  static const _accent   = Color(0xFFF63366);
  static const _bg       = Color(0xFFF0F2F6);
  static const _border   = Color(0xFFE2E6E9);
  static const _text     = Color(0xFF31333F);
  static const _subtext  = Color(0xFF5A5C69);

  // ── Firestore session path ──────────────────────────────────────────────────
  CollectionReference? get _sessionsRef {
    final user = FirebaseAuth.instance.currentUser;
    if (user?.email == null) return null;
    return FirebaseFirestore.instance
        .collection('users')
        .doc(user!.email)
        .collection('ai_chat_sessions');
  }

  DocumentReference? get _currentSessionRef {
    if (_sessionId == null) return null;
    return _sessionsRef?.doc(_sessionId);
  }

  @override
  void initState() {
    super.initState();
    _loadOrCreateSession();
  }

  /// Load the most recent session, or create a new one if none exists.
  Future<void> _loadOrCreateSession() async {
    if (AuthService.isGuest) {
      // Guest mode: no persistence, just start fresh
      setState(() => _isLoadingHistory = false);
      _maybeSendInitialQuery();
      return;
    }

    try {
      final ref = _sessionsRef;
      if (ref == null) {
        setState(() => _isLoadingHistory = false);
        return;
      }

      // Find most recent session
      final snap = await ref
          .orderBy('updated_at', descending: true)
          .limit(1)
          .get();

      if (snap.docs.isNotEmpty && widget.initialQuery == null) {
        // Restore last session
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
        setState(() {
          _messages.addAll(loaded.cast<Map<String, String>>());
          _isLoadingHistory = false;
        });
        _scrollToBottom();
      } else {
        // Start a fresh session
        await _startNewSession();
      }
    } catch (e) {
      debugPrint('[AiChat] Failed to load session: $e');
      setState(() => _isLoadingHistory = false);
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
        Uri.parse('https://numista-backend-568985927038.us-central1.run.app/api/deep_dive'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'user_email': AuthService.userEmail,
          'query': query.trim(),
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

      // Persist to Firestore
      _persistMessages([userMsg, aiMsg]);
    } catch (e) {
      if (!mounted) return;
      final errorMsg = {'role': 'assistant', 'content': 'Failed to connect. Check your connection and try again.'};
      setState(() {
        _messages.add(errorMsg);
        _isLoading = false;
      });
      _persistMessages([userMsg, errorMsg]);
    }
    _scrollToBottom();
  }

  /// Appends new messages to the Firestore session document.
  void _persistMessages(List<Map<String, String>> newMsgs) {
    if (AuthService.isGuest || _currentSessionRef == null) return;
    _currentSessionRef!.update({
      'messages':   FieldValue.arrayUnion(newMsgs),
      'updated_at': FieldValue.serverTimestamp(),
      // Keep a trimmed preview of the last message for the session list
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
        backgroundColor: const Color(0xFF1A1D27),
        title: const Text('New Chat', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        content: const Text(
          'Start a fresh conversation? Your current chat history is saved and will be accessible next time.',
          style: TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel', style: TextStyle(color: Colors.white54)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: _accent,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('New Chat'),
          ),
        ],
      ),
    );
    if (confirm == true) {
      setState(() => _isLoadingHistory = true);
      await _startNewSession();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // ── Header ────────────────────────────────────────────────────────
        Container(
          width: double.infinity,
          padding: const EdgeInsets.fromLTRB(16, 16, 8, 12),
          color: Colors.white,
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: _accent.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.psychology, color: _accent, size: 20),
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('AI Numismatic Deepdive',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: _text)),
                    Text('Ask anything about your collection',
                        style: TextStyle(fontSize: 12, color: _subtext)),
                  ],
                ),
              ),
              // New Chat button
              IconButton(
                icon: const Icon(Icons.add_comment_outlined, color: _subtext),
                tooltip: 'New Chat',
                onPressed: _isLoading ? null : _onNewChat,
              ),
            ],
          ),
        ),
        const Divider(height: 1, color: _border),

        // ── Loading indicator ──────────────────────────────────────────────
        if (_isLoadingHistory)
          const LinearProgressIndicator(color: _accent, minHeight: 2),

        // ── Suggestions (shown only until first message) ───────────────────
        if (_messages.isEmpty && !_isLoadingHistory)
          Container(
            color: _bg,
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Try asking:',
                    style: TextStyle(color: _subtext, fontSize: 12, fontWeight: FontWeight.w600)),
                const SizedBox(height: 10),
                Wrap(spacing: 8, runSpacing: 8, children: [
                  _pill('What is my most valuable coin?'),
                  _pill('Which coins should I sell?'),
                  _pill('What should I add next?'),
                  _pill('How much silver do I own?'),
                  _pill('Show me my 1960s coins'),
                  _pill('Summarise my collection'),
                ]),
              ],
            ),
          ),

        // ── Message list ───────────────────────────────────────────────────
        Expanded(
          child: ListView.builder(
            controller: _scrollCtrl,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            itemCount: _messages.length + (_isLoading ? 1 : 0),
            itemBuilder: (ctx, i) {
              // Loading bubble
              if (_isLoading && i == _messages.length) {
                return Align(
                  alignment: Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.only(top: 6, bottom: 4),
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: _border),
                    ),
                    child: const SizedBox(
                      width: 48, height: 14,
                      child: LinearProgressIndicator(
                          color: Color(0xFF3B82F6),
                          backgroundColor: Color(0xFFBFD0FB)),
                    ),
                  ),
                );
              }
              final msg    = _messages[i];
              final isUser = msg['role'] == 'user';
              return Align(
                alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                child: Container(
                  margin: const EdgeInsets.only(top: 6, bottom: 4),
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  constraints: BoxConstraints(
                      maxWidth: MediaQuery.of(context).size.width * 0.78),
                  decoration: BoxDecoration(
                    color: isUser ? _accent : Colors.white,
                    borderRadius: BorderRadius.only(
                      topLeft:     const Radius.circular(16),
                      topRight:    const Radius.circular(16),
                      bottomLeft:  Radius.circular(isUser ? 16 : 4),
                      bottomRight: Radius.circular(isUser ? 4  : 16),
                    ),
                    border: isUser ? null : Border.all(color: _border),
                    boxShadow: [
                      BoxShadow(color: Colors.black.withValues(alpha: 0.04),
                          blurRadius: 4, offset: const Offset(0, 2)),
                    ],
                  ),
                  child: Text(
                    msg['content'] ?? '',
                    style: TextStyle(
                        fontSize: 14,
                        color: isUser ? Colors.white : _text,
                        height: 1.45),
                  ),
                ),
              );
            },
          ),
        ),

        // ── Input bar ─────────────────────────────────────────────────────
        Container(
          padding: const EdgeInsets.fromLTRB(12, 8, 12, 4),
          decoration: const BoxDecoration(
            color: Colors.white,
            border: Border(top: BorderSide(color: _border)),
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
                  ),
                  child: TextField(
                    controller: _controller,
                    style: const TextStyle(color: _text, fontSize: 14),
                    decoration: const InputDecoration(
                      hintText: 'Ask about your collection...',
                      hintStyle: TextStyle(color: Color(0xFFA0A3AB)),
                      border: InputBorder.none,
                      contentPadding: EdgeInsets.symmetric(vertical: 12),
                    ),
                    onSubmitted: _send,
                    textInputAction: TextInputAction.send,
                    maxLines: null,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              GestureDetector(
                onTap: _isLoading ? null : () => _send(_controller.text),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 150),
                  width: 44, height: 44,
                  decoration: BoxDecoration(
                    color: _isLoading ? _border : _accent,
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    _isLoading ? Icons.hourglass_empty : Icons.send,
                    color: Colors.white, size: 18),
                ),
              ),
            ]),
          ),
        ),
      ],
    );
  }

  Widget _pill(String label) => GestureDetector(
    onTap: () => _send(label),
    child: Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _border),
        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 2, offset: const Offset(0, 1))],
      ),
      child: Text(label,
          style: const TextStyle(fontSize: 13, color: _text)),
    ),
  );
}
