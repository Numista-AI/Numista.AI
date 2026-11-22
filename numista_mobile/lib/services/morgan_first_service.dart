import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:numista_ai/constants.dart';
import 'package:numista_ai/services/http_auth_client.dart';

class MorganHomeFlagsState {
  final bool morganHomeAllowlist;
  final bool morganHomeNewUsers;
  final bool morganHomeEveryone;
  final bool eligible;
  final String preferredHome; // 'morgan' | 'full_site'
  final bool showMorganHome;

  const MorganHomeFlagsState({
    this.morganHomeAllowlist = false,
    this.morganHomeNewUsers = false,
    this.morganHomeEveryone = false,
    this.eligible = false,
    this.preferredHome = 'full_site',
    this.showMorganHome = false,
  });

  MorganHomeFlagsState copyWith({
    bool? morganHomeAllowlist,
    bool? morganHomeNewUsers,
    bool? morganHomeEveryone,
    bool? eligible,
    String? preferredHome,
    bool? showMorganHome,
  }) {
    return MorganHomeFlagsState(
      morganHomeAllowlist: morganHomeAllowlist ?? this.morganHomeAllowlist,
      morganHomeNewUsers: morganHomeNewUsers ?? this.morganHomeNewUsers,
      morganHomeEveryone: morganHomeEveryone ?? this.morganHomeEveryone,
      eligible: eligible ?? this.eligible,
      preferredHome: preferredHome ?? this.preferredHome,
      showMorganHome: showMorganHome ?? this.showMorganHome,
    );
  }
}

class MorganFirstService {
  static final ValueNotifier<MorganHomeFlagsState> state =
      ValueNotifier<MorganHomeFlagsState>(const MorganHomeFlagsState());

  static MorganHomeFlagsState get current => state.value;
  static bool get showMorganHome => state.value.showMorganHome;

  static Future<void> refresh({
    Future<http.Response> Function(Uri uri)? getFn,
  }) async {
    try {
      final response = await (getFn != null
          ? getFn(Uri.parse('$kApiBaseUrl/api/morgan/home_flags'))
          : HttpAuthClient.get(Uri.parse('$kApiBaseUrl/api/morgan/home_flags')));
      if (response.statusCode == 200) {
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        final flags = (body['flags'] as Map<String, dynamic>?) ?? {};
        final eligible = body['eligible'] == true;
        final pref = (body['preferred_home'] as String?) ??
            (eligible ? 'morgan' : 'full_site');
        final show = body['show_morgan_home'] == true;
        state.value = MorganHomeFlagsState(
          morganHomeAllowlist: flags['morgan_home_allowlist'] == true,
          morganHomeNewUsers: flags['morgan_home_new_users'] == true,
          morganHomeEveryone: flags['morgan_home_everyone'] == true,
          eligible: eligible,
          preferredHome: pref,
          showMorganHome: show,
        );
      } else {
        state.value = const MorganHomeFlagsState();
      }
    } catch (_) {
      state.value = const MorganHomeFlagsState();
    }
  }

  static Future<bool> setPreference(
    String preferredHome, {
    Future<http.Response> Function(Uri uri, {Object? body})? postFn,
  }) async {
    if (preferredHome != 'morgan' && preferredHome != 'full_site') {
      return false;
    }
    try {
      final uri = Uri.parse('$kApiBaseUrl/api/morgan/home_preference');
      final payload = jsonEncode({'preferred_home': preferredHome});
      final response = await (postFn != null
          ? postFn(uri, body: payload)
          : HttpAuthClient.post(uri, body: payload));
      if (response.statusCode == 200) {
        final cur = state.value;
        state.value = cur.copyWith(
          preferredHome: preferredHome,
          showMorganHome: cur.eligible && preferredHome == 'morgan',
        );
        return true;
      }
    } catch (_) {}
    return false;
  }

  static Future<Map<String, dynamic>> proposeAddCoin(
    Map<String, dynamic> coinData, {
    Future<http.Response> Function(Uri uri, {Object? body})? postFn,
  }) async {
    final uri = Uri.parse('$kApiBaseUrl/api/morgan/propose');
    final payload = jsonEncode({
      'action': 'add_coin',
      'coin_data': coinData,
    });
    final response = await (postFn != null
        ? postFn(uri, body: payload)
        : HttpAuthClient.post(uri, body: payload));
    if (response.statusCode != 200) {
      throw Exception('Proposal failed (${response.statusCode})');
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  static Future<Map<String, dynamic>> confirmProposal(
    String proposalId, {
    Future<http.Response> Function(Uri uri, {Object? body})? postFn,
  }) async {
    final uri = Uri.parse('$kApiBaseUrl/api/morgan/confirm');
    final payload = jsonEncode({'proposal_id': proposalId});
    final response = await (postFn != null
        ? postFn(uri, body: payload)
        : HttpAuthClient.post(uri, body: payload));
    if (response.statusCode != 200) {
      throw Exception('Confirm failed (${response.statusCode})');
    }
    return jsonDecode(response.body) as Map<String, dynamic>;
  }

  static void reset() {
    state.value = const MorganHomeFlagsState();
  }

  /// Confidence words first, small % after (Plan v3.2 §3).
  static String confidenceWords(double pct) {
    final rounded = pct.round();
    if (pct >= 90) return 'Morgan is very sure ($rounded%)';
    if (pct >= 70) return 'Morgan is fairly sure ($rounded%)';
    if (pct >= 40) return 'Morgan is not sure ($rounded%) - please check';
    return "Morgan can't tell - try another photo";
  }

  static String? confidenceSubline(double pct) {
    if (pct >= 70 && pct < 90) return 'Please look it over.';
    return null;
  }

  static bool canAddForConfidence(double pct) => pct >= 40;
  static bool highlightFixFirst(double pct) => pct >= 40 && pct < 70;
}
