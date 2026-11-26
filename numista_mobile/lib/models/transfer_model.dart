class TransferModel {
  final String transferId;
  final String senderId;
  final String? recipientEmail;

  /// Legacy 6-digit PIN. Empty for v2 transfers (and for legacy transfers hardened at deploy).
  final String claimPin;

  /// v2: shown ONCE at creation. The server stores only hashes, so these are never read back.
  final String claimToken;
  final String claimCode;
  final String documentPdfB64;
  final String transferType;
  final int version;
  final List<dynamic> items;
  final List<String> itemIds;
  final DateTime createdAt;
  final DateTime expiresAt;
  final String status; // 'pending', 'claimed', 'recalled', 'expired'
  final Map<String, dynamic> privacyToggles;

  TransferModel({
    required this.transferId,
    required this.senderId,
    this.recipientEmail,
    this.claimPin = '',
    this.claimToken = '',
    this.claimCode = '',
    this.documentPdfB64 = '',
    this.transferType = 'lateral',
    this.version = 1,
    required this.items,
    required this.itemIds,
    required this.createdAt,
    required this.expiresAt,
    required this.status,
    required this.privacyToggles,
  });

  bool get isV2 => version >= 2;

  factory TransferModel.fromMap(Map<String, dynamic> data, String id) {
    return TransferModel(
      transferId: id,
      senderId: data['sender_id']?.toString() ?? '',
      recipientEmail: data['recipient_email']?.toString(),
      claimPin: data['claim_pin']?.toString() ?? '',
      claimToken: data['claim_token']?.toString() ?? '',
      claimCode: data['claim_code']?.toString() ?? '',
      documentPdfB64: data['document_pdf_b64']?.toString() ?? '',
      transferType: data['transfer_type']?.toString() ?? 'lateral',
      version: int.tryParse(data['version']?.toString() ?? '') ?? 1,
      items: data['items'] as List<dynamic>? ?? [],
      itemIds: (data['item_ids'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      createdAt: DateTime.tryParse(data['created_at']?.toString() ?? '') ?? DateTime.now(),
      expiresAt: DateTime.tryParse(data['expires_at']?.toString() ?? '') ?? DateTime.now().add(const Duration(days: 60)),
      status: data['status']?.toString() ?? 'pending',
      privacyToggles: data['privacy_toggles'] as Map<String, dynamic>? ?? {},
    );
  }

  /// Never writes the secrets (token, code, PDF) anywhere: they exist only for the creation screen.
  Map<String, dynamic> toMap() {
    return {
      'transfer_id': transferId,
      'sender_id': senderId,
      'recipient_email': recipientEmail,
      'claim_pin': claimPin,
      'transfer_type': transferType,
      'version': version,
      'items': items,
      'item_ids': itemIds,
      'created_at': createdAt.toIso8601String(),
      'expires_at': expiresAt.toIso8601String(),
      'status': status,
      'privacy_toggles': privacyToggles,
    };
  }
}
