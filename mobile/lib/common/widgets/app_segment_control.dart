import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

/// Segmented control (docs/DESIGN_SYSTEM.md §6.4).
///
/// Week / Month / Year, Accounts / Cards / Loans, ...
/// [brand] = Home tabs variant (`primary500` active segment).
class AppSegmentControl extends StatelessWidget {
  final List<String> children;
  final int index;
  final ValueChanged<int>? onChanged;
  final bool brand;
  final double height;

  /// Track color; defaults to `background` (`border` in dark mode).
  final Color? trackColor;

  /// Label size (13 in sheets, 14 on screens).
  final double fontSize;

  const AppSegmentControl({
    super.key,
    required this.children,
    this.index = 0,
    this.onChanged,
    this.brand = false,
    this.height = 40,
    this.trackColor,
    this.fontSize = 14,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final activeBg = brand ? c.primary : c.surface;
    final activeFg = brand ? c.onPrimary : c.textPrimary;

    return Container(
      padding: const .all(AppSpacing.xs),
      decoration: BoxDecoration(
        color: trackColor ?? (context.isDark ? c.border : c.background),
        borderRadius: .circular(AppRadius.md),
      ),
      child: LayoutBuilder(
        builder: (context, constraints) {
          const gap = AppSpacing.xs;
          final count = children.length;
          final itemWidth = (constraints.maxWidth - gap * (count - 1)) / count;

          return SizedBox(
            height: height,
            child: Stack(
              children: [
                AnimatedPositioned(
                  duration: AppMotion.fast,
                  curve: AppMotion.ease,
                  left: index * (itemWidth + gap),
                  top: 0,
                  bottom: 0,
                  width: itemWidth,
                  child: DecoratedBox(
                    decoration: BoxDecoration(
                      color: activeBg,
                      borderRadius: .circular(AppRadius.sm),
                      boxShadow: brand ? null : AppShadows.segmentActive,
                    ),
                  ),
                ),
                Row(
                  spacing: gap,
                  children: [
                    for (var i = 0; i < count; i++)
                      Expanded(
                        child: Semantics(
                          button: true,
                          selected: i == index,
                          child: GestureDetector(
                            behavior: HitTestBehavior.opaque,
                            onTap: () => onChanged?.call(i),
                            child: Center(
                              child: AnimatedDefaultTextStyle(
                                duration: AppMotion.fast,
                                style: AppTypography.bodyMedium.copyWith(
                                  fontSize: fontSize,
                                  fontWeight: .w600,
                                  color: i == index
                                      ? activeFg
                                      : c.textSecondary,
                                ),
                                child: Text(
                                  children[i],
                                  maxLines: 1,
                                  overflow: .ellipsis,
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
