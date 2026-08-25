// support_portal_screen.dart
//
// Admin-only Support Portal. Requires admin == true custom claim (enforced by backend).
// Never reads private sub-document directly from Firestore.
// All coin data is fetched via GET /support/tickets/:id which re-fetches and
// re-redacts server-side on every call.

import 'package:flutter/material.dart';
import '../services/ticket_service.dart';
import '../models/ticket_model.dart';

class SupportPortalScreen extends StatefulWidget {
  const SupportPortalScreen({super.key});

  @override
  State<SupportPortalScreen> createState() => _SupportPortalScreenState();
}

class _SupportPortalScreenState extends State<SupportPortalScreen> {
  // Queue state
  List<HelpTicket> _queue = [];
  bool _queueLoading = true;
  String? _queueError;

  // Selected ticket state
  HelpTicket? _selectedTicket;
  SupportTicketView? _ticketView;
  bool _viewLoading = false;
  String? _viewError;

  // Message compose
  final _replyController = TextEditingController();
  bool _replySending = false;

  @override
  void initState() {
    super.initState();
    _loadQueue();
  }

  @override
  void dispose() {
    _replyController.dispose();
    super.dispose();
  }

  Future<void> _loadQueue() async {
    setState(() { _queueLoading = true; _queueError = null; });
    try {
      final list = await TicketService.listSupportTickets();
      if (mounted) setState(() { _queue = list; _queueLoading = false; });
    } catch (e) {
      if (mounted) setState(() { _queueLoading = false; _queueError = e.toString(); });
    }
  }

  Future<void> _openTicket(HelpTicket ticket) async {
    setState(() { _selectedTicket = ticket; _viewLoading = true; _viewError = null; _ticketView = null; });
    try {
      final view = await TicketService.getSupportTicketView(
        ticketId: ticket.ticketId,
      );
      if (mounted) setState(() { _ticketView = view; _viewLoading = false; });
    } catch (e) {
      if (mounted) setState(() { _viewLoading = false; _viewError = e.toString(); });
    }
  }

