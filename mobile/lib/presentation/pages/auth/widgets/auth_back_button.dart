import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/words/words.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// 44×44 round back button on `background` fill.
class AuthBackButton extends StatelessWidget {
  final VoidCallback onPressed;

  const AuthBackButton({super.key, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Align(
      alignment: AlignmentDirectional.centerStart,
      child: AppIconButton(
        icon: FinoraIcons.back,
        semanticLabel: Words.back.str,
        bordered: false,
        background: c.background,
        foreground: c.textPrimary,
        onPressed: onPressed,
      ),
    );
  }
}

/// Title (28/34 Bold) + description (15/22 secondary), gap 8.
class AuthTitle extends StatelessWidget {
  final String title;
  final Widget subtitle;

  const AuthTitle({super.key, required this.title, required this.subtitle});

  @override
  Widget build(BuildContext context) {
    final styles = context.textStyles;

    return Column(
      crossAxisAlignment: .start,
      spacing: AppSpacing.sm,
      children: [
        Text(
          title,
          style: styles.headline.copyWith(
            fontSize: 28,
            height: 34 / 28,
            letterSpacing: -0.56,
          ),
        ),
        DefaultTextStyle.merge(style: styles.bodySecondary, child: subtitle),
      ],
    );
  }
}

/// Status bar for white auth screens (dark icons; light in dark mode).
SystemUiOverlayStyle authOverlayStyle(BuildContext context) {
  final c = context.appColors;
  return (context.isDark
          ? SystemUiOverlayStyle.light
          : SystemUiOverlayStyle.dark)
      .copyWith(
        statusBarColor: Colors.transparent,
        systemNavigationBarColor: c.surface,
      );
}

/// Status bar for `primary900` screens (splash, onboarding).
const darkGreenOverlayStyle = SystemUiOverlayStyle(
  statusBarColor: Colors.transparent,
  statusBarIconBrightness: Brightness.light,
  statusBarBrightness: Brightness.dark,
  systemNavigationBarColor: AppPalette.primary900,
  systemNavigationBarIconBrightness: Brightness.light,
);
