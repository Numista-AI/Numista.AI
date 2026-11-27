import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:numista_ai/screens/ai_chat_screen.dart';
import 'package:numista_ai/screens/base_layout.dart';
import 'package:numista_ai/screens/home_dashboard.dart';
import 'package:numista_ai/screens/morgan_first_home_screen.dart';
import 'package:numista_ai/screens/my_collection_screen.dart';
import 'package:numista_ai/services/camera_capture_service.dart';
import 'package:numista_ai/services/http_auth_client.dart';
import 'package:numista_ai/services/morgan_first_service.dart';
import 'package:numista_ai/services/morgan_prefs.dart';
import 'package:numista_ai/widgets/morgan_full_site_toggle.dart';
import 'package:numista_ai/widgets/morgan_greeter.dart';
import 'package:numista_ai/widgets/morgan_settings_panel.dart';

void main() {
  tearDown(() {
    HttpAuthClient.tokenProviderOverride = null;
    HttpAuthClient.httpClientOverride = null;
    MorganFirstService.reset();
  });

  testWidgets(
      'AT-03, AT-06, AT-07, AT-09, AT-10, AT-11 (F2/F4): Real HTTP P5 capture, honest Type card, Fix Details, Add, Done',
      (WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(1440, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    final captured = <http.BaseRequest>[];
    final proposeBodies = <Map<String, dynamic>>[];
    int propSeq = 0;

    HttpAuthClient.tokenProviderOverride = () async => 'test-bearer-token';
    HttpAuthClient.httpClientOverride = MockClient((req) async {
      captured.add(req);
      if (req.url.path.endsWith('/api/morgan/home_flags') && req.method == 'GET') {
        return http.Response(
          jsonEncode({
            'flags': {
              'morgan_home_allowlist': true,
              'morgan_home_new_users': false,
              'morgan_home_everyone': false,
            },
            'eligible': true,
            'preferred_home': 'morgan',
            'show_morgan_home': true,
          }),
          200,
        );
      }
      if (req.url.path.endsWith('/api/morgan/home_preference') &&
          req.method == 'POST') {
        return http.Response(
          jsonEncode({'status': 'ok', 'preferred_home': 'full_site'}),
          200,
        );
      }
      if (req.url.path.endsWith('/api/morgan/propose') && req.method == 'POST') {
        propSeq++;
        final body = jsonDecode(req.body) as Map<String, dynamic>;
        proposeBodies.add(body);
        return http.Response(
          jsonEncode({'status': 'proposed', 'proposal_id': 'prop-$propSeq'}),
          200,
        );
      }
      if (req.url.path.endsWith('/api/morgan/confirm') && req.method == 'POST') {
        return http.Response(
          jsonEncode({'status': 'success', 'coin_id': 'coin-1'}),
          200,
        );
      }
      return http.Response('{}', 404);
    });

    // AT-11 & AT-10 via real MorganFirstService HTTP calls
    await MorganFirstService.refresh();
    expect(MorganFirstService.current.showMorganHome, isTrue);
    expect(captured.last.method, 'GET');
    expect(captured.last.url.path, '/api/morgan/home_flags');
    expect(captured.last.headers['Authorization'], 'Bearer test-bearer-token');

    final prefOk = await MorganFirstService.setPreference('full_site');
    expect(prefOk, isTrue);
    expect(captured.last.method, 'POST');
    expect(captured.last.url.path, '/api/morgan/home_preference');
    expect(captured.last.headers['Authorization'], 'Bearer test-bearer-token');

    bool switchedToFullSite = false;

    // Render MorganFirstHomeScreen with NO proposeFn/confirmFn hooks (real HTTP path)
    await tester.pumpWidget(
      MaterialApp(
        home: MorganFirstHomeScreen(
          onSwitchToFullSite: () => switchedToFullSite = true,
        ),
      ),
    );

    // 3 balanced tiles, Upload tile hidden
    expect(find.byKey(const Key('tile_photo')), findsOneWidget);
    expect(find.byKey(const Key('tile_scan')), findsOneWidget);
    expect(find.byKey(const Key('tile_type')), findsOneWidget);
    expect(find.text('Upload file'), findsNothing);

    // Go to Type
    await tester.tap(find.byKey(const Key('tile_type')));
    await tester.pumpAndSettle();

    expect(find.text('Type your question'), findsOneWidget);
    await tester.enterText(find.byKey(const Key('morgan_type_input')),
        '1921 Morgan dollar, Denver, about fine');
    await tester.tap(find.byKey(const Key('type_submit_btn')));
    await tester.pumpAndSettle();

    // F2/G1: Parsed into clean fields (not whole sentence as Denomination) & NO invented 85%
    expect(proposeBodies.last['coin_data']['Year'], '1921');
    expect(proposeBodies.last['coin_data']['Denomination'], 'Dollar');
    expect(proposeBodies.last['coin_data']['Series'], 'Morgan Dollar');
    expect(proposeBodies.last['coin_data']['Mint Mark'], 'D');
    expect(proposeBodies.last['coin_data']['Condition'], 'About Fine');
    expect(find.byKey(const Key('morgan_confirm_card')), findsOneWidget);
    expect(find.text('You typed this, please check it.'), findsOneWidget);
    expect(find.textContaining('85%'), findsNothing);
    expect(
      captured.where((r) => r.url.path.endsWith('/api/morgan/confirm')),
      isEmpty,
    );

    // AT-06: Fix details -> edit -> returns to confirm card without saving
    await tester.tap(find.byKey(const Key('confirm_fix_btn')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('morgan_fix_details')), findsOneWidget);
    await tester.enterText(find.byKey(const Key('fix_condition_input')), 'MS-63');
    await tester.tap(find.byKey(const Key('fix_done_btn')));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('morgan_confirm_card')), findsOneWidget);
    expect(find.textContaining('Condition: MS-63'), findsOneWidget);
    expect(
      captured.where((r) => r.url.path.endsWith('/api/morgan/confirm')),
      isEmpty,
    );

    // AT-09: Tap Add to collection -> captures real POST /api/morgan/confirm with Bearer
    await tester.tap(find.byKey(const Key('confirm_add_btn')));
    await tester.pumpAndSettle();

    final confirmReqs =
        captured.where((r) => r.url.path.endsWith('/api/morgan/confirm')).toList();
    expect(confirmReqs.length, 1);
    expect(confirmReqs.first.method, 'POST');
    expect(confirmReqs.first.headers['Authorization'], 'Bearer test-bearer-token');
    expect(find.byKey(const Key('morgan_done_heading')), findsOneWidget);

    // AT-07: See my coins switches to Full site
    await tester.tap(find.byKey(const Key('see_my_coins_btn')));
    await tester.pumpAndSettle();
    expect(switchedToFullSite, isTrue);
  });

  testWidgets(
      'AT-04, AT-05, AT-12 (F3/F4): Photo/Scan camera chooser, real /api/identify_coin_photo, <40% card hides Add, Skip does not save',
      (WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(1024, 768));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    final captured = <http.BaseRequest>[];
    String? capturedDeviceId;

    HttpAuthClient.tokenProviderOverride = () async => 'test-bearer-token';
    HttpAuthClient.httpClientOverride = MockClient.streaming((req, bodyStream) async {
      captured.add(req);
      if (req.url.path.endsWith('/api/identify_coin_photo')) {
        return http.StreamedResponse(
          Stream.value(utf8.encode(jsonEncode({
            'Year': '1921',
            'Denomination': 'Morgan Dollar',
            'Mint Mark': 'D',
            'Condition': 'Fine',
            'confidence': 32,
          }))),
          200,
        );
      }
      if (req.url.path.endsWith('/api/morgan/propose')) {
        return http.StreamedResponse(
          Stream.value(utf8.encode(jsonEncode({
            'status': 'proposed',
            'proposal_id': 'prop-low',
          }))),
          200,
        );
      }
      return http.StreamedResponse(Stream.value(utf8.encode('{}')), 404);
    });

    String? pickedFileSlot;
    await tester.pumpWidget(
      MaterialApp(
        home: MorganFirstHomeScreen(
          onSwitchToFullSite: () {},
          listCamerasFn: () async => const [
            CameraDeviceInfo(deviceId: 'cam-1', label: 'Built-in Camera'),
            CameraDeviceInfo(deviceId: 'cam-2', label: 'USB Microscope'),
          ],
          capturePhotoFn: (deviceId) async {
            capturedDeviceId = deviceId;
            return CameraCaptureResult(
              bytes: base64Decode(
                  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='),
              name: 'coin.png',
            );
          },
          pickFileFn: (slot) async {
            pickedFileSlot = slot;
            return base64Decode(
                'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=');
          },
        ),
      ),
    );
    await tester.pumpAndSettle();

    // Enter Scan mode and select USB Microscope (cam-2)
    await tester.tap(find.byKey(const Key('tile_scan')));
    await tester.pumpAndSettle();

    // G3: Both front and reverse have 'Or choose a photo file'
    expect(find.byKey(const Key('pick_front_file_btn')), findsOneWidget);
    expect(find.byKey(const Key('pick_back_file_btn')), findsOneWidget);
    expect(find.text('Or choose a photo file'), findsNWidgets(2));

    await tester.tap(find.byKey(const Key('choose_camera_dropdown')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('USB Microscope').last);
    await tester.pumpAndSettle();

    // Capture front photo using selected camera deviceId, and reverse via file picker (G3)
    await tester.tap(find.byKey(const Key('pick_front_btn')));
    await tester.pumpAndSettle();
    expect(capturedDeviceId, 'cam-2');

    await tester.tap(find.byKey(const Key('pick_back_file_btn')));
    await tester.pumpAndSettle();
    expect(pickedFileSlot, 'back');
    expect(find.text('Back photo ready'), findsOneWidget);

    // Submit for identification -> calls real /api/identify_coin_photo + /api/morgan/propose
    await tester.tap(find.byKey(const Key('identify_photo_btn')));
    await tester.pumpAndSettle();

    final idReqs = captured
        .where((r) => r.url.path.endsWith('/api/identify_coin_photo'))
        .toList();
    expect(idReqs.length, 1);
    expect(idReqs.first.method, 'POST');
    expect(idReqs.first.headers['Authorization'], 'Bearer test-bearer-token');
    expect(idReqs.first, isA<http.MultipartRequest>());
    final mpReq = idReqs.first as http.MultipartRequest;
    expect(mpReq.fields.containsKey('user_email'), isFalse);
    expect(mpReq.fields['save_to_collection'], 'false');

    // AT-04: Real rendered <40% Confirm Card has NO Add button, shows Retake & Type
    expect(find.byKey(const Key('morgan_confirm_card')), findsOneWidget);
    expect(find.text("Morgan can't tell - try another photo"), findsOneWidget);
    expect(find.byKey(const Key('confirm_add_btn')), findsNothing);
    expect(find.byKey(const Key('confirm_retake_btn')), findsOneWidget);
    expect(find.byKey(const Key('confirm_type_fallback_btn')), findsOneWidget);

    // AT-05: Skip asks and discards without calling /api/morgan/confirm
    await tester.tap(find.byKey(const Key('confirm_skip_btn')));
    await tester.pumpAndSettle();
    expect(find.text('Throw away this photo?'), findsOneWidget);
    await tester.tap(find.byKey(const Key('skip_discard_btn')));
    await tester.pumpAndSettle();
    expect(find.text("Hello. I'm Morgan."), findsOneWidget);
    expect(
      captured.where((r) => r.url.path.endsWith('/api/morgan/confirm')),
      isEmpty,
    );
  });

  testWidgets(
      'AT-16 (F4): No microphone control on Morgan home, Type, Confirm card, FullSiteMorganBar, HomeDashboard, AiChatScreen, or Settings (1440/1024/390)',
      (WidgetTester tester) async {
    void expectNoMicAnywhere() {
      expect(find.byIcon(Icons.mic), findsNothing);
      expect(find.byIcon(Icons.mic_none), findsNothing);
      expect(find.byIcon(Icons.mic_rounded), findsNothing);
      expect(find.byIcon(Icons.mic_none_rounded), findsNothing);
      expect(find.text('Microphone'), findsNothing);
      expect(find.bySemanticsLabel('Speak to Morgan'), findsNothing);
      expect(find.textContaining('Voice Microphone'), findsNothing);
    }

    for (final size in [
      const Size(1440, 900),
      const Size(1024, 768),
      const Size(390, 844),
    ]) {
      await tester.binding.setSurfaceSize(size);

      // 1. MorganFirstHomeScreen (Home + Type + Confirm Card)
      await tester.pumpWidget(
        MaterialApp(
          home: MorganFirstHomeScreen(
            onSwitchToFullSite: () {},
            proposeFn: (coinData) async => {'proposal_id': 'prop-16'},
          ),
        ),
      );
      await tester.pumpAndSettle();
      expectNoMicAnywhere();

      await tester.tap(find.byKey(const Key('tile_type')));
      await tester.pumpAndSettle();
      expectNoMicAnywhere();
      expect(find.text('Type your question'), findsOneWidget);

      await tester.enterText(
          find.byKey(const Key('morgan_type_input')), '1921 Morgan dollar');
      await tester.tap(find.byKey(const Key('type_submit_btn')));
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('morgan_confirm_card')), findsOneWidget);
      expectNoMicAnywhere();

      // 2. FullSiteMorganBar + HomeDashboard Ask Morgan box
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Column(
              children: [
                FullSiteMorganBar(onBackToMorgan: () {}),
                Expanded(
                  child: HomeDashboard(
                    testStream: Stream.value(CombinedDashboardData(
                      coins: const [],
                      currency: const [],
                      worldItems: const [],
                    )),
                    onAskMorgan: () {},
                    onTakePhoto: () {},
                  ),
                ),
              ],
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expectNoMicAnywhere();
      expect(find.text('Type your question'), findsOneWidget);
      expect(find.text('Back to Morgan'), findsOneWidget);

      // 3. AiChatScreen (Ask Morgan chat box) — G2: default restores spellCheckConfiguration
      expect(const AiChatScreen(isPopout: false).disableSpellCheckForTest, isFalse);
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: size.width,
              height: size.height,
              child: const AiChatScreen(
                isPopout: false,
                disableSpellCheckForTest: true,
              ),
            ),
          ),
        ),
      );
      await tester.pump();
      expectNoMicAnywhere();
      expect(find.text('Type your question'), findsOneWidget);

      // 4. MorganSettingsPanel
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: MorganSettingsPanel(),
          ),
        ),
      );
      await tester.pump();
      expectNoMicAnywhere();
    }
    await tester.pump(const Duration(seconds: 26));
    await tester.binding.setSurfaceSize(null);
  });

  test('G1 typed-coin parser cases: AU, whole-word ASE, and 1881-S Morgan without dollar', () {
    final auCase = MorganFirstHomeScreen.parseTypedCoin(
        '1921 Morgan dollar, about uncirculated');
    expect(auCase['Condition'], 'AU');
    expect(auCase['Denomination'], 'Dollar');
    expect(auCase['Series'], 'Morgan Dollar');

    final purchasedCase =
        MorganFirstHomeScreen.parseTypedCoin('purchased 1921 dime');
    expect(purchasedCase['Denomination'], 'Dime');
    expect(purchasedCase['Series'], '');

    final morganNoDollar =
        MorganFirstHomeScreen.parseTypedCoin('1881-S Morgan');
    expect(morganNoDollar['Year'], '1881');
    expect(morganNoDollar['Mint Mark'], 'S');
    expect(morganNoDollar['Denomination'], 'Dollar');
    expect(morganNoDollar['Series'], 'Morgan Dollar');

    final aseWholeWord = MorganFirstHomeScreen.parseTypedCoin('2024 ASE');
    expect(aseWholeWord['Denomination'], 'Dollar');
    expect(aseWholeWord['Series'], 'American Silver Eagle');
  });

  test('D2 intent classifier + SAG 97->100 year-plus-question-mark negative tests & D6 title helpers', () {
    // Questions & ambiguous inputs -> answer path (false)
    expect(MorganFirstHomeScreen.isCoinAddDescription('What is a 1793 Chain cent worth?'), isFalse);
    expect(MorganFirstHomeScreen.isCoinAddDescription('1793 Chain cent worth'), isFalse);
    expect(MorganFirstHomeScreen.isCoinAddDescription('hello morgan'), isFalse);
    // SAG 97->100 explicit negative test: string with BOTH a year and '?' routes to answer
    expect(MorganFirstHomeScreen.isCoinAddDescription('1921 Morgan dollar?'), isFalse);
    expect(MorganFirstHomeScreen.isCoinAddDescription('1921 Morgan dollar, Denver?'), isFalse);

    // Clear coin descriptions -> propose/add path (true)
    expect(MorganFirstHomeScreen.isCoinAddDescription('1921 Morgan dollar, Denver, about fine'), isTrue);
    expect(MorganFirstHomeScreen.isCoinAddDescription('1921 Morgan dollar'), isTrue);
    expect(MorganFirstHomeScreen.isCoinAddDescription('add 1909 s vdb cent'), isTrue);

    // D6 doubled-year stripping & formatting
    expect(
      MorganFirstHomeScreen.stripRedundantYear('1921 Morgan Dollar', '1921'),
      'Morgan Dollar',
    );
    expect(
      MorganFirstHomeScreen.formatCoinTitle('1793', '1793 Cent'),
      '1793 Cent',
    );
    expect(
      formatCollectionCoinTitle(
        year: '1921',
        mint: 'D',
        label: 'FT-TEST 1921 Morgan Dollar',
      ),
      '1921D FT-TEST Morgan Dollar',
    );
    expect(
      formatCollectionCoinTitle(
        year: '1793',
        mint: '',
        label: '1793 Cent',
      ),
      '1793 Cent',
    );
  });

  testWidgets(
      'D1, D2, D6, D9: Typed question answered + Add this coin instead, /api/deep_dive fallback, Fix Details no-double-year, typed Skip wording',
      (WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(1440, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    final captured = <http.BaseRequest>[];
    final proposeBodies = <Map<String, dynamic>>[];
    bool forceCopilot404 = false;

    HttpAuthClient.tokenProviderOverride = () async => 'test-bearer-token';
    HttpAuthClient.httpClientOverride = MockClient.streaming((req, bodyStream) async {
      captured.add(req);
      final bodyBytes = await bodyStream.toBytes();
      final bodyStr = utf8.decode(bodyBytes);
      if (req.url.path.endsWith('/api/morgan/copilot')) {
        if (forceCopilot404) {
          return http.StreamedResponse(Stream.value(utf8.encode('{}')), 404);
        }
        return http.StreamedResponse(
          Stream.value(utf8.encode(jsonEncode({
            'response': 'A 1793 Chain cent is the first large cent, very rare.',
          }))),
          200,
        );
      }
      if (req.url.path.endsWith('/api/deep_dive')) {
        return http.StreamedResponse(
          Stream.value(utf8.encode(jsonEncode({
            'response': 'Fallback answer from deep dive.',
          }))),
          200,
        );
      }
      if (req.url.path.endsWith('/api/morgan/propose')) {
        proposeBodies.add(jsonDecode(bodyStr) as Map<String, dynamic>);
        return http.StreamedResponse(
          Stream.value(utf8.encode(jsonEncode({
            'status': 'proposed',
            'proposal_id': 'prop-${proposeBodies.length}',
          }))),
          200,
        );
      }
      return http.StreamedResponse(Stream.value(utf8.encode('{}')), 404);
    });

    await tester.pumpWidget(
      MaterialApp(
        home: MorganFirstHomeScreen(
          onSwitchToFullSite: () {},
        ),
      ),
    );
    await tester.pumpAndSettle();

    // 1. D2 question path ("What is a 1793 Chain cent worth?")
    await tester.tap(find.byKey(const Key('tile_type')));
    await tester.pumpAndSettle();
    await tester.enterText(
      find.byKey(const Key('morgan_type_input')),
      'What is a 1793 Chain cent worth?',
    );
    await tester.tap(find.byKey(const Key('type_submit_btn')));
    await tester.pumpAndSettle();

    // P5: /api/morgan/copilot called with Bearer, ZERO query params in URL, ZERO propose/confirm
    final copilotReqs =
        captured.where((r) => r.url.path.endsWith('/api/morgan/copilot')).toList();
    expect(copilotReqs.length, 1);
    expect(copilotReqs.first.headers['Authorization'], 'Bearer test-bearer-token');
    expect(copilotReqs.first.url.query, isEmpty);
    expect(proposeBodies, isEmpty);
    expect(captured.where((r) => r.url.path.endsWith('/api/morgan/confirm')), isEmpty);
    expect(find.byKey(const Key('morgan_answer_card')), findsOneWidget);
    expect(find.textContaining('first large cent'), findsOneWidget);
    expect(find.byKey(const Key('answer_add_coin_instead_btn')), findsOneWidget);

    // 2. Tap "Add this coin instead" -> proposes only (never confirms) + D9 typed Skip wording
    await tester.tap(find.byKey(const Key('answer_add_coin_instead_btn')));
    await tester.pumpAndSettle();
    expect(proposeBodies.length, 1);
    expect(find.byKey(const Key('morgan_confirm_card')), findsOneWidget);

    await tester.tap(find.byKey(const Key('confirm_skip_btn')));
    await tester.pumpAndSettle();
    expect(find.text('Throw away this entry?'), findsOneWidget);
    expect(find.text('Throw away this photo?'), findsNothing);
    await tester.tap(find.byKey(const Key('skip_discard_btn')));
    await tester.pumpAndSettle();

    // 3. SAG 97->100 negative case ("1921 Morgan dollar?") + /api/deep_dive fallback on 404
    forceCopilot404 = true;
    await tester.tap(find.byKey(const Key('tile_type')));
    await tester.pumpAndSettle();
    await tester.enterText(
      find.byKey(const Key('morgan_type_input')),
      '1921 Morgan dollar?',
    );
    await tester.tap(find.byKey(const Key('type_submit_btn')));
    await tester.pumpAndSettle();
    expect(
      captured.where((r) => r.url.path.endsWith('/api/deep_dive')).length,
      1,
    );
    expect(find.text('Fallback answer from deep dive.'), findsOneWidget);
    await tester.tap(find.byKey(const Key('answer_back_home_btn')));
    await tester.pumpAndSettle();

    // 4. D6 Fix Details pre-fills clean name (no "1921") and avoids doubled year
    await tester.tap(find.byKey(const Key('tile_type')));
    await tester.pumpAndSettle();
    await tester.enterText(
      find.byKey(const Key('morgan_type_input')),
      '1921 Morgan dollar, Denver, about fine',
    );
    await tester.tap(find.byKey(const Key('type_submit_btn')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('confirm_fix_btn')));
    await tester.pumpAndSettle();
    final nameField = tester.widget<TextField>(find.byKey(const Key('fix_name_input')));
    expect(nameField.controller!.text, 'Morgan Dollar');
    await tester.enterText(find.byKey(const Key('fix_name_input')), 'FT-TEST 1921 Morgan Dollar');
    await tester.tap(find.byKey(const Key('fix_done_btn')));
    await tester.pumpAndSettle();
    expect(proposeBodies.last['coin_data']['Year'], '1921');
    expect(proposeBodies.last['coin_data']['Denomination'], 'FT-TEST Morgan Dollar');
    expect(find.text('1921 FT-TEST Morgan Dollar'), findsOneWidget);
  });

  testWidgets('D3 & D7: Sign Out button at 360x780 & 1440x900 (no preference change) + Photo error clears on leave',
      (WidgetTester tester) async {
    final captured = <http.BaseRequest>[];
    HttpAuthClient.tokenProviderOverride = () async => 'test-bearer-token';
    HttpAuthClient.httpClientOverride = MockClient((req) async {
      captured.add(req);
      return http.Response('{"detail": "server error"}', 500);
    });

    bool signOutTapped = false;
    for (final size in [const Size(1440, 900), const Size(360, 780)]) {
      signOutTapped = false;
      await tester.binding.setSurfaceSize(size);
      await tester.pumpWidget(
        MaterialApp(
          home: MorganFirstHomeScreen(
            onSwitchToFullSite: () {},
            onSignOut: () => signOutTapped = true,
            pickFileFn: (slot) async => base64Decode(
                'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('morgan_sign_out_btn')), findsOneWidget);
      await tester.tap(find.byKey(const Key('morgan_sign_out_btn')));
      await tester.pumpAndSettle();
      expect(signOutTapped, isTrue);
      expect(
        captured.where((r) => r.url.path.endsWith('/api/morgan/home_preference')),
        isEmpty,
      );
    }
    await tester.binding.setSurfaceSize(null);

    // D7: Error banner on Photo screen clears cleanly on "Type instead" and dismiss button
    await tester.tap(find.byKey(const Key('tile_photo')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('pick_front_file_btn')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('identify_photo_btn')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('morgan_error_banner')), findsOneWidget);

    await tester.ensureVisible(find.byKey(const Key('photo_type_instead_btn')));
    await tester.tap(find.byKey(const Key('photo_type_instead_btn')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('morgan_error_banner')), findsNothing);
  });

  testWidgets('D8 / P3: MorganGreeter 360x780 title wrap & markSeen persists across reload',
      (WidgetTester tester) async {
    SharedPreferences.setMockInitialValues({});
    expect(await MorganGreeter.shouldShow(), isTrue);
    await MorganGreeter.markSeen();
    expect(await MorganGreeter.shouldShow(), isFalse);
    expect(await MorganPrefs.showOnStartup(), isFalse);

    await tester.binding.setSurfaceSize(const Size(360, 780));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(
      MaterialApp(
        home: MorganGreeter(onAction: (_, _) {}),
      ),
    );
    await tester.pump(const Duration(milliseconds: 800));

    final titleFinder = find.text('Add coins, notes, or medals');
    expect(titleFinder, findsOneWidget);
    final titleText = tester.widget<Text>(titleFinder);
    expect(titleText.maxLines, 2);
    expect(titleText.softWrap, isTrue);
  });

  testWidgets('D5: BaseLayout See my coins opens My Collection without flipping preferred_home',
      (WidgetTester tester) async {
    await tester.binding.setSurfaceSize(const Size(1440, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    final captured = <http.BaseRequest>[];
    HttpAuthClient.tokenProviderOverride = () async => 'test-bearer-token';
    HttpAuthClient.httpClientOverride = MockClient((req) async {
      captured.add(req);
      if (req.url.path.endsWith('/api/morgan/propose')) {
        return http.Response(jsonEncode({'status': 'proposed', 'proposal_id': 'prop-d5'}), 200);
      }
      if (req.url.path.endsWith('/api/morgan/confirm')) {
        return http.Response(jsonEncode({'status': 'success', 'coin_id': 'coin-d5'}), 200);
      }
      return http.Response('{}', 200);
    });

    MorganFirstService.state.value = const MorganHomeFlagsState(
      morganHomeAllowlist: true,
      eligible: true,
      preferredHome: 'morgan',
      showMorganHome: true,
    );

    await tester.pumpWidget(
      MaterialApp(
        home: BaseLayout(
          testSkipFirebase: true,
          testRouteBuilder: (route, _, _) => Center(child: Text('ROUTE:$route')),
        ),
      ),
    );
    await tester.pump(const Duration(milliseconds: 300));

    expect(find.text("Hello. I'm Morgan."), findsOneWidget);
    await tester.tap(find.byKey(const Key('tile_type')));
    await tester.pump(const Duration(milliseconds: 200));
    await tester.enterText(find.byKey(const Key('morgan_type_input')), '1921 Morgan dollar');
    await tester.tap(find.byKey(const Key('type_submit_btn')));
    await tester.pump(const Duration(milliseconds: 300));
    await tester.tap(find.byKey(const Key('confirm_add_btn')));
    await tester.pump(const Duration(milliseconds: 300));

    expect(find.byKey(const Key('morgan_done_heading')), findsOneWidget);
    await tester.tap(find.byKey(const Key('see_my_coins_btn')));
    await tester.pump(const Duration(milliseconds: 300));

    // Opens My Collection with FullSiteMorganBar and ZERO POST /api/morgan/home_preference
    expect(find.text('ROUTE:My Collection'), findsOneWidget);
    expect(find.byKey(const Key('back_to_morgan_button')), findsOneWidget);
    expect(MorganFirstService.current.preferredHome, 'morgan');
    expect(
      captured.where((r) => r.url.path.endsWith('/api/morgan/home_preference')),
      isEmpty,
    );

    // Back to Morgan clears temporary full-site flag cleanly without extra POST
    await tester.tap(find.byKey(const Key('back_to_morgan_button')));
    await tester.pump(const Duration(milliseconds: 300));
    expect(find.text("Hello. I'm Morgan."), findsOneWidget);
    await tester.pump(const Duration(seconds: 26));
  });
}
