// my_tickets_screen.dart
//
// User-facing ticket inbox: list own tickets, view details, issue/revoke grants.
// Desktop Web only. All security decisions are made server-side.

import 'package:flutter/material.dart';
import '../services/ticket_service.dart';
import '../models/ticket_model.dart';

class MyTicketsScreen extends StatefulWidget {
  const MyTicketsScreen({super.key});

  @override
  State<MyTicketsScreen> createState() => _MyTicketsScreenState();
}

class _MyTicketsScreenState extends State<MyTicketsScreen> {
  List<HelpTicket> _tickets = [];
  bool _loading = true;
  String? _error;

  @override

  void initState() {
    super.initState();
    _loadTickets();
  }

  Future<void> _loadTickets() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final list = await TicketService.listMyTickets();
      if (mounted) {
        setState(() {
          _tickets = list;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _loading = false;
          _error = e.toString();
        });
      }
    }
  }

  Future<void> _revokeGrant(String ticketId) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Revoke Support Access?'),
        content: const Text(
            'This immediately terminates the support agent\'s ability to view '
            'your coin details. You can issue a new grant at any time.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red.shade600),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Revoke', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
    if (confirm != true) return;
    try {
      await TicketService.revokeGrant(ticketId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
              content: Text('Support access revoked.'),
              backgroundColor: Color(0xFF34A853)),
        );
        _loadTickets();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to revoke: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  Future<void> _showGrantDialog(HelpTicket ticket) async {
    final result = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (ctx) => _GrantDialog(ticket: ticket),
    );
    if (result == null) return;

    try {
      final response = await TicketService.createGrant(
        ticketId: ticket.ticketId,
        allowedCoinIds: (result['coin_ids'] as List<String>?) ?? [],
        redactedFields: [],
        durationHours: (result['duration_hours'] as int?) ?? 48,
      );

      if (mounted) {
        final expiresAt = response['expires_at'] as String?;
        final hours = response['duration_hours'] as int? ?? 48;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Support access granted for $hours hours'
              '${expiresAt != null ? ' (expires ${expiresAt.substring(0, 10)})' : ''}. '
              'You can revoke it at any time.',
            ),
            backgroundColor: const Color(0xFF34A853),
            duration: const Duration(seconds: 6),
          ),
        );
        _loadTickets();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to create grant: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(children: [
            const Text(
              'My Tickets',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.w900,
                fontStyle: FontStyle.italic,
                color: Color(0xFFC8D0E0),
              ),
            ),
            const SizedBox(width: 12),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: const Color(0xFF1967D2),
                borderRadius: BorderRadius.circular(6),
              ),
              child: const Text('SUPPORT HISTORY',
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: 11,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.5)),
            ),
            const Spacer(),
            IconButton(
              icon: const Icon(Icons.refresh_rounded),
              tooltip: 'Refresh',
              onPressed: _loadTickets,
            ),
          ]),
          const SizedBox(height: 8),
          const Text(
            'Track your open tickets. Issue temporary, scoped support access — '
            'you control exactly which coins are visible and for how long.',
            style: TextStyle(color: Color(0xFFC8D0E0), fontSize: 14),
          ),
          const SizedBox(height: 32),

          if (_loading)
            const Center(child: CircularProgressIndicator())
          else if (_error != null)
            _buildErrorBanner(_error!)
          else if (_tickets.isEmpty)
            _buildEmptyState()
          else
            ..._tickets.map((t) => _buildTicketCard(t)),

        ],
      ),
    );
  }

  Widget _buildTicketCard(HelpTicket ticket) {
    final statusColor = _statusColor(ticket.status);

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E6E9)),
        boxShadow: [
          BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 8,
              offset: const Offset(0, 2))
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  ticket.subject,
                  style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF31333F)),
                ),
              ),
              const SizedBox(width: 12),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: statusColor.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  ticket.status.label,
                  style: TextStyle(
                      color: statusColor,
                      fontSize: 12,
                      fontWeight: FontWeight.w700),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            '${ticket.categoryLabel}  ·  ${_formatDate(ticket.createdAt)}',
            style: const TextStyle(color: Color(0xFF8A8C96), fontSize: 12),
          ),
          const SizedBox(height: 12),
          Text(
            ticket.description,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(color: Color(0xFF5A5C69), fontSize: 13),
          ),

          // Grant status
          if (ticket.grantActive) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFFFFBE6),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFFFFD700)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.vpn_key_rounded,
                      color: Color(0xFFB8860B), size: 18),
                  const SizedBox(width: 8),
                  const Expanded(
                    child: Text(
                      'Support access is currently active.',
                      style: TextStyle(
                          color: Color(0xFF7A6200),
                          fontWeight: FontWeight.w600,
                          fontSize: 13),
                    ),
                  ),
                  TextButton(
                    onPressed: () => _revokeGrant(ticket.ticketId),
                    style: TextButton.styleFrom(
                        foregroundColor: Colors.red.shade700),
                    child: const Text('Revoke'),
                  ),
                ],
              ),
            ),
          ] else if (ticket.status == TicketStatus.open ||
              ticket.status == TicketStatus.inProgress ||
              ticket.status == TicketStatus.waitingOnUser) ...[
            const SizedBox(height: 16),
            OutlinedButton.icon(
              onPressed: () => _showGrantDialog(ticket),
              icon: const Icon(Icons.vpn_key_outlined, size: 16),
              label: const Text('Grant Temporary Support Access'),
              style: OutlinedButton.styleFrom(
                foregroundColor: const Color(0xFF1967D2),
                side: const BorderSide(color: Color(0xFF1967D2)),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.all(40),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E6E9)),
      ),
      child: const Center(
        child: Column(
          children: [
            Icon(Icons.inbox_outlined, size: 48, color: Color(0xFFB0B4C1)),
            SizedBox(height: 12),
            Text('No tickets yet',
                style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF5A5C69))),
            SizedBox(height: 6),
            Text('Submit a ticket from Customer Service and it will appear here.',
                style: TextStyle(color: Color(0xFF8A8C96), fontSize: 13)),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorBanner(String error) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFFFF0F0),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.red.shade200),
      ),
      child: Row(
        children: [
          Icon(Icons.error_outline, color: Colors.red.shade600, size: 20),
          const SizedBox(width: 12),
          Expanded(
              child: Text(error,
                  style: TextStyle(color: Colors.red.shade800, fontSize: 13))),
          TextButton(
            onPressed: _loadTickets,
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Color _statusColor(TicketStatus s) {
    switch (s) {
      case TicketStatus.open:
        return const Color(0xFF1967D2);
      case TicketStatus.inProgress:
        return const Color(0xFFE37400);
      case TicketStatus.waitingOnUser:
        return const Color(0xFF7B61FF);
      case TicketStatus.resolved:
        return const Color(0xFF34A853);
      case TicketStatus.closed:
        return const Color(0xFF8A8C96);
    }
  }

  String _formatDate(DateTime dt) {
    return '${dt.year}-${dt.month.toString().padLeft(2, '0')}-${dt.day.toString().padLeft(2, '0')}';
  }
}

// ── Grant dialog ──────────────────────────────────────────────────────────

class _GrantDialog extends StatefulWidget {
  final HelpTicket ticket;
  const _GrantDialog({required this.ticket});

  @override
  State<_GrantDialog> createState() => _GrantDialogState();
}

class _GrantDialogState extends State<_GrantDialog> {
  int _hours = 48;

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Row(
        children: [
          Icon(Icons.vpn_key_outlined, color: Color(0xFF1967D2)),
          SizedBox(width: 8),
          Text('Grant Support Access'),
        ],
      ),
      content: SizedBox(
        width: 480,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFF0F4FF),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Text(
                '🔒  This grants temporary read-only access to your selected coins. '
                'No financial data (cost, value, notes) is ever visible to support. '
                'You can revoke at any time.',
                style: TextStyle(color: Color(0xFF1967D2), fontSize: 13),
              ),
            ),
            const SizedBox(height: 20),
            const Text('Grant Duration',
                style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
            const SizedBox(height: 8),
            DropdownButtonFormField<int>(
              initialValue: _hours,

              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                contentPadding:
                    EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              ),
              items: const [
                DropdownMenuItem(value: 2, child: Text('2 hours')),
                DropdownMenuItem(value: 8, child: Text('8 hours')),
                DropdownMenuItem(value: 24, child: Text('24 hours')),
                DropdownMenuItem(value: 48, child: Text('48 hours (max)')),
              ],
              onChanged: (v) => setState(() => _hours = v!),
            ),
            const SizedBox(height: 16),
            const Text(
              'Coin Access Scope',
              style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
            ),
            const SizedBox(height: 8),
            const Text(
              'This initial grant gives support visibility into your ticket description '
              'and diagnostic data only — no coin details. '
              'After submitting, you can expand access from My Tickets if needed.',
              style: TextStyle(color: Color(0xFF5A5C69), fontSize: 13),
            ),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Cancel'),
        ),
        ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF1967D2),
            foregroundColor: Colors.white,
          ),
          onPressed: () => Navigator.pop(context, {
            'duration_hours': _hours,
            'coin_ids': <String>[],
          }),
          child: const Text('Issue Grant'),
        ),
      ],
    );
  }
}
