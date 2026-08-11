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

      // Collect all programs from snapshot
      final List<CoinProgram> allDocs = snapshot.docs
          .map((doc) => CoinProgram.fromMap(doc.data(), doc.id))
          .where((p) => p.coins.isNotEmpty) // Filter out 0-coin ghost docs
          .toList();

      // Deduplicate deterministically by display name: highest coins count, then smallest doc ID
      final Map<String, CoinProgram> canonicalMap = {};
      for (final program in allDocs) {
        final title = program.name.trim().toLowerCase();
        if (!canonicalMap.containsKey(title)) {
          canonicalMap[title] = program;
        } else {
          final existing = canonicalMap[title]!;
          if (program.coins.length > existing.coins.length ||
              (program.coins.length == existing.coins.length && program.id.compareTo(existing.id) < 0)) {
            canonicalMap[title] = program;
          }
        }
      }

      final Map<String, List<CoinProgram>> grouped = {};
      for (final program in canonicalMap.values) {
        final category = program.category.isEmpty ? 'Other' : program.category;
        grouped.putIfAbsent(category, () => []).add(program);
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
