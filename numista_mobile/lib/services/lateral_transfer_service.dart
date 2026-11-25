import 'dart:convert';
import '../constants.dart';
import '../models/transfer_model.dart';
import 'http_auth_client.dart';

class LateralTransferService {
  final String baseUrl;

  LateralTransferService({this.baseUrl = kApiBaseUrl});

  /// Initiates a transfer (v2). The server returns the claim token, code and the Transfer Document
  /// (base64 PDF) ONCE; only hashes are stored.
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
    final response = await HttpAuthClient.post(
      Uri.parse('$baseUrl/api/transfer/initiate'),
      body: jsonEncode({
        'user_id': userId,
        'item_ids': itemIds,
        'recipient_email': recipientEmail,
        'item_quantities': itemQuantities,
        'transfer_type': transferType,
        'expires_days': expiresDays,
        'source': source,
        'sender_display': senderDisplay,
        'sender_address': senderAddress,
        'show_price': showPrice,
        'sale_price_usd': salePriceUsd,
        'include_photos': includePhotos,
        'privacy_toggles': privacyToggles ?? {
          'hide_cost_basis': true,
          'hide_private_notes': true,
          'hide_storage_location': true,
          'hide_invoices': true,
        },
      }),
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      return TransferModel.fromMap(json['transfer'], json['transfer']['transfer_id']);
    } else {
      throw Exception('Failed to initiate transfer: ${response.body}');
    }
  }

  /// Claims a pending transfer. One endpoint: pass a [claimToken] (QR), a [claimCode] (typed),
  /// or the legacy [transferId] + [claimPin].
  Future<Map<String, dynamic>> claimTransfer({
    required String userId,
    String? transferId,
    String? claimPin,
    String? claimToken,
    String? claimCode,
    List<String>? selectedItemIds,
  }) async {
    final response = await HttpAuthClient.post(
      Uri.parse('$baseUrl/api/transfer/claim'),
      body: jsonEncode({
        'user_id': userId,
        'transfer_id': ?transferId,
        'claim_pin': ?claimPin,
        'claim_token': ?claimToken,
        'claim_code': ?claimCode,
        'selected_item_ids': selectedItemIds,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else if (response.statusCode == 429) {
      throw Exception('Too many attempts. Please try again later.');
    } else {
      throw Exception('Failed to claim transfer: ${response.body}');
    }
  }

  /// Authenticated preview of a claim link: item titles only.
  Future<Map<String, dynamic>> previewTransfer({String? claimToken, String? claimCode}) async {
    final params = <String, String>{
      'claim_token': ?claimToken,
      'claim_code': ?claimCode,
    };
    final response = await HttpAuthClient.get(
      Uri.parse('$baseUrl/api/transfer/preview').replace(queryParameters: params),
    );
    if (response.statusCode == 200) {
      return Map<String, dynamic>.from(jsonDecode(response.body)['preview'] as Map);
    }
    throw Exception('Failed to preview transfer: ${response.body}');
  }

  /// Lists the authenticated sender's pending transfers (summary only; no hashes or secrets).
  Future<List<Map<String, dynamic>>> listPendingTransfers() async {
    final response = await HttpAuthClient.get(
      Uri.parse('$baseUrl/api/transfer/pending'),
    );
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final list = (data['transfers'] as List<dynamic>?) ?? const [];
      return list.map((e) => Map<String, dynamic>.from(e as Map)).toList();
    }
    throw Exception('Failed to load pending transfers: ${response.body}');
  }

  /// Sender reissues a pending transfer's token and code (also upgrades a legacy PIN transfer).
  Future<Map<String, dynamic>> rotateClaimCode(String transferId) async {
    final response = await HttpAuthClient.post(
      Uri.parse('$baseUrl/api/transfer/rotate-code'),
      body: jsonEncode({'transfer_id': transferId}),
    );
    if (response.statusCode == 200) {
      return Map<String, dynamic>.from(jsonDecode(response.body)['result'] as Map);
    }
    throw Exception('Failed to reissue code: ${response.body}');
  }

  /// Recalls an unclaimed pending transfer
  Future<Map<String, dynamic>> recallTransfer({
    required String userId,
    required String transferId,
  }) async {
    final response = await HttpAuthClient.post(
      Uri.parse('$baseUrl/api/transfer/recall'),
      body: jsonEncode({
        'user_id': userId,
        'transfer_id': transferId,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to recall transfer: ${response.body}');
    }
  }

  /// Gets Passport PDF download URL
  /// Fetches the Certificate of Transfer PDF bytes via authenticated request.
  /// The plain URL approach is replaced because the route now requires a Bearer token.
  Future<List<int>> fetchCertificatePdfBytes(String transferId) async {
    final response = await HttpAuthClient.get(
      Uri.parse('$baseUrl/api/transfer/passport-pdf/$transferId'),
    );
    if (response.statusCode == 200) {
      return response.bodyBytes;
    } else {
      throw Exception('Failed to fetch Certificate PDF: ${response.statusCode} ${response.body}');
    }
  }

  /// Records a direct sale outside Numista.AI (Mode 3, G1-G3)
  Future<Map<String, dynamic>> recordDirectSale({
    required String userId,
    required String coinId,
    required int qtySold,
    required double salePriceUsd,
    double feesUsd = 0.0,
    String? saleDate,
    String salesVenue = 'Direct / Outside',
    String? buyerReference,
    String? notes,
  }) async {
    final response = await HttpAuthClient.post(
      Uri.parse('$baseUrl/api/transfer/sell-direct'),
      body: jsonEncode({
        'user_id': userId,
        'coin_id': coinId,
        'qty_sold': qtySold,
        'sale_price': salePriceUsd,
        'sale_price_usd': salePriceUsd,
        'fees': feesUsd,
        'fees_usd': feesUsd,
        'sale_date': saleDate,
        'sales_venue': salesVenue,
        'buyer_reference': buyerReference,
        'notes': notes,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to record direct sale: ${response.body}');
    }
  }

  /// Undoes a Mode 3 sale, restoring active quantity and marking archive voided (CoS Lock L3)
  Future<Map<String, dynamic>> undoSale({
    required String userId,
    required String saleArchiveId,
  }) async {
    final response = await HttpAuthClient.post(
      Uri.parse('$baseUrl/api/transfer/undo-sale'),
      body: jsonEncode({
        'user_id': userId,
        'sale_archive_id': saleArchiveId,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to undo sale: ${response.body}');
    }
  }

  /// Fetches sold/transferred inventory for a user
  Future<List<Map<String, dynamic>>> getSoldInventory(String userId) async {
    final cleanUid = userId.trim().toLowerCase();
    final response = await HttpAuthClient.get(
      Uri.parse('$baseUrl/api/transfer/sold-items/$cleanUid'),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final list = (data['sold_items'] ?? data['items']) as List<dynamic>? ?? [];
      return list.map((e) => Map<String, dynamic>.from(e as Map)).toList();
    } else {
      throw Exception('Failed to fetch sold items: ${response.body}');
    }
  }
}

