import 'dart:convert';
import 'dart:io';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('Census: Public catalog contains exactly 3,202 records and zero PII', () async {
    final file = File('assets/catalog/catalog_public_v1.json');
    expect(file.existsSync(), isTrue, reason: 'Public catalog asset must exist');

    final content = await file.readAsString();
    final List<dynamic> catalog = jsonDecode(content) as List<dynamic>;

    expect(catalog.length, equals(3202));

    int coins = 0;
    int notes = 0;
    int medals = 0;

    const forbiddenKeys = [
      'uid', 'email', 'userId', 'user_id',
      'purchase_price', 'Purchase Cost', 'purchaseCost', 'cost_basis',
      'acquisition_date', 'Purchase Date', 'purchaseDate',
      'Retailer/Website', 'retailer',
      'Retailer Item No.', 'retailerItemNo',
      'Retailer Invoice #', 'retailerInvoiceNo',
      'Storage Location', 'storageLocation',
      'private_notes', 'Personal Notes I', 'personalNotes',
      'Personal Reference #', 'personalRef',
      'cert_number', 'Certification Number', 'certificationNumber',
      'owner_photos', 'ownerPhotos', 'provenanceLedger',
      'transferStatus', 'transferId',
    ];

    for (final item in catalog) {
      final map = item as Map<String, dynamic>;
      final type = map['type'] as String?;
      if (type == 'coin') coins++;
      if (type == 'note') notes++;
      if (type == 'medal') medals++;

      // Verify foreign exclusion: segment 2 of nac_code must be US
      final nac = map['nac_code'] as String;
      final parts = nac.split('.');
      expect(parts.length, greaterThan(2));
      expect(parts[2], equals('US'), reason: 'All records must be US numismatics');

      for (final key in forbiddenKeys) {
        expect(map.containsKey(key), isFalse, reason: 'Public catalog must not contain $key');
      }
    }

    expect(coins, equals(2965));
    expect(notes, equals(181));
    expect(medals, equals(56));
  });
}
