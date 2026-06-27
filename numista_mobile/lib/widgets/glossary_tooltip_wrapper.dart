import 'dart:convert';
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../constants.dart';

class GlossaryTooltipWrapper extends StatefulWidget {
  final String text;
  final TextStyle? style;
  final TextStyle? linkStyle;

  const GlossaryTooltipWrapper({
    super.key,
    required this.text,
    this.style,
    this.linkStyle,
  });

  @override
  State<GlossaryTooltipWrapper> createState() => _GlossaryTooltipWrapperState();
}

class _GlossaryTooltipWrapperState extends State<GlossaryTooltipWrapper> {
  static List<Map<String, dynamic>>? _cachedGlossary;
  static bool _loading = false;
  static final List<VoidCallback> _pendingCallbacks = [];

  bool _isInitLoaded = false;
  OverlayEntry? _overlayEntry;

  @override
  void initState() {
    super.initState();
    _loadGlossaryData();
  }

  @override
  void dispose() {
    _hideTooltip();
    super.dispose();
  }

  void _loadGlossaryData() async {
    if (_cachedGlossary != null) {
      if (mounted) {
        setState(() {
          _isInitLoaded = true;
        });
      }
      return;
    }

    if (_loading) {
      _pendingCallbacks.add(() {
        if (mounted) {
          setState(() {
            _isInitLoaded = true;
          });
        }
      });
      return;
    }

    _loading = true;
    try {
      final response = await http.get(Uri.parse('$kApiBaseUrl/api/reference/glossary'));
      if (response.statusCode == 200) {
        _cachedGlossary = List<Map<String, dynamic>>.from(json.decode(response.body));
      }
    } catch (e) {
      debugPrint('Error fetching glossary for tooltips: $e');
    } finally {
      _loading = false;
      for (final callback in _pendingCallbacks) {
        callback();
      }
      _pendingCallbacks.clear();
      if (mounted) {
        setState(() {
          _isInitLoaded = true;
        });
      }
    }
  }

  void _showTooltip(BuildContext context, TapDownDetails details, String term, String definition) {
    _hideTooltip();

    final overlay = Overlay.of(context);
    final tapPosition = details.globalPosition;

    _overlayEntry = OverlayEntry(
      builder: (context) {
        return Stack(
          children: [
            // Full screen dismisser
            Positioned.fill(
              child: GestureDetector(
                behavior: HitTestBehavior.translucent,
                onTap: _hideTooltip,
                child: const SizedBox.shrink(),
              ),
            ),
            // Tooltip box positioned near tap location
            Positioned(
              left: (tapPosition.dx - 125).clamp(10.0, MediaQuery.of(context).size.width - 260.0),
              top: tapPosition.dy > MediaQuery.of(context).size.height * 0.6
                  ? tapPosition.dy - 120 // Show above tap
                  : tapPosition.dy + 15, // Show below tap
              child: Material(
                color: Colors.transparent,
                child: Container(
                  width: 250,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E293B),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: const Color(0xFF334155), width: 1),
                    boxShadow: const [
                      BoxShadow(
                        color: Colors.black45,
                        blurRadius: 8,
                        offset: Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        term,
                        style: const TextStyle(
                          color: Color(0xFFF63366),
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        definition,
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 12,
                          height: 1.4,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        );
      },
    );

    overlay.insert(_overlayEntry!);
  }

  void _hideTooltip() {
    _overlayEntry?.remove();
    _overlayEntry = null;
  }

  @override
  Widget build(BuildContext context) {
    if (!_isInitLoaded || _cachedGlossary == null || _cachedGlossary!.isEmpty) {
      return Text(widget.text, style: widget.style);
    }

    return RichText(
      text: TextSpan(
        style: widget.style ?? DefaultTextStyle.of(context).style,
        children: _parseText(widget.text),
      ),
    );
  }

  List<TextSpan> _parseText(String rawText) {
    final spans = <TextSpan>[];
    if (rawText.isEmpty) return spans;

    // Create a regular expression matching all glossary terms and mappings
    final termsPatternMap = <String, Map<String, dynamic>>{};
    final patternParts = <String>[];

    for (final item in _cachedGlossary!) {
      final termName = item['term'] as String;
      final definition = item['definition'] as String;
      final mappings = List<String>.from(item['colloquial_mappings'] ?? []);
      
      final allWords = [termName, ...mappings].map((w) => RegExp.escape(w)).toList();
      final wordPattern = '\\b(${allWords.join('|')})\\b';
      
      patternParts.add(wordPattern);
      
      // Map pattern part back to glossary data
      for (final word in [termName, ...mappings]) {
        termsPatternMap[word.toLowerCase()] = {
          'term': termName,
          'definition': definition,
        };
      }
    }

    if (patternParts.isEmpty) {
      return [TextSpan(text: rawText)];
    }

    // Combined regex for all terms
    final regex = RegExp(patternParts.join('|'), caseSensitive: false);
    
    int lastIndex = 0;
    
    for (final match in regex.allMatches(rawText)) {
      // Add plain text before match
      if (match.start > lastIndex) {
        spans.add(TextSpan(text: rawText.substring(lastIndex, match.start)));
      }

      final matchedText = match.group(0)!;
      final matchedKey = matchedText.toLowerCase();
      final termData = termsPatternMap[matchedKey];

      if (termData != null) {
        final String term = termData['term'];
        final String definition = termData['definition'];
        
        final tapRecognizer = TapGestureRecognizer();
        // Use a customized tap down recognizer to get global position
        tapRecognizer.onTapDown = (details) {
          _showTooltip(context, details, term, definition);
        };

        spans.add(
          TextSpan(
            text: matchedText,
            style: widget.linkStyle ??
                const TextStyle(
                  color: Color(0xFFF63366),
                  decoration: TextDecoration.underline,
                  decorationStyle: TextDecorationStyle.dashed,
                  fontWeight: FontWeight.w500,
                ),
            recognizer: tapRecognizer,
          ),
        );
      } else {
        spans.add(TextSpan(text: matchedText));
      }
      
      lastIndex = match.end;
    }

    // Add trailing text
    if (lastIndex < rawText.length) {
      spans.add(TextSpan(text: rawText.substring(lastIndex)));
    }

    return spans;
  }
}
