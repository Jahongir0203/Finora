import 'package:auto_route/auto_route.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/widgets/finora_logo.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/di.dart';
import 'package:finora/infrastructure/services/cache/app_cache.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:finora/presentation/routes/app_router.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'widgets/onboarding_illustrations.dart';

/// Onboarding, 3 slides (docs/AUTH_SCREENS.md §3).
@RoutePage()
class OnboardingPage extends StatefulWidget {
  const OnboardingPage({super.key});

  @override
  State<OnboardingPage> createState() => _OnboardingPageState();
}

class _OnboardingPageState extends State<OnboardingPage> {
  static const _slideCount = 3;

  final _pageController = PageController();
  var _page = 0;

  bool get _isLast => _page == _slideCount - 1;

  Future<void> _finish() async {
    await di<AppCache>().setOnboardingSeen();
    if (mounted) await context.router.push(SignInRoute());
  }

  void _next() {
    if (_isLast) {
      _finish();
      return;
    }
    _pageController.nextPage(duration: AppMotion.push, curve: AppMotion.ease);
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final compact = MediaQuery.sizeOf(context).height < 700;

    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: darkGreenOverlayStyle,
      // Android back: previous slide, or leave the app on the first one.
      child: PopScope(
        canPop: _page == 0,
        onPopInvokedWithResult: (didPop, _) {
          if (!didPop) {
            _pageController.previousPage(
              duration: AppMotion.push,
              curve: AppMotion.ease,
            );
          }
        },
        child: Scaffold(
          backgroundColor: AppPalette.primary900,
          body: SafeArea(
            child: Padding(
              padding: .fromLTRB(
                AppSpacing.x2l,
                AppSpacing.md,
                AppSpacing.x2l,
                compact ? AppSpacing.lg : 44,
              ),
              child: Column(
                spacing: compact ? AppSpacing.lg : AppSpacing.x2l,
                children: [
                  _Header(onSkip: _finish),
                  Expanded(
                    child: PageView.builder(
                      controller: _pageController,
                      itemCount: _slideCount,
                      onPageChanged: (i) => setState(() => _page = i),
                      itemBuilder: (_, i) => _Slide(index: i, compact: compact),
                    ),
                  ),
                  Align(
                    alignment: AlignmentDirectional.centerStart,
                    child: _PageIndicator(count: _slideCount, index: _page),
                  ),
                  Column(
                    spacing: 10,
                    children: [
                      AppButton(
                        text: _isLast ? Words.getStarted.str : Words.next.str,
                        size: .large,
                        onPressed: _next,
                      ),
                      _GhostButton(
                        text: Words.haveAccount.str,
                        onPressed: _finish,
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _Header extends StatelessWidget {
  final VoidCallback onSkip;

  const _Header({required this.onSkip});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        const FinoraLogo(size: 36),
        const SizedBox(width: 10),
        Expanded(
          child: Text(
            'Finora',
            style: AppTypography.title.copyWith(
              fontWeight: .w700,
              color: Colors.white,
            ),
          ),
        ),
        AppPressable(
          onTap: onSkip,
          child: Container(
            height: 40,
            constraints: const BoxConstraints(minWidth: AppSizes.minTap),
            padding: const .symmetric(horizontal: AppSpacing.xs),
            alignment: .center,
            child: Text(
              Words.skip.str,
              style: AppTypography.bodyMedium.copyWith(
                color: AppPalette.primary200,
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _Slide extends StatelessWidget {
  final int index;
  final bool compact;

  const _Slide({required this.index, required this.compact});

  @override
  Widget build(BuildContext context) {
    final (title, description) = switch (index) {
      0 => (Words.onboardingTitle1, Words.onboardingDesc1),
      1 => (Words.onboardingTitle2, Words.onboardingDesc2),
      _ => (Words.onboardingTitle3, Words.onboardingDesc3),
    };

    return AppFadeIn(
      horizontal: true,
      child: Column(
        spacing: compact ? AppSpacing.lg : AppSpacing.x2l,
        children: [
          Expanded(child: OnboardingIllustration(index: index)),
          ConstrainedBox(
            constraints: BoxConstraints(minHeight: compact ? 0 : 140),
            child: Column(
              crossAxisAlignment: .start,
              spacing: AppSpacing.md,
              children: [
                SizedBox(
                  width: double.infinity,
                  child: Text(
                    title.str,
                    style: AppTypography.display.copyWith(
                      fontSize: compact ? 26 : 32,
                      height: 38 / 32,
                      color: Colors.white,
                    ),
                  ),
                ),
                Text(
                  description.str,
                  style: AppTypography.body.copyWith(
                    fontSize: 16,
                    height: 24 / 16,
                    color: AppPalette.primary200,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _PageIndicator extends StatelessWidget {
  final int count;
  final int index;

  const _PageIndicator({required this.count, required this.index});

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: '${index + 1} / $count',
      child: Row(
        mainAxisSize: .min,
        spacing: 6,
        children: [
          for (var i = 0; i < count; i++)
            AnimatedContainer(
              duration: const Duration(milliseconds: 350),
              curve: AppMotion.ease,
              width: i == index ? 24 : 8,
              height: 8,
              decoration: BoxDecoration(
                color: i == index
                    ? AppPalette.primary500
                    : AppPalette.heroBlock,
                borderRadius: .circular(AppRadius.full),
              ),
            ),
        ],
      ),
    );
  }
}

class _GhostButton extends StatelessWidget {
  final String text;
  final VoidCallback onPressed;

  const _GhostButton({required this.text, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return AppPressable(
      onTap: onPressed,
      child: Container(
        height: 48,
        width: double.infinity,
        alignment: .center,
        child: Text(
          text,
          style: AppTypography.bodyMedium.copyWith(color: Colors.white),
        ),
      ),
    );
  }
}