  Future<void> _sendReply() async {
    final body = _replyController.text.trim();
    if (body.isEmpty || _selectedTicket == null) return;
    setState(() => _replySending = true);
    try {
      await TicketService.supportPostMessage(
        ticketId: _selectedTicket!.ticketId,
        msgBody: body,
      );
      _replyController.clear();
      // Refresh the view
      final view = await TicketService.getSupportTicketView(
        ticketId: _selectedTicket!.ticketId,
      );
      if (mounted) setState(() { _ticketView = view; _replySending = false; });
    } catch (e) {
      if (mounted) {
        setState(() => _replySending = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to send: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  Future<void> _updateStatus(String status) async {
    if (_selectedTicket == null) return;
    try {
      await TicketService.updateTicketStatus(_selectedTicket!.ticketId, status);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Status updated to $status'), backgroundColor: const Color(0xFF34A853)),
      );
      _loadQueue();
      setState(() { _selectedTicket = null; _ticketView = null; });
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed: $e'), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Left panel: ticket queue
        Container(
          width: 320,
          decoration: const BoxDecoration(
            border: Border(right: BorderSide(color: Color(0xFFE2E6E9))),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildQueueHeader(),
              Expanded(child: _buildQueue()),
            ],
          ),
        ),

        // Right panel: ticket view
        Expanded(
          child: _selectedTicket == null
              ? _buildEmptyDetail()
              : _viewLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _viewError != null
                      ? _buildViewError()
                      : _buildTicketDetail(),
        ),
      ],
    );
  }

  Widget _buildQueueHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Color(0xFFE2E6E9))),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Support Queue',
              style: TextStyle(
                  fontSize: 18, fontWeight: FontWeight.w800, color: Color(0xFF31333F))),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: Text(
                  '${_queue.length} open ticket(s)',
                  style: const TextStyle(color: Color(0xFF8A8C96), fontSize: 12),
                ),
              ),
              IconButton(
                icon: const Icon(Icons.refresh_rounded, size: 18),
                tooltip: 'Refresh queue',
                onPressed: _loadQueue,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQueue() {
    if (_queueLoading) return const Center(child: CircularProgressIndicator());
    if (_queueError != null) {
      return Padding(
        padding: const EdgeInsets.all(16),
        child: Text(_queueError!, style: const TextStyle(color: Colors.red, fontSize: 13)),
      );
    }
    if (_queue.isEmpty) {
      return const Center(
        child: Text('No open tickets', style: TextStyle(color: Color(0xFF8A8C96))),
      );
    }
    return ListView.builder(
      itemCount: _queue.length,
      itemBuilder: (ctx, i) {
        final t = _queue[i];
        final isSelected = _selectedTicket?.ticketId == t.ticketId;
        return InkWell(
          onTap: () => _openTicket(t),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
            decoration: BoxDecoration(
              color: isSelected
                  ? const Color(0xFFEBF2FF)
                  : Colors.transparent,
              border: const Border(
                  bottom: BorderSide(color: Color(0xFFF0F1F3))),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(t.subject,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(
                              fontWeight: isSelected
                                  ? FontWeight.w700
                                  : FontWeight.w500,
                              fontSize: 13,
                              color: const Color(0xFF31333F))),
                    ),
                    if (t.grantActive)
                      Container(
                        margin: const EdgeInsets.only(left: 6),
                        width: 8,
                        height: 8,
                        decoration: const BoxDecoration(
                          color: Color(0xFFE37400),
                          shape: BoxShape.circle,
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  '${t.categoryLabel}  ·  ${t.status.label}',
                  style: const TextStyle(
                      color: Color(0xFF8A8C96), fontSize: 11),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildEmptyDetail() {
    return const Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.support_agent_outlined, size: 56, color: Color(0xFFB0B4C1)),
          SizedBox(height: 12),
          Text('Select a ticket and enter the grant token to view.',
              style: TextStyle(color: Color(0xFF8A8C96), fontSize: 14)),
        ],
      ),
    );
  }

  Widget _buildViewError() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.lock_outline, size: 48, color: Color(0xFFB0B4C1)),
            const SizedBox(height: 12),
            Text(
              _viewError ?? 'Access denied',
              textAlign: TextAlign.center,
              style: const TextStyle(color: Color(0xFF5A5C69), fontSize: 14),
            ),
            const SizedBox(height: 16),
            OutlinedButton(
              onPressed: () => setState(() { _selectedTicket = null; _viewError = null; }),
              child: const Text('Back to Queue'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTicketDetail() {
    final view = _ticketView!;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Ticket header
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(view.subject,
                        style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.w800,
                            color: Color(0xFF31333F))),
                    const SizedBox(height: 4),
                    Text(
                      '${view.category}  ·  ${view.platform}  ·  v${view.appVersion}',
                      style: const TextStyle(color: Color(0xFF8A8C96), fontSize: 12),
                    ),
                  ],
                ),
              ),
              // Status changer
              DropdownButton<String>(
                value: view.status,
                items: const [
                  DropdownMenuItem(value: 'open', child: Text('Open')),
                  DropdownMenuItem(value: 'in_progress', child: Text('In Progress')),
                  DropdownMenuItem(value: 'waiting_on_user', child: Text('Waiting on User')),
                  DropdownMenuItem(value: 'resolved', child: Text('Resolved')),
                  DropdownMenuItem(value: 'closed', child: Text('Closed')),
                ],
                onChanged: (s) { if (s != null) _updateStatus(s); },
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Description
          _buildSection('Description', view.description),

          // Redacted fields notice
          if (view.redactedFieldsApplied.isNotEmpty) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFFFF8E1),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFFFFE082)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.visibility_off_outlined,
                      color: Color(0xFF7A6200), size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Fields withheld by user or privacy policy: '
                      '${view.redactedFieldsApplied.join(', ')}',
                      style: const TextStyle(
                          color: Color(0xFF7A6200), fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
          ],

          // Coins
          if (view.coins.isNotEmpty) ...[
            const SizedBox(height: 24),
            const Text('Shared Coins',
                style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF31333F))),
            const SizedBox(height: 12),
            ...view.coins.map((c) => _buildCoinCard(c)),

          ],

          // Error logs
          if (view.errorLogs.isNotEmpty) ...[
            const SizedBox(height: 24),
            const Text('Error Logs',
                style: TextStyle(
                    fontSize: 15, fontWeight: FontWeight.w700, color: Color(0xFF31333F))),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFF8F9FB),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFFE2E6E9)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: view.errorLogs
                    .map((l) => Padding(
                          padding: const EdgeInsets.only(bottom: 4),
                          child: Text(l,
                              style: const TextStyle(
                                  fontSize: 12, fontFamily: 'monospace')),
                        ))
                    .toList(),
              ),
            ),
          ],

          // Messages
          const SizedBox(height: 28),
          const Text('Messages',
              style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF31333F))),
          const SizedBox(height: 12),
          if (view.messages.isEmpty)
            const Text('No messages yet.',
                style: TextStyle(color: Color(0xFF8A8C96), fontSize: 13))
          else
            ...view.messages.map((m) => _buildMessage(m)),


          // Reply box
          const SizedBox(height: 20),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Expanded(
                child: TextField(
                  controller: _replyController,
                  maxLines: 3,
                  style: const TextStyle(fontSize: 14),
                  decoration: InputDecoration(
                    hintText: 'Type a reply…',
                    filled: true,
                    fillColor: const Color(0xFFF8F9FB),
                    border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                        borderSide: const BorderSide(color: Color(0xFFDDE1E7))),
                    enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                        borderSide: const BorderSide(color: Color(0xFFDDE1E7))),
                    contentPadding:
                        const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              ElevatedButton.icon(
                onPressed: _replySending ? null : _sendReply,
                icon: _replySending
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(
                            strokeWidth: 2, color: Colors.white))
                    : const Icon(Icons.send_rounded, size: 18),
                label: Text(_replySending ? 'Sending…' : 'Send Reply'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF1967D2),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSection(String title, String body) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title,
            style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: Color(0xFF31333F))),
        const SizedBox(height: 6),
        Text(body,
            style: const TextStyle(color: Color(0xFF5A5C69), fontSize: 14)),
      ],
    );
  }

  Widget _buildCoinCard(SupportCoinView coin) {
    final fields = <String, String?>{
      'Denomination': coin.denomination,
      'Year': coin.year,
      'Program/Series': coin.programSeries,
      'Grade': coin.grade,
      'Mint Mark': coin.mintMark,
      'Country': coin.country,
      'Composition': coin.composition,
      'Variety': coin.variety,
    }.entries.where((e) => e.value != null && e.value!.isNotEmpty).toList();

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F9FB),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFE2E6E9)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Image thumbnail
          if (coin.obverseImageUrl != null)
            ClipRRect(
              borderRadius: BorderRadius.circular(6),
              child: Image.network(
                coin.obverseImageUrl!,
                width: 64,
                height: 64,
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) => Container(

                    width: 64,
                    height: 64,
                    color: const Color(0xFFE2E6E9),
                    child: const Icon(Icons.monetization_on_outlined,
                        color: Color(0xFFB0B4C1))),
              ),
            )
          else
            Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                color: const Color(0xFFE2E6E9),
                borderRadius: BorderRadius.circular(6),
              ),
              child: const Icon(Icons.monetization_on_outlined,
                  color: Color(0xFFB0B4C1)),
            ),
          const SizedBox(width: 14),
          Expanded(
            child: Wrap(
              spacing: 12,
              runSpacing: 4,
              children: fields
                  .map((e) => RichText(
                        text: TextSpan(
                          children: [
                            TextSpan(
                                text: '${e.key}: ',
                                style: const TextStyle(
                                    fontWeight: FontWeight.w600,
                                    color: Color(0xFF31333F),
                                    fontSize: 13)),
                            TextSpan(
                                text: e.value,
                                style: const TextStyle(
                                    color: Color(0xFF5A5C69), fontSize: 13)),
                          ],
                        ),
                      ))
                  .toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessage(TicketMessage msg) {
    final isSupport = msg.sender == 'support';
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: isSupport
            ? const Color(0xFFEBF2FF)
            : const Color(0xFFF8F9FB),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
            color: isSupport
                ? const Color(0xFFBFD0FB)
                : const Color(0xFFE2E6E9)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                isSupport ? 'Support' : 'User',
                style: TextStyle(
                    fontWeight: FontWeight.w700,
                    fontSize: 12,
                    color: isSupport
                        ? const Color(0xFF1967D2)
                        : const Color(0xFF5A5C69)),
              ),
              const Spacer(),
              Text(
                _formatDateTime(msg.createdAt),
                style: const TextStyle(color: Color(0xFF8A8C96), fontSize: 11),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(msg.body,
              style: const TextStyle(color: Color(0xFF31333F), fontSize: 13)),
        ],
      ),
    );
  }

  String _formatDateTime(DateTime dt) {
    return '${dt.year}-${dt.month.toString().padLeft(2, '0')}-${dt.day.toString().padLeft(2, '0')} '
        '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
  }
}
