import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

import 'app_pressable.dart';
import 'app_card.dart';
import 'app_float.dart';

/// Full-screen empty / error state (docs/DESIGN_SYSTEM.md §8).
///
/// ```dart
/// AppEmptyState(
///   icon: FinoraIcons.empty,
///   title: 'No transactions yet',
///   message: 'Add your first expense or scan a receipt.',
///   action: AppButton(text: 'Add transaction', onPressed: ...),
/// )
/// ```
class AppEmptyState extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? message;
  final Widget? action;
  final Widget? secondaryAction;
  final bool isError;

  /// 120px circle / 68px square / 20 title (Notifications, Home cards).
  final bool large;

  const AppEmptyState({
    super.key,
    required this.icon,
    required this.title,
    this.message,
    this.action,
    this.secondaryAction,
    this.isError = false,
    this.large = false,
  });

  const AppEmptyState.error({
    super.key,
    this.icon = FinoraIcons.serverError,
    this.title = 'Something went wrong',
    this.message,
    this.action,
    this.secondaryAction,
  }) : isError = true,
       large = false;

  const AppEmptyState.offline({
    super.key,
    this.icon = FinoraIcons.offline,
    this.title = "You're offline",
    this.message = 'Check your connection and try again.',
    this.action,
    this.secondaryAction,
  }) : isError = true,
       large = false;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final styles = context.textStyles;

    final outer = isError ? c.dangerSoft : c.tint;
    final inner = isError ? c.danger : AppPalette.primary500;
    final iconColor = isError ? c.onDanger : AppPalette.primary950;

    return Center(
      child: SingleChildScrollView(
        padding: const .symmetric(
          horizontal: AppSpacing.x2l,
          vertical: AppSpacing.x3l,
        ),
        child: Column(
          mainAxisSize: .min,
          children: [
            _Pop(
              child: Container(
                width: large ? 120 : 96,
                height: large ? 120 : 96,
                alignment: .center,
                decoration: BoxDecoration(color: outer, shape: BoxShape.circle),
                child: AppFloat(
                  distance: 6,
                  period: const Duration(milliseconds: 3500),
                  child: Container(
                    width: large ? 68 : 60,
                    height: large ? 68 : 60,
                    alignment: .center,
                    decoration: BoxDecoration(
                      color: inner,
                      borderRadius: .circular(large ? 22 : AppRadius.xl),
                    ),
                    child: Icon(icon, size: large ? 30 : 28, color: iconColor),
                  ),
                ),
              ),
            ),
            const SizedBox(height: AppSpacing.lg),
            Text(
              title,
              textAlign: .center,
              style: styles.titleSmall.copyWith(
                fontSize: large ? 20 : 18,
                fontWeight: .w700,
              ),
            ),
            if (message != null) ...[
              const SizedBox(height: AppSpacing.sm),
              ConstrainedBox(
                constraints: BoxConstraints(maxWidth: large ? 280 : 260),
                child: Text(
                  message!,
                  textAlign: .center,
                  style: styles.bodySecondary.copyWith(
                    fontSize: large ? 15 : 14,
                    height: large ? 22 / 15 : 20 / 14,
                  ),
                ),
              ),
            ],
            if (action != null) ...[
              const SizedBox(height: AppSpacing.lg),
              action!,
            ],
            if (secondaryAction != null) ...[
              const SizedBox(height: AppSpacing.sm),
              secondaryAction!,
            ],
          ],
        ),
      ),
    );
  }
}

/// Inline empty card with dashed border (docs/screens/BUDGETS_GOALS.md §1.3).
class AppEmptyCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? message;
  final String? actionText;
  final VoidCallback? onAction;

  const AppEmptyCard({
    super.key,
    required this.icon,
    required this.title,
    this.message,
    this.actionText,
    this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return AppCard.dashed(
      padding: const .symmetric(horizontal: 16, vertical: 22),
      child: Column(
        spacing: 10,
        children: [
          Container(
            width: 48,
            height: 48,
            alignment: .center,
            decoration: BoxDecoration(
              color: c.tint,
              borderRadius: .circular(15),
            ),
            child: Icon(
              icon,
              size: AppSizes.iconQuickAction,
              color: c.primaryText,
            ),
          ),
          Text(
            title,
            textAlign: .center,
            style: AppTypography.bodyMedium.copyWith(
              fontSize: 16,
              fontWeight: .w600,
              color: c.textPrimary,
            ),
          ),
          if (message != null)
            ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 260),
              child: Text(
                message!,
                textAlign: .center,
                style: AppTypography.body.copyWith(
                  fontSize: 14,
                  height: 20 / 14,
                  color: c.textSecondary,
                ),
              ),
            ),
          if (actionText != null)
            AppPressable(
              onTap: onAction,
              child: Container(
                height: 40,
                padding: const .symmetric(horizontal: AppSpacing.lg),
                decoration: BoxDecoration(
                  color: c.tint,
                  borderRadius: .circular(12),
                ),
                child: Row(
                  mainAxisSize: .min,
                  spacing: 6,
                  children: [
                    Icon(
                      FinoraIcons.add,
                      size: AppSizes.iconSm,
                      color: c.primaryText,
                    ),
                    Text(
                      actionText!,
                      style: AppTypography.button.copyWith(
                        fontSize: 14,
                        color: c.primaryText,
                      ),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}

/// `fnPop`: scale .6 → 1.06 → 1.
class _Pop extends StatelessWidget {
  final Widget child;

  const _Pop({required this.child});

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: AppMotion.pop,
      builder: (_, t, child) {
        final scale = t < 0.7
            ? 0.6 + (1.06 - 0.6) * Curves.easeOut.transform(t / 0.7)
            : 1.06 -
                  0.06 *
                      Curves.easeInOut.transform(
                        ((t - 0.7) / 0.3).clamp(0.0, 1.0),
                      );
        return Opacity(
          opacity: (t * 2).clamp(0, 1),
          child: Transform.scale(scale: scale, child: child),
        );
      },
      child: child,
    );
  }
}
