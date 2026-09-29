import 'package:auto_route/auto_route.dart';
import 'package:finora/domain/models/notifications/app_notification.dart';
import 'package:finora/presentation/pages/activity/widgets/add_transaction_sheet.dart';
import 'package:finora/presentation/pages/activity/widgets/export_sheet.dart';
import 'package:finora/presentation/pages/goals/widgets/new_goal_sheet.dart';
import 'package:finora/presentation/pages/home/widgets/balance_sheet.dart';
import 'package:finora/presentation/routes/app_router.dart';
import 'package:flutter/widgets.dart';

import 'main_tab.dart';

/// Destinations reached from Home, Notifications and the tab bar.
abstract final class MainActions {
  static void openTab(BuildContext context, MainTab tab) =>
      context.router.navigate(TabsRoute(children: [tab.route]));

  static void notifications(BuildContext context) =>
      context.router.navigate(const NotificationsRoute());

  static Future<void> balance(BuildContext context) =>
      BalanceSheet.show(context);

  static Future<void> newTransaction(BuildContext context) =>
      AddTransactionSheet.show(context);

  static Future<void> export(BuildContext context) => ExportSheet.show(context);

  static void scan(BuildContext context) =>
      context.router.navigate(const ScanRoute());

  static void reminders(BuildContext context, {bool create = false}) =>
      context.router.navigate(RemindersRoute(create: create));

  static void goals(BuildContext context, {bool create = false}) {
    openTab(context, .budgets);
    if (create) NewGoalSheet.show(context);
  }

  static void insights(BuildContext context) =>
      context.router.navigate(const InsightsRoute());

  static void profile(BuildContext context) =>
      context.router.navigate(const ProfileRoute());

  static void forNotification(BuildContext context, NotificationType type) {
    switch (type) {
      case .paymentDue:
        reminders(context);
      case .income:
        openTab(context, .activity);
      case .budgetExceeded || .goalMilestone:
        openTab(context, .budgets);
      case .weeklyReport:
        openTab(context, .stats);
      case .security:
        profile(context);
    }
  }
}
