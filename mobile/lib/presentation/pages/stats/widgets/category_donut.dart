import 'dart:math' as math;

import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/words/words.dart';
import 'package:flutter/material.dart';

/// 200px donut, 28px ring, total in the middle (STATS_INSIGHTS.md §1.3).
class CategoryDonut extends StatelessWidget {
  final List<(Color, num)> segments;
  final num total;

  const CategoryDonut({super.key, required this.segments, required this.total});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final sum = segments.fold<num>(0, (s, e) => s + e.$2);
    final fractions = [for (final (_, v) in segments) sum == 0 ? 0.0 : v / sum];

    // fnSpin on first build: rotate −90° → 0, scale .85 → 1, fade in.
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: const Duration(milliseconds: 900),
      curve: AppMotion.ease,
      builder: (_, t, child) => Opacity(
        opacity: t,
        child: Transform.rotate(
          angle: -math.pi / 2 * (1 - t),
          child: Transform.scale(scale: 0.85 + 0.15 * t, child: child),
        ),
      ),
      child: SizedBox.square(
        dimension: 200,
        child: Stack(
          alignment: .center,
          children: [
            Positioned.fill(
              child: TweenAnimationBuilder<List<double>>(
                tween: _ListTween(end: fractions),
                duration: const Duration(milliseconds: 500),
                curve: AppMotion.ease,
                builder: (_, values, _) => CustomPaint(
                  painter: _DonutPainter(
                    colors: [for (final (color, _) in segments) color],
                    fractions: values,
                  ),
                ),
              ),
            ),
            Container(
              width: 144,
              height: 144,
              decoration: BoxDecoration(
                color: c.surface,
                shape: BoxShape.circle,
              ),
              child: Column(
                mainAxisAlignment: .center,
                children: [
                  Text(
                    Words.spent.str.toUpperCase(),
                    style: AppTypography.label.copyWith(color: c.textTertiary),
                  ),
                  Text(
                    total.toShort(),
                    style: AppTypography.display.copyWith(
                      fontSize: 22,
                      height: 28 / 22,
                      letterSpacing: 0,
                      color: c.textPrimary,
                    ),
                  ),
                  Text(
                    AppFormat.currency,
                    style: AppTypography.caption.copyWith(
                      fontSize: 12,
                      color: c.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ListTween extends Tween<List<double>> {
  _ListTween({required List<double> end}) : super(begin: end, end: end);

  @override
  List<double> lerp(double t) {
    final a = begin!, b = end!;
    if (a.length != b.length) return b;
    return [for (var i = 0; i < b.length; i++) a[i] + (b[i] - a[i]) * t];
  }
}

class _DonutPainter extends CustomPainter {
  final List<Color> colors;
  final List<double> fractions;

  const _DonutPainter({required this.colors, required this.fractions});

  static const _stroke = 28.0;

  @override
  void paint(Canvas canvas, Size size) {
    final rect = (Offset.zero & size).deflate(_stroke / 2);
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = _stroke
      ..strokeCap = StrokeCap.butt;

    var start = -math.pi / 2;
    for (var i = 0; i < fractions.length; i++) {
      final sweep = math.pi * 2 * fractions[i];
      canvas.drawArc(rect, start, sweep, false, paint..color = colors[i]);
      start += sweep;
    }
  }

  @override
  bool shouldRepaint(_DonutPainter old) =>
      old.fractions != fractions || old.colors != colors;
}
