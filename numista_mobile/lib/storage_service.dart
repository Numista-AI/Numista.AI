import 'dart:io';
import 'package:flutter/foundation.dart'; // required for debugPrint
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_storage/firebase_storage.dart';

class StorageService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  // Firebase Storage bucket — must match firebase_options.dart storageBucket exactly
  final FirebaseStorage _storage = FirebaseStorage.instanceFor(
      bucket: 'studio-9101802118-8c9a8.firebasestorage.app');

  // ─── LOCAL PATH ────────────────────────────────────────────────────────────
  // Using a raw string so backslashes and the apostrophe are taken literally.
  // dart:io Directory() handles this fine on Windows.
  static const String capturesPath =
      r"C:\Users\ericd\Documents\MyVertexProject\AJ's AI Coin Collection app\captures";

  Future<void> syncLocalCaptures() async {
    debugPrint('═══════════════════════════════════════════════');
    debugPrint('[SYNC] Scholar\'s Slug Engine: STARTING');
    debugPrint('[SYNC] Scanning path: $capturesPath');

    // ── 1. Privacy guard ──────────────────────────────────────────────────
    const String userEmail = 'eric@numista.ai';
    final String storageBucketPath = 'users/$userEmail/';
    debugPrint('[SYNC] Privacy guard OK → user: $userEmail');

    // ── 2. Locate local captures directory ───────────────────────────────
    final directory = Directory(capturesPath);
    final bool dirExists = await directory.exists();
    debugPrint('[SYNC] Directory exists: $dirExists');

    if (!dirExists) {
      debugPrint('[SYNC] ❌ ABORT — captures directory NOT found.');
      debugPrint('[SYNC] Expected: $capturesPath');
      return;
    }

    // ── 3. List files — use path.split('\\').last, NOT uri.pathSegments ──
    // uri.pathSegments URL-encodes the apostrophe in "AJ's" → %27, which
    // breaks every string comparison. We use File.path.split() instead.
    final List<File> localFiles = directory
        .listSync()
        .whereType<File>()
        .where((f) => f.path.toLowerCase().endsWith('.jpg'))
        .toList();

    debugPrint('[SYNC] .jpg files found: ${localFiles.length}');
    for (var f in localFiles) {
      // Safe name extraction — no URI encoding
      final name = f.path.split(r'\').last;
      debugPrint('[SYNC]   📷 $name');
    }

    if (localFiles.isEmpty) {
      debugPrint('[SYNC] ⚠️  No .jpg files in the captures folder. Nothing to do.');
      return;
    }

    // ── 4. Spot-check for Washington / 2007 ──────────────────────────────
    final bool hasWashington = localFiles
        .any((f) => f.path.split(r'\').last.toLowerCase().contains('washington'));
    final bool has2007 = localFiles
        .any((f) => f.path.split(r'\').last.contains('2007'));
    debugPrint('[SYNC] Washington match found: $hasWashington');
    debugPrint('[SYNC] 2007 match found: $has2007');

    // ── 5. Fetch Firestore coins ──────────────────────────────────────────
    debugPrint('[SYNC] Fetching Firestore coins for $userEmail ...');
    final QuerySnapshot coinsSnapshot =
        await _firestore.collection('users/$userEmail/coins').get();
    debugPrint('[SYNC] Coins fetched: ${coinsSnapshot.docs.length}');

    int uploadCount = 0;
    int skipCount = 0;

    for (var doc in coinsSnapshot.docs) {
      final data = doc.data() as Map<String, dynamic>;

      // ── Safe field extraction ─────────────────────────────────────────────
      // Firestore stores spreadsheet numbers as doubles (e.g. 2007 → 2007.0).
      // _toCleanString() converts 2007.0 → "2007" and strips NaN/null.
      final String year     = _toCleanString(data['Year']);
      final String denom    = _toCleanString(data['Denomination']);
      final String mintMark = _toCleanString(data['Mint Mark']);
      final String theme    = _toCleanString(
          data['Theme/Subject'] ?? data['Theme / Subject']);

      debugPrint('[SYNC] Doc "${doc.id}" → year="$year" denom="$denom" theme="$theme"');

      // Skip only if we have NO usable identifiers at all
      if (denom.isEmpty && theme.isEmpty) {
        debugPrint('[SYNC]   ↳ SKIP (no denom or theme to match on)');
        continue;
      }

      // Normalise raw numeric denominations from spreadsheet imports
      // e.g. "1" → "Dollar" (Presidential / Sacagawea dollar coins)
      // The filename always spells out "Dollar" so we need the word form.
      final String effectiveDenom = _normaliseDenom(denom);

      for (var file in localFiles) {
        // ✅ Safe name — no URL encoding
        final String fileName = file.path.split(r'\').last;
        final String lowerFile = fileName.toLowerCase();

        // Determine side from filename first — only process labelled sides
        String side = 'Unknown';
        if (lowerFile.contains('obverse')) {
          side = 'Obverse';
        } else if (lowerFile.contains('reverse')) {
          side = 'Reverse';
        } else {
          continue;
        }

        // Skip if Firestore already has this URL
        final String fieldName = 'image_url_${side.toLowerCase()}';
        if ((data[fieldName]?.toString() ?? '').isNotEmpty) {
          skipCount++;
          debugPrint('[SYNC]   ↳ SKIP $side (already synced)');
          continue;
        }

        // ─── MATCH LOGIC ────────────────────────────────────────────────────
        // Path A: year present in Firestore → year must appear in filename
        // Path B: year absent in Firestore  → match purely on theme/denom keywords
        final bool yearInFile = year.isNotEmpty && fileName.contains(year);
        final bool yearMissing = year.isEmpty;

        if (!yearInFile && !yearMissing) {
          // Year present in DB but not in this filename → wrong coin
          continue;
        }

        // Theme/denom fuzzy match
        final bool themeMatch =
            _containsApproximate(fileName, theme, effectiveDenom);

        if (yearMissing && !themeMatch) {
          // No year anchor AND theme fails → genuinely wrong coin, skip
          debugPrint('[SYNC]   ↳ SKIP $side (no year in DB, theme also failed)');
          continue;
        }

        if (!yearMissing && !themeMatch) {
          // Year matched but theme failed → log warning, force override
          debugPrint('[SYNC] ⚠️  YEAR MATCH (year=$year) but theme FAILED:');
          debugPrint('[SYNC]    File:  $fileName');
          debugPrint('[SYNC]    Theme: "$theme"  Denom: "$effectiveDenom"');
          debugPrint('[SYNC]    → YEAR-ONLY OVERRIDE — forcing match.');
        } else {
          debugPrint('[SYNC] ✅ MATCH ($side) → "$fileName"');
        }

        // ── Build Scholar's Slug name ──────────────────────────────────
        // Format: [Year]_[Mint]_[Denom]_[Theme-Subject]_[Side].jpg
        // Strip parentheses and special chars cleanly before slugifying.
        String cleanTheme = theme
            .replaceAll(RegExp(r'[()\/]'), ' ')  // remove parens, slashes
            .replaceAll(RegExp(r'\s+'), ' ')       // collapse spaces
            .trim()
            .replaceAll(' ', '-');

        String cleanDenom = denom
            .replaceAll(RegExp(r'[()\/\s]+'), '-')
            .replaceAll(RegExp(r'-+'), '-');

        final String slugMint = mintMark.isEmpty ? 'NoMint' : mintMark;

        // Final sanitise — only alphanumeric, dash, underscore, dot
        String optimizedName =
            '${year}_${slugMint}_${cleanDenom}_${cleanTheme}_$side.jpg';
        optimizedName =
            optimizedName.replaceAll(RegExp(r'[^a-zA-Z0-9_\-\.]'), '_');

        debugPrint('[SYNC] ✅ MATCH — uploading as: $optimizedName');

        try {
          final Reference ref =
              _storage.ref().child('$storageBucketPath$optimizedName');

          await ref.putFile(file);
          final String downloadUrl = await ref.getDownloadURL();

          await doc.reference.update({fieldName: downloadUrl});

          debugPrint('[SYNC] ☁️  Upload OK → $downloadUrl');
          uploadCount++;
        } catch (e, stack) {
          debugPrint('[SYNC] ❌ Upload FAILED for $optimizedName');
          debugPrint('[SYNC] Error: $e');
          debugPrint('[SYNC] Stack: $stack');
        }
      }
    }

    debugPrint('═══════════════════════════════════════════════');
    debugPrint('[SYNC] DONE — Uploaded: $uploadCount | Skipped (already synced): $skipCount');
    debugPrint('═══════════════════════════════════════════════');
  }

  // ── Fuzzy matcher ──────────────────────────────────────────────────────────
  // Returns true only if the theme keywords match the filename. 
  // If no theme keywords are found, falls back to denomination.
  bool _containsApproximate(String fileName, String theme, String denom) {
    final String lowerFile = fileName.toLowerCase();

    // ── Theme Matching ──────────────────────────────────────────────────
    final List<String> themeKeywords = theme
        .replaceAll(RegExp(r'\(.*?\)'), '') // strip parentheticals
        .split(RegExp(r'[\s/\-_,;:]+')) 
        .map((t) => t.replaceAll(RegExp(r'[^a-zA-Z0-9]'), ''))
        .where((t) => t.length >= 3)
        .toList();

    bool themeMatchFound = false;
    if (themeKeywords.isNotEmpty) {
      for (final keyword in themeKeywords) {
        if (lowerFile.contains(keyword.toLowerCase())) {
          debugPrint('[SYNC]   ✓ Theme hit: "$keyword"');
          themeMatchFound = true;
          break;
        }
      }
    }

    // If we have a theme match, we're done. 
    if (themeMatchFound) return true;

    // If the Firestore record HAS a theme (like "Madison") but it didn't
    // match the filename (which is "Washington"), we must FAIL here.
    // We cannot fall back to Denom ("Dollar") or we'd match every president.
    if (themeKeywords.isNotEmpty) {
      debugPrint('[SYNC]   ✗ Theme provided but NO match found.');
      return false;
    }

    // ── Denomination Fallback ──────────────────────────────────────────
    // Only used if the Firestore record has no descriptive Theme/Subject.
    final List<String> denomKeywords = denom
        .replaceAll(RegExp(r'\(.*?\)'), '')
        .split(RegExp(r'[\s/\-_,;:]+'))
        .map((t) => t.replaceAll(RegExp(r'[^a-zA-Z0-9]'), ''))
        .where((t) => t.length >= 4)
        .toList();

    for (final dw in denomKeywords) {
      if (lowerFile.contains(dw.toLowerCase())) {
        debugPrint('[SYNC]   ✓ Denom fallback hit: "$dw"');
        return true;
      }
    }

    return false;
  }

  // ── _normaliseDenom ───────────────────────────────────────────────────────
  // Convert raw spreadsheet denomination values to matchable word forms.
  // Firestore may store "1" (the number) for any dollar coin, or "$0.25" etc.
  String _normaliseDenom(String denom) {
    switch (denom.trim()) {
      case '1': return 'Dollar';
      case '0.5':
      case '\$0.50':
      case '0.50':  return 'HalfDollar';
      case '0.25':
      case '\$0.25': return 'Quarter';
      case '0.10':
      case '\$0.10': return 'Dime';
      case '0.05':
      case '\$0.05': return 'Nickel';
      case '0.01':
      case '\$0.01': return 'Penny';
      default:       return denom; // Already a word (e.g. "Dollar", "Dime")
    }
  }

  // ── _toCleanString ────────────────────────────────────────────────────────
  // Safely converts any Firestore field value to a trimmed string.
  // KEY FIX: spreadsheet imports store years as doubles (2007 → 2007.0).
  // We detect numeric types and convert via .toInt() to get "2007" not "2007.0".
  String _toCleanString(dynamic value) {
    if (value == null) return '';
    String result;
    if (value is double) {
      // 2007.0 → 2007 (integer string, no decimal)
      result = value.toInt().toString();
    } else if (value is int) {
      result = value.toString();
    } else {
      result = value.toString().trim();
    }
    // Treat spreadsheet NaN / "null" / "nan" as empty
    final lower = result.toLowerCase();
    if (lower == 'nan' || lower == 'null' || result.isEmpty) return '';
    return result;
  }
}
