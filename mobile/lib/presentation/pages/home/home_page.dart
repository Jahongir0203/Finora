import 'package:auto_route/auto_route.dart';
import 'package:easy_localization/easy_localization.dart';
import 'package:finora/application/home/home_cubit.dart';
import 'package:finora/application/network_info/network_info_cubit.dart';
import 'package:finora/application/notifications/notifications_cubit.dart';
import 'package:finora/common/extensions/datetime_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_banner.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/domain/models/home/home_data.dart';
import 'package:finora/presentation/pages/main/main_actions.dart';
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'widgets/ai_insight_card.dart';
import 'widgets/budget_summary_card.dart';
import 'widgets/get_started_card.dart';
import 'widgets/home_hero.dart';
import 'widgets/quick_actions.dart';
import 'widgets/recent_transactions.dart';
import 'widgets/upcoming_payments.dart';

/// Home tab (docs/screens/HOME_SCREENS.md §3).
@RoutePage()
class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final _scroll = ScrollController();

  @override
  void dispose() {
    _scroll.dispose();
    super.dispose();
  }

  SystemUiOverlayStyle _overlay(AppColorSchema c) =>
      SystemUiOverlayStyle.light.copyWith(
        statusBarColor: Colors.transparent,
        systemNavigationBarColor: c.surface,
        systemNavigationBarIconBrightness: context.isDark
            ? Brightness.light
            : Brightness.dark,
      );

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final hasUnread = context.select(
      (NotificationsCubit b) => b.state.hasUnread,
    );

    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: _overlay(c),
      child: BlocListener<HomeCubit, HomeState>(
        listenWhen: (a, b) => a.failureTick != b.failureTick,
        listener: (_, _) => AppToast.error(Words.happenError.str),
        child: Scaffold(
          backgroundColor: c.background,
          body: BlocBuilder<HomeCubit, HomeState>(
            builder: (context, state) {
              final data = state.data;
              final cubit = context.read<HomeCubit>();

              return Stack(
                children: [
                  // Dark backdrop for the top overscroll bounce.
                  const Positioned(
                    top: 0,
                    left: 0,
                    right: 0,
                    height: 360,
                    child: ColoredBox(color: AppPalette.primary950),
                  ),
                  AppFadeIn(
                    child: CustomScrollView(
                      controller: _scroll,
                      slivers: [
                        // One sliver: the viewport paints earlier slivers on
                        // top, and the panel has to overlap the hero.
                        SliverToBoxAdapter(
                          child: Column(
                            crossAxisAlignment: .stretch,
                            children: [
                              HomeHero(
                                scroll: _scroll,
                                userName: data?.userName ?? '',
                                balance: data?.balance ?? 0,
                                income: data?.monthIncome ?? 0,
                                expenses: data?.monthExpenses ?? 0,
                                balanceHidden: state.balanceHidden,
                                needBalance: data?.needBalance ?? false,
                                hasUnread: hasUnread,
                                onToggleBalance: cubit.toggleBalance,
                                onAddBalance: () =>
                                    MainActions.balance(context),
                                onBell: () =>
                                    MainActions.notifications(context),
                                onAvatar: () => MainActions.profile(context),
                              ),
                              // Panel overlaps the hero by 24px.
                              Transform.translate(
                                offset: const Offset(0, -24),
                                child: _Content(
                                  data: data,
                                  isLoading: state.isLoading,
                                  onRetry: cubit.load,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  Positioned(
                    top: 0,
                    left: 0,
                    right: 0,
                    child: HomeCollapsedBar(
                      scroll: _scroll,
                      userName: data?.userName ?? '',
                      balance: data?.balance ?? 0,
                      balanceHidden: state.balanceHidden,
                      onAdd: () => MainActions.newTransaction(context),
                      onAvatar: () => MainActions.profile(context),
                    ),
                  ),
                ],
              );
            },
          ),
        ),
      ),
    );
  }
}

class _Content extends StatelessWidget {
  final HomeData? data;
  final bool isLoading;
  final VoidCallback onRetry;

  const _Content({
    required this.data,
    required this.isLoading,
    required this.onRetry,
  });

  static const _gap = 22.0;

  void _onStep(BuildContext context, ChecklistStep step) => switch (step) {
    .balance => MainActions.balance(context),
    .transaction => MainActions.newTransaction(context),
    .goal => MainActions.goals(context, create: true),
    .reminder => MainActions.reminders(context, create: true),
  };

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final data = this.data;
    final isOffline = context.select(
      (NetworkInfoCubit b) => !b.state.isConnected,
    );
    // The panel is shifted up 24px, so that much of the bottom inset is free.
    final bottom = 28 + MediaQuery.paddingOf(context).bottom - 24;

    Widget padded(Widget child) =>
        Padding(padding: AppSpacing.screenPadding, child: child);

    return Container(
      padding: .only(top: _gap, bottom: bottom),
      decoration: BoxDecoration(
        color: c.background,
        borderRadius: const .vertical(top: .circular(AppRadius.sheet)),
      ),
      child: Column(
        crossAxisAlignment: .stretch,
        children: [
          if (isOffline && data != null) ...[
            padded(
              AppOfflineBanner(
                message: Words.offlineSince.tr(args: [data.fetchedAt.time24]),
                onRetry: () {
                  AppToast.info(Words.reconnecting.str);
                  onRetry();
                },
              ),
            ),
            const SizedBox(height: _gap),
          ],
          padded(
            QuickActions(
              onAdd: () => MainActions.newTransaction(context),
              onScan: () => MainActions.scan(context),
              onReminders: () => MainActions.reminders(context),
              onGoals: () => MainActions.goals(context),
            ),
          ),
          const SizedBox(height: _gap),
          if (data == null)
            padded(
              Padding(
                padding: const .symmetric(vertical: AppSpacing.x3l),
                child: isLoading
                    ? const CupertinoActivityIndicator()
                    : Center(
                        child: AppButton.secondary(
                          text: Words.retry.str,
                          expanded: false,
                          onPressed: onRetry,
                        ),
                      ),
              ),
            )
          else ...[
            // Fades and collapses away once all 4 steps are done.
            AnimatedSwitcher(
              duration: AppMotion.push,
              switchInCurve: AppMotion.ease,
              switchOutCurve: AppMotion.ease,
              transitionBuilder: (child, animation) => SizeTransition(
                sizeFactor: animation,
                alignment: Alignment.topCenter,
                child: FadeTransition(opacity: animation, child: child),
              ),
              child: data.showChecklist
                  ? Padding(
                      key: const ValueKey('checklist'),
                      padding: const .fromLTRB(20, 0, 20, _gap),
                      child: AppFadeIn(
                        delay: const Duration(milliseconds: 100),
                        duration: const Duration(milliseconds: 500),
                        child: GetStartedCard(
                          data: data,
                          onStep: (step) => _onStep(context, step),
                        ),
                      ),
                    )
                  : const SizedBox(width: double.infinity),
            ),
            if (data.showInsights && data.aiSavingAmount != null) ...[
              padded(
                AppFadeIn(
                  delay: const Duration(milliseconds: 150),
                  duration: const Duration(milliseconds: 500),
                  child: AiInsightCard(
                    amount: data.aiSavingAmount!,
                    onTap: () => MainActions.insights(context),
                  ),
                ),
              ),
              const SizedBox(height: _gap),
            ],
            if (data.showInsights && data.budget != null) ...[
              padded(
                BudgetSummaryCard(
                  budget: data.budget!,
                  onTap: () => MainActions.openTab(context, .budgets),
                ),
              ),
              const SizedBox(height: _gap),
            ],
            UpcomingPayments(
              payments: data.upcomingPayments,
              onSeeAll: () => MainActions.reminders(context),
              onAddReminder: () => MainActions.reminders(context, create: true),
              onPayment: (_) => MainActions.reminders(context),
            ),
            const SizedBox(height: _gap),
            padded(
              RecentTransactions(
                transactions: data.recentTransactions,
                onSeeAll: () => MainActions.openTab(context, .activity),
                onAdd: () => MainActions.newTransaction(context),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
