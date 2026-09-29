import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_card.dart';
import 'package:finora/common/widgets/app_empty_state.dart';
import 'package:finora/common/words/words.dart';
import 'package:flutter/material.dart';

/// "No payments scheduled" row; the whole card is tappable (§3.4).
class PaymentsEmptyCard extends StatelessWidget {
  final VoidCallback onTap;

  const PaymentsEmptyCard({super.key, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return AppCard.dashed(
      onTap: onTap,
      padding: const .symmetric(horizontal: 16, vertical: 14),
      child: Row(
        spacing: AppSpacing.md,
        children: [
          const _IconTile(icon: FinoraIcons.addReminder, size: 40, radius: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: .start,
              children: [
                Text(
                  Words.noPaymentsTitle.str,
                  style: AppTypography.body.copyWith(
                    fontWeight: .w600,
                    color: c.textPrimary,
                  ),
                ),
                Text(
                  Words.noPaymentsDesc.str,
                  style: AppTypography.caption.copyWith(color: c.textSecondary),
                ),
              ],
            ),
          ),
          Icon(
            FinoraIcons.add,
            size: AppSizes.iconTrailing,
            color: c.primaryText,
          ),
        ],
      ),
    );
  }
}

/// "No transactions yet" with an "Add transaction" button (§3.4).
class TransactionsEmptyCard extends StatelessWidget {
  final VoidCallback onAdd;

  const TransactionsEmptyCard({super.key, required this.onAdd});

  @override
  Widget build(BuildContext context) => AppEmptyCard(
    icon: FinoraIcons.receipt,
    title: Words.noTransactionsTitle.str,
    message: Words.noTransactionsDesc.str,
    actionText: Words.addTransaction.str,
    onAction: onAdd,
  );
}

class _IconTile extends StatelessWidget {
  final IconData icon;
  final double size;
  final double radius;
  final double iconSize = AppSizes.iconMd;

  const _IconTile({
    required this.icon,
    required this.size,
    required this.radius,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Container(
      width: size,
      height: size,
      alignment: .center,
      decoration: BoxDecoration(color: c.tint, borderRadius: .circular(radius)),
      child: Icon(icon, size: iconSize, color: c.primaryText),
    );
  }
}
