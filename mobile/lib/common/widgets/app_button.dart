import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/cupertino.dart';

import 'app_pressable.dart';

enum AppButtonVariant {
  primary,
  secondary,
  outline,
  destructive,
  destructiveSolid,
  dark,
}

enum AppButtonSize {
  /// 56px — main screen CTA.
  large,

  /// 52px — default.
  medium,

  /// 44px, radius 14 — buttons inside empty states.
  small,

  /// 36px pill.
  pill,
}

/// Finora button (docs/DESIGN_SYSTEM.md §6.1).
///
/// One [AppButtonVariant.primary] per screen; everything else secondary/outline.
class AppButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final AppButtonVariant variant;
  final AppButtonSize size;
  final IconData? icon;
  final bool isLoading;
  final bool expanded;

  /// Looks disabled but still receives taps (e.g. to show validation errors).
  final bool muted;

  const AppButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.variant = AppButtonVariant.primary,
    this.size = AppButtonSize.medium,
    this.icon,
    this.isLoading = false,
    this.expanded = true,
    this.muted = false,
  });

  const AppButton.secondary({
    super.key,
    required this.text,
    required this.onPressed,
    this.size = AppButtonSize.medium,
    this.icon,
    this.isLoading = false,
    this.expanded = true,
    this.muted = false,
  }) : variant = AppButtonVariant.secondary;

  const AppButton.outline({
    super.key,
    required this.text,
    required this.onPressed,
    this.size = AppButtonSize.medium,
    this.icon,
    this.isLoading = false,
    this.expanded = true,
    this.muted = false,
  }) : variant = AppButtonVariant.outline;

  const AppButton.destructive({
    super.key,
    required this.text,
    required this.onPressed,
    this.size = AppButtonSize.medium,
    this.icon,
    this.isLoading = false,
    this.expanded = true,
    this.muted = false,
  }) : variant = AppButtonVariant.destructive;

  const AppButton.pill({
    super.key,
    required this.text,
    required this.onPressed,
    this.variant = AppButtonVariant.primary,
    this.icon,
    this.isLoading = false,
    this.muted = false,
  }) : size = AppButtonSize.pill,
       expanded = false;

  bool get _disabled => onPressed == null;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    final (bg, fg) = _disabled || muted
        ? (c.divider, c.textTertiary)
        : switch (variant) {
            .primary => (c.primary, c.onPrimary),
            .secondary => (c.tint, c.primaryText),
            .outline => (c.surface, c.textPrimary),
            .destructive => (c.dangerSoft, c.danger),
            .destructiveSolid => (c.danger, c.onDanger),
            .dark => (c.textPrimary, c.surface),
          };

    final height = switch (size) {
      .large => AppSizes.buttonLarge,
      .medium => AppSizes.button,
      .small => 44.0,
      .pill => AppSizes.buttonPill,
    };
    final isPill = size == .pill;
    final textStyle = AppTypography.button.copyWith(
      color: fg,
      fontSize: isPill ? 14 : 16,
    );

    final content = isLoading
        ? CupertinoActivityIndicator(color: fg)
        : Row(
            mainAxisSize: .min,
            mainAxisAlignment: .center,
            spacing: isPill ? 6 : 8,
            children: [
              if (icon != null)
                Icon(
                  icon,
                  size: isPill ? AppSizes.iconSm : AppSizes.iconMd,
                  color: fg,
                ),
              Flexible(
                child: Text(
                  text,
                  style: textStyle,
                  maxLines: 1,
                  overflow: .ellipsis,
                ),
              ),
            ],
          );

    final button = AnimatedContainer(
      duration: AppMotion.fast,
      height: height,
      width: expanded ? double.infinity : null,
      constraints: const BoxConstraints(minWidth: AppSizes.minTap),
      padding: .symmetric(
        horizontal: isPill || size == .small ? AppSpacing.lg : AppSpacing.x2l,
      ),
      alignment: .center,
      decoration: BoxDecoration(
        color: bg,
        borderRadius: .circular(
          isPill
              ? AppRadius.full
              : size == .small
              ? AppRadius.md
              : AppRadius.lg,
        ),
        border: variant == .outline && !_disabled && !muted
            ? Border.all(color: c.border)
            : null,
      ),
      child: content,
    );

    return AppPressable(
      onTap: _disabled || isLoading ? null : onPressed,
      // A non-expanded button hugs its content even in a stretching parent.
      child: expanded ? button : IntrinsicWidth(child: button),
    );
  }
}

/// 44×44 round icon button: `surface` + border (§6.1).
class AppIconButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback? onPressed;
  final String semanticLabel;
  final double size;
  final double iconSize;
  final Color? background;
  final Color? foreground;
  final bool bordered;

  const AppIconButton({
    super.key,
    required this.icon,
    required this.onPressed,
    required this.semanticLabel,
    this.size = AppSizes.minTap,
    this.iconSize = AppSizes.iconMd,
    this.background,
    this.foreground,
    this.bordered = true,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return AppPressable(
      onTap: onPressed,
      semanticLabel: semanticLabel,
      child: Container(
        width: size,
        height: size,
        alignment: .center,
        decoration: BoxDecoration(
          color: background ?? c.surface,
          shape: BoxShape.circle,
          border: bordered ? Border.all(color: c.border) : null,
        ),
        child: Icon(
          icon,
          size: iconSize,
          color: onPressed == null
              ? c.textDisabled
              : foreground ?? c.textPrimary,
        ),
      ),
    );
  }
}
