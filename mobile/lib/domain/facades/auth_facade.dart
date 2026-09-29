import 'package:dartz/dartz.dart';
import 'package:finora/domain/models/auth/auth_failure.dart';
import 'package:finora/domain/models/auth/verify_result.dart';

abstract class AuthFacade {
  /// `POST /auth/otp`. [phone] in E.164: `+998901234567`. [sms] forces SMS
  /// instead of the Telegram bot.
  Future<Either<AuthFailure, OtpSent>> requestOtp(
    String phone, {
    bool sms = false,
  });

  /// `POST /auth/verify`. Saves tokens on success. [pinReset] signs in again
  /// after "Forgot PIN" (the server drops the old session).
  Future<Either<AuthFailure, VerifyResult>> verifyOtp({
    required String phone,
    required String code,
    bool pinReset = false,
  });

  Future<bool> hasSession();

  /// `POST /me/pin-setup` after the PIN is created.
  Future<void> pinCreated();

  /// `POST /devices/current/pin-lockout`: too many wrong PINs. The server
  /// revokes the session.
  Future<void> reportPinLockout();

  /// `POST /auth/logout` (best effort).
  Future<void> logout();
}
