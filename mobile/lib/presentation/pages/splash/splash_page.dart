import 'dart:async';

import 'package:auto_route/auto_route.dart';
import 'package:finora/application/auth/splash/splash_cubit.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/finora_logo.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/di.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:finora/presentation/routes/app_router.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';

/// Splash (docs/AUTH_SCREENS.md §2).
///
/// Leaves after 2.2 s or once the session check finishes, whichever is later.
/// A tap skips the wait.
@RoutePage()
class SplashPage extends StatefulWidget {
  const SplashPage({super.key});

  @override
  State<SplashPage> createState() => _SplashPageState();
}

class _SplashPageState extends State<SplashPage> {
  static const _minDuration = Duration(milliseconds: 2200);

  final _cubit = di<SplashCubit>();
  late final Future<SplashDestination> _destination = _cubit.resolve();
  Timer? _timer;
  var _navigated = false;

  @override
  void initState() {
    super.initState();
    _timer = Timer(_minDuration, _go);
  }

  Future<void> _go() async {
    final destination = await _destination;
    if (!mounted || _navigated) return;
    _navigated = true;
    _timer?.cancel();

    final PageRouteInfo route = switch (destination) {
      .onboarding => const OnboardingRoute(),
      .signIn => SignInRoute(),
      .lock => PinLockRoute(),
    };
    await context.router.replace(route);
  }

  @override
  void dispose() {
    _timer?.cancel();
    _cubit.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: darkGreenOverlayStyle,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: _go,
        child: Scaffold(
          backgroundColor: AppPalette.primary900,
          body: Stack(
            children: [
              Center(
                child: Column(
                  mainAxisSize: .min,
                  spacing: 22,
                  children: [
                    const _LogoPop(child: FinoraLogo(size: 92, glow: true)),
                    _FadeUp(
                      delay: const Duration(milliseconds: 300),
                      child: Column(
                        spacing: 6,
                        children: [
                          Text(
                            'Finora',
                            style: GoogleFonts.onest(
                              fontSize: 36,
                              fontWeight: .w700,
                              letterSpacing: -0.72,
                              color: Colors.white,
                            ),
                          ),
                          Text(
                            Words.splashTagline.str,
                            textAlign: .center,
                            style: AppTypography.body.copyWith(
                              color: AppPalette.primary200,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const Positioned(
                left: 0,
                right: 0,
                bottom: 72,
                child: Center(child: _LoadingBar()),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Logo pop: scale 0.6 → 1.06 → 1.0, opacity reaches 1 at 60%. 800ms.
class _LogoPop extends StatelessWidget {
  final Widget child;

  const _LogoPop({required this.child});

  static final _scale = TweenSequence<double>([
    TweenSequenceItem(
      tween: Tween(
        begin: 0.6,
        end: 1.06,
      ).chain(CurveTween(curve: Curves.easeOut)),
      weight: 60,
    ),
    TweenSequenceItem(
      tween: Tween(
        begin: 1.06,
        end: 1.0,
      ).chain(CurveTween(curve: Curves.easeInOut)),
      weight: 40,
    ),
  ]);

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: const Duration(milliseconds: 800),
      child: child,
      builder: (_, t, child) => Opacity(
        opacity: (t / 0.6).clamp(0, 1),
        child: Transform.scale(scale: _scale.transform(t), child: child),
      ),
    );
  }
}

/// Fade + slide up (Y +14 → 0), 600ms after [delay].
class _FadeUp extends StatefulWidget {
  final Widget child;
  final Duration delay;

  const _FadeUp({required this.child, required this.delay});

  @override
  State<_FadeUp> createState() => _FadeUpState();
}

class _FadeUpState extends State<_FadeUp> with SingleTickerProviderStateMixin {
  late final _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 600),
  );
  late final _curve = CurvedAnimation(
    parent: _controller,
    curve: AppMotion.ease,
  );

  @override
  void initState() {
    super.initState();
    Future.delayed(widget.delay, () {
      if (mounted) _controller.forward();
    });
  }

  @override
  void dispose() {
    _curve.dispose();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _curve,
      child: widget.child,
      builder: (_, child) => Opacity(
        opacity: _curve.value,
        child: Transform.translate(
          offset: Offset(0, 14 * (1 - _curve.value)),
          child: child,
        ),
      ),
    );
  }
}

/// 120×4 track with a 48px indicator sweeping X −100% → +260%, 1300ms.
class _LoadingBar extends StatefulWidget {
  const _LoadingBar();

  @override
  State<_LoadingBar> createState() => _LoadingBarState();
}

class _LoadingBarState extends State<_LoadingBar>
    with SingleTickerProviderStateMixin {
  static const _width = 120.0;
  static const _indicator = _width * 0.4;

  late final _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 1300),
  );

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (MediaQuery.disableAnimationsOf(context)) {
      _controller.stop();
      _controller.value = 0.35;
    } else if (!_controller.isAnimating) {
      _controller.repeat();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: _width,
      height: 4,
      clipBehavior: Clip.hardEdge,
      decoration: BoxDecoration(
        color: AppPalette.heroBlock,
        borderRadius: .circular(AppRadius.full),
      ),
      child: AnimatedBuilder(
        animation: _controller,
        builder: (_, _) {
          final t = Curves.easeInOut.transform(_controller.value);
          // −100% … +260% of the indicator's own width
          final dx = _indicator * (-1 + 3.6 * t);
          return Stack(
            children: [
              Positioned(
                left: dx,
                top: 0,
                bottom: 0,
                width: _indicator,
                child: DecoratedBox(
                  decoration: BoxDecoration(
                    color: AppPalette.primary500,
                    borderRadius: .circular(AppRadius.full),
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
