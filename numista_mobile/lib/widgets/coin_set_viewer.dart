import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';

// ─────────────────────────────────────────────────────────────────────────────
// CoinSetViewer
// ─────────────────────────────────────────────────────────────────────────────
// Displays a coin set (e.g. Jamul Sovereign, Birth Year Set) as an interactive
// horizontal strip. Each coin tile:
//   • Shows the obverse by default
//   • Taps to flip to the reverse (AnimatedSwitcher)
//   • Long-press opens a full-screen lightbox
//   • Has a denomination label beneath it
//
// Usage (in inspector panel or detail screen):
//   CoinSetViewer(setId: 'jamul-sovereign-2018')
//
// The widget loads the set manifest from Firestore coin_set_index/{setId} and
// then renders one tile per denomination in face-value order.
// ─────────────────────────────────────────────────────────────────────────────

// ─── Colour constants (matches my_collection_screen.dart palette) ─────────────
const _kSurface = Colors.white;
const _kText    = Color(0xFF31333F);
const _kSubtext = Color(0xFF5A5C69);
const _kAccent  = Color(0xFF4C8CDA);
const _kBorder  = Color(0xFFE2E6E9);
const _kBadge   = Color(0xFF1A3A5C);

// ─── Data model ───────────────────────────────────────────────────────────────
class _CoinInSet {
  final String denomination;
  final String label;
  final String name;
  final String? obverseUrl;
  final String? reverseUrl;

  const _CoinInSet({
    required this.denomination,
    required this.label,
    required this.name,
    this.obverseUrl,
    this.reverseUrl,
  });

  factory _CoinInSet.fromMap(Map<String, dynamic> m) => _CoinInSet(
        denomination: m['denomination'] as String? ?? '',
        label:        m['label']        as String? ?? '',
        name:         m['name']         as String? ?? '',
        obverseUrl:   m['obverse_url']  as String?,
        reverseUrl:   m['reverse_url']  as String?,
      );
}

class _CoinSetData {
  final String setId;
  final String name;
  final String year;
  final String attribution;
  final String heroUrl;
  final List<_CoinInSet> coins;

  const _CoinSetData({
    required this.setId,
    required this.name,
    required this.year,
    required this.attribution,
    required this.heroUrl,
    required this.coins,
  });

  factory _CoinSetData.fromDoc(Map<String, dynamic> d) => _CoinSetData(
        setId:       d['set_id']       as String? ?? '',
        name:        d['name']         as String? ?? 'Coin Set',
        year:        d['year']?.toString() ?? '',
        attribution: d['attribution']  as String? ?? '',
        heroUrl:     d['hero_url']     as String? ?? '',
        coins: ((d['coins'] as List?) ?? [])
            .map((c) => _CoinInSet.fromMap(Map<String, dynamic>.from(c as Map)))
            .toList(),
      );
}

// ─────────────────────────────────────────────────────────────────────────────
// Public widget
// ─────────────────────────────────────────────────────────────────────────────
class CoinSetViewer extends StatefulWidget {
  final String setId;

  /// Optional: if you already have the data loaded, pass it directly
  /// to avoid a Firestore round-trip.
  final Map<String, dynamic>? preloadedData;

  const CoinSetViewer({
    super.key,
    required this.setId,
    this.preloadedData,
  });

  @override
  State<CoinSetViewer> createState() => _CoinSetViewerState();
}

