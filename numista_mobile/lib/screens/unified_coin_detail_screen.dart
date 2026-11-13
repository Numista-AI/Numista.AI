import 'dart:async';
import 'dart:convert';

import 'package:cloud_firestore/cloud_firestore.dart'
    show DocumentSnapshot, QueryDocumentSnapshot;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show AssetBundle, rootBundle;
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:url_launcher/url_launcher.dart';

import '../models/coin_model.dart';
import '../utils/owned_storage_url.dart';
import 'unified_coin_detail_deps.dart';

/// Fail-closed feature gate consulted by UnifiedCoinDetailScreen.show() and showPublic().
class UnifiedDetailsGate {
  static Future<bool>? _cached;

  @visibleForTesting
  static AssetBundle? debugBundle;

  @visibleForTesting
  static void debugReset() => _cached = null;

  static Future<bool> isEnabled() => _cached ??= _load();

  static Future<bool> _load() async {
    try {
      final jsonStr =
          await (debugBundle ?? rootBundle).loadString('assets/config/features.json');
      final Map<String, dynamic> config = jsonDecode(jsonStr) as Map<String, dynamic>;
      return config['unified_details_view_v1'] == true;
    } catch (_) {
      return false; // fail closed to legacy views if config missing/malformed
    }
  }
}

/// Top-level virtual-child parent index resolver used across all call sites and tests.
int? resolveParentIndex(List<dynamic> rows, String parentId) {
  if (parentId.isEmpty) return null;
  final idx = rows.indexWhere((r) {
    try {
      return r.id == parentId;
    } catch (_) {
      return false;
    }
  });
  return idx >= 0 ? idx : null;
}

/// Strips raw HTML tags (including script/style blocks), markdown images, and links while preserving bold/italic/plain text.
String sanitizeNotesText(String raw) {
  var out = raw.replaceAll(
    RegExp(r'<(script|style)\b[^>]*>[\s\S]*?</\1>', caseSensitive: false),
    '',
  );
  out = out.replaceAll(RegExp(r'<[^>]*>'), '');
  out = out.replaceAll(RegExp(r'!\[[^\]]*\]\([^\)]*\)'), '');
  out = out.replaceAllMapped(
    RegExp(r'\[([^\]]+)\]\([^\)]*\)'),
    (m) => m.group(1) ?? '',
  );
  return out.trim();
}

/// High-contrast sandboxed markdown style sheet (prevents inherited white-on-white text).
MarkdownStyleSheet getSandboxedMarkdownStyleSheet(BuildContext context) {
  final isDark = Theme.of(context).brightness == Brightness.dark;
  final baseColor = isDark ? const Color(0xFFF8FAFC) : const Color(0xFF0F172A);
  return MarkdownStyleSheet.fromTheme(Theme.of(context)).copyWith(
    p: TextStyle(color: baseColor, fontSize: 15, height: 1.5),
    strong: TextStyle(color: baseColor, fontWeight: FontWeight.w700),
    em: TextStyle(color: baseColor, fontStyle: FontStyle.italic),
    listBullet: TextStyle(color: baseColor),
  );
}

/// Validates strict HTTPS Congress.gov bill URLs without userInfo/ports.
bool isValidCongressGovUrl(String url) {
  final uri = Uri.tryParse(url.trim());
  if (uri == null || uri.scheme != 'https') return false;
  if (uri.userInfo.isNotEmpty || uri.hasPort) return false;
  final host = uri.host.toLowerCase();
  if (host != 'www.congress.gov' && host != 'congress.gov') return false;
  return RegExp(r'^/bill/\d+(st|nd|rd|th)-congress/(house|senate)-bill/\d+$')
      .hasMatch(uri.path);
}

/// Launches validated Congress.gov URLs externally without auth headers.
Future<void> launchOutboundCongressUrl(
  BuildContext context,
  String url, {
  UnifiedCoinDetailDeps? harness,
}) async {
  if (!isValidCongressGovUrl(url)) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Invalid or untrusted legislative link'),
        backgroundColor: Colors.redAccent,
      ),
    );
    return;
  }
  if (harness?.onLaunchUrl != null) {
    harness!.onLaunchUrl!(url);
    return;
  }
  await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
}

/// Read-only public catalog projection (redacts private owner fields).
class PublicCoinProjection {
  final String nacCode;
  final String title;
  final String denomination;
  final String composition;
  final double? cpgRetail;
  final String? primaryImageUrl;
  final String? legislationKey;
  final String? weightG;
  final String? diameterMm;

