import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/morgan_proactive_rescue_observer.dart';
import '../services/stt_voice_service.dart';
import 'morgan_guide_flow.dart';
import 'morgan_settings_panel.dart';

class MorganGateProposal {
  final String actionType;
  final String summaryText;
  final Map<String, dynamic> payload;

  const MorganGateProposal({
    required this.actionType,
    required this.summaryText,
    this.payload = const <String, dynamic>{},
  });
}

/// Senior-friendly WCAG AAA cards hosted inside the unified Morgan Co-Pilot window:
/// - Active step-by-step guide banner (unified from `MorganGuideService`)
/// - Proactive Rescue banner (`Fix It For Me` & `I Need More Time`)
/// - Gate 0 High-Contrast Confirmation Card (`minHeight: 56`, `18px` bold, voice + keyboard)
class MorganCopilotBannerHost extends StatefulWidget {
  final MorganGateProposal? activeProposal;
  final Future<void> Function(MorganGateProposal proposal)? onConfirmProposal;
  final VoidCallback? onCancelProposal;

  const MorganCopilotBannerHost({
    super.key,
    this.activeProposal,
    this.onConfirmProposal,
    this.onCancelProposal,
  });

  @override
  State<MorganCopilotBannerHost> createState() =>
      _MorganCopilotBannerHostState();
}

class _MorganCopilotBannerHostState extends State<MorganCopilotBannerHost> {
  final FocusNode _cancelFocusNode = FocusNode();
  bool _submitting = false;

  @override
  void initState() {
    super.initState();
    SttVoiceService.instance.onUtterance = _handleSttUtterance;
  }

