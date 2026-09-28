import 'dart:math' as math;

import 'package:auto_route/auto_route.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/application/finance/finance_cubit.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/category_icons.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/widgets/app_segment_control.dart';
import 'package:finora/common/widgets/category_chip.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:finora/presentation/pages/main/main_actions.dart';
import 'package:finora/presentation/pages/pin/widgets/pin_badge.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'stats_data.dart';
import 'widgets/category_donut.dart';
import 'widgets/spending_trend_chart.dart';

/// Statistics tab (docs/screens/STATS_INSIGHTS.md §1).
@RoutePage()
class StatsPage extends StatefulWidget {
  const StatsPage({super.key});

  @override
  State<StatsPage> createState() => _StatsPageState();
}

class _StatsPageState extends State<StatsPage> {
  var _period = StatsPeriod.month;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final snapshot = context.watch<FinanceCubit>().state;
    // New users see the empty state until there is data to chart.
    final empty = snapshot.transactions.isEmpty;

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
                TabHeader(
                  title: Words.statistics.str,
                  actions: [
                    _AiTipsButton(onTap: () => MainActions.insights(context)),
                    AppIconButton(
                      icon: FinoraIcons.export,
                      semanticLabel: Words.exportReport.str,
                      onPressed: () => MainActions.export(context),
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.lg),
                if (empty)
                  const _Empty()
                else ...[
                  AppSegmentControl(
                    height: 36,
                    trackColor: c.border,
                    index: _period.index,
                    children: [Words.week.str, Words.month.str, Words.year.str],
                    onChanged: (i) =>
                        setState(() => _period = StatsPeriod.values[i]),
                  ),
                  const SizedBox(height: AppSpacing.lg),
                  _DonutCard(period: _period),
                  const SizedBox(height: AppSpacing.lg),
                  _TrendCard(period: _period),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _AiTipsButton extends StatelessWidget {
  final VoidCallback onTap;

  const _AiTipsButton({required this.onTap});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return AppPressable(
      onTap: onTap,
      child: Container(
        height: AppSizes.minTap,
        padding: const .symmetric(horizontal: 14),
        decoration: BoxDecoration(
          color: c.tint,
          borderRadius: .circular(AppRadius.full),
        ),
        child: Row(
          mainAxisSize: .min,
          spacing: 6,
          children: [
            Icon(FinoraIcons.ai, size: AppSizes.iconSm, color: c.primaryText),
            Text(
              Words.aiTips.str,
              style: AppTypography.button.copyWith(
                fontSize: 14,
                color: c.primaryText,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DonutCard extends StatelessWidget {
  final StatsPeriod period;

  const _DonutCard({required this.period});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final snapshot = context.watch<FinanceCubit>().state;
    final rows = statsBreakdown(period);
    final total = rows.fold<num>(0, (s, e) => s + e.$2);
    final categories = [for (final (id, _) in rows) snapshot.category(id)];

    return _StatsCard(
      child: Column(
        spacing: 20,
        children: [
          CategoryDonut(
            total: total,
            segments: [
              for (final (i, (_, v)) in rows.indexed)
                (categories[i]?.colorValue ?? c.textTertiary, v),
            ],
          ),
          Column(
            children: [
              for (final (i, (_, v)) in rows.indexed)
                AppFadeIn(
                  index: i,
                  child: Container(
                    padding: const .symmetric(vertical: 10),
                    decoration: i == 0
                        ? null
                        : BoxDecoration(
                            border: Border(top: BorderSide(color: c.divider)),
                          ),
                    child: Row(
                      spacing: AppSpacing.md,
                      children: [
                        CategoryTile(
                          category: categories[i],
                          size: 36,
                          radius: 12,
                          iconSize: 18,
                        ),
                        Expanded(
                          child: Text(
                            categories[i]?.name ?? '',
                            maxLines: 1,
                            overflow: .ellipsis,
                            style: context.textStyles.bodyMedium,
                          ),
                        ),
                        SizedBox(
                          width: 40,
                          child: Text(
                            '${(v / total * 100).round()}%',
                            textAlign: .right,
                            style: AppTypography.caption.copyWith(
                              color: c.textTertiary,
                            ),
                          ),
                        ),
                        SizedBox(
                          width: 96,
                          child: Text(
                            v.toMoney(),
                            textAlign: .right,
                            style: context.textStyles.amount,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}

class _TrendCard extends StatelessWidget {
  final StatsPeriod period;

  const _TrendCard({required this.period});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return _StatsCard(
      child: Column(
        crossAxisAlignment: .stretch,
        spacing: AppSpacing.lg,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  Words.spendingTrend.str,
                  style: context.textStyles.titleSmall,
                ),
              ),
              Icon(
                FinoraIcons.trendDown,
                size: AppSizes.iconSm,
                color: c.primaryText,
              ),
              const SizedBox(width: 4),
              Text(
                Words.vsLast.tr(args: ['8']),
                style: AppTypography.caption.copyWith(
                  fontWeight: .w600,
                  color: c.primaryText,
                ),
              ),
            ],
          ),
          SpendingTrendChart(
            key: ValueKey(period),
            bars: statsTrend(period),
            current: statsCurrentBar(period),
          ),
        ],
      ),
    );
  }
}

class _StatsCard extends StatelessWidget {
  final Widget child;

  const _StatsCard({required this.child});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Container(
      padding: const .all(20),
      decoration: BoxDecoration(
        color: c.surface,
        borderRadius: .circular(AppRadius.x2l),
        border: Border.all(color: c.border),
      ),
      child: child,
    );
  }
}

/// "Not enough data yet" with a 3-part ring (§1.5).
class _Empty extends StatelessWidget {
  const _Empty();

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Padding(
      padding: const .only(top: 64),
      child: Column(
        spacing: AppSpacing.md,
        children: [
          PopIn(
            duration: const Duration(milliseconds: 600),
            child: SizedBox.square(
              dimension: 120,
              child: Stack(
                alignment: .center,
                children: [
                  CustomPaint(
                    size: const Size.square(120),
                    painter: _RingPainter([
                      (c.tint2, 0.35),
                      (c.divider, 0.25),
                      (c.tint, 0.40),
                    ]),
                  ),
                  Container(
                    width: 84,
                    height: 84,
                    alignment: .center,
                    decoration: BoxDecoration(
                      color: c.background,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      FinoraIcons.stats,
                      size: 30,
                      color: c.primaryText,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: AppSpacing.xs),
          Text(
            Words.notEnoughData.str,
            style: context.textStyles.titleSmall.copyWith(
              fontSize: 18,
              fontWeight: .w700,
            ),
          ),
          ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 270),
            child: Text(
              Words.statsEmptyDesc.str,
              textAlign: .center,
              style: AppTypography.body.copyWith(
                fontSize: 14,
                height: 20 / 14,
                color: c.textSecondary,
              ),
            ),
          ),
          const SizedBox(height: AppSpacing.xs),
          AppButton(
            text: Words.addTransaction.str,
            size: AppButtonSize.small,
            expanded: false,
            onPressed: () => MainActions.newTransaction(context),
          ),
        ],
      ),
    );
  }
}

class _RingPainter extends CustomPainter {
  final List<(Color, double)> parts;

  const _RingPainter(this.parts);

  @override
  void paint(Canvas canvas, Size size) {
    final rect = Offset.zero & size;
    var start = -math.pi / 2;
    for (final (color, f) in parts) {
      final sweep = math.pi * 2 * f;
      canvas.drawArc(rect, start, sweep, true, Paint()..color = color);
      start += sweep;
    }
  }

  @override
  bool shouldRepaint(_RingPainter old) => old.parts != parts;
}
