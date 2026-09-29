import 'package:finora/common/helpers/api_call.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/application/finance/finance_cubit.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/category_icons.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_bottom_sheet.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_chip.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/widgets/app_segment_control.dart';
import 'package:finora/common/widgets/app_text_field.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/widgets/edge_scroll_row.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/presentation/pages/goals/goal_details_page.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

/// New goal (docs/screens/BUDGETS_GOALS.md §3).
class NewGoalSheet extends StatefulWidget {
  const NewGoalSheet({super.key});

  static Future<void> show(BuildContext context) {
    final finance = context.read<FinanceCubit>();
    return AppBottomSheet.show(
      context,
      child: BlocProvider.value(value: finance, child: const NewGoalSheet()),
    );
  }

  @override
  State<NewGoalSheet> createState() => _NewGoalSheetState();
}

class _NewGoalSheetState extends State<NewGoalSheet> {
  static const _minTarget = 100000;
  static const _autoSaves = [null, 500000, 1000000, 2000000];

  /// Months from now: Dec 2026 · Mar 2027 · Jun 2027 · Dec 2027 · Jun 2028
  /// when opened in Sep 2026.
  static const _monthOffsets = [3, 6, 9, 15, 21];

  final _name = TextEditingController();
  final _target = TextEditingController();
  var _icon = CategoryIcons.goalPicker.first;
  var _dateIndex = 2;
  var _autoIndex = 0;
  var _showErrors = false;

  late final _dates = [
    for (final m in _monthOffsets)
      DateTime(DateTime.now().year, DateTime.now().month + m),
  ];

  int get _amount => SpacedDigitsFormatter.parse(_target.text);

  String? get _nameError => _showErrors && _name.text.trim().isEmpty
      ? Words.goalNameRequired.str
      : null;

  String? get _targetError => _showErrors && _amount < _minTarget
      ? Words.targetMin.tr(args: [_minTarget.toMoney()])
      : null;

  bool get _valid => _name.text.trim().isNotEmpty && _amount >= _minTarget;

  @override
  void dispose() {
    _name.dispose();
    _target.dispose();
    super.dispose();
  }

  String _hint() {
    final auto = _autoSaves[_autoIndex];
    if (_amount == 0) return Words.goalHintEmpty.str;
    if (auto != null) {
      return Words.goalHintAuto.tr(
        args: [auto.toShort(), '${(_amount / auto).ceil()}'],
      );
    }
    final months = GoalDetailsPage.monthsUntil(
      _dates[_dateIndex],
      DateTime.now(),
    );
    final perMonth = (_amount / months / 1000).ceil() * 1000;
    return Words.goalHintManual.tr(
      args: [perMonth.toShort(), _label(_dates[_dateIndex])],
    );
  }

  String _label(DateTime d) =>
      DateFormat('MMM y', context.locale.languageCode).format(d);

  Future<void> _create() async {
    if (!_valid) {
      setState(() => _showErrors = true);
      return;
    }
    final finance = context.read<FinanceCubit>().facade;
    final ok = await apiRun(
      () => finance.addGoal(
        name: _name.text.trim(),
        icon: _icon,
        target: _amount,
        due: _dates[_dateIndex],
        autoSave: _autoSaves[_autoIndex],
      ),
    );
    if (!ok || !mounted) return;
    Navigator.of(context).pop();
    AppToast.success(Words.goalCreated.str);
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Column(
      mainAxisSize: .min,
      crossAxisAlignment: .stretch,
      children: [
        SheetHeader(title: Words.newGoal.str),
        const SizedBox(height: AppSpacing.lg),
        Row(
          crossAxisAlignment: .end,
          spacing: AppSpacing.lg,
          children: [
            Container(
              width: 56,
              height: 56,
              margin: .only(bottom: _nameError == null ? 0 : 24),
              alignment: .center,
              decoration: BoxDecoration(
                color: AppPalette.primary500,
                borderRadius: .circular(18),
              ),
              child: Icon(
                CategoryIcons.of(_icon),
                size: 26,
                color: AppPalette.primary950,
              ),
            ),
            Expanded(
              child: AppFormField(
                label: Words.goalName.str,
                hint: Words.goalNameHint.str,
                controller: _name,
                maxLength: 32,
                errorText: _nameError,
                onChanged: (_) => setState(() {}),
              ),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.lg),
        Row(
          spacing: 6,
          children: [
            for (final icon in CategoryIcons.goalPicker)
              Expanded(
                child: AspectRatio(
                  aspectRatio: 1,
                  child: Semantics(
                    selected: icon == _icon,
                    button: true,
                    child: AppPressable(
                      onTap: () => setState(() => _icon = icon),
                      child: AnimatedContainer(
                        duration: AppMotion.fast,
                        decoration: BoxDecoration(
                          color: icon == _icon ? c.tint : c.background,
                          borderRadius: .circular(12),
                          border: Border.all(
                            color: icon == _icon
                                ? AppPalette.primary500
                                : Colors.transparent,
                            width: AppSizes.borderThick,
                          ),
                        ),
                        child: Icon(
                          CategoryIcons.of(icon),
                          size: AppSizes.iconMd,
                          color: icon == _icon
                              ? c.primaryText
                              : c.textSecondary,
                        ),
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
        const SizedBox(height: AppSpacing.lg),
        AppInlineAmountField(
          label: Words.targetAmount.str,
          controller: _target,
          errorText: _targetError,
          onChanged: (_) => setState(() {}),
        ),
        const SizedBox(height: AppSpacing.lg),
        SectionLabel(Words.targetDateLabel.str),
        const SizedBox(height: AppSpacing.sm),
        EdgeScrollRow(
          height: 38,
          children: [
            for (final (i, d) in _dates.indexed)
              AppChip(
                label: _label(d),
                style: AppChipStyle.brand,
                selected: i == _dateIndex,
                height: 38,
                onTap: () => setState(() => _dateIndex = i),
              ),
          ],
        ),
        const SizedBox(height: AppSpacing.lg),
        SectionLabel(Words.monthlyAutoSave.str),
        const SizedBox(height: AppSpacing.sm),
        AppSegmentControl(
          height: 36,
          fontSize: 13,
          index: _autoIndex,
          children: [Words.off.str, '500K', '1M', '2M'],
          onChanged: (i) => setState(() => _autoIndex = i),
        ),
        const SizedBox(height: AppSpacing.sm),
        Text(
          _hint(),
          style: AppTypography.caption.copyWith(color: c.textSecondary),
        ),
        const SizedBox(height: AppSpacing.lg),
        AppButton(
          text: Words.createGoal.str,
          size: AppButtonSize.large,
          muted: !_valid,
          onPressed: _create,
        ),
      ],
    );
  }
}