  const PublicCoinProjection({
    required this.nacCode,
    required this.title,
    required this.denomination,
    required this.composition,
    this.cpgRetail,
    this.primaryImageUrl,
    this.legislationKey,
    this.weightG,
    this.diameterMm,
  });

  static const Set<String> _approvedCatalogHosts = {
    'images.metmuseum.org',
    'numismatics.org',
    'thumb.wikimedia.org',
    'upload.wikimedia.org',
  };

  static bool isApprovedCatalogHostUrl(String url) {
    final uri = Uri.tryParse(url.trim());
    if (uri == null ||
        uri.scheme != 'https' ||
        uri.userInfo.isNotEmpty ||
        uri.hasPort) {
      return false;
    }
    return _approvedCatalogHosts.contains(uri.host.toLowerCase());
  }

  static String? _approvedPrimaryImageUrl(dynamic img) {
    if (img is! Map) return null;
    final url = img['url']?.toString() ?? '';
    final license = img['license']?.toString() ?? '';
    final source = img['source_url']?.toString() ?? '';
    if (!isApprovedCatalogHostUrl(url)) return null;
    if (license.isEmpty || source.isEmpty) return null;
    return url;
  }

  factory PublicCoinProjection.fromCatalogMap(Map<String, dynamic> m) {
    return PublicCoinProjection(
      nacCode: m['nac_code']?.toString() ?? '',
      title: m['title']?.toString() ?? m['name']?.toString() ?? 'Catalog Coin',
      denomination: m['denomination']?.toString() ?? '',
      composition: m['composition']?.toString() ??
          m['metalContent']?.toString() ??
          'Not Recorded',
      cpgRetail: (m['cpg_retail'] as num?)?.toDouble() ??
          (m['cpgRetail'] as num?)?.toDouble(),
      primaryImageUrl: _approvedPrimaryImageUrl(m['primary_image']),
      legislationKey: m['legislation_key']?.toString(),
      weightG: m['weight_g']?.toString() ?? 'Not Recorded',
      diameterMm: m['diameter_mm']?.toString() ?? 'Not Recorded',
    );
  }

  factory PublicCoinProjection.fromCoinModel(
    CoinModel coin, {
    String? referenceImageUrl,
  }) {
    return PublicCoinProjection(
      nacCode: RegExp(r'^NAC1?\.').hasMatch(coin.personalRef.trim().toUpperCase())
          ? coin.personalRef.trim().toUpperCase()
          : '',
      title: coin.themeSubject.isNotEmpty ? coin.themeSubject : 'Catalog Coin',
      denomination: coin.denomination,
      composition:
          coin.metalContent.isNotEmpty ? coin.metalContent : 'Not Recorded',
      cpgRetail: coin.cpgRetail > 0 ? coin.cpgRetail : null,
      primaryImageUrl: referenceImageUrl,
      legislationKey: null,
      weightG: null,
      diameterMm: null,
    );
  }

  CoinModel toSyntheticCoinModel() {
    return CoinModel(
      id: nacCode.isNotEmpty ? nacCode : 'public_entry',
      themeSubject: title,
      denomination: denomination,
      metalContent: composition,
      cpgRetail: cpgRetail ?? 0.0,
      imageUrlObverse: primaryImageUrl ?? '',
    );
  }
}

/// Public test-visible view of navigation state.
abstract class UnifiedCoinDetailNavState {
  int? get currentParentIndex;
}

class UnifiedCoinDetailScreen extends StatefulWidget {
  final CoinModel? initialCoin;
  final DocumentSnapshot? initialSnapshot;
  final int? initialParentIndex;
  final List<dynamic> collectionRows;
  final List<QueryDocumentSnapshot<Map<String, dynamic>>> cachedCoinsDocs;
  final PublicCoinProjection? publicProjection;
  final UnifiedCoinDetailDeps? deps;

  const UnifiedCoinDetailScreen({
    super.key,
    CoinModel? coin,
    CoinModel? initialCoin,
    this.initialSnapshot,
    this.initialParentIndex,
    this.collectionRows = const [],
    this.cachedCoinsDocs = const [],
    this.deps,
  })  : initialCoin = initialCoin ?? coin,
        publicProjection = null;

  const UnifiedCoinDetailScreen.public({
    super.key,
    required PublicCoinProjection projection,
    this.deps,
  })  : publicProjection = projection,
        initialCoin = null,
        initialSnapshot = null,
        initialParentIndex = null,
        collectionRows = const [],
        cachedCoinsDocs = const [];

