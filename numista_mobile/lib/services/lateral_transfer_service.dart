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
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/transfer/initiate'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'item_ids': itemIds,
        'recipient_email': recipientEmail,
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
}
