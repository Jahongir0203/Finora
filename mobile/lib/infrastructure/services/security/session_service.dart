import 'package:finora/domain/facades/auth_facade.dart';
import 'package:finora/domain/facades/finance_facade.dart';
import 'package:finora/infrastructure/services/cache/secure_cache.dart';
import 'package:injectable/injectable.dart';

import 'pin_service.dart';

/// Ends the session: tokens and PIN are removed from the device.
@LazySingleton()
class SessionService {
  final SecureCache _secureCache;
  final PinService _pins;
  final AuthFacade _auth;
  final FinanceFacade _finance;

  SessionService(this._secureCache, this._pins, this._auth, this._finance);

  /// [remote] also revokes the session on the server (`POST /auth/logout`).
  /// Signing out locally never waits for the network to succeed.
  Future<void> signOut({bool remote = true}) async {
    if (remote) {
      try {
        await _auth.logout();
      } catch (_) {}
    }
    await _pins.clear();
    await _secureCache.clear();
    _finance.reset();
  }
}
