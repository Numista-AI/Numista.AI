import 'dart:io';

/// Mobile/desktop implementation: writes the file to the current directory.
Future<String> downloadCsvFile(List<int> bytes, String filename) async {
  final dir = Directory.current.path;
  final file = File('$dir/$filename');
  await file.writeAsBytes(bytes);
  return file.path;
}
