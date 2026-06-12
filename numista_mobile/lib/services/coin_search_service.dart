import 'dart:convert';
import 'package:http/http.dart' as http;
import '../constants.dart';

/// A single coin result from the Vertex AI Search reference library.
class CoinSearchResult {
  final String id;
  final String programName;
  final String coinYear;
  final String coinName;
  final String denomination;
  final String category;
  final String mintMarks;
  final String metal;
  final String designer;
  final String notes;
  final String imageUrl;
  final String content;
  final String snippet;

  const CoinSearchResult({
    required this.id,
    required this.programName,
    required this.coinYear,
    required this.coinName,
    required this.denomination,
    required this.category,
    required this.mintMarks,
    required this.metal,
    required this.designer,
    required this.notes,
    required this.imageUrl,
    required this.content,
    required this.snippet,
  });

  factory CoinSearchResult.fromJson(Map<String, dynamic> j) {
    return CoinSearchResult(
      id:          j['id']           as String? ?? '',
      programName: j['program_name'] as String? ?? '',
      coinYear:    j['coin_year']    as String? ?? '',
      coinName:    j['coin_name']    as String? ?? '',
      denomination:j['denomination'] as String? ?? '',
      category:    j['category']     as String? ?? '',
      mintMarks:   j['mint_marks']   as String? ?? '',
      metal:       j['metal']        as String? ?? '',
      designer:    j['designer']     as String? ?? '',
      notes:       j['notes']        as String? ?? '',
      imageUrl:    j['image_url']    as String? ?? '',
      content:     j['content']      as String? ?? '',
      snippet:     j['snippet']      as String? ?? '',
    );
  }

  /// Human-readable label, e.g. "1921 Morgan Silver Dollar"
  String get displayTitle {
    final parts = <String>[];
    if (coinYear.isNotEmpty) parts.add(coinYear);
    if (coinName.isNotEmpty && coinName != programName) parts.add(coinName);
    if (programName.isNotEmpty) parts.add(programName);
    return parts.isEmpty ? id : parts.join(' ');
  }

  /// Subtitle line — mints + metal
  String get displaySubtitle {
    final parts = <String>[];
    if (mintMarks.isNotEmpty)  parts.add(mintMarks);
    if (metal.isNotEmpty)      parts.add(metal);
    if (category.isNotEmpty)   parts.add(category);
    return parts.join(' · ');
  }
}

/// Response envelope from /api/coin_search
class CoinSearchResponse {
  final String query;
  final int total;
  final int offset;
  final List<CoinSearchResult> results;
  final String summary;
  final String? error;

  const CoinSearchResponse({
    required this.query,
    required this.total,
    required this.offset,
    required this.results,
    required this.summary,
    this.error,
  });

  factory CoinSearchResponse.fromJson(Map<String, dynamic> j) {
    final rawResults = j['results'] as List<dynamic>? ?? [];
    return CoinSearchResponse(
      query:   j['query']   as String? ?? '',
      total:   (j['total']  as num?)?.toInt()  ?? 0,
      offset:  (j['offset'] as num?)?.toInt()  ?? 0,
      results: rawResults
          .map((r) => CoinSearchResult.fromJson(r as Map<String, dynamic>))
          .toList(),
      summary: j['summary'] as String? ?? '',
      error:   j['error']   as String?,
    );
  }

  factory CoinSearchResponse.empty(String q) => CoinSearchResponse(
        query: q, total: 0, offset: 0, results: [], summary: '');

  factory CoinSearchResponse.withError(String q, String err) =>
      CoinSearchResponse(
        query: q, total: 0, offset: 0, results: [], summary: '', error: err);
}

/// Calls GET /api/coin_search on the Numista.AI Cloud Run backend.
/// Open endpoint — no auth header needed.
class CoinSearchService {
  static const String _baseUrl = kApiBaseUrl;

  /// Searches the Vertex AI-indexed coin reference library.
  ///
  /// [query]    — natural language search term
  /// [pageSize] — number of results (1–25, default 10)
  /// [offset]   — pagination offset (default 0)
  static Future<CoinSearchResponse> search({
    required String query,
    int pageSize = 10,
    int offset = 0,
  }) async {
    final q = query.trim();
    if (q.isEmpty) return CoinSearchResponse.empty(q);

    try {
      final uri = Uri.parse('$_baseUrl/api/coin_search').replace(
        queryParameters: {
          'q': q,
          'page_size': pageSize.toString(),
          'offset': offset.toString(),
        },
      );

      final resp = await http.get(uri).timeout(
            const Duration(seconds: 15),
            onTimeout: () => throw Exception('Search timed out'),
          );

      if (resp.statusCode == 200) {
        final json = jsonDecode(resp.body) as Map<String, dynamic>;
        return CoinSearchResponse.fromJson(json);
      } else {
        return CoinSearchResponse.withError(
            q, 'Server error ${resp.statusCode}');
      }
    } catch (e) {
      return CoinSearchResponse.withError(q, e.toString());
    }
  }
}
