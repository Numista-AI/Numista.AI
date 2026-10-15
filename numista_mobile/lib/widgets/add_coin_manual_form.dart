import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../constants/denomination_canon.dart';

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
    'Quantity': '',
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
            Expanded(
              child: _buildField(
                context,
                'Year',
                'e.g. 1921',
                isRequired: true,
                keyboardType: TextInputType.number,
                inputFormatters: [FilteringTextInputFormatter.digitsOnly],
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildMintMarkField(context),
            ),
          ]),
          const SizedBox(height: 12),
          _buildField(
            context,
            'Denomination',
            'e.g. Quarter Dollar, Dime, Cent',
            isRequired: true,
          ),
          const SizedBox(height: 12),
          _buildField(
            context,
            'Program/Series',
            'e.g. Morgan Silver Dollar',
            isRequired: true,
          ),
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
            Expanded(
              child: _buildField(
                context,
                'Cost',
                '25.00',
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                prefixText: '\$ ',
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildField(
                context,
                'Quantity',
                '1',
                keyboardType: TextInputType.number,
                inputFormatters: [FilteringTextInputFormatter.digitsOnly],
              ),
            ),
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
            height: 56,
            child: ElevatedButton.icon(
              onPressed: widget.isProcessing ? null : _submit,
              icon: widget.isProcessing
                  ? const SizedBox(
                      height: 20, width: 20,
                      child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Icon(Icons.check_circle_outline, size: 20),
              label: Text(
                widget.isProcessing ? 'Saving…' : 'Save to My Collection',
                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: _accent,
                foregroundColor: Colors.white,
                minimumSize: const Size(double.infinity, 56),
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
      // GI-NOM-01: Normalize manual entry to formal US Mint denomination
      final rawDenom = _formData['Denomination'] as String? ?? '';
      _formData['Denomination'] = DenominationCanon.normalize(rawDenom);
      // Qty prefill bug fix: default to '1' if left blank
      final qtyStr = _formData['Quantity']?.toString().trim() ?? '';
      _formData['Quantity'] = qtyStr.isEmpty ? '1' : qtyStr;
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
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final labelColor = isDark ? Colors.white : const Color(0xFF0F172A);

    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Mint Mark',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: labelColor,
            ),
          ),
          const SizedBox(height: 6),
          TextFormField(
            controller: _mintCtrl,
            textCapitalization: TextCapitalization.characters,
            inputFormatters: [UpperCaseTextFormatter()],
            style: TextStyle(color: isDark ? Colors.white : const Color(0xFF1E293B)),
            decoration: _inputDeco(context, 'D, S, P, W'),
            onSaved: (val) => _formData['Mint Mark'] = (val ?? '').toUpperCase(),
          ),
        ],
      ),
    );
  }

  Widget _buildField(
    BuildContext context,
    String key,
    String hint, {
    bool isRequired = false,
    TextInputType keyboardType = TextInputType.text,
    List<TextInputFormatter>? inputFormatters,
    String? prefixText,
    int maxLines = 1,
  }) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final labelColor = isDark ? Colors.white : const Color(0xFF0F172A);

    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          RichText(
            text: TextSpan(
              text: key,
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: labelColor,
              ),
              children: isRequired
                  ? const [
                      TextSpan(
                        text: ' *',
                        style: TextStyle(
                          color: Color(0xFFEF4444),
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                        ),
                      ),
                    ]
                  : null,
            ),
          ),
          const SizedBox(height: 6),
          TextFormField(
            initialValue: _formData[key]?.toString().isNotEmpty == true
                ? _formData[key].toString()
                : null,
            keyboardType: keyboardType,
            inputFormatters: inputFormatters,
            maxLines: maxLines,
            style: TextStyle(color: isDark ? Colors.white : const Color(0xFF1E293B)),
            decoration: _inputDeco(context, hint, prefixText: prefixText),
            onSaved: (val) => _formData[key] = val ?? '',
          ),
        ],
      ),
    );
  }

  InputDecoration _inputDeco(BuildContext context, String hint, {String? prefixText}) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final borderCol = isDark ? const Color(0xFF334155) : const Color(0xFFCBD5E1);

    return InputDecoration(
      hintText: hint,
      prefixText: prefixText,
      prefixStyle: TextStyle(color: isDark ? Colors.white : const Color(0xFF1E293B)),
      hintStyle: const TextStyle(color: Color(0xFFADB5BD), fontSize: 14),
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
