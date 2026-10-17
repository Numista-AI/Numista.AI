import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'backup_export_stub.dart'
    if (dart.library.js_interop) 'backup_export_web.dart' as dl_impl;
import 'auth_service.dart';
import 'package:intl/intl.dart';
import '../utils/text_sanitizer.dart';

/// Handles exporting the user's Firestore collection into a schemaVersion: 1 JSON bundle
/// or a companion CSV spreadsheet for legal estate planning and offline backup.
class BackupExportService {
  BackupExportService._();

  /// Generates schemaVersion: 2 full-fidelity JSON export bundle.
  /// Includes coins, currency, world items, transfers, estate, and preferences.
  static Future<Map<String, dynamic>> generateExportPayload() async {
    final user = FirebaseAuth.instance.currentUser;
    final email = user?.email ?? 'guest@numista.ai';
    final fs = FirebaseFirestore.instance;

    // Helper: query a subcollection under the user doc and return list of maps
    Future<List<Map<String, dynamic>>> fetchCollection(String subcollection) async {
      final List<Map<String, dynamic>> results = [];
      try {
        final snap = await fs.doc(AuthService.userDocPath).collection(subcollection).get();
        for (final doc in snap.docs) {
          results.add({'_id': doc.id, ...doc.data()});
        }
      } catch (e) {
        debugPrint('[BackupExportService] Error fetching $subcollection: $e');
      }
      return results;
    }

    // Helper: fetch a single document
    Future<Map<String, dynamic>?> fetchSingleDoc(String subcollection, String docId) async {
      try {
        final docSnap = await fs.doc(AuthService.userDocPath).collection(subcollection).doc(docId).get();
        if (docSnap.exists && docSnap.data() != null) {
          return {'_id': docSnap.id, ...docSnap.data()!};
        }
      } catch (e) {
        debugPrint('[BackupExportService] Error fetching $subcollection/$docId: $e');
      }
      return null;
    }

    if (AuthService.isGuest || user == null) {
      return {
        'schemaVersion': 2,
        'exported_at': DateTime.now().toUtc().toIso8601String(),
        'user_email': email,
        'collections': {'coins': [], 'currency': [], 'world_items': [], 'transferred_coins': [], 'transferred_currency': []},
        'estate': {'profile': null, 'coin_data': []},
        'preferences': {'program_preferences': [], 'beta_checklist': null},
        'metadata': {'coin_count': 0, 'currency_count': 0, 'world_item_count': 0, 'set_count': 0},
      };
    }

    // Fetch all collections in parallel for speed
    final results = await Future.wait([
      fetchCollection('coins'),              // 0
      fetchCollection('currency'),           // 1
      fetchCollection('world_items'),        // 2
      fetchCollection('transferred_coins'),  // 3
      fetchCollection('transferred_currency'), // 4
      fetchCollection('estate_data'),        // 5
      fetchCollection('program_preferences'), // 6
    ]);

    final coins = results[0];
    final currency = results[1];
    final worldItems = results[2];
    final transferredCoins = results[3];
    final transferredCurrency = results[4];
    final estateData = results[5];
    final programPrefs = results[6];

    // Single docs
    final estateProfile = await fetchSingleDoc('estate_profile', 'data');
    final betaChecklist = await fetchSingleDoc('settings', 'beta_checklist');

    // Sanitize coins for export (no .0 integers, uniform $0.00 cost, readable Added date, full fields)
    final sanitizedCoins = coins.map((c) {
      final m = Map<String, dynamic>.from(c);
      final y = m['Year'] ?? m['year'];
      if (y != null) {
        final yNum = (y is num) ? y.toInt() : (double.tryParse(y.toString())?.toInt() ?? int.tryParse(y.toString()));
        if (yNum != null && yNum > 0) {
          m['Year'] = yNum;
          m['year'] = yNum;
        }
      }
      final q = m['Quantity'] ?? m['quantity'] ?? m['qty'];
      final qInt = _formatQuantity(q);
      m['Quantity'] = qInt;
      m['quantity'] = qInt;

      final costVal = m['Cost'] ?? m['cost'] ?? m['purchase_cost'];
      m['Cost'] = _formatCost(costVal);
      m['cost'] = m['Cost'];

      m['Retailer/Website'] = (m['Retailer/Website'] ?? m['Retailer'] ?? m['retailer'] ?? m['Dealer'] ?? m['dealer'] ?? '').toString();
      m['Retailer Invoice #'] = (m['Retailer Invoice #'] ?? m['Invoice #'] ?? m['Invoice'] ?? m['invoice'] ?? '').toString();
      m['Notes'] = (m['Notes'] ?? m['notes'] ?? m['Personal Notes'] ?? '').toString();

      final addedVal = m['Added'] ?? m['timestamp'] ?? m['created_at'];
      m['Added'] = _formatDate(addedVal);

      return m;
    }).toList();

    // Count sets for metadata
    final setCount = sanitizedCoins.where((c) => c['is_set'] == true || c['Denomination'] == 'Set').length;

    final payload = {
      'schemaVersion': 2,
      'exported_at': DateTime.now().toUtc().toIso8601String(),
      'user_email': email,
      'app_version': '4.339',
      'collections': {
        'coins': sanitizedCoins,
        'currency': currency,
        'world_items': worldItems,
        'transferred_coins': transferredCoins,
        'transferred_currency': transferredCurrency,
      },
      'estate': {
        'profile': estateProfile,
        'coin_data': estateData,
      },
      'preferences': {
        'program_preferences': programPrefs,
        'beta_checklist': betaChecklist,
      },
      'metadata': {
        'coin_count': sanitizedCoins.length,
        'currency_count': currency.length,
        'world_item_count': worldItems.length,
        'transferred_coin_count': transferredCoins.length,
        'transferred_currency_count': transferredCurrency.length,
        'set_count': setCount,
        'estate_data_count': estateData.length,
        'program_preference_count': programPrefs.length,
      },
      // Legacy compat: flat 'coins' key for schemaVersion: 1 consumers
      'coins': sanitizedCoins,
      'item_count': sanitizedCoins.length,
    };

    return payload;
  }

