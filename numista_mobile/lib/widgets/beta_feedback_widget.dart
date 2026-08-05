import 'dart:ui' as ui;
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import '../services/auth_service.dart';
import '../services/beta_feedback_service.dart';

class BetaFeedbackWidget extends StatefulWidget {
  final String currentRoute;
  final String pageTitle;
  final GlobalKey? repaintKey;

  const BetaFeedbackWidget({
    super.key,
    required this.currentRoute,
    required this.pageTitle,
    this.repaintKey,
  });

  @override
  State<BetaFeedbackWidget> createState() => _BetaFeedbackWidgetState();
}

class _BetaFeedbackWidgetState extends State<BetaFeedbackWidget> {
  bool _isSubmitting = false;
  Uint8List? _capturedScreenshot;
  String _selectedCategory = 'UI / Layout Suggestion';
  int _easeOfUse = 5;
  int _accuracyRating = 5;
  int _aestheticsRating = 5;
  int _satisfactionRating = 5;
  int _utilityRating = 5;
  final TextEditingController _commentController = TextEditingController();

  final List<String> _categories = [
    'UI / Layout Suggestion',
    'Bug Report',
    'Confusing / Hard to Use',
    'Feature Request',
    'Praise / What Works Well',
  ];

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  Future<void> _captureScreen() async {
    try {
      if (widget.repaintKey?.currentContext != null) {
        final boundary = widget.repaintKey!.currentContext!
            .findRenderObject() as RenderRepaintBoundary?;
        if (boundary != null) {
          final image = await boundary.toImage(pixelRatio: 1.5);
          final byteData =
              await image.toByteData(format: ui.ImageByteFormat.png);
          if (byteData != null) {
            setState(() {
              _capturedScreenshot = byteData.buffer.asUint8List();
            });
          }
        }
      }
    } catch (e) {
      debugPrint('Screenshot capture failed: $e');
    }
  }

