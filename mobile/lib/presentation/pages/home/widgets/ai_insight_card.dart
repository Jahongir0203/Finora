import 'dart:math' as math;

import 'package:easy_localization/easy_localization.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_card.dart';
import 'package:finora/common/words/words.dart';
import 'package:flutter/material.dart';

/// "Finora AI · You could save … UZS this month" (§3.3).
class AiInsightCard extends StatelessWidget {
  final num amount;
  final VoidCallback onTap;

  const AiInsightCard({super.key, required this.amount, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return AppCard.tinted(
      onTap: onTap,
      child: Row(
        spacing: 14,
        children: [
          const _GlowingIcon(),
          Expanded(
            child: Column(
              crossAxisAlignment: .start,
              spacing: 2,
              children: [
                Text(
                  Words.finoraAi.str.toUpperCase(),
                  style: AppTypography.label.copyWith(color: c.primaryText),
                ),
                Text(
                  Words.aiCouldSave.tr(args: [amount.toMoney()]),
                  style: AppTypography.body.copyWith(
                    height: 20 / 15,
                    fontWeight: .w600,
                    color: c.textPrimary,
                  ),
                ),
              ],
            ),
          ),
          Icon(
            FinoraIcons.forward,
            size: AppSizes.iconTrailing,
            color: c.textTertiary,
          ),
        ],
      ),
    );
  }
}

/// 44×44 `primary500` tile with `sparkles`; `fnGlow` (0 → 7px, 2.4s ∞).
class _GlowingIcon extends StatefulWidget {
  const _GlowingIcon();

  @override
  State<_GlowingIcon> createState() => _GlowingIconState();
}

class _GlowingIconState extends State<_GlowingIcon>
    with SingleTickerProviderStateMixin {
  late final _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 2400),
  );

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (MediaQuery.disableAnimationsOf(context)) {
      _controller
        ..stop()
        ..value = 0;
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

    return AnimatedBuilder(
      animation: _controller,
      builder: (_, child) {
        final wave = math.sin(math.pi * _controller.value);
        return DecoratedBox(
          decoration: BoxDecoration(
            borderRadius: .circular(AppRadius.md),
            boxShadow: [
              BoxShadow(
                color: AppPalette.primary500.withValues(alpha: 0.35 * wave),
                blurRadius: 7 * wave,
                spreadRadius: 7 * wave / 2,
              ),
            ],
          ),
          child: child,
        );
      },
      child: Container(
        width: 44,
        height: 44,
        alignment: .center,
        decoration: BoxDecoration(
          color: c.primary,
          borderRadius: .circular(AppRadius.md),
        ),
        child: Icon(
          FinoraIcons.ai,
          size: AppSizes.iconQuickAction,
          color: c.onPrimary,
        ),
      ),
    );
  }
}
