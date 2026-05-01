import 'dart:convert';
import 'package:flutter/foundation.dart' show debugPrint;
import 'package:http/http.dart' as http;

class NumistaService {
  static const String _baseUrl = 'https://en.numista.com/api/v3';
  static const String _apiKey = 'ExpST6TaGRDXkcEt6QajYJ0Lj76JZ8oqBPPpWhe';

  /// Fetches varieties (issues) for a specific coin type.
  /// Cross-references with the Numista catalog to ensure "Expert" accuracy.
  Future<Map<String, dynamic>?> fetchCoinType(int typeId) async {
    final url = Uri.parse('$_baseUrl/types/$typeId');
    try {
      final response = await http.get(
        url,
        headers: {
          'Numista-API-Key': _apiKey,
          'Accept': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        debugPrint('Numista API Error: ${response.statusCode} - ${response.body}');
        return null;
      }
    } catch (e) {
      debugPrint('Numista Service Exception: $e');
      return null;
    }
  }

  /// Searches for a coin by query (e.g., "2004 Texas Quarter")
  Future<List<dynamic>> searchCoins(String query) async {
    final url = Uri.parse('$_baseUrl/types?q=${Uri.encodeComponent(query)}');
    try {
      final response = await http.get(
        url,
        headers: {
          'Numista-API-Key': _apiKey,
          'Accept': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['types'] ?? [];
      }
    } catch (e) {
      debugPrint('Numista Search Error: $e');
    }
    return [];
  }
}
