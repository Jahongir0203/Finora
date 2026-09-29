import 'dart:async';

import 'package:bloc/bloc.dart';
import 'package:finora/domain/facades/auth_facade.dart';
import 'package:finora/domain/models/auth/auth_failure.dart';
import 'package:finora/domain/models/auth/verify_result.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:injectable/injectable.dart';

part 'verify_code_cubit.freezed.dart';
part 'verify_code_state.dart';

/// SMS OTP flow (docs/AUTH_SCREENS.md §5).
@Injectable()
class VerifyCodeCubit extends Cubit<VerifyCodeState> {
  static const codeLength = 6;
  static const resendSeconds = 60;
  static const _submitDelay = Duration(milliseconds: 200);
  static const _errorHold = Duration(milliseconds: 600);

  final AuthFacade _auth;
  Timer? _timer;

  VerifyCodeCubit(this._auth) : super(const .initial());

  void init(String phone, {bool pinReset = false, OtpSent? sent}) {
    emit(
      state.copyWith(
        phone: phone,
        pinReset: pinReset,
        telegramBotUrl: sent?.telegramBotUrl,
      ),
    );
    _startCountdown(sent?.resendAfter ?? resendSeconds);
  }

  void input(String digit) {
    if (!state.canType || state.code.length >= codeLength) return;

    final code = state.code + digit;
    emit(state.copyWith(code: code));

    if (code.length == codeLength) {
      Future.delayed(_submitDelay, () {
        if (!isClosed && state.code == code && state.phase == .input) {
          _verify(code);
        }
      });
    }
  }

  /// Fills all boxes at once (SMS autofill / paste).
  void fill(String code) {
    final digits = code.replaceAll(RegExp(r'\D'), '');
    if (!state.canType || digits.length != codeLength) return;
    emit(state.copyWith(code: ''));
    for (final d in digits.split('')) {
      input(d);
    }
  }

  void deleteLast() {
    if (!state.canType || state.code.isEmpty) return;
    emit(state.copyWith(code: state.code.substring(0, state.code.length - 1)));
  }

  void clear() {
    if (!state.canType) return;
    emit(state.copyWith(code: ''));
  }

  /// [sms] = "Send by SMS" instead of the Telegram bot.
  Future<void> resend({bool sms = false}) async {
    if (!state.canResend) return;

    emit(state.copyWith(isResending: true));
    final result = await _auth.requestOtp(state.phone, sms: sms);
    if (isClosed) return;

    result.fold(
      (failure) {
        emit(state.copyWith(isResending: false));
        _handleFailure(failure);
      },
      (sent) {
        emit(
          state.copyWith(
            isResending: false,
            code: '',
            attemptsLeft: null,
            resentTick: state.resentTick + 1,
          ),
        );
        _startCountdown(sent.resendAfter);
      },
    );
  }

  Future<void> _verify(String code) async {
    emit(state.copyWith(phase: .verifying));
    final result = await _auth.verifyOtp(
      phone: state.phone,
      code: code,
      pinReset: state.pinReset,
    );
    if (isClosed) return;

    result.fold(_handleFailure, (value) {
      _timer?.cancel();
      emit(state.copyWith(phase: .input, attemptsLeft: null, result: value));
    });
  }

  void _handleFailure(AuthFailure failure) {
    switch (failure) {
      case InvalidCodeFailure(:final attemptsLeft):
        emit(
          state.copyWith(
            phase: .error,
            attemptsLeft: attemptsLeft,
            shakeTick: state.shakeTick + 1,
          ),
        );
        Future.delayed(_errorHold, () {
          if (!isClosed && state.phase == .error) {
            emit(state.copyWith(phase: .input, code: ''));
          }
        });
      case RateLimitedFailure():
        _timer?.cancel();
        emit(
          state.copyWith(
            phase: .locked,
            lockedMinutes: failure.minutes,
            attemptsLeft: null,
            shakeTick: state.shakeTick + 1,
          ),
        );
        Future.delayed(_errorHold, () {
          if (!isClosed) emit(state.copyWith(code: ''));
        });
      case ExpiredCodeFailure():
        _timer?.cancel();
        emit(
          state.copyWith(
            phase: .input,
            code: '',
            secondsLeft: 0,
            expiredTick: state.expiredTick + 1,
          ),
        );
      case UnknownAuthFailure(:final message):
        emit(
          state.copyWith(
            phase: .input,
            code: '',
            failureMessage: message,
            failureTick: state.failureTick + 1,
          ),
        );
    }
  }

  void _startCountdown(int seconds) {
    _timer?.cancel();
    // Count from a deadline so the timer stays correct after backgrounding.
    final deadline = DateTime.now().add(Duration(seconds: seconds));
    emit(state.copyWith(secondsLeft: seconds));
    _timer = Timer.periodic(const Duration(milliseconds: 250), (timer) {
      final ms = deadline.difference(DateTime.now()).inMilliseconds;
      final left = ms <= 0 ? 0 : (ms / 1000).ceil();
      if (left != state.secondsLeft) emit(state.copyWith(secondsLeft: left));
      if (left == 0) timer.cancel();
    });
  }

  @override
  Future<void> close() {
    _timer?.cancel();
    return super.close();
  }
}