  static String _formatDate(dynamic val) {
    if (val == null) return '';
    if (val is Timestamp) return DateFormat('yyyy-MM-dd').format(val.toDate());
    if (val is DateTime) return DateFormat('yyyy-MM-dd').format(val);
    final str = val.toString().trim();
    if (str.isEmpty) return '';
    if (str.contains('Timestamp(seconds=')) {
      final match = RegExp(r'seconds=(\d+)').firstMatch(str);
      if (match != null) {
        final sec = int.tryParse(match.group(1)!) ?? 0;
        return DateFormat('yyyy-MM-dd').format(DateTime.fromMillisecondsSinceEpoch(sec * 1000));
      }
    }
    if (str.contains('T')) {
      final parsed = DateTime.tryParse(str);
      if (parsed != null) return DateFormat('yyyy-MM-dd').format(parsed);
    }
    return str;
  }

  static String _formatYear(dynamic val) {
    if (val == null) return '';
    if (val is num) {
      final intVal = val.toInt();
      return intVal > 0 ? intVal.toString() : '';
    }
    final s = val.toString().trim();
    final parsed = double.tryParse(s)?.toInt() ?? int.tryParse(s);
    if (parsed != null && parsed > 0) return parsed.toString();
    return s.replaceAll(RegExp(r'\.0$'), '');
  }

  static String _formatCost(dynamic val) {
    if (val == null) return '\$0.00';
    if (val is num) {
      return '\$${val.toDouble().toStringAsFixed(2)}';
    }
    final raw = val.toString().replaceAll(r'$', '').replaceAll(',', '').trim();
    final d = double.tryParse(raw);
    if (d == null) return '\$0.00';
    return '\$${d.toStringAsFixed(2)}';
  }

  static int _formatQuantity(dynamic val) {
    if (val == null) return 1;
    if (val is num) {
      final i = val.toInt();
      return i > 0 ? i : 1;
    }
    final s = val.toString().trim();
    final i = int.tryParse(s) ?? double.tryParse(s)?.toInt() ?? 1;
    return i > 0 ? i : 1;
  }

  /// Triggers JSON file download in browser or web target.
  static Future<void> exportJsonDownload() async {
    final payload = await generateExportPayload();
    final jsonEncoder = JsonEncoder.withIndent('  ', (object) {
      if (object is Timestamp) return DateFormat('yyyy-MM-dd').format(object.toDate());
      if (object is DateTime) return DateFormat('yyyy-MM-dd').format(object);
      return object.toString();
    });
    final jsonStr = jsonEncoder.convert(payload);
    final filename = 'numista_collection_backup_${DateTime.now().millisecondsSinceEpoch}.json';

    if (kIsWeb) {
      _triggerWebDownload(jsonStr, filename, 'application/json');
    } else {
      debugPrint('[BackupExportService] Non-web export triggered. Length: ${jsonStr.length}');
    }
  }

