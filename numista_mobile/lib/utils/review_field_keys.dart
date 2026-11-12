import 'package:flutter/foundation.dart';

/// Canonical mapping between Review Hub UI controller labels, primary UI keys,
/// and backend/CSV snake_case keys.
class ReviewFieldSpec {
  final String label;
  final List<String> readKeys;
  final List<String> writeKeys;

  const ReviewFieldSpec({
    required this.label,
    required this.readKeys,
    required this.writeKeys,
  });
}

class ReviewFieldKeys {
  ReviewFieldKeys._();

  @visibleForTesting
  static const List<ReviewFieldSpec> kReviewFieldSpecs = [
    ReviewFieldSpec(
      label: 'Year',
      readKeys: ['Year', 'year'],
      writeKeys: ['Year', 'year'],
    ),
    ReviewFieldSpec(
      label: 'Denomination',
      readKeys: ['Denomination', 'denomination'],
      writeKeys: ['Denomination', 'denomination'],
    ),
    ReviewFieldSpec(
      label: 'Mint Mark',
      readKeys: ['Mint Mark', 'mint_mark'],
      writeKeys: ['Mint Mark', 'mint_mark'],
    ),
    ReviewFieldSpec(
      label: 'Country',
      readKeys: ['Country', 'country'],
      writeKeys: ['Country', 'country'],
    ),
    ReviewFieldSpec(
      label: 'Program/Series',
      readKeys: ['Program/Series', 'program_series'],
      writeKeys: ['Program/Series', 'program_series'],
    ),
    ReviewFieldSpec(
      label: 'Theme/Subject',
      readKeys: ['Theme/Subject', 'theme_subject'],
      writeKeys: ['Theme/Subject', 'theme_subject'],
    ),
    ReviewFieldSpec(
      label: 'Variety',
      readKeys: ['Variety', 'variety'],
      writeKeys: ['Variety', 'variety'],
    ),
    ReviewFieldSpec(
      label: 'Condition',
      readKeys: ['Condition', 'condition'],
      writeKeys: ['Condition', 'condition'],
    ),
    ReviewFieldSpec(
      label: 'Strike Type',
      readKeys: ['Strike Type', 'strike_type'],
      writeKeys: ['Strike Type', 'strike_type'],
    ),
    ReviewFieldSpec(
      label: 'Metal Content',
      readKeys: ['Metal Content', 'metal_content'],
      writeKeys: ['Metal Content', 'metal_content'],
    ),
    ReviewFieldSpec(
      label: 'Purchase Cost',
      readKeys: ['Cost', 'Purchase Cost', 'cost', 'purchase_cost', 'cost_basis'],
      writeKeys: ['cost', 'Cost', 'Purchase Cost', 'cost_basis'],
    ),
    ReviewFieldSpec(
      label: 'Fee',
      readKeys: ['allocated_fees', 'shipping_fee', 'Fee', 'fee', 'Allocated Fees'],
      writeKeys: ['allocated_fees', 'shipping_fee'],
    ),
    ReviewFieldSpec(
      label: 'Purchase Date',
      readKeys: ['Purchase Date', 'purchase_date'],
      writeKeys: ['Purchase Date', 'purchase_date'],
    ),
    ReviewFieldSpec(
      label: 'Retailer/Website',
      readKeys: ['Retailer/Website', 'retailer_website', 'retailer'],
      writeKeys: ['Retailer/Website', 'retailer_website'],
    ),
    ReviewFieldSpec(
      label: 'Retailer Invoice #',
      readKeys: ['Retailer Invoice #', 'retailer_invoice_num', 'invoice_number'],
      writeKeys: ['Retailer Invoice #', 'retailer_invoice_num'],
    ),
    ReviewFieldSpec(
      label: 'Retailer Item No.',
      readKeys: ['retailer_item_num', 'item_number', 'Retailer Item No.'],
      // NEVER write 'Retailer Item No.' to Firestore .update() because '.' is
      // interpreted by Firestore as a nested field path separator.
      writeKeys: ['retailer_item_num'],
    ),
    ReviewFieldSpec(
      label: 'Storage Location',
      readKeys: ['Storage Location', 'storage_location'],
      writeKeys: ['Storage Location', 'storage_location'],
    ),
    ReviewFieldSpec(
      label: 'Quantity',
      readKeys: ['Quantity', 'quantity', 'qty'],
      writeKeys: ['Quantity', 'quantity'],
    ),
  ];

  /// Reads the initial formatted string value for each controller from a
  /// Firestore map, checking all alias keys in precedence order.
  /// Returned strings are used directly for both `initialValues` and
  /// `TextEditingController(text: ...)` so they are character-for-character identical.
  static Map<String, String> extractInitialReviewValues(
    Map<String, dynamic> data,
  ) {
    final result = <String, String>{};
    for (final spec in kReviewFieldSpecs) {
      if (spec.label == 'Fee') {
        final rawFeeVal = data['allocated_fees'] ??
            data['Allocated Fees'] ??
            data['shipping_fee'] ??
            data['Fee'] ??
            data['fee'] ??
            0.0;
        final feeNum = (rawFeeVal is num)
            ? rawFeeVal.toDouble()
            : (double.tryParse(rawFeeVal.toString().replaceAll('\$', '').trim()) ?? 0.0);
        result['Fee'] = feeNum > 0 ? feeNum.toStringAsFixed(2) : '';
        continue;
      }

      String resolved = '';
      dynamic rawResolved;
      for (final key in spec.readKeys) {
        final raw = data[key];
        if (raw != null && raw.toString().trim().isNotEmpty) {
          resolved = raw.toString().trim();
          rawResolved = raw;
          break;
        }
      }

      if (spec.label == 'Purchase Cost') {
        if (resolved.isEmpty) {
          result['Purchase Cost'] = '';
          continue;
        }
        final numVal = (rawResolved is num)
            ? rawResolved.toDouble()
            : double.tryParse(resolved.replaceAll(RegExp(r'[\$,\s]'), ''));
        if (numVal != null &&
            numVal == 0.0 &&
            data['Purchase Cost'] == null &&
            data['Cost'] == null) {
          resolved = '';
        }
      } else if (spec.label == 'Country' && resolved.isEmpty) {
        resolved = 'USA';
      } else if (spec.label == 'Quantity' && resolved.isEmpty) {
        resolved = '1';
      }

      result[spec.label] = resolved;
    }
    return result;
  }

