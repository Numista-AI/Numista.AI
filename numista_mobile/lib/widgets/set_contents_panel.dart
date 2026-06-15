import 'package:flutter/material.dart';
import '../services/coin_image_service.dart';

// ─────────────────────────────────────────────────────────────────────────────
// SetContentsPanel
// ─────────────────────────────────────────────────────────────────────────────
// Renders the "Set Contents" section in the Coin Inspector for sets imported
// from invoices. Unlike CoinSetViewer (which loads from coin_set_index),
// this widget works entirely from the set_contents array stored in the
// parent Firestore document — no additional Firestore lookup needed.
//
// Displays:
//   1. A scrollable image strip: shared obverse + one reverse per unique design
//   2. A grouped list: each design (park / subject) with P / D / S mint badges
//
// Usage:
//   SetContentsPanel(data: coinDocumentData)
// ─────────────────────────────────────────────────────────────────────────────

// ─── Colour constants (matches my_collection_screen.dart palette) ─────────────
const _kText    = Color(0xFF31333F);
const _kSubtext = Color(0xFF5A5C69);
const _kAccent  = Color(0xFF4C8CDA);
const _kBorder  = Color(0xFFE2E6E9);
const _kBadge   = Color(0xFF1A3A5C);
const _kSurface = Colors.white;

// ─────────────────────────────────────────────────────────────────────────────
// Data model
// ─────────────────────────────────────────────────────────────────────────────
class _DesignGroup {
  final String subject;
  final String denomination;
  final String year;
  final List<String> mints;

