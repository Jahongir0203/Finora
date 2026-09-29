import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/words/words.dart';
import 'package:flutter/material.dart';

import '../main_tab.dart';

/// Tab bar with the center FAB (docs/screens/HOME_SCREENS.md §2).
class AppBottomNav extends StatelessWidget {
  final MainTab current;
  final ValueChanged<MainTab> onSelect;
  final VoidCallback onAdd;

  const AppBottomNav({
    super.key,
    required this.current,
    required this.onSelect,
    required this.onAdd,
  });

  static const _fabSize = 56.0;

  /// How far the FAB rises above the bar (−22 margin, 8 padding).
  static const _overhang = 14.0;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final bottom = MediaQuery.viewPaddingOf(context).bottom > 0 ? 28.0 : 12.0;

    Widget tab(MainTab t) => Expanded(
      child: _TabItem(tab: t, active: t == current, onTap: () => onSelect(t)),
    );

    return Stack(
      clipBehavior: Clip.none,
      children: [
        Padding(
          padding: const .only(top: _overhang),
          child: Container(
            padding: .fromLTRB(12, 8, 12, bottom),
            decoration: BoxDecoration(
              color: c.surface,
              border: Border(top: BorderSide(color: c.border)),
            ),
            child: Row(
              children: [
                tab(.home),
                tab(.activity),
                const SizedBox(width: 72),
                tab(.stats),
                tab(.budgets),
              ],
            ),
          ),
        ),
        Positioned(
          top: 0,
          left: 0,
          right: 0,
          child: Center(
            child: _Fab(size: _fabSize, onTap: onAdd),
          ),
        ),
      ],
    );
  }
}

class _TabItem extends StatelessWidget {
  final MainTab tab;
  final bool active;
  final VoidCallback onTap;

  const _TabItem({
    required this.tab,
    required this.active,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final color = active ? c.primaryText : c.textTertiary;

    return Semantics(
      selected: active,
      child: AppPressable(
        onTap: onTap,
        semanticLabel: tab.label.str,
        child: SizedBox(
          height: 52,
          child: Column(
            mainAxisAlignment: .center,
            children: [
              Icon(tab.icon, size: AppSizes.iconQuickAction, color: color),
              const SizedBox(height: 4),
              ExcludeSemantics(
                child: Text(
                  tab.label.str,
                  maxLines: 1,
                  overflow: .ellipsis,
                  style: AppTypography.tabLabel.copyWith(color: color),
                ),
              ),
              const SizedBox(height: 3),
              AnimatedContainer(
                duration: AppMotion.fade,
                curve: AppMotion.ease,
                width: active ? 18 : 0,
                height: 3,
                decoration: BoxDecoration(
                  color: AppPalette.primary500,
                  borderRadius: .circular(AppRadius.full),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// 56px `primary500` circle with `plus`; pops in on first build.
class _Fab extends StatelessWidget {
  final double size;
  final VoidCallback onTap;

  const _Fab({required this.size, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    final fab = AppPressable(
      onTap: onTap,
      semanticLabel: Words.newTransaction.str,
      child: Container(
        width: size,
        height: size,
        alignment: .center,
        decoration: const BoxDecoration(
          color: AppPalette.primary500,
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(
              color: Color(0x5910B981), // rgba(16,185,129,0.35)
              blurRadius: 20,
              offset: Offset(0, 8),
            ),
          ],
        ),
        child: Icon(FinoraIcons.add, size: 26, color: c.onPrimary),
      ),
    );

    if (MediaQuery.disableAnimationsOf(context)) return fab;

    // fnPop: scale .6 → 1.06 → 1, 600ms after a 150ms delay.
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: const Duration(milliseconds: 750),
      builder: (_, v, child) {
        final t = ((v * 750 - 150) / 600).clamp(0.0, 1.0);
        final scale = t < 0.7
            ? 0.6 + 0.46 * Curves.easeOut.transform(t / 0.7)
            : 1.06 -
                  0.06 *
                      Curves.easeInOut.transform(
                        ((t - 0.7) / 0.3).clamp(0.0, 1.0),
                      );
        return Opacity(
          opacity: (t * 2).clamp(0.0, 1.0),
          child: Transform.scale(scale: scale, child: child),
        );
      },
      child: fab,
    );
  }
}
