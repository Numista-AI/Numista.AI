import '../utils/collection_image_utils.dart';
import '../utils/owned_storage_url.dart';
import 'canonical_mint_asset_service.dart';
import 'coin_image_service.dart';

/// Unified image selection result used across Collection Cards, Vault Gallery,
/// and Coin Details screens.
class CoinPictureSelection {
  final String? primaryObverseUrl;
  final String? primaryReverseUrl;
  final String? preferredCardUrl;
  final String preferredSide; // 'obverse' or 'reverse'
  final bool hasUserObverse;
  final bool hasUserReverse;
  final bool needsReferenceFetch;
  final bool isUnownedUserUpload;
  final String? referenceObverseUrl;
  final String? referenceReverseUrl;
  final String? attribution;

  const CoinPictureSelection({
    this.primaryObverseUrl,
    this.primaryReverseUrl,
    this.preferredCardUrl,
    required this.preferredSide,
    this.hasUserObverse = false,
    this.hasUserReverse = false,
    this.needsReferenceFetch = false,
    this.isUnownedUserUpload = false,
    this.referenceObverseUrl,
    this.referenceReverseUrl,
    this.attribution,
  });

  bool get hasAny =>
      (primaryObverseUrl != null && primaryObverseUrl!.isNotEmpty) ||
      (primaryReverseUrl != null && primaryReverseUrl!.isNotEmpty);

  String? get fallbackCardUrl {
    if (preferredSide == 'obverse') {
      if (referenceObverseUrl != null &&
          referenceObverseUrl!.isNotEmpty &&
          isOwnedStorageUrl(referenceObverseUrl)) {
        return referenceObverseUrl;
      }
      if (referenceReverseUrl != null &&
          referenceReverseUrl!.isNotEmpty &&
          isOwnedStorageUrl(referenceReverseUrl)) {
        return referenceReverseUrl;
      }
      return null;
    }
    if (referenceReverseUrl != null &&
        referenceReverseUrl!.isNotEmpty &&
        isOwnedStorageUrl(referenceReverseUrl)) {
      return referenceReverseUrl;
    }
    if (referenceObverseUrl != null &&
        referenceObverseUrl!.isNotEmpty &&
        isOwnedStorageUrl(referenceObverseUrl)) {
      return referenceObverseUrl;
    }
    return null;
  }
}

/// Single shared picture-picker replacing divergent image selection logic
/// across collection cards, vault gallery/inspector, and coin detail screens.
class CoinPicturePicker {
  CoinPicturePicker._();

  static const _obverseKeys = <String>[
    'image_url_obverse',
    'imageUrlObverse',
    'obverse_image_url',
    'obverse_url',
    'imageObverse',
    'image_obverse',
    'obverseUrl',
    'photo_obverse',
  ];

  static const _reverseKeys = <String>[
    'image_url_reverse',
    'imageUrlReverse',
    'reverse_image_url',
    'reverse_url',
    'imageReverse',
    'image_reverse',
    'reverseUrl',
    'photo_reverse',
  ];

  /// Extracts a user-supplied URL, admitting both `extractUserPhoto` HTTP(S)
  /// URLs and owned `gs://` storage URIs (validated via `isOwnedStorageUrl`).
  static String extractUserStorageUrl(
    Map<String, dynamic> data, {
    required bool isObverse,
  }) {
    final direct = extractUserPhoto(data, isObverse: isObverse);
    if (direct.isNotEmpty) return direct;

    final keys = isObverse ? _obverseKeys : _reverseKeys;
    for (final k in keys) {
      final val = data[k];
      if (val == null) continue;
      final s = val.toString().trim();
      if (s.toLowerCase().startsWith('gs://') && isOwnedStorageUrl(s)) {
        return s;
      }
    }
    return '';
  }

  /// Program-aware distinctive side for collection cards.
  ///
  /// - `presidential-dollars`: `obverse` (per-president portrait; shared Liberty reverse)
  /// - `50-state-quarters`, `america-the-beautiful`, `american-women-quarters`,
  ///   `american-innovation`, `native-american-dollar` (2009+): `reverse`
  /// - `2026` Semiquincentennial dimes: defaults to `obverse` (mint-specific)
  ///   unless [prefer2026DimeObverse] is explicitly set to `false`.
  static String distinctiveSide({
    String? program,
    String? year,
    String? denomination,
    bool prefer2026DimeObverse = true,
  }) {
    final p = (program ?? '').trim().toLowerCase();
    final y = (year ?? '').trim().replaceFirst(RegExp(r'\.0+$'), '');
    final d = (denomination ?? '').trim().toLowerCase();

    if (p == 'presidential-dollars') return 'obverse';
    if (p == '50-state-quarters' ||
        p == 'america-the-beautiful' ||
        p == 'american-women-quarters' ||
        p == 'american-innovation') {
      return 'reverse';
    }
    if (p == 'native-american-dollar') {
      final yr = int.tryParse(y);
      if (yr != null && yr >= 2009) return 'reverse';
    }
    if (y == '2026' && (p == 'dime' || d.contains('dime'))) {
      return prefer2026DimeObverse ? 'obverse' : 'reverse';
    }
    return 'reverse';
  }

  static String _readField(
    Map<String, dynamic> data,
    String snakeKey,
    String legacyKey,
  ) {
    final s = data[snakeKey]?.toString();
    if (s != null && s.trim().isNotEmpty && s.trim() != 'None' && s.trim() != 'null') {
      return s.trim();
    }
    final l = data[legacyKey]?.toString();
    if (l != null && l.trim().isNotEmpty && l.trim() != 'None' && l.trim() != 'null') {
      return l.trim();
    }
    return '';
  }

