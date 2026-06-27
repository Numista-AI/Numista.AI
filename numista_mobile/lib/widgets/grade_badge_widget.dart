import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:cached_network_image/cached_network_image.dart';
import '../constants.dart';

class GradeBadgeWidget extends StatelessWidget {
  final String gradeCode;
  final VoidCallback? onTap;

  const GradeBadgeWidget({
    super.key,
    required this.gradeCode,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    if (gradeCode.isEmpty) return const SizedBox.shrink();

    final colors = _getBadgeColors(gradeCode);
    return GestureDetector(
      onTap: onTap ?? () => _showGradeDetails(context),
      child: MouseRegion(
        cursor: SystemMouseCursors.click,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(
            color: colors.backgroundColor,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: colors.borderColor, width: 1),
            boxShadow: [
              BoxShadow(
                color: colors.textColor.withAlpha(10),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Text(
            gradeCode,
            style: TextStyle(
              color: colors.textColor,
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 0.5,
            ),
          ),
        ),
      ),
    );
  }

  void _showGradeDetails(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _GradeDetailsSheet(gradeCode: gradeCode),
    );
  }

  _BadgeColors _getBadgeColors(String code) {
    final clean = code.toUpperCase().trim();
    if (clean.startsWith('MS') || clean.startsWith('PF') || clean.startsWith('PR')) {
      // Uncirculated / Proof — Gold
      return const _BadgeColors(
        backgroundColor: Color(0xFFFEF3C7),
        borderColor: Color(0xFFF59E0B),
        textColor: Color(0xFFB45309),
      );
    } else if (clean.startsWith('AU')) {
      // About Uncirculated — Blue
      return const _BadgeColors(
        backgroundColor: Color(0xFFDBEAFE),
        borderColor: Color(0xFF3B82F6),
        textColor: Color(0xFF1D4ED8),
      );
    } else if (clean.startsWith('XF') || clean.startsWith('EF')) {
      // Extremely Fine — Green
      return const _BadgeColors(
        backgroundColor: Color(0xFFD1FAE5),
        borderColor: Color(0xFF10B981),
        textColor: Color(0xFF047857),
      );
    } else if (clean.startsWith('VF')) {
      // Very Fine — Purple
      return const _BadgeColors(
        backgroundColor: Color(0xFFF3E8FF),
        borderColor: Color(0xFF8B5CF6),
        textColor: Color(0xFF6D28D9),
      );
    } else if (clean.startsWith('F')) {
      // Fine — Orange
      return const _BadgeColors(
        backgroundColor: Color(0xFFFFEDD5),
        borderColor: Color(0xFFF97316),
        textColor: Color(0xFFC2410C),
      );
    } else {
      // Slate/Grey for circulated/lower grades (VG, G, AG, FR, P)
      return const _BadgeColors(
        backgroundColor: Color(0xFFF1F5F9),
        borderColor: Color(0xFF94A3B8),
        textColor: Color(0xFF475569),
      );
    }
  }
}

class _BadgeColors {
  final Color backgroundColor;
  final Color borderColor;
  final Color textColor;

  const _BadgeColors({
    required this.backgroundColor,
    required this.borderColor,
    required this.textColor,
  });
}

class _GradeDetailsSheet extends StatefulWidget {
  final String gradeCode;
  const _GradeDetailsSheet({required this.gradeCode});

  @override
  State<_GradeDetailsSheet> createState() => _GradeDetailsSheetState();
}

class _GradeDetailsSheetState extends State<_GradeDetailsSheet> {
  bool _loading = true;
  String? _error;
  Map<String, dynamic>? _gradeData;

  @override
  void initState() {
    super.initState();
    _fetchDetails();
  }

