/// Stub implementation — never actually called at runtime.
/// The conditional import in settings_screen.dart selects either
/// file_saver_web.dart or file_saver_io.dart based on the platform.
Future<String> downloadCsvFile(List<int> bytes, String filename) {
  throw UnsupportedError('downloadCsvFile is not supported on this platform.');
}
