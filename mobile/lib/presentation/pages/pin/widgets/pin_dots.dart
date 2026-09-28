import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

/// 4 PIN dots: empty ring → filled `primary500` (scale 1.15) → `danger`.
class PinDots extends StatelessWidget {
  final int filled;
  final int length;
  final bool error;

  const PinDots({
    super.key,
    required this.filled,
    this.length = 4,
    this.error = false,
  });

  @override
  Widget build(BuildContext context) {
    // PIN screens are always dark green, so use the light-mode danger.
    final danger = AppColors.light.danger;

    return Semantics(
      label: '$filled of $length',
      child: Row(
        mainAxisAlignment: .center,
        spacing: 18,
        children: [
          for (var i = 0; i < length; i++)
            AnimatedScale(
              scale: !error && i < filled ? 1.15 : 1,
              duration: const Duration(milliseconds: 180),
              curve: AppMotion.ease,
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 150),
                width: 16,
                height: 16,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: error
                      ? danger
                      : i < filled
                      ? AppPalette.primary500
                      : Colors.transparent,
                  border: Border.all(
                    width: 2,
                    color: error
                        ? danger
                        : i < filled
                        ? AppPalette.primary500
                        : AppPalette.pinDotBorder,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
