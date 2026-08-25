// ticket_model.dart
//
// Data models for Scoped Consent Support Access feature.
// Server is the authority for all redaction and grant validity.
// Client models are display-only — they never make security decisions.

import 'package:cloud_firestore/cloud_firestore.dart';

// ── Ticket status ─────────────────────────────────────────────────────────

enum TicketStatus {
  open,
  inProgress,
  waitingOnUser,
  resolved,
  closed;

  static TicketStatus fromString(String s) {
    switch (s) {
      case 'in_progress':
        return TicketStatus.inProgress;
      case 'waiting_on_user':
        return TicketStatus.waitingOnUser;
      case 'resolved':
        return TicketStatus.resolved;
      case 'closed':
        return TicketStatus.closed;
      default:
        return TicketStatus.open;
    }
  }

  String get label {
    switch (this) {
      case TicketStatus.open:
        return 'Open';
      case TicketStatus.inProgress:
        return 'In Progress';
      case TicketStatus.waitingOnUser:
        return 'Waiting on You';
      case TicketStatus.resolved:
        return 'Resolved';
      case TicketStatus.closed:
        return 'Closed';
    }
  }
}

// ── Ticket categories (snake_case, matches backend VALID_CATEGORIES) ──────

const kTicketCategories = <String, String>{
  'bug_report': 'Bug Report',
  'scan_camera': 'Scan / Camera',
  'import_pcgs_excel_invoice': 'Import / PCGS Invoice',
  'pcgs_data': 'PCGS Data',
  'coin_display_images': 'Coin Images',
  'checklist': 'Checklist',
  'ai_chat_morgan': 'AI Chat — Morgan',
  'ai_trainer_grading': 'AI Trainer / Grading',
  'pricing_valuation': 'Pricing & Valuation',
  'wishlist': 'Wishlist',
  'estate_planning': 'Estate Planning',
  'currency_collection': 'Currency Collection',
  'supplies': 'Supplies',
  'settings_backup': 'Settings & Backup',
  'account_login': 'Account / Login',
  'other': 'Other',
};

// ── TicketMessage ─────────────────────────────────────────────────────────

class TicketMessage {
  final String messageId;
  final String sender; // 'user' | 'support'
  final String senderId;
  final String body;
  final DateTime createdAt;

  const TicketMessage({
    required this.messageId,
    required this.sender,
    required this.senderId,
    required this.body,
    required this.createdAt,
  });

  factory TicketMessage.fromMap(Map<String, dynamic> m) {
    return TicketMessage(
      messageId: m['message_id'] as String? ?? '',
      sender: m['sender'] as String? ?? 'user',
      senderId: m['sender_id'] as String? ?? '',
      body: m['body'] as String? ?? '',
      createdAt: _toDateTime(m['created_at']),
    );
  }
}

// ── SupportGrant (display metadata only — raw token never stored client-side) ──

class SupportGrant {
  final DateTime expiresAt;
  final bool revoked;
  final DateTime? grantUsedAt; // informational only — not a gate

  const SupportGrant({
    required this.expiresAt,
    required this.revoked,
    this.grantUsedAt,
  });

  /// True if the grant has not expired and has not been explicitly revoked.
  /// Client-side only for UI display. Server re-validates on every API call.
  bool get isActive => !revoked && DateTime.now().isBefore(expiresAt);
}

// ── HelpTicket ────────────────────────────────────────────────────────────

class HelpTicket {
  final String ticketId;
  final String userId;
  final DateTime createdAt;
  final DateTime updatedAt;
  final TicketStatus status;
  final String subject;
  final String description;
  final String category;
  final String platform;
  final String appVersion;
  final bool grantActive;
  final DateTime? closedAt;

  const HelpTicket({
    required this.ticketId,
    required this.userId,
    required this.createdAt,
    required this.updatedAt,
    required this.status,
    required this.subject,
    required this.description,
    required this.category,
    required this.platform,
    required this.appVersion,
    required this.grantActive,
    this.closedAt,
  });

