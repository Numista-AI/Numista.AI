import 'package:flutter/material.dart';
import 'package:numista_ai/services/canonical_mint_asset_service.dart';
import 'package:numista_ai/services/coin_image_service.dart';
import 'package:numista_ai/services/coin_picture_picker.dart';
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
  bool _userPhotoFailed = false;
  String? _lastSelSig;

  @override
  void initState() {
    super.initState();
    _checkAndInitFetch();
  }

  @override
  void didUpdateWidget(covariant CollectionCardImage oldWidget) {
    super.didUpdateWidget(oldWidget);
    final newKey = CollectionCardImageRequestKey.fromData(widget.data);
    final nextSig = _selectionSignature(ignoreUserPhotos: false);
    // v2.1 MF-SAG-I5: also refresh when the photo selection changes (cleared/added/changed URL)
    if (newKey != _lastKey || nextSig != _lastSelSig) {
      _userPhotoFailed = false;
      _checkAndInitFetch();
    }
  }

  String _selectionSignature({required bool ignoreUserPhotos}) {
    final sel = CoinPicturePicker.select(
      widget.data,
      ignoreUserPhotos: ignoreUserPhotos,
    );
    if (sel.isUnownedUserUpload) return 'U|unowned';
    if (sel.preferredCardUrl != null) {
      final tag = (sel.hasUserObverse || sel.hasUserReverse) ? 'U' : 'C';
      return '$tag|${sel.preferredCardUrl}';
    }
    return 'R';
  }

  void _checkAndInitFetch() {
    _lastKey = CollectionCardImageRequestKey.fromData(widget.data);
    final sel = CoinPicturePicker.select(
      widget.data,
      ignoreUserPhotos: _userPhotoFailed,
    );
    _lastSelSig = _selectionSignature(ignoreUserPhotos: false);
    if (sel.isUnownedUserUpload || (sel.preferredCardUrl != null && !sel.needsReferenceFetch)) {
      _refFuture = null;
      return;
    }
    if (sel.preferredCardUrl != null && !_userPhotoFailed) {
      _refFuture = null;
      return;
    }
    final fetcher = widget.imageFetcher ?? CoinImageService.fetchReferenceImages;
    _refFuture = fetcher(
      year: _lastKey!.year,
      mint: _lastKey!.mint.isEmpty ? null : _lastKey!.mint,
      denomination: _lastKey!.denomination.isEmpty ? null : _lastKey!.denomination,
      series: _lastKey!.series.isEmpty ? null : _lastKey!.series,
      subject: _lastKey!.subject.isEmpty ? null : _lastKey!.subject,
    );
  }

  void _onUserPhotoError() {
    if (_userPhotoFailed || !mounted) return;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted || _userPhotoFailed) return;
      setState(() {
        _userPhotoFailed = true;
        _checkAndInitFetch();
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    final sel = CoinPicturePicker.select(
      widget.data,
      ignoreUserPhotos: _userPhotoFailed,
    );
    if (sel.isUnownedUserUpload) return _buildPlaceholder();
    if (sel.preferredCardUrl != null) {
      final isUser = sel.hasUserObverse || sel.hasUserReverse;
      return _buildCoinImage(sel.preferredCardUrl!, isUserPhoto: isUser);
    }
    if (_refFuture == null) return _buildPlaceholder();

    return FutureBuilder<CoinImageResult>(
      future: _refFuture,
      builder: (context, snapshot) {
        final refSel = CoinPicturePicker.select(
          widget.data,
          referenceResult: snapshot.data,
          ignoreUserPhotos: _userPhotoFailed,
        );
        final refUrl = refSel.preferredCardUrl ?? '';

        if (refUrl.isNotEmpty && isOwnedStorageUrl(refUrl)) {
          return _buildCoinImage(refUrl, isUserPhoto: false);
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

  Widget _buildCoinImage(String url, {bool isUserPhoto = false}) {
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
          errorBuilder: (_) {
            if (isUserPhoto && !_userPhotoFailed) {
              _onUserPhotoError();
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
