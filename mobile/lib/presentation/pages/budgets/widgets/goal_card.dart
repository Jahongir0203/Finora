import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/category_icons.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/widgets/app_progress_bar.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:flutter/material.dart';

/// Savings goal tile; the first goal uses the dark [hero] style (§1.2).
class GoalCard extends StatelessWidget {
  final Goal goal;
  final bool hero;
  final VoidCallback onTap;

  const GoalCard({
    super.key,
    required this.goal,
    required this.onTap,
    this.hero = false,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final fg = hero ? AppPalette.white : c.textPrimary;
    final sub = hero ? AppPalette.primary200 : c.textSecondary;
    final due = DateFormat(
      'MMM y',
      context.locale.languageCode,
    ).format(goal.due);

    return AppPressable(
      onTap: onTap,
      scale: 0.97,
      child: Container(
        padding: const .all(16),
        decoration: BoxDecoration(
          color: hero ? AppPalette.primary900 : c.surface,
          borderRadius: .circular(AppRadius.xl),
          border: Border.all(color: hero ? AppPalette.primary900 : c.border),
        ),
        child: Column(
          crossAxisAlignment: .stretch,
          spacing: AppSpacing.md,
          children: [
            Row(
              children: [
                Container(
                  width: 40,
                  height: 40,
                  alignment: .center,
                  decoration: BoxDecoration(
                    color: hero ? AppPalette.primary500 : c.tint,
                    borderRadius: .circular(12),
                  ),
                  child: Icon(
                    goal.iconData,
                    size: AppSizes.iconMd,
                    color: hero ? AppPalette.primary950 : c.primaryText,
                  ),
                ),
                const Spacer(),
                Text(
                  '${(goal.progress * 100).round()}%',
                  style: AppTypography.caption.copyWith(
                    fontWeight: .w600,
                    color: hero ? AppPalette.primary200 : c.textSecondary,
                  ),
                ),
              ],
            ),
            Column(
              crossAxisAlignment: .start,
              children: [
                Text(
                  goal.name,
                  maxLines: 1,
                  overflow: .ellipsis,
                  style: AppTypography.body.copyWith(
                    fontWeight: .w600,
                    color: fg,
                  ),
                ),
                Text(
                  '${goal.saved.toShort()} / ${goal.target.toShort()} · $due',
                  style: AppTypography.caption.copyWith(
                    color: sub,
                    fontFeatures: const [FontFeature.tabularFigures()],
                  ),
                ),
              ],
            ),
            AppProgressBar(
              value: goal.progress,
              height: 6,
              color: AppPalette.primary500,
              onDark: hero,
            ),
          ],
        ),
      ),
    );
  }
}
