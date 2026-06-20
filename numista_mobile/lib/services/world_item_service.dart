// world_item_service.dart
//
// Handles all network and Firestore operations for World & Specialty Items.
//
// Responsibilities:
//   1. POST /api/identify-world-item  — sends image + hints to backend,
//      returns GeminiIdentification + optional NumistaMatch list.
//   2. saveWorldItem()                — writes a WorldItem document to
//      Firestore at users/{uid}/world_items/{id}.
//   3. worldItemsStream()             — real-time stream of all world items
//      for the current user.
//   4. deleteWorldItem()              — removes a world item by Firestore ID.

import 'dart:convert';
import 'dart:typed_data';

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/foundation.dart' show debugPrint;
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

import '../constants.dart';
import 'auth_service.dart';

// ── Data Models ───────────────────────────────────────────────────────────────

/// Categories a user can choose when adding a world/specialty item.
enum WorldItemType {
  foreignCoin,
  foreignBanknote,
  bullion,
  specialtyCollectible,
  unknown;

  String get displayLabel {
    switch (this) {
      case WorldItemType.foreignCoin:
        return 'Foreign / World Coin';
      case WorldItemType.foreignBanknote:
        return 'Foreign Currency / Banknote';
      case WorldItemType.bullion:
        return 'Bullion';
      case WorldItemType.specialtyCollectible:
        return 'Specialty Collectible';
      case WorldItemType.unknown:
        return 'Unknown — Let AI Try';
    }
  }

  String get emoji {
    switch (this) {
      case WorldItemType.foreignCoin:
        return '🌍';
      case WorldItemType.foreignBanknote:
        return '💵';
      case WorldItemType.bullion:
        return '🪙';
      case WorldItemType.specialtyCollectible:
        return '🏛️';
      case WorldItemType.unknown:
        return '❓';
    }
  }

  /// Maps to the hint string expected by the backend.
  String get backendHint {
    switch (this) {
      case WorldItemType.foreignCoin:
        return 'coin';
      case WorldItemType.foreignBanknote:
        return 'banknote';
      case WorldItemType.bullion:
        return 'bullion';
      case WorldItemType.specialtyCollectible:
        return 'collectible';
      case WorldItemType.unknown:
        return 'unknown';
    }
  }
}

/// The AI identification returned by Gemini (via the backend).
class GeminiIdentification {
  final String identification;
  final String itemType;
  final String country;
  final String era;
  final String? denomination;
  final String? material;
  final List<String> designKeywords;
  final double confidence;
  final String? confidenceNotes;

  const GeminiIdentification({
    required this.identification,
    required this.itemType,
    required this.country,
    required this.era,
    this.denomination,
    this.material,
    required this.designKeywords,
    required this.confidence,
    this.confidenceNotes,
  });

