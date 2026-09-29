import 'dart:math' as math;

import 'package:easy_localization/easy_localization.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_float.dart';
import 'package:finora/common/widgets/app_progress_bar.dart';
import 'package:finora/common/words/words.dart';
import 'package:flutter/material.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

/// Onboarding illustrations built from UI cards (docs/AUTH_SCREENS.md §3).
///
/// Laid out at 342px and scaled down on small screens.
class OnboardingIllustration extends StatelessWidget {
  final int index;

  const OnboardingIllustration({super.key, required this.index});

  @override
  Widget build(BuildContext context) {
    final (first, second) = switch (index) {
      0 => (const _BalanceCard(), const _SavedCard()),
      1 => (const _BudgetsCard(), const _WarningCard()),
      _ => (const _ReminderCard(), const _RentCard()),
    };

    return Center(
      child: FittedBox(
        fit: BoxFit.scaleDown,
        child: SizedBox(
          width: 342,
          child: Column(
            mainAxisSize: .min,
            spacing: AppSpacing.md,
            children: [
              AppFloat(child: first),
              AppFloat(delay: const Duration(milliseconds: 800), child: second),
            ],
          ),
        ),
      ),
    );
  }
}

double _deg(double d) => d * math.pi / 180;

// ─── Slide 1 ─────────────────────────────────────────────────────────────────

class _BalanceCard extends StatelessWidget {
  const _BalanceCard();

  @override
  Widget build(BuildContext context) {
    return Transform.rotate(
      angle: _deg(-3),
      child: Container(
        padding: const .all(AppSpacing.xl),
        decoration: BoxDecoration(
          color: AppPalette.heroBlock,
          borderRadius: .circular(AppRadius.x2l),
        ),
        child: Column(
          crossAxisAlignment: .start,
          spacing: 14,
          children: [
            Text(
              Words.totalBalance.str.toUpperCase(),
              style: AppTypography.label.copyWith(color: AppPalette.primary200),
            ),
            Text.rich(
              TextSpan(
                text: 24850000.toMoney(),
                style: AppTypography.display.copyWith(
                  fontSize: 30,
                  height: 1.2,
                  color: Colors.white,
                ),
                children: [
                  TextSpan(
                    text: ' ${AppFormat.currency}',
                    style: AppTypography.bodyMedium.copyWith(
                      color: AppPalette.primary200,
                      letterSpacing: 0,
                    ),
                  ),
                ],
              ),
            ),
            const AppProgressBar(
              value: 0.68,
              color: AppPalette.primary500,
              trackColor: AppPalette.primary900,
            ),
          ],
        ),
      ),
    );
  }
}

class _SavedCard extends StatelessWidget {
  const _SavedCard();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const .symmetric(horizontal: 18),
      child: Transform.rotate(
        angle: _deg(2),
        child: _WhiteRow(
          radius: AppRadius.xl,
          leading: _IconBox(
            size: 40,
            radius: 12,
            color: AppPalette.tintOf(AppPalette.primary500),
            child: const Icon(
              FinoraIcons.savings,
              size: AppSizes.iconMd,
              color: AppPalette.primary700,
            ),
          ),
          child: Text(
            Words.savedThisMonth.tr(args: [1200000.toMoney()]),
            style: AppTypography.bodyMedium.copyWith(
              fontSize: 14,
              color: AppColors.light.textPrimary,
            ),
          ),
        ),
      ),
    );
  }
}

// ─── Slide 2 ─────────────────────────────────────────────────────────────────

class _BudgetsCard extends StatelessWidget {
  const _BudgetsCard();

