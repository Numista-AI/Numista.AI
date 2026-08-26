import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../services/auth_service.dart';
import '../services/mint_history_service.dart';

// ─── Roll types ───────────────────────────────────────────────────────────────
enum RollType { identical, sequential, mixed, lot }

// ─── Result returned to the caller ───────────────────────────────────────────
class RollEntryResult {
  final int coinsAdded;
  final String rollId;
  const RollEntryResult(this.coinsAdded, this.rollId);
}

// ─── Colours (match app palette) ─────────────────────────────────────────────
const _bg      = Color(0xFFF8FAFC);
const _surface = Colors.white;
const _text    = Color(0xFF1E293B);
const _sub     = Color(0xFF64748B);
const _accent  = Color(0xFFF63366);
const _blue    = Color(0xFF4C8CDA);
const _border  = Color(0xFFE2E6E9);

// ─────────────────────────────────────────────────────────────────────────────
// Main entry point — call this from any upload tab
// ─────────────────────────────────────────────────────────────────────────────
Future<RollEntryResult?> showRollEntryDialog(BuildContext context) {
  return showDialog<RollEntryResult>(
    context: context,
    barrierDismissible: false,
    builder: (_) => const _RollDialog(),
  );
}

// ─────────────────────────────────────────────────────────────────────────────
class _RollDialog extends StatefulWidget {
  const _RollDialog();
  @override
  State<_RollDialog> createState() => _RollDialogState();
}

class _RollDialogState extends State<_RollDialog> {
  int        _step     = 0;       // 0=type, 1=details, 2=preview
  RollType?  _rollType;

  // Shared fields
  String _denom    = 'quarter';
  String _condition = 'Circulated';
  String _notes    = '';

  // Identical roll
  int    _quantity = 40;
  int    _year     = DateTime.now().year;
  String _mint     = 'P';

  // Sequential years
  int    _startYear = 1970;
  int    _endYear   = 1990;
  // year → set of selected mint marks
  Map<int, Set<String>> _yearMints = {};

  // Lot
  String _lotNotes = '';

  // Preview list
  List<Map<String, dynamic>> _preview = [];

