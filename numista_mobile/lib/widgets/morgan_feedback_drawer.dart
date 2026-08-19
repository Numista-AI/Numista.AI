// lib/widgets/morgan_feedback_drawer.dart
//
// The MORGAN Feedback Drawer and its full-screen overlay wrapper.
//
// FeedbackDrawerOverlay wraps the entire app shell in a Stack:
//   [0] appShell     — always at the back
//   [1] blur barrier — GestureDetector(opaque) absorbs all taps, triggers soft dismiss
//   [2] drawer       — 420px right-side panel, fully interactive
//
// The _drawerOpen bool on FeedbackTriggerObserver.instance is the single source
// of truth. No route-string matching is used.

import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../constants/feedback_constants.dart';
import '../services/feedback_trigger_observer.dart';
import '../services/beta_feedback_service.dart';
import '../services/morgan_feedback_session.dart';
import 'feedback_fallback_form.dart';

// ---------------------------------------------------------------------------
// FeedbackDrawerOverlay
// Wraps the root child. Registers callbacks with FeedbackTriggerObserver.
// ---------------------------------------------------------------------------

class FeedbackDrawerOverlay extends StatefulWidget {
  final Widget child;

  const FeedbackDrawerOverlay({super.key, required this.child});

  @override
  State<FeedbackDrawerOverlay> createState() => _FeedbackDrawerOverlayState();
}

class _FeedbackDrawerOverlayState extends State<FeedbackDrawerOverlay> {
  bool _open = false;
  MorganFeedbackSession? _session;
  String? _rateLimitMessage;
  bool _fallbackMode = false;

  // Soft-dismiss banner
  bool _bannerVisible = false;
  DateTime? _bannerShownAt;

  // Created once in state — never in build() — to prevent per-rebuild leak.
  late final FocusNode _keyboardFocusNode;

  @override
  void initState() {
    super.initState();
    _keyboardFocusNode = FocusNode();
    FeedbackTriggerObserver.instance.registerCallbacks(
      onOpenDrawer: _openDrawer,
      onOpenFallback: _openFallback,
    );
  }

  @override
  void dispose() {
    _keyboardFocusNode.dispose();
    super.dispose();
  }

  void _openDrawer(FeedbackTriggerEvent event, CheckResult checkResult) {
    if (_open) return;
    setState(() {
      _session = MorganFeedbackSession(
        triggerEvent: event,
        checkResult: checkResult,
      );
      _fallbackMode = false;
      _rateLimitMessage = null;
      _open = true;
      _bannerVisible = false;
    });
    FeedbackTriggerObserver.instance.setDrawerOpen(true);
    _session!.start();
  }

  void _openFallback(FeedbackTriggerEvent event, String? message) {
    if (_open) return;
    setState(() {
      _rateLimitMessage = message;
      _fallbackMode = true;
      _session = null;
      _open = true;
    });
    FeedbackTriggerObserver.instance.setDrawerOpen(true);
  }

  void _softDismiss() {
    if (!_open) return;
    setState(() {
      _bannerVisible = true;
      _bannerShownAt = DateTime.now();
    });

    // Auto-close after kSoftDismissWindowMs if user doesn't resume
    Future.delayed(
      Duration(milliseconds: FeedbackConstants.kSoftDismissWindowMs),
      () {
        if (!mounted) return;
        final shown = _bannerShownAt;
        if (shown != null &&
            DateTime.now().difference(shown).inMilliseconds >=
                FeedbackConstants.kSoftDismissWindowMs) {
          _hardClose(reason: 'banner_timeout');
        }
      },
    );
  }

  void _resumeInterview() {
    setState(() => _bannerVisible = false);
  }

  Future<void> _hardClose({String reason = 'user_closed'}) async {
    final lockId = _session?.checkResult.lockId;
    if (lockId != null) {
      await BetaFeedbackService.dismiss(
        lockId: lockId,
        dismissReason: reason,
      );
    }
    if (!mounted) return;
    setState(() {
      _open = false;
      _session = null;
      _bannerVisible = false;
      _bannerShownAt = null;
    });
    FeedbackTriggerObserver.instance.setDrawerOpen(false);
  }

