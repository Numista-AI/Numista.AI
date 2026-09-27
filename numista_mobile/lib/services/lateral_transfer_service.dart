import 'dart:convert';
import 'package:http/http.dart' as http;
import '../constants.dart';
import '../models/transfer_model.dart';

class LateralTransferService {
  final String baseUrl;

  LateralTransferService({this.baseUrl = kApiBaseUrl});

  /// Initiates a lateral transfer with privacy options
  Future<TransferModel> initiateTransfer({
    required String userId,
    required List<String> itemIds,
    String? recipientEmail,
    Map<String, bool>? privacyToggles,
    Map<String, int>? itemQuantities,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/transfer/initiate'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'item_ids': itemIds,
        'recipient_email': recipientEmail,
        'item_quantities': itemQuantities,
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

  /// Claims a pending transfer using PIN/token
  Future<Map<String, dynamic>> claimTransfer({
    required String userId,
    required String transferId,
    required String claimPin,
    List<String>? selectedItemIds,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/transfer/claim'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'transfer_id': transferId,
        'claim_pin': claimPin,
        'selected_item_ids': selectedItemIds,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to claim transfer: ${response.body}');
    }
  }

  /// Recalls an unclaimed pending transfer
  Future<Map<String, dynamic>> recallTransfer({
    required String userId,
    required String transferId,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/transfer/recall'),
      headers: {'Content-Type': 'application/json'},
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
  String getPassportPdfUrl(String transferId) {
    return '$baseUrl/api/transfer/passport-pdf/$transferId';
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
    final response = await http.post(
      Uri.parse('$baseUrl/api/transfer/sell-direct'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'coin_id': coinId,
        'qty_sold': qtySold,
        'sale_price_usd': salePriceUsd,
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
    final response = await http.post(
      Uri.parse('$baseUrl/api/transfer/undo-sale'),
      headers: {'Content-Type': 'application/json'},
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
    final response = await http.get(
      Uri.parse('$baseUrl/api/transfer/sold-items/$cleanUid'),
      headers: {'Accept': 'application/json'},
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final list = data['items'] as List<dynamic>? ?? [];
      return list.map((e) => Map<String, dynamic>.from(e as Map)).toList();
    } else {
      throw Exception('Failed to fetch sold items: ${response.body}');
    }
  }
}

