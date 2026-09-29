import 'package:finora/common/helpers/api_call.dart';
import 'package:auto_route/auto_route.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/application/finance/finance_cubit.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/category_icons.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_card.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_list_tiles.dart';
import 'package:finora/common/widgets/app_switch.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:finora/presentation/pages/pin/widgets/pin_badge.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'widgets/goal_sheets.dart';

/// Goal details (docs/screens/BUDGETS_GOALS.md §2).
@RoutePage()
class GoalDetailsPage extends StatelessWidget {
  final String goalId;

  const GoalDetailsPage({super.key, @PathParam('id') required this.goalId});

  static const _autoSaveAmount = 1000000;

  /// Whole months from now to the target month (min 1).
  static int monthsUntil(DateTime due, DateTime now) {
    final m = (due.year - now.year) * 12 + due.month - now.month;
    return m < 1 ? 1 : m;
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final goal = context.select(
      (FinanceCubit b) =>
          b.state.goals.where((g) => g.id == goalId).firstOrNull,
    );
    // Deleted: the delete sheet pops this page.
    if (goal == null) return Scaffold(backgroundColor: c.background);

    final locale = context.locale.languageCode;
    final due = DateFormat('MMM y', locale).format(goal.due);
    final rem = goal.remaining;
    final perMonth = rem == 0
        ? '—'
        : '${((rem / monthsUntil(goal.due, DateTime.now()) / 1000).ceil() * 1000).toShort()} ${AppFormat.currency}';
    final finance = context.read<FinanceCubit>().facade;

    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: authOverlayStyle(
        context,
      ).copyWith(systemNavigationBarColor: c.background),
      child: Scaffold(
        backgroundColor: c.background,
        body: SafeArea(
          bottom: false,
          child: AppFadeIn(
            horizontal: true,
            child: ListView(
              padding: .fromLTRB(
                20,
                8,
                20,
                28 + MediaQuery.paddingOf(context).bottom,
              ),
              children: [
                PushHeader(
                  title: Words.goal.str,
                  large: true,
                  trailing: AppIconButton(
                    icon: FinoraIcons.trash,
                    semanticLabel: Words.delete.str,
                    iconSize: AppSizes.iconTrailing,
                    foreground: c.danger,
                    onPressed: () => GoalDeleteSheet.show(context, goal),
                  ),
                ),
                const SizedBox(height: AppSpacing.lg),
                _Hero(goal: goal, due: due),
                const SizedBox(height: AppSpacing.lg),
                Row(
                  spacing: 10,
                  children: [
                    Expanded(
                      child: AppButton(
                        text: Words.addMoney.str,
                        icon: FinoraIcons.add,
                        onPressed: () =>
                            GoalFundSheet.show(context, goal, withdraw: false),
                      ),
                    ),
                    Expanded(
                      child: AppButton.outline(
                        text: Words.withdraw.str,
                        icon: FinoraIcons.minus,
                        onPressed: () =>
                            GoalFundSheet.show(context, goal, withdraw: true),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.lg),
                AppListCard(
                  children: [
                    _InfoRow(
                      icon: FinoraIcons.calendarClock,
                      title: Words.suggestedMonthly.str,
                      subtitle: Words.toReachItBy.tr(args: [due]),
                      trailing: Text(
                        perMonth,
                        style: context.textStyles.amount,
                      ),
                    ),
                    _InfoRow(
                      icon: FinoraIcons.subscriptions,
                      title: Words.autoSave.str,
                      subtitle: goal.autoSave == null
                          ? Words.off.str
                          : Words.autoSaveDesc.tr(
                              args: [goal.autoSave!.toMoney()],
                            ),
                      trailing: AppSwitch(
                        value: goal.autoSave != null,
                        semanticLabel: Words.autoSave.str,
                        onChanged: (on) async {
                          final ok = await apiRun(
                            () => finance.setGoalAutoSave(
                              goal.id,
                              on ? _autoSaveAmount : null,
                            ),
                          );
                          if (!ok) return;
                          AppToast.success(
                            on
                                ? Words.autoSaveOnToast.tr(
                                    args: [_autoSaveAmount.toMoney()],
                                  )
                                : Words.autoSaveOffToast.str,
                          );
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.x2l),
                Text(Words.history.str, style: context.textStyles.titleSmall),
                const SizedBox(height: AppSpacing.md),
                _GoalHistory(goal: goal),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// `GET /goals/{id}/history`, reloaded when the saved amount changes.
class _GoalHistory extends StatefulWidget {
  final Goal goal;

  const _GoalHistory({required this.goal});

  @override
  State<_GoalHistory> createState() => _GoalHistoryState();
}

class _GoalHistoryState extends State<_GoalHistory> {
  List<GoalEntry>? _history;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void didUpdateWidget(_GoalHistory old) {
    super.didUpdateWidget(old);
    if (old.goal.saved != widget.goal.saved) _load();
  }

  Future<void> _load() async {
    final finance = context.read<FinanceCubit>().facade;
    try {
      final items = await finance.goalHistory(widget.goal.id);
      if (mounted) setState(() => _history = items);
    } catch (_) {
      if (mounted) setState(() => _history ??= const []);
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final history = _history;
    if (history == null) return const SizedBox(height: 64);
    if (history.isEmpty) {
      return AppCard.dashed(
        child: Text(
          Words.noDepositsYet.str,
          textAlign: .center,
          style: AppTypography.body.copyWith(
            fontSize: 14,
            color: c.textTertiary,
          ),
        ),
      );
    }
    return AppListCard(
      children: [
        for (final (i, e) in history.indexed)
          AppFadeIn(
            index: i,
            step: const Duration(milliseconds: 40),
            child: _HistoryRow(entry: e),
          ),
      ],
    );
  }
}

class _Hero extends StatelessWidget {
  final Goal goal;
  final String due;

  const _Hero({required this.goal, required this.due});

  @override
  Widget build(BuildContext context) {
    const light = AppPalette.primary200;
    final pct = (goal.progress * 100).round();

    return AppCard.hero(
      child: Column(
        crossAxisAlignment: .stretch,
        spacing: AppSpacing.lg,
        children: [
          Row(
            spacing: AppSpacing.md,
            children: [
              IconBadge(
                icon: goal.iconData,
                size: 48,
                radius: 15,
                iconSize: 24,
                background: AppPalette.primary500,
                foreground: AppPalette.primary950,
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: .start,
                  children: [
                    Text(
                      goal.name,
                      style: AppTypography.titleSmall.copyWith(
                        fontSize: 18,
                        color: AppPalette.white,
                      ),
                    ),
                    Text(
                      Words.targetDate.tr(args: [due]),
                      style: AppTypography.caption.copyWith(color: light),
                    ),
                  ],
                ),
              ),
              if (goal.reached)
                PopIn(
                  child: Container(
                    height: 26,
                    padding: const .symmetric(horizontal: 8),
                    decoration: BoxDecoration(
                      color: AppPalette.primary500,
                      borderRadius: .circular(AppRadius.full),
                    ),
                    child: Row(
                      mainAxisSize: .min,
                      spacing: 4,
                      children: [
                        const Icon(
                          FinoraIcons.check,
                          size: 14,
                          color: AppPalette.primary950,
                        ),
                        Text(
                          Words.reached.str,
                          style: AppTypography.label.copyWith(
                            fontWeight: .w700,
                            letterSpacing: 0,
                            color: AppPalette.primary950,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
            ],
          ),
          Column(
            crossAxisAlignment: .start,
            children: [
              Text(
                Words.saved.str,
                style: AppTypography.caption.copyWith(color: light),
              ),
              Text.rich(
                TextSpan(
                  text: goal.saved.toMoney(),
                  style: AppTypography.display.copyWith(
                    color: AppPalette.white,
                  ),
                  children: [
                    TextSpan(
                      text: ' ${AppFormat.currency}',
                      style: AppTypography.body.copyWith(
                        fontWeight: .w500,
                        color: light,
                      ),
                    ),
                  ],
                ),
              ),
              Text(
                Words.ofTarget.tr(args: [goal.target.toMoney()]),
                style: AppTypography.body.copyWith(
                  fontSize: 14,
                  color: AppPalette.pinChipText,
                ),
              ),
            ],
          ),
          Column(
            spacing: AppSpacing.sm,
            children: [
              ClipRRect(
                borderRadius: .circular(AppRadius.full),
                child: Container(
                  height: 10,
                  color: AppPalette.heroTrack,
                  alignment: Alignment.centerLeft,
                  child: TweenAnimationBuilder<double>(
                    tween: Tween(end: goal.progress),
                    duration: const Duration(milliseconds: 600),
                    curve: AppMotion.ease,
                    builder: (_, v, _) => FractionallySizedBox(
                      widthFactor: v,
                      heightFactor: 1,
                      child: DecoratedBox(
                        decoration: BoxDecoration(
                          color: AppPalette.primary500,
                          borderRadius: .circular(AppRadius.full),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
              Row(
                children: [
                  Text(
                    Words.pctSaved.tr(args: ['$pct']),
                    style: AppTypography.caption.copyWith(
                      fontWeight: .w600,
                      color: AppPalette.white,
                    ),
                  ),
                  const Spacer(),
                  Text(
                    goal.remaining > 0
                        ? Words.toGo.tr(args: [goal.remaining.toMoney()])
                        : Words.targetReached.str,
                    style: AppTypography.caption.copyWith(
                      color: light,
                      fontFeatures: const [FontFeature.tabularFigures()],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final Widget trailing;

  const _InfoRow({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.trailing,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Padding(
      padding: const .symmetric(vertical: 12),
      child: Row(
        spacing: AppSpacing.md,
        children: [
          Container(
            width: 40,
            height: 40,
            alignment: .center,
            decoration: BoxDecoration(
              color: c.tint,
              borderRadius: .circular(12),
            ),
            child: Icon(icon, size: AppSizes.iconMd, color: c.primaryText),
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: .start,
              children: [
                Text(title, style: context.textStyles.bodyMedium),
                Text(subtitle, style: context.textStyles.caption),
              ],
            ),
          ),
          trailing,
        ],
      ),
    );
  }
}

class _HistoryRow extends StatelessWidget {
  final GoalEntry entry;

  const _HistoryRow({required this.entry});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final deposit = entry.amount > 0;

    return Padding(
      padding: const .symmetric(vertical: 12),
      child: Row(
        spacing: AppSpacing.md,
        children: [
          Container(
            width: 40,
            height: 40,
            alignment: .center,
            decoration: BoxDecoration(
              color: deposit ? c.tint : c.background,
              borderRadius: .circular(12),
            ),
            child: Icon(
              deposit ? FinoraIcons.income : FinoraIcons.expense,
              size: AppSizes.iconMd,
              color: deposit ? c.primaryText : c.textPrimary,
            ),
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: .start,
              children: [
                Text(
                  deposit ? Words.deposit.str : Words.withdrawal.str,
                  style: context.textStyles.bodyMedium,
                ),
                Text(
                  DateFormat(
                    'd MMM',
                    context.locale.languageCode,
                  ).format(entry.date),
                  style: context.textStyles.caption,
                ),
              ],
            ),
          ),
          Text(
            entry.amount.toMoney(sign: true),
            style: context.textStyles.amount.copyWith(
              color: deposit ? c.primaryText : c.textPrimary,
            ),
          ),
        ],
      ),
    );
  }
}
