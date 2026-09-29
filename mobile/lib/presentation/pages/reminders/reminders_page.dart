import 'package:finora/common/helpers/api_call.dart';
import 'package:auto_route/auto_route.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/application/finance/finance_cubit.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_card.dart';
import 'package:finora/common/widgets/app_empty_state.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_switch.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'widgets/new_reminder_sheet.dart';

/// Payment reminders (docs/screens/REMINDERS.md §1).
@RoutePage()
class RemindersPage extends StatefulWidget {
  /// Open the New reminder sheet right away.
  final bool create;

  const RemindersPage({super.key, this.create = false});

  @override
  State<RemindersPage> createState() => _RemindersPageState();
}

class _RemindersPageState extends State<RemindersPage> {
  @override
  void initState() {
    super.initState();
    if (widget.create) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) NewReminderSheet.show(context);
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final s = context.watch<FinanceCubit>().state;
    final now = DateTime.now();
    final reminders = s.reminders;
    final due = reminders.where((r) => r.enabled && r.dueIn(now) <= 30);
    final total = due.fold<num>(0, (sum, r) => sum + r.amount);

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
                  title: Words.paymentReminders.str,
                  trailing: AppAddButton(
                    semanticLabel: Words.newReminder.str,
                    onPressed: () => NewReminderSheet.show(context),
                  ),
                ),
                const SizedBox(height: AppSpacing.lg),
                AppCard.hero(
                  child: Column(
                    crossAxisAlignment: .start,
                    spacing: 6,
                    children: [
                      Text(
                        Words.dueNext30.str.toUpperCase(),
                        style: AppTypography.label.copyWith(
                          color: AppPalette.primary200,
                        ),
                      ),
                      Text.rich(
                        TextSpan(
                          text: total.toMoney(),
                          style: AppTypography.display.copyWith(
                            fontSize: 30,
                            height: 38 / 30,
                            color: AppPalette.white,
                          ),
                          children: [
                            TextSpan(
                              text: ' ${AppFormat.currency}',
                              style: AppTypography.body.copyWith(
                                fontWeight: .w500,
                                color: AppPalette.primary200,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Text(
                        Words.paymentsScheduled.tr(args: ['${due.length}']),
                        style: AppTypography.body.copyWith(
                          fontSize: 14,
                          color: AppPalette.primary200,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: AppSpacing.lg),
                if (reminders.isEmpty)
                  AppEmptyCard(
                    icon: FinoraIcons.reminder,
                    title: Words.noPaymentReminders.str,
                    message: Words.noPaymentRemindersDesc.str,
                    actionText: Words.addReminder.str,
                    onAction: () => NewReminderSheet.show(context),
                  )
                else ...[
                  SectionLabel(
                    Words.upcoming.str,
                    padding: const .symmetric(horizontal: 4),
                  ),
                  for (final (i, r) in reminders.indexed)
                    Padding(
                      padding: const .only(top: 10),
                      child: AppFadeIn(
                        key: ValueKey(r.id),
                        index: i,
                        step: const Duration(milliseconds: 60),
                        child: _ReminderTile(reminder: r),
                      ),
                    ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ReminderTile extends StatelessWidget {
  final Reminder reminder;

  const _ReminderTile({required this.reminder});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final r = reminder;
    final now = DateTime.now();
    final dueIn = r.dueIn(now);
    final locale = context.locale.languageCode;

    final (badgeBg, badgeFg) = !r.enabled
        ? (c.background, c.textTertiary)
        : dueIn <= 1
        ? (c.warningSoft, c.warningText)
        : (c.tint, c.primaryText);

    final (dueText, dueColor) = !r.enabled
        ? (Words.paused.str, c.textTertiary)
        : switch (dueIn) {
            <= 0 => (Words.dueToday.str, c.danger),
            1 => (Words.dueTomorrow.str, c.warningText),
            <= 14 => (Words.dueInDays.tr(args: ['$dueIn']), c.textSecondary),
            _ => (
              DateFormat('d MMM', locale).format(r.dueDate),
              c.textTertiary,
            ),
          };

    final repeat = switch (r.repeat) {
      .once => Words.once.str,
      .weekly => Words.weekly.str,
      .monthly => Words.monthly.str,
      .yearly => Words.yearly.str,
    };

    return AppCard(
      padding: const .symmetric(horizontal: 16, vertical: 14),
      child: Row(
        spacing: AppSpacing.md,
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: badgeBg,
              borderRadius: .circular(AppRadius.md),
            ),
            child: Column(
              mainAxisAlignment: .center,
              children: [
                Text(
                  DateFormat('MMM', locale).format(r.dueDate).toUpperCase(),
                  style: AppTypography.tabLabel.copyWith(
                    fontWeight: .w600,
                    color: badgeFg,
                  ),
                ),
                Text(
                  '${r.dueDate.day}',
                  style: AppTypography.titleSmall.copyWith(
                    fontSize: 18,
                    height: 20 / 18,
                    fontWeight: .w700,
                    color: badgeFg,
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: .start,
              spacing: 1,
              children: [
                Text(
                  r.title,
                  maxLines: 1,
                  overflow: .ellipsis,
                  style: AppTypography.body.copyWith(
                    fontWeight: .w600,
                    color: r.enabled ? c.textPrimary : c.textTertiary,
                  ),
                ),
                Text(
                  '${r.amount.toUzs()} · $repeat',
                  style: AppTypography.caption.copyWith(
                    color: c.textSecondary,
                    fontFeatures: const [FontFeature.tabularFigures()],
                  ),
                ),
                Text(
                  dueText,
                  style: AppTypography.label.copyWith(
                    letterSpacing: 0,
                    color: dueColor,
                  ),
                ),
              ],
            ),
          ),
          AppSwitch(
            large: true,
            value: r.enabled,
            semanticLabel: r.title,
            onChanged: (v) {
              final finance = context.read<FinanceCubit>().facade;
              apiRun(() => finance.setReminderEnabled(r.id, v));
            },
          ),
        ],
      ),
    );
  }
}
