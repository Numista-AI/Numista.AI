import 'dart:js_interop';
import 'dart:typed_data';
import 'package:web/web.dart' as web;

/// Web implementation: creates a Blob URL and triggers a browser download.
Future<String> downloadCsvFile(List<int> bytes, String filename) async {
  final uint8 = Uint8List.fromList(bytes);
  final jsBytes = uint8.toJS;
  final blob = web.Blob(
    [jsBytes].toJS,
    web.BlobPropertyBag(type: 'text/csv;charset=utf-8'),
  );
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
