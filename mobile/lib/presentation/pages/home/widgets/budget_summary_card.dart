import 'package:easy_localization/easy_localization.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_card.dart';
import 'package:finora/common/widgets/app_progress_bar.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/domain/models/home/home_data.dart';
import 'package:flutter/material.dart';

/// "{Month} budget · {n} days left" with a progress bar (§3.3).
class BudgetSummaryCard extends StatelessWidget {
  final BudgetSummary budget;
  final VoidCallback onTap;

  const BudgetSummaryCard({
    super.key,
    required this.budget,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final month = DateFormat.MMMM(
      context.locale.languageCode,
    ).format(budget.month).capitalized;

    return AppCard(
      onTap: onTap,
      child: Column(
        crossAxisAlignment: .stretch,
        spacing: AppSpacing.md,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  Words.monthBudget.tr(args: [month]),
                  style: AppTypography.body.copyWith(
                    fontWeight: .w600,
                    color: c.textPrimary,
                  ),
                ),
              ),
              Text(
                Words.daysLeft.tr(args: ['${budget.daysLeft(DateTime.now())}']),
                style: AppTypography.caption.copyWith(color: c.textSecondary),
              ),
            ],
          ),
          Text.rich(
            TextSpan(
              text: budget.spent.toMoney(),
              style: AppTypography.titleSmall.copyWith(
                color: c.textPrimary,
                fontFeatures: const [FontFeature.tabularFigures()],
              ),
              children: [
                TextSpan(
                  text: Words.ofLimit.tr(args: [budget.limit.toMoney()]),
                  style: AppTypography.caption.copyWith(
                    color: c.textSecondary,
                    fontFeatures: const [FontFeature.tabularFigures()],
                  ),
                ),
              ],
            ),
          ),
          AppProgressBar(
            value: budget.progress,
            delay: const Duration(milliseconds: 200),
          ),
        ],
      ),
    );
  }
}

extension on String {
  String get capitalized =>
      isEmpty ? this : '${this[0].toUpperCase()}${substring(1)}';
}
