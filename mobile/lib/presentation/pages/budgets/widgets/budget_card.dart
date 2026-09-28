import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_card.dart';
import 'package:finora/common/widgets/app_progress_bar.dart';
import 'package:finora/common/widgets/category_chip.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:flutter/material.dart';

/// Category budget with progress (docs/screens/BUDGETS_GOALS.md §1.1).
class BudgetCard extends StatelessWidget {
  final Category category;
  final num spent;
  final Duration delay;
  final VoidCallback? onTap;

  const BudgetCard({
    super.key,
    required this.category,
    required this.spent,
    this.delay = Duration.zero,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final limit = category.limit ?? 0;
    final p = limit == 0 ? 0.0 : spent / limit;
    final over = p > 1;
    final left = limit - spent;
    const tabular = [FontFeature.tabularFigures()];

    return AppCard(
      onTap: onTap,
      child: Column(
        crossAxisAlignment: .stretch,
        spacing: AppSpacing.md,
        children: [
          Row(
            spacing: AppSpacing.md,
            children: [
              CategoryTile(category: category, size: 40, radius: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: .start,
                  children: [
                    Text(
                      category.name,
                      style: AppTypography.body.copyWith(
                        fontWeight: .w600,
                        color: c.textPrimary,
                      ),
                    ),
                    Text(
                      Words.spentOfLimit.tr(
                        args: [spent.toMoney(), limit.toMoney()],
                      ),
                      maxLines: 1,
                      overflow: .ellipsis,
                      style: AppTypography.caption.copyWith(
                        color: c.textSecondary,
                        fontFeatures: tabular,
                      ),
                    ),
                  ],
                ),
              ),
              Text(
                '${(p * 100).round()}%',
                style: AppTypography.body.copyWith(
                  fontWeight: .w600,
                  color: over ? c.danger : c.textPrimary,
                  fontFeatures: tabular,
                ),
              ),
            ],
          ),
          AppProgressBar(value: p, delay: delay),
          Text(
            over
                ? Words.overBy.tr(args: [(-left).toMoney()])
                : Words.uzsLeft.tr(args: [left.toMoney()]),
            style: AppTypography.caption.copyWith(
              fontWeight: .w500,
              color: over ? c.danger : c.textSecondary,
              fontFeatures: tabular,
            ),
          ),
        ],
      ),
    );
  }
}
