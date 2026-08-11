import 'dart:math';
import 'dart:typed_data';

import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;

import '../models/program_model.dart';

/// Programs whose data is live/actively updated — show generation timestamp prominently.
const _activePrograms = {
  'American Innovation \$1 Coin Program',
  'American Women Quarters',
  'America the Beautiful Quarters (National Parks)',
  '2026 U.S. Circulating Coins',
};

class ChecklistGeneratorService {
  /// Sanitize strings for PDF Helvetica: replace characters outside Latin-1.
  static String _s(String? text) {
    if (text == null || text.isEmpty) return '';
    return text
        .replaceAll('\u2014', ' - ')  // em-dash
        .replaceAll('\u2013', '-')    // en-dash
        .replaceAll('\u2018', "'")    // left single quote
        .replaceAll('\u2019', "'")    // right single quote
        .replaceAll('\u201C', '"')    // left double quote
        .replaceAll('\u201D', '"')    // right double quote
        .replaceAll('\u2026', '...')  // ellipsis
        .replaceAll('\u00A0', ' ');   // non-breaking space
  }

  /// Safely renders memory image bytes, falling back gracefully if image header fails to parse.
  static pw.Widget _buildSafeMemoryImage(Uint8List? bytes, {double? width, double? height}) {
    if (bytes == null || bytes.isEmpty) return pw.SizedBox();
    try {
      return pw.Image(pw.MemoryImage(bytes), width: width, height: height);
    } catch (e) {
      return pw.SizedBox();
    }
  }

  /// Lightweight vector square checkbox for printable PDF tables.
  static pw.Widget _buildCheckboxSquare() {
    return pw.Center(
      child: pw.Container(
        width: 11,
        height: 11,
        decoration: pw.BoxDecoration(
          border: pw.Border.all(color: PdfColors.grey700, width: 0.8),
          borderRadius: const pw.BorderRadius.all(pw.Radius.circular(1.5)),
        ),
      ),
    );
  }

