import 'dart:convert';

/// Systemic text sanitizer for Numista.AI.
/// Fixes double-encoded UTF-8 and Latin-1 mojibake across coin names,
/// denominations, descriptions, notes, and export payloads.
class TextSanitizer {
  TextSanitizer._();

  /// Fixes mojibake caused by UTF-8 bytes being incorrectly interpreted as Latin-1 (ISO-8859-1)
  /// or double-encoded UTF-8. For example:
  /// 'Ã‚Â£2' -> '£2'
  /// 'Â£' -> '£'
  /// 'Ã‚' -> ''
  static String fixMojibake(String input) {
    if (input.isEmpty) return input;
    if (!input.contains('Ã') && !input.contains('Â')) return input;

    String current = input;
    // Attempt up to 2 rounds of recovery if double-encoded
    for (int i = 0; i < 2; i++) {
      if (!current.contains('Ã') && !current.contains('Â')) break;
      try {
        final units = current.codeUnits;
        if (units.any((u) => u > 255)) {
          current = _repairKnownSequences(current);
          break;
        }
        final bytes = latin1.encode(current);
        final decoded = utf8.decode(bytes, allowMalformed: false);
        current = decoded;
      } catch (_) {
        current = _repairKnownSequences(current);
        break;
      }
    }
    return _repairKnownSequences(current);
  }

  static String _repairKnownSequences(String text) {
    return text
        .replaceAll('Ã‚Â£', '£')
        .replaceAll('Ã‚Â', '')
        .replaceAll('Ã‚', '')
        .replaceAll('Â£', '£')
        .replaceAll('Â', '')
        .replaceAll('â€™', "'")
        .replaceAll('â€œ', '"')
        .replaceAll('â€\x9d', '"')
        .replaceAll('â€”', '—')
        .replaceAll('â€“', '–')
        .replaceAll('Â°', '°');
  }
}