  @override
  void didUpdateWidget(covariant MorganCopilotBannerHost oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.activeProposal != null && oldWidget.activeProposal == null) {
      SttVoiceService.instance.resetConfirmationWindow();
    }
  }

  Future<void> _handleSttUtterance(SttUtteranceEvent event) async {
    final proposal = widget.activeProposal;
    if (proposal == null || _submitting || !mounted) return;
    final decision = SttVoiceService.instance.evaluateConfirmationUtterance(
      event,
      isConfirmationCardVisible: true,
      expectedGateAction: proposal.actionType,
    );
    if (decision.confirmed) {
      setState(() => _submitting = true);
      try {
        await widget.onConfirmProposal?.call(proposal);
      } finally {
        if (mounted) setState(() => _submitting = false);
      }
    }
  }

  @override
  void dispose() {
    if (SttVoiceService.instance.onUtterance == _handleSttUtterance) {
      SttVoiceService.instance.onUtterance = null;
    }
    _cancelFocusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final rescueObserver = MorganProactiveRescueObserver.instance;
    return ListenableBuilder(
      listenable: Listenable.merge([
        MorganGuideService.current,
        rescueObserver,
      ]),
      builder: (context, _) {
        final guideState = MorganGuideService.current.value;
        final rescue = rescueObserver.activePrompt;
        final proposal = widget.activeProposal;

        if (guideState == null && rescue == null && proposal == null) {
          return const SizedBox.shrink();
        }

        return FocusTraversalGroup(
          policy: OrderedTraversalPolicy(),
          child: Container(
            color: const Color(0xFFF8FAFC),
            padding: const EdgeInsets.fromLTRB(12, 8, 12, 4),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (guideState != null) _buildGuideCard(guideState),
                if (rescue != null) _buildRescueCard(rescueObserver, rescue),
                if (proposal != null) _buildConfirmationGateCard(proposal),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildGuideCard(GuideState state) {
    final step = state.guide.steps[state.step];
    final total = state.guide.steps.length;
    final isLast = state.step >= total - 1;

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      color: const Color(0xFFFFFFFF),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: Color(0xFF0F172A), width: 1.5),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Step ${state.step + 1} of $total: ${state.guide.title}',
              style: const TextStyle(
                color: Color(0xFF0F172A),
                fontSize: 17,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              step.narration,
              style: const TextStyle(
                color: Color(0xFF1E293B),
                fontSize: 16,
                height: 1.45,
              ),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                if (state.step > 0) ...[
                  ConstrainedBox(
                    constraints: const BoxConstraints(minHeight: 56),
                    child: OutlinedButton(
                      onPressed: MorganGuideService.back,
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFF0F172A),
                        side: const BorderSide(
                            color: Color(0xFF0F172A), width: 1.5),
                        textStyle: const TextStyle(
                            fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                      child: const Text('Back'),
                    ),
                  ),
                  const SizedBox(width: 8),
                ],
                Expanded(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(minHeight: 56),
                    child: ElevatedButton(
                      onPressed: isLast
                          ? MorganGuideService.exit
                          : MorganGuideService.next,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF14532D),
                        foregroundColor: Colors.white,
                        textStyle: const TextStyle(
                            fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                      child: Text(isLast ? 'Done' : 'Next Step →'),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                ConstrainedBox(
                  constraints: const BoxConstraints(minHeight: 56),
                  child: TextButton(
                    onPressed: MorganGuideService.exit,
                    style: TextButton.styleFrom(
                      foregroundColor: const Color(0xFF1E293B),
                      textStyle: const TextStyle(
                          fontSize: 16, fontWeight: FontWeight.w600),
                    ),
                    child: const Text('Exit Guide'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRescueCard(
    MorganProactiveRescueObserver observer,
    MorganRescuePrompt rescue,
  ) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      color: const Color(0xFFFEF3C7),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: Color(0xFF0F172A), width: 2),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              rescue.title,
              style: const TextStyle(
                color: Color(0xFF0F172A),
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              rescue.message,
              style: const TextStyle(
                color: Color(0xFF1E293B),
                fontSize: 16,
                height: 1.45,
              ),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                Semantics(
                  identifier: 'morgan_rescue_fix_btn',
                  button: true,
                  label: rescue.fixButtonLabel,
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(minHeight: 56),
                    child: ElevatedButton(
                      onPressed: observer.triggerFixItForMe,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF14532D),
                        foregroundColor: Colors.white,
                        textStyle: const TextStyle(
                          fontSize: 17,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      child: Text(rescue.fixButtonLabel),
                    ),
                  ),
                ),
                Semantics(
                  identifier: 'morgan_need_more_time_btn',
                  button: true,
                  label: 'I Need More Time',
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(minHeight: 56),
                    child: OutlinedButton(
                      onPressed: observer.pauseForSession,
                      style: OutlinedButton.styleFrom(
                        foregroundColor: const Color(0xFF0F172A),
                        backgroundColor: Colors.white,
                        side: const BorderSide(
                            color: Color(0xFF0F172A), width: 1.5),
                        textStyle: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      child: const Text('I Need More Time'),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildConfirmationGateCard(MorganGateProposal proposal) {
    final isDelete = proposal.actionType == 'delete_coin';
    return CallbackShortcuts(
      bindings: <ShortcutActivator, VoidCallback>{
        const SingleActivator(LogicalKeyboardKey.escape): () {
          widget.onCancelProposal?.call();
        },
      },
      child: Card(
        margin: const EdgeInsets.only(bottom: 8),
        color: const Color(0xFFFFFFFF),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(14),
          side: const BorderSide(color: Color(0xFF0F172A), width: 2),
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'Confirm Before Saving',
                style: TextStyle(
                  color: Color(0xFF0F172A),
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                proposal.summaryText,
                style: const TextStyle(
                  color: Color(0xFF1E293B),
                  fontSize: 16,
                  height: 1.45,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                isDelete
                    ? 'Tip: Say "Yes delete" or tap Confirm below.'
                    : 'Tip: Say "Yes, please save that" or tap Confirm below.',
                style: const TextStyle(
                  color: Color(0xFF334155),
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: Semantics(
                      identifier: 'morgan_confirm_cancel_btn',
                      button: true,
                      label: 'Cancel',
                      child: ConstrainedBox(
                        constraints: const BoxConstraints(minHeight: 56),
                        child: OutlinedButton(
                          focusNode: _cancelFocusNode,
                          autofocus: true,
                          onPressed: _submitting ? null : widget.onCancelProposal,
                          style: OutlinedButton.styleFrom(
                            foregroundColor: const Color(0xFF0F172A),
                            side: const BorderSide(
                              color: Color(0xFF0F172A),
                              width: 2,
                            ),
                            textStyle: const TextStyle(
                              fontSize: 17,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          child: const Text('Cancel'),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Semantics(
                      identifier: 'morgan_confirm_yes_btn',
                      button: true,
                      label: isDelete ? 'Yes, Delete' : 'Yes, Save',
                      child: ConstrainedBox(
                        constraints: const BoxConstraints(minHeight: 56),
                        child: ElevatedButton(
                          onPressed: _submitting
                              ? null
                              : () async {
                                  setState(() => _submitting = true);
                                  try {
                                    await widget.onConfirmProposal
                                        ?.call(proposal);
                                  } finally {
                                    if (mounted) {
                                      setState(() => _submitting = false);
                                    }
                                  }
                                },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: isDelete
                                ? const Color(0xFF991B1B)
                                : const Color(0xFF14532D),
                            foregroundColor: Colors.white,
                            textStyle: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          child: Text(isDelete ? 'Yes, Delete' : 'Yes, Save'),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Dialog wrapper to show [MorganSettingsPanel] cleanly from the Morgan header.
Future<void> showMorganCopilotPrivacySettingsDialog(BuildContext context) async {
  await MorganSettingsService.instance.load();
  if (!context.mounted) return;
  await showDialog<void>(
    context: context,
    builder: (ctx) => AlertDialog(
      backgroundColor: const Color(0xFFFFFFFF),
      title: const Text(
        'Morgan Co-Pilot Comfort & Privacy',
        style: TextStyle(color: Color(0xFF0F172A), fontWeight: FontWeight.bold),
      ),
      content: const SingleChildScrollView(
        child: SizedBox(width: 420, child: MorganSettingsPanel()),
      ),
      actions: [
        ConstrainedBox(
          constraints: const BoxConstraints(minHeight: 56),
          child: ElevatedButton(
            onPressed: () => Navigator.of(ctx).pop(),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF14532D),
              foregroundColor: Colors.white,
              textStyle: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            child: const Text('Done'),
          ),
        ),
      ],
    ),
  );
}
