import 'dart:math' as math;

import 'package:easy_localization/easy_localization.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_card.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/domain/models/home/home_data.dart';
import 'package:flutter/material.dart';

/// New-user checklist with a progress ring (§3.3).
class GetStartedCard extends StatelessWidget {
  final HomeData data;
  final ValueChanged<ChecklistStep> onStep;

  const GetStartedCard({super.key, required this.data, required this.onStep});

  static (String, String) _texts(ChecklistStep step) => switch (step) {
    .balance => (Words.stepBalanceTitle, Words.stepBalanceSub),
    .transaction => (Words.stepTransactionTitle, Words.stepTransactionSub),
    .goal => (Words.stepGoalTitle, Words.stepGoalSub),
    .reminder => (Words.stepReminderTitle, Words.stepReminderSub),
  };

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final total = ChecklistStep.values.length;
    final done = data.checklistDone;

    return AppCard(
      padding: const .fromLTRB(16, 16, 16, 6),
      child: Column(
        crossAxisAlignment: .stretch,
        spacing: AppSpacing.xs,
        children: [
          Padding(
            padding: const .only(bottom: 10),
            child: Row(
              spacing: AppSpacing.md,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: .start,
                    children: [
                      Text(
                        Words.checklistTitle.str,
                        style: context.textStyles.titleSmall,
                      ),
                      Text(
                        Words.checklistProgress.tr(args: ['$done', '$total']),
                        style: AppTypography.caption.copyWith(
                          color: c.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
                _ProgressRing(value: done / total),
              ],
            ),
          ),
          for (final step in ChecklistStep.values)
            _StepRow(
              title: _texts(step).$1.str,
              subtitle: _texts(step).$2.str,
              done: data.isStepDone(step),
              onTap: () => onStep(step),
            ),
        ],
      ),
    );
  }
}

class _StepRow extends StatelessWidget {
  final String title;
  final String subtitle;
  final bool done;
  final VoidCallback onTap;

  const _StepRow({
    required this.title,
    required this.subtitle,
    required this.done,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    final row = Container(
      padding: const .symmetric(vertical: 10),
      decoration: BoxDecoration(
        border: Border(top: BorderSide(color: c.divider)),
      ),
      child: Row(
        spacing: AppSpacing.md,
        children: [
          AnimatedContainer(
            duration: AppMotion.fast,
            width: 26,
            height: 26,
            alignment: .center,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: done ? c.primary : null,
              border: done ? null : Border.all(color: c.border, width: 2),
            ),
            child: done
                ? Icon(FinoraIcons.check, size: 14, color: c.onPrimary)
                : null,
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: .start,
              children: [
                Text(
                  title,
                  style: AppTypography.bodyMedium.copyWith(
                    color: done ? c.textTertiary : c.textPrimary,
                    decoration: done ? TextDecoration.lineThrough : null,
                    decorationColor: c.textTertiary,
                  ),
                ),
                Text(
                  subtitle,
                  style: AppTypography.caption.copyWith(color: c.textTertiary),
                ),
              ],
            ),
          ),
          if (!done)
            Icon(
              FinoraIcons.forward,
              size: AppSizes.iconTrailing,
              color: c.textTertiary,
            ),
        ],
      ),
    );

    return Semantics(
      checked: done,
      child: done
          ? row
          : AppPressable(
              onTap: onTap,
              scale: AppMotion.pressScaleCard,
              child: row,
            ),
    );
  }
}

/// 44×44 ring: `primary500` sweep over a `divider` track, percent inside.
class _ProgressRing extends StatelessWidget {
  final double value;

  const _ProgressRing({required this.value});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return TweenAnimationBuilder<double>(
      tween: Tween(end: value),
      duration: AppMotion.bar,
      curve: AppMotion.ease,
      builder: (_, v, _) => CustomPaint(
        painter: _RingPainter(value: v, color: c.primary, track: c.divider),
        child: SizedBox.square(
          dimension: 44,
          child: Center(
            child: Text(
              '${(value * 100).round()}%',
              style: AppTypography.label.copyWith(
                letterSpacing: 0,
                fontWeight: .w700,
                fontFeatures: const [FontFeature.tabularFigures()],
                color: c.primaryText,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _RingPainter extends CustomPainter {
  final double value;
  final Color color;
  final Color track;

  const _RingPainter({
    required this.value,
    required this.color,
    required this.track,
  });

  // 44 outer, 34 inner → 5px ring.
  static const _stroke = 5.0;

  @override
  void paint(Canvas canvas, Size size) {
    final rect = (Offset.zero & size).deflate(_stroke / 2);
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = _stroke;

    canvas.drawArc(rect, 0, math.pi * 2, false, paint..color = track);
    if (value > 0) {
      canvas.drawArc(
        rect,
        -math.pi / 2,
        math.pi * 2 * value.clamp(0, 1),
        false,
        paint..color = color,
      );
    }
  }

  @override
  bool shouldRepaint(_RingPainter old) =>
      old.value != value || old.color != color || old.track != track;
}
