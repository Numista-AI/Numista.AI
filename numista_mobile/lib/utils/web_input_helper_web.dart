// lib/utils/web_input_helper_web.dart
import 'dart:js_interop';
import 'package:web/web.dart' as web;

void applyStaticInputModes(Map<String, String?> modes) {
  try {
    final inputs = web.document.querySelectorAll('input');
    for (int i = 0; i < inputs.length; i++) {
      final node = inputs.item(i);
      if (node != null && node.isA<web.HTMLInputElement>()) {
        final input = node as web.HTMLInputElement;
        final label = (input.getAttribute('aria-label') ??
                       input.getAttribute('placeholder') ??
                       input.getAttribute('name') ?? '').toLowerCase();
        final parentLabel = (input.parentElement?.getAttribute('aria-label') ?? '').toLowerCase();
        final full = '$label $parentLabel';
        for (final entry in modes.entries) {
          if (entry.value != null && full.contains(entry.key.toLowerCase())) {
            input.setAttribute('inputmode', entry.value!);
            break;
          }
        }
      }
    }
  } catch (_) {}
}

void setActiveInputMode(String mode) {
  // Safe no-op in V8.9 to prevent inputmode swapping on focus
}

