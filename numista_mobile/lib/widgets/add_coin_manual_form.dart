import 'package:flutter/material.dart';

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
  final Map<String, String> _formData = {
    'Year': '',
    'Mint Mark': '',
    'Denomination': '',
    'Program/Series': '',
    'Theme/Subject': '',
    'Variety': '',
    'Condition': 'Ungraded',
    'Purchase Cost': '\$0.00',
    'Quantity': '1',
    'Storage Location': '',
  };

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        children: [
          _buildField('Year', 'e.g. 2024'),
          _buildField('Retailer Invoice #', 'e.g. \$INV-9988'),
          _buildField('Mint Mark', 'e.g. W, S, P, D'),
          _buildField('Denomination', 'e.g. \$1, 25c'),
          _buildField('Program/Series', 'e.g. American Women Quarters'),
          _buildField('Theme/Subject', 'e.g. Dr. Pauli Murray'),
          _buildField('Variety', 'e.g. Double Die'),
          _buildField('Condition', 'e.g. MS65, PR70'),
          _buildField('Purchase Cost', 'e.g. \$25.00'),
          _buildField('Quantity', 'numerical'),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: widget.isProcessing ? null : () {
                if (_formKey.currentState!.validate()) {
                  _formKey.currentState!.save();
                  widget.onSubmit(_formData);
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF3B82F6),
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: widget.isProcessing 
                ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                : const Text('Submit to Collection'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildField(String key, String hint) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: TextFormField(
        decoration: InputDecoration(
          labelText: key,
          hintText: hint,
          border: const OutlineInputBorder(),
        ),
        initialValue: _formData[key],
        onSaved: (val) => _formData[key] = val ?? '',
      ),
    );
  }
}
