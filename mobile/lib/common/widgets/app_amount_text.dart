import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

/// Money text: tabular digits + `UZS` at ~50% size, Medium, secondary color
/// (docs/DESIGN_SYSTEM.md §3, §11).
///
/// ```dart
/// AppAmountText(24850000, style: context.textStyles.displayLarge)
/// AppAmountText(-186400, sign: true, showCurrency: false)
/// ```
class AppAmountText extends StatelessWidget {
  final num value;
  final TextStyle? style;

  /// Adds `+` for positive values. Negative values always get `−`.
  final bool sign;
  final bool showCurrency;

  /// Replaces digits with `•••••••`.
  final bool hidden;
  final Color? color;
  final Color? currencyColor;

  const AppAmountText(
    this.value, {
    super.key,
    this.style,
    this.sign = false,
    this.showCurrency = true,
    this.hidden = false,
    this.color,
    this.currencyColor,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final base = (style ?? context.textStyles.amount).copyWith(
      color: color,
      fontFeatures: const [FontFeature.tabularFigures()],
    );
    final fontSize = base.fontSize ?? 15;

    final text = hidden ? AppFormat.hiddenBalance : value.toMoney(sign: sign);

    return Text.rich(
      TextSpan(
        text: text,
        style: base,
        children: [
          if (showCurrency && !hidden)
            TextSpan(
              text: ' ${AppFormat.currency}',
              style: base.copyWith(
                fontSize: (fontSize * 0.5).clamp(11, double.infinity),
                fontWeight: .w500,
                letterSpacing: 0,
                color: currencyColor ?? c.textSecondary,
              ),
            ),
        ],
      ),
      maxLines: 1,
      overflow: .ellipsis,
      semanticsLabel: hidden ? 'Balance hidden' : null,
    );
  }
}
