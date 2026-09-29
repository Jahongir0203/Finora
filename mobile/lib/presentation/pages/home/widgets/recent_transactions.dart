import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:finora/application/finance/finance_cubit.dart';
import 'package:finora/common/theme/category_icons.dart';
import 'package:easy_localization/easy_localization.dart';
import 'package:finora/common/extensions/datetime_extensions.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_card.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/category_icon.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/domain/models/home/home_data.dart';
import 'package:flutter/material.dart';

import 'empty_card.dart';
import 'home_section_header.dart';

/// Header + last 4 transactions, or the empty card (§3.3).
class RecentTransactions extends StatelessWidget {
  final List<TransactionItem> transactions;
  final VoidCallback onSeeAll;
  final VoidCallback onAdd;

  const RecentTransactions({
    super.key,
    required this.transactions,
    required this.onSeeAll,
    required this.onAdd,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Column(
      crossAxisAlignment: .stretch,
      spacing: AppSpacing.md,
      children: [
        HomeSectionHeader(
          title: Words.recentTransactions.str,
          onSeeAll: onSeeAll,
        ),
        if (transactions.isEmpty)
          TransactionsEmptyCard(onAdd: onAdd)
        else
          AppCard(
            padding: const .symmetric(horizontal: 16, vertical: 4),
            child: Column(
              children: [
                for (final (i, t) in transactions.indexed)
                  AppFadeIn(
                    index: i,
                    step: const Duration(milliseconds: 60),
                    child: Container(
                      decoration: i == 0
                          ? null
                          : BoxDecoration(
                              border: Border(top: BorderSide(color: c.divider)),
                            ),
                      child: _TransactionRow(transaction: t),
                    ),
                  ),
              ],
            ),
          ),
      ],
    );
  }
}

class _TransactionRow extends StatelessWidget {
  final TransactionItem transaction;

  const _TransactionRow({required this.transaction});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final t = transaction;
    final category = context.select(
      (FinanceCubit b) => b.state.category(t.category),
    );
    final now = DateTime.now();
    final isToday =
        t.date.year == now.year &&
        t.date.month == now.month &&
        t.date.day == now.day;
    final when = isToday
        ? t.date.time24
        : DateFormat('d MMM', context.locale.languageCode).format(t.date);

    return Padding(
      padding: const .symmetric(vertical: 12),
      child: Row(
        spacing: AppSpacing.md,
        children: [
          category != null
              ? CategoryIcon(
                  icon: category.iconData,
                  color: category.colorValue,
                )
              : CategoryIcon(
                  icon: t.isIncome ? FinoraIcons.salary : FinoraIcons.wallet,
                  color: t.isIncome ? AppPalette.primary500 : c.textSecondary,
                ),
          Expanded(
            child: Column(
              crossAxisAlignment: .start,
              children: [
                Text(
                  t.title,
                  maxLines: 1,
                  overflow: .ellipsis,
                  style: context.textStyles.bodyMedium,
                ),
                Text(
                  '${t.categoryLabel} · $when',
                  maxLines: 1,
                  overflow: .ellipsis,
                  style: context.textStyles.caption,
                ),
              ],
            ),
          ),
          Text(
            t.amount.toMoney(sign: true),
            style: context.textStyles.amount.copyWith(
              color: t.isIncome ? c.primaryText : c.textPrimary,
            ),
          ),
        ],
      ),
    );
  }
}
