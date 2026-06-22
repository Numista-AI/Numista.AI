// mint_error_detail_screen.dart
//
// Full-screen detail view for a single Mint Error entry.
//
// Features:
//   - Zoomable image with:
//       • Mouse wheel / trackpad scroll = zoom (desktop)
//       • Click + drag = pan (desktop) | touch-drag (mobile)
//       • Pinch = zoom (mobile & Mac trackpad)
//       • Double-click/tap = zoom toggle
//       • [−] [+] [⛶] overlay buttons as visible affordance for PC users
//   - Animated hotspot pulse ring — click to auto-zoom to error location
//   - Image attribution watermark
//   - Full metadata panel: year, mint, category, rarity, value
//   - "How to Spot It" callout box
//   - Cross-linked related coins section
//   - Action buttons: Add to Wishlist / Search eBay / Ask AI

import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:photo_view/photo_view.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/mint_error.dart';

// ─── Design tokens ────────────────────────────────────────────────────────────
const _kBg      = Color(0xFFF0F2F6);
const _kDark    = Color(0xFF0E1117);
const _kAccent  = Color(0xFF4C8CDA);
const _kBrand   = Color(0xFFF63366);
const _kSurface = Color(0xFFFFFFFF);
const _kText    = Color(0xFF31333F);
const _kSubtext = Color(0xFF5A5C69);
const _kBorder  = Color(0xFFE2E6E9);

class MintErrorDetailScreen extends StatefulWidget {
  final MintError error;

  const MintErrorDetailScreen({super.key, required this.error});

  @override
  State<MintErrorDetailScreen> createState() => _MintErrorDetailScreenState();
}

