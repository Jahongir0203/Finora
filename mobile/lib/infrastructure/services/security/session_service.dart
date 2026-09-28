import 'package:finora/infrastructure/services/cache/secure_cache.dart';
import 'package:injectable/injectable.dart';

import 'pin_service.dart';

/// Ends the session: tokens and PIN are removed from the device.
@LazySingleton()
class SessionService {
  final SecureCache _secureCache;
  final PinService _pins;

  SessionService(this._secureCache, this._pins);

  Future<void> signOut() async {
    await _pins.clear();
    await _secureCache.clear();
  }
}
