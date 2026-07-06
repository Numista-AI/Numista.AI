// coin_normalizer_service.dart
//
// Runs silently in the background after login.
// Checks every coin that lacks the _normalized flag and corrects field
// values against official US Mint terminology using Gemini 2.0 Flash.
//
// Corrections made:
//   - Denomination: "5" → "$5", "25" → "$25", etc.
//   - Program/Series: title-cased ("american gold eagle" → "American Gold Eagle")
//   - Theme/Subject: removes values that are conditions, duplicates, or corrupted
//   - Condition: validates against ANA standard (does NOT override PCGS/NGC grades)
//
// Firestore flag: each coin doc gets `_normalized: true` once processed.
// Re-runs: only for coins added/edited after normalization.

import 'dart:convert';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_ai/firebase_ai.dart';
import 'auth_service.dart';

class CoinNormalizerService {
  static const int _batchSize = 8;

  // Prevent re-running in the same browser session (BaseLayout is re-created
  // on sign-in, so without this guard we'd fetch all coins on every login).
  static bool _sessionRan = false;

  /// Call this once per login session (non-blocking).
  /// Runs fully in background — caller does not need to await.
  static void runForUser() {
    if (_sessionRan) return;
    _sessionRan = true;
    _run().catchError((e) {
      // Silently swallow errors — normalization is a best-effort service
      // ignore: avoid_print
      print('[Normalizer] Error: $e');
    });
  }

  static Future<void> _run() async {
    final col = FirebaseFirestore.instance.collection(AuthService.coinsPath);

    // ── Phase 1: Fix combined Year+Mint on ALL coins (no AI, idempotent) ──────
    await _fixYearMintAll(col);

    // ── Phase 2: AI normalization for coins that still need it ─────────────────
    // Only fetch un-normalised coins (avoids reading all 3,700 docs again).
    // Cap at 80 per session so we never make more than 10 Gemini API calls.
    final snap2 = await col
        .where('_normalized', isNotEqualTo: true)
        .limit(80)
        .get();
    final toNormalize = snap2.docs;

    if (toNormalize.isEmpty) {
      // ignore: avoid_print
      print('[Normalizer] All coins already normalized — nothing to do.');
      return;
    }

    // ignore: avoid_print
    print('[Normalizer] Starting AI normalization for ${toNormalize.length} coins...');
    for (int i = 0; i < toNormalize.length; i += _batchSize) {
      final batch = toNormalize.skip(i).take(_batchSize).toList();
      final shouldContinue = await _normalizeBatch(batch, col);
      if (!shouldContinue) {
        // ignore: avoid_print
        print('[Normalizer] Stopped early — will resume on next login.');
        return;
      }
    }
    // ignore: avoid_print
    print('[Normalizer] ✅ Normalization complete.');
  }


  // ── Year+Mint split regex ─────────────────────────────────────────────────
  static final _yearMintRe =
      RegExp(r'^(\d{4}(?:-\d{4})?)\s*([A-WY-Z])$', caseSensitive: false);

  /// Pre-pass: detects combined Year+MintMark values (e.g. "2006D") in ALL
  /// coins and writes them back as separate fields. Runs before AI batching.
  /// Safe to run repeatedly — skips coins where Mint Mark is already set.
  static Future<void> _fixYearMintAll(
    CollectionReference<Map<String, dynamic>> col,
  ) async {
    // Only fetch coins where Mint Mark is empty — avoids reading all 3,700 docs.
    // Coins with a populated Mint Mark are already split.
    final emptyMintSnap = await col.where('Mint Mark', isEqualTo: '').get();
    final nullMintSnap  = await col.where('Mint Mark', isNull: true).get();
    final candidates = [...emptyMintSnap.docs, ...nullMintSnap.docs];
    final toFix = candidates.where((doc) {
      final rawYear = doc.data()['Year']?.toString().trim() ?? '';
      return _yearMintRe.hasMatch(rawYear);
    }).toList();

    if (toFix.isEmpty) {
      // ignore: avoid_print
      print('[Normalizer] Year+Mint: all coins already split.');
      return;
    }
    // ignore: avoid_print
    print('[Normalizer] Splitting Year+Mint on ${toFix.length} coins...');

    const firestoreBatchLimit = 500;
    for (int i = 0; i < toFix.length; i += firestoreBatchLimit) {
      final chunk = toFix.skip(i).take(firestoreBatchLimit);
      final wb = FirebaseFirestore.instance.batch();
      for (final doc in chunk) {
        final rawYear = doc.data()['Year']?.toString().trim() ?? '';
        final m = _yearMintRe.firstMatch(rawYear)!;
        wb.set(col.doc(doc.id), {
          'Year': m.group(1),
          'Mint Mark': m.group(2)!.toUpperCase(),
          // reset _normalized so AI also re-reviews these coins' other fields
          '_normalized': false,
        }, SetOptions(merge: true));
      }
      await wb.commit();
    }
    // ignore: avoid_print
    print('[Normalizer] ✅ Year+Mint split complete.');
  }

