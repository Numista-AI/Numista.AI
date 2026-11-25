import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/transfer_model.dart';

void main() {
  test('parses a v2 creation response (secrets shown once)', () {
    final m = TransferModel.fromMap({
      'transfer_id': 't1',
      'version': 2,
      'transfer_type': 'sale_ebay',
      'claim_token': 'TOK',
      'claim_code': 'ABCDE-FGHJK',
      'document_pdf_b64': 'JVBERg==',
      'items': [],
      'item_ids': ['c1'],
      'created_at': '2026-11-25T00:00:00+00:00',
      'expires_at': '2026-12-25T00:00:00+00:00',
      'status': 'pending',
    }, 't1');
    expect(m.isV2, isTrue);
    expect(m.claimCode, 'ABCDE-FGHJK');
    expect(m.claimToken, 'TOK');
    expect(m.claimPin, isEmpty);
    expect(m.transferType, 'sale_ebay');
  });

  test('toMap never writes the token, the code or the PDF anywhere', () {
    final m = TransferModel.fromMap({
      'transfer_id': 't1', 'version': 2, 'claim_token': 'TOK', 'claim_code': 'ABCDE-FGHJK',
      'document_pdf_b64': 'JVBERg==', 'items': [], 'item_ids': [],
    }, 't1');
    final map = m.toMap();
    expect(map.toString().contains('TOK'), isFalse);
    expect(map.toString().contains('ABCDE'), isFalse);
    expect(map.toString().contains('JVBERg'), isFalse);
  });

  test('a legacy transfer still parses (PIN present, version 1)', () {
    final m = TransferModel.fromMap({'transfer_id': 't0', 'claim_pin': '123456', 'items': [], 'item_ids': []}, 't0');
    expect(m.isV2, isFalse);
    expect(m.claimPin, '123456');
  });

  test('a minimal payload does not throw (existing integration test relies on this)', () {
    expect(() => TransferModel.fromMap({'transfer_id': 'x'}, 'x'), returnsNormally);
  });
}