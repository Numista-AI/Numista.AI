import 'package:flutter/material.dart';

class SecondaryDisplayLayout extends StatelessWidget {
  final Widget collectionGrid;
  final Widget liveSpotTicker;
  final Widget aiChatWidget;

  const SecondaryDisplayLayout({
    super.key,
    required this.collectionGrid,
    required this.liveSpotTicker,
    required this.aiChatWidget,
  });

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isUltraWide = screenWidth > 1600;

    if (!isUltraWide) {
      // Standard single/dual pane fallback
      return Column(
        children: [
          liveSpotTicker,
          Expanded(child: collectionGrid),
        ],
      );
    }

    // Ultra-Wide Multi-Pane Workspace (> 1600px width / 21:9 displays)
    return Column(
      children: [
        liveSpotTicker,
        Expanded(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Main Data Grid Workspace (65% width)
              Expanded(
                flex: 65,
                child: Container(
                  margin: const EdgeInsets.all(8.0),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(8.0),
                    boxShadow: const [
                      BoxShadow(color: Colors.black12, blurRadius: 4.0),
                    ],
                  ),
                  child: collectionGrid,
                ),
              ),

              // Side-by-Side Morgan AI Chat & Intel Workspace (35% width)
              Expanded(
                flex: 35,
                child: Container(
                  margin: const EdgeInsets.all(8.0),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    borderRadius: BorderRadius.circular(8.0),
                    border: Border.all(color: Colors.blueGrey.shade100),
                  ),
                  child: Column(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(12.0),
                        color: const Color(0xFF1E3A8A),
                        width: double.infinity,
                        child: const Text(
                          '🤖 Morgan AI Assistant — Live Studio',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 15,
                          ),
                        ),
                      ),
                      Expanded(child: aiChatWidget),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
