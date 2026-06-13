// Web implementation — opens PDF in a new browser tab via Blob URL.
// Uses package:web + dart:js_interop (replaces deprecated dart:html).
import 'dart:js_interop';
import 'dart:typed_data';
import 'package:web/web.dart' as web;

Future<void> openPdfPlatform(Uint8List pdfBytes, String filename) async {
  final blob = web.Blob(
    [pdfBytes.toJS].toJS,
    web.BlobPropertyBag(type: 'application/pdf'),
  );
  final url = web.URL.createObjectURL(blob);
  web.window.open(url, '_blank');
  // Revoke after a short delay to allow the browser to load the blob
  Future.delayed(const Duration(seconds: 30), () {
    web.URL.revokeObjectURL(url);
  });
}
