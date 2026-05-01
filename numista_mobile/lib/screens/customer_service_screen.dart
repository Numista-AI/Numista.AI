import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'dart:math';
import '../services/auth_service.dart';

class CustomerServiceScreen extends StatefulWidget {
  const CustomerServiceScreen({super.key});

  @override
  State<CustomerServiceScreen> createState() => _CustomerServiceScreenState();
}

class _CustomerServiceScreenState extends State<CustomerServiceScreen> {
  final _dmMessageController = TextEditingController();
  final _fbMessageController = TextEditingController();
  String _feedbackType = 'Bug Report';
  bool _dmSubmitting = false;
  bool _fbSubmitting = false;
  String? _dmSuccess;
  String? _fbSuccess;

  @override
  void dispose() {
    _dmMessageController.dispose();
    _fbMessageController.dispose();
    super.dispose();
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
        _dmSuccess = 'Thank you for your message! It has been sent to Eric. If you are logged in, you may receive a response at your registered email.';
      });
    } catch (e) {
      setState(() => _dmSubmitting = false);
      _showError('Failed to submit message. ($e)');
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
        _fbSuccess = 'Thank you for your feedback! It has been submitted successfully.';
      });
    } catch (e) {
      setState(() => _fbSubmitting = false);
      _showError('Failed to submit feedback. ($e)');
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
            child: Row(children: [
              const Icon(Icons.info_outline, color: Color(0xFF1967D2), size: 20),
              const SizedBox(width: 12),
              const Expanded(
                child: Text(
                  'You can also connect with Eric directly on LinkedIn at linkedin.com/in/ericdseaman',
                  style: TextStyle(color: Color(0xFF1967D2), fontSize: 13),
                ),
              ),
            ]),
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
