import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/words/words.dart';
import 'package:flutter/material.dart';

/// Add · Scan · Reminders · Goals (§3.3).
class QuickActions extends StatelessWidget {
  final VoidCallback onAdd;
  final VoidCallback onScan;
  final VoidCallback onReminders;
  final VoidCallback onGoals;

  const QuickActions({
    super.key,
    required this.onAdd,
    required this.onScan,
    required this.onReminders,
    required this.onGoals,
  });

  @override
  Widget build(BuildContext context) {
    final items = [
      (FinoraIcons.add, Words.add, onAdd),
      (FinoraIcons.scan, Words.scan, onScan),
      (FinoraIcons.reminder, Words.reminders, onReminders),
      (FinoraIcons.budgets, Words.goals, onGoals),
    ];

    return Row(
      crossAxisAlignment: .start,
      spacing: AppSpacing.sm,
      children: [
        for (final (i, (icon, label, onTap)) in items.indexed)
          Expanded(
            child: AppFadeIn(
              index: i,
              step: const Duration(milliseconds: 40),
              child: _QuickAction(icon: icon, label: label.str, onTap: onTap),
            ),
          ),
      ],
    );
  }
}

class _QuickAction extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _QuickAction({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return AppPressable(
      onTap: onTap,
      semanticLabel: label,
      child: Column(
        spacing: AppSpacing.sm,
        children: [
          Container(
            width: 56,
            height: 56,
            alignment: .center,
            decoration: BoxDecoration(
              color: c.surface,
              borderRadius: .circular(18),
              border: Border.all(color: c.border),
            ),
            child: Icon(
              icon,
              size: AppSizes.iconQuickAction,
              color: c.primaryText,
            ),
          ),
          ExcludeSemantics(
            child: Text(
              label,
              maxLines: 1,
              overflow: .ellipsis,
              style: AppTypography.bodyMedium.copyWith(
                fontSize: 13,
                height: 18 / 13,
                color: c.textSecondary,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
