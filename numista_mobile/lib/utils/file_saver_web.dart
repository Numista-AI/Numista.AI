import 'dart:js_interop';
import 'package:web/web.dart' as web;

/// Web implementation: creates a Blob URL and triggers a browser download.
Future<String> downloadCsvFile(List<int> bytes, String filename) async {
  final jsArray = bytes.map((b) => b.toJS).toList().toJS;
  final blob = web.Blob(jsArray, web.BlobPropertyBag(type: 'text/csv'));
  final url = web.URL.createObjectURL(blob);
  final anchor = web.HTMLAnchorElement()
    ..href = url
    ..setAttribute('download', filename);
  web.document.body!.append(anchor);
  anchor.click();
  anchor.remove();
  web.URL.revokeObjectURL(url);
  return filename;
}
