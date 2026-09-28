import 'dart:ui';

/// Theme-dependent color tokens (docs/DESIGN_SYSTEM.md §2, §10).
abstract interface class AppColorSchema {
  // Brand
  Color get primary; // primary500, same in both modes
  Color get primaryPressed; // primary600
  Color get onPrimary; // text/icons on primary500, never white
  Color get primaryText; // primary700 / primary400 (dark): income, active tab
  Color get tint; // primary50: secondary button, tinted surfaces
  Color get tint2; // primary100: avatar, soft background

  // Neutral
  Color get background;
  Color get surface;
  Color get textPrimary;
  Color get textSecondary;
  Color get textTertiary;
  Color get textDisabled;
  Color get border;
  Color get divider;
  Color get scrim;

  // Semantic
  Color get success;
  Color get danger;
  Color get dangerSoft;
  Color get onDanger;
  Color get warning;
  Color get warningText;
  Color get warningSoft;
  Color get info;
}
