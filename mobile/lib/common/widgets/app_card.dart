import 'dart:ui' as ui;

import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

import 'app_pressable.dart';

enum AppCardVariant {
  /// `surface` + 1px border, radius 20.
  plain,

  /// AI card: `primary50` + 1px `primary100`.
  tinted,

  /// Balance / goal hero: `primary900`, radius 24, padding 20.
  hero,

  /// Empty state: dashed border.
  dashed,
}

/// Card container (docs/DESIGN_SYSTEM.md §6.7). No shadows.
class AppCard extends StatelessWidget {
  final Widget child;
  final AppCardVariant variant;
  final EdgeInsetsGeometry? padding;
  final VoidCallback? onTap;
  final Color? color;

  const AppCard({
    super.key,
    required this.child,
    this.variant = AppCardVariant.plain,
    this.padding,
    this.onTap,
    this.color,
  });

  const AppCard.hero({
    super.key,
    required this.child,
    this.padding,
    this.onTap,
    this.color,
  }) : variant = AppCardVariant.hero;

  const AppCard.tinted({
    super.key,
    required this.child,
    this.padding,
    this.onTap,
  }) : variant = AppCardVariant.tinted,
       color = null;

  const AppCard.dashed({
    super.key,
    required this.child,
    this.padding,
    this.onTap,
  }) : variant = AppCardVariant.dashed,
       color = null;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final radius = variant == .hero ? AppRadius.x2l : AppRadius.xl;

    final defaultPadding = switch (variant) {
      .hero => const EdgeInsets.all(AppSpacing.xl),
      .dashed => const EdgeInsets.symmetric(horizontal: 16, vertical: 22),
      _ => const EdgeInsets.all(AppSpacing.lg),
    };

    final (bg, border) = switch (variant) {
      .plain => (c.surface, c.border),
      .tinted => (c.tint, context.isDark ? c.tint2 : AppPalette.primary100),
      .hero => (AppPalette.primary900, null),
      .dashed => (c.surface, null),
    };

    Widget card = Container(
      width: double.infinity,
      padding: padding ?? defaultPadding,
      decoration: BoxDecoration(
        color: color ?? bg,
        borderRadius: .circular(radius),
        border: border == null ? null : Border.all(color: border),
      ),
      child: variant == .hero
          ? DefaultTextStyle.merge(
              style: const TextStyle(color: Colors.white),
              child: IconTheme.merge(
                data: const IconThemeData(color: AppPalette.primary200),
                child: child,
              ),
            )
          : child,
    );

    if (variant == .dashed) {
      card = CustomPaint(
        foregroundPainter: _DashedBorderPainter(
          color: c.border,
          radius: radius,
        ),
        child: card,
      );
    }

    if (onTap == null) return card;
    return AppPressable(
      onTap: onTap,
      scale: AppMotion.pressScaleCard,
      child: card,
    );
  }
}

class _DashedBorderPainter extends CustomPainter {
  final Color color;
  final double radius;

  const _DashedBorderPainter({required this.color, required this.radius});

  @override
  void paint(Canvas canvas, Size size) {
    const dash = 6.0, gap = 4.0;
    final paint = Paint()
      ..color = color
      ..strokeWidth = 1
      ..style = PaintingStyle.stroke;

    final rrect = RRect.fromRectAndRadius(
      Offset.zero & size,
      Radius.circular(radius),
    ).deflate(0.5);

    final path = Path()..addRRect(rrect);
    final dashed = Path();
    for (final ui.PathMetric metric in path.computeMetrics()) {
      for (var d = 0.0; d < metric.length; d += dash + gap) {
        dashed.addPath(metric.extractPath(d, d + dash), Offset.zero);
      }
    }
    canvas.drawPath(dashed, paint);
  }

  @override
  bool shouldRepaint(_DashedBorderPainter old) =>
      old.color != color || old.radius != radius;
}
