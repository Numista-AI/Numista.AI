import 'package:flutter/material.dart';
import 'package:numista_ai/services/canonical_mint_asset_service.dart';
import 'package:numista_ai/services/coin_image_service.dart';
import 'package:numista_ai/utils/collection_image_utils.dart';
import 'package:numista_ai/utils/owned_storage_url.dart';
import 'package:numista_ai/widgets/signed_storage_image.dart';

/// Semantic request key for memoizing reference image fetches.
/// Uses CanonicalMintAssetService.canonicalYear to normalize year representation.
@immutable
class CollectionCardImageRequestKey {
  final String year;
  final String mint;
  final String denomination;
  final String series;
  final String subject;

  const CollectionCardImageRequestKey({
    required this.year,
    required this.mint,
    required this.denomination,
    required this.series,
    required this.subject,
  });

  factory CollectionCardImageRequestKey.fromData(Map<String, dynamic> data) {
    String read(String snakeKey, String legacyKey) {
      final s = data[snakeKey]?.toString();
      if (s != null && s.trim().isNotEmpty && s.trim() != 'None' && s.trim() != 'null') return s.trim();
      final l = data[legacyKey]?.toString();
      if (l != null && l.trim().isNotEmpty && l.trim() != 'None' && l.trim() != 'null') return l.trim();
      return '';
    }

    final canonYear = CanonicalMintAssetService.canonicalYear(data);
    final year = canonYear.isNotEmpty ? canonYear : read('year', 'Year').replaceAll(RegExp(r'\.0$'), '');
    final mint = read('mint_mark', 'Mint Mark');
    final denom = read('denomination', 'Denomination');
    final series = read('program_series', 'Program/Series');
    final subject = read('theme_subject', 'Theme/Subject');

    return CollectionCardImageRequestKey(
      year: year,
      mint: mint,
      denomination: denom,
      series: series,
      subject: subject,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is CollectionCardImageRequestKey &&
          runtimeType == other.runtimeType &&
          year == other.year &&
          mint == other.mint &&
          denomination == other.denomination &&
          series == other.series &&
          subject == other.subject;

  @override
  int get hashCode => Object.hash(year, mint, denomination, series, subject);
}

typedef ImageFetcherFn = Future<CoinImageResult> Function({
  required String year,
  String? mint,
  String? denomination,
  String? series,
  String? subject,
});

/// v2.1: result of the shared precedence decision.
class _Selection {
  final String? url;
  final bool needsReference;
  final String signature;
  const _Selection.image(String this.url, this.signature) : needsReference = false;
  const _Selection.placeholder(this.signature) : url = null, needsReference = false;
  const _Selection.reference(this.signature) : url = null, needsReference = true;
}

/// Production collection card image widget with lifecycle caching, fail-closed
/// storage validation, shipped precedence (`Canonical -> Direct URL -> Reference`),
/// reverse-preference display policy, and MF-V3-3 steal-guard.
class CollectionCardImage extends StatefulWidget {
  final Map<String, dynamic> data;
  final ImageFetcherFn? imageFetcher;
  final WidgetBuilder? emptyPlaceholderBuilder;

  const CollectionCardImage({
    super.key,
    required this.data,
    this.imageFetcher,
    this.emptyPlaceholderBuilder,
  });

  @override
  State<CollectionCardImage> createState() => _CollectionCardImageState();
}

class _CollectionCardImageState extends State<CollectionCardImage> {
  Future<CoinImageResult>? _refFuture;
  CollectionCardImageRequestKey? _lastKey;

  @override
  void initState() {
    super.initState();
    _checkAndInitFetch();
  }

  String? _lastSelSig;

  @override
  void didUpdateWidget(covariant CollectionCardImage oldWidget) {
    super.didUpdateWidget(oldWidget);
    final newKey = CollectionCardImageRequestKey.fromData(widget.data);
    // v2.1 MF-SAG-I5: also refresh when the photo selection changes (cleared/added/changed URL)
    if (newKey != _lastKey || _select().signature != _lastSelSig) {
      _checkAndInitFetch();
    }
  }

  /// v2.1 MF-SAG-I1: ONE precedence decision shared by build() and _checkAndInitFetch().
  _Selection _select() {
    final data = widget.data;
    final rev = extractUserPhoto(data, isObverse: false);
    final obv = extractUserPhoto(data, isObverse: true);
    final userUploaded = CanonicalMintAssetService.hasUserUploadedPhotos(data); // pin :27 (+users%2f patch)

    if (userUploaded) {
      final selected = rev.isNotEmpty ? rev : obv;             // preferred side only
      if (selected.isNotEmpty) {
        if (isOwnedStorageUrl(selected)) return _Selection.image(selected, 'U|$selected');
        return const _Selection.placeholder('U|unowned');       // non-empty unowned URL -> placeholder, never fall through to canonical
      }
      // v2.3 MF-2: Signal-only upload (e.g. scan_source == 'microscope'/'hardware agent'
      // or stored_obv/stored_rev with no extractable http(s) direct URL) -> preserve canonical
      // suppression and fall through to reference fetch (matching shipped :6369-6406).
      return const _Selection.reference('R');
    }

    // Not a confirmed user upload: unowned / non-URL fields are treated as ABSENT.
    final canon = CanonicalMintAssetService.resolveFromMap(data);
    if (canon != null) {
      final c = canon.reverseUrl.isNotEmpty ? canon.reverseUrl : canon.obverseUrl;
      if (c.isNotEmpty && isOwnedStorageUrl(c)) return _Selection.image(c, 'C|$c');
    }
    final ownedRev = (rev.isNotEmpty && isOwnedStorageUrl(rev)) ? rev : '';
    final ownedObv = (obv.isNotEmpty && isOwnedStorageUrl(obv)) ? obv : '';
    final direct = ownedRev.isNotEmpty ? ownedRev : ownedObv;
    if (direct.isNotEmpty) return _Selection.image(direct, 'D|$direct');
    return const _Selection.reference('R');
  }

  void _checkAndInitFetch() {
    _lastKey = CollectionCardImageRequestKey.fromData(widget.data);
    final sel = _select();
    _lastSelSig = sel.signature;
    if (!sel.needsReference) {
      _refFuture = null;
      return;
    }
    // Reference step: same call shape as shipped :6399-6406. v2.1 MF-SAG-I4: NO timeout (shipped has none).
    final fetcher = widget.imageFetcher ?? CoinImageService.fetchReferenceImages;
    _refFuture = fetcher(
      year: _lastKey!.year,
      mint: _lastKey!.mint.isEmpty ? null : _lastKey!.mint,
      denomination: _lastKey!.denomination.isEmpty ? null : _lastKey!.denomination,
      series: _lastKey!.series.isEmpty ? null : _lastKey!.series,
      subject: _lastKey!.subject.isEmpty ? null : _lastKey!.subject,
    );
  }

  @override
  Widget build(BuildContext context) {
    final sel = _select();
    if (sel.url != null) return _buildCoinImage(sel.url!);
    if (!sel.needsReference || _refFuture == null) return _buildPlaceholder();

    return FutureBuilder<CoinImageResult>(
      future: _refFuture,
      builder: (context, snapshot) {
        final ref = snapshot.data;

        // MF-V3-3 Steal-Guard (:6409-6417): When subject is known and reverse is null,
        // show placeholder instead of falling back to generic obverse.
        final refUrl = (ref?.reverseUrl?.isNotEmpty == true)
            ? ref!.reverseUrl!
            : (_lastKey!.subject.isEmpty && ref?.obverseUrl?.isNotEmpty == true)
                ? ref!.obverseUrl!
                : '';

        if (refUrl.isNotEmpty && isOwnedStorageUrl(refUrl)) {
          return _buildCoinImage(refUrl);
        }

        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(
            child: SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: Color(0xFFC9A227),
              ),
            ),
          );
        }

        return _buildPlaceholder();
      },
    );
  }

  Widget _buildPlaceholder() {
    if (widget.emptyPlaceholderBuilder != null) {
      return widget.emptyPlaceholderBuilder!(context);
    }
    return const Center(
      child: Icon(Icons.image_not_supported_outlined, size: 36, color: Color(0xFF8B92B4)),
    );
  }

  Widget _buildCoinImage(String url) {
    return Center(
      child: Container(
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(
              color: const Color(0xFFC9A227).withAlpha(40),
              blurRadius: 14,
              spreadRadius: 1,
            ),
          ],
        ),
        child: SignedStorageImage(
          url: url,
          fit: BoxFit.contain, // Prevents coin edge cropping
          errorBuilder: (_) => _buildPlaceholder(),
          placeholderBuilder: (_) => const Center(
            child: SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: Color(0xFFC9A227),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
