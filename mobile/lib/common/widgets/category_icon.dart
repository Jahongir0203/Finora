import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

/// Rounded square with category color at 12% and the icon in full color.
class CategoryIcon extends StatelessWidget {
  final IconData icon;
  final Color color;
  final double size;
  final double iconSize;

  const CategoryIcon({
    super.key,
    required this.icon,
    required this.color,
    this.size = 44,
    this.iconSize = AppSizes.iconMd,
  });

  CategoryIcon.category(
    AppCategory category, {
    super.key,
    this.size = 44,
    this.iconSize = AppSizes.iconMd,
  }) : icon = category.icon,
       color = category.color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      alignment: .center,
      decoration: BoxDecoration(
        color: AppPalette.tintOf(color),
        borderRadius: .circular(size >= 44 ? AppRadius.md : AppRadius.md - 2),
      ),
      child: Icon(icon, size: iconSize, color: color),
    );
  }
}
