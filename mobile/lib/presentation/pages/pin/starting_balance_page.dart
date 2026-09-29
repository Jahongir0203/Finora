import 'package:finora/common/helpers/api_call.dart';
import 'package:auto_route/auto_route.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/widgets/app_text_field.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/di.dart';
import 'package:finora/domain/facades/finance_facade.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:finora/presentation/routes/app_router.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'widgets/pin_badge.dart';

/// Optional starting balance, shown once after Create PIN
/// (docs/screens/PIN_SETUP_SCREENS.md §5).
@RoutePage()
class StartingBalancePage extends StatefulWidget {
  const StartingBalancePage({super.key});

  @override
  State<StartingBalancePage> createState() => _StartingBalancePageState();
}

class _StartingBalancePageState extends State<StartingBalancePage> {
  static const _maxDigits = 12;

  final _controller = TextEditingController();
  var _location = BalanceLocation.card;

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

  Future<void> _continue() async {
    final ok = await apiRun(
      () => di<FinanceFacade>().setStartingBalance(
        _amount,
        location: _location,
      ),
    );
    if (!ok || !mounted) return;
    AppToast.success(Words.balanceSavedWelcome.str);
    context.router.replaceAll([const MainRoute()]);
  }

  void _skip() {
    AppToast.info(Words.welcomeToFinora.str);
    context.router.replaceAll([const MainRoute()]);
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return PopScope(
      // PIN is already saved: back behaves like Skip.
      canPop: false,
      onPopInvokedWithResult: (didPop, _) {
        if (!didPop) _skip();
      },
      child: AnnotatedRegion<SystemUiOverlayStyle>(
        value: authOverlayStyle(context),
        child: Scaffold(
          backgroundColor: c.surface,
          body: SafeArea(
            child: AppFadeIn(
              horizontal: true,
              child: LayoutBuilder(
                builder: (context, constraints) => SingleChildScrollView(
                  child: ConstrainedBox(
                    constraints: BoxConstraints(
                      minHeight: constraints.maxHeight,
                    ),
                    child: IntrinsicHeight(
                      child: Padding(
                        padding: const .fromLTRB(24, 8, 24, 28),
                        child: Column(
                          crossAxisAlignment: .stretch,
                          children: [
                            SizedBox(
                              height: AppSizes.minTap,
                              child: Row(
                                children: [
                                  const _StepIndicator(),
                                  const Spacer(),
                                  _TextButton(
                                    text: Words.skip.str,
                                    height: 40,
                                    onTap: _skip,
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: AppSpacing.x2l),
                            Align(
                              alignment: AlignmentDirectional.centerStart,
                              child: PopIn(
                                duration: const Duration(milliseconds: 600),
                                child: IconBadge(
                                  icon: FinoraIcons.wallet,
                                  size: 56,
                                  radius: 18,
                                  iconSize: 26,
                                  background: c.tint,
                                  foreground: c.primaryText,
                                ),
                              ),
                            ),
                            const SizedBox(height: 14),
                            AuthTitle(
                              title: Words.startingBalanceTitle.str,
                              subtitle: Text(Words.startingBalanceDesc.str),
                            ),
                            const SizedBox(height: AppSpacing.x2l),
                            AppBoxedAmountField(
                              controller: _controller,
                              maxDigits: _maxDigits,
                            ),
                            const SizedBox(height: AppSpacing.sm),
                            AmountQuickChips(onAdd: _add),
                            const SizedBox(height: AppSpacing.x2l),
                            Text(
                              Words.whereDoYouKeepIt.str,
                              style: AppTypography.caption.copyWith(
                                fontWeight: .w600,
                                color: c.textSecondary,
                              ),
                            ),
                            const SizedBox(height: AppSpacing.sm),
                            _LocationGrid(
                              value: _location,
                              onChanged: (v) => setState(() => _location = v),
                            ),
                            const SizedBox(height: AppSpacing.x2l),
                            Row(
                              crossAxisAlignment: .start,
                              spacing: 10,
                              children: [
                                Icon(
                                  FinoraIcons.lock,
                                  size: AppSizes.iconSm,
                                  color: c.textTertiary,
                                ),
                                Expanded(
                                  child: Text(
                                    Words.onlyYouCanSee.str,
                                    style: AppTypography.caption.copyWith(
                                      color: c.textTertiary,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const Spacer(),
                            const SizedBox(height: AppSpacing.x2l),
                            AppButton(
                              text: Words.continueAction.str,
                              size: AppButtonSize.large,
                              onPressed: _amount > 0 ? _continue : null,
                            ),
                            const SizedBox(height: AppSpacing.sm),
                            _TextButton(
                              text: Words.illDoItLater.str,
                              height: 48,
                              onTap: _skip,
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

/// 3 × 22×4 bars, all filled (last setup step).
class _StepIndicator extends StatelessWidget {
  const _StepIndicator();

  @override
  Widget build(BuildContext context) {
    return Row(
      spacing: 6,
      children: [
        for (var i = 0; i < 3; i++)
          Container(
            width: 22,
            height: 4,
            decoration: BoxDecoration(
              color: AppPalette.primary500,
              borderRadius: .circular(AppRadius.full),
            ),
          ),
      ],
    );
  }
}

class _TextButton extends StatelessWidget {
  final String text;
  final double height;
  final VoidCallback onTap;

  const _TextButton({
    required this.text,
    required this.height,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return AppPressable(
      onTap: onTap,
      child: SizedBox(
        height: height,
        child: Center(
          child: Text(
            text,
            style: AppTypography.button.copyWith(
              fontSize: 15,
              color: context.appColors.textSecondary,
            ),
          ),
        ),
      ),
    );
  }
}

class _LocationGrid extends StatelessWidget {
  final BalanceLocation value;
  final ValueChanged<BalanceLocation> onChanged;

  const _LocationGrid({required this.value, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final items = [
      (BalanceLocation.cash, FinoraIcons.banknote, Words.cash),
      (BalanceLocation.card, FinoraIcons.card, Words.card),
      (BalanceLocation.both, FinoraIcons.layers, Words.both),
    ];

    return Row(
      spacing: AppSpacing.sm,
      children: [
        for (final (id, icon, label) in items)
          Expanded(
            child: Semantics(
              selected: id == value,
              child: AppPressable(
                onTap: () => onChanged(id),
                child: AnimatedContainer(
                  duration: AppMotion.fast,
                  height: 76,
                  decoration: BoxDecoration(
                    color: id == value ? c.tint : Colors.transparent,
                    borderRadius: .circular(AppRadius.lg),
                    border: Border.all(
                      color: id == value ? AppPalette.primary500 : c.border,
                      width: AppSizes.borderThick,
                    ),
                  ),
                  child: Column(
                    mainAxisAlignment: .center,
                    spacing: 6,
                    children: [
                      Icon(
                        icon,
                        size: AppSizes.iconQuickAction,
                        color: id == value ? c.primaryText : c.textSecondary,
                      ),
                      Text(
                        label.str,
                        style: AppTypography.button.copyWith(
                          fontSize: 14,
                          color: id == value ? c.primaryText : c.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }
}
