import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

import 'app_amount_text.dart';
import 'app_pressable.dart';
import 'category_icon.dart';

/// 68px transaction row (docs/DESIGN_SYSTEM.md §6.8).
///
/// Income: `+` in `primaryText`. Expense: `−` in `textPrimary` (never red).
class TransactionTile extends StatelessWidget {
  final String title;
  final String subtitle;

  /// Signed amount: positive = income, negative = expense.
  final num amount;
  final IconData icon;
  final Color color;
  final VoidCallback? onTap;

  const TransactionTile({
    super.key,
    required this.title,
    required this.subtitle,
    required this.amount,
    required this.icon,
    required this.color,
    this.onTap,
  });

  TransactionTile.category({
    super.key,
    required this.title,
    required this.subtitle,
    required this.amount,
    required AppCategory category,
    this.onTap,
  }) : icon = category.icon,
       color = category.color;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final styles = context.textStyles;

    return AppPressable(
      onTap: onTap,
      scale: AppMotion.pressScaleCard,
      child: SizedBox(
        height: AppSizes.transactionRow,
        child: Row(
          spacing: AppSpacing.md,
          children: [
            CategoryIcon(icon: icon, color: color),
            Expanded(
              child: Column(
                mainAxisAlignment: .center,
                crossAxisAlignment: .start,
                spacing: 2,
                children: [
                  Text(
                    title,
                    style: styles.bodyMedium,
                    maxLines: 1,
                    overflow: .ellipsis,
                  ),
                  Text(
                    subtitle,
                    style: styles.caption,
                    maxLines: 1,
                    overflow: .ellipsis,
                  ),
                ],
              ),
            ),
            AppAmountText(
              amount,
              sign: true,
              showCurrency: false,
              color: amount > 0 ? c.primaryText : c.textPrimary,
            ),
          ],
        ),
      ),
    );
  }
}

/// 56px settings row (docs/DESIGN_SYSTEM.md §6.9).
class SettingsTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final String? value;
  final Widget? trailing;
  final VoidCallback? onTap;
  final bool destructive;

  const SettingsTile({
    super.key,
    required this.icon,
    required this.label,
    this.value,
    this.trailing,
    this.onTap,
    this.destructive = false,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final styles = context.textStyles;
    final fg = destructive ? c.danger : c.primaryText;

    return AppPressable(
      onTap: onTap,
      scale: AppMotion.pressScaleCard,
      child: SizedBox(
        height: AppSizes.settingsRow,
        child: Row(
          spacing: AppSpacing.md,
          children: [
            Container(
              width: 36,
              height: 36,
              alignment: .center,
              decoration: BoxDecoration(
                color: destructive ? c.dangerSoft : c.tint,
                borderRadius: .circular(12),
              ),
              child: Icon(icon, size: AppSizes.iconTrailing, color: fg),
            ),
            Expanded(
              child: Text(
                label,
                style: styles.bodyMedium.copyWith(
                  color: destructive ? c.danger : null,
                ),
              ),
            ),
            if (value != null)
              Text(
                value!,
                style: styles.body.copyWith(
                  fontSize: 14,
                  color: c.textTertiary,
                ),
              ),
            trailing ??
                (onTap != null
                    ? Icon(
                        FinoraIcons.forward,
                        size: AppSizes.iconTrailing,
                        color: c.textTertiary,
                      )
                    : const SizedBox.shrink()),
          ],
        ),
      ),
    );
  }
}

/// Card with rows separated by 1px `divider` (padding 4×16).
class AppListCard extends StatelessWidget {
  final List<Widget> children;
  final EdgeInsetsGeometry padding;

  const AppListCard({
    super.key,
    required this.children,
    this.padding = const EdgeInsets.symmetric(
      horizontal: AppSpacing.lg,
      vertical: AppSpacing.xs,
    ),
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Container(
      padding: padding,
      decoration: BoxDecoration(
        color: c.surface,
        borderRadius: .circular(AppRadius.xl),
        border: Border.all(color: c.border),
      ),
      child: Column(
        children: [
          for (var i = 0; i < children.length; i++) ...[
            if (i > 0) Divider(height: 1, color: c.divider),
            children[i],
          ],
        ],
      ),
    );
  }
}
