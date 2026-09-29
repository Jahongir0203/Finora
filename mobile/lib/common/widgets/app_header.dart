import 'package:auto_route/auto_route.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/words/words.dart';
import 'package:flutter/material.dart';

import 'app_button.dart';
import 'app_pressable.dart';

/// Push screen header: 44px back · title 17/600 · optional trailing
/// (docs/screens/PROFILE_SETTINGS.md §1).
class PushHeader extends StatelessWidget {
  final String title;
  final Widget? trailing;
  final VoidCallback? onBack;

  /// 20/700 instead of 17/600 (Goal details).
  final bool large;

  const PushHeader({
    super.key,
    required this.title,
    this.trailing,
    this.onBack,
    this.large = false,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      spacing: AppSpacing.md,
      children: [
        AppIconButton(
          icon: FinoraIcons.back,
          semanticLabel: Words.back.str,
          onPressed: onBack ?? () => context.router.maybePop(),
        ),
        Expanded(
          child: Semantics(
            header: true,
            child: Text(
              title,
              maxLines: 1,
              overflow: .ellipsis,
              style: large
                  ? context.textStyles.title.copyWith(fontWeight: .w700)
                  : context.textStyles.titleSmall,
            ),
          ),
        ),
        ?trailing,
      ],
    );
  }
}

/// 44px `primary500` circle with `plus` (header "add" action).
class AppAddButton extends StatelessWidget {
  final VoidCallback onPressed;
  final String semanticLabel;

  const AppAddButton({
    super.key,
    required this.onPressed,
    required this.semanticLabel,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return AppPressable(
      onTap: onPressed,
      semanticLabel: semanticLabel,
      child: Container(
        width: AppSizes.minTap,
        height: AppSizes.minTap,
        alignment: .center,
        decoration: BoxDecoration(color: c.primary, shape: BoxShape.circle),
        child: Icon(
          FinoraIcons.add,
          size: AppSizes.iconQuickAction,
          color: c.onPrimary,
        ),
      ),
    );
  }
}

/// Tab screen title row: 24/700 + optional actions.
class TabHeader extends StatelessWidget {
  final String title;
  final List<Widget> actions;

  const TabHeader({super.key, required this.title, this.actions = const []});

  @override
  Widget build(BuildContext context) {
    return Row(
      spacing: AppSpacing.sm,
      children: [
        Expanded(
          child: Semantics(
            header: true,
            child: Text(title, style: context.textStyles.headline),
          ),
        ),
        ...actions,
      ],
    );
  }
}

/// 13/600 `textSecondary` label above a group ("Upcoming", "Include", ...).
class SectionLabel extends StatelessWidget {
  final String text;
  final EdgeInsetsGeometry padding;

  const SectionLabel(this.text, {super.key, this.padding = EdgeInsets.zero});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: padding,
      child: Text(
        text,
        style: AppTypography.caption.copyWith(
          fontWeight: .w600,
          color: context.appColors.textSecondary,
        ),
      ),
    );
  }
}

/// Sheet header: title 20/600 (+ subtitle) and a 40px close button (§6.10).
class SheetHeader extends StatelessWidget {
  final String title;
  final String? subtitle;
  final Widget? leading;

  const SheetHeader({
    super.key,
    required this.title,
    this.subtitle,
    this.leading,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Row(
      spacing: AppSpacing.md,
      children: [
        ?leading,
        Expanded(
          child: Column(
            crossAxisAlignment: .start,
            children: [
              Text(title, style: context.textStyles.title),
              if (subtitle != null)
                Text(
                  subtitle!,
                  style: AppTypography.caption.copyWith(color: c.textSecondary),
                ),
            ],
          ),
        ),
        AppIconButton(
          icon: FinoraIcons.close,
          semanticLabel: Words.close.str,
          size: 40,
          iconSize: AppSizes.iconTrailing,
          bordered: false,
          background: c.background,
          onPressed: () => Navigator.of(context).maybePop(),
        ),
      ],
    );
  }
}
