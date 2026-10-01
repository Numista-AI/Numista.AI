import 'dart:convert';
import 'package:numista_ai/constants.dart';
import 'package:numista_ai/services/http_auth_client.dart';

class GradeFlagService {
  static Future<bool> resolveFlag(String flagId, String decision, String notes, {String resolvedGrade = ''}) async {
    final response = await HttpAuthClient.post(
      Uri.parse('$kApiBaseUrl/api/admin/grade_flags/$flagId/resolve'),
      body: jsonEncode({'decision': decision, 'resolved_grade': resolvedGrade, 'notes': notes}),
    );
    return response.statusCode == 200;
  }
}
