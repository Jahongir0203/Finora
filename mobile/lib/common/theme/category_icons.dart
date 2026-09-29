import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:flutter/widgets.dart';
import 'package:lucide_icons_flutter/lucide_icons.dart';

/// Lucide names used by categories and goals → [IconData].
abstract final class CategoryIcons {
  static const Map<String, IconData> all = {
    'shopping-cart': LucideIcons.shoppingCart,
    'utensils': LucideIcons.utensils,
    'coffee': LucideIcons.coffee,
    'car': LucideIcons.car,
    'bus': LucideIcons.bus,
    'receipt': LucideIcons.receipt,
    'heart-pulse': LucideIcons.heartPulse,
    'dumbbell': LucideIcons.dumbbell,
    'shopping-bag': LucideIcons.shoppingBag,
    'house': LucideIcons.house,
    'repeat': LucideIcons.repeat,
    'plane': LucideIcons.plane,
    'graduation-cap': LucideIcons.graduationCap,
    'gift': LucideIcons.gift,
    'baby': LucideIcons.baby,
    'paw-print': LucideIcons.pawPrint,
    'smartphone': LucideIcons.smartphone,
    'briefcase': LucideIcons.briefcase,
    'arrow-down-left': LucideIcons.arrowDownLeft,
    'arrow-left-right': LucideIcons.arrowLeftRight,
    'trending-up': LucideIcons.trendingUp,
    'piggy-bank': LucideIcons.piggyBank,
    'laptop': LucideIcons.laptop,
    'heart': LucideIcons.heart,
    'shield-check': LucideIcons.shieldCheck,
  };

  /// Category sheet icon picker (18).
  static const categoryPicker = [
    'shopping-cart', 'utensils', 'coffee', 'car', 'bus', 'receipt', //
    'heart-pulse', 'dumbbell', 'shopping-bag', 'house', 'repeat', 'plane',
    'graduation-cap', 'gift', 'baby', 'paw-print', 'smartphone', 'briefcase',
  ];

  /// New goal icon picker (8).
  static const goalPicker = [
    'piggy-bank', 'plane', 'laptop', 'car', //
    'house', 'graduation-cap', 'heart', 'gift',
  ];

  /// Category sheet colors.
  static const colors = [
    0xFF10B981, 0xFF14B8A6, 0xFF0EA5E9, 0xFF3B82F6, 0xFF6366F1, //
    0xFF8B5CF6, 0xFFEC4899, 0xFFEF4444, 0xFFF59E0B, 0xFF84CC16,
  ];

  static IconData of(String name) => all[name] ?? LucideIcons.circle;
}

extension CategoryUi on Category {
  IconData get iconData => CategoryIcons.of(icon);

  Color get colorValue => Color(color);
}

extension GoalUi on Goal {
  IconData get iconData => CategoryIcons.of(icon);
}
