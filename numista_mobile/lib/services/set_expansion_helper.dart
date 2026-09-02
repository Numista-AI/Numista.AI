import 'dart:convert';

/// Shared set-expansion and counting helpers for the Dart client.
///
/// Mirrors `scan_service/collection_inventory.py` exactly.
/// Used by home_dashboard, collection_stats_service, morgan_chat_context.

// ---------------------------------------------------------------------------
// Blocklists
// ---------------------------------------------------------------------------
const Set<String> inheritBlocklistYear = {'', 'multiple', 'various', 'n/a'};
const Set<String> inheritBlocklistDenom = {
  '',
  'set',
  'multiple',
  'various',
  'n/a'
};

// ---------------------------------------------------------------------------
// Expansion Result
// ---------------------------------------------------------------------------
class ExpansionResult {
  final List<Map<String, dynamic>> allItems; // parents + children
  final List<Map<String, dynamic>> parentOnly; // parent docs only (for LPT)
  final int totalCoins; // physical coins
  final int totalLots; // parent docs
  final int setCount; // set parents

  const ExpansionResult({
    required this.allItems,
    required this.parentOnly,
    required this.totalCoins,
    required this.totalLots,
    required this.setCount,
  });
}

// ---------------------------------------------------------------------------
// Set-Expansion
// ---------------------------------------------------------------------------

/// Expand Firestore coin document snapshots into a flat inventory list.
///
/// Each [doc] is a `QueryDocumentSnapshot` with `.id` and `.data()`.
/// Returns [ExpansionResult] with counts and two projections.
ExpansionResult expandCollection(
    List<Map<String, dynamic>> docs, List<String> docIds) {
  final List<Map<String, dynamic>> allItems = [];
  int setCount = 0;

  for (int i = 0; i < docs.length; i++) {
    final d = docs[i];
    final docId = docIds[i];

    final rawItemType =
        (d['item_type']?.toString().trim() ?? '').toLowerCase();

    // Detect set: explicit item_type OR presence of set_contents
    List<dynamic> setContentsList = [];
    final rawContents = d['set_contents'];
    if (rawContents is String && rawContents.isNotEmpty) {
      try {
        setContentsList = jsonDecode(rawContents) as List<dynamic>;
      } catch (_) {}
    } else if (rawContents is List) {
      setContentsList = rawContents;
    }

    final isSet = rawItemType == 'set' || setContentsList.isNotEmpty;

    if (isSet) {
      setCount++;
      final setName = _getField(d, ['Theme/Subject', 'theme_subject'],
          defaultVal: 'Unknown Set');

      // Parent row
      allItems.add({
        'coin_id': docId,
        'year': _getField(d, ['Year', 'year']),
        'denomination': _getField(d, ['Denomination', 'denomination']),
        'mint_mark': _getField(d, ['Mint Mark', 'mint_mark']),
        'condition': _getField(d, ['Condition', 'condition']),
        'theme_subject': _getField(d, ['Theme/Subject', 'theme_subject']),
        'program_series': _getField(d, ['Program/Series', 'program_series']),
        'ai_estimated_value': _getField(
            d, ['AI Estimated Value', 'ai_estimated_value'],
            defaultVal: '\$0.00'),
        'cost': _getField(d, ['Cost', 'cost', 'purchase_cost'],
            defaultVal: '\$0.00'),
        'item_type': 'set',
        'from_set': null,
        'from_set_name': null,
        'is_set_parent': true,
      });

      final parentYear = _getField(d, ['Year', 'year']);
      final parentCond = _getField(d, ['Condition', 'condition']);

      for (int idx = 0; idx < setContentsList.length; idx++) {
        final child = setContentsList[idx];
        if (child is! Map) continue;

        var childYear = _getField(child, ['Year', 'year']);
        var childDenom = _getField(child, ['Denomination', 'denomination']);

        // Inherit parent year only if child blank and parent not blocked
        if (childYear.isEmpty &&
            !inheritBlocklistYear.contains(parentYear.toLowerCase())) {
          childYear = parentYear;
        }
        // Never inherit blocked denominations
        if (inheritBlocklistDenom.contains(childDenom.toLowerCase())) {
          childDenom = '';
        }

        // Child item_type (paper/medal/supply preserved)
        var childItemType =
            _getField(child, ['item_type'], defaultVal: 'coin').toLowerCase();
        if ({'set', 'multiple', 'n/a', ''}.contains(childItemType)) {
          childItemType = 'coin';
        }

        allItems.add({
          'coin_id': '${docId}__set_coin_$idx',
          'year': childYear,
          'denomination': childDenom,
          'mint_mark': _getField(child, ['Mint Mark', 'mint_mark']),
          'condition':
              _getField(child, ['Condition', 'condition']).isNotEmpty
                  ? _getField(child, ['Condition', 'condition'])
                  : parentCond,
          'theme_subject':
              _getField(child, ['Theme/Subject', 'theme_subject']),
          'program_series':
              _getField(child, ['Program/Series', 'program_series']),
          'ai_estimated_value': _getField(
              child, ['AI Estimated Value', 'ai_estimated_value'],
              defaultVal: '\$0.00'),
          'cost': _getField(child, ['Cost', 'cost', 'purchase_cost'],
              defaultVal: '\$0.00'),
          'item_type': childItemType,
          'from_set': docId, // parent doc.id — system number
          'from_set_name': setName, // display label
          'is_set_parent': false,
        });
      }
    } else {
      // Regular coin / paper_currency / medal / other
      allItems.add({
        'coin_id': docId,
        'year': _getField(d, ['Year', 'year']),
        'denomination': _getField(d, ['Denomination', 'denomination']),
        'mint_mark': _getField(d, ['Mint Mark', 'mint_mark']),
        'condition': _getField(d, ['Condition', 'condition']),
        'theme_subject': _getField(d, ['Theme/Subject', 'theme_subject']),
        'program_series': _getField(d, ['Program/Series', 'program_series']),
        'ai_estimated_value': _getField(
            d, ['AI Estimated Value', 'ai_estimated_value'],
            defaultVal: '\$0.00'),
        'cost': _getField(d, ['Cost', 'cost', 'purchase_cost'],
            defaultVal: '\$0.00'),
        'item_type': rawItemType.isNotEmpty ? rawItemType : 'coin',
        'from_set': null,
        'from_set_name': null,
        'is_set_parent': false,
      });
    }
  }

  final parentOnly = allItems.where((r) => r['from_set'] == null).toList();
  final totalCoins = allItems.where((r) => isPhysicalCoin(r)).length;
  final totalLots = parentOnly.length;

  return ExpansionResult(
    allItems: allItems,
    parentOnly: parentOnly,
    totalCoins: totalCoins,
    totalLots: totalLots,
    setCount: setCount,
  );
}

