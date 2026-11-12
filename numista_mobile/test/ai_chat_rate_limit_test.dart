import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/ai_chat_screen.dart';

void main() {
  group('formatChatErrorResponse', () {
    test('extracts user-friendly detail from HTTP 429 JSON body', () {
      const body =
          '{"detail":"Your daily Morgan web lookup limit reached (3/day). Please try again tomorrow."}';
      expect(
        formatChatErrorResponse(429, body),
        'Your daily Morgan web lookup limit reached (3/day). Please try again tomorrow.',
      );
    });

    test('extracts global 429 detail from HTTP 429 JSON body', () {
      const body =
          '{"detail":"Global daily Morgan web lookup limit reached (50/day). Please try again tomorrow."}';
      expect(
        formatChatErrorResponse(429, body),
        'Global daily Morgan web lookup limit reached (50/day). Please try again tomorrow.',
      );
    });

    test('falls back cleanly when HTTP 429 body is non-JSON or empty detail', () {
      expect(
        formatChatErrorResponse(429, 'Too Many Requests'),
        'Daily Morgan web lookup limit reached. Please try again tomorrow.',
      );
      expect(
        formatChatErrorResponse(429, '{"detail":"   "}'),
        'Daily Morgan web lookup limit reached. Please try again tomorrow.',
      );
    });

    test('formats non-429 status codes with generic error text', () {
      expect(
        formatChatErrorResponse(500, '{"detail":"Internal Server Error"}'),
        'Error 500: please try again.',
      );
    });
  });
}
