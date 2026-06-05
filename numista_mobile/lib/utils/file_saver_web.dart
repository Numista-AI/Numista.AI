// ignore: avoid_web_libraries_in_flutter
import 'dart:html' as html;

/// Web implementation: creates a Blob URL and triggers a browser download.
Future<String> downloadCsvFile(List<int> bytes, String filename) async {
  final blob = html.Blob([bytes], 'text/csv');
  final url = html.Url.createObjectUrlFromBlob(blob);
  html.AnchorElement(href: url)
    ..setAttribute('download', filename)
    ..click();
  html.Url.revokeObjectUrl(url);
  return filename;
}
