// ticket_service.dart
//
// HTTP service layer for Scoped Consent Support Access.
// All calls go through HttpAuthClient which attaches the Firebase ID token.
// The backend (Cloud Run) is the authority for all grant validation,
// redaction, and coin data — this service only makes HTTP calls.

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../services/http_auth_client.dart';
import '../constants.dart';
import '../models/ticket_model.dart';

const _base = kApiBaseUrl;

class TicketService {
  TicketService._();

  // ── Header builder ─────────────────────────────────────────────────────

  /// Returns base JSON headers with Authorization token attached.
  static Future<Map<String, String>> _headers(
      {Map<String, String>? extra}) async {
    final token = await HttpAuthClient.getIdToken();
    final h = <String, String>{
      'Content-Type': 'application/json',
      if (token != null && token.isNotEmpty) 'Authorization': 'Bearer $token',
      if (extra != null) ...extra,
    };
    return h;
  }

  // ── User-facing endpoints ──────────────────────────────────────────────

  /// Submit a new help ticket. Returns the new ticket_id on success.
  static Future<String> createTicket({
    required String subject,
    required String description,
    required String category,
    String appVersion = '',
    Map<String, dynamic>? diagnosticPackage,
  }) async {
    final body = <String, dynamic>{
      'subject': subject,
      'description': description,
      'category': category,
      'app_version': appVersion,
      if (diagnosticPackage != null) 'diagnostic_package': diagnosticPackage,
    };

    final resp = await http.post(
      Uri.parse('$_base/tickets'),
      headers: await _headers(),
      body: jsonEncode(body),
    );

    if (resp.statusCode == 201) {
      final data = jsonDecode(resp.body) as Map<String, dynamic>;
      return data['ticket_id'] as String;
    }
    throw Exception('Failed to create ticket: ${_extractError(resp)}');
  }

  /// Fetch the caller's own ticket list.
  static Future<List<HelpTicket>> listMyTickets() async {
    final resp = await http.get(
      Uri.parse('$_base/tickets'),
      headers: await _headers(),
    );

    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body) as Map<String, dynamic>;
      return (data['tickets'] as List? ?? [])
          .map((t) => HelpTicket.fromMap(t as Map<String, dynamic>))
          .toList();
    }
    if (resp.statusCode == 503) {
      throw Exception('Setting up — please wait a moment and try again.');
    }
    throw Exception('Failed to load tickets: ${resp.statusCode}');
  }

  /// Issue a support grant for a ticket.
  /// Returns metadata only — no token is generated or returned.
  static Future<Map<String, dynamic>> createGrant({
    required String ticketId,
    required List<String> allowedCoinIds,
    required List<String> redactedFields,
    int durationHours = 48,
  }) async {
    final body = {
      'allowed_coin_ids': allowedCoinIds,
      'redacted_fields': redactedFields,
      'duration_hours': durationHours,
    };

    final resp = await http.post(
      Uri.parse('$_base/tickets/$ticketId/grant'),
      headers: await _headers(),
      body: jsonEncode(body),
    );

    if (resp.statusCode == 201) {
      return jsonDecode(resp.body) as Map<String, dynamic>;
    }
    throw Exception('Failed to create grant: ${_extractError(resp)}');
  }

  /// Revoke the active grant on a ticket.
  static Future<void> revokeGrant(String ticketId) async {
    final resp = await http.post(
      Uri.parse('$_base/tickets/$ticketId/revoke'),
      headers: await _headers(),
    );

    if (resp.statusCode != 200) {
      throw Exception('Failed to revoke grant: ${_extractError(resp)}');
    }
  }

  /// Update ticket subject/description/status.
  static Future<void> updateTicket(
    String ticketId, {
    String? subject,
    String? description,
    String? status,
  }) async {
    final body = <String, dynamic>{
      if (subject != null) 'subject': subject,
      if (description != null) 'description': description,
      if (status != null) 'status': status,
    };

    final resp = await http.patch(
      Uri.parse('$_base/tickets/$ticketId'),
      headers: await _headers(),
      body: jsonEncode(body),
    );

    if (resp.statusCode != 200) {
      throw Exception('Failed to update ticket: ${_extractError(resp)}');
    }
  }

  /// Post a message to a ticket thread (user side).
  static Future<String> postMessage(String ticketId, String msgBody) async {
    final resp = await http.post(
      Uri.parse('$_base/tickets/$ticketId/messages'),
      headers: await _headers(),
      body: jsonEncode({'body': msgBody}),
    );

    if (resp.statusCode == 201) {
      final data = jsonDecode(resp.body) as Map<String, dynamic>;
      return data['message_id'] as String;
    }
    throw Exception('Failed to post message: ${_extractError(resp)}');
  }

  // ── Support / Admin endpoints ──────────────────────────────────────────

  /// Fetch the support queue (admin only).
  static Future<List<HelpTicket>> listSupportTickets() async {
    final resp = await http.get(
      Uri.parse('$_base/support/tickets'),
      headers: await _headers(),
    );

    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body) as Map<String, dynamic>;
      return (data['tickets'] as List? ?? [])
          .map((t) => HelpTicket.fromMap(t as Map<String, dynamic>))
          .toList();
    }
    throw Exception('Support queue fetch failed: ${resp.statusCode}');
  }

  /// Fetch a ticket's support view. No token required — backend validates grant_active flag.
  static Future<SupportTicketView> getSupportTicketView({
    required String ticketId,
  }) async {
    final resp = await http.get(
      Uri.parse('$_base/support/tickets/$ticketId'),
      headers: await _headers(),
    );

    if (resp.statusCode == 200) {
      return SupportTicketView.fromJson(
          jsonDecode(resp.body) as Map<String, dynamic>);
    }
    final err = _extractError(resp);
    throw Exception('Support view failed (${resp.statusCode}): $err');
  }

  /// Support agent posts a reply message. No token required.
  static Future<void> supportPostMessage({
    required String ticketId,
    required String msgBody,
  }) async {
    final resp = await http.post(
      Uri.parse('$_base/support/tickets/$ticketId/messages'),
      headers: await _headers(),
      body: jsonEncode({'body': msgBody}),
    );

    if (resp.statusCode != 201) {
      throw Exception(
          'Failed to post support message: ${_extractError(resp)}');
    }
  }

  /// Admin updates ticket status.
  static Future<void> updateTicketStatus(
      String ticketId, String status) async {
    final resp = await http.patch(
      Uri.parse('$_base/support/tickets/$ticketId/status'),
      headers: await _headers(),
      body: jsonEncode({'status': status}),
    );

    if (resp.statusCode != 200) {
      throw Exception('Failed to update status: ${_extractError(resp)}');
    }
  }

  // ── Helpers ────────────────────────────────────────────────────────────

  static String _extractError(http.Response resp) {
    try {
      final body = jsonDecode(resp.body) as Map<String, dynamic>;
      return body['detail'] as String? ?? resp.body;
    } catch (_) {
      return resp.body;
    }
  }
}
