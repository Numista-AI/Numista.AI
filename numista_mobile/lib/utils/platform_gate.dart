import 'package:flutter/foundation.dart' show visibleForTesting;
import '_platform_gate_stub.dart'
    if (dart.library.io) '_platform_gate_io.dart';

@visibleForTesting
bool? debugIsNativePhoneOverride;

bool get isNativePhone => debugIsNativePhoneOverride ?? getNativePhone();