class _CoinSetViewerState extends State<CoinSetViewer> {
  _CoinSetData? _data;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    if (widget.preloadedData != null) {
      _data    = _CoinSetData.fromDoc(widget.preloadedData!);
      _loading = false;
    } else {
      _load();
    }
  }

  Future<void> _load() async {
    try {
      final doc = await FirebaseFirestore.instance
          .collection('coin_set_index')
          .doc(widget.setId)
          .get();
      if (!doc.exists) {
        setState(() { _error = 'Set not found: ${widget.setId}'; _loading = false; });
        return;
      }
      setState(() {
        _data    = _CoinSetData.fromDoc(doc.data()!);
        _loading = false;
      });
    } catch (e) {
      setState(() { _error = e.toString(); _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const SizedBox(
        height: 160,
        child: Center(
          child: CircularProgressIndicator(color: _kAccent, strokeWidth: 2),
        ),
      );
    }
    if (_error != null) {
      return Padding(
        padding: const EdgeInsets.all(16),
        child: Text('⚠ $_error',
            style: const TextStyle(color: Colors.red, fontSize: 12)),
      );
    }
    final data = _data!;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // ── Header ──────────────────────────────────────────────────────────
        Padding(
          padding: const EdgeInsets.only(bottom: 10),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: _kBadge,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.collections_outlined,
                        size: 12, color: Colors.white70),
                    const SizedBox(width: 5),
                    Text(
                      '${data.coins.length}-COIN SET',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 10,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 0.8,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  data.name,
                  style: const TextStyle(
                    color: _kText,
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ),

        // ── Coin strip ──────────────────────────────────────────────────────
        SizedBox(
          height: 148,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: data.coins.length,
            separatorBuilder: (_, __) => const SizedBox(width: 10),
            itemBuilder: (ctx, i) => _CoinTile(
              coin: data.coins[i],
              onLongPress: (url, label) =>
                  _showLightbox(context, url, label, data.attribution),
            ),
          ),
        ),

        // ── Attribution footer ───────────────────────────────────────────────
        if (data.attribution.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 6),
            child: Text(
              data.attribution,
              style: TextStyle(
                fontSize: 9,
                color: _kSubtext.withAlpha(160),
                fontStyle: FontStyle.italic,
              ),
            ),
          ),

        const SizedBox(height: 4),
        Text(
          'Tap coin to flip  •  Long-press to expand',
          style: TextStyle(
            fontSize: 10,
            color: _kSubtext.withAlpha(130),
            fontStyle: FontStyle.italic,
          ),
        ),
      ],
    );
  }

  void _showLightbox(
      BuildContext ctx, String url, String label, String attribution) {
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
                style:
                    const TextStyle(color: Colors.white54, fontSize: 11),
              ),
              if (attribution.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(
                    attribution,
                    style: const TextStyle(
                        color: Colors.white38, fontSize: 9,
                        fontStyle: FontStyle.italic),
                    textAlign: TextAlign.center,
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Individual coin tile — tappable flip card
// ─────────────────────────────────────────────────────────────────────────────
class _CoinTile extends StatefulWidget {
  final _CoinInSet coin;
  final void Function(String url, String label) onLongPress;

  const _CoinTile({required this.coin, required this.onLongPress});

  @override
  State<_CoinTile> createState() => _CoinTileState();
}

class _CoinTileState extends State<_CoinTile> {
  bool _showingReverse = false;

  String? get _currentUrl =>
      _showingReverse ? widget.coin.reverseUrl : widget.coin.obverseUrl;

  String get _sideLabel => _showingReverse ? 'Reverse' : 'Obverse';

  bool get _canFlip =>
      widget.coin.obverseUrl != null && widget.coin.reverseUrl != null;

  @override
  Widget build(BuildContext context) {
    final label = '${widget.coin.label}${widget.coin.name.isNotEmpty ? " — ${widget.coin.name}" : ""}';

    return GestureDetector(
      onTap: _canFlip
          ? () => setState(() => _showingReverse = !_showingReverse)
          : null,
      onLongPress: _currentUrl != null
          ? () => widget.onLongPress(_currentUrl!, '$label · $_sideLabel')
          : null,
      child: SizedBox(
        width: 100,
        child: Column(
          children: [
            // ── Image with flip animation ──────────────────────────────────
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: _kSurface,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: _kBorder),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withAlpha(15),
                      blurRadius: 4,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(7),
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      // Image
                      AnimatedSwitcher(
                        duration: const Duration(milliseconds: 280),
                        transitionBuilder: (child, animation) =>
                            FadeTransition(opacity: animation, child: child),
                        child: _currentUrl != null
                            ? Image.network(
                                _currentUrl!,
                                key: ValueKey(_currentUrl),
                                fit: BoxFit.cover,
                                errorBuilder: (_, e, st) => const Center(
                                  child: Icon(Icons.broken_image_outlined,
                                      color: _kSubtext, size: 28),
                                ),
                              )
                            : const Center(
                                child: Icon(Icons.image_not_supported_outlined,
                                    color: _kBorder, size: 28),
                              ),
                      ),

                      // Side indicator badge (top-right)
                      Positioned(
                        top: 4,
                        right: 4,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 5, vertical: 2),
                          decoration: BoxDecoration(
                            color: Colors.black54,
                            borderRadius: BorderRadius.circular(3),
                          ),
                          child: Text(
                            _showingReverse ? 'REV' : 'OBV',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 8,
                              fontWeight: FontWeight.bold,
                              letterSpacing: 0.5,
                            ),
                          ),
                        ),
                      ),

                      // Flip indicator overlay (only if flippable)
                      if (_canFlip)
                        Positioned(
                          bottom: 4,
                          right: 4,
                          child: Container(
                            padding: const EdgeInsets.all(3),
                            decoration: BoxDecoration(
                              color: _kAccent.withAlpha(200),
                              borderRadius: BorderRadius.circular(3),
                            ),
                            child: const Icon(Icons.flip,
                                size: 10, color: Colors.white),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            ),

            // ── Denomination label ─────────────────────────────────────────
            const SizedBox(height: 5),
            Text(
              widget.coin.label,
              style: const TextStyle(
                color: _kText,
                fontSize: 11,
                fontWeight: FontWeight.w600,
              ),
              textAlign: TextAlign.center,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            if (widget.coin.name.isNotEmpty)
              Text(
                widget.coin.name,
                style: const TextStyle(color: _kSubtext, fontSize: 9),
                textAlign: TextAlign.center,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Collection list thumbnail — used in the table/grid view
// Shows hero image with a "N-coin set" badge overlay
// ─────────────────────────────────────────────────────────────────────────────
class CoinSetThumbnail extends StatelessWidget {
  final String heroUrl;
  final int    coinCount;
  final double size;

  const CoinSetThumbnail({
    super.key,
    required this.heroUrl,
    required this.coinCount,
    this.size = 48,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        fit: StackFit.expand,
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: Image.network(
              heroUrl,
              fit: BoxFit.cover,
              errorBuilder: (_, _, _) => Container(
                color: _kBorder,
                child: const Icon(Icons.monetization_on_outlined,
                    color: _kSubtext, size: 20),
              ),
            ),
          ),
          // Badge
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 2),
              decoration: BoxDecoration(
                color: _kBadge.withAlpha(210),
                borderRadius: const BorderRadius.only(
                  bottomLeft:  Radius.circular(6),
                  bottomRight: Radius.circular(6),
                ),
              ),
              child: Text(
                '$coinCount coins',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 8,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
