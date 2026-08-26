import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:file_picker/file_picker.dart';
// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;
import 'dart:typed_data';
import 'dart:math';
import '../services/auth_service.dart';
import '../services/ticket_service.dart';
import '../models/ticket_model.dart';


class CustomerServiceScreen extends StatefulWidget {
  /// Called when the user taps "My Tickets" from the success banner or nav link.
  final VoidCallback? onNavigateToTickets;
  const CustomerServiceScreen({super.key, this.onNavigateToTickets});

  @override
  State<CustomerServiceScreen> createState() => _CustomerServiceScreenState();
}

class _CustomerServiceScreenState extends State<CustomerServiceScreen> {
  final _dmMessageController = TextEditingController();
  final _fbMessageController = TextEditingController();
  final _tkSubjectController = TextEditingController();
  final _tkDescController = TextEditingController();
  String _feedbackType = 'Bug Report';
  String _ticketCategory = 'bug_report';
  bool _dmSubmitting = false;
  bool _fbSubmitting = false;
  bool _tkSubmitting = false;
  String? _dmSuccess;
  String? _fbSuccess;
  String? _tkSuccess;


  @override
  void dispose() {
    _dmMessageController.dispose();
    _fbMessageController.dispose();
    _tkSubjectController.dispose();
    _tkDescController.dispose();
    super.dispose();
  }

  Future<void> _submitTicket() async {
    final subject = _tkSubjectController.text.trim();
    final desc = _tkDescController.text.trim();
    if (subject.isEmpty) {
      _showError('Please enter a subject for your ticket.');
      return;
    }
    if (desc.isEmpty) {
      _showError('Please describe the issue before submitting.');
      return;
    }
    setState(() => _tkSubmitting = true);
    try {
      await TicketService.createTicket(
        subject: subject,
        description: desc,
        category: _ticketCategory,
        appVersion: '',
      );
      _tkSubjectController.clear();
      _tkDescController.clear();
      setState(() {
        _tkSubmitting = false;
        _tkSuccess = 'Ticket submitted! We\'ll respond as soon as possible. '
            'Track progress in My Tickets.';
      });
    } catch (e) {
      setState(() => _tkSubmitting = false);
      _showError('Couldn\'t submit ticket. Please try again or email customerservice@numista.ai');
    }
  }

  Future<void> _submitDirectMessage() async {
    final msg = _dmMessageController.text.trim();
    if (msg.isEmpty) {
      _showError('Please enter a message before submitting.');
      return;
    }
    setState(() => _dmSubmitting = true);
    try {
      final uid = _generateId();
      await FirebaseFirestore.instance.collection('feedback').doc(uid).set({
        'id': uid,
        'user_email': AuthService.userEmail,
        'type': 'Direct Message',
        'message': msg,
        'status': 'New',
        'created_at': FieldValue.serverTimestamp(),
      });
      _dmMessageController.clear();
      setState(() {
        _dmSubmitting = false;
        _dmSuccess = 'Message sent! We will respond to your registered email, or you can reach us directly at customerservice@numista.ai';
      });
    } catch (e) {
      setState(() => _dmSubmitting = false);
      _showError('Couldn\'t send your message. Please email us directly at customerservice@numista.ai');
    }
  }

  Future<void> _submitFeedback() async {
    final msg = _fbMessageController.text.trim();
    if (msg.isEmpty) {
      _showError('Please enter a message before submitting.');
      return;
    }
    setState(() => _fbSubmitting = true);
    try {
      final uid = _generateId();
      await FirebaseFirestore.instance.collection('feedback').doc(uid).set({
        'id': uid,
        'user_email': AuthService.userEmail,
        'type': _feedbackType,
        'message': msg,
        'status': 'New',
        'created_at': FieldValue.serverTimestamp(),
      });
      _fbMessageController.clear();
      setState(() {
        _fbSubmitting = false;
        _fbSuccess = 'Feedback submitted — thank you! You can also email customerservice@numista.ai for a faster response.';
      });
    } catch (e) {
      setState(() => _fbSubmitting = false);
      _showError('Couldn\'t submit. Please email customerservice@numista.ai directly.');
    }
  }

