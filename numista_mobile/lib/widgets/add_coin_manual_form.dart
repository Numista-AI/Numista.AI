import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class AddCoinManualForm extends StatefulWidget {
  final Function(Map<String, dynamic>) onSubmit;
  final bool isProcessing;

  const AddCoinManualForm({
    super.key,
    required this.onSubmit,
    this.isProcessing = false,
  });

  @override
  State<AddCoinManualForm> createState() => _AddCoinManualFormState();
}

class _AddCoinManualFormState extends State<AddCoinManualForm> {
  final _formKey = GlobalKey<FormState>();

  // Controllers for fields that need real-time transformation
  final _mintCtrl = TextEditingController();

  final Map<String, dynamic> _formData = {
    'Year': '',
    'Mint Mark': '',
    'Denomination': '',
    'Program/Series': '',
    'Theme/Subject': '',
    'Variety': '',
    'Condition': 'Ungraded',
    'Cost': '',
    'Quantity': '1',
    'Storage Location': '',
    'Retailer/Website': '',
    'Retailer Invoice #': '',
    'Notes': '',
  };

  static const _accent = Color(0xFF3B82F6);
  Color get _border => Theme.of(context).brightness == Brightness.dark ? const Color(0xFF334155) : const Color(0xFFCBD5E1);
  static const _labelStyle = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.w600,
    color: Color(0xFF64748B),
    letterSpacing: 0.3,
  );

  @override
  void dispose() {
    _mintCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Section: Identity ─────────────────────────────────────────────
          _sectionHeader('Identity', Icons.tag),
          const SizedBox(height: 12),
          Row(children: [
            Expanded(flex: 2, child: _buildField(context, 'Year', 'e.g. 1921',
                keyboardType: TextInputType.number)),
            const SizedBox(width: 12),
            Expanded(child: _buildMintMarkField(context)),
            const SizedBox(width: 12),
            Expanded(flex: 2, child: _buildField(context, 'Denomination', 'e.g. \$1, 25c')),
          ]),
          const SizedBox(height: 12),
          _buildField(context, 'Program/Series', 'e.g. Morgan Silver Dollar'),
          _buildField(context, 'Theme/Subject', 'e.g. Liberty Head'),
          _buildField(context, 'Variety', 'e.g. Double Die, Over Mint Mark'),

          const SizedBox(height: 8),
          // ── Section: Condition ────────────────────────────────────────────
          _sectionHeader('Condition & Grading', Icons.grade),
          const SizedBox(height: 12),
          _buildField(context, 'Condition', 'e.g. MS65, AU58, Ungraded'),

          const SizedBox(height: 8),
          // ── Section: Purchase ─────────────────────────────────────────────
          _sectionHeader('Purchase Details', Icons.receipt_long),
          const SizedBox(height: 12),
          Row(children: [
            Expanded(child: _buildField(context, 'Cost', 'e.g. \$25.00',
                keyboardType: TextInputType.number,
                prefixText: '\$')),
            const SizedBox(width: 12),
            Expanded(child: _buildField(context, 'Quantity', 'e.g. 1',
                keyboardType: TextInputType.number)),
          ]),
          _buildField(context, 'Retailer/Website', 'e.g. APMEX, eBay'),
          _buildField(context, 'Retailer Invoice #', 'e.g. INV-9988'),

          const SizedBox(height: 8),
          // ── Section: Storage ──────────────────────────────────────────────
          _sectionHeader('Storage & Notes', Icons.inventory_2_outlined),
          const SizedBox(height: 12),
          _buildField(context, 'Storage Location', 'e.g. Safe Box A, Folder 2'),
          _buildField(context, 'Notes', 'Any additional notes', maxLines: 3),

          const SizedBox(height: 32),

          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: widget.isProcessing ? null : _submit,
              icon: widget.isProcessing
                  ? const SizedBox(
                      height: 18, width: 18,
                      child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Icon(Icons.check_circle_outline, size: 18),
              label: Text(
                widget.isProcessing ? 'Saving…' : 'Submit to Collection',
                style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: _accent,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 18),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _submit() {
    if (_formKey.currentState!.validate()) {
      _formKey.currentState!.save();
      // Ensure mint mark is always uppercase
      _formData['Mint Mark'] = (_formData['Mint Mark'] as String).toUpperCase();
      widget.onSubmit(_formData);
    }
  }

  Widget _sectionHeader(String title, IconData icon) {
    return Padding(
      padding: const EdgeInsets.only(top: 8, bottom: 4),
      child: Row(children: [
        Icon(icon, size: 16, color: const Color(0xFF94A3B8)),
        const SizedBox(width: 6),
        Text(title.toUpperCase(), style: _labelStyle),
        const SizedBox(width: 8),
        Expanded(child: Divider(color: _border)),
      ]),
    );
  }

  /// Special Mint Mark field — auto-uppercase on every keystroke.
  Widget _buildMintMarkField(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: TextFormField(
        controller: _mintCtrl,
        textCapitalization: TextCapitalization.characters,
        inputFormatters: [UpperCaseTextFormatter()],
        style: TextStyle(color: Theme.of(context).brightness == Brightness.dark ? Colors.white : const Color(0xFF1E293B)),
        decoration: _inputDeco(context, 'Mint Mark', 'D, S, P, W'),
        onSaved: (val) => _formData['Mint Mark'] = (val ?? '').toUpperCase(),
      ),
    );
  }

  Widget _buildField(
    BuildContext context,
    String key,
    String hint, {
    TextInputType keyboardType = TextInputType.text,
    String? prefixText,
    int maxLines = 1,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: TextFormField(
        initialValue: _formData[key]?.toString(),
        keyboardType: keyboardType,
        maxLines: maxLines,
        style: TextStyle(color: Theme.of(context).brightness == Brightness.dark ? Colors.white : const Color(0xFF1E293B)),
        decoration: _inputDeco(context, key, hint, prefixText: prefixText),
        onSaved: (val) => _formData[key] = val ?? '',
      ),
    );
  }

  InputDecoration _inputDeco(BuildContext context, String label, String hint, {String? prefixText}) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final borderCol = isDark ? const Color(0xFF334155) : const Color(0xFFCBD5E1);

    return InputDecoration(
      labelText: label,
      hintText: hint,
      prefixText: prefixText,
      prefixStyle: TextStyle(color: isDark ? Colors.white : const Color(0xFF1E293B)),
      labelStyle: const TextStyle(color: Color(0xFF64748B), fontSize: 13),
      hintStyle: const TextStyle(color: Color(0xFFADB5BD), fontSize: 13),
      filled: true,
      fillColor: isDark ? const Color(0xFF0F172A) : const Color(0xFFF8FAFC),
      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
      border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: borderCol)),
      enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: borderCol)),
      focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: _accent, width: 1.5)),
    );
  }
}

/// Forces all typed characters to uppercase immediately.
class UpperCaseTextFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
      TextEditingValue oldValue, TextEditingValue newValue) {
    return newValue.copyWith(text: newValue.text.toUpperCase());
  }
}
