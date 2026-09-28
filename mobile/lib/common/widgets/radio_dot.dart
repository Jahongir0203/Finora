import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

/// 22px radio: 2px ring, 10px dot that scales in (PROFILE_SETTINGS.md §1).
class RadioDot extends StatelessWidget {
  final bool selected;

  const RadioDot({super.key, required this.selected});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return AnimatedContainer(
      duration: AppMotion.fast,
      width: 22,
      height: 22,
      alignment: .center,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(
          color: selected ? AppPalette.primary500 : c.textDisabled,
          width: 2,
        ),
      ),
      child: AnimatedScale(
        scale: selected ? 1 : 0,
        duration: AppMotion.fast,
        curve: AppMotion.ease,
        child: Container(
          width: 10,
          height: 10,
          decoration: const BoxDecoration(
            color: AppPalette.primary500,
            shape: BoxShape.circle,
          ),
        ),
      ),
    );
  }
}
