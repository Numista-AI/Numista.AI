import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:cloud_firestore/cloud_firestore.dart';
import 'auth_service.dart';
import '../constants.dart';

/// PCGS Public API import service.
///
/// The PCGS API is protected by Cloudflare and can only be called from
/// a browser context (not server-to-server). This service runs client-side
/// inside the Flutter Web app, which satisfies Cloudflare's browser check.
///
/// API Docs: https://www.pcgs.com/publicapi/documentation
/// Daily Limit: 1,000 calls per account
class PcgsImportService {
  static const _baseUrl    = 'https://api.pcgs.com/publicapi';
  static const _backendUrl = kApiBaseUrl;

  // ─── Token Management ────────────────────────────────────────────────────
  //
  // Priority:
  //   1. Platform token — stored at `config/pcgs` in Firestore by us (admins).
  //      Called from the browser, so Cloudflare passes it through.
  //      Users never see or manage this token.
  //   2. User personal token — stored in `users/{email}` as a fallback for
  //      power users who want their own PCGS quota (1,000 calls/day each).

  static const _platformTokenPath = 'config';
  static const _platformTokenDoc  = 'pcgs';
  static const _platformTokenField = 'bearerToken';

  /// Returns the effective token — platform first, then user's personal token.
  /// Throws if neither is configured.
  static Future<String?> getToken() async {
    // 1. Platform token (shared, invisible to users)
    try {
      final platformDoc = await FirebaseFirestore.instance
          .collection(_platformTokenPath)
          .doc(_platformTokenDoc)
          .get();
      final platformToken = platformDoc.data()?[_platformTokenField] as String?;
      if (platformToken != null && platformToken.isNotEmpty) {
        return platformToken;
      }
    } catch (_) {
      // Firestore rules may deny unauthenticated read; fall through to user token.
    }

    // 2. User's personal token (fallback / power-user override)
    final email = AuthService.userEmail;
    if (email.isEmpty) return null;
    final doc = await FirebaseFirestore.instance
        .collection('users')
        .doc(email)
        .get();
    return doc.data()?['pcgsToken'] as String?;
  }

  /// Returns true if a platform-level token is configured.
  /// Used by the UI to hide the personal-token section when unnecessary.
  static Future<bool> hasPlatformToken() async {
    try {
      final doc = await FirebaseFirestore.instance
          .collection(_platformTokenPath)
          .doc(_platformTokenDoc)
          .get();
      final t = doc.data()?[_platformTokenField] as String?;
      return t != null && t.isNotEmpty;
    } catch (_) {
      return false;
    }
  }

  /// Saves the user's personal PCGS Bearer token to their Firestore profile.
  static Future<void> saveToken(String token) async {
    final email = AuthService.userEmail;
    await FirebaseFirestore.instance
        .collection('users')
        .doc(email)
        .set({'pcgsToken': token.trim()}, SetOptions(merge: true));
  }

  /// [Admin use only] Stores the platform PCGS token in Firestore.
  /// Firestore rules should restrict writes to admin accounts only.
  static Future<void> setPlatformToken(String token) async {
    await FirebaseFirestore.instance
        .collection(_platformTokenPath)
        .doc(_platformTokenDoc)
        .set({_platformTokenField: token.trim()}, SetOptions(merge: true));
  }

  // ─── API Calls ────────────────────────────────────────────────────────────

