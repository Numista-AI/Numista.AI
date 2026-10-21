import 'dart:io';
import 'package:flutter/foundation.dart' show kIsWeb;

bool getNativePhone() => !kIsWeb && (Platform.isAndroid || Platform.isIOS);
