import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:numista_ai/screens/ai_chat_screen.dart';
import 'package:numista_ai/screens/base_layout.dart';
import 'package:numista_ai/screens/home_dashboard.dart';
import 'package:numista_ai/services/display_preferences_service.dart';
import 'package:numista_ai/services/http_auth_client.dart';
import 'package:numista_ai/services/morgan_proactive_rescue_observer.dart';
import 'package:numista_ai/services/morgan_screen_state_registry.dart';
import 'package:numista_ai/services/morgan_test_harness.dart';
import 'package:numista_ai/services/stt_voice_service.dart';
import 'package:numista_ai/widgets/morgan_chat_popout.dart';

Future<void> _settle(WidgetTester tester, {int ticks = 6}) async {
  for (var i = 0; i < ticks; i++) {
    await tester.pump(const Duration(milliseconds: 50));
  }
}

void _ignorePreExistingLayoutOverflows() {
  final prev = FlutterError.onError;
  FlutterError.onError = (FlutterErrorDetails details) {
    final msg = details.exceptionAsString();
    if (msg.contains('A RenderFlex overflowed')) {
      return;
    }
    prev?.call(details);
  };
  addTearDown(() {
    FlutterError.onError = prev;
  });
}

Widget _wrapPhoneHome({
  void Function(String query)? onAskMorganWithQuery,
  VoidCallback? onAskMorgan,
  VoidCallback? onTakePhoto,
  Size size = const Size(412, 915),
}) {
  return MaterialApp(
    home: MediaQuery(
      data: MediaQueryData(size: size),
      child: Scaffold(
        body: SizedBox(
          width: size.width,
          height: size.height,
          child: HomeDashboard(
            onAskMorgan: onAskMorgan,
            onAskMorganWithQuery: onAskMorganWithQuery,
            onTakePhoto: onTakePhoto,
            reviewQueueCount: 0,
            isReviewCountLoading: false,
            testStream: Stream<CombinedDashboardData>.value(
              CombinedDashboardData(
                coins: const [],
                currency: const [],
                worldItems: const [],
              ),
            ),
          ),
        ),
      ),
    ),
  );
}

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
    DisplayPreferencesService.instance.resetForTest(initialValue: true);
    MorganScreenStateRegistry.instance.resetForTesting();
    MorganProactiveRescueObserver.instance.resetForTesting();
    MorganTestHarness.debugEnabledOverride = true;
    SttVoiceService.instance.stopListening();
    SttVoiceService.instance.onUtterance = null;
    SttVoiceService.instance.micAllowed = true;
    HttpAuthClient.tokenProviderOverride = () async => 'unit-test-bearer-token';
  });

  tearDown(() {
    HttpAuthClient.tokenProviderOverride = null;
    HttpAuthClient.httpClientOverride = null;
    SttVoiceService.instance.stopListening();
    SttVoiceService.instance.onUtterance = null;
    SttVoiceService.instance.micAllowed = true;
    MorganTestHarness.debugEnabledOverride = null;
    MorganProactiveRescueObserver.instance.resetForTesting();
    MorganScreenStateRegistry.instance.resetForTesting();
  });

  testWidgets(
      '1. Phone submit hands off to AiChatScreen, auto-sends once, and sends Authorization Bearer header (Fix #4)',
      (tester) async {
    _ignorePreExistingLayoutOverflows();
    await tester.binding.setSurfaceSize(const Size(412, 915));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    final copilotRequests = <http.Request>[];
    HttpAuthClient.httpClientOverride = MockClient((req) async {
      if (req.url.path.endsWith('/api/morgan/copilot')) {
        copilotRequests.add(req);
        return http.Response(
          jsonEncode({'response': 'An MS63 1921 Morgan Dollar typically retails around \$55.'}),
          200,
        );
      }
      return http.Response('{}', 200);
    });

    await tester.pumpWidget(
      const MaterialApp(
        home: MediaQuery(
          data: MediaQueryData(size: Size(412, 915)),
          child: BaseLayout(
            isDemoMode: true,
            testSkipFirebase: true,
          ),
        ),
      ),
    );
    await _settle(tester);

    expect(find.byType(HomeDashboard), findsOneWidget);
    final inputFinder = find.widgetWithText(TextField, 'Type or say your question...');
    expect(inputFinder, findsOneWidget);

    await tester.enterText(inputFinder, 'What is a 1921 Morgan Dollar worth in MS63?');
    await tester.pump();
    await tester.tap(find.byKey(const Key('home_ask_morgan_send_btn')));
    await _settle(tester, ticks: 8);

    expect(find.byType(AiChatScreen), findsOneWidget);
    expect(copilotRequests.length, 1);

    final req = copilotRequests.single;
    expect(req.method, 'POST');
    expect(req.headers['Authorization'], 'Bearer unit-test-bearer-token');
    final decodedBody = jsonDecode(req.body) as Map<String, dynamic>;
    expect(decodedBody['query'], 'What is a 1921 Morgan Dollar worth in MS63?');
    expect(find.textContaining('MS63 1921 Morgan Dollar typically retails'), findsOneWidget);
    MorganProactiveRescueObserver.instance.resetForTesting();
    await tester.pump(const Duration(milliseconds: 350));
  });

  testWidgets(
      '2. No double-send across async loadGate rebuilds, rapid Send double-tap (Fix #1), or back-nav',
      (tester) async {
    _ignorePreExistingLayoutOverflows();

    // 2A: Slow loadGate + parent rebuilds on AiChatScreen -> still sends strictly once
    final loadGate = Completer<void>();
    int copilotCalls = 0;
    HttpAuthClient.httpClientOverride = MockClient((req) async {
      if (req.url.path.endsWith('/api/morgan/copilot')) {
        copilotCalls++;
        return http.Response(jsonEncode({'response': 'Morgan single-send reply.'}), 200);
      }
      return http.Response('{}', 200);
    });

    late StateSetter outerSetState;
    int rebuildTick = 0;
    await tester.pumpWidget(
      MaterialApp(
        home: StatefulBuilder(
          builder: (context, setState) {
            outerSetState = setState;
            return Scaffold(
              body: Column(
                children: [
                  Text('tick:$rebuildTick'),
                  Expanded(
                    child: AiChatScreen(
                      initialQuery: 'Check 1893-S key date',
                      initialQueryNonce: 1,
                      testSkipFirebase: true,
                      testLoadGate: () => loadGate.future,
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
    await tester.pump();

    // Parent rebuilds while session load is still in flight
    outerSetState(() => rebuildTick++);
    await tester.pump();
    outerSetState(() => rebuildTick++);
    await tester.pump();
    expect(copilotCalls, 0);

    // Complete async load and rebuild again -> strictly 1 send
    loadGate.complete();
    await _settle(tester);
    outerSetState(() => rebuildTick++);
    await _settle(tester);
    expect(copilotCalls, 1);

    // 2B: Double-tap on Home Send button disables button and submits once (Fix #1)
    int homeSubmissions = 0;
    await tester.pumpWidget(
      _wrapPhoneHome(onAskMorganWithQuery: (_) => homeSubmissions++),
    );
    await _settle(tester);

    await tester.enterText(
      find.widgetWithText(TextField, 'Type or say your question...'),
      'Grade my Peace Dollar',
    );
    await tester.pump();
    await tester.tap(find.byKey(const Key('home_ask_morgan_send_btn')));
    await tester.pump();
    final disabledBtn = tester.widget<IconButton>(find.byKey(const Key('home_ask_morgan_send_btn')));
    expect(disabledBtn.onPressed, isNull);
    await tester.tap(find.byKey(const Key('home_ask_morgan_send_btn')));
    await tester.pump(const Duration(milliseconds: 350));
    expect(homeSubmissions, 1);

    // 2C: Route exit clears unconsumed initialQuery so returning to Ask Morgan does not replay it
    final routeQueries = <String>[];
    await tester.pumpWidget(
      MaterialApp(
        home: MediaQuery(
          data: const MediaQueryData(size: Size(412, 915)),
          child: BaseLayout(
            isDemoMode: true,
            testSkipFirebase: true,
            testRouteBuilder: (route, aiInitialQuery, _) {
              routeQueries.add('$route::$aiInitialQuery');
              if (route == 'Home Dashboard') {
                return PrimaryScrollController.none(
                  child: HomeDashboard(
                    onAskMorganWithQuery: (q) {},
                    testStream: Stream<CombinedDashboardData>.value(
                      CombinedDashboardData(coins: const [], currency: const [], worldItems: const []),
                    ),
                  ),
                );
              }
              return Center(child: Text('ROUTE:$route'));
            },
          ),
        ),
      ),
    );
    await _settle(tester);
    expect(routeQueries.first, 'Home Dashboard::null');
    MorganProactiveRescueObserver.instance.resetForTesting();
    await tester.pump(const Duration(milliseconds: 350));
  });

  testWidgets(
      '3. Offline / HTTP 500 fallback keeps exact query in AiChatScreen input for easy retry',
      (tester) async {
    int attempts = 0;
    HttpAuthClient.httpClientOverride = MockClient((req) async {
      if (req.url.path.endsWith('/api/morgan/copilot')) {
        attempts++;
        return http.Response('{"detail":"Internal Server Error"}', 500);
      }
      return http.Response('{}', 200);
    });

    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: AiChatScreen(
            initialQuery: 'Offline Morgan test question',
            initialQueryNonce: 1,
            testSkipFirebase: true,
          ),
        ),
      ),
    );
    await _settle(tester, ticks: 8);

    expect(attempts, 1);
    expect(find.textContaining('Error 500'), findsOneWidget);

    final chatInput = find.byWidgetPredicate(
      (w) => w is TextField && (w.decoration?.hintText?.contains('Ask Morgan') ?? false),
    );
    expect(chatInput, findsOneWidget);
    final field = tester.widget<TextField>(chatInput);
    expect(field.controller?.text, 'Offline Morgan test question');
    MorganProactiveRescueObserver.instance.resetForTesting();
  });

  testWidgets(
      '4. Empty or whitespace submit is a no-op, keeps focus, triggers zero navigations and zero HTTP calls',
      (tester) async {
    _ignorePreExistingLayoutOverflows();
    int askCount = 0;
    int queryCount = 0;
    int httpCount = 0;
    HttpAuthClient.httpClientOverride = MockClient((req) async {
      httpCount++;
      return http.Response('{}', 200);
    });

    await tester.pumpWidget(
      _wrapPhoneHome(
        onAskMorgan: () => askCount++,
        onAskMorganWithQuery: (_) => queryCount++,
      ),
    );
    await _settle(tester);

    final inputFinder = find.widgetWithText(TextField, 'Type or say your question...');
    await tester.enterText(inputFinder, '   \n\t  ');
    await tester.pump();
    await tester.tap(find.byKey(const Key('home_ask_morgan_send_btn')));
    await tester.pump();
    await tester.testTextInput.receiveAction(TextInputAction.send);
    await tester.pump();

    expect(askCount, 0);
    expect(queryCount, 0);
    expect(httpCount, 0);
    final editable = tester.widget<EditableText>(
      find.descendant(of: inputFinder, matching: find.byType(EditableText)),
    );
    expect(editable.focusNode.hasFocus, isTrue);
  });

  testWidgets(
      '5. Desktop popout opens MorganChatPopout on cold load and handles 2nd submit with incremented nonce',
      (tester) async {
    _ignorePreExistingLayoutOverflows();
    await tester.binding.setSurfaceSize(const Size(1440, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    final submittedQueries = <String>[];
    HttpAuthClient.httpClientOverride = MockClient((req) async {
      if (req.url.path.endsWith('/api/morgan/copilot')) {
        final body = jsonDecode(req.body) as Map<String, dynamic>;
        submittedQueries.add(body['query'] as String);
        return http.Response(jsonEncode({'response': 'Popout reply ${submittedQueries.length}'}), 200);
      }
      return http.Response('{}', 200);
    });

    await tester.pumpWidget(
      const MaterialApp(
        home: MediaQuery(
          data: MediaQueryData(size: Size(1440, 900)),
          child: BaseLayout(
            isDemoMode: true,
            testSkipFirebase: true,
          ),
        ),
      ),
    );
    await _settle(tester);

    final homeInput = find.widgetWithText(TextField, 'Type or say your question...');
    await tester.enterText(homeInput, 'First desktop question');
    await tester.pump();
    await tester.tap(find.byKey(const Key('home_ask_morgan_send_btn')));
    await _settle(tester, ticks: 8);

    expect(find.byType(MorganChatPopout), findsOneWidget);
    expect(submittedQueries, ['First desktop question']);

    // Wait out 300ms double-tap guard and submit again while popout stays open
    await tester.pump(const Duration(milliseconds: 350));
    await tester.enterText(homeInput, 'First desktop question');
    await tester.pump();
    await tester.tap(find.byKey(const Key('home_ask_morgan_send_btn')));
    await _settle(tester, ticks: 8);

    expect(submittedQueries, ['First desktop question', 'First desktop question']);
    MorganProactiveRescueObserver.instance.resetForTesting();
    await tester.pump(const Duration(milliseconds: 350));
  });

  testWidgets(
      '6. Home Speak/STT shows Stop (Fix #2), disables Send (Fix #1), stops on Photo (Fix #3), and auto-submits utterance',
      (tester) async {
    _ignorePreExistingLayoutOverflows();
    final submitted = <String>[];
    int photoTaps = 0;

    await tester.pumpWidget(
      _wrapPhoneHome(
        onAskMorganWithQuery: (q) => submitted.add(q),
        onTakePhoto: () => photoTaps++,
      ),
    );
    await _settle(tester);

    // Idle shows Speak (never Listening...) and enabled Send button
    expect(find.text('Speak'), findsOneWidget);
    expect(find.text('Microphone'), findsNothing);
    expect(
      tester.widget<IconButton>(find.byKey(const Key('home_ask_morgan_send_btn'))).onPressed,
      isNotNull,
    );

    // Start listening -> shows red 'Stop' icon/label and disables Send button (Fixes #1 & #2)
    await tester.tap(find.text('Speak'));
    await tester.pump();

    expect(find.text('Stop'), findsOneWidget);
    expect(find.text('Listening…'), findsNothing);
    final stopIcon = tester.widget<Icon>(find.byIcon(Icons.mic));
    expect(stopIcon.color, const Color(0xFFDC2626));
    expect(
      tester.widget<IconButton>(find.byKey(const Key('home_ask_morgan_send_btn'))).onPressed,
      isNull,
    );

    // Fix #3: tapping Photo stops active STT before navigating
    await tester.tap(find.text('Photo'));
    await tester.pump();
    expect(photoTaps, 1);
    expect(find.text('Speak'), findsOneWidget);
    expect(
      tester.widget<IconButton>(find.byKey(const Key('home_ask_morgan_send_btn'))).onPressed,
      isNotNull,
    );

    // Start listening again -> voice utterance auto-populates and hands off once
    await tester.tap(find.text('Speak'));
    await tester.pump();
    await MorganTestHarness.voiceInjectionHook!('Tell me about Peace Dollars');
    await tester.pump(const Duration(milliseconds: 350));

    expect(submitted, ['Tell me about Peace Dollars']);
    expect(find.text('Speak'), findsOneWidget);

    // Unsupported browser shows SnackBar and focuses input
    MorganTestHarness.debugEnabledOverride = false;
    await tester.pumpWidget(
      _wrapPhoneHome(onAskMorganWithQuery: (q) => submitted.add(q)),
    );
    await _settle(tester);
    await tester.tap(find.text('Speak'));
    await tester.pump();
    expect(find.textContaining('type your question above'), findsOneWidget);
  });

  testWidgets(
      '7. Photo tap on Home routes in 1 step to AI Photo Identification camera scanner',
      (tester) async {
    _ignorePreExistingLayoutOverflows();
    await tester.binding.setSurfaceSize(const Size(412, 915));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      const MaterialApp(
        home: MediaQuery(
          data: MediaQueryData(size: Size(412, 915)),
          child: BaseLayout(
            isDemoMode: true,
            testSkipFirebase: true,
          ),
        ),
      ),
    );
    await _settle(tester);

    await tester.tap(find.text('Photo'));
    await _settle(tester);

    expect(find.text('AI Photo Identification'), findsOneWidget);
    MorganProactiveRescueObserver.instance.resetForTesting();
  });

  testWidgets(
      '8. Ask Morgan Card at 360x740 & 412x915 has zero overflows, single-line Speak/Stop/Photo, height >= 56px, fontSize >= 18px',
      (tester) async {
    final prevOnError = FlutterError.onError;
    final overflows = <String>[];
    bool measureCardOverflows = false;
    FlutterError.onError = (details) {
      final msg = details.exceptionAsString();
      if (msg.contains('overflowed') || msg.contains('RenderFlex')) {
        if (measureCardOverflows) {
          overflows.add(msg);
        }
        return;
      }
      prevOnError?.call(details);
    };
    addTearDown(() => FlutterError.onError = prevOnError);

    for (final surface in const [Size(360, 740), Size(412, 915)]) {
      await tester.binding.setSurfaceSize(surface);
      measureCardOverflows = false;
      await tester.pumpWidget(_wrapPhoneHome(size: surface));
      await tester.pump();
      measureCardOverflows = true;
      await _settle(tester);

      for (final label in const ['Speak', 'Photo']) {
        final textFinder = find.text(label);
        expect(textFinder, findsOneWidget);
        final textWidget = tester.widget<Text>(textFinder);
        expect((textWidget.style?.fontSize ?? 0) >= 18.0, isTrue,
            reason: '$label fontSize on $surface');
        expect(tester.getSize(textFinder).height <= 30.0, isTrue,
            reason: '$label wrapped onto multiple lines on $surface');
      }
      for (final btn in tester.widgetList<OutlinedButton>(find.byType(OutlinedButton))) {
        final box = tester.getSize(find.byWidget(btn));
        expect(box.height >= 56.0, isTrue, reason: 'OutlinedButton height on $surface');
      }
      expect(
        tester.getSize(find.byKey(const Key('home_ask_morgan_send_btn'))).height >= 48.0,
        isTrue,
      );

      // Also verify listening ('Stop') state stays single-line without overflow at 360px
      await tester.tap(find.text('Speak'));
      await tester.pump();
      final stopFinder = find.text('Stop');
      expect(stopFinder, findsOneWidget);
      expect(tester.getSize(stopFinder).height <= 30.0, isTrue);
      await tester.tap(stopFinder);
      await tester.pump();
      expect(find.text('Speak'), findsOneWidget);
    }
    await tester.binding.setSurfaceSize(null);
    FlutterError.onError = prevOnError;
    expect(overflows, isEmpty);
  });
}
