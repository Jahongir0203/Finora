import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

import 'app_pressable.dart';

enum AppChipStyle {
  /// Selected filter: dark (`textPrimary`) fill.
  filter,

  /// Selected category / date: `primary500` fill.
  brand,

  /// Always tinted (`primary50` + `primary700`).
  tinted,
}

/// 36px pill chip (docs/DESIGN_SYSTEM.md §6.3).
class AppChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback? onTap;
  final AppChipStyle style;
  final IconData? icon;

  /// Icon color when not selected (category chips use the category color).
  final Color? iconColor;
  final double height;

  const AppChip({
    super.key,
    required this.label,
    this.selected = false,
    this.onTap,
    this.style = AppChipStyle.filter,
    this.icon,
    this.iconColor,
    this.height = AppSizes.chip,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    final (bg, fg, border) = switch ((style, selected)) {
      (.tinted, _) => (c.tint, c.primaryText, null),
      (.filter, true) => (c.textPrimary, c.surface, null),
      (.brand, true) => (c.primary, c.onPrimary, null),
      _ => (c.surface, c.textPrimary, c.border),
    };

    return AppPressable(
      onTap: onTap,
      child: AnimatedContainer(
        duration: AppMotion.fast,
        curve: AppMotion.ease,
        height: height,
        padding: const .symmetric(horizontal: 15),
        decoration: BoxDecoration(
          color: bg,
          borderRadius: .circular(AppRadius.full),
          border: border == null ? null : Border.all(color: border),
        ),
        child: Row(
          mainAxisSize: .min,
          spacing: 6,
          children: [
            if (icon != null)
              Icon(
                icon,
                size: AppSizes.iconSm,
                color: selected ? fg : iconColor ?? fg,
              ),
            Text(
              label,
              style: AppTypography.bodyMedium.copyWith(fontSize: 14, color: fg),
            ),
          ],
        ),
      ),
    );
  }
}