  /// Generates a dynamic PDF checklist for [program].
  ///
  /// [mintMarkDiagrams] maps mint_mark_type strings to PNG bytes for 8 templates.
  /// Generates a dynamic PDF checklist for [program].
  ///
  /// [mintMarkDiagrams] maps mint_mark_type strings to PNG bytes for 8 templates.
  static Future<Uint8List> generateChecklist(
    CoinProgram program, {
    Uint8List? logoBytes,
    Uint8List? edgeDiagramBytes,           // legacy compat
    Map<String, Uint8List>? mintMarkDiagrams,
    Uint8List? ttfFontBytes,
    Uint8List? ttfBoldFontBytes,
  }) async {
    final now = DateTime.now();
    final printDate = '${now.year}-${now.month.toString().padLeft(2,'0')}-${now.day.toString().padLeft(2,'0')}';
    final isActive = _activePrograms.contains(program.name);

    // ── Build Theme with custom UTF-8 TTF Font if provided ───────────────────
    pw.ThemeData? theme;
    if (ttfFontBytes != null && ttfFontBytes.isNotEmpty) {
      try {
        final ttf = pw.Font.ttf(ByteData.sublistView(ttfFontBytes));
        final ttfBold = (ttfBoldFontBytes != null && ttfBoldFontBytes.isNotEmpty)
            ? pw.Font.ttf(ByteData.sublistView(ttfBoldFontBytes))
            : ttf;
        theme = pw.ThemeData.withFont(base: ttf, bold: ttfBold);
      } catch (e) {
        // Fallback to default PDF font if font bytes are invalid
      }
    }

    final pdf = pw.Document(
      title: _s('${program.name} Checklist'),
      author: 'Numista.AI',
    );

    // ── Defensive Guard: Empty Coins List ────────────────────────────────────
    if (program.coins.isEmpty) {
      pdf.addPage(
        pw.Page(
          theme: theme,
          pageFormat: PdfPageFormat.letter,
          margin: const pw.EdgeInsets.all(32),
          build: (pw.Context context) {
            return pw.Center(
              child: pw.Column(
                mainAxisAlignment: pw.MainAxisAlignment.center,
                children: [
                  pw.Text('Numista.AI Official Program Checklist',
                      style: pw.TextStyle(fontSize: 18, fontWeight: pw.FontWeight.bold, color: PdfColors.blue800)),
                  pw.SizedBox(height: 12),
                  pw.Text(_s(program.name.toUpperCase()),
                      style: pw.TextStyle(fontSize: 16, fontWeight: pw.FontWeight.bold)),
                  pw.SizedBox(height: 24),
                  pw.Text('No coin items are currently configured for this program.',
                      style: const pw.TextStyle(fontSize: 12, color: PdfColors.grey700)),
                ],
              ),
            );
          },
        ),
      );
      return pdf.save();
    }

    // ── Resolve diagram ───────────────────────────────────────────────────────
    final mmType = program.mintMarkType ?? '';
    final mmDesc = _s(program.mintMarkDescription);

    Uint8List? diagramBytes;
    if (mintMarkDiagrams != null && mmType.isNotEmpty) {
      diagramBytes = mintMarkDiagrams[mmType];
    } else if (edgeDiagramBytes != null && (mmType == 'EDGE' || mmType.isEmpty)) {
      diagramBytes = edgeDiagramBytes;
    }

    // Text color based on type
    PdfColor labelColor;
    switch (mmType) {
      case 'EDGE':   labelColor = PdfColors.red700; break;
      case 'MIXED':  labelColor = PdfColors.orange800; break;
      default:       labelColor = PdfColors.blue800;
    }

    // ── Determine layout: simple (1 variety/row) vs multi-column ─────────────
    final maxVarieties = program.coins.fold<int>(
      0, (m, c) => max(m, c.varieties.isEmpty ? 1 : c.varieties.length));
    final useSimpleLayout = maxVarieties <= 1;

    // ── Build variety columns for multi layout ────────────────────────────────
    final varietiesSet = <String>{};
    if (!useSimpleLayout) {
      for (var coin in program.coins) {
        for (var v in coin.varieties) { varietiesSet.add(v.id); }
      }
    }
    final vList = varietiesSet.toList();
    final order = ['P', 'D', 'W', 'O', 'CC', 'S', 'S-VDB', 'P-VDB', 'S-SILVER',
                   'S-PROOF', 'S-SATIN', 'SMS'];
    vList.sort((a, b) {
      String baseA = a.replaceAll('-UNC', '');
      String baseB = b.replaceAll('-UNC', '');
      int idxA = order.indexOf(baseA); if (idxA == -1) idxA = 99;
      int idxB = order.indexOf(baseB); if (idxB == -1) idxB = 99;
      return idxA == idxB ? a.compareTo(b) : idxA.compareTo(idxB);
    });
    final varietyLabels = vList.map((id) => _s(ChecklistVariety.fromId(id).label)).toList();

    // ── Helper: coin label without duplicate year ────────────────────────────
    String coinLabel(ProgramCoin coin) {
      final yr  = coin.year ?? '';
      final nm  = _s(coin.name);
      if (yr.isEmpty) return nm;
      // Avoid "1879 - 1879" or "1909 - 1909-S VDB"
      if (nm == yr || nm.startsWith(yr)) return nm;
      return '$yr - $nm';
    }

    // ── Table data builders ───────────────────────────────────────────────────
    List<dynamic> buildMultiRow(ProgramCoin coin, int rowIndex) {
      final row = <dynamic>[coinLabel(coin)];
      final coinVarietyIds = coin.varieties.map((v) => v.id).toSet();
      for (var v in vList) {
        if (coinVarietyIds.contains(v)) {
          row.add(_buildCheckboxSquare());
        } else {
          row.add('');
        }
      }
      row.add(''); // Notes
      return row;
    }

    pdf.addPage(
      pw.MultiPage(
        theme: theme,
        pageFormat: PdfPageFormat.letter,
        margin: const pw.EdgeInsets.fromLTRB(32, 32, 32, 48), // extra bottom for footer

        // ── Footer (page 2+) ───────────────────────────────────────────────
        footer: (pw.Context context) {
          if (context.pageNumber <= 1) return pw.SizedBox();
          return pw.Container(
            decoration: const pw.BoxDecoration(
              border: pw.Border(top: pw.BorderSide(color: PdfColors.grey300, width: 0.5))),
            padding: const pw.EdgeInsets.only(top: 4),
            child: pw.Row(
              mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
              children: [
                pw.Text(_s(program.name.toUpperCase()),
                    style: const pw.TextStyle(fontSize: 8, color: PdfColors.grey600)),
                pw.Text('Page ${context.pageNumber} of ${context.pagesCount}',
                    style: const pw.TextStyle(fontSize: 8, color: PdfColors.grey600)),
                pw.Text('Printed: $printDate',
                    style: const pw.TextStyle(fontSize: 8, color: PdfColors.grey600)),
              ],
            ),
          );
        },

        build: (pw.Context context) {
          return [
            // ── Header ─────────────────────────────────────────────────────
            pw.Header(
              level: 0,
              child: pw.Row(
                mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
                children: [
                  pw.Row(children: [
                    if (logoBytes != null) ...[
                      _buildSafeMemoryImage(logoBytes, width: 30, height: 30),
                      pw.SizedBox(width: 8),
                    ],
                    pw.Text('Numista.AI Checklist',
                        style: pw.TextStyle(fontSize: 20,
                            fontWeight: pw.FontWeight.bold,
                            color: PdfColors.blue800)),
                  ]),
                  pw.Column(
                    crossAxisAlignment: pw.CrossAxisAlignment.end,
                    children: [
                      pw.Text('Generated: $printDate',
                          style: const pw.TextStyle(fontSize: 9, color: PdfColors.grey500)),
                      if (isActive)
                        pw.Text('* Active series - verify for latest coins',
                            style: pw.TextStyle(fontSize: 8, color: PdfColors.orange700,
                                fontStyle: pw.FontStyle.italic)),
                    ],
                  ),
                ],
              ),
            ),
            pw.SizedBox(height: 8),

            // ── Program title + years ───────────────────────────────────────
            pw.Row(
              crossAxisAlignment: pw.CrossAxisAlignment.end,
              children: [
                pw.Text(_s(program.name.toUpperCase()),
                    style: pw.TextStyle(fontSize: 18, fontWeight: pw.FontWeight.bold)),
                pw.SizedBox(width: 8),
                if (program.years.isNotEmpty)
                  pw.Text('(${_s(program.years)})',
                      style: const pw.TextStyle(fontSize: 14, color: PdfColors.grey700)),
              ],
            ),
            if (program.category.isNotEmpty && program.category != 'Other')
              pw.Text('Category: ${_s(program.category)}',
                  style: const pw.TextStyle(fontSize: 12, color: PdfColors.grey)),

            // ── Mint Mark Box ───────────────────────────────────────────────
            if (program.mintMarkLocations.isNotEmpty || mmDesc.isNotEmpty) ...[
              pw.SizedBox(height: 6),
              pw.Container(
                padding: const pw.EdgeInsets.all(8),
                decoration: pw.BoxDecoration(
                  border: pw.Border.all(color: PdfColors.grey300),
                  borderRadius: const pw.BorderRadius.all(pw.Radius.circular(4)),
                  color: PdfColors.grey50,
                ),
                child: pw.Column(
                  crossAxisAlignment: pw.CrossAxisAlignment.start,
                  children: [
                    if (program.mintMarkLocations.isNotEmpty)
                      pw.Text(_s(program.mintMarkLocations),
                          style: pw.TextStyle(fontSize: 10,
                              color: PdfColors.grey700,
                              fontStyle: pw.FontStyle.italic)),
                    if (mmDesc.isNotEmpty) ...[
                      pw.SizedBox(height: 6),
                      pw.Row(
                        crossAxisAlignment: pw.CrossAxisAlignment.center,
                        children: [
                          // TEXT LEFT
                          pw.Expanded(
                            child: pw.Text(mmDesc,
                                style: pw.TextStyle(fontSize: 11,
                                    fontWeight: pw.FontWeight.bold,
                                    color: labelColor)),
                          ),
                          // DIAGRAM RIGHT
                          if (diagramBytes != null) ...[
                            pw.SizedBox(width: 14),
                            _buildSafeMemoryImage(diagramBytes, width: 160, height: 76),
                          ],
                        ],
                      ),
                    ],
                  ],
                ),
              ),
            ],

            pw.SizedBox(height: 8),
            pw.Text(
              "Check off the coins you own. Use the 'Notes / QTY' column to record quantity IF you have more than 1 (e.g. QTY:3) and grade (e.g. MS-65 or VF-30).",
              style: const pw.TextStyle(fontSize: 10, color: PdfColors.grey700),
            ),
            pw.SizedBox(height: 16),

            // ── Coin Table ──────────────────────────────────────────────────
            if (useSimpleLayout) ...[
              // 2-up layout: pair consecutive coins side-by-side to halve page count
              () {
                final pairs = <List<ProgramCoin>>[];
                for (int i = 0; i < program.coins.length; i += 2) {
                  pairs.add(program.coins.sublist(
                      i, min(i + 2, program.coins.length)));
                }
                return pw.TableHelper.fromTextArray(
                  headers: [
                    'Year / Subject', 'Owned?', 'Notes / QTY',
                    'Year / Subject', 'Owned?', 'Notes / QTY',
                  ],
                  headerStyle: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 10),
                  headerDecoration: const pw.BoxDecoration(color: PdfColors.grey200),
                  cellHeight: 26,
                  columnWidths: {
                    0: const pw.FlexColumnWidth(3),
                    1: const pw.FixedColumnWidth(54), // wide enough for 'Owned?' on one line
                    2: const pw.FlexColumnWidth(1.6),
                    3: const pw.FlexColumnWidth(3),
                    4: const pw.FixedColumnWidth(54),
                    5: const pw.FlexColumnWidth(1.6),
                  },
                  cellAlignments: {
                    0: pw.Alignment.centerLeft,
                    1: pw.Alignment.center,
                    2: pw.Alignment.centerLeft,
                    3: pw.Alignment.centerLeft,
                    4: pw.Alignment.center,
                    5: pw.Alignment.centerLeft,
                  },
                  data: pairs.map((pair) {
                    final coinA = pair[0];
                    final row = <dynamic>[
                      coinLabel(coinA),
                      _buildCheckboxSquare(),
                      '',
                    ];
                    if (pair.length > 1) {
                      final coinB = pair[1];
                      row.addAll([
                        coinLabel(coinB),
                        _buildCheckboxSquare(),
                        '',
                      ]);
                    } else {
                      row.addAll(['', '', '']); // pad odd-count programs
                    }
                    return row;
                  }).toList(),
                );
              }(),
            ] else
              () {
                // ── Dynamic sizing ───────────────────────────────────────────
                final hFont = vList.length >= 6 ? 8.0
                            : vList.length >= 4 ? 9.0 : 11.0;

                // Year/Subject: size to the longest actual label + a small pad
                final maxLabelLen = program.coins
                    .map((c) => coinLabel(c).length)
                    .fold<int>(0, max);
                // ~6pt per char at font 11; clamp between 100 and 210
                final yrColW = (maxLabelLen * 6.2).clamp(100.0, 210.0);

                // Per-column width: short IDs (P, D, S, W, O) → narrow; longer → wider
                double colWidthFor(String id) {
                  if (id.length <= 2) return 26.0;   // P, D, S, W, O — just a checkbox
                  if (vList.length >= 6) return 38.0; // many columns — stay tight
                  if (vList.length >= 4) return 44.0;
                  return 52.0;
                }

                // Notes: flex — takes whatever is left over
                final hasTypes = vList.any((id) => id.contains('-T'));

                return pw.Column(
                  crossAxisAlignment: pw.CrossAxisAlignment.start,
                  children: [
                    pw.TableHelper.fromTextArray(
                      headers: ['Year / Subject', ...varietyLabels, 'Notes / QTY'],
                      headerStyle: pw.TextStyle(
                          fontWeight: pw.FontWeight.bold, fontSize: hFont),
                      headerDecoration: const pw.BoxDecoration(color: PdfColors.grey200),
                      cellHeight: 28,
                      columnWidths: {
                        0: pw.FixedColumnWidth(yrColW),
                        for (int i = 1; i <= vList.length; i++)
                          i: pw.FixedColumnWidth(colWidthFor(vList[i - 1])),
                        vList.length + 1: const pw.FlexColumnWidth(1),
                      },
                      cellAlignments: {
                        0: pw.Alignment.centerLeft,
                        for (int i = 1; i <= vList.length; i++) i: pw.Alignment.center,
                        vList.length + 1: pw.Alignment.centerLeft,
                      },
                      data: program.coins.asMap().entries
                          .map((e) => buildMultiRow(e.value, e.key))
                          .toList(),
                    ),
                    // Bicentennial Type 1 / Type 2 key
                    if (hasTypes) ...[
                      pw.SizedBox(height: 5),
                      pw.Text(
                        '* 1976 Bicentennial Types:  '
                        'Type 1 = Block lettering "DOLLAR" (early 1975-76 production).  '
                        'Type 2 = Redesigned, slightly slimmer lettering (later 1976 production).',
                        style: pw.TextStyle(fontSize: 8, color: PdfColors.grey600,
                            fontStyle: pw.FontStyle.italic),
                      ),
                    ],
                  ],
                );
              }(),

            // ── Notes Block ─────────────────────────────────────────────────
            pw.SizedBox(height: 24),
            pw.Text('ADDITIONAL NOTES',
                style: pw.TextStyle(fontSize: 11, fontWeight: pw.FontWeight.bold,
                    color: PdfColors.grey700)),
            pw.SizedBox(height: 6),
            ...List.generate(8, (_) => pw.Column(
              children: [
                pw.SizedBox(height: 14),
                pw.Container(height: 0.5,
                    decoration: const pw.BoxDecoration(
                        border: pw.Border(bottom: pw.BorderSide(
                            color: PdfColors.grey400, width: 0.5)))),
              ],
            )),
          ];
        },
      ),
    );

    return pdf.save();
  }
}
