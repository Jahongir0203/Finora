part of 'sign_in_cubit.dart';

@freezed
abstract class SignInState with _$SignInState {
  const SignInState._();

  const factory SignInState.initial({
    /// National number without `+998`, digits only (max 9).
    @Default('') String digits,
    @Default(false) bool showError,

    /// Incremented on each failed submit to replay the shake animation.
    @Default(0) int shakeTick,
    @Default(VarStatus()) VarStatus status,

    /// Set on success; the code screen reads its resend timer.
    OtpSent? sent,
  }) = _Initial;

  bool get isValid => digits.length == SignInCubit.phoneLength;

  /// E.164: `+998901234567`.
  String get phone => '+998$digits';
}
