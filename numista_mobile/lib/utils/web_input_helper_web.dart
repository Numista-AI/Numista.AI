// lib/utils/web_input_helper_web.dart
import 'dart:js_interop';
import 'package:web/web.dart' as web;

void setActiveInputMode(String mode) {
  try {
    final active = web.document.activeElement;
    if (active != null && active.isA<web.HTMLInputElement>()) {
      (active as web.HTMLInputElement).inputMode = mode;
      return;
    }
    // Fallback: scan all input elements inside the flutter text editing host
    final inputs = web.document.querySelectorAll('input');
    for (int i = 0; i < inputs.length; i++) {
      final node = inputs.item(i);
      if (node != null && node.isA<web.HTMLInputElement>()) {
        (node as web.HTMLInputElement).inputMode = mode;
      }
    }
  } catch (_) {}
}
