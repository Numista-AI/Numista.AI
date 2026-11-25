import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/models/transfer_model.dart';
import 'package:numista_ai/screens/lateral_transfer_screen.dart';
import 'package:numista_ai/services/batch_valuation_service.dart';
import 'package:numista_ai/services/lateral_transfer_service.dart';
import 'package:numista_ai/utils/sell_transfer_access.dart';

class _FakeTransferService extends LateralTransferService {
  Map<String, dynamic>? lastInitiateCall;
  String? lastRecalledId;
  String? lastRotatedId;
  String? lastPreviewCode;
  List<Map<String, dynamic>> pendingRows = [];
  List<Map<String, dynamic>> soldRows = [];

  @override
  Future<TransferModel> initiateTransfer({
    required String userId,
    required List<String> itemIds,
    String? recipientEmail,
    Map<String, bool>? privacyToggles,
    Map<String, int>? itemQuantities,
    String transferType = 'lateral',
    int? expiresDays,
    String source = 'active',
    String? senderDisplay,
    String? senderAddress,
    bool showPrice = false,
    double? salePriceUsd,
    bool includePhotos = false,
  }) async {
    lastInitiateCall = {
      'userId': userId,
      'itemIds': itemIds,
      'transferType': transferType,
      'source': source,
      'showPrice': showPrice,
      'salePriceUsd': salePriceUsd,
      'includePhotos': includePhotos,
    };
    return TransferModel(
      transferId: 'tr_new_1',
      senderId: userId,
      claimPin: '',
      claimCode: 'ABCDE-FGHIJ',
      claimToken: 'tok_123',
      documentPdfB64: '',
      transferType: transferType,
      status: 'pending',
      createdAt: DateTime(2026, 11, 25),
      expiresAt: DateTime(2027, 1, 24),
      itemIds: itemIds,
      items: const [],
      privacyToggles: const {},
    );
  }

  @override
  Future<List<Map<String, dynamic>>> listPendingTransfers() async => List.from(pendingRows);

  @override
  Future<Map<String, dynamic>> recallTransfer({
    required String userId,
    required String transferId,
  }) async {
    lastRecalledId = transferId;
    pendingRows.removeWhere((r) => r['transfer_id'] == transferId);
    return {'status': 'success'};
  }

  @override
  Future<Map<String, dynamic>> rotateClaimCode(String transferId) async {
    lastRotatedId = transferId;
    return {
      'transfer_id': transferId,
      'claim_code': 'ZZZZZ-99999',
      'claim_token': 'tok_new',
      'document_pdf_b64': '',
    };
  }

  @override
  Future<Map<String, dynamic>> previewTransfer({String? claimToken, String? claimCode}) async {
    lastPreviewCode = claimCode ?? claimToken;
    return {
      'items': [
        {'title': '1921 Morgan Dollar', 'quantity': 1},
      ],
      'expires_at': '2027-01-24T00:00:00+00:00',
    };
  }

  @override
  Future<List<Map<String, dynamic>>> getSoldInventory(String userId) async => List.from(soldRows);
}

CoinModel _coin(String id, {bool isSold = false, bool isLocked = false}) {
  return CoinModel.fromMap({
    'Year': '1921',
    'Denomination': '\$1',
    'Program/Series': 'Morgan Dollar',
    'Condition': 'MS-63',
    'Quantity': '1',
    if (isSold) 'status': 'sold',
    if (isLocked) 'locked_pending_upgrade': true,
  }, id);
}