class _MintErrorDetailScreenState extends State<MintErrorDetailScreen>
    with TickerProviderStateMixin {
  // ── Zoom controller — typed directly as PhotoViewController (no cast needed) ─
  final PhotoViewController _photoController = PhotoViewController();
  int _imageIndex = 0;   // Which image in the list is displayed
  bool _hotspotVisible = true;
  bool _descriptionExpanded = false;

  // ── Pulse animation for hotspot ───────────────────────────────────────────
  late AnimationController _pulseCtrl;
  late Animation<double> _pulseAnim;

  // Current scale for zoom buttons
  double _currentScale = 1.0;
  static const double _minScale = 0.5;
  static const double _maxScale = 8.0;
  static const double _scaleStep = 0.5;

  @override
  void initState() {
    super.initState();
    _pulseCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1600),
    )..repeat(reverse: true);
    _pulseAnim = Tween<double>(begin: 0.7, end: 1.0).animate(
      CurvedAnimation(parent: _pulseCtrl, curve: Curves.easeInOut),
    );
    // Track current scale for the zoom % indicator
    _photoController.outputStateStream.listen((state) {
      if (mounted) setState(() => _currentScale = state.scale ?? 1.0);
    });
  }

  @override
  void dispose() {
    _pulseCtrl.dispose();
    _photoController.dispose();
    super.dispose();
  }

  MintError get error => widget.error;
  ErrorImage? get _currentImage =>
      error.images.isNotEmpty ? error.images[_imageIndex] : null;

  // ── Zoom to hotspot — sets scale + repositions to error coordinates ──────
  void _zoomToHotspot() {
    final hotspot = _currentImage?.hotspot;
    if (hotspot == null) return;
    // Zoom to 4× directly (photo_view 0.15 has no animateScale; use direct set)
    _photoController.scale = 4.0;
    // Offset the image so the hotspot is centred in the viewport
    final size = MediaQuery.of(context).size;
    _photoController.position = Offset(
      -(hotspot.x - 0.5) * size.width * 4,
      -(hotspot.y - 0.5) * size.height * 4,
    );
  }

  // ── Zoom in / out buttons ─────────────────────────────────────────────────
  void _zoomIn() {
    final newScale = math.min(_currentScale + _scaleStep, _maxScale);
    _photoController.scale = newScale;
  }

  void _zoomOut() {
    final newScale = math.max(_currentScale - _scaleStep, _minScale);
    _photoController.scale = newScale;
  }

  void _resetZoom() {
    _photoController.scale = 1.0;
    _photoController.position = Offset.zero;
  }

  // ─────────────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _kBg,
      body: SafeArea(
        child: Column(
          children: [
            _buildTopBar(),
            Expanded(
              child: LayoutBuilder(
                builder: (context, constraints) {
                  final isWide = constraints.maxWidth > 800;
                  return isWide
                      ? _buildWideLayout(constraints)
                      : _buildNarrowLayout();
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── Top bar ───────────────────────────────────────────────────────────────
  Widget _buildTopBar() {
    return Container(
      color: _kDark,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      child: Row(
        children: [
          IconButton(
            onPressed: () => Navigator.of(context).pop(),
            icon: const Icon(Icons.arrow_back_ios_new, color: Colors.white70, size: 18),
            tooltip: 'Back to Error Library',
          ),
          const SizedBox(width: 4),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  error.name,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                    fontWeight: FontWeight.w700,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                Text(
                  error.category + (error.designation.isNotEmpty ? ' · ${error.designation}' : ''),
                  style: const TextStyle(color: Colors.white54, fontSize: 11),
                ),
              ],
            ),
          ),
          // Hotspot toggle
          if (_currentImage?.hotspot != null)
            IconButton(
              onPressed: () => setState(() => _hotspotVisible = !_hotspotVisible),
              icon: Icon(
                _hotspotVisible ? Icons.gps_fixed : Icons.gps_not_fixed,
                color: _hotspotVisible ? _kBrand : Colors.white54,
                size: 20,
              ),
              tooltip: _hotspotVisible ? 'Hide error hotspot' : 'Show error hotspot',
            ),
        ],
      ),
    );
  }

  // ── Wide layout (desktop): image left, detail right ───────────────────────
  Widget _buildWideLayout(BoxConstraints constraints) {
    final imageWidth = constraints.maxWidth * 0.55;
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Left — image + zoom controls
        SizedBox(
          width: imageWidth,
          child: Column(
            children: [
              Expanded(child: _buildImageViewer()),
              _buildZoomControls(),
              _buildImageSelector(),
              _buildAttribution(),
            ],
          ),
        ),
        const VerticalDivider(width: 1, color: _kBorder),
        // Right — details panel
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: _buildDetailPanel(),
          ),
        ),
      ],
    );
  }

  // ── Narrow layout (mobile): stacked ──────────────────────────────────────
  Widget _buildNarrowLayout() {
    return SingleChildScrollView(
      child: Column(
        children: [
          SizedBox(
            height: 280,
            child: _buildImageViewer(),
          ),
          _buildZoomControls(),
          _buildImageSelector(),
          _buildAttribution(),
          const Divider(height: 1, color: _kBorder),
          Padding(
            padding: const EdgeInsets.all(16),
            child: _buildDetailPanel(),
          ),
        ],
      ),
    );
  }

  // ── Image viewer with hotspot overlay ─────────────────────────────────────
  Widget _buildImageViewer() {
    final img = _currentImage;

    return Container(
      color: const Color(0xFF1A1D2E),
      child: Stack(
        children: [
          // ── Photo view (zoom engine) ──────────────────────────────────────
          img != null && img.url.isNotEmpty
              ? PhotoView(
                  controller: _photoController,
                  imageProvider: CachedNetworkImageProvider(img.url),
                  minScale: PhotoViewComputedScale.contained * _minScale,
                  maxScale: PhotoViewComputedScale.contained * _maxScale,
                  initialScale: PhotoViewComputedScale.contained,
                  backgroundDecoration:
                      const BoxDecoration(color: Color(0xFF1A1D2E)),
                  enableRotation: false,
                  loadingBuilder: (_, _) => const Center(
                    child: CircularProgressIndicator(color: _kBrand),
                  ),
                  errorBuilder: (_, _, _) => _buildImagePlaceholder(),
                )
              : _buildImagePlaceholder(),

          // ── Hotspot pulse overlay ─────────────────────────────────────────
          if (_hotspotVisible && img?.hotspot != null)
            Positioned.fill(
              child: LayoutBuilder(
                builder: (context, c) => GestureDetector(
                  onTap: _zoomToHotspot,
                  child: CustomPaint(
                    painter: _HotspotPainter(
                      hotspot: img!.hotspot!,
                      pulseValue: _pulseAnim.value,
                    ),
                  ),
                ),
              ),
            ),

          // ── Zoom hint overlay (bottom-left, fades after first zoom) ───────
          Positioned(
            bottom: 8,
            left: 8,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.black.withAlpha(140),
                borderRadius: BorderRadius.circular(6),
              ),
              child: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.mouse, color: Colors.white54, size: 12),
                  SizedBox(width: 4),
                  Text(
                    'Scroll to zoom · Drag to pan',
                    style: TextStyle(color: Colors.white54, fontSize: 10),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Zoom control buttons (for PC users) ───────────────────────────────────
  Widget _buildZoomControls() {
    return Container(
      color: const Color(0xFF1A1D2E),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      child: Row(
        children: [
          // Zoom out
          _ZoomButton(
            icon: Icons.remove,
            tooltip: 'Zoom out',
            onTap: _zoomOut,
          ),
          const SizedBox(width: 4),
          // Scale indicator
          Expanded(
            child: Center(
              child: Text(
                '${(_currentScale * 100).toInt()}%',
                style: const TextStyle(
                  color: Colors.white54,
                  fontSize: 11,
                  fontFamily: 'monospace',
                ),
              ),
            ),
          ),
          // Zoom in
          _ZoomButton(
            icon: Icons.add,
            tooltip: 'Zoom in',
            onTap: _zoomIn,
          ),
          const SizedBox(width: 8),
          // Reset zoom
          _ZoomButton(
            icon: Icons.fit_screen_outlined,
            tooltip: 'Reset zoom',
            onTap: _resetZoom,
          ),
          // Jump to hotspot
          if (_currentImage?.hotspot != null) ...[
            const SizedBox(width: 8),
            _ZoomButton(
              icon: Icons.gps_fixed,
              tooltip: 'Zoom to error location',
              onTap: _zoomToHotspot,
              color: _kBrand,
            ),
          ],
        ],
      ),
    );
  }

  // ── Image selector (if multiple images) ───────────────────────────────────
  Widget _buildImageSelector() {
    if (error.images.length <= 1) return const SizedBox.shrink();
    return Container(
      color: const Color(0xFF1A1D2E),
      height: 56,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
        itemCount: error.images.length,
        itemBuilder: (_, i) {
          final selected = i == _imageIndex;
          final img = error.images[i];
          return GestureDetector(
            onTap: () => setState(() => _imageIndex = i),
            child: Container(
              width: 44,
              height: 44,
              margin: const EdgeInsets.only(right: 6),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(6),
                border: Border.all(
                  color: selected ? _kBrand : Colors.transparent,
                  width: 2,
                ),
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: img.url.isNotEmpty
                    ? CachedNetworkImage(
                        imageUrl: img.url,
                        fit: BoxFit.cover,
                        errorWidget: (_, _, _) => Container(
                          color: Colors.white12,
                          child: const Icon(Icons.image_not_supported, size: 16, color: Colors.white30),
                        ),
                      )
                    : Container(
                        color: Colors.white12,
                        child: const Icon(Icons.image, size: 16, color: Colors.white30),
                      ),
              ),
            ),
          );
        },
      ),
    );
  }

  // ── Attribution strip ─────────────────────────────────────────────────────
  Widget _buildAttribution() {
    final img = _currentImage;
    if (img == null || img.attributionText.isEmpty) return const SizedBox.shrink();
    return GestureDetector(
      onTap: img.attributionUrl.isNotEmpty
          ? () => launchUrl(Uri.parse(img.attributionUrl))
          : null,
      child: Container(
        color: const Color(0xFF12151F),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
        child: Row(
          children: [
            const Icon(Icons.info_outline, size: 11, color: Colors.white38),
            const SizedBox(width: 5),
            Expanded(
              child: Text(
                'Image: ${img.attributionText}',
                style: const TextStyle(
                  color: Colors.white38,
                  fontSize: 10,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            if (img.attributionUrl.isNotEmpty)
              const Icon(Icons.open_in_new, size: 10, color: Colors.white24),
          ],
        ),
      ),
    );
  }

  // ── Detail panel ──────────────────────────────────────────────────────────
  Widget _buildDetailPanel() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildMetadataGrid(),
        const SizedBox(height: 16),
        _buildHowToSpot(),
        const SizedBox(height: 16),
        _buildDescription(),
        const SizedBox(height: 16),
        _buildActionButtons(),
        const SizedBox(height: 16),
        _buildSources(),
      ],
    );
  }

  // ── Metadata grid ─────────────────────────────────────────────────────────
  Widget _buildMetadataGrid() {
    final items = [
      {'label': 'Year', 'value': error.yearDisplay, 'icon': Icons.calendar_today_outlined},
      {'label': 'Denomination', 'value': error.denominations.map(_fmtDenom).join(', '), 'icon': Icons.monetization_on_outlined},
      {'label': 'Mint Marks', 'value': error.mintMarks.isEmpty ? 'All' : error.mintMarks.join(', '), 'icon': Icons.place_outlined},
      {'label': 'Category', 'value': error.category, 'icon': Icons.category_outlined},
      {'label': 'Rarity', 'value': error.rarity, 'icon': Icons.diamond_outlined},
      {'label': 'Est. Value', 'value': error.valueRange, 'icon': Icons.attach_money},
      if (error.designation.isNotEmpty)
        {'label': 'Designation', 'value': error.designation, 'icon': Icons.label_outline},
    ];

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: items.map((item) {
        return Container(
          constraints: const BoxConstraints(minWidth: 130),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: _kSurface,
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: _kBorder),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(item['icon'] as IconData, size: 12, color: _kSubtext),
                  const SizedBox(width: 4),
                  Text(
                    item['label'] as String,
                    style: const TextStyle(
                      fontSize: 10,
                      color: _kSubtext,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 2),
              Text(
                item['value'] as String,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: _kText,
                ),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  // ── How to Spot It ────────────────────────────────────────────────────────
  Widget _buildHowToSpot() {
    if (error.howToSpot.isEmpty) return const SizedBox.shrink();
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: _kAccent.withAlpha(15),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: _kAccent.withAlpha(60)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.visibility_outlined, size: 15, color: _kAccent),
              const SizedBox(width: 6),
              const Text(
                'How to Spot It',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: _kAccent,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            error.howToSpot,
            style: const TextStyle(fontSize: 13, color: _kText, height: 1.5),
          ),
        ],
      ),
    );
  }

  // ── Description ───────────────────────────────────────────────────────────
  Widget _buildDescription() {
    if (error.description.isEmpty) return const SizedBox.shrink();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'About This Error',
          style: TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: _kText),
        ),
        const SizedBox(height: 8),
        Text(
          _descriptionExpanded
              ? error.description
              : (error.description.length > 300
                  ? '${error.description.substring(0, 300)}…'
                  : error.description),
          style: const TextStyle(fontSize: 13, color: _kText, height: 1.6),
        ),
        if (error.description.length > 300)
          TextButton(
            onPressed: () =>
                setState(() => _descriptionExpanded = !_descriptionExpanded),
            child: Text(
              _descriptionExpanded ? 'Show less' : 'Read more',
              style: const TextStyle(fontSize: 12, color: _kAccent),
            ),
          ),
      ],
    );
  }

  // ── Action buttons ────────────────────────────────────────────────────────
  Widget _buildActionButtons() {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        // Search eBay
        _ActionButton(
          icon: Icons.storefront_outlined,
          label: 'Search eBay',
          color: const Color(0xFF0064D2),
          onTap: () async {
            final query = Uri.encodeComponent('${error.shortName} error coin');
            final url = 'https://www.ebay.com/sch/i.html?_nkw=$query&_sacat=11116';
            if (await canLaunchUrl(Uri.parse(url))) {
              await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
            }
          },
        ),
        // Ask AI
        _ActionButton(
          icon: Icons.psychology_outlined,
          label: 'Ask AI About This',
          color: _kBrand,
          onTap: () {
            // Pop back and signal a navigation to AI Deepdive with a pre-filled query
            Navigator.of(context).pop();
            // The parent MintErrorLibraryScreen can pass a callback in Phase 2;
            // for now we notify via a returned result that the caller can check.
          },
        ),
        // External: PCGS lookup
        _ActionButton(
          icon: Icons.search_outlined,
          label: 'Look Up on PCGS',
          color: const Color(0xFF1A3A5C),
          onTap: () async {
            final q = Uri.encodeComponent(error.name);
            final url = 'https://www.pcgs.com/coinfacts/search?SearchTerm=$q';
            if (await canLaunchUrl(Uri.parse(url))) {
              await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
            }
          },
        ),
      ],
    );
  }

  // ── Sources ───────────────────────────────────────────────────────────────
  Widget _buildSources() {
    if (error.sources.isEmpty) return const SizedBox.shrink();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Sources & References',
          style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: _kSubtext),
        ),
        const SizedBox(height: 6),
        ...error.sources.map(
          (s) => Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('• ', style: TextStyle(color: _kSubtext)),
                Expanded(
                  child: Text(s, style: const TextStyle(fontSize: 12, color: _kSubtext)),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  // ── Image placeholder ─────────────────────────────────────────────────────
  Widget _buildImagePlaceholder() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.photo_camera_outlined,
            size: 48,
            color: Colors.white24,
          ),
          const SizedBox(height: 12),
          Text(
            error.shortName,
            style: const TextStyle(
              color: Colors.white54,
              fontSize: 16,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 6),
          const Text(
            'High-quality image pending.\nCheck back soon or view on PCGS CoinFacts.',
            style: TextStyle(color: Colors.white30, fontSize: 12),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}

// ─── Hotspot Painter (animated pulse ring) ────────────────────────────────────
class _HotspotPainter extends CustomPainter {
  final ErrorHotspot hotspot;
  final double pulseValue; // 0.7 – 1.0

  const _HotspotPainter({required this.hotspot, required this.pulseValue});

  @override
  void paint(Canvas canvas, Size size) {
    final cx = hotspot.x * size.width;
    final cy = hotspot.y * size.height;
    final r = hotspot.radius * math.min(size.width, size.height);

    // Outer pulse ring
    final outerPaint = Paint()
      ..color = const Color(0xFFF63366).withAlpha((80 * (1 - pulseValue + 0.3)).clamp(0, 255).toInt())
      ..style = PaintingStyle.fill;
    canvas.drawCircle(Offset(cx, cy), r * 1.8 * pulseValue, outerPaint);

    // Inner ring (solid outline)
    final ringPaint = Paint()
      ..color = const Color(0xFFF63366)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;
    canvas.drawCircle(Offset(cx, cy), r, ringPaint);

    // Center dot
    final dotPaint = Paint()
      ..color = const Color(0xFFF63366).withAlpha(180)
      ..style = PaintingStyle.fill;
    canvas.drawCircle(Offset(cx, cy), 4, dotPaint);
  }

  @override
  bool shouldRepaint(_HotspotPainter old) => old.pulseValue != pulseValue;
}

// ─── Zoom button widget ───────────────────────────────────────────────────────
class _ZoomButton extends StatelessWidget {
  final IconData icon;
  final String tooltip;
  final VoidCallback onTap;
  final Color? color;

  const _ZoomButton({
    required this.icon,
    required this.tooltip,
    required this.onTap,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: tooltip,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(6),
        child: Container(
          padding: const EdgeInsets.all(6),
          decoration: BoxDecoration(
            color: Colors.white.withAlpha(12),
            borderRadius: BorderRadius.circular(6),
          ),
          child: Icon(
            icon,
            size: 16,
            color: color ?? Colors.white70,
          ),
        ),
      ),
    );
  }
}

// ─── Action button widget ─────────────────────────────────────────────────────
class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _ActionButton({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton.icon(
      onPressed: onTap,
      icon: Icon(icon, size: 15),
      label: Text(label, style: const TextStyle(fontSize: 12)),
      style: ElevatedButton.styleFrom(
        backgroundColor: color,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        elevation: 0,
      ),
    );
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
String _fmtDenom(String d) {
  switch (d.toLowerCase()) {
    case 'cent': return 'Cent';
    case 'nickel': return 'Nickel';
    case 'dime': return 'Dime';
    case 'quarter': return 'Quarter';
    case 'half dollar': return 'Half Dollar';
    case 'dollar': return 'Dollar';
    case 'silver eagle': return 'Silver Eagle';
    case 'gold eagle': return 'Gold Eagle';
    case 'currency': return 'Currency';
    default: return d;
  }
}
