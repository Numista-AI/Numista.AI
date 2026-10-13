import 'package:flutter/material.dart';

/// Centralized design tokens for Numista.AI.
/// Apply to all new and updated widgets. Do not hard-code font sizes.
class NumistaTheme {
  // ── Text sizes ────────────────────────────────────────────────────────
  static const double textCaption  = 14.0;  // captions, timestamps — minimum readable size
  static const double textBodySm   = 14.0;  // secondary labels, sub-text
  static const double textBody     = 16.0;  // standard body (minimum for primary text)
  static const double textLg       = 18.0;  // section labels, button text
  static const double textXl       = 22.0;  // headings
  static const double textDisplay  = 28.0;  // hero numbers

  // ── Tap targets ───────────────────────────────────────────────────────
  static const double tapTarget    = 44.0;
  static const double tapTargetLg  = 56.0;  // primary action buttons

  // ── Primary button style ──────────────────────────────────────────────
  static ButtonStyle primaryButtonStyle = ElevatedButton.styleFrom(
    minimumSize: const Size.fromHeight(tapTargetLg),
    textStyle: const TextStyle(fontSize: textLg, fontWeight: FontWeight.w600),
  );

  NumistaTheme._();
}