void main() {
  setUp(() {
    canSellOrTransferOverride = () => true;
  });

  tearDown(() {
    canSellOrTransferOverride = null;
  });

  test('R3: BatchValuationService skips Sold coins and Sold currency', () {
    expect(
      BatchValuationService.buildCoinTask('c1', {'Year': '1921', 'Denomination': '\$1', 'status': 'sold'}),
      isNull,
    );
    expect(
      BatchValuationService.buildCoinTask('c2', {'Year': '1921', 'Denomination': '\$1'}),
      isNotNull,
    );
    expect(
      BatchValuationService.buildCurrencyTask('b1', {'Year': '1935', 'Denomination': '\$1', 'status': 'sold'}),
      isNull,
    );
    expect(
      BatchValuationService.buildCurrencyTask('b2', {'Year': '1935', 'Denomination': '\$1'}),
      isNotNull,
    );
  });

  testWidgets('Send form exposes show-price and include-photos switches and submits values', (tester) async {
    final fake = _FakeTransferService();
    await tester.pumpWidget(MaterialApp(
      home: LateralTransferScreen(
        userId: 'seller@test.com',
        itemsToTransfer: [_coin('c1')],
        initialTab: 'send',
        transferService: fake,
      ),
    ));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('transfer_show_price_switch')), findsOneWidget);
    expect(find.byKey(const Key('transfer_include_photos_switch')), findsOneWidget);
    expect(find.byKey(const Key('transfer_price_field')), findsNothing);

    await tester.ensureVisible(find.byKey(const Key('transfer_show_price_switch')));
    await tester.tap(find.byKey(const Key('transfer_show_price_switch')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('transfer_price_field')), findsOneWidget);

    await tester.enterText(find.byKey(const Key('transfer_price_field')), '145.50');
    await tester.ensureVisible(find.byKey(const Key('transfer_include_photos_switch')));
    await tester.tap(find.byKey(const Key('transfer_include_photos_switch')));
    await tester.pumpAndSettle();

    final submitBtn = find.textContaining('Generate Passport Token & PDF');
    await tester.ensureVisible(submitBtn);
    await tester.tap(submitBtn);
    await tester.pumpAndSettle();

    expect(fake.lastInitiateCall?['showPrice'], isTrue);
    expect(fake.lastInitiateCall?['salePriceUsd'], 145.50);
    expect(fake.lastInitiateCall?['includePhotos'], isTrue);
    expect(find.byKey(const Key('created_claim_code')), findsOneWidget);
  });

  testWidgets('Pending Transfers tab supports Reissue code and Cancel', (tester) async {
    final fake = _FakeTransferService()
      ..pendingRows = [
        {
          'transfer_id': 'tr_pending_1',
          'status': 'pending',
          'item_count': 1,
          'item_titles': ['1921 Morgan Dollar'],
          'expires_at': '2027-01-24T00:00:00Z',
          'is_expired': false,
        },
      ];
    await tester.pumpWidget(MaterialApp(
      home: LateralTransferScreen(
        userId: 'seller@test.com',
        itemsToTransfer: const [],
        initialTab: 'pending',
        transferService: fake,
      ),
    ));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('pending_transfer_card_tr_pending_1')), findsOneWidget);

    // Reissue code
    await tester.tap(find.byKey(const Key('pending_reissue_tr_pending_1')));
    await tester.pumpAndSettle();
    expect(fake.lastRotatedId, 'tr_pending_1');
    expect(find.byKey(const Key('reissued_claim_code')), findsOneWidget);
    expect(find.text('ZZZZZ-99999'), findsOneWidget);
    await tester.tap(find.text('Done'));
    await tester.pumpAndSettle();

    // Cancel transfer
    await tester.tap(find.byKey(const Key('pending_cancel_tr_pending_1')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Cancel Transfer'));
    await tester.pumpAndSettle();
    expect(fake.lastRecalledId, 'tr_pending_1');
    expect(find.text('No pending transfers right now.'), findsOneWidget);
  });

  testWidgets('Claim tab previews item titles before claiming', (tester) async {
    final fake = _FakeTransferService();
    await tester.pumpWidget(MaterialApp(
      home: LateralTransferScreen(
        userId: 'buyer@test.com',
        itemsToTransfer: const [],
        initialTab: 'claim',
        transferService: fake,
      ),
    ));
    await tester.pumpAndSettle();

    await tester.enterText(find.byKey(const Key('claim_code_field')), 'ABCDE-FGHIJ');
    await tester.tap(find.byKey(const Key('claim_preview_button')));
    await tester.pumpAndSettle();

    expect(fake.lastPreviewCode, 'ABCDE-FGHIJ');
    expect(find.byKey(const Key('claim_preview_card')), findsOneWidget);
    expect(find.textContaining('1921 Morgan Dollar'), findsOneWidget);
  });

  testWidgets('Sold History tab offers Create Transfer Document for the buyer', (tester) async {
    final fake = _FakeTransferService()
      ..soldRows = [
        {
          'doc_id': 'sale_1',
          'original_coin_id': 'coin_sold_1',
          'title': '1921 Morgan Dollar',
          'status': 'sold',
          'sales_venue': 'eBay',
          'sale_price_usd': 85.0,
          'remaining_qty': 0,
        },
      ];
    await tester.pumpWidget(MaterialApp(
      home: LateralTransferScreen(
        userId: 'seller@test.com',
        itemsToTransfer: const [],
        initialTab: 'sold_history',
        transferService: fake,
      ),
    ));
    await tester.pumpAndSettle();

    final btn = find.byKey(const Key('sold_create_transfer_coin_sold_1'));
    expect(btn, findsOneWidget);
    await tester.tap(btn);
    await tester.pumpAndSettle();

    await tester.tap(find.text('Create Document'));
    await tester.pumpAndSettle();

    expect(fake.lastInitiateCall?['source'], 'sold_item');
    expect(fake.lastInitiateCall?['itemIds'], ['coin_sold_1']);
    expect(fake.lastInitiateCall?['transferType'], 'sale_ebay');
    expect(find.byKey(const Key('created_claim_code')), findsOneWidget);
  });
}