  // ── Build ──────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return KeyboardListener(
      focusNode: _keyboardFocusNode,
      onKeyEvent: (event) {
        if (event is KeyDownEvent &&
            event.logicalKey == LogicalKeyboardKey.escape &&
            _open) {
          _softDismiss();
        }
      },
      child: Stack(
        // StackFit.expand is required when placed inside MaterialApp.builder:
        // that context is unconstrained on web, and Positioned.fill children
        // throw "RenderBox was not laid out" without an explicit tight size.
        fit: StackFit.expand,
        children: [
          // ① App shell — always first (bottom of stack)
          widget.child,

          // ② Blur barrier — absorbs ALL pointer events; taps trigger soft dismiss
          if (_open)
            Positioned.fill(
              child: GestureDetector(
                behavior: HitTestBehavior.opaque,
                onTap: _softDismiss,
                child: BackdropFilter(
                  filter: ImageFilter.blur(
                    sigmaX: FeedbackConstants.kBackdropBlurSigma,
                    sigmaY: FeedbackConstants.kBackdropBlurSigma,
                  ),
                  child: Container(
                    color: Colors.black.withValues(alpha: 0.18),
                  ),
                ),
              ),
            ),


          // ③ Soft-dismiss banner — above barrier, below drawer
          if (_open && _bannerVisible)
            Positioned(
              top: 0,
              left: 0,
              right: FeedbackConstants.kDrawerWidthPx,
              child: _SoftDismissBanner(
                onResume: _resumeInterview,
                onClose: () => _hardClose(reason: 'user_closed'),
              ),
            ),

          // ④ Feedback drawer — last child = topmost; fully interactive
          if (_open)
            Positioned(
              top: 0,
              right: 0,
              bottom: 0,
              width: FeedbackConstants.kDrawerWidthPx,
              child: FocusScope(
                // Trap focus inside drawer while open
                child: _MorganFeedbackDrawerPanel(
                  session: _session,
                  fallbackMode: _fallbackMode,
                  rateLimitMessage: _rateLimitMessage,
                  onClose: () => _hardClose(reason: 'user_closed'),
                  onSoftDismiss: _softDismiss,
                  onOpenFallback: () {
                    setState(() {
                      _fallbackMode = true;
                      _session = null;
                    });
                  },
                ),
              ),
            ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// _SoftDismissBanner
// ---------------------------------------------------------------------------

class _SoftDismissBanner extends StatelessWidget {
  final VoidCallback onResume;
  final VoidCallback onClose;

  const _SoftDismissBanner({
    required this.onResume,
    required this.onClose,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: Container(
        margin: const EdgeInsets.all(12),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: const Color(0xFF1E293B),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: Colors.amberAccent.withValues(alpha: 0.4)),
          boxShadow: const [BoxShadow(color: Colors.black45, blurRadius: 12)],
        ),
        child: Row(
          children: [
            const Icon(Icons.chat_bubble_outline,
                color: Colors.amberAccent, size: 20),
            const SizedBox(width: 10),
            const Expanded(
              child: Text(
                'Your feedback conversation is paused.',
                style: TextStyle(color: Colors.white, fontSize: 13),
              ),
            ),
            TextButton(
              onPressed: onResume,
              child: const Text('Resume',
                  style: TextStyle(color: Colors.amberAccent)),
            ),
            TextButton(
              onPressed: onClose,
              child: const Text('Close',
                  style: TextStyle(color: Colors.redAccent)),
            ),
          ],
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// _MorganFeedbackDrawerPanel
// ---------------------------------------------------------------------------

class _MorganFeedbackDrawerPanel extends StatefulWidget {
  final MorganFeedbackSession? session;
  final bool fallbackMode;
  final String? rateLimitMessage;
  final VoidCallback onClose;
  final VoidCallback onSoftDismiss;
  final VoidCallback onOpenFallback;

  const _MorganFeedbackDrawerPanel({
    required this.session,
    required this.fallbackMode,
    required this.rateLimitMessage,
    required this.onClose,
    required this.onSoftDismiss,
    required this.onOpenFallback,
  });

  @override
  State<_MorganFeedbackDrawerPanel> createState() =>
      _MorganFeedbackDrawerPanelState();
}

class _MorganFeedbackDrawerPanelState
    extends State<_MorganFeedbackDrawerPanel> {
  final TextEditingController _inputController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  @override
  void dispose() {
    _inputController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 280),
      curve: Curves.easeOutCubic,
      decoration: const BoxDecoration(
        color: Color(0xFF111827),
        border: Border(
          left: BorderSide(color: Color(0xFF374151), width: 1),
        ),
        boxShadow: [
          BoxShadow(color: Colors.black54, blurRadius: 24, offset: Offset(-4, 0)),
        ],
      ),
      child: Column(
        children: [
          _buildHeader(),
          const Divider(height: 1, color: Color(0xFF374151)),
          Expanded(child: _buildBody()),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      color: const Color(0xFF1E2937),
      child: Row(
        children: [
          // Feedback mode chip
          Container(
            padding:
                const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.amber.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(12),
              border:
                  Border.all(color: Colors.amber.withValues(alpha: 0.4)),
            ),
            child: const Text(
              'Feedback Mode',
              style: TextStyle(
                  color: Colors.amber,
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 0.3),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              widget.session?.triggerEvent.pageTitle ?? 'Feedback',
              style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 12,
                  overflow: TextOverflow.ellipsis),
            ),
          ),
          // "File a short note instead" escape hatch
          if (!widget.fallbackMode)
            TextButton(
              onPressed: widget.onOpenFallback,
              style: TextButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 8)),
              child: const Text(
                'File a short note instead',
                style: TextStyle(color: Colors.grey, fontSize: 11),
              ),
            ),
          IconButton(
            icon: const Icon(Icons.close, color: Colors.grey, size: 18),
            onPressed: widget.onClose,
            tooltip: 'Close',
          ),
        ],
      ),
    );
  }

  Widget _buildBody() {
    if (widget.fallbackMode) {
      return FeedbackFallbackForm(
        message: widget.rateLimitMessage,
        session: widget.session,
        onClose: widget.onClose,
      );
    }

    final session = widget.session;
    if (session == null) return const SizedBox.shrink();

    return ListenableBuilder(
      listenable: session,
      builder: (context, _) {
        _scrollToBottom();

        switch (session.phase) {
          case SessionPhase.extractFailed:
            return _buildExtractFailView(session);
          case SessionPhase.submitted:
            return _buildSubmittedView(session);
          case SessionPhase.fallbackRequired:
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (mounted) widget.onOpenFallback();
            });
            return const SizedBox.shrink();
          default:
            return Column(
              children: [
                Expanded(child: _buildChatList(session)),
                if (session.phase == SessionPhase.awaitingConfirmation)
                  _buildConfirmationButtons(session)
                else
                  _buildInputRow(session),
              ],
            );
        }
      },
    );
  }

  Widget _buildChatList(MorganFeedbackSession session) {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      itemCount: session.bubbles.length,
      itemBuilder: (ctx, i) {
        final bubble = session.bubbles[i];
        return _ChatBubbleWidget(bubble: bubble);
      },
    );
  }

