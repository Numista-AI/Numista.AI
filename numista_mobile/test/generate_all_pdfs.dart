#!/usr/bin/env dart
/// Generates PDFs for EVERY program in master_coin_programs.json
/// Uses the full mint mark diagram taxonomy (8 types).
/// Usage: dart test/generate_all_pdfs.dart
library;
import 'dart:io';
import 'dart:convert';
import 'dart:typed_data';
import 'package:numista_ai/models/program_model.dart';
import 'package:numista_ai/services/checklist_generator_service.dart';

void main() async {
  final jsonFile = File('../numista_backend/master_coin_programs.json');
  final List<dynamic> allPrograms = jsonDecode(jsonFile.readAsStringSync());

  // Load logo
  Uint8List? logoBytes;
  try { logoBytes = File('assets/logo_owl.png').readAsBytesSync(); } catch (_) {}

  // Load all 8 mint mark diagrams from assets/mint_mark_diagrams/
  const diagramTypes = [
    'EDGE', 'OBVERSE_PORTRAIT', 'OBVERSE_DATE',
    'REVERSE_EAGLE', 'REVERSE_LOWER', 'REVERSE_UPPER',
    'MIXED', 'NONE',
  ];
  final Map<String, Uint8List> mintMarkDiagrams = {};
  for (final t in diagramTypes) {
    final f = File('assets/mint_mark_diagrams/$t.png');
    if (f.existsSync()) {
      mintMarkDiagrams[t] = f.readAsBytesSync();
      stdout.writeln('Loaded diagram: $t.png');
    } else {
      stderr.writeln('WARNING: Missing diagram: $t.png');
    }
  }

  int success = 0, skipped = 0;

  for (final p in allPrograms) {
    final progName = p['name']?.toString() ?? '';

    // Skip reference-only and superseded entries
    if (p['_skip_checklist'] == true || p['category'] == 'Reference') {
      stdout.writeln('SKIP: $progName');
      skipped++;
      continue;
    }

    final coinsData = p['coins'] as List<dynamic>? ?? [];
    if (coinsData.isEmpty) {
      stdout.writeln('SKIP (no coins): $progName');
      skipped++;
      continue;
    }

    final coinsList = coinsData.map((c) {
      final rawV = c['varieties'] as List<dynamic>?;
      List<ChecklistVariety> varieties = [];
      if (rawV != null && rawV.isNotEmpty) {
        varieties = rawV.map((v) {
          if (v is Map) {
            return ChecklistVariety(
              id: v['id']?.toString() ?? '',
              label: v['label']?.toString() ?? '',
            );
          }
          return ChecklistVariety.fromId(v.toString());
        }).toList();
      } else {
        varieties = [ChecklistVariety.fromId('P'), ChecklistVariety.fromId('D')];
      }
      return ProgramCoin(
        id: c['id']?.toString() ?? c['name'].toString().replaceAll(' ', '_'),
        name: c['name']?.toString() ?? '',
        year: c['year']?.toString(),
        varieties: varieties,
      );
    }).toList();

    final prog = CoinProgram(
      id: p['id']?.toString() ?? progName.toLowerCase().replaceAll(' ', '_'),
      name: progName,
      years: p['years']?.toString() ?? '',
      url: '',
      category: p['category']?.toString() ?? '',
      mintMarkLocations: p['mint_mark_locations']?.toString() ?? '',
      mintMarkType: p['mint_mark_type']?.toString(),
      mintMarkDescription: p['mint_mark_description']?.toString(),
      coins: coinsList,
    );

    try {
      final bytes = await ChecklistGeneratorService.generateChecklist(
        prog,
        logoBytes: logoBytes,
        mintMarkDiagrams: mintMarkDiagrams,
      );
      final safe = progName
          .toLowerCase()
          .replaceAll(RegExp(r'[^a-z0-9]+'), '_')
          .replaceAll(RegExp(r'^_|_$'), '');
      await File('${safe}_checklist.pdf').writeAsBytes(bytes);
      stdout.writeln('OK [${p['mint_mark_type'] ?? '?'}]: ${safe}_checklist.pdf  (${coinsList.length} coins)');
      success++;
    } catch (e) {
      stderr.writeln('ERROR: $progName — $e');
    }
  }

  stdout.writeln('\nDone: $success PDFs generated, $skipped skipped.');
}
