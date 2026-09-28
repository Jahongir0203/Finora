import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';

import 'core/functions.dart';

abstract final class AppTheme {
  static ThemeData theme(Brightness brightness) {
    final c = AppColors.withBrightness(brightness);
    final styles = AppTextStyles(c);
    final isDark = brightness == .dark;

    return ThemeData(
      useMaterial3: true,
      brightness: brightness,
      fontFamily: GoogleFonts.onest().fontFamily,
      textTheme: _textTheme(c),
      scaffoldBackgroundColor: c.background,
      canvasColor: c.background,
      dividerColor: c.divider,
      hintColor: c.textTertiary,
      disabledColor: c.textDisabled,
      splashFactory: NoSplash.splashFactory,
      highlightColor: Colors.transparent,
      colorScheme: ColorScheme(
        brightness: brightness,
        primary: c.primary,
        onPrimary: c.onPrimary,
        primaryContainer: c.tint,
        onPrimaryContainer: c.primaryText,
        secondary: c.primaryText,
        onSecondary: c.surface,
        error: c.danger,
        onError: c.onDanger,
        errorContainer: c.dangerSoft,
        onErrorContainer: c.danger,
        surface: c.surface,
        onSurface: c.textPrimary,
        onSurfaceVariant: c.textSecondary,
        surfaceContainerHighest: c.background,
        outline: c.border,
        outlineVariant: c.divider,
        scrim: c.scrim,
        shadow: const Color(0x1406140E),
      ),
      appBarTheme: AppBarTheme(
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: false,
        backgroundColor: c.background,
        surfaceTintColor: Colors.transparent,
        foregroundColor: c.textPrimary,
        iconTheme: IconThemeData(color: c.textPrimary, size: AppSizes.iconLg),
        titleTextStyle: styles.titleSmall,
        systemOverlayStyle: isDark
            ? SystemUiOverlayStyle.light
            : SystemUiOverlayStyle.dark,
      ),
      iconTheme: IconThemeData(color: c.textPrimary, size: AppSizes.iconLg),
      filledButtonTheme: FilledButtonThemeData(
        style: _buttonStyle(bg: c.primary, fg: c.onPrimary, c: c),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: _buttonStyle(bg: c.primary, fg: c.onPrimary, c: c),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: _buttonStyle(
          bg: c.surface,
          fg: c.textPrimary,
          c: c,
        ).copyWith(side: WidgetStatePropertyAll(BorderSide(color: c.border))),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: c.primaryText,
          textStyle: AppTypography.button,
          minimumSize: const Size(AppSizes.minTap, AppSizes.minTap),
          shape: RoundedRectangleBorder(borderRadius: .circular(AppRadius.lg)),
        ),
      ),
      floatingActionButtonTheme: FloatingActionButtonThemeData(
        backgroundColor: c.primary,
        foregroundColor: c.onPrimary,
        elevation: 0,
        highlightElevation: 0,
        shape: const CircleBorder(),
      ),
      inputDecorationTheme: _inputDecorationTheme(c),
      textSelectionTheme: TextSelectionThemeData(
        cursorColor: c.primary,
        selectionColor: c.primary.withValues(alpha: 0.25),
        selectionHandleColor: c.primary,
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        margin: .zero,
        color: c.surface,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: .circular(AppRadius.xl),
          side: BorderSide(color: c.border),
        ),
      ),
      dividerTheme: DividerThemeData(color: c.divider, thickness: 1, space: 1),
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: c.surface,
        surfaceTintColor: Colors.transparent,
        modalBarrierColor: c.scrim,
        elevation: 0,
        showDragHandle: false,
        shape: const RoundedRectangleBorder(
          borderRadius: .vertical(top: .circular(AppRadius.sheet)),
        ),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: c.surface,
        surfaceTintColor: Colors.transparent,
        barrierColor: c.scrim,
        titleTextStyle: styles.title,
        contentTextStyle: styles.bodySecondary,
        shape: RoundedRectangleBorder(borderRadius: .circular(AppRadius.x2l)),
      ),
      switchTheme: SwitchThemeData(
        thumbColor: const WidgetStatePropertyAll(Colors.white),
        trackColor: WidgetStateProperty.resolveWith(
          (s) => s.contains(WidgetState.selected) ? c.primary : c.border,
        ),
        trackOutlineColor: const WidgetStatePropertyAll(Colors.transparent),
      ),
      progressIndicatorTheme: ProgressIndicatorThemeData(
        color: c.primary,
        linearTrackColor: c.divider,
        circularTrackColor: c.divider,
      ),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: c.textPrimary,
        contentTextStyle: AppTypography.bodyMedium.copyWith(
          fontSize: 14,
          color: c.surface,
        ),
        behavior: SnackBarBehavior.floating,
        elevation: 0,
        shape: const StadiumBorder(),
      ),
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: c.surface,
        elevation: 0,
        type: BottomNavigationBarType.fixed,
        selectedItemColor: c.primaryText,
        unselectedItemColor: c.textTertiary,
        selectedLabelStyle: AppTypography.tabLabel,
        unselectedLabelStyle: AppTypography.tabLabel,
      ),
    );
  }

  static ButtonStyle _buttonStyle({
    required Color bg,
    required Color fg,
    required AppColorSchema c,
  }) {
    return ButtonStyle(
      elevation: const WidgetStatePropertyAll(0),
      minimumSize: const WidgetStatePropertyAll(
        Size(AppSizes.minTap, AppSizes.button),
      ),
      padding: const WidgetStatePropertyAll(
        .symmetric(horizontal: AppSpacing.x2l),
      ),
      textStyle: WidgetStatePropertyAll(AppTypography.button),
      shape: const WidgetStatePropertyAll(
        RoundedRectangleBorder(borderRadius: .all(.circular(AppRadius.lg))),
      ),
      backgroundColor: WidgetStateProperty.resolveWith(
        (s) => s.contains(WidgetState.disabled) ? c.divider : bg,
      ),
      foregroundColor: WidgetStateProperty.resolveWith(
        (s) => s.contains(WidgetState.disabled) ? c.textTertiary : fg,
      ),
      overlayColor: const WidgetStatePropertyAll(Colors.transparent),
    );
  }

  static InputDecorationTheme _inputDecorationTheme(AppColorSchema c) {
    OutlineInputBorder border(Color color, [double width = 1]) =>
        OutlineInputBorder(
          borderRadius: .circular(AppRadius.md),
          borderSide: BorderSide(color: color, width: width),
        );

    return InputDecorationTheme(
      filled: true,
      fillColor: c.surface,
      isDense: true,
      contentPadding: const .symmetric(horizontal: 16, vertical: 14),
      hintStyle: AppTypography.body.copyWith(color: c.textTertiary),
      labelStyle: AppTypography.body.copyWith(color: c.textSecondary),
      errorStyle: AppTypography.caption.copyWith(color: c.danger),
      prefixIconColor: c.textTertiary,
      suffixIconColor: c.textTertiary,
      border: border(c.border),
      enabledBorder: border(c.border),
      disabledBorder: border(c.divider),
      focusedBorder: border(c.primary, AppSizes.borderThick),
      errorBorder: border(c.danger, AppSizes.borderThick),
      focusedErrorBorder: border(c.danger, AppSizes.borderThick),
    );
  }

  static TextTheme _textTheme(AppColorSchema c) {
    final s = AppTextStyles(c);
    return TextTheme(
      displayLarge: s.displayLarge,
      displayMedium: s.display,
      headlineMedium: s.headline,
      titleLarge: s.title,
      titleMedium: s.titleSmall,
      // for TextField
      bodyLarge: s.body,
      // for Text
      bodyMedium: s.body,
      bodySmall: s.caption,
      labelLarge: s.button,
      labelMedium: s.label,
      labelSmall: s.tabLabel,
    );
  }
}
