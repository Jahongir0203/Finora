part of 'verify_code_cubit.dart';

enum VerifyPhase {
  /// Waiting for digits.
  input,

  /// 6 digits entered, request in flight.
  verifying,

  /// Wrong code: boxes red for a moment, then cleared.
  error,

  /// Too many attempts: keypad blocked.
  locked,
}

@freezed
abstract class VerifyCodeState with _$VerifyCodeState {
  const VerifyCodeState._();

  const factory VerifyCodeState.initial({
    /// E.164 phone the code was sent to.
    @Default('') String phone,
    @Default('') String code,
    @Default(VerifyCodeCubit.resendSeconds) int secondsLeft,
    @Default(VerifyPhase.input) VerifyPhase phase,

    /// Set after a wrong code; stays visible until the next verification.
    int? attemptsLeft,
    int? lockedMinutes,
    @Default(false) bool isResending,

    /// Incremented to replay the shake animation.
    @Default(0) int shakeTick,

    /// Incremented on unexpected errors (network, server).
    @Default(0) int failureTick,

    /// Incremented when a new code was sent.
    @Default(0) int resentTick,
    VerifyResult? result,
  }) = _Initial;

  bool get canType => phase == .input && result == null;

  bool get canResend => secondsLeft == 0 && !isResending && phase != .locked;
}