  void _showError(String msg) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg), backgroundColor: Colors.red.shade700),
    );
  }

  String _generateId() {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    final rng = Random.secure();
    return List.generate(28, (_) => chars[rng.nextInt(chars.length)]).join();
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Header ────────────────────────────────────────────────────────
          Row(children: [
            const Text(
              'Customer Service',
              style: TextStyle(
                fontSize: 32, fontWeight: FontWeight.w900,
                fontStyle: FontStyle.italic, color: Color(0xFF31333F),
              ),
            ),
            const SizedBox(width: 12),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: const Color(0xFF3B82F6),
                borderRadius: BorderRadius.circular(6),
              ),
              child: const Text('SUPPORT & FEEDBACK',
                  style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w700, letterSpacing: 0.5)),
            ),
          ]),
          const SizedBox(height: 8),
          const Text(
            "We're here to help! If you have any questions, want to report a bug, or have a feature request, please let us know.",
            style: TextStyle(color: Color(0xFF5A5C69), fontSize: 14),
          ),
          const SizedBox(height: 40),

          // ── Privacy notice ────────────────────────────────────────────────
          Container(
            padding: const EdgeInsets.all(16),
            margin: const EdgeInsets.only(bottom: 24),
            decoration: BoxDecoration(
              color: const Color(0xFFF0F4FF),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFFBFD0FB)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.lock_outline, color: Color(0xFF1967D2), size: 18),
                const SizedBox(width: 10),
                const Expanded(
                  child: Text(
                    '🔒  Privacy First — Submitting a ticket never gives Numista.AI staff access to your collection. '
                    'If needed, you can issue a temporary, scoped support grant from My Tickets — '
                    'you control exactly what can be seen and for how long.',
                    style: TextStyle(color: Color(0xFF1967D2), fontSize: 13),
                  ),
                ),
              ],
            ),
          ),

          // ── Help Ticket card (full width) ─────────────────────────────────
          _buildCard(
            icon: Icons.confirmation_number_outlined,
            title: 'Submit a Help Ticket',
            subtitle: 'Track your issue, share diagnostic details, and get a written response.',
            child: _tkSuccess != null
                ? Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildSuccessBanner(_tkSuccess!),
                      const SizedBox(height: 12),
                      if (widget.onNavigateToTickets != null)
                        TextButton.icon(
                          onPressed: widget.onNavigateToTickets,
                          icon: const Icon(Icons.receipt_long_outlined, size: 16),
                          label: const Text('View My Tickets'),
                          style: TextButton.styleFrom(
                            foregroundColor: const Color(0xFF1967D2),
                          ),
                        ),
                    ],
                  )
                : Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildLabel('Category'),
                      const SizedBox(height: 8),
                      DropdownButtonFormField<String>(
                        initialValue: _ticketCategory,
                        decoration: _inputDecoration(null).copyWith(
                          contentPadding:
                              const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                        ),
                        style: const TextStyle(color: Color(0xFF31333F), fontSize: 14),
                        dropdownColor: Colors.white,
                        items: kTicketCategories.entries
                            .map((e) => DropdownMenuItem(
                                  value: e.key,
                                  child: Text(e.value),
                                ))
                            .toList(),
                        onChanged: (v) => setState(() => _ticketCategory = v!),
                      ),
                      const SizedBox(height: 16),
                      _buildLabel('Subject'),
                      const SizedBox(height: 8),
                      TextField(
                        controller: _tkSubjectController,
                        maxLines: 1,
                        maxLength: 120,
                        style: const TextStyle(color: Color(0xFF31333F), fontSize: 14),
                        decoration: _inputDecoration('Brief summary of the issue'),
                      ),
                      const SizedBox(height: 16),
                      _buildLabel('Description'),
                      const SizedBox(height: 8),
                      TextField(
                        controller: _tkDescController,
                        maxLines: 5,
                        style: const TextStyle(color: Color(0xFF31333F), fontSize: 14),
                        decoration: _inputDecoration(
                            'Describe the issue in detail. Steps to reproduce, what you expected vs what happened...'),
                      ),
                      const SizedBox(height: 20),
                      Row(
                        children: [
                          Expanded(
                            child: ElevatedButton.icon(
                              onPressed: _tkSubmitting ? null : _submitTicket,
                              icon: _tkSubmitting
                                  ? const SizedBox(
                                      width: 16,
                                      height: 16,
                                      child: CircularProgressIndicator(
                                          strokeWidth: 2, color: Colors.white))
                                  : const Icon(Icons.send_rounded, size: 18),
                              label: Text(
                                  _tkSubmitting ? 'Submitting…' : 'Submit Ticket'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF1967D2),
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(vertical: 14),
                                shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(8)),
                              ),
                            ),
                          ),
                          if (widget.onNavigateToTickets != null) ...[
                            const SizedBox(width: 12),
                            TextButton.icon(
                              onPressed: widget.onNavigateToTickets,
                              icon: const Icon(Icons.receipt_long_outlined, size: 16),
                              label: const Text('My Tickets'),
                              style: TextButton.styleFrom(
                                foregroundColor: const Color(0xFF1967D2),
                              ),
                            ),
                          ],
                        ],
                      ),
                    ],
                  ),
          ),
          const SizedBox(height: 32),

          // ── Two-column layout ─────────────────────────────────────────────
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── Direct Message ──────────────────────────────────────────
              Expanded(
                child: _buildCard(
                  icon: Icons.message_outlined,
                  title: 'Direct Message Eric',
                  subtitle: 'For immediate assistance, send Eric a direct message:',
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (_dmSuccess != null)
                        _buildSuccessBanner(_dmSuccess!)
                      else ...[
                        _buildLabel('Your Message'),
                        const SizedBox(height: 8),
                        TextField(
                          controller: _dmMessageController,
                          maxLines: 6,
                          style: const TextStyle(color: Color(0xFF31333F), fontSize: 14),
                          decoration: _inputDecoration('Hi Eric, I need help with...'),
                        ),
                        const SizedBox(height: 20),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            onPressed: _dmSubmitting ? null : _submitDirectMessage,
                            icon: _dmSubmitting
                                ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                                : const Icon(Icons.send_rounded, size: 18),
                            label: Text(_dmSubmitting ? 'Sending...' : 'Send Message'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF1967D2),
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 32),

              // ── Feedback Form ───────────────────────────────────────────
              Expanded(
                child: _buildCard(
                  icon: Icons.rate_review_outlined,
                  title: 'Send Feedback',
                  subtitle: 'Bug reports, feature requests, or general inquiries:',
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (_fbSuccess != null)
                        _buildSuccessBanner(_fbSuccess!)
                      else ...[
                        _buildLabel('Topic'),
                        const SizedBox(height: 8),
                        DropdownButtonFormField<String>(
                          initialValue: _feedbackType,
                          decoration: _inputDecoration(null).copyWith(
                            contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                          ),
                          style: const TextStyle(color: Color(0xFF31333F), fontSize: 14),
                          dropdownColor: Colors.white,
                          items: ['Bug Report', 'Feature Request', 'General Inquiry']
                              .map((t) => DropdownMenuItem(value: t, child: Text(t)))
                              .toList(),
                          onChanged: (v) => setState(() => _feedbackType = v!),
                        ),
                        const SizedBox(height: 16),
                        _buildLabel('Message'),
                        const SizedBox(height: 8),
                        TextField(
                          controller: _fbMessageController,
                          maxLines: 5,
                          style: const TextStyle(color: Color(0xFF31333F), fontSize: 14),
                          decoration: _inputDecoration('Describe your issue or suggestion here...'),
                        ),
                        const SizedBox(height: 20),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton.icon(
                            onPressed: _fbSubmitting ? null : _submitFeedback,
                            icon: _fbSubmitting
                                ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                                : const Icon(Icons.upload_rounded, size: 18),
                            label: Text(_fbSubmitting ? 'Submitting...' : 'Submit Feedback'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF34A853),
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 40),

          // ── Contact Info Footer ────────────────────────────────────────────
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: const Color(0xFFF0F4FF),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFFBFD0FB)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.info_outline, color: Color(0xFF1967D2), size: 20),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Tooltip(
                        message: 'Click to email · Right-click to copy address',
                        child: MouseRegion(
                          cursor: SystemMouseCursors.click,
                          child: GestureDetector(
                            onTap: () async {
                              final uri = Uri.parse('mailto:customerservice@numista.ai');
                              if (await canLaunchUrl(uri)) {
                                await launchUrl(uri);
                              } else {
                                await Clipboard.setData(const ClipboardData(text: 'customerservice@numista.ai'));
                                if (context.mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(content: Text('Email address copied to clipboard!')),
                                  );
                                }
                              }
                            },
                            onSecondaryTap: () async {
                              await Clipboard.setData(const ClipboardData(text: 'customerservice@numista.ai'));
                              if (context.mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(content: Text('Email address copied to clipboard!')),
                                );
                              }
                            },
                            child: const Text(
                              '✉  customerservice@numista.ai',
                              style: TextStyle(
                                color: Color(0xFF1967D2),
                                fontSize: 14,
                                fontWeight: FontWeight.w700,
                                decoration: TextDecoration.underline,
                                decorationColor: Color(0xFF1967D2),
                              ),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 4),
                      const Text(
                        'You can also connect with Eric directly on LinkedIn at linkedin.com/in/ericdseaman',
                        style: TextStyle(color: Color(0xFF1967D2), fontSize: 13),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required Widget child,
  }) {
    return Container(
      padding: const EdgeInsets.all(28),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E6E9)),
        boxShadow: [
          BoxShadow(color: Colors.black.withValues(alpha: 0.04), blurRadius: 8, offset: const Offset(0, 2)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Icon(icon, color: const Color(0xFF1967D2), size: 22),
            const SizedBox(width: 10),
            Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: Color(0xFF31333F))),
          ]),
          const SizedBox(height: 8),
          Text(subtitle, style: const TextStyle(color: Color(0xFF5A5C69), fontSize: 13)),
          const SizedBox(height: 24),
          child,
        ],
      ),
    );
  }

  Widget _buildLabel(String text) {
    return Text(text, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF31333F)));
  }

  InputDecoration _inputDecoration(String? hint) {
    return InputDecoration(
      hintText: hint,
      hintStyle: const TextStyle(color: Color(0xFFA0A3AB), fontSize: 13),
      filled: true,
      fillColor: const Color(0xFFF8F9FB),
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Color(0xFFDDE1E7))),
      enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Color(0xFFDDE1E7))),
      focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Color(0xFF1967D2), width: 2)),
      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
    );
  }

  Widget _buildSuccessBanner(String message) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFFE6F4EA),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFF34A853)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.check_circle_outline, color: Color(0xFF34A853), size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Text(message, style: const TextStyle(color: Color(0xFF1E6B33), fontSize: 13)),
          ),
        ],
      ),
    );
  }
}
