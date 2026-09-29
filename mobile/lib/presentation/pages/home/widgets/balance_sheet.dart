import 'package:finora/application/home/home_cubit.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_bottom_sheet.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_text_field.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/words/words.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

/// "Current balance" sheet from the hero pill or checklist step 1
/// (docs/screens/HOME_NOTIFICATIONS.md §3.5).
class BalanceSheet extends StatefulWidget {
  const BalanceSheet({super.key});

  static Future<void> show(BuildContext context) {
    final cubit = context.read<HomeCubit>();
    return AppBottomSheet.show(
      context,
      child: BlocProvider.value(value: cubit, child: const BalanceSheet()),
    );
  }

  @override
  State<BalanceSheet> createState() => _BalanceSheetState();
}

class _BalanceSheetState extends State<BalanceSheet> {
  static const _maxDigits = 13;

  final _controller = TextEditingController();

  int get _amount => SpacedDigitsFormatter.parse(_controller.text);

  @override
  void initState() {
    super.initState();
    _controller.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _add(int value) {
    final next = _amount + value;
    if ('$next'.length <= _maxDigits) setSpacedAmount(_controller, next);
  }

  Future<void> _save() async {
    final ok = await context.read<HomeCubit>().saveBalance(_amount);
    if (!mounted) return;
    if (ok) {
      Navigator.of(context).pop();
      AppToast.success(Words.balanceUpdated.str);
    } else {
      AppToast.error(Words.happenError.str);
    }
  }

  @override
  Widget build(BuildContext context) {
    final saving = context.select((HomeCubit b) => b.state.isSavingBalance);

    return Column(
      mainAxisSize: .min,
      crossAxisAlignment: .stretch,
      spacing: AppSpacing.lg,
      children: [
        SheetHeader(
          title: Words.currentBalance.str,
          subtitle: Words.cashAndCards.str,
        ),
        AppBoxedAmountField(
          controller: _controller,
          height: 68,
          fontSize: 30,
          maxDigits: _maxDigits,
          autofocus: true,
          enabled: !saving,
          onSubmitted: (_) => _amount > 0 ? _save() : null,
        ),
        AmountQuickChips(height: 44, onAdd: saving ? (_) {} : _add),
        AppButton(
          text: Words.saveBalance.str,
          size: AppButtonSize.large,
          isLoading: saving,
          onPressed: _amount > 0 ? _save : null,
        ),
      ],
    );
  }
}
