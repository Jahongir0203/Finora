import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

import 'app_button.dart';

/// Bottom sheet (docs/DESIGN_SYSTEM.md §6.10).
///
/// ```dart
/// AppBottomSheet.show(context, title: 'New goal', child: ...);
/// ```
abstract final class AppBottomSheet {
  static const maxHeight = 790.0;

  static Future<T?> show<T>(
    BuildContext context, {
    required Widget child,
    String? title,
    bool isDismissible = true,
    bool scrollable = true,
    Color? barrierColor,
  }) {
    return showModalBottomSheet<T>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      isDismissible: isDismissible,
      enableDrag: isDismissible,
      barrierColor: barrierColor ?? context.appColors.scrim,
      sheetAnimationStyle: const AnimationStyle(
        duration: AppMotion.sheet,
        reverseDuration: AppMotion.fade,
        curve: AppMotion.easeSheet,
      ),
      constraints: const BoxConstraints(maxHeight: maxHeight),
      builder: (_) =>
          AppSheetBody(title: title, scrollable: scrollable, child: child),
    );
  }
}

/// Handle + optional title row + content, with keyboard inset.
class AppSheetBody extends StatelessWidget {
  final String? title;
  final Widget child;
  final bool scrollable;

  const AppSheetBody({
    super.key,
    required this.child,
    this.title,
    this.scrollable = true,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final bottomInset = MediaQuery.viewInsetsOf(context).bottom;

    final content = Padding(
      padding: .fromLTRB(
        AppSpacing.xl,
        0,
        AppSpacing.xl,
        (bottomInset > 0 ? bottomInset + AppSpacing.lg : 34),
      ),
      child: child,
    );

    return Column(
      mainAxisSize: .min,
      crossAxisAlignment: .stretch,
      children: [
        const SizedBox(height: 10),
        Center(
          child: Container(
            width: 40,
            height: 5,
            decoration: BoxDecoration(
              color: c.border,
              borderRadius: .circular(AppRadius.full),
            ),
          ),
        ),
        if (title != null)
          Padding(
            padding: const .fromLTRB(
              AppSpacing.xl,
              14,
              AppSpacing.xl,
              AppSpacing.lg,
            ),
            child: Row(
              children: [
                Expanded(child: Text(title!, style: context.textStyles.title)),
                AppIconButton(
                  icon: FinoraIcons.close,
                  semanticLabel: 'Close',
                  size: 40,
                  iconSize: AppSizes.iconTrailing,
                  bordered: false,
                  background: c.background,
                  onPressed: () => Navigator.of(context).maybePop(),
                ),
              ],
            ),
          )
        else
          const SizedBox(height: AppSpacing.lg),
        if (scrollable)
          Flexible(child: SingleChildScrollView(child: content))
        else
          content,
      ],
    );
  }
}
