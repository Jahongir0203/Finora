import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

/// 44×24 toggle (docs/DESIGN_SYSTEM.md §6.5).
class AppSwitch extends StatelessWidget {
  final bool value;
  final ValueChanged<bool>? onChanged;
  final String? semanticLabel;

  /// 48×28 with a 22px knob (reminders, profile).
  final bool large;

  const AppSwitch({
    super.key,
    required this.value,
    required this.onChanged,
    this.semanticLabel,
    this.large = false,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Semantics(
      toggled: value,
      enabled: onChanged != null,
      label: semanticLabel,
      child: GestureDetector(
        onTap: onChanged == null ? null : () => onChanged!(!value),
        child: Opacity(
          opacity: onChanged == null ? 0.5 : 1,
          child: AnimatedContainer(
            duration: AppMotion.fast,
            curve: AppMotion.ease,
            width: large ? 48 : 44,
            height: large ? 28 : 24,
            padding: .all(large ? 3 : 2),
            alignment: value ? Alignment.centerRight : Alignment.centerLeft,
            decoration: BoxDecoration(
              color: value ? c.primary : c.border,
              borderRadius: .circular(AppRadius.full),
            ),
            child: Container(
              width: large ? 22 : 20,
              height: large ? 22 : 20,
              decoration: const BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
                boxShadow: AppShadows.toggleKnob,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
