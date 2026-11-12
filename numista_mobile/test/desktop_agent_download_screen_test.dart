import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/desktop_agent_download_screen.dart';

void main() {
  testWidgets('hides Download Setup Installer button until clean build', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: DesktopAgentDownloadScreen(),
      ),
    );
    await tester.pump();

    expect(find.textContaining('Download Setup Installer'), findsNothing);
    expect(find.textContaining('Setup Installer temporarily unavailable'), findsOneWidget);
  });
}
