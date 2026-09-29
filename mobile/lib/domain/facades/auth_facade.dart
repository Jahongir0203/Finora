import 'package:dartz/dartz.dart';
import 'package:finora/domain/models/auth/auth_failure.dart';
import 'package:finora/domain/models/auth/verify_result.dart';

abstract class AuthFacade {
  /// `POST /auth/otp`. [phone] in E.164: `+998901234567`.
  Future<Either<AuthFailure, Unit>> requestOtp(String phone);

  /// `POST /auth/verify`. Saves tokens on success.
  Future<Either<AuthFailure, VerifyResult>> verifyOtp({
    required String phone,
    required String code,
  });

  Future<bool> hasSession();
}
