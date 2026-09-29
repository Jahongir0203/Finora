/// Errors returned by `AuthFacade`. Maps backend error codes
/// (`otp_invalid`, `otp_expired`, `rate_limited`, `otp_blocked`).
sealed class AuthFailure {
  const AuthFailure();
}

/// Wrong OTP code.
class InvalidCodeFailure extends AuthFailure {
  final int attemptsLeft;

  const InvalidCodeFailure(this.attemptsLeft);
}

/// The code is no longer valid; a new one must be requested.
class ExpiredCodeFailure extends AuthFailure {
  const ExpiredCodeFailure();
}

/// Too many OTP requests / attempts.
class RateLimitedFailure extends AuthFailure {
  final Duration retryAfter;

  const RateLimitedFailure(this.retryAfter);

  /// Whole minutes, rounded up (at least 1).
  int get minutes => (retryAfter.inSeconds / 60).ceil().clamp(1, 1 << 30);
}

/// Network / server / unknown error. [message] is ready to show.
class UnknownAuthFailure extends AuthFailure {
  final String? message;

  const UnknownAuthFailure([this.message]);
}
