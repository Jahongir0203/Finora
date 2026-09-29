import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

/// Offline banner (docs/DESIGN_SYSTEM.md §6.16).
class AppOfflineBanner extends StatelessWidget {
  final String message;
  final VoidCallback? onRetry;

  const AppOfflineBanner({
    super.key,
    this.message = "You're offline",
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final style = AppTypography.bodyMedium.copyWith(
      fontSize: 14,
      color: c.warningText,
    );

    return Container(
      padding: const .symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: c.warningSoft,
        borderRadius: .circular(AppRadius.md),
      ),
      child: Row(
        spacing: AppSpacing.sm,
        children: [
          Icon(
            FinoraIcons.offline,
            size: AppSizes.iconSm,
            color: c.warningText,
          ),
          Expanded(child: Text(message, style: style)),
          if (onRetry != null)
            GestureDetector(
              onTap: onRetry,
              behavior: HitTestBehavior.opaque,
              child: Padding(
                padding: const .all(AppSpacing.xs),
                child: Text(
                  'Retry',
                  style: style.copyWith(
                    fontWeight: .w600,
                    decoration: TextDecoration.underline,
                    decorationColor: c.warningText,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

/// 8×8 pulsing unread dot with a 2px ring in [ringColor] (`fnPulse`).
class AppUnreadDot extends StatefulWidget {
  final Color? ringColor;

  /// Defaults to `primary500`.
  final Color? color;

  const AppUnreadDot({super.key, this.ringColor, this.color});

  @override
  State<AppUnreadDot> createState() => _AppUnreadDotState();
}

class _AppUnreadDotState extends State<AppUnreadDot>
    with SingleTickerProviderStateMixin {
  late final _controller = AnimationController(
    vsync: this,
    duration: const Duration(seconds: 2),
  );

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Infinite animations are off with reduced motion.
    if (MediaQuery.disableAnimationsOf(context)) {
      _controller.stop();
    } else if (!_controller.isAnimating) {
      _controller.repeat();
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return SizedBox.square(
      dimension: 12,
      child: AnimatedBuilder(
        animation: _controller,
        builder: (_, _) {
          final t = _controller.value;
          return Stack(
            alignment: .center,
            clipBehavior: Clip.none,
            children: [
              Container(
                width: 12 + 8 * t,
                height: 12 + 8 * t,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: AppPalette.primary400.withValues(alpha: 0.4 * (1 - t)),
                ),
              ),
              Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  color: widget.color ?? AppPalette.primary500,
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: widget.ringColor ?? c.surface,
                    width: 2,
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
