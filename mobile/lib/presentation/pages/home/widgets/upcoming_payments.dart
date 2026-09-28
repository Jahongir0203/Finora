import 'package:easy_localization/easy_localization.dart';
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

/// Header + horizontal payment cards, or the empty card (§3.3).
///
/// Pads itself so the card list can scroll edge to edge.
class UpcomingPayments extends StatelessWidget {
  final List<UpcomingPayment> payments;
  final VoidCallback onSeeAll;
  final VoidCallback onAddReminder;
  final ValueChanged<UpcomingPayment> onPayment;

  const UpcomingPayments({
    super.key,
    required this.payments,
    required this.onSeeAll,
    required this.onAddReminder,
    required this.onPayment,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: .stretch,
      spacing: AppSpacing.md,
      children: [
        Padding(
          padding: AppSpacing.screenPadding,
          child: HomeSectionHeader(
            title: Words.upcomingPayments.str,
            onSeeAll: onSeeAll,
          ),
        ),
        if (payments.isEmpty)
          Padding(
            padding: AppSpacing.screenPadding,
            child: PaymentsEmptyCard(onTap: onAddReminder),
          )
        else
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: AppSpacing.screenPadding,
            child: IntrinsicHeight(
              child: Row(
                crossAxisAlignment: .stretch,
                spacing: 10,
                children: [
                  for (final (i, p) in payments.indexed)
                    AppFadeIn(
                      index: i,
                      horizontal: true,
                      step: const Duration(milliseconds: 60),
                      duration: const Duration(milliseconds: 500),
                      child: _PaymentCard(
                        payment: p,
                        onTap: () => onPayment(p),
                      ),
                    ),
                ],
              ),
            ),
          ),
      ],
    );
  }
}

class _PaymentCard extends StatelessWidget {
  final UpcomingPayment payment;
  final VoidCallback onTap;

  const _PaymentCard({required this.payment, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final category = AppCategory.byName(payment.category) ?? .bills;
    final (due, dueColor) = dueLabel(context, payment.dueDate, DateTime.now());

    return SizedBox(
      width: 164,
      child: AppCard(
        onTap: onTap,
        padding: const .all(14),
        child: Column(
          crossAxisAlignment: .start,
          spacing: 10,
          children: [
            CategoryIcon.category(category, size: 36),
            Column(
              crossAxisAlignment: .start,
              children: [
                Text(
                  payment.title,
                  maxLines: 1,
                  overflow: .ellipsis,
                  style: AppTypography.body.copyWith(
                    fontWeight: .w600,
                    color: c.textPrimary,
                  ),
                ),
                Text(
                  payment.amount.toUzs(),
                  maxLines: 1,
                  overflow: .ellipsis,
                  style: AppTypography.body.copyWith(
                    fontSize: 14,
                    height: 20 / 14,
                    color: c.textSecondary,
                    fontFeatures: const [FontFeature.tabularFigures()],
                  ),
                ),
              ],
            ),
            Text(
              due,
              style: AppTypography.label.copyWith(
                letterSpacing: 0,
                color: dueColor,
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Due today / Due tomorrow / In {n} days (≤14) / {d} {Mon}.
  static (String, Color) dueLabel(
    BuildContext context,
    DateTime due,
    DateTime now,
  ) {
    final c = context.appColors;
    final days = DateTime.utc(
      due.year,
      due.month,
      due.day,
    ).difference(DateTime.utc(now.year, now.month, now.day)).inDays;

    if (days <= 0) return (Words.dueToday.str, c.danger);
    if (days == 1) return (Words.dueTomorrow.str, c.warning);
    if (days <= 14) {
      return (Words.dueInDays.tr(args: ['$days']), c.textSecondary);
    }
    return (
      DateFormat('d MMM', context.locale.languageCode).format(due),
      c.textTertiary,
    );
  }
}
