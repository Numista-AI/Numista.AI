// web_meta_web.dart
import 'package:web/web.dart' as web;

void injectNoIndexMeta() {
  try {
    final meta = web.document.createElement('meta') as web.HTMLMetaElement;
    meta.name = 'robots';
    meta.content = 'noindex';
    web.document.head?.appendChild(meta);
  } catch (_) {
    // Suppress any DOM exception
  }
}
