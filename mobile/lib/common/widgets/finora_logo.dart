import 'package:finora/common/theme/core/functions.dart';
import 'package:flutter/material.dart';

/// Brand mark: `wallet` icon on a `primary500` rounded square.
class FinoraLogo extends StatelessWidget {
  final double size;
  final bool glow;

  const FinoraLogo({super.key, this.size = 36, this.glow = false});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      alignment: .center,
      decoration: BoxDecoration(
        color: AppPalette.primary500,
        // 36 → 11, 92 → 28
        borderRadius: .circular(size * 0.305),
        boxShadow: glow
            ? const [
                BoxShadow(
                  color: Color(0x5910B981), // rgba(16,185,129,0.35)
                  blurRadius: 50,
                  offset: Offset(0, 20),
                ),
              ]
            : null,
      ),
      child: Icon(
        FinoraIcons.wallet,
        size: size / 2,
        color: AppPalette.primary950,
      ),
    );
  }
}
