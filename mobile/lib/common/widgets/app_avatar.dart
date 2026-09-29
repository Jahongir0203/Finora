import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

/// Initials avatar (docs/DESIGN_SYSTEM.md §6.15). Sizes: 34, 44, 72, 88.
class AppAvatar extends StatelessWidget {
  final String name;
  final double size;
  final bool onDark;

  /// Defaults to 38% of [size].
  final double? fontSize;

  const AppAvatar({
    super.key,
    required this.name,
    this.size = 44,
    this.onDark = false,
    this.fontSize,
  });

  static String initials(String name) {
    final parts = name.trim().split(RegExp(r'\s+')).where((e) => e.isNotEmpty);
    return parts.take(2).map((e) => e.characters.first.toUpperCase()).join();
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final bg = onDark ? AppPalette.heroAvatarBg : c.tint2;
    final fg = onDark ? AppPalette.primary200 : c.primaryText;

    return Semantics(
      label: name,
      child: Container(
        width: size,
        height: size,
        alignment: .center,
        decoration: BoxDecoration(color: bg, shape: BoxShape.circle),
        child: ExcludeSemantics(
          child: Text(
            initials(name),
            style: AppTypography.bodyMedium.copyWith(
              fontSize: fontSize ?? size * 0.38,
              height: 1,
              fontWeight: .w700,
              color: fg,
            ),
          ),
        ),
      ),
    );
  }
}
