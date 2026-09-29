class VerifyResult {
  final bool isNewUser;

  /// Whether this account finished PIN setup on this device before.
  final bool hasPin;

  /// Starting balance was already entered (skip that step).
  final bool balanceSet;

  const VerifyResult({
    required this.isNewUser,
    required this.hasPin,
    this.balanceSet = false,
  });
}

/// `POST /auth/otp` answer.
class OtpSent {
  /// Seconds until "Resend code" is available.
  final int resendAfter;

  /// `t.me/<bot>?start=login` when the Telegram bot is configured.
  final String? telegramBotUrl;

  const OtpSent({required this.resendAfter, this.telegramBotUrl});
}
