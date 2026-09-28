import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

/// Bars 150px tall, max 28 wide, label below (STATS_INSIGHTS.md §1.2).
class SpendingTrendChart extends StatelessWidget {
  final List<(String, double)> bars;
  final int current;

  const SpendingTrendChart({
    super.key,
    required this.bars,
    required this.current,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final max = bars.fold<double>(0, (m, e) => e.$2 > m ? e.$2 : m);

    return SizedBox(
      height: 150,
      child: Row(
        crossAxisAlignment: .end,
        spacing: 6,
        children: [
          for (final (i, (label, v)) in bars.indexed)
            Expanded(
              child: Column(
                mainAxisAlignment: .end,
                spacing: 6,
                children: [
                  // fnCol: grows from the bottom, 40ms stagger.
                  TweenAnimationBuilder<double>(
                    key: ValueKey('${bars.length}-$i'),
                    tween: Tween(begin: 0, end: 1),
                    duration: Duration(milliseconds: 700 + i * 40),
                    curve: AppMotion.ease,
                    builder: (_, t, child) => Align(
                      alignment: Alignment.bottomCenter,
                      heightFactor: t,
                      child: child,
                    ),
                    child: AnimatedContainer(
                      duration: const Duration(milliseconds: 500),
                      curve: AppMotion.ease,
                      constraints: const BoxConstraints(maxWidth: 28),
                      height: max == 0 ? 4 : (v / max * 118).clamp(4, 118),
                      decoration: BoxDecoration(
                        color: v == 0
                            ? c.divider
                            : i == current
                            ? AppPalette.primary500
                            : c.tint2,
                        borderRadius: .circular(8),
                      ),
                    ),
                  ),
                  Text(
                    label,
                    style: AppTypography.tabLabel.copyWith(
                      color: c.textTertiary,
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}
