import 'package:auto_route/auto_route.dart';
import 'package:flutter/material.dart';

import 'main_actions.dart';
import 'main_tab.dart';
import 'widgets/app_bottom_nav.dart';

/// Home · Activity · [+] · Stats · Budgets.
@RoutePage()
class TabsPage extends StatelessWidget {
  const TabsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return AutoTabsRouter(
      routes: [for (final tab in MainTab.values) tab.route],
      transitionBuilder: (_, child, animation) =>
          FadeTransition(opacity: animation, child: child),
      builder: (context, child) {
        final tabs = AutoTabsRouter.of(context);

        return Scaffold(
          // Pages scroll under the bar; the FAB overhangs it.
          extendBody: true,
          body: child,
          bottomNavigationBar: AppBottomNav(
            current: MainTab.values[tabs.activeIndex],
            onSelect: (tab) => tabs.setActiveIndex(tab.index),
            onAdd: () => MainActions.newTransaction(context),
          ),
        );
      },
    );
  }
}
