import 'dart:convert';
import 'package:http/http.dart' as http;

class SubAccountModel {
  final String childId;
  final String parentEmail;
  final String childAlias;
  final String relationship;
  final String permissionLevel;
  final double bequestPercentage;
  final double createdAt;

  SubAccountModel({
    required this.childId,
    required this.parentEmail,
    required this.childAlias,
    required this.relationship,
    required this.permissionLevel,
    required this.bequestPercentage,
    required this.createdAt,
  });

  factory SubAccountModel.fromJson(Map<String, dynamic> json) {
    return SubAccountModel(
      childId: json['child_id'] ?? '',
      parentEmail: json['parent_email'] ?? '',
      childAlias: json['child_alias'] ?? '',
      relationship: json['relationship'] ?? 'Heir',
      permissionLevel: json['permission_level'] ?? 'VIEW_ONLY',
      bequestPercentage: (json['bequest_percentage'] as num?)?.toDouble() ?? 0.0,
      createdAt: (json['created_at'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() => {
    'child_id': childId,
    'parent_email': parentEmail,
    'child_alias': childAlias,
    'relationship': relationship,
    'permission_level': permissionLevel,
    'bequest_percentage': bequestPercentage,
    'created_at': createdAt,
  };
}

class FamilySubaccountService {
  static const String baseUrl = 'https://numista-backend-568985927038.us-central1.run.app/api/v1/family';

  /// Create a new sub-account under parent email. Enforces Pro tier limit (5) vs Estate tier (Unlimited).
  Future<SubAccountModel> createSubAccount({
    required String parentEmail,
    required String childAlias,
    required String relationship,
    required String permissionLevel,
    required double bequestPercentage,
    String userTier = 'Pro',
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/subaccounts'),
      headers: {
        'Content-Type': 'application/json',
        'user_tier': userTier,
      },
      body: jsonEncode({
        'parent_email': parentEmail,
        'child_alias': childAlias,
        'relationship': relationship,
        'permission_level': permissionLevel,
        'bequest_percentage': bequestPercentage,
      }),
    );

    if (response.statusCode == 200) {
      return SubAccountModel.fromJson(jsonDecode(response.body));
    } else {
      final errorData = jsonDecode(response.body);
      throw Exception(errorData['detail'] ?? 'Failed to create sub-account');
    }
  }

  /// List all sub-accounts for parent
  Future<List<SubAccountModel>> fetchSubAccounts(String parentEmail) async {
    final response = await http.get(
      Uri.parse('$baseUrl/subaccounts?parent_email=$parentEmail'),
    );

    if (response.statusCode == 200) {
      final List<dynamic> list = jsonDecode(response.body);
      return list.map((item) => SubAccountModel.fromJson(item)).toList();
    } else {
      return [];
    }
  }

  /// Delete sub-account
  Future<bool> deleteSubAccount(String childId, String parentEmail) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/subaccounts/$childId?parent_email=$parentEmail'),
    );
    return response.statusCode == 200;
  }
}
