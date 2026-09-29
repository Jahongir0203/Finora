import 'package:flutter/material.dart';

/// `fnFloat`: slow vertical bob (Y 0 → −[distance] → 0), infinite.
/// Stops when the system asks to reduce motion.
class AppFloat extends StatefulWidget {
  final Widget child;
  final double distance;
  final Duration period;
  final Duration delay;

  const AppFloat({
    super.key,
    required this.child,
    this.distance = 8,
    this.period = const Duration(milliseconds: 4000),
    this.delay = Duration.zero,
  });

  @override
  State<AppFloat> createState() => _AppFloatState();
}

class _AppFloatState extends State<AppFloat>
    with SingleTickerProviderStateMixin {
  late final _controller = AnimationController(
    vsync: this,
    duration: widget.period,
  );
  var _started = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (MediaQuery.disableAnimationsOf(context)) {
      _controller.stop();
      _controller.value = 0;
    } else if (!_started) {
      _started = true;
      Future.delayed(widget.delay, () {
        if (mounted) _controller.repeat();
      });
    } else if (!_controller.isAnimating) {
      _controller.repeat();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      child: widget.child,
      builder: (_, child) {
        // 0 → 1 → 0 over one period, eased.
        final t = _controller.value;
        final wave = Curves.easeInOut.transform(t < 0.5 ? t * 2 : (1 - t) * 2);
        return Transform.translate(
          offset: Offset(0, -widget.distance * wave),
          child: child,
        );
      },
    );
  }
}
