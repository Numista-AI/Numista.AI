import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/foundation.dart' show debugPrint;
import '../models/program_model.dart';
import 'coin_programs_data.dart';

class ReferenceService {
  static final FirebaseFirestore _db = FirebaseFirestore.instance;

  /// Fetch all programs from the global cloud repository.
  /// Professional Choice: Enables persistence/caching for offline SME access.
  static Stream<Map<String, List<CoinProgram>>> getGroupedProgramsStream() {
    return _db.collection('global_programs').snapshots().map((snapshot) {
      if (snapshot.docs.isEmpty) {
        // Professional Choice: Fallback to local static data if Cloud is empty
        return CoinProgramsData.usPrograms;
      }

      final Map<String, List<CoinProgram>> grouped = {};

      for (var doc in snapshot.docs) {
        final program = CoinProgram.fromMap(doc.data(), doc.id);
        final category = program.category;

        if (!grouped.containsKey(category)) {
          grouped[category] = [];
        }
        grouped[category]!.add(program);
      }

      return grouped;
    });
  }

  /// Helper to fetch a single program by ID with local cache priority
  static Future<CoinProgram?> getProgram(String programId) async {
    try {
      final doc = await _db.collection('global_programs').doc(programId).get();
      if (doc.exists) {
        return CoinProgram.fromMap(doc.data()!, doc.id);
      }
    } catch (e) {
      debugPrint('Error fetching program $programId: $e');
    }
    return null;
  }
}
