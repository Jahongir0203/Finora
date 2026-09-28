import 'package:auto_route/auto_route.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/application/finance/finance_cubit.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_list_tiles.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:finora/presentation/pages/main/main_actions.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'widgets/bank_card.dart';

/// Accounts & cards (docs/screens/PROFILE_SETTINGS.md §4).
@RoutePage()
class AccountsPage extends StatefulWidget {
  const AccountsPage({super.key});

  @override
  State<AccountsPage> createState() => _AccountsPageState();
}

class _AccountsPageState extends State<AccountsPage> {
  static const _cardWidth = 290.0;
  static const _gap = 12.0;

  final _scroll = ScrollController();
  var _active = 0;

  @override
  void initState() {
    super.initState();
    _scroll.addListener(() {
      final i = (_scroll.offset / (_cardWidth + _gap)).round();
      if (i != _active) setState(() => _active = i);
    });
  }

  @override
  void dispose() {
    _scroll.dispose();
    super.dispose();
  }

  void _addCard() => AppToast.info(Words.soon.str);

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final s = context.watch<FinanceCubit>().state;
    final cards = s.accounts.where((a) => a.isCard).toList();
    final active = cards[_active.clamp(0, cards.length - 1)];
    final total = s.accounts.fold<num>(0, (sum, a) => sum + a.balance);
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
              padding: .only(
                top: 8,
                bottom: 28 + MediaQuery.paddingOf(context).bottom,
              ),
              children: [
                Padding(
                  padding: AppSpacing.screenPadding,
                  child: PushHeader(
                    title: Words.accountsAndCards.str,
                    trailing: AppAddButton(
                      semanticLabel: Words.addCardOrAccount.str,
                      onPressed: _addCard,
                    ),
                  ),
                ),
                const SizedBox(height: 18),
                Padding(
                  padding: AppSpacing.screenPadding,
                  child: Column(
                    crossAxisAlignment: .start,
                    children: [
                      Text(
                        Words.totalAcross.tr(args: ['${s.accounts.length}']),
                        style: AppTypography.caption.copyWith(
                          color: c.textSecondary,
                        ),
                      ),
                      Text.rich(
                        TextSpan(
                          text: total.toMoney(),
                          style: AppTypography.display.copyWith(
                            fontSize: 30,
                            color: c.textPrimary,
                          ),
                          children: [
                            TextSpan(
                              text: ' ${AppFormat.currency}',
                              style: AppTypography.body.copyWith(
                                fontWeight: .w500,
                                color: c.textTertiary,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 18),
                SizedBox(
                  height: 180,
                  child: ListView.separated(
                    controller: _scroll,
                    scrollDirection: Axis.horizontal,
                    padding: AppSpacing.screenPadding,
                    physics: const _SnapPhysics(_cardWidth + _gap),
                    itemCount: cards.length,
                    separatorBuilder: (_, _) => const SizedBox(width: _gap),
                    itemBuilder: (_, i) => AppFadeIn(
                      index: i,
                      horizontal: true,
                      step: const Duration(milliseconds: 90),
                      child: BankCard(account: cards[i], holder: s.userName),
                    ),
                  ),
                ),
                const SizedBox(height: 18),
                Row(
                  mainAxisAlignment: .center,
                  spacing: 6,
                  children: [
                    for (var i = 0; i < cards.length; i++)
                      AnimatedContainer(
                        duration: AppMotion.fade,
                        width: i == _active ? 18 : 6,
                        height: 6,
                        decoration: BoxDecoration(
                          color: i == _active
                              ? AppPalette.primary500
                              : c.textDisabled,
                          borderRadius: .circular(AppRadius.full),
                        ),
                      ),
                  ],
                ),
                const SizedBox(height: 18),
                Padding(
                  padding: AppSpacing.screenPadding,
                  child: Row(
                    spacing: AppSpacing.sm,
                    children: [
                      _Action(
                        icon: FinoraIcons.add,
                        color: c.primaryText,
                        label: Words.topUp.str,
                        onTap: () => AppToast.info(Words.topUpChoose.str),
                      ),
                      _Action(
                        icon: FinoraIcons.send,
                        color: c.primaryText,
                        label: Words.transfer.str,
                        onTap: () => MainActions.newTransaction(context),
                      ),
                      _Action(
                        icon: FinoraIcons.snowflake,
                        color: c.info,
                        label: active.frozen
                            ? Words.unfreeze.str
                            : Words.freeze.str,
                        onTap: () {
                          finance.setAccountFrozen(active.id, !active.frozen);
                          AppToast.info(
                            active.frozen
                                ? Words.cardUnfrozen.str
                                : Words.cardFrozen.str,
                          );
                        },
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 18),
                Padding(
                  padding: AppSpacing.screenPadding,
                  child: AppListCard(
                    padding: const .symmetric(horizontal: 16),
                    children: [
                      _Detail(
                        label: Words.cardHolder.str,
                        value: s.userName.toUpperCase(),
                      ),
                      _Detail(
                        label: Words.cardNumber.str,
                        value: '•••• ${active.last4}',
                      ),
                      _Detail(
                        label: Words.status.str,
                        value: active.frozen
                            ? Words.frozen.str
                            : Words.active.str,
                        color: active.frozen ? c.info : c.primaryText,
                      ),
                      _Detail(
                        label: Words.monthlyLimit.str,
                        value: active.monthlyLimit?.toUzs() ?? '—',
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 18),
                Padding(
                  padding: AppSpacing.screenPadding,
                  child: Column(
                    crossAxisAlignment: .stretch,
                    children: [
                      SectionLabel(
                        Words.allAccounts.str,
                        padding: const .symmetric(horizontal: 4),
                      ),
                      const SizedBox(height: AppSpacing.sm),
                      AppListCard(
                        children: [
                          for (final a in s.accounts) _AccountRow(account: a),
                        ],
                      ),
                      const SizedBox(height: 18),
                      _DashedButton(
                        label: Words.addCardOrAccount.str,
                        onTap: _addCard,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Snaps the carousel to card starts.
class _SnapPhysics extends ScrollPhysics {
  final double itemExtent;

  const _SnapPhysics(this.itemExtent, {super.parent});

  @override
  _SnapPhysics applyTo(ScrollPhysics? ancestor) =>
      _SnapPhysics(itemExtent, parent: buildParent(ancestor));

  @override
  Simulation? createBallisticSimulation(
    ScrollMetrics position,
    double velocity,
  ) {
    final page = position.pixels / itemExtent;
    final target =
        (velocity.abs() > 300
            ? (velocity > 0 ? page.ceil() : page.floor())
            : page.round()) *
        itemExtent;
    final clamped = target.clamp(
      position.minScrollExtent,
      position.maxScrollExtent,
    );
    if ((clamped - position.pixels).abs() < 0.5) return null;
    return ScrollSpringSimulation(
      spring,
      position.pixels,
      clamped,
      velocity,
      tolerance: toleranceFor(position),
    );
  }
}

class _Action extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String label;
  final VoidCallback onTap;

  const _Action({
    required this.icon,
    required this.color,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Expanded(
      child: AppPressable(
        onTap: onTap,
        child: Container(
          height: 72,
          decoration: BoxDecoration(
            color: c.surface,
            borderRadius: .circular(18),
            border: Border.all(color: c.border),
          ),
          child: Column(
            mainAxisAlignment: .center,
            spacing: 6,
            children: [
              Icon(icon, size: AppSizes.iconMd, color: color),
              Text(
                label,
                style: AppTypography.bodyMedium.copyWith(
                  fontSize: 13,
                  color: c.textPrimary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Detail extends StatelessWidget {
  final String label;
  final String value;
  final Color? color;

  const _Detail({required this.label, required this.value, this.color});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return SizedBox(
      height: 50,
      child: Row(
        children: [
          Expanded(
            child: Text(
              label,
              style: AppTypography.body.copyWith(
                fontSize: 14,
                color: c.textSecondary,
              ),
            ),
          ),
          Text(
            value,
            style: AppTypography.body.copyWith(
              fontSize: 14,
              fontWeight: .w600,
              color: color ?? c.textPrimary,
              fontFeatures: const [FontFeature.tabularFigures()],
            ),
          ),
        ],
      ),
    );
  }
}

class _AccountRow extends StatelessWidget {
  final Account account;

  const _AccountRow({required this.account});

  @override
  Widget build(BuildContext context) {
    final a = account;
    final name = a.isCard
        ? '${a.bank} ${BankCard.networkTitle(a.network!)}'
        : a.bank;
    final sub = a.isCard
        ? '•••• ${a.last4}${a.isMain ? ' · ${Words.main.str}' : ''}'
        : Words.updatedToday.str;

    return Padding(
      padding: const .symmetric(vertical: 12),
      child: Row(
        spacing: AppSpacing.md,
        children: [
          Container(
            width: 44,
            height: 44,
            alignment: .center,
            decoration: BoxDecoration(
              color: Color(a.color),
              borderRadius: .circular(AppRadius.md),
            ),
            child: Icon(
              a.isCard ? FinoraIcons.card : FinoraIcons.wallet,
              size: AppSizes.iconMd,
              color: AppPalette.white,
            ),
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: .start,
              children: [
                Text(
                  name,
                  maxLines: 1,
                  overflow: .ellipsis,
                  style: context.textStyles.bodyMedium,
                ),
                Text(sub, style: context.textStyles.caption),
              ],
            ),
          ),
          Text(a.balance.toMoney(), style: context.textStyles.amount),
        ],
      ),
    );
  }
}

class _DashedButton extends StatelessWidget {
  final String label;
  final VoidCallback onTap;

  const _DashedButton({required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return AppPressable(
      onTap: onTap,
      child: CustomPaint(
        foregroundPainter: _DashedRectPainter(c.textDisabled),
        child: SizedBox(
          height: 52,
          child: Row(
            mainAxisAlignment: .center,
            spacing: AppSpacing.sm,
            children: [
              Icon(
                FinoraIcons.add,
                size: AppSizes.iconTrailing,
                color: c.primaryText,
              ),
              Text(
                label,
                style: AppTypography.button.copyWith(
                  fontSize: 15,
                  color: c.primaryText,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _DashedRectPainter extends CustomPainter {
  final Color color;

  const _DashedRectPainter(this.color);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 1.5
      ..style = PaintingStyle.stroke;
    final path = Path()
      ..addRRect(
        RRect.fromRectAndRadius(
          (Offset.zero & size).deflate(0.75),
          const Radius.circular(AppRadius.lg),
        ),
      );
    for (final m in path.computeMetrics()) {
      for (var d = 0.0; d < m.length; d += 10) {
        canvas.drawPath(m.extractPath(d, d + 6), paint);
      }
    }
  }

  @override
  bool shouldRepaint(_DashedRectPainter old) => old.color != color;
}