  Widget _buildInputRow(MorganFeedbackSession session) {
    final busy = session.phase == SessionPhase.extracting;
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: Color(0xFF374151))),
      ),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _inputController,
              enabled: !busy,
              style: const TextStyle(color: Colors.white, fontSize: 14),
              decoration: InputDecoration(
                hintText: busy ? 'MORGAN is thinking…' : 'Type your reply…',
                hintStyle:
                    const TextStyle(color: Colors.grey, fontSize: 13),
                filled: true,
                fillColor: const Color(0xFF1E2937),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                  borderSide: BorderSide.none,
                ),
                contentPadding: const EdgeInsets.symmetric(
                    horizontal: 12, vertical: 10),
              ),
              onSubmitted: busy
                  ? null
                  : (text) {
                      session.sendUserMessage(text);
                      _inputController.clear();
                    },
            ),
          ),
          const SizedBox(width: 8),
          IconButton(
            icon: busy
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                        strokeWidth: 2, color: Colors.amberAccent))
                : const Icon(Icons.send, color: Colors.amberAccent),
            onPressed: busy
                ? null
                : () {
                    session.sendUserMessage(_inputController.text);
                    _inputController.clear();
                  },
          ),
        ],
      ),
    );
  }

  Widget _buildConfirmationButtons(MorganFeedbackSession session) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: Color(0xFF374151))),
      ),
      child: Row(
        children: [
          Expanded(
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green.shade700,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8)),
              ),
              onPressed: () async {
                final result = await session.confirmAndSubmit();
                if (result != null && mounted) setState(() {});
              },
              child: const Text('Yes, file it',
                  style: TextStyle(color: Colors.white)),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: OutlinedButton(
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: Colors.grey),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8)),
              ),
              onPressed: () {
                showDialog(
                  context: context,
                  builder: (ctx) => _CorrectionDialog(
                    onSubmit: (note) {
                      Navigator.of(ctx).pop();
                      session.requestCorrection(note);
                    },
                  ),
                );
              },
              child: const Text("No, let me clarify",
                  style: TextStyle(color: Colors.white70)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildExtractFailView(MorganFeedbackSession session) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // MORGAN's best-effort summary text
          if (session.bubbles.isNotEmpty) ...[
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF1E2937),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                session.bubbles.last.text,
                style: const TextStyle(color: Colors.white70, fontSize: 13),
              ),
            ),
            const SizedBox(height: 20),
          ],
          const Text(
            'I wasn\'t able to fully structure your feedback, but I\'ve captured our conversation.',
            style: TextStyle(color: Colors.grey, fontSize: 12),
          ),
          const SizedBox(height: 16),
          // Primary action — must be explicit tap
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF1E4ED8),
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8)),
              ),
              onPressed: () async {
                await session.fileUnconfirmed();
                if (mounted) setState(() {});
              },
              child: const Text('File this as unconfirmed',
                  style: TextStyle(
                      color: Colors.white, fontWeight: FontWeight.w600)),
            ),
          ),
          const SizedBox(height: 8),
          // Secondary — DISMISS, no doc written
          SizedBox(
            width: double.infinity,
            child: TextButton(
              onPressed: widget.onClose, // triggers DISMISS in _hardClose
              child: const Text('Close without filing',
                  style: TextStyle(color: Colors.grey)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSubmittedView(MorganFeedbackSession session) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.check_circle_outline,
              color: Colors.greenAccent, size: 40),
          const SizedBox(height: 12),
          const Text(
            'Filed and on its way to the team.',
            style: TextStyle(
                color: Colors.white,
                fontSize: 15,
                fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 8),
          Text(
            'Back to ${session.triggerEvent.pageTitle}',
            style: const TextStyle(color: Colors.grey, fontSize: 12),
          ),
          if (session.correctionWindowOpen) ...[
            const SizedBox(height: 16),
            TextButton.icon(
              onPressed: () {
                showDialog(
                  context: context,
                  builder: (ctx) => _CorrectionDialog(
                    onSubmit: (note) {
                      Navigator.of(ctx).pop();
                      final docId = session.submittedDocId;
                      if (docId != null) {
                        BetaFeedbackService.submitCorrection(
                          docId: docId,
                          correctionText: note,
                        );
                      }
                    },
                  ),
                );
              },
              icon: const Icon(Icons.edit_note,
                  color: Colors.amberAccent, size: 16),
              label: const Text('Something not right? Add a correction',
                  style: TextStyle(color: Colors.amberAccent, fontSize: 12)),
            ),
          ],
          const Spacer(),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF1E2937),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8)),
              ),
              onPressed: widget.onClose,
              child: const Text('Close',
                  style: TextStyle(color: Colors.white70)),
            ),
          ),
        ],
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// _ChatBubbleWidget
// ---------------------------------------------------------------------------

