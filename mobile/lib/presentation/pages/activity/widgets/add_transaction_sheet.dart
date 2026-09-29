import 'package:finora/application/finance/finance_cubit.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_bottom_sheet.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_segment_control.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/widgets/category_chip.dart';
import 'package:finora/common/widgets/edge_scroll_row.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

/// "New transaction" sheet with its own keypad
/// (docs/screens/ACTIVITY_SCAN.md §3).
class AddTransactionSheet extends StatefulWidget {
  const AddTransactionSheet({super.key});

  static Future<void> show(BuildContext context) {
    final finance = context.read<FinanceCubit>();
    return AppBottomSheet.show(
      context,
      child: BlocProvider.value(
        value: finance,
        child: const AddTransactionSheet(),
      ),
    );
  }

  @override
  State<AddTransactionSheet> createState() => _AddTransactionSheetState();
}

class _AddTransactionSheetState extends State<AddTransactionSheet> {
  static const _maxDigits = 11;

  var _income = false;
  var _digits = '';
  String? _categoryId;

  int get _amount => int.tryParse(_digits) ?? 0;

  List<Category> _categories(FinanceSnapshot s) =>
      s.categories.where((e) => e.isIncome == _income).toList();

  void _type(bool income) {
    if (income == _income) return;
    setState(() {
      _income = income;
      _categoryId = null; // → default for the new type
    });
  }

  void _key(String k) {
    HapticFeedback.selectionClick();
    setState(() {
      if (k == '⌫') {
        if (_digits.isNotEmpty) {
          _digits = _digits.substring(0, _digits.length - 1);
        }
        return;
      }
      final next = (_digits + k).replaceFirst(RegExp(r'^0+'), '');
      if (next.length <= _maxDigits) _digits = next;
    });
  }

  Future<void> _save(String categoryId) async {
    final finance = context.read<FinanceCubit>().facade;
    await finance.addTransaction(
      categoryId: categoryId,
      amount: _income ? _amount : -_amount,
    );
    if (!mounted) return;
    Navigator.of(context).pop();
    AppToast.success(Words.transactionSaved.str);
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final snapshot = context.watch<FinanceCubit>().state;
    final categories = _categories(snapshot);
    final defaultId = _income ? 'salary' : 'groceries';
    final selected =
        _categoryId ??
        (categories.any((e) => e.id == defaultId)
            ? defaultId
            : categories.firstOrNull?.id);

    final amountColor = _amount == 0
        ? c.textDisabled
        : _income
        ? c.primaryText
        : c.textPrimary;
    final prefix = _amount == 0 ? '' : (_income ? '+' : AppFormat.minus);

    return Column(
      mainAxisSize: .min,
      crossAxisAlignment: .stretch,
      spacing: AppSpacing.lg,
      children: [
        SheetHeader(title: Words.newTransaction.str),
        AppSegmentControl(
          height: 38,
          index: _income ? 1 : 0,
          children: [Words.expense.str, Words.income.str],
          onChanged: (i) => _type(i == 1),
        ),
        Padding(
          padding: const .symmetric(vertical: 6),
          child: FittedBox(
            fit: BoxFit.scaleDown,
            child: Text.rich(
              TextSpan(
                text: '$prefix${AppFormat.spaced(_amount)}',
                style: AppTypography.displayLarge.copyWith(
                  height: 1.2,
                  color: amountColor,
                ),
                children: [
                  TextSpan(
                    text: ' ${AppFormat.currency}',
                    style: AppTypography.titleSmall.copyWith(
                      fontWeight: .w500,
                      color: c.textTertiary,
                    ),
                  ),
                ],
              ),
              semanticsLabel: '$prefix$_amount ${AppFormat.currency}',
            ),
          ),
        ),
        EdgeScrollRow(
          height: 38,
          children: [
            for (final cat in categories)
              CategoryChip(
                category: cat,
                selected: cat.id == selected,
                onTap: () => setState(() => _categoryId = cat.id),
              ),
          ],
        ),
        _AmountKeypad(onKey: _key),
        AppButton(
          text: Words.saveTransaction.str,
          size: AppButtonSize.large,
          onPressed: _amount > 0 && selected != null
              ? () => _save(selected)
              : null,
        ),
      ],
    );
  }
}

/// 1–9, 000, 0, ⌫ — 52px keys, radius 14 (§3.2).
class _AmountKeypad extends StatelessWidget {
  final ValueChanged<String> onKey;

  const _AmountKeypad({required this.onKey});

  static const _keys = [
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9',
    '000',
    '0',
    '⌫',
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      spacing: 6,
      children: [
        for (var r = 0; r < 4; r++)
          Row(
            spacing: 6,
            children: [
              for (final k in _keys.sublist(r * 3, r * 3 + 3))
                Expanded(
                  child: _KeypadKey(label: k, onTap: () => onKey(k)),
                ),
            ],
          ),
      ],
    );
  }
}

class _KeypadKey extends StatefulWidget {
  final String label;
  final VoidCallback onTap;

  const _KeypadKey({required this.label, required this.onTap});

  @override
  State<_KeypadKey> createState() => _KeypadKeyState();
}

class _KeypadKeyState extends State<_KeypadKey> {
  var _down = false;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final isDelete = widget.label == '⌫';

    return Semantics(
      button: true,
      label: isDelete ? Words.delete.str : widget.label,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTapDown: (_) => setState(() => _down = true),
        onTapUp: (_) => setState(() => _down = false),
        onTapCancel: () => setState(() => _down = false),
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 120),
          height: 52,
          alignment: .center,
          decoration: BoxDecoration(
            color: _down ? c.background : Colors.transparent,
            borderRadius: .circular(AppRadius.md),
          ),
          child: ExcludeSemantics(
            child: isDelete
                ? Icon(
                    FinoraIcons.delete,
                    size: AppSizes.iconQuickAction,
                    color: c.textPrimary,
                  )
                : Text(
                    widget.label,
                    style: AppTypography.title.copyWith(
                      fontSize: 22,
                      fontWeight: .w500,
                      color: c.textPrimary,
                    ),
                  ),
          ),
        ),
      ),
    );
  }
}
