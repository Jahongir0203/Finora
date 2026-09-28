import 'package:flutter/material.dart';

/// Spacing, 4px base (docs/DESIGN_SYSTEM.md §5).
abstract final class AppSpacing {
  static const xs = 4.0;
  static const sm = 8.0;
  static const md = 12.0;
  static const lg = 16.0;
  static const xl = 20.0;
  static const x2l = 24.0;
  static const x3l = 32.0;

  /// Horizontal screen padding.
  static const screen = 20.0;
  static const screenPadding = EdgeInsets.symmetric(horizontal: screen);
}

abstract final class AppRadius {
  static const sm = 10.0;
  static const md = 14.0;
  static const lg = 16.0;
  static const xl = 20.0;
  static const x2l = 24.0;
  static const sheet = 28.0;
  static const full = 999.0;
}

abstract final class AppSizes {
  // Icons
  static const iconInline = 14.0;
  static const iconSm = 16.0;
  static const iconTrailing = 18.0;
  static const iconMd = 20.0;
  static const iconQuickAction = 22.0;
  static const iconLg = 24.0;
  static const iconHero = 28.0;

  // Touch & controls
  static const minTap = 44.0;
  static const button = 52.0;
  static const buttonLarge = 56.0;
  static const buttonPill = 36.0;
  static const input = 50.0;
  static const inputAmount = 70.0;
  static const chip = 36.0;

  // Rows
  static const transactionRow = 68.0;
  static const settingsRow = 56.0;

  // Borders
  static const borderThin = 1.0;
  static const borderThick = 1.5;
}

abstract final class AppShadows {
  static const toggleKnob = [
    BoxShadow(color: Color(0x33000000), blurRadius: 3, offset: Offset(0, 1)),
  ];

  static const segmentActive = [
    BoxShadow(color: Color(0x14000000), blurRadius: 3, offset: Offset(0, 1)),
  ];

  static const toast = [
    BoxShadow(color: Color(0x2E06140E), blurRadius: 24, offset: Offset(0, 8)),
  ];
}
