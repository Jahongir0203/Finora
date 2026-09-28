import 'package:auto_route/auto_route.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/application/finance/finance_cubit.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_bottom_sheet.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_text_field.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:finora/presentation/pages/pin/widgets/pin_badge.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

/// Add money / Withdraw (docs/screens/BUDGETS_GOALS.md §2.2).
class GoalFundSheet extends StatefulWidget {
  final Goal goal;
  final bool withdraw;

  const GoalFundSheet({super.key, required this.goal, required this.withdraw});

  static Future<void> show(
    BuildContext context,
    Goal goal, {
    required bool withdraw,
  }) {
    final finance = context.read<FinanceCubit>();
    return AppBottomSheet.show(
      context,
      child: BlocProvider.value(
        value: finance,
        child: GoalFundSheet(goal: goal, withdraw: withdraw),
      ),
    );
  }

  @override
  State<GoalFundSheet> createState() => _GoalFundSheetState();
}

class _GoalFundSheetState extends State<GoalFundSheet> {
  final _controller = TextEditingController();

  int get _amount => SpacedDigitsFormatter.parse(_controller.text);

  bool get _tooMuch => widget.withdraw && _amount > widget.goal.saved;

  bool get _valid => _amount > 0 && !_tooMuch;

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

  Future<void> _save() async {
    final finance = context.read<FinanceCubit>().facade;
    final amount = _amount;
    final updated = await finance.moveGoalMoney(
      widget.goal.id,
      widget.withdraw ? -amount : amount,
    );
    if (!mounted) return;
    Navigator.of(context).pop();
    if (!widget.withdraw && updated.reached && !widget.goal.reached) {
      AppToast.success(Words.goalReached.str);
    } else {
      AppToast.success(
        (widget.withdraw ? Words.amountWithdrawn : Words.amountAdded).tr(
          args: [amount.toMoney()],
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final account = context.watch<FinanceCubit>().state.accounts.firstWhere(
      (a) => a.isMain,
    );
    final style = AppTypography.displayLarge.copyWith(
      height: 1.2,
      color: c.textPrimary,
    );

    return Column(
      mainAxisSize: .min,
      crossAxisAlignment: .stretch,
      children: [
        SheetHeader(
          title: widget.withdraw ? Words.withdraw.str : Words.addMoney.str,
          subtitle: widget.goal.name,
        ),
        const SizedBox(height: AppSpacing.x2l),
        Center(
          child: SizedBox(
            width: 240,
            child: TextField(
              controller: _controller,
              autofocus: true,
              textAlign: .center,
              keyboardType: TextInputType.number,
              inputFormatters: const [SpacedDigitsFormatter(maxDigits: 11)],
              style: style,
              cursorColor: c.primary,
              decoration: bareInputDecoration(hint: '0',
                hintStyle: style.copyWith(color: c.textTertiary),
              ),
            ),
          ),
        ),
        const SizedBox(height: AppSpacing.xs),
        Text(
          _tooMuch
              ? Words.onlyAvailable.tr(args: [widget.goal.saved.toMoney()])
              : AppFormat.currency,
          textAlign: .center,
          style: AppTypography.bodyMedium.copyWith(
            fontSize: 14,
            color: _tooMuch ? c.danger : c.textTertiary,
          ),
        ),
        const SizedBox(height: AppSpacing.x2l),
        AmountQuickChips(
          height: 40,
          presets: const [
            (100000, '+100K'),
            (500000, '+500K'),
            (1000000, '+1M'),
          ],
          onAdd: (v) => setSpacedAmount(_controller, _amount + v),
        ),
        const SizedBox(height: AppSpacing.lg),
        Container(
          padding: const .symmetric(horizontal: 14, vertical: 12),
          decoration: BoxDecoration(
            borderRadius: .circular(AppRadius.lg),
            border: Border.all(color: c.border),
          ),
          child: Row(
            spacing: AppSpacing.md,
            children: [
              Container(
                width: 40,
                height: 28,
                decoration: BoxDecoration(
                  color: Color(account.color),
                  borderRadius: .circular(7),
                ),
              ),
              Expanded(
                child: Column(
                  crossAxisAlignment: .start,
                  children: [
                    Text(
                      widget.withdraw ? Words.to.str : Words.from.str,
                      style: context.textStyles.bodyMedium,
                    ),
                    Text(
                      '${account.bank} ${_title(account.network)} •••• ${account.last4}',
                      style: context.textStyles.caption,
                    ),
                  ],
                ),
              ),
              Icon(
                FinoraIcons.forward,
                size: AppSizes.iconTrailing,
                color: c.textTertiary,
              ),
            ],
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        AppButton(
          text: widget.withdraw
              ? Words.withdrawToCard.str
              : Words.addToGoal.str,
          size: AppButtonSize.large,
          variant: widget.withdraw
              ? AppButtonVariant.dark
              : AppButtonVariant.primary,
          onPressed: _valid ? _save : null,
        ),
      ],
    );
  }

  static String _title(String? network) => network == null
      ? ''
      : '${network[0]}${network.substring(1).toLowerCase()}';
}

/// Delete confirmation (docs/screens/BUDGETS_GOALS.md §2.3).
class GoalDeleteSheet extends StatelessWidget {
  final Goal goal;

  const GoalDeleteSheet({super.key, required this.goal});

  static Future<void> show(BuildContext context, Goal goal) {
    final finance = context.read<FinanceCubit>();
    return AppBottomSheet.show(
      context,
      child: BlocProvider.value(
        value: finance,
        child: GoalDeleteSheet(goal: goal),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Column(
      mainAxisSize: .min,
      crossAxisAlignment: .stretch,
      children: [
        const SizedBox(height: AppSpacing.sm),
        Center(
          child: IconBadge(
            icon: FinoraIcons.trash,
            size: 56,
            radius: 18,
            iconSize: 24,
            background: c.dangerSoft,
            foreground: c.danger,
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        Text(
          Words.deleteGoalTitle.tr(args: [goal.name]),
          textAlign: .center,
          style: context.textStyles.title,
        ),
        const SizedBox(height: AppSpacing.sm),
        Text(
          Words.deleteGoalDesc.tr(args: [goal.saved.toMoney()]),
          textAlign: .center,
          style: AppTypography.body.copyWith(
            fontSize: 14,
            height: 21 / 14,
            color: c.textSecondary,
          ),
        ),
        const SizedBox(height: AppSpacing.x2l),
        Row(
          spacing: AppSpacing.md,
          children: [
            Expanded(
              child: AppButton.outline(
                text: Words.cancel.str,
                onPressed: () => Navigator.of(context).pop(),
              ),
            ),
            Expanded(
              child: AppButton(
                text: Words.delete.str,
                variant: AppButtonVariant.destructiveSolid,
                onPressed: () async {
                  final router = context.router;
                  final finance = context.read<FinanceCubit>().facade;
                  Navigator.of(context).pop();
                  await finance.deleteGoal(goal.id);
                  router.maybePop();
                  AppToast.success(Words.goalDeleted.str);
                },
              ),
            ),
          ],
        ),
      ],
    );
  }
}
