import 'package:dartz/dartz.dart';
import 'package:finora/domain/facades/auth_facade.dart';
import 'package:finora/domain/models/auth/auth_failure.dart';
import 'package:finora/domain/models/auth/verify_result.dart';
import 'package:injectable/injectable.dart';

import '../services/cache/secure_cache.dart';

/// Temporary in-memory auth so the screens can be used end-to-end.
///
/// Accepts code `123456`; 5 wrong codes → 15 min lock.
///
/// TODO: replace with a Dio datasource for `/auth/otp` and `/auth/verify`
/// once device keys (installation_id, device_public_key) are implemented
/// (docs/security/03-mobile.md).
@Injectable(as: AuthFacade)
class AuthFakeDatasource implements AuthFacade {
  final SecureCache _secureCache;

  AuthFakeDatasource(this._secureCache);

  static const _validCode = '123456';
  static const _maxAttempts = 5;
  static var _attempts = 0;
  static DateTime? _blockedUntil;

  @override
  Future<Either<AuthFailure, Unit>> requestOtp(String phone) async {
    await Future.delayed(const Duration(milliseconds: 800));
    final blocked = _blockedFor();
    if (blocked != null) return left(RateLimitedFailure(blocked));
    return right(unit);
  }

  @override
  Future<Either<AuthFailure, VerifyResult>> verifyOtp({
    required String phone,
    required String code,
  }) async {
    await Future.delayed(const Duration(milliseconds: 700));

    final blocked = _blockedFor();
    if (blocked != null) return left(RateLimitedFailure(blocked));

    if (code != _validCode) {
      _attempts++;
      if (_attempts >= _maxAttempts) {
        _attempts = 0;
        _blockedUntil = DateTime.now().add(const Duration(minutes: 15));
        return left(const RateLimitedFailure(Duration(minutes: 15)));
      }
      return left(InvalidCodeFailure(_maxAttempts - _attempts));
    }

    _attempts = 0;
    await _secureCache.setToken('fake-access-token');
    return right(const VerifyResult(isNewUser: true, hasPin: false));
  }

  @override
  Future<bool> hasSession() async => (await _secureCache.token).isNotEmpty;

  Duration? _blockedFor() {
    final until = _blockedUntil;
    if (until == null) return null;
    final left = until.difference(DateTime.now());
    return left.isNegative ? null : left;
  }
}