  // ── Step 0: choose roll type ──────────────────────────────────────────────
  Widget _buildTypeStep() {
    final types = [
      (RollType.identical,  Icons.content_copy_outlined,   'Identical Roll',
       'All the same coin — same year, mint, condition'),
      (RollType.sequential, Icons.linear_scale_outlined,    'Sequential Years',
       'Same denomination across a range of years'),
      (RollType.mixed,      Icons.shuffle_outlined,          'Mixed Roll',
       'Unknown contents — I\'ll scan each coin individually'),
      (RollType.lot,        Icons.inventory_2_outlined,      'Unopened Lot',
       'Record as a single lot, verify later'),
    ];
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('What kind of roll?', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: _text)),
        const SizedBox(height: 4),
        const Text('Choose the type that best describes your coins.', style: TextStyle(color: _sub, fontSize: 13)),
        const SizedBox(height: 20),
        ...types.map((t) {
          final selected = _rollType == t.$1;
          return GestureDetector(
            onTap: () => setState(() => _rollType = t.$1),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 180),
              margin: const EdgeInsets.only(bottom: 10),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: selected ? _accent.withAlpha(15) : _surface,
                border: Border.all(color: selected ? _accent : _border, width: selected ? 2 : 1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Row(children: [
                Icon(t.$2, color: selected ? _accent : _sub, size: 22),
                const SizedBox(width: 14),
                Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(t.$3, style: TextStyle(fontWeight: FontWeight.w600, color: selected ? _accent : _text, fontSize: 14)),
                  Text(t.$4, style: const TextStyle(color: _sub, fontSize: 12)),
                ])),
                if (selected) const Icon(Icons.check_circle, color: _accent, size: 20),
              ]),
            ),
          );
        }),
      ],
    );
  }

  // ── Shared: denomination picker ───────────────────────────────────────────
  Widget _denomPicker() => DropdownButtonFormField<String>(
    initialValue: _denom,
    decoration: _decor('Denomination'),
    items: kDenominations.map((d) =>
      DropdownMenuItem(value: d['key'], child: Text(d['label']!))).toList(),
    onChanged: (v) => setState(() { _denom = v!; _quantity = kRollSize[v] ?? 40; }),
  );

  Widget _conditionPicker() => DropdownButtonFormField<String>(
    initialValue: _condition,
    decoration: _decor('Condition'),
    items: ['Poor','Good','Fine','Very Fine','Extremely Fine','About Unc.',
            'MS-60','MS-63','MS-65','MS-67','Proof','Circulated','Uncirculated']
      .map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
    onChanged: (v) => setState(() => _condition = v!),
  );

  InputDecoration _decor(String label) => InputDecoration(
    labelText: label, border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
  );

  // ── Step 1A: identical roll ───────────────────────────────────────────────
  Widget _buildIdenticalStep() {
    final mints = MintHistoryService.getMints(_denom, _year);
    return Column(mainAxisSize: MainAxisSize.min, children: [
      _denomPicker(),
      const SizedBox(height: 12),
      Row(children: [
        Expanded(child: TextFormField(
          initialValue: _year.toString(),
          decoration: _decor('Year'),
          keyboardType: TextInputType.number,
          onChanged: (v) => setState(() { _year = int.tryParse(v) ?? _year; }),
        )),
        const SizedBox(width: 12),
        Expanded(child: DropdownButtonFormField<String>(
          initialValue: mints.contains(_mint) ? _mint : (mints.isNotEmpty ? mints.first : ''),
          decoration: _decor('Mint Mark'),
          items: mints.map((m) => DropdownMenuItem(value: m, child: Text(m.isEmpty ? 'P (no mark)' : m))).toList(),
          onChanged: (v) => setState(() => _mint = v ?? ''),
        )),
      ]),
      const SizedBox(height: 12),
      Row(children: [
        Expanded(child: TextFormField(
          initialValue: _quantity.toString(),
          decoration: _decor('Quantity (coins)'),
          keyboardType: TextInputType.number,
          onChanged: (v) => setState(() => _quantity = int.tryParse(v) ?? _quantity),
        )),
        const SizedBox(width: 12),
        Expanded(child: _conditionPicker()),
      ]),
      const SizedBox(height: 12),
      TextFormField(
        decoration: _decor('Notes (optional)'),
        onChanged: (v) => setState(() => _notes = v),
      ),
    ]);
  }

  // ── Step 1B: sequential years ─────────────────────────────────────────────
  void _loadSequentialMints() {
    final rows = MintHistoryService.getRange(_denom, _startYear, _endYear);
    _yearMints = { for (final r in rows) r.year: Set<String>.from(r.circulation) };
  }

  Widget _buildSequentialStep() {
    return Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
      _denomPicker(),
      const SizedBox(height: 12),
      Row(children: [
        Expanded(child: TextFormField(
          initialValue: _startYear.toString(),
          decoration: _decor('Start Year'),
          keyboardType: TextInputType.number,
          onChanged: (v) { setState(() { _startYear = int.tryParse(v) ?? _startYear; _loadSequentialMints(); }); },
        )),
        const SizedBox(width: 12),
        Expanded(child: TextFormField(
          initialValue: _endYear.toString(),
          decoration: _decor('End Year'),
          keyboardType: TextInputType.number,
          onChanged: (v) { setState(() { _endYear = int.tryParse(v) ?? _endYear; _loadSequentialMints(); }); },
        )),
        const SizedBox(width: 12),
        ElevatedButton(
          style: ElevatedButton.styleFrom(backgroundColor: _blue, foregroundColor: Colors.white, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8))),
          onPressed: () => setState(_loadSequentialMints),
          child: const Text('Load'),
        ),
      ]),
      const SizedBox(height: 12),
      _conditionPicker(),
      const SizedBox(height: 16),
      if (_yearMints.isEmpty)
        const Text('Tap Load to auto-fill mint marks.', style: TextStyle(color: _sub, fontSize: 12))
      else ...[
        Row(children: [
          const Text('Uncheck mints you don\'t have:', style: TextStyle(color: _sub, fontSize: 12)),
          const Spacer(),
          Text('${_yearMints.values.fold(0, (s, m) => s + m.length)} coins selected', style: const TextStyle(color: _blue, fontSize: 12, fontWeight: FontWeight.w600)),
        ]),
        const SizedBox(height: 8),
        ConstrainedBox(
          constraints: const BoxConstraints(maxHeight: 260),
          child: SingleChildScrollView(
            child: Table(
              columnWidths: const {0: FixedColumnWidth(56)},
              border: TableBorder.all(color: _border, width: 0.5, borderRadius: BorderRadius.circular(6)),
              children: [
                TableRow(decoration: const BoxDecoration(color: Color(0xFFF1F5F9)), children: [
                  const Padding(padding: EdgeInsets.all(8), child: Text('Year', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: _text))),
                  ..._allMints().map((m) => Padding(padding: const EdgeInsets.all(8),
                    child: Text(m.isEmpty ? 'P*' : m, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: _text), textAlign: TextAlign.center))),
                ]),
                ..._yearMints.entries.map((e) {
                  final year = e.key;
                  final available = MintHistoryService.getMints(_denom, year);
                  return TableRow(children: [
                    Padding(padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
                      child: Text(year.toString(), style: const TextStyle(fontSize: 12, color: _text))),
                    ..._allMints().map((m) {
                      final avail = available.contains(m);
                      final checked = e.value.contains(m);
                      return Center(child: avail
                        ? Checkbox(
                            value: checked,
                            activeColor: _accent,
                            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                            onChanged: (v) => setState(() { v == true ? e.value.add(m) : e.value.remove(m); }))
                        : const Text('—', style: TextStyle(color: _border, fontSize: 12)),
                      );
                    }),
                  ]);
                }),
              ],
            ),
          ),
        ),
        const SizedBox(height: 6),
        const Text('* P (no mark) = Philadelphia pre-1980', style: TextStyle(color: _sub, fontSize: 10)),
      ],
    ]);
  }

  List<String> _allMints() {
    final all = <String>{};
    for (final s in _yearMints.values) { all.addAll(s); }
    for (final e in _yearMints.entries) {
      all.addAll(MintHistoryService.getMints(_denom, e.key));
    }
    final ordered = ['', 'P', 'D', 'S', 'W', 'CC', 'O'];
    return ordered.where(all.contains).toList();
  }

  // ── Step 1D: lot ──────────────────────────────────────────────────────────
  Widget _buildLotStep() => Column(mainAxisSize: MainAxisSize.min, children: [
    _denomPicker(),
    const SizedBox(height: 12),
    Row(children: [
      Expanded(child: TextFormField(initialValue: _startYear.toString(), decoration: _decor('Approx. Start Year (optional)'), keyboardType: TextInputType.number, onChanged: (v) => setState(() => _startYear = int.tryParse(v) ?? _startYear))),
      const SizedBox(width: 12),
      Expanded(child: TextFormField(initialValue: _quantity.toString(), decoration: _decor('Approximate Count'), keyboardType: TextInputType.number, onChanged: (v) => setState(() => _quantity = int.tryParse(v) ?? _quantity))),
    ]),
    const SizedBox(height: 12),
    TextFormField(maxLines: 3, decoration: _decor('Notes / Description'), onChanged: (v) => setState(() => _lotNotes = v)),
    const SizedBox(height: 12),
    Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(color: const Color(0xFFFFF8E1), borderRadius: BorderRadius.circular(8), border: Border.all(color: const Color(0xFFFFD54F))),
      child: const Row(children: [
        Icon(Icons.info_outline, color: Color(0xFFF57F17), size: 16),
        SizedBox(width: 8),
        Expanded(child: Text('This will create a single "Lot" record flagged for future verification. You can expand it later using the AI scanner.', style: TextStyle(fontSize: 12, color: Color(0xFF5D4037)))),
      ]),
    ),
  ]);

  // ── Build preview list ────────────────────────────────────────────────────
  void _buildPreview() {
    _preview = [];
    final denomLabel = kDenominations.firstWhere((d) => d['key'] == _denom, orElse: () => {'label': _denom})['label']!;
    final series = kDenominations.firstWhere((d) => d['key'] == _denom, orElse: () => {'series': _denom})['series']!;

    switch (_rollType) {
      case RollType.identical:
        for (int i = 0; i < _quantity; i++) {
          _preview.add({'Year': _year.toString(), 'Mint Mark': _mint, 'Denomination': denomLabel, 'Program/Series': series, 'Condition': _condition, 'Personal Notes': _notes});
        }
        break;
      case RollType.sequential:
        for (final e in _yearMints.entries) {
          for (final m in e.value) {
            _preview.add({'Year': e.key.toString(), 'Mint Mark': m, 'Denomination': denomLabel, 'Program/Series': series, 'Condition': _condition});
          }
        }
        break;
      case RollType.lot:
        _preview.add({'Year': _startYear > 0 ? '~$_startYear' : 'Unknown', 'Denomination': denomLabel, 'Program/Series': series, 'Condition': 'Unknown', 'Personal Notes': _lotNotes, 'roll_type': 'lot', 'lot_quantity': _quantity});
        break;
      default: break;
    }
  }

  // ── Step 2: preview ───────────────────────────────────────────────────────
  Widget _buildPreviewStep() {
    if (_preview.isEmpty) return const Center(child: Text('No coins to add.', style: TextStyle(color: _sub)));
    return Column(mainAxisSize: MainAxisSize.min, crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(children: [
        const Icon(Icons.fact_check_outlined, color: _blue, size: 20),
        const SizedBox(width: 8),
        Text('${_preview.length} coin${_preview.length == 1 ? '' : 's'} will be added', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: _text)),
      ]),
      const SizedBox(height: 12),
      ConstrainedBox(
        constraints: const BoxConstraints(maxHeight: 320),
        child: ListView.separated(
          shrinkWrap: true,
          itemCount: _preview.length > 50 ? 51 : _preview.length,
          separatorBuilder: (_, _) => const Divider(height: 1, color: _border),
          itemBuilder: (_, i) {
            if (i == 50) return Padding(padding: const EdgeInsets.all(8), child: Text('... and ${_preview.length - 50} more', style: const TextStyle(color: _sub, fontSize: 12)));
            final c = _preview[i];
            final mint = c['Mint Mark'] as String? ?? '';
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 4),
              child: Row(children: [
                SizedBox(width: 48, child: Text(c['Year'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: _text))),
                if (mint.isNotEmpty) Container(
                  margin: const EdgeInsets.only(right: 8),
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(color: _blue.withAlpha(20), borderRadius: BorderRadius.circular(4), border: Border.all(color: _blue.withAlpha(80))),
                  child: Text(mint, style: const TextStyle(fontSize: 11, color: _blue, fontWeight: FontWeight.bold)),
                ),
                Expanded(child: Text(c['Program/Series'] ?? c['Denomination'] ?? '', style: const TextStyle(fontSize: 12, color: _sub), overflow: TextOverflow.ellipsis)),
                Text(c['Condition'] ?? '', style: const TextStyle(fontSize: 11, color: _sub)),
              ]),
            );
          },
        ),
      ),
    ]);
  }

  // ── Commit to Firestore ───────────────────────────────────────────────────
  Future<void> _commit() async {
    final rollId = 'roll_${_denom}_${DateTime.now().millisecondsSinceEpoch}';
    final email  = AuthService.userEmail;
    final col    = FirebaseFirestore.instance.collection('users').doc(email).collection('coins');
    var batch    = FirebaseFirestore.instance.batch();
    int count    = 0;

    for (final coin in _preview) {
      final doc = col.doc();
      batch.set(doc, {
        ...coin,
        'roll_id':          rollId,
        'roll_type':        _rollType?.name ?? 'unknown',
        'added_at':         DateTime.now().toIso8601String(),
        'source':           'roll_wizard',
        // ITEM 6: stamp is_demo: false so real coins remain visible after display filter ships
        'is_demo':          false,
        'is_demo_cleared':  false,
      });
      count++;
      if (count % 400 == 0) {
        await batch.commit();
        batch = FirebaseFirestore.instance.batch();
      }
    }
    await batch.commit();

    if (mounted) Navigator.pop(context, RollEntryResult(count, rollId));
  }

  // ── Dialog chrome ─────────────────────────────────────────────────────────
  String get _title => ['What kind of roll?', _rollType == RollType.identical ? 'Identical Roll Details' : _rollType == RollType.sequential ? 'Sequential Years' : _rollType == RollType.lot ? 'Lot Details' : 'Roll Details', 'Preview & Confirm'][_step];

  bool get _canNext {
    if (_step == 0) return _rollType != null && _rollType != RollType.mixed;
    if (_step == 1) {
      if (_rollType == RollType.sequential) return _yearMints.isNotEmpty && _yearMints.values.any((s) => s.isNotEmpty);
      return true;
    }
    return _preview.isNotEmpty;
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      backgroundColor: _bg,
      insetPadding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 680),
        child: Padding(
          padding: const EdgeInsets.all(28),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(children: [
                if (_step > 0) IconButton(icon: const Icon(Icons.arrow_back, color: _sub), onPressed: () => setState(() => _step--), tooltip: 'Back'),
                const Icon(Icons.currency_exchange, color: _accent, size: 24),
                const SizedBox(width: 10),
                Expanded(child: Text(_title, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: _text))),
                // Step indicator
                Row(children: List.generate(3, (i) => Container(
                  margin: const EdgeInsets.only(left: 5),
                  width: 8, height: 8,
                  decoration: BoxDecoration(shape: BoxShape.circle, color: i == _step ? _accent : _border),
                ))),
                const SizedBox(width: 8),
                IconButton(icon: const Icon(Icons.close, color: _sub), onPressed: () => Navigator.pop(context)),
              ]),
              const SizedBox(height: 20),
              // Body
              Flexible(
                child: SingleChildScrollView(
                  child: switch (_step) {
                    0 => _buildTypeStep(),
                    1 => switch (_rollType) {
                      RollType.identical  => _buildIdenticalStep(),
                      RollType.sequential => _buildSequentialStep(),
                      RollType.lot        => _buildLotStep(),
                      _                   => const SizedBox.shrink(),
                    },
                    _ => _buildPreviewStep(),
                  },
                ),
              ),
              const SizedBox(height: 24),
              // Footer buttons
              Row(children: [
                if (_rollType == RollType.mixed && _step == 0) ...[
                  const Icon(Icons.info_outline, color: _sub, size: 16),
                  const SizedBox(width: 6),
                  const Expanded(child: Text('Use the AI Scanner tab to identify each coin individually.', style: TextStyle(color: _sub, fontSize: 12))),
                ] else const Spacer(),
                TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel', style: TextStyle(color: _sub))),
                const SizedBox(width: 8),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(backgroundColor: _accent, foregroundColor: Colors.white, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)), padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12)),
                  onPressed: _canNext ? () {
                    if (_step == 1) { _buildPreview(); setState(() => _step = 2); }
                    else if (_step == 2) { _commit(); }
                    else { setState(() => _step++); }
                  } : null,
                  child: Text(_step == 2 ? 'Add ${_preview.length} Coins' : 'Next →'),
                ),
              ]),
            ],
          ),
        ),
      ),
    );
  }
}
