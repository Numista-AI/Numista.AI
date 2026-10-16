// lib/utils/web_input_helper.dart
// V8.7 FIX Item 3: Sets inputmode on Flutter web <input> elements so mobile
// browsers show the correct numeric / decimal soft keyboard.
//
// Flutter web (3.41.5) emits type="text" for all TextFormFields. The engine
// has go9(){return"numeric"} / go9(){return"decimal"} for numberWithOptions,
// but the DOM setup code (b2p()) calls removeAttribute("inputmode") for all
// non-password / non-email types, and only restores it after the keyboard
// connection is opened (on focus).
//
// Solution: attach a FocusNode listener to each numeric / decimal field and
// call setActiveInputMode() on focus. On web, this finds the active
// Flutter text-editing <input> element and sets inputmode.

import 'package:flutter/foundation.dart' show kIsWeb;

import 'web_input_helper_stub.dart'
    if (dart.library.js_interop) 'web_input_helper_web.dart' as impl;

class WebInputHelper {
  WebInputHelper._();

  /// Sets inputmode on the currently active Flutter web <input>.
  /// No-op on native platforms.
  static void setActiveInputMode(String mode) {
    if (!kIsWeb) return;
    impl.setActiveInputMode(mode);
  }
}