  factory HelpTicket.fromMap(Map<String, dynamic> m) {
    return HelpTicket(
      ticketId: m['ticket_id'] as String? ?? '',
      userId: m['user_id'] as String? ?? '',
      createdAt: _toDateTime(m['created_at']),
      updatedAt: _toDateTime(m['updated_at']),
      status: TicketStatus.fromString(m['status'] as String? ?? 'open'),
      subject: m['subject'] as String? ?? '',
      description: m['description'] as String? ?? '',
      category: m['category'] as String? ?? 'other',
      platform: m['platform'] as String? ?? 'web',
      appVersion: m['app_version'] as String? ?? '',
      grantActive: m['grant_active'] as bool? ?? false,
      closedAt: m['closed_at'] != null ? _toDateTime(m['closed_at']) : null,
    );
  }

  String get categoryLabel =>
      kTicketCategories[category] ?? category;
}

// ── SupportCoinView (server-redacted) ─────────────────────────────────────

class SupportCoinView {
  final String coinId;
  final String? denomination;
  final String? year;
  final String? programSeries;
  final String? grade;
  final String? mintMark;
  final String? variety;
  final String? country;
  final String? composition;
  final String? obverseImageUrl;
  final String? reverseImageUrl;

  const SupportCoinView({
    required this.coinId,
    this.denomination,
    this.year,
    this.programSeries,
    this.grade,
    this.mintMark,
    this.variety,
    this.country,
    this.composition,
    this.obverseImageUrl,
    this.reverseImageUrl,
  });

  factory SupportCoinView.fromMap(Map<String, dynamic> m) {
    return SupportCoinView(
      coinId: m['coin_id'] as String? ?? '',
      denomination: m['denomination'] as String?,
      year: m['year']?.toString(),
      programSeries: m['program_series'] as String?,
      grade: m['grade'] as String?,
      mintMark: m['mint_mark'] as String?,
      variety: m['variety'] as String?,
      country: m['country'] as String?,
      composition: m['composition'] as String?,
      obverseImageUrl: m['obverse_image_url'] as String?,
      reverseImageUrl: m['reverse_image_url'] as String?,
    );
  }
}

// ── SupportTicketView (full portal view from backend) ────────────────────

class SupportTicketView {
  final String ticketId;
  final String status;
  final String subject;
  final String description;
  final String category;
  final String platform;
  final String appVersion;
  final DateTime? grantExpiresAt;
  final Map<String, dynamic> deviceInfo;
  final List<String> errorLogs;
  final Map<String, dynamic> collectionStats;
  final List<SupportCoinView> coins;
  final List<String> redactedFieldsApplied;
  final List<TicketMessage> messages;

  const SupportTicketView({
    required this.ticketId,
    required this.status,
    required this.subject,
    required this.description,
    required this.category,
    required this.platform,
    required this.appVersion,
    this.grantExpiresAt,
    required this.deviceInfo,
    required this.errorLogs,
    required this.collectionStats,
    required this.coins,
    required this.redactedFieldsApplied,
    required this.messages,
  });

  factory SupportTicketView.fromJson(Map<String, dynamic> j) {
    return SupportTicketView(
      ticketId: j['ticket_id'] as String? ?? '',
      status: j['status'] as String? ?? '',
      subject: j['subject'] as String? ?? '',
      description: j['description'] as String? ?? '',
      category: j['category'] as String? ?? '',
      platform: j['platform'] as String? ?? '',
      appVersion: j['app_version'] as String? ?? '',
      grantExpiresAt: j['grant_expires_at'] != null
          ? DateTime.tryParse(j['grant_expires_at'] as String)
          : null,
      deviceInfo: (j['device_info'] as Map<String, dynamic>?) ?? {},
      errorLogs: List<String>.from(j['error_logs'] as List? ?? []),
      collectionStats:
          (j['collection_stats'] as Map<String, dynamic>?) ?? {},
      coins: ((j['coins'] as List?) ?? [])
          .map((c) => SupportCoinView.fromMap(c as Map<String, dynamic>))
          .toList(),
      redactedFieldsApplied:
          List<String>.from(j['redacted_fields_applied'] as List? ?? []),
      messages: ((j['messages'] as List?) ?? [])
          .map((m) => TicketMessage.fromMap(m as Map<String, dynamic>))
          .toList(),
    );
  }
}

// ── Utility ───────────────────────────────────────────────────────────────

DateTime _toDateTime(dynamic value) {
  if (value is DateTime) return value;
  if (value is Timestamp) return value.toDate();
  if (value is String) return DateTime.tryParse(value) ?? DateTime.now();
  return DateTime.now();
}
