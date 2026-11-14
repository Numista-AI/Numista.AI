import 'package:flutter/material.dart';
import '../services/signed_photo_url_service.dart';

/// Renders either a public HTTPS image URL directly or a private `gs://` /
/// `/users/...` storage URL resolved via [SignedPhotoUrlService.resolve].
/// Never calls `resolve()` inside `build()`; performs at most one cache
/// invalidation + re-resolve if a signed URL expires while mounted.
class SignedStorageImage extends StatefulWidget {
  final String? url;
  final BoxFit fit;
  final double? width;
  final double? height;
  final Key? imageKey;
  final WidgetBuilder? placeholderBuilder;
  final WidgetBuilder? errorBuilder;
  final Future<String?> Function(String? url)? resolver;

  const SignedStorageImage({
    super.key,
    required this.url,
    this.fit = BoxFit.cover,
    this.width,
    this.height,
    this.imageKey,
    this.placeholderBuilder,
    this.errorBuilder,
    this.resolver,
  });

  @override
  State<SignedStorageImage> createState() => _SignedStorageImageState();
}

class _SignedStorageImageState extends State<SignedStorageImage> {
  Future<String?>? _resolveFuture;
  bool _retriedAfterExpiry = false;
  bool _retryScheduled = false;
  String _lastUrl = '';

  @override
  void initState() {
    super.initState();
    _initForUrl(widget.url);
  }

  @override
  void didUpdateWidget(covariant SignedStorageImage oldWidget) {
    super.didUpdateWidget(oldWidget);
    final nextTrimmed = (widget.url ?? '').trim();
    if (nextTrimmed != _lastUrl) {
      _initForUrl(widget.url);
    }
  }

  void _initForUrl(String? rawUrl) {
    final trimmed = (rawUrl ?? '').trim();
    _lastUrl = trimmed;
    _retriedAfterExpiry = false;
    _retryScheduled = false;
    if (trimmed.isEmpty || !SignedPhotoUrlService.needsSigning(trimmed)) {
      _resolveFuture = null;
      return;
    }
    final resolveFn = widget.resolver ?? SignedPhotoUrlService.resolve;
    _resolveFuture = resolveFn(trimmed);
  }

  void _retryAfterExpiry() {
    if (_retriedAfterExpiry || _lastUrl.isEmpty || !mounted) return;
    debugPrint('[SignedStorageImage] Invalidating expired signed URL and retrying once.');
    SignedPhotoUrlService.invalidate(_lastUrl);
    final resolveFn = widget.resolver ?? SignedPhotoUrlService.resolve;
    setState(() {
      _retriedAfterExpiry = true;
      _retryScheduled = false;
      _resolveFuture = resolveFn(_lastUrl);
    });
  }

  @override
  void dispose() {
    // SignedPhotoUrlService.resolve returns a shared coalesced batch Future
    // with no per-widget cancellation; `mounted` guards all post-await setState calls.
    super.dispose();
  }

  Widget _buildPlaceholder(BuildContext context) =>
      widget.placeholderBuilder?.call(context) ??
      SizedBox(
        width: widget.width,
        height: widget.height,
        child: const Center(child: CircularProgressIndicator(strokeWidth: 2)),
      );

  Widget _buildError(BuildContext context) =>
      widget.errorBuilder?.call(context) ??
      SizedBox(
        width: widget.width,
        height: widget.height,
        child: const Icon(Icons.broken_image_outlined),
      );

  Widget _buildNetworkImage(BuildContext context, String resolvedUrl) {
    return Image.network(
      resolvedUrl,
      key: widget.imageKey,
      fit: widget.fit,
      width: widget.width,
      height: widget.height,
      errorBuilder: (ctx, _, _) {
        if (SignedPhotoUrlService.needsSigning(_lastUrl) &&
            !_retriedAfterExpiry &&
            !_retryScheduled) {
          _retryScheduled = true;
          WidgetsBinding.instance.addPostFrameCallback((_) => _retryAfterExpiry());
          return _buildPlaceholder(ctx);
        }
        return _buildError(ctx);
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_lastUrl.isEmpty) return _buildError(context);

    // Public URLs bypass SignedPhotoUrlService completely.
    if (_resolveFuture == null) {
      return _buildNetworkImage(context, _lastUrl);
    }

    return FutureBuilder<String?>(
      future: _resolveFuture,
      builder: (ctx, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return _buildPlaceholder(ctx);
        }
        final resolved = snapshot.data;
        if (resolved == null || resolved.isEmpty) {
          return _buildError(ctx);
        }
        return _buildNetworkImage(ctx, resolved);
      },
    );
  }
}