  /// Validates dirty numeric fields before saving. Returns null if valid, or a
  /// user-facing error message if any dirty field has an invalid format.
  static String? validateDirtyReviewInputs({
    required Map<String, String> initialValues,
    required Map<String, String> currentValues,
  }) {
    final initCost = (initialValues['Purchase Cost'] ?? '').trim();
    final currCost = (currentValues['Purchase Cost'] ?? '').trim();
    if (currCost != initCost && currCost.isNotEmpty) {
      final cleaned = currCost.replaceAll(RegExp(r'[\$,\s]'), '');
      final parsed = double.tryParse(cleaned);
      if (parsed == null || parsed.isNaN || parsed.isInfinite || parsed < 0) {
        return 'Invalid Purchase Cost. Enter a non-negative number (e.g. 12.50).';
      }
    }

    final initFee = (initialValues['Fee'] ?? '').trim();
    final currFee = (currentValues['Fee'] ?? '').trim();
    if (currFee != initFee && currFee.isNotEmpty) {
      final cleaned = currFee.replaceAll(RegExp(r'[\$,\s]'), '');
      final parsed = double.tryParse(cleaned);
      if (parsed == null || parsed.isNaN || parsed.isInfinite || parsed < 0) {
        return 'Invalid Fee. Enter a non-negative number (e.g. 2.50).';
      }
    }

    final initQty = (initialValues['Quantity'] ?? '1').trim();
    final currQty = (currentValues['Quantity'] ?? '').trim();
    if (currQty != initQty) {
      final parsed = int.tryParse(currQty);
      if (parsed == null || parsed <= 0) {
        return 'Quantity must be a whole number of 1 or more.';
      }
    }

    return null;
  }

  /// Pure diff builder: emits Firestore update keys ONLY for fields whose
  /// trimmed current value differs from the initial snapshot.
  static Map<String, dynamic> buildDirtyReviewQueueUpdates({
    required Map<String, String> initialValues,
    required Map<String, String> currentValues,
  }) {
    final updates = <String, dynamic>{};

    // Pre-check Year + Mint Mark auto-split when Year or Mint Mark was edited.
    // Auto-split applies ONLY when Mint Mark is empty.
    String yearCurr = (currentValues['Year'] ?? '').trim();
    final String yearInit = (initialValues['Year'] ?? '').trim();
    String mintCurr = (currentValues['Mint Mark'] ?? '').trim();
    final String mintInit = (initialValues['Mint Mark'] ?? '').trim();

    bool yearForcedDirty = false;
    bool mintForcedDirty = false;
    if ((yearCurr != yearInit || mintCurr != mintInit) && mintCurr.isEmpty) {
      final match = RegExp(
        r'^(\d{4}(?:-\d{4})?)\s*([A-WY-Z])$',
        caseSensitive: false,
      ).firstMatch(yearCurr);
      if (match != null) {
        yearCurr = match.group(1)!;
        mintCurr = match.group(2)!.toUpperCase();
        yearForcedDirty = true;
        mintForcedDirty = true;
      }
    }

    for (final spec in kReviewFieldSpecs) {
      final initial = (initialValues[spec.label] ?? '').trim();
      String current = (currentValues[spec.label] ?? '').trim();

      if (spec.label == 'Year' && yearForcedDirty) {
        current = yearCurr;
      } else if (spec.label == 'Mint Mark' && mintForcedDirty) {
        current = mintCurr;
      }

      final isDirty = (current != initial) ||
          (spec.label == 'Year' && yearForcedDirty) ||
          (spec.label == 'Mint Mark' && mintForcedDirty);

      if (!isDirty) continue;

      if (spec.label == 'Purchase Cost' || spec.label == 'Fee') {
        if (current.isEmpty) {
          for (final k in spec.writeKeys) {
            updates[k] = 0.0;
          }
        } else {
          final cleaned = current.replaceAll(RegExp(r'[\$,\s]'), '');
          final numVal = double.tryParse(cleaned);
          if (numVal != null && !numVal.isNaN && !numVal.isInfinite && numVal >= 0) {
            for (final k in spec.writeKeys) {
              updates[k] = numVal;
            }
          }
        }
        continue;
      }

      if (spec.label == 'Quantity') {
        final parsed = int.tryParse(current);
        final safeQty = (parsed != null && parsed > 0) ? parsed : 1;
        for (final k in spec.writeKeys) {
          updates[k] = safeQty;
        }
        continue;
      }

      if (spec.label == 'Mint Mark') {
        final upperMint = current.toUpperCase();
        for (final k in spec.writeKeys) {
          updates[k] = upperMint;
        }
        continue;
      }

      for (final k in spec.writeKeys) {
        updates[k] = current;
      }
    }

    return updates;
  }
}
