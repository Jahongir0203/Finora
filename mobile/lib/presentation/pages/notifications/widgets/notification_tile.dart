import 'package:easy_localization/easy_localization.dart';
import 'package:finora/common/extensions/datetime_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_banner.dart';
import 'package:finora/domain/models/notifications/app_notification.dart';
import 'package:flutter/material.dart';

extension NotificationTypeUi on NotificationType {
  IconData get icon => switch (this) {
    .paymentDue => FinoraIcons.reminder,
    .income => FinoraIcons.income,
    .budgetExceeded => FinoraIcons.warning,
    .weeklyReport => FinoraIcons.stats,
    .goalMilestone => FinoraIcons.savings,
    .security => FinoraIcons.security,
  };

  Color color(AppColorSchema c) => switch (this) {
    .paymentDue => c.warning,
    .income || .goalMilestone => AppPalette.primary500,
    .budgetExceeded => c.danger,
    .weeklyReport => c.info,
    .security => c.textSecondary,
  };
}

/// One notification row (§4).
class NotificationTile extends StatelessWidget {
  final AppNotification notification;

  /// Draws the top divider (every tile but the first in a group).
  final bool divided;
  final VoidCallback onTap;

  const NotificationTile({
    super.key,
    required this.notification,
    required this.divided,
    required this.onTap,
  });

  /// Today: `10:00`; ≤ 6 days: `Mon`; older: `20 Sep`.
  static String time(BuildContext context, DateTime date, DateTime now) {
    final days = DateTime.utc(
      now.year,
      now.month,
      now.day,
    ).difference(DateTime.utc(date.year, date.month, date.day)).inDays;
    final locale = context.locale.languageCode;
    if (days <= 0) return date.time24;
    if (days <= 6) return DateFormat.E(locale).format(date);
    return DateFormat('d MMM', locale).format(date);
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final n = notification;
    final color = n.type.color(c);

    return Semantics(
      button: true,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: onTap,
        child: Container(
          padding: const .symmetric(vertical: 14),
          decoration: divided
              ? BoxDecoration(
                  border: Border(top: BorderSide(color: c.divider)),
                )
              : null,
          child: Row(
            crossAxisAlignment: .start,
            spacing: AppSpacing.md,
            children: [
              Container(
                width: 40,
                height: 40,
                alignment: .center,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.12),
                  borderRadius: .circular(12),
                ),
                child: Icon(n.type.icon, size: AppSizes.iconMd, color: color),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: .start,
                  spacing: 3,
                  children: [
                    Row(
                      crossAxisAlignment: .start,
                      spacing: AppSpacing.sm,
                      children: [
                        Expanded(
                          child: Text(
                            n.title,
                            style: AppTypography.body.copyWith(
                              fontWeight: .w600,
                              color: c.textPrimary,
                            ),
                          ),
                        ),
                        Padding(
                          padding: const .only(top: 2),
                          child: Text(
                            time(context, n.createdAt, DateTime.now()),
                            style: AppTypography.label.copyWith(
                              fontWeight: .w400,
                              letterSpacing: 0,
                              color: c.textTertiary,
                            ),
                          ),
                        ),
                      ],
                    ),
                    Text(
                      n.body,
                      style: AppTypography.body.copyWith(
                        fontSize: 14,
                        height: 20 / 14,
                        color: c.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
              // 12px box with a 2px surface ring → 8px visible dot.
              Padding(
                padding: const .only(top: 4),
                child: SizedBox.square(
                  dimension: 12,
                  child: n.isRead ? null : AppUnreadDot(ringColor: c.surface),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
