/// Extracts cleaned direct user photo URL candidate from coin document map.
///
/// MF-I6: Preserves shipped `_cleanUrl` (`my_collection_screen.dart:6360-6365`)
/// semantics so non-URL sentinel values ('N/A', 'pending', 'none', 'null', '—',
/// 'gs://...', or bare filenames like 'IMG_001.jpg') return '' and fall through
/// cleanly to CanonicalMintAssetService / CoinImageService.
///
/// Returns non-empty string ONLY when the field contains an explicit HTTP(S) URL,
/// a same-origin '/' path, or a protocol-relative '//' / '/\' URL candidate
/// (which is then validated fail-closed by `isOwnedStorageUrl`).
///
/// NOTE (v2.3 MF-2): `stored_obv` and `stored_rev` are checked ONLY as user-upload
/// signals in `CanonicalMintAssetService.hasUserUploadedPhotos` (not displayed directly
/// by `extractUserPhoto`, matching shipped `_CollectionCardImage` at
/// `my_collection_screen.dart:6377-6379`).
String extractUserPhoto(Map<String, dynamic> data, {bool isObverse = true}) {
  final keys = isObverse
      ? const <String>[
          'image_url_obverse',
          'imageUrlObverse',
          'obverse_image_url',
          'obverse_url',
          'imageObverse',
          'image_obverse',
          'obverseUrl',
          'photo_obverse',
        ]
      : const <String>[
          'image_url_reverse',
          'imageUrlReverse',
          'reverse_image_url',
          'reverse_url',
          'imageReverse',
          'image_reverse',
          'reverseUrl',
          'photo_reverse',
        ];

  for (final k in keys) {
    final val = data[k];
    if (val != null) {
      final s = val.toString().trim();
      if (s.isEmpty) continue;
      final lower = s.toLowerCase();
      if (lower == 'null' ||
          lower == 'none' ||
          lower == 'n/a' ||
          lower == 'na' ||
          lower == 'pending' ||
          lower == '—' ||
          lower == '-' ||
          lower.startsWith('gs://')) {
        continue;
      }
      // Match shipped _cleanUrl (:6363) + relative/protocol-relative path candidates
      if (lower.startsWith('https://') ||
          lower.startsWith('http://') ||
          s.startsWith('/')) {
        return s;
      }
    }
  }
  return '';
}
