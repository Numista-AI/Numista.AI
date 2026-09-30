import 'package:flutter/foundation.dart';

void triggerWebDownload(String content, String filename, String mimeType) {
  debugPrint('[BackupExportService] Non-web download fallback: ${content.length} bytes for $filename');
}
