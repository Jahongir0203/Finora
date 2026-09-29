import 'package:flutter/material.dart';

import 'core/schemas.dart';
import 'palette.dart';

class LightColorScheme implements AppColorSchema {
  const LightColorScheme();

  @override
  Color get primary => AppPalette.primary500;

  @override
  Color get primaryPressed => AppPalette.primary600;

  @override
  Color get onPrimary => AppPalette.primary950;

  @override
  Color get primaryText => AppPalette.primary700;

  @override
  Color get tint => AppPalette.primary50;

  @override
  Color get tint2 => AppPalette.primary100;

  @override
  Color get background => const Color(0xFFF4F7F5);

  @override
  Color get surface => const Color(0xFFFFFFFF);

  @override
  Color get textPrimary => const Color(0xFF0E1A14);

  @override
  Color get textSecondary => const Color(0xFF56655D);

  @override
  Color get textTertiary => const Color(0xFF8B988F);

  @override
  Color get textDisabled => const Color(0xFFC3CDC7);

  @override
  Color get border => const Color(0xFFE4EAE6);

  @override
  Color get divider => const Color(0xFFEEF2EF);

  @override
  Color get scrim => const Color(0x7306140E);

  @override
  Color get success => AppPalette.primary500;

  @override
  Color get danger => const Color(0xFFDC2626);

  @override
  Color get dangerSoft => const Color(0xFFFEF2F2);

  @override
  Color get onDanger => const Color(0xFFFFFFFF);

  @override
  Color get warning => const Color(0xFFF59E0B);

  @override
  Color get warningText => const Color(0xFFB45309);

  @override
  Color get warningSoft => const Color(0xFFFEF3C7);

  @override
  Color get info => const Color(0xFF3B82F6);
}

class DarkColorScheme implements AppColorSchema {
  const DarkColorScheme();

  @override
  Color get primary => AppPalette.primary500;

  @override
  Color get primaryPressed => AppPalette.primary600;

  @override
  Color get onPrimary => AppPalette.primary950;

  @override
  Color get primaryText => AppPalette.primary400;

  @override
  Color get tint => const Color(0xFF0F2A21);

  @override
  Color get tint2 => const Color(0xFF15503C);

  @override
  Color get background => const Color(0xFF0B1210);

  @override
  Color get surface => const Color(0xFF141D19);

  @override
  Color get textPrimary => const Color(0xFFE8EFEB);

  @override
  Color get textSecondary => const Color(0xFFA3B1A9);

  @override
  Color get textTertiary => const Color(0xFF76857D);

  @override
  Color get textDisabled => const Color(0xFF3A4741);

  @override
  Color get border => const Color(0xFF24302B);

  @override
  Color get divider => const Color(0xFF1C2622);

  @override
  Color get scrim => const Color(0x99000000);

  @override
  Color get success => AppPalette.primary500;

  @override
  Color get danger => const Color(0xFFF87171);

  // Not defined in the design system — derived for dark mode.
  @override
  Color get dangerSoft => const Color(0xFF2A1616);

  @override
  Color get onDanger => const Color(0xFFFFFFFF);

  @override
  Color get warning => const Color(0xFFF59E0B);

  @override
  Color get warningText => const Color(0xFFFBBF24);

  @override
  Color get warningSoft => const Color(0xFF2B2110);

  @override
  Color get info => const Color(0xFF60A5FA);
}
