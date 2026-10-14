import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/backup_export_service.dart';

void main() {
  group('CSV Formula Injection Prevention', () {
    test('neutralizes formula starting with =', () {
      expect(BackupExportService.cleanCsvCell('=1+1'), equals('"\'=1+1"'));
    });

    test('neutralizes formula starting with +', () {
      expect(BackupExportService.cleanCsvCell('+cmd|calc'), equals('"\'cmd|calc"'.replaceAll('cmd|calc', '+cmd|calc')));
    });

    test('neutralizes formula starting with -', () {
      expect(BackupExportService.cleanCsvCell('-2'), equals('"\'-2"'));
    });

    test('neutralizes formula starting with @', () {
      expect(BackupExportService.cleanCsvCell('@SUM(A1)'), equals('"\'@SUM(A1)"'));
    });

    test('leaves normal text untouched in quotes', () {
      expect(BackupExportService.cleanCsvCell('normal text'), equals('"normal text"'));
    });

    test('handles null values correctly', () {
      expect(BackupExportService.cleanCsvCell(null), equals('""'));
    });

    test('escapes internal quotes correctly', () {
      expect(BackupExportService.cleanCsvCell('he said "hi"'), equals('"he said ""hi"""'));
    });
  });
}
