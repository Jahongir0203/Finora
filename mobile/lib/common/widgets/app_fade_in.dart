import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

/// Entrance animation: `fnIn` (fade + Y 14→0) or `fnPush` (fade + X 32→0).
///
/// Use [index] for staggered lists: delay = [delay] + index × [step].
class AppFadeIn extends StatefulWidget {
  final Widget child;
  final int index;
  final bool horizontal;
  final Duration delay;
  final Duration step;

  /// Defaults to [AppMotion.enter] (vertical) or [AppMotion.push].
  final Duration? duration;

  const AppFadeIn({
    super.key,
    required this.child,
    this.index = 0,
    this.horizontal = false,
    this.delay = Duration.zero,
    this.step = AppMotion.stagger,
    this.duration,
  });

  @override
  State<AppFadeIn> createState() => _AppFadeInState();
}

class _AppFadeInState extends State<AppFadeIn>
    with SingleTickerProviderStateMixin {
  late final _controller = AnimationController(
    vsync: this,
    duration:
        widget.duration ??
        (widget.horizontal ? AppMotion.push : AppMotion.enter),
  );
  late final _curve = CurvedAnimation(
    parent: _controller,
    curve: AppMotion.ease,
  );

  @override
  void initState() {
    super.initState();
    final delay = widget.delay + widget.step * widget.index.clamp(0, 12);
    Future.delayed(delay, () {
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
    if (MediaQuery.disableAnimationsOf(context)) return widget.child;

    return FadeTransition(
      opacity: _curve,
      child: AnimatedBuilder(
        animation: _curve,
        child: widget.child,
        builder: (_, child) {
          final d = 1 - _curve.value;
          return Transform.translate(
            offset: widget.horizontal ? Offset(32 * d, 0) : Offset(0, 14 * d),
            child: child,
          );
        },
      ),
    );
  }
}
