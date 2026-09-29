import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/application/finance/finance_cubit.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_bottom_sheet.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/widgets/app_segment_control.dart';
import 'package:finora/common/widgets/app_text_field.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/widgets/category_chip.dart';
import 'package:finora/common/widgets/edge_scroll_row.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

/// New reminder (docs/screens/REMINDERS.md §2).
// TODO: schedule with flutter_local_notifications by `notify`.
class NewReminderSheet extends StatefulWidget {
  const NewReminderSheet({super.key});

  static Future<void> show(BuildContext context) {
    final finance = context.read<FinanceCubit>();
    return AppBottomSheet.show(
      context,
      child: BlocProvider.value(
        value: finance,
        child: const NewReminderSheet(),
      ),
    );
  }

  @override
  State<NewReminderSheet> createState() => _NewReminderSheetState();
}

class _NewReminderSheetState extends State<NewReminderSheet> {
  static const _categoryIds = [
    'bills',
    'housing',
    'subscriptions',
    'transport',
    'health',
  ];

  final _title = TextEditingController();
  final _amount = TextEditingController();
  var _categoryId = 'bills';
  var _dayIndex = 3;
  var _repeat = ReminderRepeat.monthly;
  var _notify = ReminderNotify.dayBefore;

  final _today = DateTime(
    DateTime.now().year,
    DateTime.now().month,
    DateTime.now().day,
  );

  int get _amountValue => SpacedDigitsFormatter.parse(_amount.text);

  bool get _valid => _title.text.trim().isNotEmpty && _amountValue > 0;

  @override
  void dispose() {
    _title.dispose();
    _amount.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    await context.read<FinanceCubit>().facade.addReminder(
      Reminder(
        id: '',
        title: _title.text.trim(),
        categoryId: _categoryId,
        amount: _amountValue,
        dueDate: _today.add(Duration(days: _dayIndex)),
        repeat: _repeat,
        notify: _notify,
      ),
    );
    if (!mounted) return;
    Navigator.of(context).pop();
    AppToast.success(Words.reminderSet.str);
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final s = context.watch<FinanceCubit>().state;
    final locale = context.locale.languageCode;

    return Column(
      mainAxisSize: .min,
      crossAxisAlignment: .stretch,
      children: [
        SheetHeader(title: Words.newReminder.str),
        const SizedBox(height: AppSpacing.lg),
        AppFormField(
          label: Words.paymentName.str,
          hint: Words.paymentNameHint.str,
          controller: _title,
          onChanged: (_) => setState(() {}),
        ),
        const SizedBox(height: AppSpacing.lg),
        AppInlineAmountField(
          label: Words.amount.str,
          controller: _amount,
          onChanged: (_) => setState(() {}),
        ),
        const SizedBox(height: AppSpacing.lg),
        EdgeScrollRow(
          height: 38,
          children: [
            for (final id in _categoryIds)
              if (s.category(id) case final cat?)
                CategoryChip(
                  category: cat,
                  selected: id == _categoryId,
                  onTap: () => setState(() => _categoryId = id),
                ),
          ],
        ),
        const SizedBox(height: AppSpacing.lg),
        SectionLabel(Words.dueDate.str),
        const SizedBox(height: AppSpacing.sm),
        EdgeScrollRow(
          height: 64,
          children: [
            for (var i = 0; i < 14; i++)
              Builder(
                builder: (context) {
                  final day = _today.add(Duration(days: i));
                  final selected = i == _dayIndex;
                  final fg = selected ? c.surface : c.textPrimary;
                  return Semantics(
                    selected: selected,
                    button: true,
                    child: AppPressable(
                      onTap: () => setState(() => _dayIndex = i),
                      child: AnimatedContainer(
                        duration: AppMotion.fast,
                        width: 52,
                        height: 64,
                        decoration: BoxDecoration(
                          color: selected ? c.textPrimary : c.surface,
                          borderRadius: .circular(AppRadius.md),
                          border: Border.all(
                            color: selected ? c.textPrimary : c.border,
                          ),
                        ),
                        child: Column(
                          mainAxisAlignment: .center,
                          spacing: 2,
                          children: [
                            Text(
                              i == 0
                                  ? Words.today.str
                                  : DateFormat.E(locale).format(day),
                              style: AppTypography.tabLabel.copyWith(color: fg),
                            ),
                            Text(
                              '${day.day}',
                              style: AppTypography.titleSmall.copyWith(
                                fontSize: 18,
                                fontWeight: .w700,
                                color: fg,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
          ],
        ),
        const SizedBox(height: AppSpacing.lg),
        SectionLabel(Words.repeat.str),
        const SizedBox(height: AppSpacing.sm),
        AppSegmentControl(
          height: 36,
          fontSize: 13,
          index: _repeat.index,
          children: [
            Words.once.str,
            Words.weekly.str,
            Words.monthly.str,
            Words.yearly.str,
          ],
          onChanged: (i) => setState(() => _repeat = ReminderRepeat.values[i]),
        ),
        const SizedBox(height: AppSpacing.lg),
        SectionLabel(Words.notifyMe.str),
        const SizedBox(height: AppSpacing.sm),
        AppSegmentControl(
          height: 36,
          fontSize: 13,
          index: _notify.index,
          children: [
            Words.sameDay.str,
            Words.dayBefore.str,
            Words.threeDaysBefore.str,
          ],
          onChanged: (i) => setState(() => _notify = ReminderNotify.values[i]),
        ),
        const SizedBox(height: AppSpacing.lg),
        AppButton(
          text: Words.saveReminder.str,
          size: AppButtonSize.large,
          onPressed: _valid ? _save : null,
        ),
      ],
    );
  }
}
