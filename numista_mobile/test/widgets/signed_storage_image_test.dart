import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/widgets/signed_storage_image.dart';

void main() {
  testWidgets('Public HTTPS URL bypasses resolver and renders Image.network',
      (tester) async {
    int resolveCalls = 0;
    const publicUrl =
        'https://storage.googleapis.com/numista-reference-library/morgan.jpg';

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SignedStorageImage(
            url: publicUrl,
            resolver: (_) async {
              resolveCalls++;
              return publicUrl;
            },
          ),
        ),
      ),
    );
    await tester.pump();

    expect(resolveCalls, equals(0));
    expect(find.byType(Image), findsOneWidget);
  });

  testWidgets('gs:// URI shows placeholder while resolving then renders image',
      (tester) async {
    final completer = Completer<String?>();
    int resolveCalls = 0;
    const gsUri = 'gs://numista-uploads-studio-9101802118-8c9a8/users/u1/obv.jpg';
    const signedUrl = 'https://storage.googleapis.com/signed-test-obv.jpg';

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SignedStorageImage(
            url: gsUri,
            placeholderBuilder: (_) =>
                const SizedBox(key: Key('custom_placeholder')),
            resolver: (raw) {
              resolveCalls++;
              expect(raw, equals(gsUri));
              return completer.future;
            },
          ),
        ),
      ),
    );

    expect(find.byKey(const Key('custom_placeholder')), findsOneWidget);
    expect(resolveCalls, equals(1));

    completer.complete(signedUrl);
    await tester.pump();

    expect(find.byType(Image), findsOneWidget);
  });

  testWidgets('Expired signed URL triggers single re-resolve on Image error',
      (tester) async {
    int resolveCalls = 0;
    const gsUri = 'gs://numista-uploads-studio-9101802118-8c9a8/users/u1/expired.jpg';

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SignedStorageImage(
            url: gsUri,
            errorBuilder: (_) => const SizedBox(key: Key('img_err_widget')),
            resolver: (_) async {
              resolveCalls++;
              return 'https://invalid.local/attempt_$resolveCalls.jpg';
            },
          ),
        ),
      ),
    );
    await tester.pump();

    expect(resolveCalls, equals(1));
    final imageWidget = tester.widget<Image>(find.byType(Image));
    expect(imageWidget.errorBuilder, isNotNull);

    // Simulate HTTP 403 / expired image load failure once.
    final ctx = tester.element(find.byType(Image));
    imageWidget.errorBuilder!(ctx, Exception('403 Forbidden'), null);
    await tester.pump();
    await tester.pump(Duration.zero);
    await tester.pump();

    // Should have re-resolved exactly once (total 2 calls).
    expect(resolveCalls, equals(2));

    // A second failure after single retry should render errorBuilder without looping.
    final imageWidget2 = tester.widget<Image>(find.byType(Image));
    final result = imageWidget2.errorBuilder!(
      tester.element(find.byType(Image)),
      Exception('403 Forbidden again'),
      null,
    );
    expect(result, isA<SizedBox>());
    expect((result as SizedBox).key, equals(const Key('img_err_widget')));
    expect(resolveCalls, equals(2));
  });
}
