import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

/// 6 OTP boxes (docs/AUTH_SCREENS.md §5).
///
/// Border: empty `border` · current `primary` · filled `textPrimary` ·
/// error `danger`.
class OtpBoxes extends StatelessWidget {
  final String code;
  final int length;
  final bool hasError;
  final bool showCursor;

  const OtpBoxes({
    super.key,
    required this.code,
    this.length = 6,
    this.hasError = false,
    this.showCursor = true,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Semantics(
      label: '${code.length} / $length',
      child: Row(
        spacing: AppSpacing.sm,
        children: [
          for (var i = 0; i < length; i++)
            Expanded(
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 150),
                height: 58,
                alignment: .center,
                decoration: BoxDecoration(
                  color: c.surface,
                  borderRadius: .circular(AppRadius.md),
                  border: Border.all(
                    width: AppSizes.borderThick,
                    color: hasError
                        ? c.danger
                        : i < code.length
                        ? c.textPrimary
                        : i == code.length && showCursor
                        ? c.primary
                        : c.border,
                  ),
                ),
                child: AnimatedSwitcher(
                  duration: const Duration(milliseconds: 150),
                  transitionBuilder: (child, animation) => ScaleTransition(
                    scale: Tween(begin: 0.6, end: 1.0).animate(animation),
                    child: FadeTransition(opacity: animation, child: child),
                  ),
                  child: Text(
                    i < code.length ? code[i] : '',
                    key: ValueKey('$i-${i < code.length ? code[i] : ''}'),
                    style: AppTypography.title.copyWith(
                      fontSize: 24,
                      height: 1,
                      color: hasError ? c.danger : c.textPrimary,
                      fontFeatures: const [FontFeature.tabularFigures()],
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
