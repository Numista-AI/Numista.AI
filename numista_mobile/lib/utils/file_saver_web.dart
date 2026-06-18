import 'dart:convert';
import 'dart:js_interop';

// Calls the native JS helper defined in web/index.html.
// Passing a Dart String to JS avoids all Dart<->JS byte-array conversion bugs.
@JS('_downloadCSV')
external void _jsDownloadCSV(String content, String filename);

/// Web implementation: converts the UTF-8 byte list to a Dart String and hands
/// it off to the native JavaScript Blob/anchor download helper.
Future<String> downloadCsvFile(List<int> bytes, String filename) async {
  final content = utf8.decode(bytes);
  _jsDownloadCSV(content, filename);
  return filename;
}
