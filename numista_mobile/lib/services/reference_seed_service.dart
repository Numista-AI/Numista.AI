import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/foundation.dart' show debugPrint;
import 'coin_programs_data.dart';
import '../models/program_model.dart';

class ReferenceSeedService {
  static final FirebaseFirestore _db = FirebaseFirestore.instance;

  /// Professional Migration: Uploads static hardcoded data to Firestore.
  /// This tool transforms the "Circulating Coin Programs" static map into dynamic cloud documents.
  static Future<void> seedGlobalPrograms() async {
    debugPrint('Starting Global Reference Migration...');
    
    int count = 0;
    for (var entry in CoinProgramsData.usPrograms.entries) {
      final category = entry.key; // e.g. "Circulating Coin Programs"
      final programs = entry.value;

      for (var program in programs) {
        // Prepare the expert program model with the explicit category
        final cloudProgram = CoinProgram(
          id: program.id,
          name: program.name,
          url: program.url,
          years: program.years,
          category: category, 
          coins: program.coins,
        );

        try {
          await _db.collection('global_programs').doc(cloudProgram.id).set(cloudProgram.toMap());
          debugPrint('Migrated Expert Program: ${cloudProgram.name} ($category)');
          count++;
        } catch (e) {
          debugPrint('FAILED to migrate ${cloudProgram.name}: $e');
        }
      }
    }
    
    debugPrint('Migration Complete. Total Expert Programs Created: $count');
  }
}
