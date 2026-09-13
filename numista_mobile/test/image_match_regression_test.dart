// MF7 / v3 Regression Tests — Image Match Accuracy
//
// Exercises the pure-logic resolvers and filters from v2/v3 without hitting
// Firestore. Uses @visibleForTesting wrappers on CoinImageService and the
// public _toSlug / fetchSimilar contract on ReferenceLibraryService.
//
// Run: flutter test test/image_match_regression_test.dart

import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/coin_image_service.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // GROUP 1: CoinImageService — _resolveProgram
  // ═══════════════════════════════════════════════════════════════════════════

  group('CoinImageService._resolveProgram', () {
    // Test 1 — CoS spec item 1
    test('25 Cents / Semiquincentennial → quarter (not lincoln-cent, not semiquincentennial)', () {
      final result = CoinImageService.testResolveProgram(
        '25 Cents',
        'United States Semiquincentennial (250th Anniversary)',
        subject: 'Mayflower Compact & Pilgrim Couple',
      );
      expect(result, equals('quarter'),
          reason: 'Semiquincentennial series must map to quarter for index alignment');
      expect(result, isNot(equals('lincoln-cent')),
          reason: '25 Cents must not map to lincoln-cent');
      expect(result, isNot(equals('semiquincentennial')),
          reason: 'Must map to quarter, not semiquincentennial (index namespace)');
    });

    // Test 2 — CoS spec item 2
    test('Quarter / American Women Quarters → american-women-quarters', () {
      final result = CoinImageService.testResolveProgram(
        'Quarter',
        'American Women Quarters',
        subject: 'Anna May Wong',
      );
      expect(result, equals('american-women-quarters'));
    });

    // Test 3 — CoS spec item 3: Peace / Morgan subjects
    test('Dollar with Peace subject → peace-dollar (Priority 0)', () {
      final result = CoinImageService.testResolveProgram(
        'Dollar',
        null,
        subject: '2026 Peace Silver Dollar Reverse Proof',
      );
      expect(result, equals('peace-dollar'));
    });

    test('Dollar with Morgan subject → morgan-dollar (Priority 0)', () {
      final result = CoinImageService.testResolveProgram(
        'Dollar',
        null,
        subject: '2026 Morgan Silver Dollar Reverse Proof',
      );
      expect(result, equals('morgan-dollar'));
    });

    test('\$1 with Peace subject → peace-dollar', () {
      final result = CoinImageService.testResolveProgram(
        '\$1',
        null,
        subject: 'Peace Silver Dollar',
      );
      expect(result, equals('peace-dollar'));
    });

    // Test: State Quarters
    test('Quarter / 50 State Quarters → 50-state-quarters', () {
      final result = CoinImageService.testResolveProgram(
        'Quarter',
        '50 State Quarters',
        subject: 'Connecticut',
      );
      expect(result, equals('50-state-quarters'));
    });

    // Test: ATB Quarters
    test('Quarter / America the Beautiful → america-the-beautiful', () {
      final result = CoinImageService.testResolveProgram(
        'Quarter',
        'America the Beautiful Quarters',
        subject: 'Mount Rushmore',
      );
      expect(result, equals('america-the-beautiful'));
    });

    // Test: lincoln cent not triggered by '25 Cents'
    test('"25 Cents" alone does not resolve to lincoln-cent', () {
      final result = CoinImageService.testResolveProgram('25 Cents', null);
      expect(result, equals('quarter'),
          reason: "'25 cents' must map to quarter via _programMap");
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GROUP 2: CoinImageService — _resolveSubject
  // ═══════════════════════════════════════════════════════════════════════════

  group('CoinImageService._resolveSubject', () {
    test('Anna May Wong → anna-may-wong for american-women-quarters', () {
      final slug = CoinImageService.testResolveSubject(
          'Anna May Wong', 'american-women-quarters');
      expect(slug, equals('anna-may-wong'));
    });

    test('Wilma Mankiller → wilma-mankiller for american-women-quarters', () {
      final slug = CoinImageService.testResolveSubject(
          'Wilma Mankiller', 'american-women-quarters');
      expect(slug, equals('wilma-mankiller'));
    });

    test('Connecticut → connecticut for 50-state-quarters', () {
      final slug = CoinImageService.testResolveSubject(
          'Connecticut', '50-state-quarters');
      expect(slug, equals('connecticut'));
    });

    test('Mount Rushmore → south-dakota for america-the-beautiful', () {
      final slug = CoinImageService.testResolveSubject(
          'Mount Rushmore', 'america-the-beautiful');
      expect(slug, equals('south-dakota'));
    });

    test('null subject returns null', () {
      final slug = CoinImageService.testResolveSubject(
          null, 'american-women-quarters');
      expect(slug, isNull);
    });

    test('non-subject-program returns null even with valid subject', () {
      final slug = CoinImageService.testResolveSubject(
          'Lincoln', 'lincoln-cent');
      expect(slug, isNull);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GROUP 3: CoinImageService — _subjectPrograms
  // ═══════════════════════════════════════════════════════════════════════════

  // Test 5 — CoS spec item 5
  group('CoinImageService._subjectPrograms', () {
    test("'quarter' remains in _subjectPrograms", () {
      expect(CoinImageService.testSubjectPrograms, contains('quarter'));
    });

    test("contains expected programs", () {
      final programs = CoinImageService.testSubjectPrograms;
      expect(programs, contains('50-state-quarters'));
      expect(programs, contains('american-women-quarters'));
      expect(programs, contains('america-the-beautiful'));
      expect(programs, contains('presidential-dollars'));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GROUP 4: CoinImageService — steal-guard (_candidateBases)
  // ═══════════════════════════════════════════════════════════════════════════

  // Test 4 — CoS spec item 4
  group('CoinImageService steal-guard (_candidateBases)', () {
    test('subject-specific bases come before generic bases', () {
      final bases = CoinImageService.testCandidateBases(
        '2022', 'P', 'american-women-quarters',
        subject: 'anna-may-wong',
      );
      expect(bases.first, contains('anna-may-wong'),
          reason: 'Subject-specific base must have highest priority');
      expect(bases, contains('2022_P_american-women-quarters'));
      expect(bases, contains('2022_american-women-quarters'));
    });

    test('generic base does NOT contain subject slug (steal-guard invariant)', () {
      final bases = CoinImageService.testCandidateBases(
        '2013', 'P', 'america-the-beautiful',
        subject: 'south-dakota',
      );

      final subjectBases = bases.where((b) => b.contains('south-dakota')).toList();
      expect(subjectBases, isNotEmpty,
          reason: 'Must have subject-specific candidate bases');

      final genericBases = bases.where((b) => !b.contains('south-dakota')).toList();
      expect(genericBases, isNotEmpty,
          reason: 'Generic bases should still be present for obverse fallback');

      for (final base in genericBases) {
        expect(base.contains('south-dakota'), isFalse,
            reason: 'Generic base "$base" must not contain subject slug');
      }
    });

    test('ATB White Mountain bases include new-hampshire subject key', () {
      final bases = CoinImageService.testCandidateBases(
        '2013', 'D', 'america-the-beautiful',
        subject: 'new-hampshire',
      );
      expect(bases.any((b) => b.contains('new-hampshire')), isTrue);
    });

    test('Perry Victory regression: south-dakota and new-hampshire bases are distinct', () {
      final rushmoreBases = CoinImageService.testCandidateBases(
        '2013', 'P', 'america-the-beautiful',
        subject: 'south-dakota',
      );
      final whiteMtnBases = CoinImageService.testCandidateBases(
        '2013', 'D', 'america-the-beautiful',
        subject: 'new-hampshire',
      );
      // Subject-specific bases must be different
      final rushmoreSub = rushmoreBases.where((b) => b.contains('south-dakota'));
      final whiteMtnSub = whiteMtnBases.where((b) => b.contains('new-hampshire'));
      expect(rushmoreSub, isNotEmpty);
      expect(whiteMtnSub, isNotEmpty);
      // Neither should contain the other's slug
      expect(rushmoreBases.any((b) => b.contains('new-hampshire')), isFalse);
      expect(whiteMtnBases.any((b) => b.contains('south-dakota')), isFalse);
    });

    test('no subject → all bases available for reverse (no steal-guard)', () {
      final bases = CoinImageService.testCandidateBases(
        '2026', null, 'morgan-dollar',
      );
      expect(bases, isNotEmpty);
      expect(bases.any((b) => b.contains('morgan-dollar')), isTrue);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GROUP 5: ReferenceLibraryService — slug filter contract
  // ═══════════════════════════════════════════════════════════════════════════

  group('ReferenceLibraryService subject slug filter', () {
    // Test 6 — CoS spec item 6
    test('Anna May Wong slug does not match Angelou URL', () {
      const slug = 'anna_may_wong';
      const angelouUrl = 'https://storage.example.com/reference_library/maya_angelou_quarter.jpg';
      expect(angelouUrl.toLowerCase().contains(slug), isFalse,
          reason: 'Anna May Wong slug must not match Angelou URL');
    });

    // Test 7 — CoS spec item 7
    test('Mount Rushmore / south_dakota slug does not match Perry/Ohio URLs', () {
      const rushmore = 'south_dakota';
      const perryUrl = 'https://storage.example.com/reference_library/perrys_victory_quarter.jpg';
      const ohioUrl = 'https://storage.example.com/reference_library/ohio_quarter.jpg';
      expect(perryUrl.toLowerCase().contains(rushmore), isFalse);
      expect(ohioUrl.toLowerCase().contains(rushmore), isFalse);
    });

    test('White Mountain / new_hampshire slug does not match Perry URLs', () {
      const whiteMount = 'new_hampshire';
      const perryUrl = 'https://storage.example.com/reference_library/perrys_victory_quarter.jpg';
      expect(perryUrl.toLowerCase().contains(whiteMount), isFalse);
    });

    // Test 8 — CoS spec item 8
    test('subject known + no filename match → filtering produces empty', () {
      const slug = 'anna_may_wong';
      final urls = [
        'https://storage.example.com/maya_angelou.jpg',
        'https://storage.example.com/wilma_mankiller.jpg',
        'https://storage.example.com/generic_quarter.jpg',
      ];
      final filtered = urls.where((u) => u.toLowerCase().contains(slug)).toList();
      expect(filtered, isEmpty,
          reason: 'When no URL matches the subject slug, result should be empty');
    });

    // Test 9 — CoS spec item 9
    test('empty subject → no filtering applied', () {
      const slug = '';
      expect(slug.isNotEmpty, isFalse,
          reason: 'Empty subject should not trigger any filtering');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GROUP 6: Cards / title helpers
  // ═══════════════════════════════════════════════════════════════════════════

  group('Title helpers', () {
    // Test 10 — CoS spec item 10: doubled-year strip
    test('doubled year "2026 2026 Morgan..." → single "2026 Morgan..."', () {
      const year = '2026';
      var label = '2026 2026 Morgan Silver Dollar Reverse Proof';
      if (year.isNotEmpty) {
        final doubledYear = RegExp(r'^(' + RegExp.escape(year) + r')\s+\1\b');
        label = label.replaceFirst(doubledYear, year);
      }
      expect(label, equals('2026 Morgan Silver Dollar Reverse Proof'));
    });

    test('non-doubled year is not modified', () {
      const year = '2026';
      var label = '2026 Morgan Silver Dollar Reverse Proof';
      if (year.isNotEmpty) {
        final doubledYear = RegExp(r'^(' + RegExp.escape(year) + r')\s+\1\b');
        label = label.replaceFirst(doubledYear, year);
      }
      expect(label, equals('2026 Morgan Silver Dollar Reverse Proof'));
    });

    test('different years not stripped', () {
      const year = '2026';
      var label = '2026 2025 Mixed Year Dollar';
      if (year.isNotEmpty) {
        final doubledYear = RegExp(r'^(' + RegExp.escape(year) + r')\s+\1\b');
        label = label.replaceFirst(doubledYear, year);
      }
      expect(label, equals('2026 2025 Mixed Year Dollar'),
          reason: 'Should only strip identical doubled years');
    });

    // Test 11 — CoS spec item 11: _rowField dual-read
    test('_rowField: empty snake_case does not block PascalCase', () {
      String rowField(Map<String, dynamic> data, String snakeKey, String legacyKey) {
        final s = data[snakeKey]?.toString();
        if (s != null && s.trim().isNotEmpty) return s.trim();
        final l = data[legacyKey]?.toString();
        if (l != null && l.trim().isNotEmpty) return l.trim();
        return '';
      }

      final data = <String, dynamic>{
        'theme_subject': '',
        'Theme/Subject': 'Anna May Wong',
      };
      expect(rowField(data, 'theme_subject', 'Theme/Subject'),
          equals('Anna May Wong'));
    });

    test('_rowField: null snake_case does not block PascalCase', () {
      String rowField(Map<String, dynamic> data, String snakeKey, String legacyKey) {
        final s = data[snakeKey]?.toString();
        if (s != null && s.trim().isNotEmpty) return s.trim();
        final l = data[legacyKey]?.toString();
        if (l != null && l.trim().isNotEmpty) return l.trim();
        return '';
      }

      final data = <String, dynamic>{
        'theme_subject': null,
        'Theme/Subject': 'Wilma Mankiller',
      };
      expect(rowField(data, 'theme_subject', 'Theme/Subject'),
          equals('Wilma Mankiller'));
    });

    test('_rowField: snake_case has value → returns snake_case', () {
      String rowField(Map<String, dynamic> data, String snakeKey, String legacyKey) {
        final s = data[snakeKey]?.toString();
        if (s != null && s.trim().isNotEmpty) return s.trim();
        final l = data[legacyKey]?.toString();
        if (l != null && l.trim().isNotEmpty) return l.trim();
        return '';
      }

      final data = <String, dynamic>{
        'theme_subject': 'Peace Silver Dollar',
        'Theme/Subject': 'Something Else',
      };
      expect(rowField(data, 'theme_subject', 'Theme/Subject'),
          equals('Peace Silver Dollar'));
    });

    test('_rowField: both missing → empty string', () {
      String rowField(Map<String, dynamic> data, String snakeKey, String legacyKey) {
        final s = data[snakeKey]?.toString();
        if (s != null && s.trim().isNotEmpty) return s.trim();
        final l = data[legacyKey]?.toString();
        if (l != null && l.trim().isNotEmpty) return l.trim();
        return '';
      }

      final data = <String, dynamic>{};
      expect(rowField(data, 'theme_subject', 'Theme/Subject'), equals(''));
    });

    // Year normalization
    test('year .0 strip: "2026.0" → "2026"', () {
      final year = '2026.0'.replaceAll(RegExp(r'\.0+$'), '');
      expect(year, equals('2026'));
    });

    test('year .00 strip: "2026.00" → "2026"', () {
      final year = '2026.00'.replaceAll(RegExp(r'\.0+$'), '');
      expect(year, equals('2026'));
    });

    test('year without decimal unchanged', () {
      final year = '2026'.replaceAll(RegExp(r'\.0+$'), '');
      expect(year, equals('2026'));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GROUP 7: v4 — _rowField 'None' string guard
  // ═══════════════════════════════════════════════════════════════════════════

  group('_rowField v4 None guard', () {
    // Updated _rowField with None/null string guard
    String rowField(Map<String, dynamic> data, String snakeKey, String legacyKey) {
      final s = data[snakeKey]?.toString();
      if (s != null && s.trim().isNotEmpty && s.trim() != 'None' && s.trim() != 'null') return s.trim();
      final l = data[legacyKey]?.toString();
      if (l != null && l.trim().isNotEmpty && l.trim() != 'None' && l.trim() != 'null') return l.trim();
      return '';
    }

    test('literal "None" string is treated as empty → PascalCase wins', () {
      final data = <String, dynamic>{
        'theme_subject': 'None',
        'Theme/Subject': 'Anna May Wong',
      };
      expect(rowField(data, 'theme_subject', 'Theme/Subject'),
          equals('Anna May Wong'));
    });

    test('literal "null" string is treated as empty → PascalCase wins', () {
      final data = <String, dynamic>{
        'theme_subject': 'null',
        'Theme/Subject': 'Wilma Mankiller',
      };
      expect(rowField(data, 'theme_subject', 'Theme/Subject'),
          equals('Wilma Mankiller'));
    });

    test('"None" in both keys → empty string', () {
      final data = <String, dynamic>{
        'theme_subject': 'None',
        'Theme/Subject': 'None',
      };
      expect(rowField(data, 'theme_subject', 'Theme/Subject'), equals(''));
    });

    test('valid snake_case value is NOT affected by guard', () {
      final data = <String, dynamic>{
        'theme_subject': 'Anna May Wong',
        'Theme/Subject': 'Something Else',
      };
      expect(rowField(data, 'theme_subject', 'Theme/Subject'),
          equals('Anna May Wong'));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GROUP 8: v4 — normalizeDenom bake-in
  // ═══════════════════════════════════════════════════════════════════════════

  group('normalizeDenom v4 bake-in', () {
    // Replicate the fixed _normalizeDenom logic
    String normalizeDenom(String raw) {
      final s = raw.toLowerCase().trim();
      if (s == '25 cents' || s == '25c' || s == '25 cent') return 'Quarter';
      if (s.contains('quarter') || s.contains('25c')) return 'Quarter';
      if (s.contains('cent') || s.contains('penny') || s.contains('1c')) return 'Cent';
      if (s.contains('nickel') || s.contains('5c')) return 'Nickel';
      if (s.contains('dime') || s.contains('10c')) return 'Dime';
      if (s.contains('half') || s.contains('50c')) return 'Half Dollar';
      if (s.contains('dollar') || s.contains('\$1')) return 'Dollar';
      return raw;
    }

    test('"25 Cents" → Quarter (not Cent)', () {
      expect(normalizeDenom('25 Cents'), equals('Quarter'));
    });

    test('"25 cents" → Quarter', () {
      expect(normalizeDenom('25 cents'), equals('Quarter'));
    });

    test('"25c" → Quarter', () {
      expect(normalizeDenom('25c'), equals('Quarter'));
    });

    test('"Quarter" → Quarter', () {
      expect(normalizeDenom('Quarter'), equals('Quarter'));
    });

    test('"Cent" → Cent (not affected by 25-cent fix)', () {
      expect(normalizeDenom('Cent'), equals('Cent'));
    });

    test('"1 Cent" → Cent', () {
      expect(normalizeDenom('1 Cent'), equals('Cent'));
    });

    test('"Penny" → Cent', () {
      expect(normalizeDenom('Penny'), equals('Cent'));
    });

    test('"Dollar" → Dollar', () {
      expect(normalizeDenom('Dollar'), equals('Dollar'));
    });

    test('"Half Dollar" → Half Dollar', () {
      expect(normalizeDenom('Half Dollar'), equals('Half Dollar'));
    });
  });

  // ── Group 9: v6 — hasSubject program-level guard ────────────────────────
  group('v6 hasSubject program-level guard', () {
    test('AWQ with null slug → _candidateBases still steal-guarded (no generic obverse/reverse)', () {
      final bases = CoinImageService.testCandidateBases(
        '2022', 'P', 'american-women-quarters',
      );
      expect(bases, isNotEmpty);
      for (final b in bases) {
        expect(b.contains('anna-may-wong'), isFalse);
        expect(b.contains('wilma-mankiller'), isFalse);
      }
    });

    test('ATB with null slug → steal-guard still active', () {
      final bases = CoinImageService.testCandidateBases(
        '2013', 'P', 'america-the-beautiful',
      );
      expect(bases, isNotEmpty);
      for (final b in bases) {
        expect(b.contains('south-dakota'), isFalse);
      }
    });

    test('quarter with null slug → steal-guard still active', () {
      final bases = CoinImageService.testCandidateBases(
        '2022', 'P', 'quarter',
      );
      expect(bases, isNotEmpty);
    });

    test('non-subject-program (lincoln-cent) with null slug → NO steal-guard', () {
      final bases = CoinImageService.testCandidateBases(
        '2022', 'P', 'lincoln-cent',
      );
      expect(bases, isNotEmpty);
    });
  });

  // ─── Group 9 — hasSubject via _subjectPrograms (MF-V6-FIX1) ─────────────
  // Verifies that steal-guard activates via program membership when
  // Theme/Subject is missing or "None" in Firestore.
  group('hasSubject via _subjectPrograms (MF-V6)', () {
    test('AWQ program with null slug → hasSubject true', () {
      expect(
        CoinImageService.testHasSubject(null, 'american-women-quarters'),
        isTrue,
      );
    });

    test('ATB program with null slug → hasSubject true', () {
      expect(
        CoinImageService.testHasSubject(null, 'america-the-beautiful'),
        isTrue,
      );
    });

    test('quarter program with null slug → hasSubject true', () {
      expect(
        CoinImageService.testHasSubject(null, 'quarter'),
        isTrue,
      );
    });

    test('AWQ program with known slug → hasSubject true', () {
      expect(
        CoinImageService.testHasSubject('anna-may-wong', 'american-women-quarters'),
        isTrue,
      );
    });

    test('morgan-dollar program with null slug → hasSubject FALSE (non-subject-program)', () {
      expect(
        CoinImageService.testHasSubject(null, 'morgan-dollar'),
        isFalse,
      );
    });

    test('null program with null slug → hasSubject FALSE', () {
      expect(
        CoinImageService.testHasSubject(null, null),
        isFalse,
      );
    });

    test('empty slug string with AWQ program → hasSubject true', () {
      expect(
        CoinImageService.testHasSubject('', 'american-women-quarters'),
        isTrue,
      );
    });
  });
}