  /// Resolves the best obverse, reverse, and card-preferred image URLs for [data].
  ///
  /// Precedence per side:
  /// 1. Owned user photo (`https://`, `/`, or owned `gs://`)
  /// 2. Canonical Mint Asset (when not suppressed by user upload)
  /// 3. Reference Library (`referenceResult`, if provided)
  ///
  /// When [ignoreUserPhotos] is true (e.g., after a user photo failed to load),
  /// user photos are skipped so canonical/reference fallback is selected cleanly.
  static CoinPictureSelection select(
    Map<String, dynamic> data, {
    CoinImageResult? referenceResult,
    bool ignoreUserPhotos = false,
    bool prefer2026DimeObverse = true,
  }) {
    final year = CanonicalMintAssetService.canonicalYear(data);
    final denom = _readField(data, 'denomination', 'Denomination');
    final series = _readField(data, 'program_series', 'Program/Series');
    final subject = _readField(data, 'theme_subject', 'Theme/Subject');

    final program = CoinImageService.resolveProgram(
      denom.isEmpty ? null : denom,
      series.isEmpty ? null : series,
      subject: subject.isEmpty ? null : subject,
    );
    final prefSide = distinctiveSide(
      program: program,
      year: year,
      denomination: denom,
      prefer2026DimeObverse: prefer2026DimeObverse,
    );

    final rawObv = extractUserStorageUrl(data, isObverse: true);
    final rawRev = extractUserStorageUrl(data, isObverse: false);
    final userUploaded = !ignoreUserPhotos &&
        CanonicalMintAssetService.hasUserUploadedPhotos(data);

    String? userObv;
    String? userRev;
    bool isUnownedUser = false;

    if (userUploaded) {
      final preferredRaw = prefSide == 'obverse' ? rawObv : rawRev;
      if (preferredRaw.isNotEmpty && !isOwnedStorageUrl(preferredRaw)) {
        return CoinPictureSelection(
          preferredSide: prefSide,
          isUnownedUserUpload: true,
          needsReferenceFetch: false,
        );
      }
      if (rawObv.isNotEmpty) {
        if (isOwnedStorageUrl(rawObv)) {
          userObv = rawObv;
        } else {
          isUnownedUser = true;
        }
      }
      if (rawRev.isNotEmpty) {
        if (isOwnedStorageUrl(rawRev)) {
          userRev = rawRev;
        } else {
          isUnownedUser = true;
        }
      }
      if (isUnownedUser && userObv == null && userRev == null) {
        return CoinPictureSelection(
          preferredSide: prefSide,
          isUnownedUserUpload: true,
          needsReferenceFetch: false,
        );
      }
    }

    // Canonical Mint Asset (suppressed if confirmed user upload)
    final canon = userUploaded ? null : CanonicalMintAssetService.resolveFromMap(data);
    final canonObv = (canon != null && canon.obverseUrl.isNotEmpty && isOwnedStorageUrl(canon.obverseUrl))
        ? canon.obverseUrl
        : null;
    final canonRev = (canon != null && canon.reverseUrl.isNotEmpty && isOwnedStorageUrl(canon.reverseUrl))
        ? canon.reverseUrl
        : null;

    // Direct owned URLs when not confirmed userUploaded (legacy/non-user field)
    final directObv = (!ignoreUserPhotos && !userUploaded && rawObv.isNotEmpty && isOwnedStorageUrl(rawObv))
        ? rawObv
        : null;
    final directRev = (!ignoreUserPhotos && !userUploaded && rawRev.isNotEmpty && isOwnedStorageUrl(rawRev))
        ? rawRev
        : null;

    // Reference library URLs
    final refObv = (referenceResult?.obverseUrl != null &&
            referenceResult!.obverseUrl!.isNotEmpty &&
            isOwnedStorageUrl(referenceResult.obverseUrl))
        ? referenceResult.obverseUrl
        : null;
    final refRev = (referenceResult?.reverseUrl != null &&
            referenceResult!.reverseUrl!.isNotEmpty &&
            isOwnedStorageUrl(referenceResult.reverseUrl))
        ? referenceResult.reverseUrl
        : null;

    final finalObv = userObv ?? canonObv ?? directObv ?? refObv;
    final finalRev = userRev ?? canonRev ?? directRev ?? refRev;

    // Card URL based on distinctiveSide — no subject guard blocking obverse!
    String? cardUrl;
    if (prefSide == 'obverse') {
      cardUrl = (finalObv != null && finalObv.isNotEmpty) ? finalObv : finalRev;
    } else {
      cardUrl = (finalRev != null && finalRev.isNotEmpty) ? finalRev : finalObv;
    }

    final needsRef = (finalObv == null || finalRev == null) &&
        !(userObv != null && userRev != null) &&
        !(canonObv != null && canonRev != null);

    return CoinPictureSelection(
      primaryObverseUrl: finalObv,
      primaryReverseUrl: finalRev,
      preferredCardUrl: cardUrl,
      preferredSide: prefSide,
      hasUserObverse: userObv != null,
      hasUserReverse: userRev != null,
      needsReferenceFetch: needsRef,
      isUnownedUserUpload: false,
      referenceObverseUrl: refObv ?? canonObv,
      referenceReverseUrl: refRev ?? canonRev,
      attribution: referenceResult?.attribution ?? (canon != null ? 'U.S. Mint' : null),
    );
  }
}
