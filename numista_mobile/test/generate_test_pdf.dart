import 'dart:io';
import 'dart:convert';
import 'dart:typed_data';
import 'package:numista_ai/models/program_model.dart';
import 'package:numista_ai/services/checklist_generator_service.dart';

/// Generic test script — pass the program name fragment as first arg.
/// Usage: dart test/generate_test_pdf.dart "Morgan"
///        dart test/generate_test_pdf.dart "Eisenhower"
void main(List<String> args) async {
  final searchTerm = args.isNotEmpty ? args[0].toLowerCase() : 'women';

  final jsonFile = File('../numista_backend/master_coin_programs.json');
  if (!jsonFile.existsSync()) { stderr.writeln("Could not find master_coin_programs.json"); exit(1); }

  final List<dynamic> allPrograms = jsonDecode(jsonFile.readAsStringSync());

  dynamic targetProgJson;
  for (var p in allPrograms) {
    final progName = (p['Name'] ?? p['name'] ?? '').toString();
    if (progName.toLowerCase().contains(searchTerm)) {
      targetProgJson = p; break;
    }
  }
  if (targetProgJson == null) { stderr.writeln("No program matching '$searchTerm'."); exit(1); }
  final progTitle = (targetProgJson['Name'] ?? targetProgJson['name']).toString();
  stdout.writeln("Found Program: $progTitle");

  final coinsData = (targetProgJson['Coins'] ?? targetProgJson['coins']) as List<dynamic>? ?? [];
  final coinsList = coinsData.map((c) {
    var rawVarieties = (c['varieties'] ?? c['Varieties']) as List<dynamic>?;
    List<ChecklistVariety> mappedVarieties = [];
    if (rawVarieties != null && rawVarieties.isNotEmpty) {
      mappedVarieties = rawVarieties.map((v) {
        if (v is Map) return ChecklistVariety(id: v['id'] ?? v.toString(), label: v['label'] ?? v.toString());
        return ChecklistVariety.fromId(v.toString());
      }).toList();
    } else {
      mappedVarieties = [ChecklistVariety.fromId('P'), ChecklistVariety.fromId('D')];
    }
    return ProgramCoin(
      id: (c['id'] ?? c['name'] ?? '').toString(),
      name: (c['name'] ?? c['Name'] ?? '').toString(),
      year: c['year']?.toString() ?? c['Year']?.toString(),
      varieties: mappedVarieties,
    );
  }).toList();

  final prog = CoinProgram(
    id: targetProgJson['Id']?.toString() ?? targetProgJson['id']?.toString() ?? searchTerm,
    name: progTitle,
    years: (targetProgJson['Years'] ?? targetProgJson['years'] ?? '').toString(),
    url: '',
    category: (targetProgJson['Category'] ?? targetProgJson['category'] ?? '').toString(),
    mintMarkLocations: (targetProgJson['Mint_mark_locations'] ?? targetProgJson['mint_mark_locations'] ?? '').toString(),
    mintMarkType: (targetProgJson['Mint_mark_type'] ?? targetProgJson['mint_mark_type'])?.toString(),
    mintMarkDescription: (targetProgJson['Mint_mark_description'] ?? targetProgJson['mint_mark_description'])?.toString(),
    coins: coinsList,
  );

  // ── Load logo ─────────────────────────────────────────────────────────────
  Uint8List? logoBytes;
  try { logoBytes = File('assets/logo_owl.png').readAsBytesSync(); } catch (_) {}

  // ── Load fonts ────────────────────────────────────────────────────────────
  Uint8List? fontBytes;
  Uint8List? boldFontBytes;
  try { fontBytes = File('assets/fonts/Roboto-Regular.ttf').readAsBytesSync(); } catch (_) {}
  try { boldFontBytes = File('assets/fonts/Roboto-Bold.ttf').readAsBytesSync(); } catch (_) {}

  // ── Load all 8 mint mark diagrams ─────────────────────────────────────────
  const diagramTypes = ['EDGE','OBVERSE_PORTRAIT','OBVERSE_DATE',
                        'REVERSE_EAGLE','REVERSE_LOWER','REVERSE_UPPER','MIXED','NONE'];
  final Map<String, Uint8List> mintMarkDiagrams = {};
  for (final t in diagramTypes) {
    final f = File('assets/mint_mark_diagrams/$t.png');
    if (f.existsSync()) mintMarkDiagrams[t] = f.readAsBytesSync();
  }
  stdout.writeln('Loaded ${mintMarkDiagrams.length}/8 mint mark diagrams.');

  stdout.writeln('Generating PDF for ${prog.name} (${prog.coins.length} coins)...');
  final bytes = await ChecklistGeneratorService.generateChecklist(
    prog,
    logoBytes: logoBytes,
    mintMarkDiagrams: mintMarkDiagrams,
    ttfFontBytes: fontBytes,
    ttfBoldFontBytes: boldFontBytes,
  );

  final safeName = prog.name
      .toLowerCase()
      .replaceAll(RegExp(r'[^a-z0-9]+'), '_')
      .replaceAll(RegExp(r'_+'), '_')
      .replaceAll(RegExp(r'^_|_$'), '');
  await File('${safeName}_checklist.pdf').writeAsBytes(bytes);
  stdout.writeln('Saved PDF to ${safeName}_checklist.pdf');
}
