import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/upcoming_releases_service.dart';

class UpcomingReleasesScreen extends StatefulWidget {
  const UpcomingReleasesScreen({super.key});

  @override
  State<UpcomingReleasesScreen> createState() => _UpcomingReleasesScreenState();
}

class _UpcomingReleasesScreenState extends State<UpcomingReleasesScreen> {
  List<UpcomingRelease> _allReleases = [];
  List<UpcomingRelease> _filteredReleases = [];
  bool _isLoading = true;
  String _selectedFilter = 'All';
  String _selectedSort = 'By Release Date';

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    final data = await UpcomingReleasesService.fetchAll();
    setState(() {
      _allReleases = data;
      _applyFilterAndSort();
      _isLoading = false;
    });
  }

  void _applyFilterAndSort() {
    List<UpcomingRelease> result = List.from(_allReleases);

    if (_selectedFilter != 'All') {
      result = result.where((r) => r.status == _selectedFilter).toList();
    }

    if (_selectedSort == 'By Price') {
      result.sort((a, b) {
        final pa = double.tryParse(a.price.replaceAll(RegExp(r'[^0-9.]'), '')) ?? 0.0;
        final pb = double.tryParse(b.price.replaceAll(RegExp(r'[^0-9.]'), '')) ?? 0.0;
        return pb.compareTo(pa);
      });
    } else if (_selectedSort == 'By Program') {
      result.sort((a, b) => a.program.compareTo(b.program));
    } else {
      // By Release Date - simple string fallback for now
      result.sort((a, b) => a.releaseDate.compareTo(b.releaseDate));
    }

    setState(() {
      _filteredReleases = result;
    });
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'Available':
        return Colors.green;
      case 'Coming Soon':
        return Colors.amber;
      case 'Pre-Order':
        return Colors.blue;
      case 'Sold Out':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bg = isDark ? const Color(0xFF0E1117) : const Color(0xFFF4F4F2);
    final surface = isDark ? const Color(0xFF1E2937) : Colors.white;
    final textCol = isDark ? const Color(0xFFE8EAF0) : const Color(0xFF0F172A);
    final accent = const Color(0xFFF63366);

    return Scaffold(
      backgroundColor: bg,
      appBar: AppBar(
        title: const Text('Upcoming US Mint Releases'),
        backgroundColor: surface,
        foregroundColor: textCol,
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.sort),
            onSelected: (val) {
              setState(() => _selectedSort = val);
              _applyFilterAndSort();
            },
            itemBuilder: (context) => [
              'By Release Date',
              'By Price',
              'By Program'
            ].map((s) => PopupMenuItem(value: s, child: Text(s))).toList(),
          )
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : Column(
                children: [
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.all(8),
                    child: Row(
                      children: ['All', 'Coming Soon', 'Available', 'Sold Out']
                          .map((f) => Padding(
                                padding: const EdgeInsets.symmetric(horizontal: 4),
                                child: ChoiceChip(
                                  label: Text(f),
                                  selected: _selectedFilter == f,
                                  onSelected: (sel) {
                                    if (sel) {
                                      setState(() => _selectedFilter = f);
                                      _applyFilterAndSort();
                                    }
                                  },
                                  selectedColor: accent.withValues(alpha: 0.2),
                                ),
                              ))
                          .toList(),
                    ),
                  ),
                  if (_filteredReleases.isNotEmpty && _selectedFilter == 'All') ...[
                    _buildHeroCard(_filteredReleases.first, surface, textCol),
                  ],
                  Expanded(
                    child: ListView.builder(
                      itemCount: _selectedFilter == 'All' && _filteredReleases.isNotEmpty
                          ? _filteredReleases.length - 1
                          : _filteredReleases.length,
                      itemBuilder: (context, i) {
                        final release = _selectedFilter == 'All'
                            ? _filteredReleases[i + 1]
                            : _filteredReleases[i];
                        return _buildProductCard(release, surface, textCol, isDark);
                      },
                    ),
                  )
                ],
              ),
      ),
    );
  }

  Widget _buildHeroCard(UpcomingRelease release, Color surface, Color textCol) {
    return Card(
      margin: const EdgeInsets.all(16),
      color: surface,
      child: InkWell(
        onTap: () => launchUrl(Uri.parse(release.productUrl)),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (release.imageUrl != null)
              CachedNetworkImage(
                imageUrl: release.imageUrl!,
                height: 200,
                fit: BoxFit.cover,
                errorWidget: (c, u, e) => const Icon(Icons.image_not_supported, size: 50),
              )
            else
              Container(
                height: 200,
                color: Colors.grey.withValues(alpha: 0.2),
                child: const Icon(Icons.image_not_supported, size: 50),
              ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('NEXT RELEASE', style: TextStyle(color: const Color(0xFFF63366), fontWeight: FontWeight.bold, fontSize: 12)),
                      _buildBadge(release.status),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(release.title, style: TextStyle(color: textCol, fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  Text('${release.releaseDate} • ${release.price}', style: const TextStyle(color: Colors.grey)),
                ],
              ),
            )
          ],
        ),
      ),
    );
  }

  Widget _buildProductCard(UpcomingRelease release, Color surface, Color textCol, bool isDark) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: surface,
      child: ListTile(
        onTap: () => launchUrl(Uri.parse(release.productUrl)),
        leading: release.imageUrl != null
            ? CachedNetworkImage(
                imageUrl: release.imageUrl!,
                width: 50,
                height: 50,
                fit: BoxFit.cover,
                errorWidget: (c, u, e) => const Icon(Icons.image_not_supported),
              )
            : const Icon(Icons.image_not_supported),
        title: Text(release.title, style: TextStyle(color: textCol, fontWeight: FontWeight.bold)),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('${release.program} • ${release.price}', style: TextStyle(color: isDark ? Colors.grey[400] : Colors.grey[700])),
            if (release.mintageLimit != null)
              Text('Mintage: ${release.mintageLimit}', style: const TextStyle(fontSize: 12)),
          ],
        ),
        trailing: _buildBadge(release.status),
      ),
    );
  }

  Widget _buildBadge(String status) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: _getStatusColor(status).withValues(alpha: 0.2),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _getStatusColor(status)),
      ),
      child: Text(
        status,
        style: TextStyle(color: _getStatusColor(status), fontSize: 12, fontWeight: FontWeight.bold),
      ),
    );
  }
}