  Future<void> _fetchDetails() async {
    try {
      final code = Uri.encodeComponent(widget.gradeCode);
      final response = await http.get(Uri.parse('$kApiBaseUrl/api/reference/grade/$code'));
      if (response.statusCode == 200) {
        if (mounted) {
          setState(() {
            _gradeData = json.decode(response.body);
            _loading = false;
          });
        }
      } else {
        if (mounted) {
          setState(() {
            _error = 'Failed to fetch details: Status ${response.statusCode}';
            _loading = false;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = 'Failed to connect to server: $e';
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final double sheetHeight = MediaQuery.of(context).size.height * 0.85;

    return Container(
      height: sheetHeight,
      decoration: const BoxDecoration(
        color: Color(0xFF0E1117), // Premium Dark Mode Background
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(24),
          topRight: Radius.circular(24),
        ),
      ),
      child: Column(
        children: [
          // Indicator bar
          Container(
            margin: const EdgeInsets.only(top: 12, bottom: 8),
            width: 40,
            height: 4,
            decoration: BoxDecoration(
              color: Colors.white24,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          // Title area
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Sheldon Grade Guide',
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close, color: Colors.white54),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ],
            ),
          ),
          const Divider(color: Colors.white12, height: 1),
          // Content
          Expanded(
            child: _buildContent(),
          ),
        ],
      ),
    );
  }

  Widget _buildContent() {
    if (_loading) {
      return const Center(
        child: CircularProgressIndicator(
          color: Color(0xFFF63366),
        ),
      );
    }

    if (_error != null) {
      return Padding(
        padding: const EdgeInsets.all(24),
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline_rounded, color: Colors.redAccent, size: 48),
              const SizedBox(height: 16),
              Text(
                _error!,
                textAlign: TextAlign.center,
                style: const TextStyle(color: Colors.white70, fontSize: 14),
              ),
            ],
          ),
        ),
      );
    }

    final data = _gradeData!;
    final gradeCode = data['grade_code'] ?? widget.gradeCode;
    final gradeName = data['grade_name'] ?? 'Unknown Grade';
    final minScore = data['min_score'] ?? 0;
    final maxScore = data['max_score'] ?? 0;
    final wearDesc = data['wear_description'] ?? 'No wear details available.';
    final lusterDesc = data['luster_description'] ?? 'No luster details available.';
    final inspectionTips = data['inspection_tips'] ?? 'No inspection tips available.';
    final imgUrl = data['illustration_url'] as String?;

    final scoreStr = minScore == maxScore ? '$minScore' : '$minScore - $maxScore';

    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header card
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF1E293B), Color(0xFF0F172A)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.white10),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      gradeCode,
                      style: const TextStyle(
                        color: Color(0xFFF63366),
                        fontSize: 32,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.white10,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        'Sheldon Score: $scoreStr',
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  gradeName,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Wear description
          _SectionTitle(title: 'Wear & Preservation'),
          Text(
            wearDesc,
            style: const TextStyle(color: Colors.white, fontSize: 14, height: 1.5),
          ),
          const SizedBox(height: 20),

          // Luster description
          _SectionTitle(title: 'Surface Luster'),
          Text(
            lusterDesc,
            style: const TextStyle(color: Colors.white, fontSize: 14, height: 1.5),
          ),
          const SizedBox(height: 20),

          // Inspection tips
          _SectionTitle(title: 'How to Inspect & Spot'),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.yellow.withAlpha(12),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.yellow.withAlpha(40)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.tips_and_updates_outlined, color: Colors.amberAccent, size: 20),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    inspectionTips,
                    style: const TextStyle(
                      color: Color(0xFFFCD34D),
                      fontSize: 13,
                      height: 1.5,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Reference image
          if (imgUrl != null && imgUrl.isNotEmpty) ...[
            _SectionTitle(title: 'Visual Grading Guide'),
            Container(
              width: double.infinity,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.white12),
                color: Colors.white.withAlpha(5),
              ),
              clipBehavior: Clip.antiAlias,
              child: CachedNetworkImage(
                imageUrl: imgUrl,
                fit: BoxFit.contain,
                placeholder: (context, url) => const SizedBox(
                  height: 180,
                  child: Center(
                    child: CircularProgressIndicator(color: Color(0xFFF63366)),
                  ),
                ),
                errorWidget: (context, url, error) => const SizedBox(
                  height: 100,
                  child: Center(
                    child: Text(
                      'Failed to load illustration.',
                      style: TextStyle(color: Colors.white30, fontSize: 12),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  final String title;
  const _SectionTitle({required this.title});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        title.toUpperCase(),
        style: const TextStyle(
          color: Colors.white38,
          fontSize: 11,
          fontWeight: FontWeight.bold,
          letterSpacing: 1.2,
        ),
      ),
    );
  }
}
