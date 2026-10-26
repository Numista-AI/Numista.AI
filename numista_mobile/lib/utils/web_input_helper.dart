// lib/utils/web_input_helper.dart
// V8.9 FIX 3 & FIX 2: Sets inputmode STATICALLY per field.
// Focus-based swapping was removed to eliminate dropped first characters (FIX 2)
// and inverted numeric keypad states (FIX 3).
//
// Static mappings:
// - Year field: inputmode="numeric"
// - Qty field:  inputmode="numeric"
// - Cost field: inputmode="decimal"
// - All text fields: no inputmode set (null)


class WebInputHelper {
  /// Instantiable for unit tests and attribute inspection.
  WebInputHelper();

  static const Map<String, String?> staticFieldInputModes = {
    'Year': 'numeric',
    'Quantity': 'numeric',
    'Qty': 'numeric',
    'Cost': 'decimal',
    'Mint Mark': null,
    'Denomination': null,
    'Program/Series': null,
    'Theme/Subject': null,
    'Variety': null,
    'Condition': null,
    'Retailer/Website': null,
    'Retailer Invoice #': null,
    'Storage Location': null,
    'Notes': null,
  };

  /// Returns the static inputmode for a field name, or null if standard text.
  static String? inputModeForField(String fieldName) => staticFieldInputModes[fieldName];

  /// Returns the static attribute map per field type for testing and inspection.
  Map<String, String?> get attributeMap => Map.unmodifiable(staticFieldInputModes);

  /// Sets static inputmode attributes on DOM elements per field type.
  static void applyStaticInputModes() {
    // Disabled in V8.11 in favor of index.html JavaScript injection
  }

  /// Deprecated focus-based hook, now a safe no-op to prevent focus loss / character dropping.
  static void setActiveInputMode(String mode) {
    // Focus-based swapping removed in V8.9 to prevent dropped first character (FIX 2)
    // and inverted numeric keypad (FIX 3).
  }
}