  static Future<void> show(
    BuildContext context, {
    required CoinModel coin,
    DocumentSnapshot? snapshot,
    int? initialParentIndex,
    List<dynamic> collectionRows = const [],
    List<QueryDocumentSnapshot<Map<String, dynamic>>> cachedCoinsDocs = const [],
    required VoidCallback legacyOpen,
  }) async {
    if (!await UnifiedDetailsGate.isEnabled()) {
      legacyOpen();
      return;
    }
    if (!context.mounted) return;
    await showDialog<void>(
      context: context,
      builder: (_) => Dialog(
        child: UnifiedCoinDetailScreen(
          initialCoin: coin,
          initialSnapshot: snapshot,
          initialParentIndex: initialParentIndex,
          collectionRows: collectionRows,
          cachedCoinsDocs: cachedCoinsDocs,
        ),
      ),
    );
  }

  static Future<void> showPublic(
    BuildContext context, {
    required PublicCoinProjection projection,
    required VoidCallback legacyOpen,
  }) async {
    if (!await UnifiedDetailsGate.isEnabled()) {
      legacyOpen();
      return;
    }
    if (!context.mounted) return;
    await showDialog<void>(
      context: context,
      builder: (_) => Dialog(
        child: UnifiedCoinDetailScreen.public(projection: projection),
      ),
    );
  }

  @override
  State<UnifiedCoinDetailScreen> createState() =>
      _UnifiedCoinDetailScreenState();
}

