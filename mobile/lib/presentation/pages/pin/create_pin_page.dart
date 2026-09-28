import 'package:auto_route/auto_route.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_shake.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/di.dart';
import 'package:finora/infrastructure/services/security/pin_service.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:finora/presentation/routes/app_router.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'widgets/pin_badge.dart';
import 'widgets/pin_dots.dart';
import 'widgets/pin_keypad.dart';

enum _Stage { enter, confirm }

/// Create PIN (setup) or Change PIN (docs/screens/PIN_SETUP_SCREENS.md §3).
@RoutePage()
class CreatePinPage extends StatefulWidget {
  /// Profile → Security → Change PIN.
  final bool change;

  const CreatePinPage({super.key, this.change = false});

  @override
  State<CreatePinPage> createState() => _CreatePinPageState();
}

class _CreatePinPageState extends State<CreatePinPage> {
  static const _length = 4;
  static const _checkDelay = Duration(milliseconds: 220);

  final _pins = di<PinService>();
  final _shake = AppShakeController();

  var _stage = _Stage.enter;
  var _code = '';
  var _first = '';
  var _mismatch = false;
  var _error = false;
  var _busy = false;

  @override
  void dispose() {
    _shake.dispose();
    super.dispose();
  }

  void _digit(String d) {
    if (_busy || _code.length >= _length) return;
    setState(() {
      _code += d;
      _error = false;
      _mismatch = false;
    });
    if (_code.length == _length) {
      _busy = true;
      Future.delayed(_checkDelay, _check);
    }
  }

  void _delete() {
    if (_busy || _code.isEmpty) return;
    setState(() => _code = _code.substring(0, _code.length - 1));
  }

  void _fail({bool mismatch = false}) {
    HapticFeedback.heavyImpact();
    _shake.shake();
    setState(() {
      _error = true;
      _mismatch = mismatch;
      _code = '';
      _first = '';
      _stage = .enter;
      _busy = false;
    });
  }

  Future<void> _check() async {
    if (!mounted) return;
    if (_stage == .enter) {
      if (PinService.weakPins.contains(_code)) return _fail();
      setState(() {
        _first = _code;
        _code = '';
        _stage = .confirm;
        _busy = false;
      });
      return;
    }

    if (_code != _first) return _fail(mismatch: true);

    await _pins.setPin(_code);
    if (!mounted) return;
    if (widget.change) {
      AppToast.success(Words.pinChanged.str);
      context.router.maybePop();
    } else {
      AppToast.success(Words.pinCreated.str);
      context.router.replaceAll([const StartingBalanceRoute()]);
    }
  }

  void _back() {
    if (_stage == .confirm) {
      setState(() {
        _stage = .enter;
        _code = '';
        _first = '';
      });
    } else if (widget.change) {
      context.router.maybePop();
    }
  }

  @override
  Widget build(BuildContext context) {
    final confirm = _stage == .confirm;
    final showBack = confirm || widget.change;

    final (icon, title, subtitle) = switch ((confirm, _mismatch)) {
      (true, _) => (
        FinoraIcons.security,
        Words.repeatPin.str,
        Words.repeatPinDesc.str,
      ),
      (false, true) => (
        FinoraIcons.pinCreate,
        Words.createPin.str,
        Words.pinsDidntMatch.str,
      ),
      _ => (
        FinoraIcons.pinCreate,
        widget.change ? Words.enterNewPin.str : Words.createPin.str,
        Words.createPinDesc.str,
      ),
    };

    return PopScope(
      canPop: widget.change && !confirm,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop) _back();
      },
      child: AnnotatedRegion<SystemUiOverlayStyle>(
        value: darkGreenOverlayStyle,
        child: Scaffold(
          backgroundColor: AppPalette.primary900,
          body: SafeArea(
            child: Padding(
              padding: const .fromLTRB(24, 8, 24, 36),
              child: Column(
                children: [
                  SizedBox(
                    height: AppSizes.minTap,
                    child: Align(
                      alignment: AlignmentDirectional.centerStart,
                      child: showBack ? PinBackButton(onTap: _back) : null,
                    ),
                  ),
                  const SizedBox(height: 28),
                  AnimatedSwitcher(
                    duration: const Duration(milliseconds: 200),
                    child: PopIn(
                      key: ValueKey(icon),
                      child: IconBadge(
                        icon: icon,
                        background: AppPalette.primary500,
                        foreground: AppPalette.primary950,
                      ),
                    ),
                  ),
                  const SizedBox(height: 14),
                  AnimatedSwitcher(
                    duration: const Duration(milliseconds: 200),
                    child: Text(
                      title,
                      key: ValueKey(title),
                      textAlign: .center,
                      style: AppTypography.headline.copyWith(
                        fontSize: 26,
                        height: 32 / 26,
                        letterSpacing: -0.52,
                        color: AppPalette.white,
                      ),
                    ),
                  ),
                  const SizedBox(height: 14),
                  ConstrainedBox(
                    constraints: const BoxConstraints(
                      maxWidth: 280,
                      minHeight: 44,
                    ),
                    child: Semantics(
                      liveRegion: true,
                      child: Text(
                        subtitle,
                        textAlign: .center,
                        style: AppTypography.body.copyWith(
                          color: _mismatch
                              ? AppPalette.pinError
                              : AppPalette.primary200,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 28),
                  AppShake(
                    controller: _shake,
                    child: PinDots(filled: _code.length, error: _error),
                  ),
                  const Spacer(),
                  PinKeypad(onDigit: _digit, onDelete: _delete),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// 44px back button on dark green (`rgba(255,255,255,0.08)`).
class PinBackButton extends StatelessWidget {
  final VoidCallback onTap;

  const PinBackButton({super.key, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Semantics(
      button: true,
      label: Words.back.str,
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          width: AppSizes.minTap,
          height: AppSizes.minTap,
          alignment: .center,
          decoration: const BoxDecoration(
            color: Color(0x14FFFFFF),
            shape: BoxShape.circle,
          ),
          child: const Icon(
            FinoraIcons.back,
            size: 20,
            color: AppPalette.white,
          ),
        ),
      ),
    );
  }
}
