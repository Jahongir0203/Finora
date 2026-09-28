import 'package:auto_route/auto_route.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_avatar.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_shake.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/di.dart';
import 'package:finora/domain/facades/finance_facade.dart';
import 'package:finora/infrastructure/services/security/auto_lock_service.dart';
import 'package:finora/infrastructure/services/security/biometric_service.dart';
import 'package:finora/infrastructure/services/security/pin_service.dart';
import 'package:finora/infrastructure/services/security/session_service.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:finora/presentation/routes/app_router.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'widgets/pin_badge.dart';
import 'widgets/pin_dots.dart';
import 'widgets/pin_keypad.dart';

enum LockReason {
  /// App opened with a saved session → Home after unlock.
  launch,

  /// Inactivity; shows the auto-lock chip and returns to the last screen.
  autoLock,

  /// Security → "Lock now"; returns to the last screen.
  manual,
}

/// PIN lock (docs/screens/PIN_SETUP_SCREENS.md §4).
@RoutePage()
class PinLockPage extends StatefulWidget {
  final LockReason reason;

  const PinLockPage({super.key, this.reason = LockReason.launch});

  @override
  State<PinLockPage> createState() => _PinLockPageState();
}

enum _Status { idle, scanning, wrong }

class _PinLockPageState extends State<PinLockPage> {
  static const _length = 4;

  final _pins = di<PinService>();
  final _biometrics = di<BiometricService>();
  final _autoLock = di<AutoLockService>();
  final _shake = AppShakeController();

  var _code = '';
  var _status = _Status.idle;
  var _attemptsLeft = PinService.maxAttempts;
  var _busy = false;
  var _faceAvailable = false;

  @override
  void initState() {
    super.initState();
    _autoLock.locked = true;
    _initBiometrics();
  }

  Future<void> _initBiometrics() async {
    final available = await _biometrics.isAvailable();
    if (!mounted || !available) return;
    setState(() => _faceAvailable = true);
    _face();
  }

  @override
  void dispose() {
    _autoLock
      ..locked = false
      ..touch();
    _shake.dispose();
    super.dispose();
  }

  void _digit(String d) {
    if (_busy || _code.length >= _length) return;
    setState(() {
      _code += d;
      if (_status == .wrong) _status = .idle;
    });
    if (_code.length == _length) {
      _busy = true;
      Future.delayed(const Duration(milliseconds: 220), _check);
    }
  }

  void _delete() {
    if (_busy || _code.isEmpty) return;
    setState(() => _code = _code.substring(0, _code.length - 1));
  }

  Future<void> _check() async {
    final left = await _pins.verify(_code);
    if (!mounted) return;
    if (left == null) return _unlock();

    if (left <= 0) {
      await di<SessionService>().signOut();
      if (!mounted) return;
      AppToast.error(Words.tooManyPinAttempts.str);
      context.router.replaceAll([const SignInRoute()]);
      return;
    }

    HapticFeedback.heavyImpact();
    _shake.shake();
    setState(() {
      _status = .wrong;
      _attemptsLeft = left;
      _code = '';
      _busy = false;
    });
  }

  void _unlock() {
    if (widget.reason == .launch) {
      context.router.replaceAll([const MainRoute()]);
    } else {
      context.router.maybePop();
    }
  }

  Future<void> _face() async {
    setState(() => _status = .scanning);
    final ok = await _biometrics.authenticate();
    if (!mounted) return;
    if (ok) return _unlock();
    setState(() => _status = .idle);
  }

  void _forgot() {
    AppToast.info(Words.verifyPhoneToReset.str);
    context.router.replaceAll([const SignInRoute()]);
  }

  @override
  Widget build(BuildContext context) {
    final name = di<FinanceFacade>().snapshot.userName;
    final (status, statusColor) = switch (_status) {
      .idle => (Words.enterPinToContinue.str, AppPalette.primary200),
      .scanning => (Words.scanningFace.str, AppPalette.primary200),
      .wrong => (
        Words.wrongPin.tr(args: ['$_attemptsLeft']),
        AppPalette.pinError,
      ),
    };

    return PopScope(
      // Android back sends the app to the background; the lock stays.
      canPop: false,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop) SystemNavigator.pop();
      },
      child: AnnotatedRegion<SystemUiOverlayStyle>(
        value: darkGreenOverlayStyle,
        child: Scaffold(
          backgroundColor: AppPalette.primary900,
          body: TweenAnimationBuilder<double>(
            tween: Tween(begin: 0, end: 1),
            duration: const Duration(milliseconds: 350),
            builder: (_, v, child) => Opacity(opacity: v, child: child),
            child: SafeArea(
              child: Padding(
                padding: const .fromLTRB(24, 24, 24, 36),
                child: Column(
                  children: [
                    const SizedBox(height: 28),
                    PopIn(
                      child: AppAvatar(
                        name: name,
                        size: 72,
                        onDark: true,
                        fontSize: 24,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      Words.welcomeBack.tr(args: [name.split(' ').first]),
                      textAlign: .center,
                      style: AppTypography.title.copyWith(
                        fontSize: 22,
                        fontWeight: .w700,
                        color: AppPalette.white,
                      ),
                    ),
                    const SizedBox(height: 12),
                    ConstrainedBox(
                      constraints: const BoxConstraints(minHeight: 22),
                      child: Semantics(
                        liveRegion: true,
                        child: Text(
                          status,
                          textAlign: .center,
                          style: AppTypography.body.copyWith(
                            color: statusColor,
                          ),
                        ),
                      ),
                    ),
                    if (widget.reason == .autoLock) ...[
                      const SizedBox(height: 28),
                      AppFadeIn(
                        duration: const Duration(milliseconds: 400),
                        child: _AutoLockChip(minutes: _autoLock.minutes),
                      ),
                    ],
                    const SizedBox(height: 28),
                    AppShake(
                      controller: _shake,
                      child: PinDots(
                        filled: _code.length,
                        error: _status == .wrong && _code.isEmpty,
                      ),
                    ),
                    const Spacer(),
                    PinKeypad(
                      onDigit: _digit,
                      onDelete: _delete,
                      onFace: _faceAvailable ? _face : null,
                    ),
                    const SizedBox(height: 28),
                    GestureDetector(
                      onTap: _forgot,
                      behavior: HitTestBehavior.opaque,
                      child: SizedBox(
                        height: 40,
                        child: Center(
                          child: Text(
                            Words.forgotPin.str,
                            style: AppTypography.button.copyWith(
                              fontSize: 15,
                              color: AppPalette.primary200,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _AutoLockChip extends StatelessWidget {
  final int minutes;

  const _AutoLockChip({required this.minutes});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 32,
      padding: const .symmetric(horizontal: 12),
      decoration: BoxDecoration(
        color: AppPalette.pinChipBg,
        borderRadius: .circular(AppRadius.full),
      ),
      child: Row(
        mainAxisSize: .min,
        spacing: AppSpacing.sm,
        children: [
          const Icon(
            FinoraIcons.autoLock,
            size: 14,
            color: AppPalette.primary200,
          ),
          Text(
            Words.lockedAfter.tr(args: ['$minutes']),
            style: AppTypography.caption.copyWith(
              color: AppPalette.pinChipText,
            ),
          ),
        ],
      ),
    );
  }
}
