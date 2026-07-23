class TransferModel {
  final String transferId;
  final String senderId;
  final String? recipientEmail;
  final String claimPin;
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
    required this.claimPin,
    required this.items,
    required this.itemIds,
    required this.createdAt,
    required this.expiresAt,
    required this.status,
    required this.privacyToggles,
  });

  factory TransferModel.fromMap(Map<String, dynamic> data, String id) {
    return TransferModel(
      transferId: id,
      senderId: data['sender_id']?.toString() ?? '',
      recipientEmail: data['recipient_email']?.toString(),
      claimPin: data['claim_pin']?.toString() ?? '',
      items: data['items'] as List<dynamic>? ?? [],
      itemIds: (data['item_ids'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      createdAt: DateTime.tryParse(data['created_at']?.toString() ?? '') ?? DateTime.now(),
      expiresAt: DateTime.tryParse(data['expires_at']?.toString() ?? '') ?? DateTime.now().add(const Duration(days: 60)),
      status: data['status']?.toString() ?? 'pending',
      privacyToggles: data['privacy_toggles'] as Map<String, dynamic>? ?? {},
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'transfer_id': transferId,
      'sender_id': senderId,
      'recipient_email': recipientEmail,
      'claim_pin': claimPin,
      'items': items,
      'item_ids': itemIds,
      'created_at': createdAt.toIso8601String(),
      'expires_at': expiresAt.toIso8601String(),
      'status': status,
      'privacy_toggles': privacyToggles,
    };
  }
}
