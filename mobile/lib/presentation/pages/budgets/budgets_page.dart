import 'package:auto_route/auto_route.dart';
import 'package:finora/application/finance/finance_cubit.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_empty_state.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:finora/presentation/pages/goals/widgets/new_goal_sheet.dart';
import 'package:finora/presentation/pages/profile/widgets/category_sheet.dart';
import 'package:finora/presentation/routes/app_router.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'widgets/budget_card.dart';
import 'widgets/goal_card.dart';

/// Budgets & goals tab (docs/screens/BUDGETS_GOALS.md §1).
@RoutePage()
class BudgetsPage extends StatelessWidget {
  const BudgetsPage({super.key});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final s = context.watch<FinanceCubit>().state;
    final budgets = s.budgets.toList();
    final goals = s.goals;

    void openGoal(String id) =>
        context.router.navigate(GoalDetailsRoute(goalId: id));

    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: authOverlayStyle(context),
      child: Scaffold(
        backgroundColor: c.background,
        body: SafeArea(
          bottom: false,
          child: AppFadeIn(
            child: ListView(
              padding: .fromLTRB(
                20,
                8,
                20,
                28 + MediaQuery.paddingOf(context).bottom,
              ),
              children: [
                TabHeader(title: Words.budgetsAndGoals.str),
                const SizedBox(height: AppSpacing.lg),
                if (budgets.isEmpty)
                  AppEmptyCard(
                    icon: FinoraIcons.budgets,
                    title: Words.noBudgets.str,
                    message: Words.noBudgetsDesc.str,
                    actionText: Words.setALimit.str,
                    onAction: () =>
                        context.router.navigate(const CategoriesRoute()),
                  )
                else
                  for (final (i, b) in budgets.indexed)
                    Padding(
                      padding: const .only(bottom: 10),
                      child: AppFadeIn(
                        index: i,
                        step: const Duration(milliseconds: 70),
                        child: BudgetCard(
                          category: b,
                          spent: s.monthSpent[b.id] ?? 0,
                          delay: Duration(milliseconds: 70 * i),
                          onTap: () => CategorySheet.show(context, category: b),
                        ),
                      ),
                    ),
                const SizedBox(height: AppSpacing.lg),
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        Words.savingsGoals.str,
                        style: context.textStyles.titleSmall,
                      ),
                    ),
                    AppPressable(
                      onTap: () => NewGoalSheet.show(context),
                      child: Container(
                        height: AppSizes.buttonPill,
                        padding: const .symmetric(horizontal: 14),
                        decoration: BoxDecoration(
                          color: c.tint,
                          borderRadius: .circular(AppRadius.full),
                        ),
                        child: Row(
                          mainAxisSize: .min,
                          spacing: 6,
                          children: [
                            Icon(
                              FinoraIcons.add,
                              size: AppSizes.iconSm,
                              color: c.primaryText,
                            ),
                            Text(
                              Words.newGoal.str,
                              style: AppTypography.button.copyWith(
                                fontSize: 14,
                                color: c.primaryText,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.lg),
                if (goals.isEmpty)
                  AppEmptyCard(
                    icon: FinoraIcons.savings,
                    title: Words.noGoals.str,
                    message: Words.noGoalsDesc.str,
                    actionText: Words.newGoal.str,
                    onAction: () => NewGoalSheet.show(context),
                  )
                else ...[
                  GoalCard(
                    goal: goals.first,
                    hero: true,
                    onTap: () => openGoal(goals.first.id),
                  ),
                  for (var i = 1; i < goals.length; i += 2) ...[
                    const SizedBox(height: 10),
                    IntrinsicHeight(
                      child: Row(
                        crossAxisAlignment: .stretch,
                        spacing: 10,
                        children: [
                          for (final g in goals.skip(i).take(2))
                            Expanded(
                              child: GoalCard(
                                goal: g,
                                onTap: () => openGoal(g.id),
                              ),
                            ),
                          if (i + 1 >= goals.length)
                            const Expanded(child: SizedBox()),
                        ],
                      ),
                    ),
                  ],
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}
