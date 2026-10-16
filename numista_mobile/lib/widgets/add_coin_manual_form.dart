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

  // ── Persistent controllers (created in initState, disposed in dispose) ──────
  // One controller per field. This ensures text survives any parent rebuild
  // (tab switch, IndexedStack rebuild, setState on _isProcessing, keyboard
  // appearance changes) without losing the first character or blanking Year.
  // The real observed trigger: the ManualEntry screen is pushed as a full-screen
  // Scaffold route via showManualFullScreen in add_coins_hub.dart. If the route
  // is popped and re-pushed (e.g. user goes back and re-enters), the State is
  // remounted and _formData defaults are used. Controllers keep values stable
  // within a single mount.
  late final TextEditingController _yearCtrl;
  late final TextEditingController _mintCtrl;
  late final TextEditingController _denomCtrl;
  late final TextEditingController _programCtrl;
  late final TextEditingController _themeCtrl;
  late final TextEditingController _varietyCtrl;
  late final TextEditingController _conditionCtrl;
  late final TextEditingController _costCtrl;
  late final TextEditingController _qtyCtrl;
  late final TextEditingController _retailerCtrl;
  late final TextEditingController _invoiceCtrl;
  late final TextEditingController _storageCtrl;
  late final TextEditingController _notesCtrl;

  // V8.7 FIX Item 3: FocusNodes for numeric fields.
  // On web, Flutter's engine sets inputmode via go9() (go9(){return"numeric"}
  // for integer, go9(){return"decimal"} for decimal per built main.dart.js).
  // However, the DOM setup code (b2p()) explicitly removes inputmode for all
  // non-email/password types. We re-inject it on focus using WebInputHelper.
  late final FocusNode _yearFocus;
  late final FocusNode _costFocus;
  late final FocusNode _qtyFocus;


  static const _accent = Color(0xFF3B82F6);
  Color get _border => Theme.of(context).brightness == Brightness.dark
      ? const Color(0xFF334155)
      : const Color(0xFFCBD5E1);
  static const _labelStyle = TextStyle(
    fontSize: 12,
    fontWeight: FontWeight.w600,
    color: Color(0xFF64748B),
    letterSpacing: 0.3,
  );

  // Condition is pre-populated; Quantity is intentionally absent so _qtyCtrl
  // starts empty (hintText '1' shows). Submitting an empty Quantity defaults to
  // '1' in _submit(). This prevents the "typing 3 gives 13" regression.
  final _formData = <String, dynamic>{'Condition': 'Ungraded'};

  @override
  void initState() {
    super.initState();
    _yearCtrl      = TextEditingController(text: _formData['Year'] as String? ?? '');
    _mintCtrl      = TextEditingController(text: _formData['Mint Mark'] as String? ?? '');
    _denomCtrl     = TextEditingController(text: _formData['Denomination'] as String? ?? '');
    _programCtrl   = TextEditingController(text: _formData['Program/Series'] as String? ?? '');
    _themeCtrl     = TextEditingController(text: _formData['Theme/Subject'] as String? ?? '');
    _varietyCtrl   = TextEditingController(text: _formData['Variety'] as String? ?? '');
    _conditionCtrl = TextEditingController(text: _formData['Condition'] as String? ?? 'Ungraded');
    _costCtrl      = TextEditingController(text: _formData['Cost'] as String? ?? '');
    _qtyCtrl       = TextEditingController(text: _formData['Quantity'] as String? ?? '');
    _retailerCtrl  = TextEditingController(text: _formData['Retailer/Website'] as String? ?? '');
    _invoiceCtrl   = TextEditingController(text: _formData['Retailer Invoice #'] as String? ?? '');
    _storageCtrl   = TextEditingController(text: _formData['Storage Location'] as String? ?? '');
    _notesCtrl     = TextEditingController(text: _formData['Notes'] as String? ?? '');

    // V8.9 FIX 3: Static inputmode assignment per field.
    // FocusNode listeners removed to eliminate dropped first characters (FIX 2)
    // and inverted keypad states (FIX 3).
    _yearFocus = FocusNode();
    _costFocus = FocusNode();
    _qtyFocus  = FocusNode();
  }



  @override
  void dispose() {
    _yearCtrl.dispose();
    _mintCtrl.dispose();
    _denomCtrl.dispose();
    _programCtrl.dispose();
    _themeCtrl.dispose();
    _varietyCtrl.dispose();
    _conditionCtrl.dispose();
    _costCtrl.dispose();
    _qtyCtrl.dispose();
    _retailerCtrl.dispose();
    _invoiceCtrl.dispose();
    _storageCtrl.dispose();
    _notesCtrl.dispose();
    _yearFocus.dispose();
    _costFocus.dispose();
    _qtyFocus.dispose();
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
                controller: _yearCtrl,
                focusNode: _yearFocus,  // V8.7: inputmode="numeric" on web focus
                isRequired: true,
                keyboardType: const TextInputType.numberWithOptions(decimal: false),
                inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                onChanged: (val) {
                  if (RegExp(r'^\d{4}$').hasMatch(val.trim())) {
                    _formKey.currentState?.validate();
                  }
                },
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
            controller: _denomCtrl,
            isRequired: true,
          ),
          const SizedBox(height: 12),
          _buildField(
            context,
            'Program/Series',
            'e.g. Morgan Silver Dollar',
            controller: _programCtrl,
            isRequired: true,
          ),
          _buildField(context, 'Theme/Subject', 'e.g. Liberty Head',
              controller: _themeCtrl),
          _buildField(context, 'Variety', 'e.g. Double Die, Over Mint Mark',
              controller: _varietyCtrl),

          const SizedBox(height: 8),
          // ── Section: Condition ────────────────────────────────────────────
          _sectionHeader('Condition & Grading', Icons.grade),
          const SizedBox(height: 12),
          _buildField(context, 'Condition', 'e.g. MS65, AU58, Ungraded',
              controller: _conditionCtrl),

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
                controller: _costCtrl,
                focusNode: _costFocus,  // V8.7: inputmode="decimal" on web focus
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                inputFormatters: [FilteringTextInputFormatter.allow(RegExp(r'[0-9.]'))],
                prefixText: '\$ ',
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildField(
                context,
                'Quantity',
                '1',
                controller: _qtyCtrl,
                focusNode: _qtyFocus,  // V8.7: inputmode="numeric" on web focus
                keyboardType: const TextInputType.numberWithOptions(decimal: false),
                inputFormatters: [FilteringTextInputFormatter.digitsOnly],

              ),
            ),
          ]),
          _buildField(context, 'Retailer/Website', 'e.g. APMEX, eBay',
              controller: _retailerCtrl),
          _buildField(context, 'Retailer Invoice #', 'e.g. INV-9988',
              controller: _invoiceCtrl),

          const SizedBox(height: 8),
          // ── Section: Storage ──────────────────────────────────────────────
          _sectionHeader('Storage & Notes', Icons.inventory_2_outlined),
          const SizedBox(height: 12),
          _buildField(context, 'Storage Location', 'e.g. Safe Box A, Folder 2',
              controller: _storageCtrl),
          _buildField(context, 'Notes', 'Any additional notes',
              controller: _notesCtrl, maxLines: 3),

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
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
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

      // Read values from controllers (controllers are the source of truth).
      final formData = <String, dynamic>{
        'Year':               _yearCtrl.text.trim(),
        'Mint Mark':          _mintCtrl.text.toUpperCase(),
        'Denomination':       DenominationCanon.normalize(_denomCtrl.text.trim()),
        'Program/Series':     _programCtrl.text.trim(),
        'Theme/Subject':      _themeCtrl.text.trim(),
        'Variety':            _varietyCtrl.text.trim(),
        'Condition':          _conditionCtrl.text.trim(),
        'Cost':               _costCtrl.text.trim(),
        'Quantity':           _qtyCtrl.text.trim().isEmpty ? '1' : _qtyCtrl.text.trim(),
        'Retailer/Website':   _retailerCtrl.text.trim(),
        'Retailer Invoice #': _invoiceCtrl.text.trim(),
        'Storage Location':   _storageCtrl.text.trim(),
        'Notes':              _notesCtrl.text.trim(),
      };

      widget.onSubmit(formData);
      _resetForm();
    }
  }

  void _resetForm() {
    _formKey.currentState?.reset();
    _yearCtrl.clear();
    _mintCtrl.clear();
    _denomCtrl.clear();
    _programCtrl.clear();
    _themeCtrl.clear();
    _varietyCtrl.clear();
    _conditionCtrl.clear();
    _costCtrl.clear();
    _qtyCtrl.text = '1';
    _retailerCtrl.clear();
    _invoiceCtrl.clear();
    _storageCtrl.clear();
    _notesCtrl.clear();
    _formData.clear();
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
          ),
        ],
      ),
    );
  }

  Widget _buildField(
    BuildContext context,
    String key,
    String hint, {
    TextEditingController? controller,
    bool isRequired = false,
    FocusNode? focusNode,          // V8.7: for web inputmode injection
    TextInputType keyboardType = TextInputType.text,
    List<TextInputFormatter>? inputFormatters,
    String? prefixText,
    int maxLines = 1,
    ValueChanged<String>? onChanged,
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
            controller: controller,
            focusNode: focusNode,  // V8.7: triggers inputmode injection on focus
            initialValue: controller == null
                ? (_formData[key]?.toString().isNotEmpty == true ? _formData[key].toString() : null)
                : null,
            keyboardType: keyboardType,
            inputFormatters: inputFormatters,
            maxLines: maxLines,
            style: TextStyle(color: isDark ? Colors.white : const Color(0xFF1E293B)),
            decoration: _inputDeco(context, hint, prefixText: prefixText),
            validator: isRequired ? (val) => _validatorFor(key, val) : null,
            onSaved: (val) => _formData[key] = val ?? '',
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }

  /// Returns the validator message for a field.
  String? _validatorFor(String key, String? val) {
    final v = val?.trim() ?? '';
    if (v.isEmpty) {
      switch (key) {
        case 'Year':
          return 'Please enter the year on the coin, like 1921.';
        case 'Denomination':
          return 'Please enter the denomination, like Quarter Dollar.';
        case 'Program/Series':
          return 'Please enter the series name, like Morgan Silver Dollar.';
        default:
          return 'This field is required.';
      }
    }
    // Year extra: must be exactly 4 digits and not in the future
    if (key == 'Year') {
      if (!RegExp(r'^\d{4}$').hasMatch(v)) {
        return 'Year must be 4 digits, like 1921.';
      }
      final year = int.tryParse(v);
      final nextYear = DateTime.now().year + 1;
      if (year != null && year > nextYear) {
        return 'That year is in the future. Please check the year on the coin.';
      }
    }
    return null;
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
      errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: Color(0xFFEF4444))),
      focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: Color(0xFFEF4444), width: 1.5)),
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
