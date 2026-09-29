import 'package:finora/common/theme/category_icons.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:flutter/material.dart';

import 'app_chip.dart';

/// 38px category chip: icon in the category color; selected = `ink` fill
/// (docs/screens/ACTIVITY_SCAN.md §3.3).
class CategoryChip extends StatelessWidget {
  final Category category;
  final bool selected;
  final VoidCallback onTap;

  const CategoryChip({
    super.key,
    required this.category,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Semantics(
      selected: selected,
      child: AppChip(
        label: category.name,
        icon: category.iconData,
        iconColor: category.colorValue,
        selected: selected,
        height: 38,
        onTap: onTap,
      ),
    );
  }
}

/// Category icon tile: category color at 12% behind the icon.
class CategoryTile extends StatelessWidget {
  final Category? category;
  final double size;
  final double radius;
  final double iconSize;

  const CategoryTile({
    super.key,
    required this.category,
    this.size = 44,
    this.radius = 14,
    this.iconSize = AppSizes.iconMd,
  });

  @override
  Widget build(BuildContext context) {
    final color = category?.colorValue ?? context.appColors.textSecondary;

    return Container(
      width: size,
      height: size,
      alignment: .center,
      decoration: BoxDecoration(
        color: AppPalette.tintOf(color),
        borderRadius: .circular(radius),
      ),
      child: Icon(
        category?.iconData ?? FinoraIcons.wallet,
        size: iconSize,
        color: color,
      ),
    );
  }
}