  factory GeminiIdentification.fromJson(Map<String, dynamic> j) {
    return GeminiIdentification(
      identification:  j['identification'] as String? ?? 'This appears to be an unidentified item.',
      itemType:        j['item_type'] as String? ?? 'unknown',
      country:         j['country'] as String? ?? 'Unknown',
      era:             j['era'] as String? ?? 'Unknown',
      denomination:    j['denomination'] as String?,
      material:        j['material'] as String?,
      designKeywords:  (j['design_keywords'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      confidence:      (j['confidence'] as num?)?.toDouble() ?? 0.5,
      confidenceNotes: j['confidence_notes'] as String?,
    );
  }

  /// Confidence level category for UI display.
  ConfidenceLevel get level {
    if (confidence >= 0.90) return ConfidenceLevel.high;
    if (confidence >= 0.75) return ConfidenceLevel.medium;
    return ConfidenceLevel.low;
  }

  String get confidencePercent => '${(confidence * 100).round()}%';
}

enum ConfidenceLevel { high, medium, low }

/// A single Numista catalogue match returned by the backend.
class NumistaMatch {
  final String? numistaId;
  final String? title;
  final String? issuer;
  final int? minYear;
  final int? maxYear;
  final String? composition;
  final String? imageObverse;
  final String? catalogueUrl;

  const NumistaMatch({
    this.numistaId,
    this.title,
    this.issuer,
    this.minYear,
    this.maxYear,
    this.composition,
    this.imageObverse,
    this.catalogueUrl,
  });

  factory NumistaMatch.fromJson(Map<String, dynamic> j) {
    return NumistaMatch(
      numistaId:    j['numista_id']?.toString(),
      title:        j['title'] as String?,
      issuer:       j['issuer'] as String?,
      minYear:      j['min_year'] as int?,
      maxYear:      j['max_year'] as int?,
      composition:  j['composition'] as String?,
      imageObverse: j['image_obverse'] as String?,
      catalogueUrl: j['catalogue_url'] as String?,
    );
  }

  String get yearRange {
    if (minYear != null && maxYear != null && minYear != maxYear) {
      return '$minYear–$maxYear';
    }
    return minYear?.toString() ?? maxYear?.toString() ?? '';
  }
}

/// Full response from POST /api/identify-world-item.
class WorldItemIdentification {
  final GeminiIdentification gemini;
  final List<NumistaMatch> numistaMatches;
  final bool showDisclaimer;
  final String? disclaimerReason;

  const WorldItemIdentification({
    required this.gemini,
    required this.numistaMatches,
    required this.showDisclaimer,
    this.disclaimerReason,
  });

  factory WorldItemIdentification.fromJson(Map<String, dynamic> j) {
    return WorldItemIdentification(
      gemini:         GeminiIdentification.fromJson(j['gemini'] as Map<String, dynamic>),
      numistaMatches: (j['numista_matches'] as List<dynamic>?)
              ?.map((m) => NumistaMatch.fromJson(m as Map<String, dynamic>))
              .toList() ??
          [],
      showDisclaimer:   j['show_disclaimer'] as bool? ?? true,
      disclaimerReason: j['disclaimer_reason'] as String?,
    );
  }
}

/// The complete data model for a saved world/specialty item.
class WorldItem {
  final String? id;  // Firestore doc ID (null before save)

  // Type
  final WorldItemType itemCategory;

  // AI identification
  final String aiIdentification;
  final double aiConfidence;
  final bool aiConfidenceFlagged;

  // Numista catalogue (nullable — only set when user confirms a match)
  final String? numistaId;
  final String? numistaTitle;
  final bool numistaConfirmedByUser;
  final String? numistaCatalogueUrl;

  // User-entered fields
  final String name;
  final String country;
  final String era;
  final String denomination;
  final String material;
  final String condition;
  final double? purchasePrice;
  final DateTime? datePurchased;
  final String purchasedFrom;
  final double? estimatedValue;
  final String storageLocation;
  final String notes;

  // Bullion-specific (all null for non-bullion items)
  final double? bullionWeightOz;
  final double? bullionPurity;
  final String? bullionMetal;
  final double? spotValueAtEntry;

  // Images (GCS URLs)
  final String? imageObverse;
  final String? imageReverse;

  // Metadata
  final DateTime? createdAt;

  const WorldItem({
    this.id,
    required this.itemCategory,
    this.aiIdentification = '',
    this.aiConfidence = 0.0,
    this.aiConfidenceFlagged = false,
    this.numistaId,
    this.numistaTitle,
    this.numistaConfirmedByUser = false,
    this.numistaCatalogueUrl,
    this.name = '',
    this.country = '',
    this.era = '',
    this.denomination = '',
    this.material = '',
    this.condition = '',
    this.purchasePrice,
    this.datePurchased,
    this.purchasedFrom = '',
    this.estimatedValue,
    this.storageLocation = '',
    this.notes = '',
    this.bullionWeightOz,
    this.bullionPurity,
    this.bullionMetal,
    this.spotValueAtEntry,
    this.imageObverse,
    this.imageReverse,
    this.createdAt,
  });

  Map<String, dynamic> toFirestore() {
    return {
      'item_type':               itemCategory.backendHint,
      'category':                itemCategory.displayLabel,
      'ai_identification':       aiIdentification,
      'ai_confidence':           aiConfidence,
      'ai_confidence_flagged':   aiConfidenceFlagged,
      'numista_id':              numistaId,
      'numista_title':           numistaTitle,
      'numista_confirmed_by_user': numistaConfirmedByUser,
      'numista_catalogue_url':   numistaCatalogueUrl,
      'name':                    name,
      'country':                 country,
      'era':                     era,
      'denomination':            denomination,
      'material':                material,
      'condition':               condition,
      'purchase_price':          purchasePrice,
      'date_purchased':          datePurchased != null
          ? Timestamp.fromDate(datePurchased!)
          : null,
      'purchased_from':          purchasedFrom,
      'estimated_value':         estimatedValue,
      'storage_location':        storageLocation,
      'notes':                   notes,
      'bullion_weight_oz':       bullionWeightOz,
      'bullion_purity':          bullionPurity,
      'bullion_metal':           bullionMetal,
      'spot_value_at_entry':     spotValueAtEntry,
      'image_obverse':           imageObverse,
      'image_reverse':           imageReverse,
      'created_at':              FieldValue.serverTimestamp(),
      'source':                  'world_item_manual',
    };
  }

  factory WorldItem.fromFirestore(DocumentSnapshot<Map<String, dynamic>> doc) {
    final d = doc.data()!;
    WorldItemType cat;
    switch (d['item_type'] as String? ?? 'unknown') {
      case 'coin':
        cat = WorldItemType.foreignCoin;
        break;
      case 'banknote':
        cat = WorldItemType.foreignBanknote;
        break;
      case 'bullion':
        cat = WorldItemType.bullion;
        break;
      case 'collectible':
        cat = WorldItemType.specialtyCollectible;
        break;
      default:
        cat = WorldItemType.unknown;
    }
    return WorldItem(
      id:                       doc.id,
      itemCategory:             cat,
      aiIdentification:         d['ai_identification'] as String? ?? '',
      aiConfidence:             (d['ai_confidence'] as num?)?.toDouble() ?? 0.0,
      aiConfidenceFlagged:      d['ai_confidence_flagged'] as bool? ?? false,
      numistaId:                d['numista_id'] as String?,
      numistaTitle:             d['numista_title'] as String?,
      numistaConfirmedByUser:   d['numista_confirmed_by_user'] as bool? ?? false,
      numistaCatalogueUrl:      d['numista_catalogue_url'] as String?,
      name:                     d['name'] as String? ?? '',
      country:                  d['country'] as String? ?? '',
      era:                      d['era'] as String? ?? '',
      denomination:             d['denomination'] as String? ?? '',
      material:                 d['material'] as String? ?? '',
      condition:                d['condition'] as String? ?? '',
      purchasePrice:            (d['purchase_price'] as num?)?.toDouble(),
      datePurchased:            (d['date_purchased'] as Timestamp?)?.toDate(),
      purchasedFrom:            d['purchased_from'] as String? ?? '',
      estimatedValue:           (d['estimated_value'] as num?)?.toDouble(),
      storageLocation:          d['storage_location'] as String? ?? '',
      notes:                    d['notes'] as String? ?? '',
      bullionWeightOz:          (d['bullion_weight_oz'] as num?)?.toDouble(),
      bullionPurity:            (d['bullion_purity'] as num?)?.toDouble(),
      bullionMetal:             d['bullion_metal'] as String?,
      spotValueAtEntry:         (d['spot_value_at_entry'] as num?)?.toDouble(),
      imageObverse:             d['image_obverse'] as String?,
      imageReverse:             d['image_reverse'] as String?,
      createdAt:                (d['created_at'] as Timestamp?)?.toDate(),
    );
  }
}

// ── Service ───────────────────────────────────────────────────────────────────

class WorldItemService {
  static const String _endpoint = '$kApiBaseUrl/api/identify-world-item';

  // ── Firestore path ──────────────────────────────────────────────────────────
  static CollectionReference<Map<String, dynamic>> get _col =>
      FirebaseFirestore.instance
          .doc(AuthService.coinsPath.replaceAll('/coins', ''))
          .collection('world_items');

  // ── AI Identification ───────────────────────────────────────────────────────

  /// Calls the backend to identify a world/specialty item.
  ///
  /// [imageBytes] — raw bytes of the uploaded image (null for text-only).
  /// [imageFileName] — original filename, used to determine MIME type.
  /// [countryHint], [yearHint], [itemTypeHint], [notesHint] — optional text hints.
  static Future<WorldItemIdentification?> identify({
    Uint8List? imageBytes,
    String imageFileName = 'photo.jpg',
    String countryHint = '',
    String yearHint = '',
    WorldItemType itemTypeHint = WorldItemType.unknown,
    String notesHint = '',
  }) async {
    try {
      final request = http.MultipartRequest('POST', Uri.parse(_endpoint));

      if (imageBytes != null) {
        final ext  = imageFileName.split('.').last.toLowerCase();
        final mime = {
          'png':  'image/png',
          'gif':  'image/gif',
          'webp': 'image/webp',
        }[ext] ?? 'image/jpeg';

        request.files.add(http.MultipartFile.fromBytes(
          'image',
          imageBytes,
          filename: imageFileName,
          contentType: MediaType.parse(mime),
        ));
      }

      request.fields['country_hint']   = countryHint;
      request.fields['year_hint']      = yearHint;
      request.fields['item_type_hint'] = itemTypeHint.backendHint;
      request.fields['notes_hint']     = notesHint;

      final streamedResp = await request.send().timeout(
        const Duration(seconds: 60),
      );
      final body = await streamedResp.stream.bytesToString();

      if (streamedResp.statusCode == 200) {
        final json = jsonDecode(body) as Map<String, dynamic>;
        return WorldItemIdentification.fromJson(json);
      } else {
        debugPrint('[WorldItemService] identify failed ${streamedResp.statusCode}: $body');
        return null;
      }
    } catch (e) {
      debugPrint('[WorldItemService] identify error: $e');
      return null;
    }
  }

  // ── Firestore CRUD ──────────────────────────────────────────────────────────

  /// Saves a WorldItem to Firestore. Returns the new document ID.
  static Future<String?> save(WorldItem item) async {
    try {
      final ref = await _col.add(item.toFirestore());
      return ref.id;
    } catch (e) {
      debugPrint('[WorldItemService] save error: $e');
      return null;
    }
  }

  /// Updates an existing WorldItem in Firestore.
  static Future<bool> update(String docId, Map<String, dynamic> fields) async {
    try {
      await _col.doc(docId).update({...fields, 'updated_at': FieldValue.serverTimestamp()});
      return true;
    } catch (e) {
      debugPrint('[WorldItemService] update error: $e');
      return false;
    }
  }

  /// Deletes a WorldItem by Firestore document ID.
  static Future<bool> delete(String docId) async {
    try {
      await _col.doc(docId).delete();
      return true;
    } catch (e) {
      debugPrint('[WorldItemService] delete error: $e');
      return false;
    }
  }

  /// Real-time stream of all world items for the current user,
  /// ordered newest first.
  static Stream<List<WorldItem>> worldItemsStream() {
    return _col
        .orderBy('created_at', descending: true)
        .snapshots()
        .map((snap) => snap.docs
            .map((doc) => WorldItem.fromFirestore(doc))
            .toList());
  }

  /// Fetches live spot prices from the backend's existing endpoint.
  /// Returns a map like {'Gold': 3200.0, 'Silver': 34.5, ...}
  static Future<Map<String, double>> fetchSpotPrices() async {
    try {
      final resp = await http
          .get(Uri.parse('$kApiBaseUrl/api/spot_prices'))
          .timeout(const Duration(seconds: 10));
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body) as Map<String, dynamic>;
        return {
          'Gold':      (data['Gold']      ?? 0).toDouble(),
          'Silver':    (data['Silver']    ?? 0).toDouble(),
          'Platinum':  (data['Platinum']  ?? 0).toDouble(),
          'Palladium': (data['Palladium'] ?? 0).toDouble(),
        };
      }
    } catch (e) {
      debugPrint('[WorldItemService] fetchSpotPrices error: $e');
    }
    // Fallback values
    return {'Gold': 3200.0, 'Silver': 34.0, 'Platinum': 1000.0, 'Palladium': 950.0};
  }

  /// Calculates melt value for a bullion item.
  /// [weightOz] — troy ounces. [purity] — e.g. 0.999 for .999 fine.
  /// [metal]    — 'Gold' | 'Silver' | 'Platinum' | 'Palladium'.
  static double? computeBullionMeltValue({
    required double weightOz,
    required double purity,
    required String metal,
    required Map<String, double> spotPrices,
  }) {
    final spot = spotPrices[metal];
    if (spot == null || spot <= 0) return null;
    return weightOz * purity * spot;
  }
}
