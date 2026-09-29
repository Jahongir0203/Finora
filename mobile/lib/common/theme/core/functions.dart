import 'package:finora/presentation/routes/app_router.dart';
import 'package:flutter/material.dart';

import '../colors.dart';
import '../text_styles.dart';
import 'schemas.dart';

export '../colors.dart';
export '../dimens.dart';
export '../categories.dart';
export '../icons.dart';
export '../motion.dart';
export '../palette.dart';
export '../text_styles.dart';
export 'schemas.dart';

abstract final class AppColors {
  static const AppColorSchema light = LightColorScheme();
  static const AppColorSchema dark = DarkColorScheme();

  static AppColorSchema of(BuildContext context) =>
      Theme.of(context).brightness == .dark ? dark : light;

  static AppColorSchema withBrightness(Brightness brightness) =>
      brightness == .dark ? dark : light;

  static AppColorSchema withoutContext() {
    final context = router.navigatorKey.currentState!.context;
    return Theme.of(context).brightness == .dark ? dark : light;
  }
}

extension AppThemeExtension on BuildContext {
  AppColorSchema get appColors => AppColors.of(this);

  AppTextStyles get textStyles => AppTextStyles(AppColors.of(this));

  bool get isDark => Theme.of(this).brightness == .dark;
}