// ---------------------------------------------------------------------------
// Counting Rules
// ---------------------------------------------------------------------------

/// True if this row is a set parent (after expansion).
bool isSetParent(Map<String, dynamic> row) {
  final flag = row['is_set_parent'];
  if (flag != null) return flag == true;
  return (row['item_type']?.toString() ?? '').toLowerCase() == 'set';
}

/// True if this row represents a countable physical coin.
bool isPhysicalCoin(Map<String, dynamic> row) {
  final it = (row['item_type']?.toString() ?? 'coin').toLowerCase().trim();
  if (it != 'coin' && it != '') return false;
  return !isSetParent(row);
}

// ---------------------------------------------------------------------------
// Lot Value
// ---------------------------------------------------------------------------

/// Deterministic value for a kept set lot.
///
/// WHILE KEPT: parent > 0 → parent, else sum of children. Never both.
double lotValue(double parentVal, List<double> childrenVals) {
  if (parentVal > 0) return parentVal;
  return childrenVals.where((v) => v > 0).fold(0.0, (a, b) => a + b);
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

String _getField(dynamic d, List<String> keys, {String defaultVal = ''}) {
  if (d is! Map) return defaultVal;
  for (final k in keys) {
    final v = d[k];
    if (v != null && v.toString().trim().isNotEmpty) {
      return v.toString().trim();
    }
  }
  return defaultVal;
}
