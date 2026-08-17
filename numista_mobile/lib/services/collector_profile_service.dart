import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:firebase_auth/firebase_auth.dart';
import '../constants.dart';

/// Service managing episodic Collector Memory and AI Preferences
/// Communicates with FastAPI endpoints at `/api/ai/profile`
class CollectorProfileService {
  static const String _baseUrl = kApiBaseUrl;

  /// Default baseline profile contract
  static Map<String, dynamic> get defaultProfile => {
    'schema_version': '1.0',
    'preferred_series': <String>[],
    'target_grade_min': '',
    'target_grade_max': '',
    'preferred_services': <String>['PCGS', 'NGC'],
    'investment_goal': 'numismatic_study',
    'budget_tier': 'intermediate',
    'opt_in_chat_extraction': true,
  };

  /// Fetch collector profile for the current user
  static Future<Map<String, dynamic>> getProfile() async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      final headers = <String, String>{
        'Content-Type': 'application/json',
      };
      if (user != null) {
        final token = await user.getIdToken();
        if (token != null && token.isNotEmpty) {
          headers['Authorization'] = 'Bearer $token';
        }
      }

      final response = await http.get(
        Uri.parse('$_baseUrl/api/ai/profile'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        if (data['profile'] is Map<String, dynamic>) {
          return _normalizeProfile(data['profile'] as Map<String, dynamic>);
        }
      }
    } catch (e) {
      if (kDebugMode) {
        print('CollectorProfileService.getProfile error: $e');
      }
    }
    return defaultProfile;
  }

  /// Update collector profile preferences (strict lowercase snake_case keys)
  static Future<bool> updateProfile(Map<String, dynamic> updates) async {
    try {
      final user = FirebaseAuth.instance.currentUser;
      final headers = <String, String>{
        'Content-Type': 'application/json',
      };
      if (user != null) {
        final token = await user.getIdToken();
        if (token != null && token.isNotEmpty) {
          headers['Authorization'] = 'Bearer $token';
        }
      }

      final payload = <String, dynamic>{};
      if (updates.containsKey('preferred_series')) {
        payload['preferred_series'] = updates['preferred_series'] ?? [];
      }
      if (updates.containsKey('target_grade_min')) {
        payload['target_grade_min'] = updates['target_grade_min'] ?? '';
      }
      if (updates.containsKey('target_grade_max')) {
        payload['target_grade_max'] = updates['target_grade_max'] ?? '';
      }
      if (updates.containsKey('preferred_services')) {
        payload['preferred_services'] = updates['preferred_services'] ?? ['PCGS', 'NGC'];
      }
      if (updates.containsKey('investment_goal')) {
        payload['investment_goal'] = updates['investment_goal'] ?? 'numismatic_study';
      }
      if (updates.containsKey('budget_tier')) {
        payload['budget_tier'] = updates['budget_tier'] ?? 'intermediate';
      }
      if (updates.containsKey('opt_in_chat_extraction')) {
        payload['opt_in_chat_extraction'] = updates['opt_in_chat_extraction'] == true;
      }

      final response = await http.post(
        Uri.parse('$_baseUrl/api/ai/profile'),
        headers: headers,
        body: jsonEncode(payload),
      );

      return response.statusCode == 200;
    } catch (e) {
      if (kDebugMode) {
        print('CollectorProfileService.updateProfile error: $e');
      }
      return false;
    }
  }

  /// Reset collector profile back to baseline defaults
  static Future<bool> resetProfile() async {
    return await updateProfile(defaultProfile);
  }

  /// Ensure all profile keys exist and have safe typed defaults
  static Map<String, dynamic> _normalizeProfile(Map<String, dynamic> raw) {
    final base = Map<String, dynamic>.from(defaultProfile);
    base.addAll(raw);

    if (base['preferred_series'] is! List) {
      base['preferred_series'] = <String>[];
    } else {
      base['preferred_series'] = (base['preferred_series'] as List)
          .map((e) => e.toString())
          .toList();
    }

    if (base['preferred_services'] is! List) {
      base['preferred_services'] = <String>['PCGS', 'NGC'];
    } else {
      base['preferred_services'] = (base['preferred_services'] as List)
          .map((e) => e.toString())
          .toList();
    }

    base['target_grade_min'] = base['target_grade_min']?.toString() ?? '';
    base['target_grade_max'] = base['target_grade_max']?.toString() ?? '';
    base['investment_goal'] = base['investment_goal']?.toString() ?? 'numismatic_study';
    base['budget_tier'] = base['budget_tier']?.toString() ?? 'intermediate';
    base['opt_in_chat_extraction'] = base['opt_in_chat_extraction'] != false;

    return base;
  }
}
