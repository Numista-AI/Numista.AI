import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web/web.dart' as web;
import 'dart:js_interop';

void triggerWebDownload(String content, String filename, String mimeType) {
  try {
    final bytes = utf8.encode(content);
    final blob = web.Blob([bytes.toJS].toJS, web.BlobPropertyBag(type: mimeType));
    final url = web.URL.createObjectURL(blob);
    final anchor = web.HTMLAnchorElement()
      ..href = url
      ..download = filename
      ..style.display = 'none';
    web.document.body?.appendChild(anchor);
    anchor.click();
    web.document.body?.removeChild(anchor);
    Future.delayed(const Duration(seconds: 5), () {
      web.URL.revokeObjectURL(url);
    });
  } catch (e) {
    debugPrint('[BackupExportService] Web download error: $e');
    rethrow;
  }
}
