// numista_mobile/lib/models/mint_product_metadata.dart

import 'package:flutter/foundation.dart';

@immutable
class MintProductMetadata {
  final double? productPriceUsd;
  final String? mintScheduleStatus;
  final String? productAvailability;
  final String? releaseDate;
  final String? releaseTimeEt;
  final DateTime? asOfDate;
  final String? sourceUrl;
  final DateTime? retrievedAt;

  const MintProductMetadata({
    this.productPriceUsd,
    this.mintScheduleStatus,
    this.productAvailability,
    this.releaseDate,
    this.releaseTimeEt,
    this.asOfDate,
    this.sourceUrl,
    this.retrievedAt,
  });

  /// Factory constructing metadata from validated catalog / overlay JSON.
  factory MintProductMetadata.fromJson(Map<String, dynamic> json) {
    // Parse price with strict NaN and negative fail-closed checks
    double? price;
    final rawPrice = json['product_price_usd'];
    if (rawPrice is num && !rawPrice.isNaN && !rawPrice.isInfinite && rawPrice >= 0) {
      price = rawPrice.toDouble();
    }

    // Parse and validate ISO-8601 release date (YYYY-MM-DD)
    String? validDate;
    final rawDate = json['release_date']?.toString();
    if (rawDate != null && RegExp(r'^\d{4}-\d{2}-\d{2}$').hasMatch(rawDate)) {
      try {
        DateTime.parse(rawDate);
        validDate = rawDate;
      } catch (_) {
        validDate = null;
      }
    }

    // Parse asOfDate & provenance (v1.7 MF-3)
    DateTime? asOf;
    final rawAsOf = json['mint_product_as_of']?.toString();
    if (rawAsOf != null) {
      asOf = DateTime.tryParse(rawAsOf);
    }
    final sourceUrl = json['source_url']?.toString().trim();
    DateTime? retrievedAt;
    final rawRetrieved = json['retrieved_at']?.toString();
    if (rawRetrieved != null) {
      retrievedAt = DateTime.tryParse(rawRetrieved);
    }

    return MintProductMetadata(
      productPriceUsd: price,
      mintScheduleStatus: json['mint_schedule_status']?.toString(),
      productAvailability: json['product_availability']?.toString(),
      releaseDate: validDate,
      releaseTimeEt: json['release_time_et']?.toString(),
      asOfDate: asOf,
      sourceUrl: (sourceUrl != null && sourceUrl.isNotEmpty) ? sourceUrl : null,
      retrievedAt: retrievedAt,
    );
  }

  /// Serializes metadata to clean JSON map for testing and verification
  Map<String, dynamic> toJson() {
    return {
      if (productPriceUsd != null) 'product_price_usd': productPriceUsd,
      if (mintScheduleStatus != null) 'mint_schedule_status': mintScheduleStatus,
      if (productAvailability != null) 'product_availability': productAvailability,
      if (releaseDate != null) 'release_date': releaseDate,
      if (releaseTimeEt != null) 'release_time_et': releaseTimeEt,
      if (asOfDate != null) 'mint_product_as_of': asOfDate!.toIso8601String(),
      if (sourceUrl != null) 'source_url': sourceUrl,
      if (retrievedAt != null) 'retrieved_at': retrievedAt!.toIso8601String(),
    };
  }

  /// Human-readable factual status copy (v1.7 MF-3: no hardcoded date).
  String get displayStatus {
    switch (mintScheduleStatus) {
      case 'COMING_SOON':
        return 'Scheduled by U.S. Mint';
      case 'ON_SALE':
        if (asOfDate != null) {
          const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
          return 'Available from U.S. Mint (as of ${months[asOfDate!.month - 1]} ${asOfDate!.year})';
        }
        return 'Available from U.S. Mint';
      case 'NOT_AVAILABLE':
      case 'SOLD_OUT':
        return 'No longer offered by U.S. Mint';
      default:
        return '';
    }
  }

  /// Formatted release date (e.g. "Jul 11, 2024").
  String get displayReleaseDate {
    if (releaseDate == null) return '';
    try {
      final dt = DateTime.parse(releaseDate!);
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      return '${months[dt.month - 1]} ${dt.day}, ${dt.year}';
    } catch (_) {
      return '';
    }
  }
}
