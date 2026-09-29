import 'package:finora/application/finance/finance_cubit.dart';
import 'package:finora/common/extensions/datetime_extensions.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/category_icons.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_list_tiles.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

/// "Today ··· +12 313 600 UZS" + a card of transactions (§2.1, §2.4).
class DayGroup extends StatelessWidget {
  final String label;
  final num total;
  final List<Transaction> transactions;

  /// Index of the first row across the whole list (entrance stagger).
  final int firstIndex;

  const DayGroup({
    super.key,
    required this.label,
    required this.total,
    required this.transactions,
    this.firstIndex = 0,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final snapshot = context.watch<FinanceCubit>().state;
    final meta = AppTypography.caption.copyWith(
      fontWeight: .w600,
      color: c.textSecondary,
    );

    return Column(
      crossAxisAlignment: .stretch,
      spacing: AppSpacing.sm,
      children: [
        Padding(
          padding: const .symmetric(horizontal: AppSpacing.xs),
          child: Row(
            children: [
              Expanded(child: Text(label, style: meta)),
              Text(
                '${total.toMoney(sign: true)} ${AppFormat.currency}',
                style: meta.copyWith(
                  fontWeight: .w400,
                  fontFeatures: const [FontFeature.tabularFigures()],
                ),
              ),
            ],
          ),
        ),
        AppListCard(
          children: [
            for (final (i, t) in transactions.indexed)
              AppFadeIn(
                key: ValueKey(t.id),
                index: firstIndex + i,
                step: const Duration(milliseconds: 40),
                child: Builder(
                  builder: (context) {
                    final category = snapshot.category(t.categoryId);
                    return TransactionTile(
                      title: t.title,
                      subtitle: '${category?.name ?? ''} · ${t.date.time24}',
                      amount: t.amount,
                      icon: category?.iconData ?? FinoraIcons.wallet,
                      color: category?.colorValue ?? c.textSecondary,
                    );
                  },
                ),
              ),
          ],
        ),
      ],
    );
  }
}
