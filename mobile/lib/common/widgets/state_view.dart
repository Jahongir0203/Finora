import 'dart:math' as math;

import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/words/words.dart';
import 'package:flutter/cupertino.dart';

import 'app_float.dart';
import 'app_pressable.dart';

enum StateKind { empty, error }

/// Full-screen empty / error state (docs/screens/STATES.md).
///
/// Use for offline, server, session and similar screen-wide states. Inline
/// empty lists use `AppEmptyState` / `AppEmptyCard`.
class StateView extends StatelessWidget {
  final StateKind kind;
  final IconData icon;
  final String title;
  final String body;
  final String? primary;
  final IconData? primaryIcon;
  final String? secondary;
  final VoidCallback? onPrimary;
  final VoidCallback? onSecondary;

  /// Retry in progress: label "Trying…" with a spinner.
  final bool busy;

  const StateView({
    super.key,
    required this.kind,
    required this.icon,
    required this.title,
    required this.body,
    this.primary,
    this.primaryIcon,
    this.secondary,
    this.onPrimary,
    this.onSecondary,
    this.busy = false,
  });

  const StateView.offline({
    super.key,
    required this.title,
    required this.body,
    required this.primary,
    this.onPrimary,
    this.busy = false,
  }) : kind = StateKind.error,
       icon = FinoraIcons.offline,
       primaryIcon = FinoraIcons.refresh,
       secondary = null,
       onSecondary = null;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final isError = kind == StateKind.error;
    final tint = isError ? c.dangerSoft : c.tint;
    final solid = isError ? c.danger : AppPalette.primary500;
    final iconColor = isError ? AppPalette.white : AppPalette.primary950;
    final (btnBg, btnFg) = isError
        ? (c.textPrimary, c.surface)
        : (AppPalette.primary500, AppPalette.primary950);

    return Center(
      child: SingleChildScrollView(
        padding: const .symmetric(horizontal: 8, vertical: 16),
        child: ConstrainedBox(
          constraints: const BoxConstraints(minHeight: 460),
          child: Column(
            mainAxisAlignment: .center,
            spacing: 22,
            children: [
              _Illustration(
                tint: tint,
                solid: solid,
                icon: icon,
                iconColor: iconColor,
              ),
              ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 300),
                child: Column(
                  spacing: AppSpacing.sm,
                  children: [
                    Text(
                      title,
                      textAlign: .center,
                      style: context.textStyles.title.copyWith(
                        fontSize: 22,
                        height: 28 / 22,
                        fontWeight: .w700,
                        letterSpacing: -0.22,
                      ),
                    ),
                    Text(
                      body,
                      textAlign: .center,
                      style: context.textStyles.bodySecondary,
                    ),
                  ],
                ),
              ),
              if (primary != null || secondary != null)
                ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 300),
                  child: Column(
                    crossAxisAlignment: .stretch,
                    spacing: AppSpacing.sm,
                    children: [
                      if (primary != null)
                        AppPressable(
                          onTap: busy ? null : onPrimary,
                          child: Container(
                            height: AppSizes.button,
                            decoration: BoxDecoration(
                              color: btnBg,
                              borderRadius: .circular(AppRadius.lg),
                            ),
                            child: Row(
                              mainAxisAlignment: .center,
                              spacing: AppSpacing.sm,
                              children: [
                                if (busy)
                                  CupertinoActivityIndicator(
                                    color: btnFg,
                                    radius: 9,
                                  )
                                else if (primaryIcon != null)
                                  Icon(
                                    primaryIcon,
                                    size: AppSizes.iconTrailing,
                                    color: btnFg,
                                  ),
                                Text(
                                  busy ? Words.trying.str : primary!,
                                  style: AppTypography.button.copyWith(
                                    color: btnFg,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      if (secondary != null)
                        AppPressable(
                          onTap: onSecondary,
                          child: SizedBox(
                            height: 48,
                            child: Center(
                              child: Text(
                                secondary!,
                                style: AppTypography.button.copyWith(
                                  fontSize: 15,
                                  color: c.primaryText,
                                ),
                              ),
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Illustration extends StatefulWidget {
  final Color tint;
  final Color solid;
  final IconData icon;
  final Color iconColor;

  const _Illustration({
    required this.tint,
    required this.solid,
    required this.icon,
    required this.iconColor,
  });

  @override
  State<_Illustration> createState() => _IllustrationState();
}

class _IllustrationState extends State<_Illustration>
    with SingleTickerProviderStateMixin {
  // fnBreath: scale 1 → 1.06 → 1, 3s.
  late final _breath = AnimationController(
    vsync: this,
    duration: const Duration(seconds: 3),
  );

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (MediaQuery.disableAnimationsOf(context)) {
      _breath.stop();
    } else if (!_breath.isAnimating) {
      _breath.repeat();
    }
  }

  @override
  void dispose() {
    _breath.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final w = widget;

    Widget dot(double size, double opacity) => Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: w.solid.withValues(alpha: opacity),
        shape: BoxShape.circle,
      ),
    );

    return SizedBox.square(
      dimension: 176,
      child: Stack(
        children: [
          Positioned.fill(
            child: AnimatedBuilder(
              animation: _breath,
              builder: (_, child) => Transform.scale(
                scale: 1 + 0.06 * math.sin(math.pi * _breath.value),
                child: child,
              ),
              child: DecoratedBox(
                decoration: BoxDecoration(
                  color: w.tint.withValues(alpha: 0.55),
                  shape: BoxShape.circle,
                ),
              ),
            ),
          ),
          Positioned.fill(
            left: 28,
            top: 28,
            right: 28,
            bottom: 28,
            child: DecoratedBox(
              decoration: BoxDecoration(color: w.tint, shape: BoxShape.circle),
            ),
          ),
          Center(
            child: AppFloat(
              period: const Duration(milliseconds: 3500),
              distance: 6,
              child: Container(
                width: 78,
                height: 78,
                alignment: .center,
                decoration: BoxDecoration(
                  color: w.solid,
                  borderRadius: .circular(AppRadius.x2l),
                  boxShadow: const [
                    BoxShadow(
                      color: Color(0x24000000),
                      blurRadius: 30,
                      offset: Offset(0, 14),
                    ),
                  ],
                ),
                child: Icon(w.icon, size: 34, color: w.iconColor),
              ),
            ),
          ),
          Positioned(
            top: 16,
            right: 24,
            child: AppFloat(
              period: const Duration(milliseconds: 2800),
              delay: const Duration(milliseconds: 400),
              child: dot(12, 0.6),
            ),
          ),
          Positioned(
            bottom: 28,
            left: 14,
            child: AppFloat(
              period: const Duration(milliseconds: 3200),
              delay: const Duration(milliseconds: 900),
              child: dot(8, 0.5),
            ),
          ),
        ],
      ),
    );
  }
}
