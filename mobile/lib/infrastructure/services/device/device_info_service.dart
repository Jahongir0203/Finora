import 'dart:io';

import 'package:device_info_plus/device_info_plus.dart';
import 'package:injectable/injectable.dart';

/// Device model shown in Profile → Devices (`device_name` at sign-in).
@LazySingleton()
class DeviceInfoService {
  String? _name;

  String get platform => Platform.isIOS ? 'ios' : 'android';

  /// "iPhone 15 Pro", "Samsung SM-S918B".
  Future<String> deviceName() async {
    if (_name != null) return _name!;
    try {
      final info = DeviceInfoPlugin();
      if (Platform.isIOS) {
        final ios = await info.iosInfo;
        _name = ios.modelName.isNotEmpty ? ios.modelName : ios.model;
      } else {
        final android = await info.androidInfo;
        final maker = android.manufacturer;
        _name =
            '${maker.isEmpty ? '' : '${maker[0].toUpperCase()}${maker.substring(1)} '}'
            '${android.model}';
      }
    } catch (_) {
      _name = Platform.isIOS ? 'iPhone' : 'Android';
    }
    return _name!;
  }
}
