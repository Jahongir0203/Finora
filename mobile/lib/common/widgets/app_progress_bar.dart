import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

/// Budget / goal progress (docs/DESIGN_SYSTEM.md §6.6).
///
/// Color by [value]: < 0.75 `primary`, 0.75–1.0 `warning`, > 1.0 `danger`.
/// Fills in from the left with `fnBar` after [delay].
class AppProgressBar extends StatefulWidget {
  /// 0.0 … ∞ (values above 1.0 mean over the limit).
  final double value;
  final double height;

  /// On a dark hero card (`primary900`).
  final bool onDark;
  final Color? color;
  final Color? trackColor;
  final Duration delay;

  const AppProgressBar({
    super.key,
    required this.value,
    this.height = 8,
    this.onDark = false,
    this.color,
    this.trackColor,
    this.delay = Duration.zero,
  });

  static Color colorFor(double value, AppColorSchema c) {
    if (value > 1) return c.danger;
    if (value >= 0.75) return c.warning;
    return c.primary;
  }

  @override
  State<AppProgressBar> createState() => _AppProgressBarState();
}

class _AppProgressBarState extends State<AppProgressBar>
    with SingleTickerProviderStateMixin {
  late final _controller = AnimationController(
    vsync: this,
    duration: AppMotion.bar,
  );
  late final _curve = CurvedAnimation(
    parent: _controller,
    curve: AppMotion.ease,
  );

  @override
  void initState() {
    super.initState();
    Future.delayed(widget.delay, () {
      if (mounted) _controller.forward();
    });
  }

  @override
  void dispose() {
    _curve.dispose();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final fill = widget.color ?? AppProgressBar.colorFor(widget.value, c);
    final track =
        widget.trackColor ?? (widget.onDark ? AppPalette.heroTrack : c.divider);

    return ClipRRect(
      borderRadius: .circular(AppRadius.full),
      child: Container(
        height: widget.height,
        color: track,
        alignment: Alignment.centerLeft,
        child: AnimatedBuilder(
          animation: _curve,
          builder: (_, _) => FractionallySizedBox(
            widthFactor: widget.value.clamp(0, 1) * _curve.value,
            heightFactor: 1,
            child: DecoratedBox(
              decoration: BoxDecoration(
                color: fill,
                borderRadius: .circular(AppRadius.full),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
