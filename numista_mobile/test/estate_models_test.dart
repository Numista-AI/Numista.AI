import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/estate_models.dart';

void main() {
  group('US Army Property Management Inspired Estate Models', () {
    test('CoinEstateData handles custody fields and serialization correctly', () {
      final now = DateTime.now();
      final data = CoinEstateData(
        coinId: 'coin_123',
        beneficiaryId: 'heir_alpha',
        beneficiaryName: 'Primary Heir',
        custodialLocation: 'Bank Safety Deposit #402',
        subHandReceiptHolder: 'Museum Exhibit Loan',
        handReceiptSignedAt: now,
        handReceiptHash: 'abc123hash',
        trustScheduleIdentifier: 'Schedule A-12',
      );

      expect(data.coinId, equals('coin_123'));
      expect(data.custodialLocation, equals('Bank Safety Deposit #402'));
      expect(data.subHandReceiptHolder, equals('Museum Exhibit Loan'));
      expect(data.trustScheduleIdentifier, equals('Schedule A-12'));
    });

    test('EstateAuditRecord initializes SHA-256 spot-check audit data', () {
      final now = DateTime.now();
      final audit = EstateAuditRecord(
        auditId: 'audit_001',
        coinId: 'coin_123',
        auditType: 'routine_spot_check',
        verifiedAt: now,
        verifiedByAlias: 'Owner',
        physicalConditionCode: 'Choice',
        certVerified: true,
        auditHash: 'sha256_sample_hash',
      );

      expect(audit.auditId, equals('audit_001'));
      expect(audit.auditType, equals('routine_spot_check'));
      expect(audit.physicalConditionCode, equals('Choice'));
      expect(audit.certVerified, isTrue);
      expect(audit.auditHash, equals('sha256_sample_hash'));
    });

    test('EstateDocumentRegisterRecord formats NUM-DOC-YYYY-XXXXX correctly', () {
      final now = DateTime.now();
      final docRecord = EstateDocumentRegisterRecord(
        docNumber: 'NUM-DOC-2026-00001',
        docType: 'baseline_lock',
        createdAt: now,
        assetCount: 10000,
        totalFmv: 250000.0,
        signatureHash: 'sig_hash_sample',
        title: 'Initial Estate Baseline Lock',
      );

      expect(docRecord.docNumber, equals('NUM-DOC-2026-00001'));
      expect(docRecord.typeLabel, equals('Initial Estate Baseline Lock'));
      expect(docRecord.assetCount, equals(10000));
      expect(docRecord.totalFmv, equals(250000.0));
    });
  });
}
