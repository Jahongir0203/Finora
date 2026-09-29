import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

/// `fnPop` (scale .6 → 1.06 → 1) played once on first build.
class PopIn extends StatelessWidget {
  final Widget child;
  final Duration duration;

  const PopIn({
    super.key,
    required this.child,
    this.duration = const Duration(milliseconds: 500),
  });

  @override
  Widget build(BuildContext context) {
    if (MediaQuery.disableAnimationsOf(context)) return child;

    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: duration,
      builder: (_, t, child) {
        final scale = t < 0.7
            ? 0.6 + 0.46 * Curves.easeOut.transform(t / 0.7)
            : 1.06 -
                  0.06 *
                      Curves.easeInOut.transform(
                        ((t - 0.7) / 0.3).clamp(0.0, 1.0),
                      );
        return Opacity(
          opacity: (t * 2).clamp(0.0, 1.0),
          child: Transform.scale(scale: scale, child: child),
        );
      },
      child: child,
    );
  }
}

/// Rounded icon tile: 64/r20 on PIN screens, 56/r18 on setup screens.
class IconBadge extends StatelessWidget {
  final IconData icon;
  final double size;
  final double radius;
  final double iconSize;
  final Color background;
  final Color foreground;

  const IconBadge({
    super.key,
    required this.icon,
    required this.background,
    required this.foreground,
    this.size = 64,
    this.radius = AppRadius.xl,
    this.iconSize = 30,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      alignment: .center,
      decoration: BoxDecoration(
        color: background,
        borderRadius: .circular(radius),
      ),
      child: Icon(icon, size: iconSize, color: foreground),
    );
  }
}