  static Future<bool> _normalizeBatch(
    List<QueryDocumentSnapshot<Map<String, dynamic>>> docs,
    CollectionReference<Map<String, dynamic>> col,
  ) async {
    // Build a JSON array of coin data for Gemini
    final coinList = docs.map((doc) {
      final d = doc.data();
      return {
        'id': doc.id,
        'Denomination': d['Denomination'] ?? '',
        'Program/Series': d['Program/Series'] ?? '',
        'Theme/Subject': d['Theme/Subject'] ?? '',
        'Condition': d['Condition'] ?? '',
        'Country': d['Country'] ?? 'USA',
      };
    }).toList();

    final prompt = 'You are a US Mint data quality expert. For each coin in the JSON array below, '
        'return ONLY a JSON array with corrected field values.\n\n'
        'Rules:\n'
        r'1. Denomination: If it is a plain number (e.g. "5", "25", "50"), prepend "$" (e.g. "$5", "$25", "$50").'
        '\n   - Keep as-is if already formatted or is a word ("Half Dollar", "One Dollar").\n'
        r'   - For US Gold Eagles: $5 = 1/10 oz, $10 = 1/4 oz, $25 = 1/2 oz, $50 = 1 oz.'
        '\n2. Program/Series: Apply Title Case using official US Mint names.\n'
        '   - "american gold eagle" → "American Gold Eagle"\n'
        '   - "morgan dollar" → "Morgan Dollar"\n'
        '   - Keep officially lowercased words as-is (e.g. "of", "the").\n'
        '3. Theme/Subject: Remove or clear this field if:\n'
        '   - It contains a grade/condition (e.g. "Gem BU", "MS-65", "Proof").\n'
        '   - It is a partial/corrupted version of Program/Series (e.g. "merican gold eagle Gem BU").\n'
        '   - It duplicates the Program/Series value.\n'
        '   - Leave as-is if it is a genuine design theme (e.g. "Statue of Liberty", "Bald Eagle").\n'
        '4. Condition:\n'
        '   - "Gem BU" or "GEM BU" → keep as "Gem BU" (valid ANA standard).\n'
        '   - Do NOT change certified grades like "MS-70", "PR-70 DCAM", etc.\n'
        '   - Only change obviously non-standard values.\n'
        '5. If a field is already correct, return it unchanged.\n'
        '6. Add "changed": true if ANY field was corrected, otherwise "changed": false.\n\n'
        'Return ONLY valid JSON, no explanations. Format:\n'
        '[{"id":"...","Denomination":"...","Program/Series":"...","Theme/Subject":"...","Condition":"...","changed":true/false},...]\n\n'
        'Coins to normalize:\n'
        '${jsonEncode(coinList)}';

    try {
      final model = FirebaseAI.googleAI().generativeModel(
        model: 'gemini-1.5-flash',
        generationConfig: GenerationConfig(
          responseMimeType: 'application/json',
          temperature: 0.1,
        ),
      );

      final response = await model.generateContent([
        Content.text(prompt),
      ]);

      final rawJson = response.text ?? '';
      if (rawJson.isEmpty) {
        _markAllNormalized(docs, col);
        return true;
      }

      // Strip markdown code fences if present
      final cleaned = rawJson
          .replaceAll('```json', '')
          .replaceAll('```', '')
          .trim();

      final List<dynamic> corrections = jsonDecode(cleaned);

      // Write corrections using set(merge:true) — keys are treated as literal
      // field names (not FieldPath expressions), so 'Program/Series' is safe.
      final writeBatch = FirebaseFirestore.instance.batch();
      for (final correction in corrections) {
        final id = correction['id'] as String?;
        if (id == null) { continue; }

        final changed = correction['changed'] as bool? ?? false;
        final updates = <String, dynamic>{'_normalized': true};
        if (changed) {
          final denom = correction['Denomination'] as String?;
          final series = correction['Program/Series'] as String?;
          final theme = correction['Theme/Subject'] as String?;
          final cond = correction['Condition'] as String?;
          if (denom != null) { updates['Denomination'] = denom; }
          if (series != null) { updates['Program/Series'] = series; }
          if (theme != null) { updates['Theme/Subject'] = theme; }
          if (cond != null) { updates['Condition'] = cond; }
        }
        writeBatch.set(col.doc(id), updates, SetOptions(merge: true));
      }

      await writeBatch.commit();
      return true;  // continue to next batch
    } catch (e) {
      final msg = e.toString();
      if (msg.contains('spending cap') || msg.contains('quota') ||
          msg.contains('RESOURCE_EXHAUSTED') || msg.contains('429')) {
        // Spending cap hit — log once and stop gracefully.
        // Coins remain un-normalized and will be retried when cap resets.
        // ignore: avoid_print
        print('[Normalizer] ⚠️ API spending cap reached — normalization paused until cap resets.');
        return false;  // signal caller to stop
      }
      // For other errors, log and skip this batch (don't halt everything)
      // ignore: avoid_print
      print('[Normalizer] Batch error (skipping): $e');
      return true;  // continue with next batch
    }
  }

  static void _markAllNormalized(
    List<QueryDocumentSnapshot<Map<String, dynamic>>> docs,
    CollectionReference<Map<String, dynamic>> col,
  ) {
    final batch = FirebaseFirestore.instance.batch();
    for (final doc in docs) {
      batch.update(col.doc(doc.id), {'_normalized': true});
    }
    batch.commit();
  }

  /// Call this after a coin is edited to re-enable normalization for that coin.
  static Future<void> resetNormalizationFlag(String coinId) async {
    await FirebaseFirestore.instance
        .collection(AuthService.coinsPath)
        .doc(coinId)
        .update({'_normalized': false});
  }
}
