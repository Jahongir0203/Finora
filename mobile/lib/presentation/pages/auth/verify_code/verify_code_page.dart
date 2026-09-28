import 'package:auto_route/auto_route.dart';
import 'package:easy_localization/easy_localization.dart';
import 'package:finora/application/auth/verify_code/verify_code_cubit.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_shake.dart';
import 'package:finora/common/widgets/app_template_text.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/di.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:finora/presentation/routes/app_router.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'widgets/numeric_keypad.dart';
import 'widgets/otp_boxes.dart';

/// SMS code verification (docs/AUTH_SCREENS.md §5).
@RoutePage()
class VerifyCodePage extends StatelessWidget implements AutoRouteWrapper {
  /// E.164: `+998901234567`.
  final String phone;

  const VerifyCodePage({super.key, required this.phone});

  @override
  Widget wrappedRoute(BuildContext context) => BlocProvider(
    create: (_) => di<VerifyCodeCubit>()..init(phone),
    child: this,
  );

  @override
  Widget build(BuildContext context) => const _VerifyCodeView();
}

class _VerifyCodeView extends StatefulWidget {
  const _VerifyCodeView();

  @override
  State<_VerifyCodeView> createState() => _VerifyCodeViewState();
}

class _VerifyCodeViewState extends State<_VerifyCodeView> {
  final _shake = AppShakeController();
  late final _change = TapGestureRecognizer()..onTap = _back;

  void _back() => context.router.maybePop();

  @override
  void dispose() {
    _shake.dispose();
    _change.dispose();
    super.dispose();
  }

  void _listen(BuildContext context, VerifyCodeState state) {
    if (state.result != null) {
      AppToast.success(Words.signedIn.str);
      context.router.replaceAll([CreatePinRoute()]);
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final cubit = context.read<VerifyCodeCubit>();

    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: authOverlayStyle(context),
      child: MultiBlocListener(
        listeners: [
          BlocListener<VerifyCodeCubit, VerifyCodeState>(
            listenWhen: (a, b) => a.shakeTick != b.shakeTick,
            listener: (_, _) {
              HapticFeedback.heavyImpact();
              _shake.shake();
            },
          ),
          BlocListener<VerifyCodeCubit, VerifyCodeState>(
            listenWhen: (a, b) => a.failureTick != b.failureTick,
            listener: (_, _) => AppToast.error(Words.happenError.str),
          ),
          BlocListener<VerifyCodeCubit, VerifyCodeState>(
            listenWhen: (a, b) => a.resentTick != b.resentTick,
            listener: (_, _) => AppToast.success(Words.codeResent.str),
          ),
          BlocListener<VerifyCodeCubit, VerifyCodeState>(
            listenWhen: (a, b) => a.result != b.result,
            listener: _listen,
          ),
        ],
        child: Scaffold(
          backgroundColor: c.surface,
          body: SafeArea(
            child: LayoutBuilder(
              builder: (context, constraints) => SingleChildScrollView(
                child: ConstrainedBox(
                  constraints: BoxConstraints(minHeight: constraints.maxHeight),
                  child: IntrinsicHeight(
                    child: Padding(
                      padding: const .fromLTRB(24, 8, 24, 24),
                      child: BlocBuilder<VerifyCodeCubit, VerifyCodeState>(
                        builder: (context, state) => Column(
                          crossAxisAlignment: .stretch,
                          spacing: AppSpacing.x2l,
                          children: [
                            AuthBackButton(onPressed: _back),
                            AuthTitle(
                              title: Words.enterCode.str,
                              subtitle: _SentTo(
                                phone: state.phone,
                                change: _change,
                              ),
                            ),
                            AppShake(
                              controller: _shake,
                              child: OtpBoxes(
                                code: state.code,
                                length: VerifyCodeCubit.codeLength,
                                hasError:
                                    state.phase == .error ||
                                    state.phase == .locked,
                                showCursor: state.canType,
                              ),
                            ),
                            _Status(state: state, onResend: cubit.resend),
                            const Spacer(),
                            NumericKeypad(
                              enabled: state.canType,
                              onDigit: cubit.input,
                              onDelete: cubit.deleteLast,
                              onClear: cubit.clear,
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _SentTo extends StatelessWidget {
  final String phone;
  final GestureRecognizer change;

  const _SentTo({required this.phone, required this.change});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Text.rich(
      TextSpan(
        children: templateSpans(Words.sentBySms.str, {
          'phone': TextSpan(
            text: phone.toPhone(),
            style: TextStyle(fontWeight: .w600, color: c.textPrimary),
          ),
          'change': TextSpan(
            text: Words.change.str,
            recognizer: change,
            style: TextStyle(fontWeight: .w600, color: c.primaryText),
          ),
        }),
      ),
    );
  }
}

class _Status extends StatelessWidget {
  final VerifyCodeState state;
  final VoidCallback onResend;

  const _Status({required this.state, required this.onResend});

  static String _mmss(int seconds) =>
      '${seconds ~/ 60}:${(seconds % 60).toString().padLeft(2, '0')}';

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final base = AppTypography.bodyMedium.copyWith(
      fontSize: 14,
      height: 20 / 14,
    );
    final secondary = base.copyWith(color: c.textSecondary);
    final danger = base.copyWith(color: c.danger);

    final Widget main = switch (state.phase) {
      .locked => Text(
        Words.tooManyAttempts.tr(args: ['${state.lockedMinutes ?? 15}']),
        style: danger,
      ),
      .verifying => Row(
        spacing: AppSpacing.sm,
        children: [
          CupertinoActivityIndicator(radius: 7, color: c.textSecondary),
          Text(Words.verifying.str, style: secondary),
        ],
      ),
      _ when state.secondsLeft > 0 => Text(
        Words.resendCodeIn.tr(args: [_mmss(state.secondsLeft)]),
        style: secondary.copyWith(
          fontFeatures: const [FontFeature.tabularFigures()],
        ),
      ),
      _ => GestureDetector(
        onTap: state.isResending ? null : onResend,
        behavior: HitTestBehavior.opaque,
        child: Text(
          Words.resendCode.str,
          style: base.copyWith(
            fontWeight: .w600,
            color: state.isResending ? c.textTertiary : c.primaryText,
          ),
        ),
      ),
    };

    return Semantics(
      liveRegion: true,
      child: Column(
        crossAxisAlignment: .start,
        spacing: AppSpacing.xs,
        children: [
          main,
          if (state.attemptsLeft != null && state.phase != .locked)
            Text(
              Words.incorrectCode.tr(args: ['${state.attemptsLeft}']),
              style: danger,
            ),
        ],
      ),
    );
  }
}