  /// Fetches coin details from PCGS CoinFacts by PCGS Number and grade.
  ///
  /// [pcgsNo] - The PCGS coin number (e.g., 7132 for 1881-S Morgan Dollar)
  /// [gradeNo] - Sheldon scale grade (e.g., 65 for MS-65)
  /// [plusGrade] - Whether the grade has a plus modifier (e.g., MS-65+)
  static Future<Map<String, dynamic>?> getCoinFactsByGrade({
    required int pcgsNo,
    required int gradeNo,
    bool plusGrade = false,
  }) async {
    final token = await getToken();
    if (token == null) throw Exception('No PCGS token saved. Please enter your token first.');

    final url = Uri.parse(
      '$_baseUrl/coindetail/GetCoinFactsByGrade'
      '?PCGSNo=$pcgsNo&GradeNo=$gradeNo&PlusGrade=$plusGrade',
    );

    final response = await http.get(url, headers: {
      'authorization': 'bearer $token',
      'Accept': 'application/json',
    });

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      if (data is Map && data['IsValidRequest'] == true) {
        return data['CoinDetail'] as Map<String, dynamic>?;
      }
    } else if (response.statusCode == 401) {
      throw Exception('PCGS token expired or invalid. Please generate a new token at pcgs.com/publicapi/documentation');
    }
    return null;
  }

  /// Fetches coin details from PCGS by certification number.
  ///
  /// This is the most useful for graded coin import — the cert number is
  /// printed on the PCGS slab and uniquely identifies a specific graded coin.
  ///
  /// Note: The cert# endpoint wraps results differently than the PCGS# endpoint.
  /// It may return a single `CoinDetail` map OR a `CoinDetails` array with
  /// one entry — this method handles both response shapes.
  static Future<Map<String, dynamic>?> getCoinFactsByCertNo({
    required String certNo,
  }) async {
    // Call our backend proxy — it forwards to PCGS server-side,
    // bypassing Cloudflare's browser-only restriction.
    final url = Uri.parse('$_backendUrl/api/pcgs/cert/$certNo');

    final response = await http.get(url, headers: {'Accept': 'application/json'});

    if (response.statusCode == 200) {
      final data = json.decode(response.body) as Map<String, dynamic>;
      if (data['found'] == true && data['coinDetail'] is Map) {
        return data['coinDetail'] as Map<String, dynamic>;
      }
      return null;  // found=false means cert not in PCGS DB
    } else if (response.statusCode == 401) {
      throw Exception('PCGS token expired. Update bearerToken in Firestore config/pcgs.');
    } else if (response.statusCode == 429) {
      throw Exception('PCGS daily limit reached (1,000 calls/day). Try again tomorrow.');
    }
    throw Exception('PCGS lookup failed (HTTP ${response.statusCode}): ${response.body.substring(0, response.body.length.clamp(0, 200))}');
  }

  /// Fetches recent auction prices for a coin by PCGS Number.
  static Future<List<Map<String, dynamic>>> getAuctionPrices({
    required int pcgsNo,
    required int gradeNo,
  }) async {
    final token = await getToken();
    if (token == null) throw Exception('No PCGS token saved.');

    final url = Uri.parse(
      '$_baseUrl/auctionprices/CoinFacts/AuctionPricesRealized'
      '?PCGSNo=$pcgsNo&GradeNo=$gradeNo',
    );

    final response = await http.get(url, headers: {
      'authorization': 'bearer $token',
      'Accept': 'application/json',
    });

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      if (data is List) {
        return data.cast<Map<String, dynamic>>();
      }
    }
    return [];
  }

  // ─── Schema Mapping ───────────────────────────────────────────────────────

  /// Converts a PCGS CoinFacts API response into the Numista.AI Firestore schema.
  ///
  /// PCGS field → Our Firestore field:
  ///   Designation       → 'Program/Series'
  ///   Year              → 'Year'
  ///   MintMark          → 'Mint Mark'
  ///   Denomination      → 'Denomination'
  ///   GradeString       → 'Condition'
  ///   PCGSNo            → 'PCGS Number'
  ///   CertNo            → 'Certification Number'
  ///   GradingService    → 'Grading Service' (always PCGS for this import)
  ///   ImageObverse      → 'image_url_obverse'
  ///   ImageReverse      → 'image_url_reverse'
  ///   PriceGuideValue   → 'AI Estimated Value'
  static Map<String, dynamic> mapToFirestoreSchema(
    Map<String, dynamic> pcgsData, {
    String? certNo,
    String? grade,
  }) {
    // The real PCGS API response has flat fields directly on the object:
    //   Name, Grade, Year, MintMark, Denomination, PCGSNo, etc.
    // (The old shape had Designation + GradeString from a different endpoint.)
    final coinName    = pcgsData['Name']?.toString()
        ?? pcgsData['CoinName']?.toString()
        ?? '';
    final designation = pcgsData['Designation']?.toString()
        ?? pcgsData['MajorVariety']?.toString()
        ?? '';
    final year        = pcgsData['Year']?.toString() ?? '';
    final mintMark    = pcgsData['MintMark']?.toString() ?? '';
    // Grade field from API is the full grade string e.g. "PR70DCAM"
    final gradeStr    = grade
        ?? pcgsData['Grade']?.toString()
        ?? pcgsData['GradeString']?.toString()
        ?? '';
    final pcgsNo      = pcgsData['PCGSNo']?.toString() ?? '';
    final priceGuide  = pcgsData['PriceGuideValue'];
    final isNFC       = pcgsData['IsNFCSecure'] as bool? ?? false;
    final population  = pcgsData['Population']?.toString() ?? '';
    final metalContent = pcgsData['MetalContent']?.toString() ?? '';
    final dieVariety  = pcgsData['DieVariety']?.toString() ?? '';
    final seriesName  = pcgsData['SeriesName']?.toString() ?? '';

    // Denomination: use the raw field if available, else parse from name
    String denomination = pcgsData['Denomination']?.toString()
        ?? _parseDenomination(coinName.isNotEmpty ? coinName : designation);

    return {
      'Year':                     year,
      'Mint Mark':                mintMark,
      'Denomination':             denomination,
      'Program/Series':           coinName.isNotEmpty ? coinName : designation,
      'Condition':                gradeStr,
      'PCGS Number':              pcgsNo,
      'Certification Number':     certNo ?? pcgsData['CertNo']?.toString() ?? '',
      'Grading Service':          'PCGS',
      'Holder Type':              'PCGS Slab',
      'image_url_obverse':        pcgsData['ObverseImageURL']?.toString() ?? '',
      'image_url_reverse':        pcgsData['ReverseImageURL']?.toString() ?? '',
      'AI Estimated Value':       priceGuide != null && priceGuide != 0 ? '\$$priceGuide' : '',
      'Country':                  pcgsData['Country']?.toString() ?? 'United States',
      'Metal Content':            metalContent,
      'Die Variety':              dieVariety,
      'Series Name':              seriesName,
      'Population':               population,
      'Is Silver':                _isSilverSeries(coinName.isNotEmpty ? coinName : designation),
      'Is NFC Secure':            isNFC,
      'Original Description from source': 'Imported via PCGS API',
      'source': 'pcgs_api',
      'importedAt': FieldValue.serverTimestamp(),
    };
  }

  // ─── Batch Import: List of Cert Numbers ──────────────────────────────────

  /// Imports a list of PCGS certification numbers into the user's collection.
  ///
  /// Returns a [PcgsImportResult] with counts of successes, failures, and
  /// the list of any failed cert numbers for retry.
  static Future<PcgsImportResult> importByCertNumbers({
    required List<String> certNumbers,
    void Function(int done, int total)? onProgress,
  }) async {
    final db = FirebaseFirestore.instance;
    final coinsPath = AuthService.coinsPath;

    int success = 0;
    int failed = 0;
    final List<String> failedCerts = [];
    final List<String> duplicateCerts = [];

    for (int i = 0; i < certNumbers.length; i++) {
      final cert = certNumbers[i].trim();
      if (cert.isEmpty) continue;

      onProgress?.call(i + 1, certNumbers.length);

      try {
        // Check for existing coin with this cert number
        final existing = await db
            .collection(coinsPath)
            .where('Certification Number', isEqualTo: cert)
            .limit(1)
            .get();

        if (existing.docs.isNotEmpty) {
          duplicateCerts.add(cert);
          continue;
        }

        final coinData = await getCoinFactsByCertNo(certNo: cert);
        if (coinData == null) {
          failedCerts.add(cert);
          failed++;
          continue;
        }

        final firestoreData = mapToFirestoreSchema(coinData, certNo: cert);
        await db.collection(coinsPath).add(firestoreData);
        success++;

        // Respect the 1,000/day rate limit — small delay between calls
        await Future.delayed(const Duration(milliseconds: 200));
      } catch (e) {
        failedCerts.add(cert);
        failed++;
      }
    }

    return PcgsImportResult(
      successCount: success,
      failedCount: failed,
      duplicateCount: duplicateCerts.length,
      failedCerts: failedCerts,
      duplicateCerts: duplicateCerts,
    );
  }

  // ─── CSV Import ───────────────────────────────────────────────────────────

  /// Parses a PCGS registry CSV export into a list of cert numbers.
  ///
  /// PCGS CSV columns typically include: Cert#, PCGS#, Designation, Grade, etc.
  ///
  /// Uses a quoted-field-aware CSV tokenizer so coin names that contain
  /// commas (e.g. "Morgan Dollar, 1881-S") don't corrupt column alignment.
  static List<String> parseCertNumbersFromCsv(String csvContent) {
    final lines = csvContent.split('\n');
    if (lines.isEmpty) return [];

    // Find the cert number column index from the header row
    final headers = _splitCsvRow(lines.first)
        .map((h) => h.trim().toLowerCase())
        .toList();

    final certIndex = headers.indexWhere(
      (h) => h.contains('cert') || h.contains('certification'),
    );

    if (certIndex < 0) return [];

    return lines
        .skip(1)
        .where((line) => line.trim().isNotEmpty)
        .map((line) {
          final cols = _splitCsvRow(line);
          if (certIndex < cols.length) {
            return cols[certIndex].trim();
          }
          return '';
        })
        .where((cert) => cert.isNotEmpty && RegExp(r'^\d+$').hasMatch(cert))
        .toList();
  }

  /// RFC-4180-compliant CSV row tokenizer.
  ///
  /// Handles quoted fields (including fields containing commas and escaped
  /// double-quotes). This is required for PCGS exports where the Designation
  /// column often contains commas (e.g. `"Morgan Dollar, 1880-S"`).
  static List<String> _splitCsvRow(String row) {
    final fields = <String>[];
    final buffer = StringBuffer();
    bool inQuotes = false;

    for (int i = 0; i < row.length; i++) {
      final ch = row[i];
      if (ch == '"') {
        if (inQuotes && i + 1 < row.length && row[i + 1] == '"') {
          // Escaped quote inside a quoted field ("")
          buffer.write('"');
          i++; // skip the second quote
        } else {
          inQuotes = !inQuotes;
        }
      } else if (ch == ',' && !inQuotes) {
        fields.add(buffer.toString());
        buffer.clear();
      } else {
        buffer.write(ch);
      }
    }
    fields.add(buffer.toString()); // last field
    return fields;
  }

  // ─── Private helpers ──────────────────────────────────────────────────────

  static String _parseDenomination(String designation) {
    final d = designation.toLowerCase();
    if (d.contains('cent') || d.contains('penny')) return 'Cent';
    if (d.contains('nickel') || d.contains('5 cent')) return 'Nickel';
    if (d.contains('dime') || d.contains('10 cent')) return 'Dime';
    if (d.contains('quarter') || d.contains('25 cent')) return 'Quarter Dollar';
    if (d.contains('half dollar') || d.contains('50 cent')) return 'Half Dollar';
    if (d.contains('dollar')) return 'Dollar';
    if (d.contains('eagle') && d.contains('quarter')) return 'Quarter Eagle (\$2.50)';
    if (d.contains('half eagle')) return 'Half Eagle (\$5)';
    if (d.contains('eagle') && !d.contains('double') && !d.contains('quarter') && !d.contains('half')) return 'Eagle (\$10)';
    if (d.contains('double eagle')) return 'Double Eagle (\$20)';
    return 'Unknown';
  }

  static bool _isSilverSeries(String designation) {
    final d = designation.toLowerCase();
    return d.contains('morgan') ||
        d.contains('peace') ||
        d.contains('walking liberty') ||
        d.contains('barber') ||
        d.contains('seated liberty') ||
        d.contains('franklin') ||
        d.contains('kennedy half') ||
        (d.contains('dime') && !d.contains('roosevelt')) ||
        d.contains('trade dollar') ||
        d.contains('bust');
  }
}

// ─── Result Model ─────────────────────────────────────────────────────────────

class PcgsImportResult {
  final int successCount;
  final int failedCount;
  final int duplicateCount;
  final List<String> failedCerts;
  final List<String> duplicateCerts;

  const PcgsImportResult({
    required this.successCount,
    required this.failedCount,
    required this.duplicateCount,
    required this.failedCerts,
    required this.duplicateCerts,
  });

  int get totalProcessed => successCount + failedCount + duplicateCount;

  @override
  String toString() =>
      'PcgsImportResult(✅ $successCount added, ❌ $failedCount failed, ⟳ $duplicateCount duplicates skipped)';
}