  _DesignGroup({
    required this.subject,
    required this.denomination,
    required this.year,
    required this.mints,
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// Public widget
// ─────────────────────────────────────────────────────────────────────────────
class SetContentsPanel extends StatefulWidget {
  /// The raw Firestore document data map for the parent coin/set record.
  final Map<String, dynamic> data;

  const SetContentsPanel({super.key, required this.data});

  @override
  State<SetContentsPanel> createState() => _SetContentsPanelState();
}

class _SetContentsPanelState extends State<SetContentsPanel> {
  List<_DesignGroup> _groups = [];
  // Parallel list of images for each unique design; null = not yet fetched.
  List<CoinImageResult?> _images = [];
  CoinImageResult? _obverseImage;
  bool _imagesLoading = true;

  @override
  void initState() {
    super.initState();
    _buildGroups();
    _fetchImages();
  }

  // ─── Parse set_contents into design groups ────────────────────────────────
  void _buildGroups() {
    final raw = widget.data['set_contents'];
    if (raw == null || raw is! List || raw.isEmpty) return;

    final map = <String, _DesignGroup>{};
    for (final item in raw) {
      if (item is! Map) continue;
      final subject = (item['Theme/Subject'] ?? '').toString().trim();
      final mint    = (item['Mint Mark']     ?? '').toString().trim().toUpperCase();
      final denom   = (item['Denomination']  ?? '').toString().trim();
      final year    = (item['Year']          ?? '').toString().trim();

      // Fall back to the parent record's denomination / year if item has none.
      final effDenom = denom.isNotEmpty ? denom
          : (widget.data['Denomination']?.toString() ?? '');
      final effYear  = year.isNotEmpty ? year
          : (widget.data['Year']?.toString() ?? '');

      if (subject.isEmpty) continue;

      if (!map.containsKey(subject)) {
        map[subject] = _DesignGroup(
          subject:      subject,
          denomination: effDenom,
          year:         effYear,
          mints:        [],
        );
      }
      if (mint.isNotEmpty && !map[subject]!.mints.contains(mint)) {
        map[subject]!.mints.add(mint);
      }
    }

    _groups = map.values.toList();

    // Sort mints in standard numismatic order.
    const mintOrder = ['P', 'D', 'S', 'W', 'O', 'CC'];
    for (final g in _groups) {
      g.mints.sort((a, b) {
        final ai = mintOrder.indexOf(a);
        final bi = mintOrder.indexOf(b);
        return (ai == -1 ? 99 : ai).compareTo(bi == -1 ? 99 : bi);
      });
    }
    _images = List.filled(_groups.length, null);
  }

  // ─── Fetch reference images ───────────────────────────────────────────────
  Future<void> _fetchImages() async {
    if (_groups.isEmpty) {
      if (mounted) setState(() => _imagesLoading = false);
      return;
    }

    final year        = (widget.data['Year']?.toString()            ?? '').trim();
    final series      = (widget.data['Program/Series']?.toString()  ?? '').trim();
    final denomination = (widget.data['Denomination']?.toString()   ?? '').trim();

    // Fetch shared obverse (no subject → generic design obverse for this program).
    try {
      final obv = await CoinImageService.fetchReferenceImages(
        year:         year.isEmpty ? (_groups.isNotEmpty ? _groups.first.year : '') : year,
        denomination: denomination,
        series:       series,
      );
      if (mounted) setState(() => _obverseImage = obv.hasAny ? obv : null);
    } catch (_) {/* silent — image lookup is non-critical */}

    // Fetch reverse for each unique design group.
    for (int i = 0; i < _groups.length; i++) {
      try {
        final img = await CoinImageService.fetchReferenceImages(
          year:         _groups[i].year.isEmpty ? year : _groups[i].year,
          denomination: denomination,
          series:       series,
          subject:      _groups[i].subject,
        );
        if (mounted) {
          setState(() {
            _images[i] = img.hasAny ? img : null;
          });
        }
      } catch (_) {/* silent */}
    }

    if (mounted) setState(() => _imagesLoading = false);
  }

  // ─── Build ────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    if (_groups.isEmpty) return const SizedBox.shrink();

    final raw        = widget.data['set_contents'];
    final totalCoins = (raw is List) ? raw.length : 0;
    final designs    = _groups.length;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Divider(color: _kBorder),
        const SizedBox(height: 16),

        // ── Section header badge ─────────────────────────────────────────────
        Row(children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: _kBadge,
              borderRadius: BorderRadius.circular(4),
            ),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              const Icon(Icons.grid_view, size: 12, color: Colors.white70),
              const SizedBox(width: 5),
              Text(
                '$totalCoins-COIN SET  ·  $designs DESIGNS',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.8,
                ),
              ),
            ]),
          ),
        ]),

        const SizedBox(height: 14),

        // ── Scrollable image strip ───────────────────────────────────────────
        _buildImageStrip(context),

        const SizedBox(height: 16),

        // ── Design rows ──────────────────────────────────────────────────────
        ..._groups.asMap().entries.map((e) => _buildDesignRow(e.key, e.value)),

        const SizedBox(height: 8),

        // ── Summary footer ───────────────────────────────────────────────────
        if (_groups.isNotEmpty)
          Text(
            '$designs designs × ${_groups.first.mints.length} mints = $totalCoins coins',
            style: TextStyle(
              fontSize: 10,
              color: _kSubtext.withAlpha(130),
              fontStyle: FontStyle.italic,
            ),
          ),

        const SizedBox(height: 4),
        Text(
          'Tap image to expand  •  Tap coin to view details',
          style: TextStyle(
            fontSize: 10,
            color: _kSubtext.withAlpha(110),
            fontStyle: FontStyle.italic,
          ),
        ),
        const SizedBox(height: 4),
      ],
    );
  }

  // ─── Image strip: [OBV] [REV_1] [REV_2] ... [REV_n] ─────────────────────
  Widget _buildImageStrip(BuildContext context) {
    return SizedBox(
      height: 148,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: 1 + _groups.length, // 1 shared obverse + N reverses
        separatorBuilder: (_, _) => const SizedBox(width: 8),
        itemBuilder: (ctx, i) {
          if (i == 0) {
            // Shared obverse
            final url = _obverseImage?.obverseUrl;
            return _ImageThumbnail(
              url:       url,
              badge:     'OBV',
              sublabel:  'Obverse\n(shared)',
              isLoading: _imagesLoading && url == null,
              onTap:     url != null
                  ? () => _showLightbox(ctx, url, 'Obverse — Shared Design')
                  : null,
            );
          }
          // Reverse for group [i-1]
          final g   = _groups[i - 1];
          final img = _images[i - 1];
          // Prefer the subject-specific reverse; fall back to obverse if only that was found.
          final url = img?.reverseUrl ?? img?.obverseUrl;
          return _ImageThumbnail(
            url:       url,
            badge:     'REV',
            sublabel:  _shortLabel(g.subject),
            isLoading: _imagesLoading && img == null,
            onTap:     url != null
                ? () => _showLightbox(ctx, url, g.subject)
                : null,
          );
        },
      ),
    );
  }

  // ─── Single design row: small preview + park name + mint badges ───────────
  Widget _buildDesignRow(int index, _DesignGroup group) {
    final img = _images[index];
    final previewUrl = img?.reverseUrl ?? img?.obverseUrl;

    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Row(crossAxisAlignment: CrossAxisAlignment.center, children: [
        // Tiny reverse preview
        Container(
          width: 34,
          height: 34,
          decoration: BoxDecoration(
            color: _kBorder.withAlpha(80),
            borderRadius: BorderRadius.circular(5),
            border: Border.all(color: _kBorder),
          ),
          child: previewUrl != null
              ? ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: Image.network(
                    previewUrl,
                    fit: BoxFit.cover,
                    errorBuilder: (_, _, _) => const Center(
                                child: Icon(Icons.image_not_supported_outlined, color: _kBorder, size: 22)),
                  ),
                )
              : const Icon(Icons.monetization_on_outlined, size: 16, color: _kBorder),
        ),
        const SizedBox(width: 10),

        // Park name + mint badges
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                group.subject,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: _kText,
                ),
              ),
              const SizedBox(height: 4),
              Wrap(
                spacing: 4,
                children: group.mints.map((m) => Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color:  _kAccent.withAlpha(20),
                    borderRadius: BorderRadius.circular(3),
                    border: Border.all(color: _kAccent.withAlpha(80)),
                  ),
                  child: Text(
                    m,
                    style: const TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      color: _kAccent,
                    ),
                  ),
                )).toList(),
              ),
            ],
          ),
        ),
      ]),
    );
  }

  // ─── Utilities ────────────────────────────────────────────────────────────

  /// Shorten a long park name to 2–3 meaningful words for the image strip label.
  String _shortLabel(String subject) {
    const skip = {'National', 'Historical', 'Park', 'The', 'Of', 'And',
                  'Monument', 'Memorial', 'Site', 'For'};
    final words = subject
        .split(' ')
        .where((w) => w.length > 2 && !skip.contains(w))
        .take(2)
        .join(' ');
    return words.isNotEmpty ? words : subject.split(' ').take(2).join(' ');
  }

  void _showLightbox(BuildContext ctx, String url, String label) {
    showDialog(
      context: ctx,
      barrierColor: Colors.black87,
      builder: (dCtx) => GestureDetector(
        onTap: () => Navigator.pop(dCtx),
        child: Dialog(
          backgroundColor: Colors.transparent,
          insetPadding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: InteractiveViewer(
                  minScale: 0.8,
                  maxScale: 5.0,
                  child: Image.network(
                    url,
                    fit: BoxFit.contain,
                    errorBuilder: (_, _, _) => const Padding(
                      padding: EdgeInsets.all(40),
                      child: Icon(Icons.broken_image_outlined,
                          color: Colors.white30, size: 60),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Text(
                '$label  •  Tap anywhere to close',
                style: const TextStyle(color: Colors.white54, fontSize: 11),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Image thumbnail tile used in the horizontal strip
// ─────────────────────────────────────────────────────────────────────────────
class _ImageThumbnail extends StatelessWidget {
  final String? url;
  final String  badge;
  final String  sublabel;
  final bool    isLoading;
  final VoidCallback? onTap;

  const _ImageThumbnail({
    required this.badge,
    required this.sublabel,
    this.url,
    this.isLoading = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: SizedBox(
        width: 100,
        child: Column(children: [
          // ── Image tile ─────────────────────────────────────────────────────
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: _kSurface,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: _kBorder),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withAlpha(12),
                    blurRadius: 4,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(7),
                child: Stack(fit: StackFit.expand, children: [
                  // Image / placeholder / spinner
                  if (url != null)
                    Image.network(
                      url!,
                      fit: BoxFit.cover,
                      loadingBuilder: (ctx, child, prog) =>
                          prog == null ? child
                          : const Center(
                              child: CircularProgressIndicator(
                                  color: _kAccent, strokeWidth: 2)),
                      errorBuilder: (_, _, _) => Center(
                        child: Column(mainAxisSize: MainAxisSize.min, children: [
                          const Icon(Icons.image_not_supported_outlined,
                              color: _kBorder, size: 22),
                          const SizedBox(height: 3),
                          Text('No image',
                              style: TextStyle(fontSize: 8,
                                  color: _kSubtext.withAlpha(130))),
                        ]),
                      ),
                    )
                  else if (isLoading)
                    const Center(
                      child: CircularProgressIndicator(
                          color: _kAccent, strokeWidth: 2))
                  else
                    Center(
                      child: Column(mainAxisSize: MainAxisSize.min, children: [
                        const Icon(Icons.monetization_on_outlined,
                            color: _kBorder, size: 22),
                        const SizedBox(height: 3),
                        Text('No image',
                            style: TextStyle(fontSize: 8,
                                color: _kSubtext.withAlpha(130))),
                      ]),
                    ),

                  // OBV / REV badge
                  Positioned(
                    top: 4, right: 4,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 5, vertical: 2),
                      decoration: BoxDecoration(
                        color: Colors.black54,
                        borderRadius: BorderRadius.circular(3),
                      ),
                      child: Text(badge,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 8,
                            fontWeight: FontWeight.bold,
                          )),
                    ),
                  ),

                  // Zoom hint (only when image loaded)
                  if (url != null)
                    Positioned(
                      bottom: 4, right: 4,
                      child: Container(
                        padding: const EdgeInsets.all(3),
                        decoration: BoxDecoration(
                          color: _kAccent.withAlpha(200),
                          borderRadius: BorderRadius.circular(3),
                        ),
                        child: const Icon(Icons.zoom_in,
                            size: 10, color: Colors.white),
                      ),
                    ),
                ]),
              ),
            ),
          ),

          // ── Label below tile ───────────────────────────────────────────────
          const SizedBox(height: 5),
          Text(
            sublabel,
            style: const TextStyle(
              color: _kText,
              fontSize: 9,
              fontWeight: FontWeight.w500,
            ),
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ]),
      ),
    );
  }
}
