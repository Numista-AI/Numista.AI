import 'dart:convert';
import 'dart:js_interop';
import 'package:flutter/foundation.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:web/web.dart' as web;
import 'auth_service.dart';

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

    // Count sets for metadata
    final setCount = coins.where((c) => c['is_set'] == true || c['Denomination'] == 'Set').length;

    final payload = {
      'schemaVersion': 2,
      'exported_at': DateTime.now().toUtc().toIso8601String(),
      'user_email': email,
      'app_version': '4.339',
      'collections': {
        'coins': coins,
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
        'coin_count': coins.length,
        'currency_count': currency.length,
        'world_item_count': worldItems.length,
        'transferred_coin_count': transferredCoins.length,
        'transferred_currency_count': transferredCurrency.length,
        'set_count': setCount,
        'estate_data_count': estateData.length,
        'program_preference_count': programPrefs.length,
      },
      // Legacy compat: flat 'coins' key for schemaVersion: 1 consumers
      'coins': coins,
      'item_count': coins.length,
    };

    return payload;
  }

  /// Triggers JSON file download in browser or web target.
  static Future<void> exportJsonDownload() async {
    final payload = await generateExportPayload();
    final jsonEncoder = JsonEncoder.withIndent('  ', (object) {
      if (object is Timestamp) return object.toDate().toIso8601String();
      if (object is DateTime) return object.toIso8601String();
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

  /// Triggers CSV file download in browser or web target.
  static Future<void> exportCsvDownload() async {
    final payload = await generateExportPayload();
    final List coins = payload['coins'] as List;

    final StringBuffer csv = StringBuffer();
    csv.writeln('Year,Mint Mark,Denomination,Program/Series,Theme/Subject,Condition,Cost,AI Estimated Value,Certification Number,Storage Location,Added');

    for (final c in coins) {
      final map = c as Map<String, dynamic>;
      csv.writeln([
        _cleanCsvCell(map['Year']),
        _cleanCsvCell(map['Mint Mark']),
        _cleanCsvCell(map['Denomination']),
        _cleanCsvCell(map['Program/Series']),
        _cleanCsvCell(map['Theme/Subject']),
        _cleanCsvCell(map['Condition']),
        _cleanCsvCell(map['Cost']),
        _cleanCsvCell(map['AI Estimated Value']),
        _cleanCsvCell(map['Certification Number']),
        _cleanCsvCell(map['Storage Location']),
        _cleanCsvCell(map['Added']),
      ].join(','));
    }

    final filename = 'numista_collection_${DateTime.now().millisecondsSinceEpoch}.csv';

    if (kIsWeb) {
      _triggerWebDownload(csv.toString(), filename, 'text/csv');
    } else {
      debugPrint('[BackupExportService] CSV non-web export length: ${csv.length}');
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


  static String _cleanCsvCell(dynamic val) {
    if (val == null) return '""';
    final str = val.toString().replaceAll('"', '""');
    return '"$str"';
  }

  static void _triggerWebDownload(String content, String filename, String mimeType) {
    try {
      final bytes = utf8.encode(content);
      final blob = web.Blob([bytes.toJS].toJS, web.BlobPropertyBag(type: mimeType));
      final url = web.URL.createObjectURL(blob);
      final anchor = web.HTMLAnchorElement()
        ..href = url
        ..download = filename
        ..style.display = 'none';
      web.document.body?.appendChild(anchor);
      anchor.click();
      web.document.body?.removeChild(anchor);
      // Give browser download manager ample time (5s) to acquire the blob stream
      Future.delayed(const Duration(seconds: 5), () {
        web.URL.revokeObjectURL(url);
      });
    } catch (e) {
      debugPrint('[BackupExportService] Web download error: $e');
      rethrow;
    }
  }
}
