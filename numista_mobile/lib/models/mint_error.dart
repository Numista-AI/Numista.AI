// mint_error.dart
//
// Data model for the Mint Error Library feature.
// Maps to the `mint_errors` Firestore top-level collection.

import 'package:cloud_firestore/cloud_firestore.dart';

// ─── Hotspot — coordinate of the error on the coin image ─────────────────────
class ErrorHotspot {
  final double x;      // 0.0–1.0 normalized x coordinate
  final double y;      // 0.0–1.0 normalized y coordinate
  final double radius; // normalized radius of the pulse circle
  final String label;  // e.g. "Doubling visible on 'LIBERTY'"

  const ErrorHotspot({
    required this.x,
    required this.y,
    required this.radius,
    required this.label,
  });

  factory ErrorHotspot.fromMap(Map<String, dynamic> m) => ErrorHotspot(
        x: (m['x'] as num?)?.toDouble() ?? 0.5,
        y: (m['y'] as num?)?.toDouble() ?? 0.5,
        radius: (m['radius'] as num?)?.toDouble() ?? 0.08,
        label: m['label'] as String? ?? '',
      );

  Map<String, dynamic> toMap() => {
        'x': x,
        'y': y,
        'radius': radius,
        'label': label,
      };
}

// ─── ErrorImage — one image record within an error document ──────────────────
class ErrorImage {
  final String url;
  final String source;           // 'pcgs' | 'heritage' | 'ngc' | 'wikimedia' | 'user' | 'error_ref'
  final String attributionText;
  final String attributionUrl;
  final bool isVerified;
  final ErrorHotspot? hotspot;

  const ErrorImage({
    required this.url,
    required this.source,
    this.attributionText = '',
    this.attributionUrl = '',
    this.isVerified = false,
    this.hotspot,
  });

  factory ErrorImage.fromMap(Map<String, dynamic> m) => ErrorImage(
        url: m['url'] as String? ?? '',
        source: m['source'] as String? ?? '',
        attributionText: m['attributionText'] as String? ?? '',
        attributionUrl: m['attributionUrl'] as String? ?? '',
        isVerified: m['isVerified'] as bool? ?? false,
        hotspot: m['hotspot'] != null
            ? ErrorHotspot.fromMap(m['hotspot'] as Map<String, dynamic>)
            : null,
      );

  Map<String, dynamic> toMap() => {
        'url': url,
        'source': source,
        'attributionText': attributionText,
        'attributionUrl': attributionUrl,
        'isVerified': isVerified,
        'hotspot': hotspot?.toMap(),
      };
}

// ─── MintError — the main model ──────────────────────────────────────────────
class MintError {
  final String id;           // Firestore doc ID / slug
  final String name;         // Full name e.g. "1955 Doubled Die Obverse Lincoln Cent"
  final String shortName;    // e.g. "1955 DDO"
  final String category;     // "Doubled Die" | "Off-Metal" | "Planchet" | "Striking" | "Die" etc.
  final String subcategory;  // "Die Errors" | "Striking Errors" | "Planchet Errors" | "Currency"
  final List<String> denominations;  // ["cent"] | ["quarter", "dollar"]
  final List<int> years;
  final List<String> mintMarks;
  final String designation;         // "FS-101" | "" 
  final int estValueLow;            // in USD (not cents)
  final int estValueHigh;
  final String rarity;              // "Common" | "Uncommon" | "Rare" | "Legendary"
  final String description;
  final String howToSpot;
  final List<String> datasets;      // ["collectible","common","recent","photographed"]
  final List<ErrorImage> images;
  final List<String> relatedCoinIds;
  final List<String> sources;
  final DateTime? dateAdded;
  final DateTime? lastUpdated;
  final bool isPublished;

  const MintError({
    required this.id,
    required this.name,
    required this.shortName,
    required this.category,
    required this.subcategory,
    required this.denominations,
    required this.years,
    required this.mintMarks,
    required this.designation,
    required this.estValueLow,
    required this.estValueHigh,
    required this.rarity,
    required this.description,
    required this.howToSpot,
    required this.datasets,
    required this.images,
    required this.relatedCoinIds,
    required this.sources,
    this.dateAdded,
    this.lastUpdated,
    this.isPublished = true,
  });

  /// The primary display image (first verified, or first in list, or null).
  ErrorImage? get primaryImage {
    if (images.isEmpty) return null;
    return images.firstWhere((img) => img.isVerified, orElse: () => images.first);
  }

  /// Formatted value range string.
  String get valueRange {
    if (estValueLow == 0 && estValueHigh == 0) return 'Value Unknown';
    if (estValueLow == estValueHigh) return '\$${_fmtInt(estValueLow)}';
    return '\$${_fmtInt(estValueLow)}–\$${_fmtInt(estValueHigh)}';
  }

  /// Year display string.
  String get yearDisplay {
    if (years.isEmpty) return 'Various';
    if (years.length == 1) return '${years.first}';
    return '${years.first}–${years.last}';
  }

  String _fmtInt(int v) {
    if (v >= 1000000) return '${(v / 1000000).toStringAsFixed(1)}M';
    if (v >= 1000) return '${(v / 1000).toStringAsFixed(0)}K';
    return '$v';
  }

  factory MintError.fromFirestore(DocumentSnapshot doc) {
    final d = doc.data() as Map<String, dynamic>;
    return MintError(
      id: doc.id,
      name: d['name'] as String? ?? '',
      shortName: d['shortName'] as String? ?? '',
      category: d['category'] as String? ?? '',
      subcategory: d['subcategory'] as String? ?? '',
      denominations: List<String>.from(d['denominations'] ?? []),
      years: List<int>.from((d['years'] ?? []).map((e) => (e as num).toInt())),
      mintMarks: List<String>.from(d['mintMarks'] ?? []),
      designation: d['designation'] as String? ?? '',
      estValueLow: (d['estValueLow'] as num?)?.toInt() ?? 0,
      estValueHigh: (d['estValueHigh'] as num?)?.toInt() ?? 0,
      rarity: d['rarity'] as String? ?? 'Unknown',
      description: d['description'] as String? ?? '',
      howToSpot: d['howToSpot'] as String? ?? '',
      datasets: List<String>.from(d['datasets'] ?? []),
      images: ((d['images'] ?? []) as List)
          .map((e) => ErrorImage.fromMap(e as Map<String, dynamic>))
          .toList(),
      relatedCoinIds: List<String>.from(d['relatedCoinIds'] ?? []),
      sources: List<String>.from(d['sources'] ?? []),
      dateAdded: (d['dateAdded'] as Timestamp?)?.toDate(),
      lastUpdated: (d['lastUpdated'] as Timestamp?)?.toDate(),
      isPublished: d['isPublished'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toFirestore() => {
        'name': name,
        'shortName': shortName,
        'category': category,
        'subcategory': subcategory,
        'denominations': denominations,
        'years': years,
        'mintMarks': mintMarks,
        'designation': designation,
        'estValueLow': estValueLow,
        'estValueHigh': estValueHigh,
        'rarity': rarity,
        'description': description,
        'howToSpot': howToSpot,
        'datasets': datasets,
        'images': images.map((img) => img.toMap()).toList(),
        'relatedCoinIds': relatedCoinIds,
        'sources': sources,
        'dateAdded': FieldValue.serverTimestamp(),
        'lastUpdated': FieldValue.serverTimestamp(),
        'isPublished': isPublished,
      };
}
