import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

/// Horizontal ±8px shake for invalid input / wrong PIN (`fnShake`, §9).
///
/// ```dart
/// final _shake = AppShakeController();
/// AppShake(controller: _shake, child: ...);
/// _shake.shake();
/// ```
class AppShakeController extends ChangeNotifier {
  void shake() => notifyListeners();
}

class AppShake extends StatefulWidget {
  final AppShakeController controller;
  final Widget child;

  const AppShake({super.key, required this.controller, required this.child});

  @override
  State<AppShake> createState() => _AppShakeState();
}

class _AppShakeState extends State<AppShake>
    with SingleTickerProviderStateMixin {
  // X keyframes: 0 → −8 → 7 → −5 → 3 → 0
  static final _offsets = TweenSequence<double>([
    for (final (a, b) in const [
      (0.0, -8.0),
      (-8.0, 7.0),
      (7.0, -5.0),
      (-5.0, 3.0),
      (3.0, 0.0),
    ])
      TweenSequenceItem(
        tween: Tween(begin: a, end: b),
        weight: 1,
      ),
  ]);

  late final _anim = AnimationController(
    vsync: this,
    duration: AppMotion.shake,
  );

  @override
  void initState() {
    super.initState();
    widget.controller.addListener(_onShake);
  }

  @override
  void didUpdateWidget(AppShake oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.controller != widget.controller) {
      oldWidget.controller.removeListener(_onShake);
      widget.controller.addListener(_onShake);
    }
  }

  void _onShake() => _anim.forward(from: 0);

  @override
  void dispose() {
    widget.controller.removeListener(_onShake);
    _anim.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _anim,
      child: widget.child,
      builder: (_, child) {
        final dx = _offsets.transform(_anim.value);
        return Transform.translate(offset: Offset(dx, 0), child: child);
      },
    );
  }
}