class _UnifiedCoinDetailScreenState extends State<UnifiedCoinDetailScreen>
    implements UnifiedCoinDetailNavState {
  static const Map<String, Map<String, dynamic>> _kCheckedLegislationManifest = {
    '110-456': {
      'title':
          'America’s Beautiful National Parks Quarter Dollar Coin Act of 2008',
      'name':
          'America’s Beautiful National Parks Quarter Dollar Coin Act of 2008',
      'public_law': '110-456',
      'bill_number': 'H.R. 6184',
      'statute_citation': '122 Stat. 5038 (31 U.S.C. § 5112(t))',
      'enacted': 'December 23, 2008',
      'congress': '110th Congress (2007–2008)',
      'congress_url':
          'https://www.congress.gov/bill/110th-congress/house-bill/6184',
    },
    '105-124': {
      'title': '50 States Commemorative Coin Program Act',
      'name': '50 States Commemorative Coin Program Act',
      'public_law': '105-124',
      'bill_number': 'H.R. 2414',
      'statute_citation': '111 Stat. 2534 (31 U.S.C. § 5112(k))',
      'enacted': 'December 1, 1997',
      'congress': '105th Congress (1997–1998)',
      'congress_url':
          'https://www.congress.gov/bill/105th-congress/house-bill/2414',
    },
    '110-161': {
      'title':
          'District of Columbia and United States Territories Circulating Quarter Dollar Program Act',
      'name':
          'Consolidated Appropriations Act, 2008 (Div. D, Title VI, § 622 — DC & Territories Quarters)',
      'public_law': '110-161',
      'bill_number': 'H.R. 2764',
      'statute_citation': '121 Stat. 2014 (31 U.S.C. § 5112(r))',
      'enacted': 'December 26, 2007',
      'congress': '110th Congress (2007–2008)',
      'congress_url':
          'https://www.congress.gov/bill/110th-congress/house-bill/2764',
    },
    '116-330': {
      'title': 'Circulating Collectible Coin Redesign Act of 2020',
      'name':
          'Circulating Collectible Coin Redesign Act of 2020 (American Women Quarters)',
      'public_law': '116-330',
      'bill_number': 'H.R. 1923',
      'statute_citation': '134 Stat. 5101 (31 U.S.C. § 5112(z))',
      'enacted': 'January 13, 2021',
      'congress': '116th Congress (2019–2020)',
      'congress_url':
          'https://www.congress.gov/bill/116th-congress/house-bill/1923',
    },
  };

  late CoinModel? _currentCoin;
  late DocumentSnapshot? _currentSnapshot;
  late int? _currentParentIndex;
  bool _showValues = false;
  bool _showLegislation = false;
  Map<String, dynamic>? _laws;
  Timer? _lawsWatchdog;
  bool _lawsTimedOut = false;

  @override
  @visibleForTesting
  int? get currentParentIndex => _currentParentIndex;

  @visibleForTesting
  DocumentSnapshot? get currentSnapshot => _currentSnapshot;

  late final UnifiedCoinDetailDeps _deps =
      widget.deps ?? UnifiedCoinDetailDeps.production(widget.cachedCoinsDocs);

  DateTime _now() => _deps.clock.now;

  @override
  void initState() {
    super.initState();
    _currentCoin = widget.initialCoin;
    _currentSnapshot = widget.initialSnapshot;
    _currentParentIndex = widget.initialParentIndex;
    _loadCurrentDoc();
  }

  @override
  void dispose() {
    _lawsWatchdog?.cancel();
    super.dispose();
  }

  Future<void> _loadCurrentDoc() async {
    final id = _currentCoin?.id;
    if (id == null || id.isEmpty) return;
    final data = await _deps.store.getDoc('coins', id);
    if (!mounted || data == null) return;
    setState(() => _currentCoin = CoinModel.fromMap(data, id));
  }

  bool get canNavigatePrevious =>
      _currentParentIndex != null && _currentParentIndex! > 0;

  bool get canNavigateNext =>
      _currentParentIndex != null &&
      _currentParentIndex! < widget.collectionRows.length - 1;

  void _stepNavigation(int direction) {
    if (_currentParentIndex == null) return;
    final rows = widget.collectionRows;
    if (rows.isEmpty) return;

    int targetIdx = _currentParentIndex! + direction;

    while (targetIdx >= 0 && targetIdx < rows.length) {
      final targetRow = rows[targetIdx];
      final String targetParentId = targetRow.isVirtualChild == true
          ? (targetRow.parentDocId?.toString() ?? '')
          : (targetRow.id?.toString() ?? '');

      if (targetParentId.isNotEmpty &&
          _currentCoin != null &&
          targetParentId == _currentCoin!.id) {
        targetIdx += direction;
        continue;
      }

      QueryDocumentSnapshot<Map<String, dynamic>>? doc;
      for (final d in widget.cachedCoinsDocs) {
        if (d.id == targetParentId) {
          doc = d;
          break;
        }
      }

      if (doc == null) {
        targetIdx += direction;
        continue;
      }

      final docData = doc.data();
      final nextCoin = CoinModel.fromMap(docData, doc.id);
      final parentIndex = resolveParentIndex(rows, targetParentId);

      _lawsWatchdog?.cancel();
      setState(() {
        _currentCoin = nextCoin;
        _currentSnapshot = doc;
        _currentParentIndex = parentIndex;
        _showLegislation = false;
        _laws = null;
        _lawsTimedOut = false;
      });
      return;
    }
  }

  String? _matchLawKey(CoinModel coin) {
    final series = coin.programSeries.toLowerCase();
    final denom = coin.denomination.toLowerCase();
    final theme = coin.themeSubject.toLowerCase();

    if (series.contains('state quarter') ||
        series.contains('50 state') ||
        series.contains('statehood quarter')) {
      return '105-124';
    }
    if ((series.contains('america') && series.contains('beautiful')) ||
        series.contains('atb') ||
        series.contains('national park')) {
      return '110-456';
    }
    if (series.contains('territor') ||
        series.contains('district of columbia') ||
        series.contains('dc &') ||
        series.contains('dc and')) {
      return '110-161';
    }
    if (series.contains('women quarter') || series.contains('american women')) {
      return '116-330';
    }
    if (series.contains('presidential dollar') ||
        series.contains('president dollar')) {
      return '109-145';
    }
    if (series.contains('silver eagle') ||
        series.contains('american silver eagle') ||
        series.contains('gold eagle')) {
      return '99-61';
    }
    if (series.contains('susan b') || series.contains('anthony')) {
      return '95-447';
    }
    if (series.contains('eisenhower')) return '91-607';
    if (series.contains('march of dimes') || theme.contains('march of dimes')) {
      return '112-209';
    }
    if (series.contains('sacagawea') ||
        series.contains('native american dollar')) {
      return '106-445';
    }
    if (denom.contains('half dollar') ||
        denom.contains('quarter') ||
        denom.contains('dime')) {
      return '89-81';
    }
    return null;
  }

  Future<void> _fetchLawsOnline(String key) async {
    final deadline = _now().add(const Duration(milliseconds: 4000));
    _lawsWatchdog?.cancel();
    _lawsWatchdog = Timer.periodic(const Duration(milliseconds: 250), (t) {
      if (_now().isAfter(deadline)) {
        t.cancel();
        if (mounted) setState(() => _lawsTimedOut = true);
      }
    });
    final fetch = _deps.lawsFetcher;
    if (fetch == null) {
      _lawsWatchdog?.cancel();
      return;
    }
    final result = await fetch(key);
    if (!mounted || _lawsTimedOut) return;
    _lawsWatchdog?.cancel();
    setState(() => _laws = result);
  }

  String? _selectHeroImageUrl(CoinModel? coin) {
    if (widget.publicProjection != null) {
      final url = widget.publicProjection!.primaryImageUrl;
      if (url != null &&
          (PublicCoinProjection.isApprovedCatalogHostUrl(url) ||
              isOwnedStorageUrl(url))) {
        return url;
      }
      return null;
    }
    final obv = coin?.imageUrlObverse ?? '';
    return isOwnedStorageUrl(obv) ? obv : null;
  }

  void _openLegislationTab(CoinModel? coin) {
    setState(() {
      _showLegislation = true;
      _lawsTimedOut = false;
      _laws = null;
    });
    final key = widget.publicProjection?.legislationKey ??
        (coin != null ? _matchLawKey(coin) : null);
    if (key != null && _kCheckedLegislationManifest.containsKey(key)) {
      setState(() => _laws = _kCheckedLegislationManifest[key]);
      return;
    }
    _fetchLawsOnline(key ?? 'unlisted');
  }

  void _launchEbaySearch(CoinModel coin) {
    final query = Uri.encodeComponent('${coin.year} ${coin.themeSubject}'.trim());
    final url = 'https://www.ebay.com/sch/i.html?_nkw=$query';
    _deps.onLaunchUrl?.call(url);
  }

  Widget _buildHeroPlaceholder() => const Icon(
        Icons.monetization_on_outlined,
        key: Key('hero_coin_placeholder'),
        size: 64,
      );

  @override
  Widget build(BuildContext context) {
    final isPublic = widget.publicProjection != null;
    final coin = _currentCoin ?? widget.publicProjection?.toSyntheticCoinModel();
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final headerBg = isDark ? const Color(0xFF0F172A) : const Color(0xFF0B1A2E);
    final headerFg = isDark ? const Color(0xFFF8FAFC) : Colors.white;
    final heroUrl = _selectHeroImageUrl(coin);

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          key: const Key('udv_header_surface'),
          decoration: BoxDecoration(color: headerBg),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          child: Row(
            children: [
              Expanded(
                child: Text(
                  coin?.themeSubject ?? '',
                  key: const Key('udv_header_title'),
                  style: TextStyle(
                    color: headerFg,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              if (canNavigateNext)
                IconButton(
                  icon: const Icon(Icons.arrow_forward_ios, color: Colors.white),
                  onPressed: () => _stepNavigation(1),
                ),
            ],
          ),
        ),
        if (heroUrl != null)
          Builder(builder: (_) {
            _deps.onImageLoad?.call(heroUrl);
            return Image.network(
              heroUrl,
              key: const Key('hero_coin_image'),
              errorBuilder: (_, _, _) => _buildHeroPlaceholder(),
            );
          })
        else
          _buildHeroPlaceholder(),
        Text((coin?.metalContent.isNotEmpty ?? false)
            ? coin!.metalContent
            : 'Not Recorded'),
        TextButton(
          onPressed: () => setState(() => _showValues = !_showValues),
          child: const Text('Show values'),
        ),
        if (_showValues && coin != null) ...[
          if (coin.cpgRetail > 0)
            Text('\$${coin.cpgRetail.toStringAsFixed(2)}'),
          if (!isPublic && coin.purchaseCost.isNotEmpty)
            Text(
              '\$${(double.tryParse(coin.purchaseCost.replaceAll(r'$', '')) ?? 0.0).toStringAsFixed(2)}',
            ),
        ],
        if (!isPublic) ...[
          if (coin?.storageLocation.isNotEmpty ?? false)
            Text(coin!.storageLocation),
          if (coin?.personalNotes.isNotEmpty ?? false)
            MarkdownBody(
              data: sanitizeNotesText(coin!.personalNotes),
              styleSheet: getSandboxedMarkdownStyleSheet(context),
              imageBuilder: (_, _, _) => const SizedBox.shrink(),
              onTapLink: (_, _, _) {},
            ),
          ElevatedButton(
            key: const Key('ebay_search_button'),
            onPressed: () => _launchEbaySearch(coin!),
            child: const Text('Search eBay'),
          ),
        ],
        TextButton(
          onPressed: () => _openLegislationTab(coin),
          child: const Text('Legislation'),
        ),
        if (_showLegislation) ...[
          if (_laws != null) ...[
            if ((_laws!['title']?.toString() ?? '').isNotEmpty)
              Text(_laws!['title'].toString()),
            if ((_laws!['statute_citation']?.toString() ?? '').isNotEmpty)
              Text(_laws!['statute_citation'].toString()),
          ] else if (_lawsTimedOut) ...[
            const Text('Founding legislation details pending verification.'),
          ],
        ],
      ],
    );
  }
}
