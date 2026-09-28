/// Errors returned by `AuthFacade`. Maps backend error codes
/// (`invalid_code`, `rate_limited`, `otp_blocked`).
sealed class AuthFailure {
  const AuthFailure();
}

/// Wrong OTP code.
class InvalidCodeFailure extends AuthFailure {
  final int attemptsLeft;

  const InvalidCodeFailure(this.attemptsLeft);
}

/// Too many OTP requests / attempts.
class RateLimitedFailure extends AuthFailure {
  final Duration retryAfter;

  const RateLimitedFailure(this.retryAfter);

  /// Whole minutes, rounded up (at least 1).
  int get minutes => (retryAfter.inSeconds / 60).ceil().clamp(1, 1 << 30);
}

/// Network / server / unknown error.
class UnknownAuthFailure extends AuthFailure {
  final Object? error;

  const UnknownAuthFailure([this.error]);
}