  /// Generates the CSV string from an export payload map.
  static String generateCsvStringFromPayload(Map<String, dynamic> payload) {
    final List coins = payload['coins'] as List? ?? [];

    final StringBuffer csv = StringBuffer();
    csv.writeln('Year,Mint Mark,Denomination,Program/Series,Theme/Subject,Condition,Qty,Cost,AI Estimated Value,Certification Number,Retailer,Invoice,Storage Location,Notes,Owner Photo URLs,Added');

    for (final c in coins) {
      final map = c as Map<String, dynamic>;
      csv.writeln([
        _cleanCsvCell(_formatYear(map['Year'] ?? map['year'])),
        _cleanCsvCell(map['Mint Mark'] ?? map['mint_mark']),
        _cleanCsvCell(map['Denomination'] ?? map['denomination']),
        _cleanCsvCell(map['Program/Series'] ?? map['program_series']),
        _cleanCsvCell(map['Theme/Subject'] ?? map['theme_subject']),
        _cleanCsvCell(map['Condition'] ?? map['condition']),
        _cleanCsvCell(_formatQuantity(map['Quantity'] ?? map['quantity'] ?? map['qty'])),
        _cleanCsvCell(_formatCost(map['Cost'] ?? map['cost'] ?? map['purchase_cost'])),
        _cleanCsvCell(map['AI Estimated Value'] ?? map['ai_estimated_value']),
        _cleanCsvCell(map['Certification Number'] ?? map['cert_number']),
        _cleanCsvCell(map['Retailer/Website'] ?? map['Retailer'] ?? map['retailer'] ?? map['Dealer'] ?? map['dealer']),
        _cleanCsvCell(map['Retailer Invoice #'] ?? map['Invoice #'] ?? map['Invoice'] ?? map['invoice']),
        _cleanCsvCell(map['Storage Location'] ?? map['storage_location'] ?? map['Location'] ?? map['location']),
        _cleanCsvCell(map['Notes'] ?? map['notes'] ?? map['Personal Notes']),
        _cleanCsvCell(_extractOwnerPhotoUrls(map)),
        _cleanCsvCell(_formatDate(map['Added'] ?? map['timestamp'] ?? map['created_at'])),
      ].join(','));
    }
    return csv.toString();
  }

  /// Triggers CSV file download in browser or web target.
  static Future<void> exportCsvDownload() async {
    final payload = await generateExportPayload();
    final csvStr = generateCsvStringFromPayload(payload);
    final filename = 'numista_collection_${DateTime.now().millisecondsSinceEpoch}.csv';

    if (kIsWeb) {
      _triggerWebDownload(csvStr, filename, 'text/csv');
    } else {
      debugPrint('[BackupExportService] CSV non-web export length: ${csvStr.length}');
    }
  }

  /// Generates and triggers download of a pre-formatted CSV template containing
  /// the full Numista Golden Schema headers and example rows for Coins, Banknotes, and Medals.
  static Future<void> downloadCsvTemplate() async {
    final StringBuffer csv = StringBuffer();
    // UTF-8 BOM for automatic Excel/Google Sheets encoding recognition
    csv.write('\uFEFF');
    csv.writeln('Category,Year,Mint Mark,Denomination,Program/Series,Theme/Subject,Variety,Condition/Grade,Grading Service,Certification Number,Strike Type,Holder Type,Metal Content,Quantity,Purchase Cost,Purchase Date,Retailer/Dealer,Storage Location,Personal Notes,Country');

    // Example 1: Coin
    csv.writeln('"Coin (Example - Delete Me)","1921","S","Morgan Dollar","Morgan Silver Dollars","Liberty Head","VAM-1A Top 100","MS64","PCGS","43521234","Business","Slab","90% Silver","1","65.00","2024-03-15","GreatCollections","Safe Box A","Toned obverse","USA"');
    // Example 2: Banknote / Paper Money
    csv.writeln('"Banknote (Example - Delete Me)","1934","","\$20 Silver Certificate","US Federal Reserve Notes","Julian-Morgenthau","Fr. 2201-A","EPQ65","PMG","80912345","Regular Issue","Slab","Paper","1","120.00","2024-05-10","Heritage Auctions","Binder 1","Crisp Uncirculated","USA"');
    // Example 3: Medal / Token
    csv.writeln('"Medal (Example - Delete Me)","1969","","Apollo 11 Commemorative Medal","NASA Space Medals","First Moon Landing","Robbins Medal #123","MS67","NGC","60123984","Proof","Slab","Sterling Silver","1","250.00","2024-06-20","Stack\'s Bowers","Display Case","Original capsule","USA"');

    const filename = 'numista_bulk_import_template.csv';

    if (kIsWeb) {
      _triggerWebDownload(csv.toString(), filename, 'text/csv;charset=utf-8;');
    } else {
      debugPrint('[BackupExportService] CSV template non-web download length: ${csv.length}');
    }
  }


  /// Extracts owner photo URLs from a coin/set map as a semicolon-delimited string.
  /// Returns empty string for non-set coins or sets without owner photos.
  static String _extractOwnerPhotoUrls(Map<String, dynamic> map) {
    final photos = map['owner_photos'];
    if (photos == null || photos is! List || photos.isEmpty) return '';
    return photos
        .map((p) => (p is Map ? p['url'] ?? '' : '').toString())
        .where((url) => url.isNotEmpty)
        .join('; ');
  }

  static String cleanCsvCell(dynamic val) {
    if (val == null) return '""';
    var str = TextSanitizer.fixMojibake(val.toString()).replaceAll('"', '""');
    if (str.isNotEmpty && '=+-@\t\r'.contains(str[0])) {
      str = "'$str";
    }
    return '"$str"';
  }

  static String _cleanCsvCell(dynamic val) => cleanCsvCell(val);

  static void _triggerWebDownload(String content, String filename, String mimeType) {
    dl_impl.triggerWebDownload(content, filename, mimeType);
  }
}