  Future<void> _openFeedbackModal(BuildContext context) async {
    // Auto capture current screen state before launching bottom sheet overlay
    await _captureScreen();

    if (!context.mounted) return;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) {
        return StatefulBuilder(
          builder: (modalCtx, setModalState) {
            final mediaQuery = MediaQuery.of(modalCtx);
            final viewportRes =
                '${mediaQuery.size.width.toInt()}x${mediaQuery.size.height.toInt()}';

            return Container(
              margin: EdgeInsets.only(
                top: 60,
                left: 16,
                right: 16,
                bottom: mediaQuery.viewInsets.bottom + 16,
              ),
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: const Color(0xFF1E293B),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.blueAccent.withValues(alpha: 0.3)),
                boxShadow: const [
                  BoxShadow(
                    color: Colors.black45,
                    blurRadius: 20,
                    offset: Offset(0, 10),
                  ),
                ],
              ),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: Colors.blueAccent.withValues(alpha: 0.2),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: const Icon(Icons.rate_review,
                                  color: Colors.blueAccent, size: 24),
                            ),
                            const SizedBox(width: 12),
                            Text(
                              'Beta Tester Feedback',
                              style: Theme.of(modalCtx)
                                  .textTheme
                                  .titleLarge
                                  ?.copyWith(
                                    color: Colors.white,
                                    fontWeight: FontWeight.bold,
                                  ),
                            ),
                          ],
                        ),
                        IconButton(
                          icon: const Icon(Icons.close, color: Colors.grey),
                          onPressed: () => Navigator.of(modalCtx).pop(),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),

                    // Context Chip
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.08),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.location_on,
                              size: 14, color: Colors.blueAccent),
                          const SizedBox(width: 6),
                          Text(
                            'Page: ${widget.pageTitle} (${widget.currentRoute})',
                            style: const TextStyle(
                                color: Colors.grey, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Category Selector
                    const Text(
                      'Feedback Category',
                      style: TextStyle(
                          color: Colors.white, fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 6),
                    DropdownButtonFormField<String>(
                      value: _selectedCategory,
                      dropdownColor: const Color(0xFF0F172A),
                      style: const TextStyle(color: Colors.white),
                      decoration: InputDecoration(
                        filled: true,
                        fillColor: Colors.black26,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                          borderSide: BorderSide.none,
                        ),
                      ),
                      items: _categories.map((cat) {
                        return DropdownMenuItem(
                          value: cat,
                          child: Text(cat),
                        );
                      }).toList(),
                      onChanged: (val) {
                        if (val != null) {
                          setModalState(() => _selectedCategory = val);
                        }
                      },
                    ),
                    const SizedBox(height: 16),

                    // Ratings Sliders (5 Tailored Dimensions)
                    _buildStarRatingRow(
                      label: 'Ease of Use',
                      rating: _easeOfUse,
                      onChanged: (r) => setModalState(() => _easeOfUse = r),
                    ),
                    const SizedBox(height: 8),
                    _buildStarRatingRow(
                      label: 'AI Accuracy & Speed',
                      rating: _accuracyRating,
                      onChanged: (r) => setModalState(() => _accuracyRating = r),
                    ),
                    const SizedBox(height: 8),
                    _buildStarRatingRow(
                      label: 'Design & Visual Aesthetics',
                      rating: _aestheticsRating,
                      onChanged: (r) => setModalState(() => _aestheticsRating = r),
                    ),
                    const SizedBox(height: 8),
                    _buildStarRatingRow(
                      label: 'Overall Satisfaction',
                      rating: _satisfactionRating,
                      onChanged: (r) => setModalState(() => _satisfactionRating = r),
                    ),
                    const SizedBox(height: 8),
                    _buildStarRatingRow(
                      label: 'Utility & Value',
                      rating: _utilityRating,
                      onChanged: (r) => setModalState(() => _utilityRating = r),
                    ),
                    const SizedBox(height: 16),

                    // Comment Input
                    const Text(
                      'Your Comments & Suggestions',
                      style: TextStyle(
                          color: Colors.white, fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 6),
                    TextField(
                      controller: _commentController,
                      maxLines: 3,
                      style: const TextStyle(color: Colors.white),
                      decoration: InputDecoration(
                        hintText:
                            'Describe what worked well or what was confusing...',
                        hintStyle: const TextStyle(color: Colors.grey),
                        filled: true,
                        fillColor: Colors.black26,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                          borderSide: BorderSide.none,
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Screenshot Capture & File Attachment Button
                    Row(
                      children: [
                        OutlinedButton.icon(
                          onPressed: () async {
                            if (_capturedScreenshot == null) {
                              await _captureScreen();
                            }
                            if (_capturedScreenshot == null) {
                              try {
                                final result = await FilePicker.pickFiles(
                                  type: FileType.image,
                                  withData: true,
                                );
                                if (result != null && result.files.isNotEmpty) {
                                  final bytes = result.files.first.bytes;
                                  if (bytes != null) {
                                    if (bytes.length > 8 * 1024 * 1024) {
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        const SnackBar(
                                          content: Text('Screenshot file exceeds 8 MB limit.'),
                                          backgroundColor: Colors.amber,
                                        ),
                                      );
                                    } else {
                                      _capturedScreenshot = bytes;
                                    }
                                  }
                                }
                              } catch (e) {
                                debugPrint('FilePicker error: $e');
                              }
                            }
                            setModalState(() {});
                          },
                          icon: Icon(
                            _capturedScreenshot != null
                                ? Icons.check_circle
                                : Icons.camera_alt,
                            color: _capturedScreenshot != null
                                ? Colors.green
                                : Colors.blueAccent,
                          ),
                          label: Text(
                            _capturedScreenshot != null
                                ? 'Screenshot Attached (${(_capturedScreenshot!.length / 1024).toStringAsFixed(0)} KB)'
                                : 'Attach Screenshot',
                            style: TextStyle(
                              color: _capturedScreenshot != null
                                  ? Colors.green
                                  : Colors.blueAccent,
                            ),
                          ),
                          style: OutlinedButton.styleFrom(
                            side: BorderSide(
                              color: _capturedScreenshot != null
                                  ? Colors.green
                                  : Colors.blueAccent,
                            ),
                          ),
                        ),
                        if (_capturedScreenshot != null) ...[
                          const SizedBox(width: 8),
                          IconButton(
                            icon: const Icon(Icons.delete_outline, color: Colors.redAccent, size: 20),
                            tooltip: 'Remove Screenshot',
                            onPressed: () {
                              setModalState(() {
                                _capturedScreenshot = null;
                              });
                            },
                          ),
                        ],
                      ],
                    ),
                    const SizedBox(height: 20),

                    // Submit Button
                    SizedBox(
                      width: double.infinity,
                      height: 48,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blueAccent,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        onPressed: _isSubmitting
                            ? null
                            : () async {
                                setModalState(() => _isSubmitting = true);
                                final payload = BetaFeedbackPayload(
                                  route: widget.currentRoute,
                                  pageTitle: widget.pageTitle,
                                  category: _selectedCategory,
                                  easeOfUseRating: _easeOfUse,
                                  accuracyRating: _accuracyRating,
                                  aestheticsRating: _aestheticsRating,
                                  satisfactionRating: _satisfactionRating,
                                  utilityRating: _utilityRating,
                                  comment: _commentController.text.trim(),
                                  screenshotBytes: _capturedScreenshot,
                                  viewportResolution: viewportRes,
                                );

                                final success =
                                    await BetaFeedbackService.submitFeedback(
                                        payload);

                                setModalState(() => _isSubmitting = false);

                                if (modalCtx.mounted) {
                                  Navigator.of(modalCtx).pop();
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      backgroundColor: success
                                          ? Colors.green
                                          : Colors.redAccent,
                                      content: Text(success
                                          ? 'Thank you! Beta feedback submitted successfully.'
                                          : 'Failed to submit feedback. Please try again.'),
                                    ),
                                  );
                                  if (success) {
                                    _commentController.clear();
                                    _capturedScreenshot = null;
                                  }
                                }
                              },
                        child: _isSubmitting
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  valueColor: AlwaysStoppedAnimation<Color>(
                                      Colors.white),
                                ),
                              )
                            : const Text(
                                'Submit Beta Feedback',
                                style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildStarRatingRow({
    required String label,
    required int rating,
    required ValueChanged<int> onChanged,
  }) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(color: Colors.grey, fontSize: 13),
        ),
        Row(
          children: List.generate(5, (index) {
            final starIndex = index + 1;
            return IconButton(
              iconSize: 20,
              padding: EdgeInsets.zero,
              constraints: const BoxConstraints(),
              icon: Icon(
                starIndex <= rating ? Icons.star : Icons.star_border,
                color: Colors.amber,
              ),
              onPressed: () => onChanged(starIndex),
            );
          }),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    // Only render for beta testers or guest mode
    if (!AuthService.isBetaTester && !AuthService.isGuest) {
      return const SizedBox.shrink();
    }

    return Positioned(
      bottom: 90,
      right: 24,
      child: Material(
        color: Colors.transparent,
        child: FloatingActionButton.extended(
          heroTag: 'beta_feedback_fab',
          backgroundColor: const Color(0xFF2563EB),
          elevation: 8,
          icon: const Icon(Icons.rate_review_outlined, color: Colors.white),
          label: const Text(
            'Feedback',
            style: TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              letterSpacing: 0.5,
            ),
          ),
          onPressed: () => _openFeedbackModal(context),
        ),
      ),
    );
  }
}
