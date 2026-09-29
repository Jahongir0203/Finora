import 'package:auto_route/auto_route.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/presentation/routes/app_router.dart';
import 'package:flutter/widgets.dart';

/// Bottom navigation tabs (docs/screens/HOME_SCREENS.md §2).
enum MainTab {
  home(FinoraIcons.home, Words.navHome, HomeRoute()),
  activity(FinoraIcons.activity, Words.navActivity, ActivityRoute()),
  stats(FinoraIcons.stats, Words.navStats, StatsRoute()),
  budgets(FinoraIcons.budgets, Words.navBudgets, BudgetsRoute());

  final IconData icon;
  final String label;
  final PageRouteInfo route;

  const MainTab(this.icon, this.label, this.route);
}
