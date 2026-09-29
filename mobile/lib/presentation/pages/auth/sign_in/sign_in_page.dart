import 'package:auto_route/auto_route.dart';
import 'package:easy_localization/easy_localization.dart';
import 'package:finora/application/auth/sign_in/sign_in_cubit.dart';
import 'package:finora/common/constants/app_env.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_icons.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/widgets/app_shake.dart';
import 'package:finora/common/widgets/app_template_text.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/di.dart';
import 'package:finora/domain/models/auth/auth_failure.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:finora/presentation/routes/app_router.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:url_launcher/url_launcher.dart';

import 'widgets/phone_field.dart';

/// Sign in with phone number (docs/AUTH_SCREENS.md §4).
@RoutePage()
class SignInPage extends StatelessWidget implements AutoRouteWrapper {
  /// "Forgot PIN": the code is verified with `purpose: pin_reset`.
  final bool pinReset;

  const SignInPage({super.key, this.pinReset = false});

  @override
  Widget wrappedRoute(BuildContext context) =>
      BlocProvider(create: (_) => di<SignInCubit>(), child: this);

  @override
  Widget build(BuildContext context) => _SignInView(pinReset: pinReset);
}

class _SignInView extends StatefulWidget {
  final bool pinReset;

  const _SignInView({required this.pinReset});

  @override
  State<_SignInView> createState() => _SignInViewState();
}

class _SignInViewState extends State<_SignInView> {
  final _phone = TextEditingController();
  final _shake = AppShakeController();

  @override
  void dispose() {
    _phone.dispose();
    _shake.dispose();
    super.dispose();
  }

  void _back() {
    if (context.router.canPop()) {
      context.router.maybePop();
    } else {
      context.router.replace(const OnboardingRoute());
    }
  }

