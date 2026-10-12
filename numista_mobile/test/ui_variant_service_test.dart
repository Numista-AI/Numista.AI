import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:numista_ai/services/http_auth_client.dart';
import 'package:numista_ai/services/ui_variant_service.dart';

void main() {
  setUp(() {
    UiVariantService.reset();
    HttpAuthClient.tokenProviderOverride = () async => 'mock-token';
  });

  tearDown(() {
    HttpAuthClient.httpClientOverride = null;
    HttpAuthClient.tokenProviderOverride = null;
    UiVariantService.reset();
  });

  test('UiVariantService defaults to classic', () {
    expect(UiVariantService.current, UiVariant.classic);
  });

  test('UiVariantService.refresh() with mock 200 alt -> current == UiVariant.alt', () async {
    HttpAuthClient.httpClientOverride = MockClient((request) async {
      if (request.url.path.endsWith('/api/user/ui_variant')) {
        return http.Response(jsonEncode({'variant': 'alt'}), 200,
            headers: {'content-type': 'application/json'});
      }
      return http.Response('Not Found', 404);
    });

    await UiVariantService.refresh();
    expect(UiVariantService.current, UiVariant.alt);
  });

  test('UiVariantService.refresh() with mock 200 classic -> current == UiVariant.classic', () async {
    HttpAuthClient.httpClientOverride = MockClient((request) async {
      return http.Response(jsonEncode({'variant': 'classic'}), 200,
          headers: {'content-type': 'application/json'});
    });

    await UiVariantService.refresh();
    expect(UiVariantService.current, UiVariant.classic);
  });

  test('UiVariantService.refresh() with mock error -> current stays UiVariant.classic (fail safe)', () async {
    // Start from alt to ensure error resets / keeps safe
    HttpAuthClient.httpClientOverride = MockClient((request) async {
      return http.Response(jsonEncode({'variant': 'alt'}), 200);
    });
    await UiVariantService.refresh();
    expect(UiVariantService.current, UiVariant.alt);

    // Now mock network failure / exception
    HttpAuthClient.httpClientOverride = MockClient((request) async {
      throw Exception('Network unreachable');
    });

    await UiVariantService.refresh();
    expect(UiVariantService.current, UiVariant.classic);
  });

  test('UiVariantService.reset() -> current == UiVariant.classic', () async {
    HttpAuthClient.httpClientOverride = MockClient((request) async {
      return http.Response(jsonEncode({'variant': 'alt'}), 200);
    });
    await UiVariantService.refresh();
    expect(UiVariantService.current, UiVariant.alt);

    UiVariantService.reset();
    expect(UiVariantService.current, UiVariant.classic);
  });
}