class _ChatBubbleWidget extends StatelessWidget {
  final ChatBubble bubble;

  const _ChatBubbleWidget({required this.bubble});

  @override
  Widget build(BuildContext context) {
    final isAssistant = bubble.role == 'assistant';
    return Align(
      alignment:
          isAssistant ? Alignment.centerLeft : Alignment.centerRight,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 320),
        margin: const EdgeInsets.only(bottom: 10),
        padding:
            const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: isAssistant
              ? const Color(0xFF1E2937)
              : const Color(0xFF1E4ED8),
          borderRadius: BorderRadius.circular(12).copyWith(
            bottomLeft: isAssistant
                ? const Radius.circular(2)
                : null,
            bottomRight: !isAssistant
                ? const Radius.circular(2)
                : null,
          ),
        ),
        child: bubble.isStreaming
            ? Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    bubble.text,
                    style: const TextStyle(
                        color: Colors.white, fontSize: 13),
                  ),
                  const SizedBox(width: 6),
                  const SizedBox(
                    width: 10,
                    height: 10,
                    child: CircularProgressIndicator(
                        strokeWidth: 1.5,
                        color: Colors.amberAccent),
                  ),
                ],
              )
            : Text(
                bubble.text,
                style: TextStyle(
                    color: isAssistant
                        ? Colors.white
                        : Colors.white,
                    fontSize: 13,
                    height: 1.45),
              ),
      ),
    );
  }
}

// ---------------------------------------------------------------------------
// _CorrectionDialog
// ---------------------------------------------------------------------------

class _CorrectionDialog extends StatefulWidget {
  final void Function(String) onSubmit;

  const _CorrectionDialog({required this.onSubmit});

  @override
  State<_CorrectionDialog> createState() => _CorrectionDialogState();
}

class _CorrectionDialogState extends State<_CorrectionDialog> {
  final _ctrl = TextEditingController();

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: const Color(0xFF1E2937),
      title: const Text('Add a correction',
          style: TextStyle(color: Colors.white, fontSize: 15)),
      content: TextField(
        controller: _ctrl,
        maxLines: 3,
        style: const TextStyle(color: Colors.white, fontSize: 13),
        decoration: InputDecoration(
          hintText: 'What would you like to correct or add?',
          hintStyle: const TextStyle(color: Colors.grey),
          filled: true,
          fillColor: const Color(0xFF0F172A),
          border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide.none),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child:
              const Text('Cancel', style: TextStyle(color: Colors.grey)),
        ),
        ElevatedButton(
          style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF1E4ED8)),
          onPressed: () {
            if (_ctrl.text.trim().isNotEmpty) {
              widget.onSubmit(_ctrl.text.trim());
            }
          },
          child: const Text('Submit correction',
              style: TextStyle(color: Colors.white)),
        ),
      ],
    );
  }
}
