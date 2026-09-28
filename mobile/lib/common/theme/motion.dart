import 'package:flutter/animation.dart';

/// Motion tokens (docs/DESIGN_SYSTEM.md §9).
abstract final class AppMotion {
  static const ease = Cubic(0.2, 0.8, 0.2, 1);
  static const easeSheet = Cubic(0.2, 0.9, 0.3, 1);

  static const fast = Duration(milliseconds: 250);
  static const fade = Duration(milliseconds: 300);
  static const push = Duration(milliseconds: 420);
  static const sheet = Duration(milliseconds: 420);
  static const enter = Duration(milliseconds: 450);
  static const shake = Duration(milliseconds: 450);
  static const pop = Duration(milliseconds: 550);
  static const bar = Duration(milliseconds: 1100);

  static const toastVisible = Duration(milliseconds: 2200);

  /// Step between list items in staggered entrances.
  static const stagger = Duration(milliseconds: 50);

  static const pressScale = 0.96;
  static const pressScaleCard = 0.98;
}