  @override
  Widget build(BuildContext context) {
    final c = AppColors.light;
    final rows = [
      (Words.catGroceries.str, 0.74, const Duration(milliseconds: 200)),
      (Words.catTransport.str, 0.77, const Duration(milliseconds: 350)),
      (Words.catShopping.str, 0.52, const Duration(milliseconds: 500)),
    ];

    return Transform.rotate(
      angle: _deg(-2),
      child: Container(
        padding: const .all(18),
        decoration: BoxDecoration(
          color: c.surface,
          borderRadius: .circular(AppRadius.x2l),
        ),
        child: Column(
          crossAxisAlignment: .start,
          spacing: 14,
          children: [
            Text(
              Words.septemberBudgets.str,
              style: AppTypography.bodyMedium.copyWith(
                fontWeight: .w600,
                color: c.textPrimary,
              ),
            ),
            for (final (name, value, delay) in rows)
              Column(
                spacing: 6,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          name,
                          style: AppTypography.caption.copyWith(
                            color: c.textPrimary,
                          ),
                        ),
                      ),
                      Text(
                        '${(value * 100).round()}%',
                        style: AppTypography.caption.copyWith(
                          color: c.textSecondary,
                        ),
                      ),
                    ],
                  ),
                  AppProgressBar(
                    value: value,
                    delay: delay,
                    color: AppProgressBar.colorFor(value, c),
                    trackColor: c.divider,
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}

class _WarningCard extends StatelessWidget {
  const _WarningCard();

  @override
  Widget build(BuildContext context) {
    final c = AppColors.light;

    return Padding(
      padding: const .symmetric(horizontal: AppSpacing.x2l),
      child: Transform.rotate(
        angle: _deg(2),
        child: Container(
          padding: const .symmetric(horizontal: 14, vertical: AppSpacing.md),
          decoration: BoxDecoration(
            color: c.dangerSoft,
            borderRadius: .circular(18),
          ),
          child: Row(
            spacing: 10,
            children: [
              Icon(
                FinoraIcons.warning,
                size: AppSizes.iconTrailing,
                color: c.danger,
              ),
              Expanded(
                child: Text(
                  Words.foodBudgetUsed.tr(args: ['90']),
                  style: AppTypography.bodyMedium.copyWith(
                    fontSize: 14,
                    color: c.textPrimary,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─── Slide 3 ─────────────────────────────────────────────────────────────────

class _ReminderCard extends StatelessWidget {
  const _ReminderCard();

  @override
  Widget build(BuildContext context) {
    final c = AppColors.light;

    return Transform.rotate(
      angle: _deg(-2),
      child: _WhiteRow(
        radius: 22,
        leading: _IconBox(
          size: 44,
          radius: AppRadius.md,
          color: c.warningSoft,
          child: _RingingBell(color: c.warningText),
        ),
        child: _TwoLines(
          title: Words.electricityDueTomorrow.str,
          subtitle: '${142000.toUzs()} · ${Words.monthly.str}',
          titleColor: c.textPrimary,
          subtitleColor: c.textSecondary,
        ),
      ),
    );
  }
}

class _RentCard extends StatelessWidget {
  const _RentCard();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const .symmetric(horizontal: AppSpacing.lg),
      child: Transform.rotate(
        angle: _deg(2),
        child: Container(
          padding: const .symmetric(horizontal: AppSpacing.lg, vertical: 14),
          decoration: BoxDecoration(
            color: AppPalette.heroBlock,
            borderRadius: .circular(22),
          ),
          child: Row(
            spacing: AppSpacing.md,
            children: [
              _IconBox(
                size: 44,
                radius: AppRadius.md,
                color: AppPalette.primary900,
                child: Column(
                  mainAxisSize: .min,
                  children: [
                    Text(
                      DateFormat.MMM(
                        context.locale.toString(),
                      ).format(DateTime(2026, 10, 5)).toUpperCase(),
                      style: AppTypography.label.copyWith(
                        fontSize: 10,
                        height: 1.2,
                        letterSpacing: 0.3,
                        color: AppPalette.primary200,
                      ),
                    ),
                    Text(
                      '05',
                      style: AppTypography.bodyMedium.copyWith(
                        fontSize: 16,
                        height: 1.2,
                        fontWeight: .w700,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: _TwoLines(
                  title: Words.rent.str,
                  subtitle:
                      '${4500000.toUzs()} · ${Words.inDays.tr(args: ['7'])}',
                  titleColor: Colors.white,
                  subtitleColor: AppPalette.primary200,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─── Parts ───────────────────────────────────────────────────────────────────

class _WhiteRow extends StatelessWidget {
  final double radius;
  final Widget leading;
  final Widget child;

  const _WhiteRow({
    required this.radius,
    required this.leading,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const .symmetric(horizontal: AppSpacing.lg, vertical: 14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: .circular(radius),
      ),
      child: Row(
        spacing: AppSpacing.md,
        children: [
          leading,
          Expanded(child: child),
        ],
      ),
    );
  }
}

class _IconBox extends StatelessWidget {
  final double size;
  final double radius;
  final Color color;
  final Widget child;

  const _IconBox({
    required this.size,
    required this.radius,
    required this.color,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      alignment: .center,
      decoration: BoxDecoration(color: color, borderRadius: .circular(radius)),
      child: child,
    );
  }
}

class _TwoLines extends StatelessWidget {
  final String title;
  final String subtitle;
  final Color titleColor;
  final Color subtitleColor;

  const _TwoLines({
    required this.title,
    required this.subtitle,
    required this.titleColor,
    required this.subtitleColor,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: .start,
      mainAxisSize: .min,
      spacing: 2,
      children: [
        Text(
          title,
          maxLines: 1,
          overflow: .ellipsis,
          style: AppTypography.bodyMedium.copyWith(
            fontWeight: .w600,
            color: titleColor,
          ),
        ),
        Text(
          subtitle,
          maxLines: 1,
          overflow: .ellipsis,
          style: AppTypography.caption.copyWith(
            color: subtitleColor,
            fontFeatures: const [FontFeature.tabularFigures()],
          ),
        ),
      ],
    );
  }
}

/// `bell-ring` swinging 0° → 14° → −12° → 8° → −4° → 0° during 70–90% of a
/// 2400ms loop.
class _RingingBell extends StatefulWidget {
  final Color color;

  const _RingingBell({required this.color});

  @override
  State<_RingingBell> createState() => _RingingBellState();
}

class _RingingBellState extends State<_RingingBell>
    with SingleTickerProviderStateMixin {
  static final _angle = TweenSequence<double>([
    TweenSequenceItem(tween: ConstantTween(0), weight: 70),
    for (final (a, b) in const [
      (0.0, 14.0),
      (14.0, -12.0),
      (-12.0, 8.0),
      (8.0, -4.0),
      (-4.0, 0.0),
    ])
      TweenSequenceItem(
        tween: Tween(begin: a, end: b),
        weight: 4,
      ),
    TweenSequenceItem(tween: ConstantTween(0), weight: 10),
  ]);

  late final _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 2400),
  );

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (MediaQuery.disableAnimationsOf(context)) {
      _controller.stop();
      _controller.value = 0;
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
    return AnimatedBuilder(
      animation: _controller,
      builder: (_, child) => Transform.rotate(
        angle: _deg(_angle.transform(_controller.value)),
        alignment: Alignment.topCenter,
        child: child,
      ),
      child: Icon(
        LucideIcons.bellRing,
        size: AppSizes.iconMd,
        color: widget.color,
      ),
    );
  }
}