  Future<void> _onListen(BuildContext context, SignInState state) async {
    final cubit = context.read<SignInCubit>();

    if (state.status.isSuccess) {
      cubit.resetStatus();
      FocusManager.instance.primaryFocus?.unfocus();
      await context.router.push(
        VerifyCodeRoute(
          phone: state.phone,
          pinReset: widget.pinReset,
          sent: state.sent,
        ),
      );
    } else if (state.status.isFail) {
      cubit.resetStatus();
      final failure = state.status.error;
      AppToast.error(switch (failure) {
        RateLimitedFailure() => Words.tooManyAttempts.tr(
          args: ['${failure.minutes}'],
        ),
        UnknownAuthFailure(:final message?) => message,
        _ => Words.happenError.str,
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final cubit = context.read<SignInCubit>();

    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: authOverlayStyle(context),
      child: BlocListener<SignInCubit, SignInState>(
        listenWhen: (a, b) =>
            a.status != b.status || a.shakeTick != b.shakeTick,
        listener: (context, state) {
          if (state.shakeTick > 0 && state.status.isInitial) _shake.shake();
          _onListen(context, state);
        },
        child: Scaffold(
          backgroundColor: c.surface,
          resizeToAvoidBottomInset: true,
          body: SafeArea(
            child: CustomScrollView(
              keyboardDismissBehavior: .onDrag,
              slivers: [
                SliverFillRemaining(
                  hasScrollBody: false,
                  child: Padding(
                    padding: const .fromLTRB(24, 8, 24, 40),
                    child: BlocBuilder<SignInCubit, SignInState>(
                      builder: (context, state) => Column(
                        crossAxisAlignment: .stretch,
                        spacing: AppSpacing.x2l,
                        children: [
                          AuthBackButton(onPressed: _back),
                          AuthTitle(
                            title: Words.welcomeTitle.str,
                            subtitle: Text(Words.welcomeSubtitle.str),
                          ),
                          _PhoneBlock(
                            controller: _phone,
                            shake: _shake,
                            showError: state.showError,
                            onChanged: cubit.phoneChanged,
                            onSubmitted: cubit.submit,
                          ),
                          AppButton(
                            text: Words.continueAction.str,
                            size: .large,
                            muted: !state.isValid,
                            isLoading: state.status.isLoading,
                            onPressed: cubit.submit,
                          ),
                          const _OrDivider(),
                          Column(
                            spacing: 10,
                            children: [
                              _SocialButton(
                                text: Words.continueWithApple.str,
                                logo: Icon(
                                  Icons.apple,
                                  size: 22,
                                  color: c.textPrimary,
                                ),
                                // TODO: native Sign in with Apple.
                                onPressed: () => AppToast.info(Words.soon.str),
                              ),
                              _SocialButton(
                                text: Words.continueWithGoogle.str,
                                logo: AppIcons.google.copyWith(
                                  width: 20,
                                  height: 20,
                                ),
                                // TODO: native Google sign-in.
                                onPressed: () => AppToast.info(Words.soon.str),
                              ),
                            ],
                          ),
                          const Spacer(),
                          const _LegalText(),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _PhoneBlock extends StatelessWidget {
  final TextEditingController controller;
  final AppShakeController shake;
  final bool showError;
  final ValueChanged<String> onChanged;
  final VoidCallback onSubmitted;

  const _PhoneBlock({
    required this.controller,
    required this.shake,
    required this.showError,
    required this.onChanged,
    required this.onSubmitted,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final errorStyle = AppTypography.caption.copyWith(
      fontWeight: .w500,
      color: c.danger,
    );

    return Column(
      crossAxisAlignment: .start,
      spacing: AppSpacing.sm,
      children: [
        Text(
          Words.phoneNumber.str,
          style: AppTypography.caption.copyWith(
            fontWeight: .w600,
            color: c.textSecondary,
          ),
        ),
        PhoneField(
          controller: controller,
          shake: shake,
          hasError: showError,
          autofocus: true,
          onChanged: onChanged,
          onSubmitted: onSubmitted,
        ),
        AnimatedSwitcher(
          duration: AppMotion.fade,
          child: showError
              ? Row(
                  key: const ValueKey('error'),
                  spacing: 6,
                  children: [
                    Icon(FinoraIcons.alert, size: 15, color: c.danger),
                    Expanded(
                      child: Text(Words.phoneInvalid.str, style: errorStyle),
                    ),
                  ],
                )
              : const SizedBox(key: ValueKey('none'), width: double.infinity),
        ),
      ],
    );
  }
}

class _OrDivider extends StatelessWidget {
  const _OrDivider();

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final line = Expanded(child: Container(height: 1, color: c.border));

    return Row(
      spacing: AppSpacing.md,
      children: [
        line,
        Text(Words.or.str, style: context.textStyles.caption),
        line,
      ],
    );
  }
}

class _SocialButton extends StatelessWidget {
  final String text;
  final Widget logo;
  final VoidCallback onPressed;

  const _SocialButton({
    required this.text,
    required this.logo,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return AppPressable(
      onTap: onPressed,
      child: Container(
        height: AppSizes.button,
        padding: const .symmetric(horizontal: AppSpacing.lg),
        decoration: BoxDecoration(
          borderRadius: .circular(AppRadius.lg),
          border: Border.all(color: c.border),
        ),
        child: Row(
          mainAxisAlignment: .center,
          spacing: 10,
          children: [
            SizedBox.square(dimension: 22, child: Center(child: logo)),
            Flexible(
              child: Text(
                text,
                maxLines: 1,
                overflow: .ellipsis,
                style: AppTypography.bodyMedium.copyWith(
                  fontWeight: .w600,
                  color: c.textPrimary,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _LegalText extends StatefulWidget {
  const _LegalText();

  @override
  State<_LegalText> createState() => _LegalTextState();
}

class _LegalTextState extends State<_LegalText> {
  late final _terms = TapGestureRecognizer()
    ..onTap = () => _open(AppEnv.termsUrl);
  late final _privacy = TapGestureRecognizer()
    ..onTap = () => _open(AppEnv.privacyUrl);

  Future<void> _open(String url) async {
    if (url.isEmpty) {
      AppToast.info(Words.soon.str);
      return;
    }
    await launchUrl(Uri.parse(url), mode: LaunchMode.inAppBrowserView);
  }

  @override
  void dispose() {
    _terms.dispose();
    _privacy.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final base = AppTypography.caption.copyWith(
      height: 19 / 13,
      color: c.textTertiary,
    );
    final link = base.copyWith(fontWeight: .w600, color: c.primaryText);

    return Text.rich(
      TextSpan(
        style: base,
        children: templateSpans(Words.legalText.str, {
          'terms': TextSpan(
            text: Words.terms.str,
            style: link,
            recognizer: _terms,
          ),
          'privacy': TextSpan(
            text: Words.privacyPolicy.str,
            style: link,
            recognizer: _privacy,
          ),
        }),
      ),
      textAlign: .center,
    );
  }
}
