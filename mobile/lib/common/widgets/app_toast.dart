import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/presentation/routes/app_router.dart';
import 'package:flutter/material.dart';

enum ToastType { success, error, warning, info }

/// Dark pill toast at the bottom center (docs/DESIGN_SYSTEM.md §6.11).
///
/// Shows one toast at a time; a new one replaces the current one.
abstract final class AppToast {
  static OverlayEntry? _current;

  static void show(
    String message, {
    ToastType type = ToastType.info,
    Duration duration = AppMotion.toastVisible,
  }) {
    final overlay = router.navigatorKey.currentState?.overlay;
    if (overlay == null) return;

    _current?.remove();
    late final OverlayEntry entry;
    entry = OverlayEntry(
      builder: (_) => _Toast(
        message: message,
        type: type,
        duration: duration,
        onDone: () {
          // A replaced entry was already removed by the next show().
          if (_current != entry) return;
          _current = null;
          entry.remove();
        },
      ),
    );
    _current = entry;
    overlay.insert(entry);
  }

  static void success(
    String message, {
    Duration duration = AppMotion.toastVisible,
  }) => show(message, type: ToastType.success, duration: duration);

  static void error(
    String message, {
    Duration duration = const Duration(seconds: 4),
  }) => show(message, type: ToastType.error, duration: duration);

  static void warning(
    String message, {
    Duration duration = AppMotion.toastVisible,
  }) => show(message, type: ToastType.warning, duration: duration);

  static void info(
    String message, {
    Duration duration = AppMotion.toastVisible,
  }) => show(message, type: ToastType.info, duration: duration);
}

class _Toast extends StatefulWidget {
  final String message;
  final ToastType type;
  final Duration duration;
  final VoidCallback onDone;

  const _Toast({
    required this.message,
    required this.type,
    required this.duration,
    required this.onDone,
  });

  @override
  State<_Toast> createState() => _ToastState();
}

class _ToastState extends State<_Toast> with SingleTickerProviderStateMixin {
  late final _controller = AnimationController(
    vsync: this,
    duration: AppMotion.fade,
  );
  late final _curve = CurvedAnimation(
    parent: _controller,
    curve: AppMotion.ease,
  );

  @override
  void initState() {
    super.initState();
    _controller.forward();
    Future.delayed(widget.duration, () async {
      if (!mounted) return;
      await _controller.reverse();
      widget.onDone();
    });
  }

  @override
  void dispose() {
    _curve.dispose();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    final (icon, iconColor) = switch (widget.type) {
      .success => (FinoraIcons.empty, AppPalette.primary400),
      .error => (FinoraIcons.alert, const Color(0xFFF87171)),
      .warning => (FinoraIcons.warning, c.warning),
      .info => (null, null),
    };

    return Positioned(
      left: AppSpacing.xl,
      right: AppSpacing.xl,
      bottom: MediaQuery.paddingOf(context).bottom + 96,
      child: IgnorePointer(
        child: Center(
          child: FadeTransition(
            opacity: _curve,
            child: AnimatedBuilder(
              animation: _curve,
              builder: (_, child) => Transform.translate(
                offset: Offset(0, 18 * (1 - _curve.value)),
                child: Transform.scale(
                  scale: 0.94 + 0.06 * _curve.value,
                  child: child,
                ),
              ),
              child: Semantics(
                liveRegion: true,
                child: Container(
                  padding: const .symmetric(horizontal: 18, vertical: 12),
                  decoration: BoxDecoration(
                    color: c.textPrimary,
                    borderRadius: .circular(AppRadius.full),
                    boxShadow: AppShadows.toast,
                  ),
                  child: Row(
                    mainAxisSize: .min,
                    spacing: AppSpacing.sm,
                    children: [
                      if (icon != null)
                        Icon(icon, size: AppSizes.iconSm, color: iconColor),
                      Flexible(
                        child: Text(
                          widget.message,
                          textAlign: .center,
                          style: AppTypography.bodyMedium.copyWith(
                            fontSize: 14,
                            height: 20 / 14,
                            color: c.surface,
                            decoration: TextDecoration.none,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
