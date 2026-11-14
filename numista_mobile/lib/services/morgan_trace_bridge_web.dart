import 'dart:js_interop';
import 'dart:js_interop_unsafe';

void publishLastTraceToWindow(Map<String, dynamic> trace) {
  try {
    globalContext.setProperty('__MORGAN_LAST_TRACE__'.toJS, trace.jsify());
  } catch (_) {
    // Ignore bridge failures in restricted frames.
  }
}
