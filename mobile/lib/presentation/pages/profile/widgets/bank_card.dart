import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:flutter/material.dart';

/// 290×180 bank card (docs/screens/PROFILE_SETTINGS.md §4.1).
class BankCard extends StatelessWidget {
  final Account account;
  final String holder;

  const BankCard({super.key, required this.account, required this.holder});

  static String networkTitle(String network) =>
      '${network[0]}${network.substring(1).toLowerCase()}';

  @override
  Widget build(BuildContext context) {
    final a = account;
    const muted = Color(0xB8FFFFFF); // rgba(255,255,255,.72)

    return AnimatedOpacity(
      duration: AppMotion.fast,
      opacity: a.frozen ? 0.55 : 1,
      child: ClipRRect(
        borderRadius: .circular(AppRadius.x2l),
        child: Container(
          width: 290,
          height: 180,
          color: Color(a.color),
          child: Stack(
            children: [
              const Positioned(
                right: -60,
                top: -70,
                child: _Circle(size: 220, alpha: 0.07),
              ),
              const Positioned(
                right: 40,
                bottom: -100,
                child: _Circle(size: 160, alpha: 0.05),
              ),
              Padding(
                padding: const .all(20),
                child: Column(
                  crossAxisAlignment: .start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            a.bank,
                            style: AppTypography.body.copyWith(
                              fontWeight: .w600,
                              color: AppPalette.white,
                            ),
                          ),
                        ),
                        Container(
                          padding: const .symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: const Color(0x24FFFFFF),
                            borderRadius: .circular(8),
                          ),
                          child: Text(
                            a.network ?? '',
                            style: AppTypography.label.copyWith(
                              fontWeight: .w700,
                              letterSpacing: 0.96,
                              color: AppPalette.white,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const Spacer(),
                    Text(
                      a.frozen ? Words.frozen.str : Words.balance.str,
                      style: AppTypography.caption.copyWith(
                        fontSize: 12,
                        color: muted,
                      ),
                    ),
                    Text.rich(
                      TextSpan(
                        text: a.balance.toMoney(),
                        style: AppTypography.display.copyWith(
                          fontSize: 24,
                          height: 30 / 24,
                          letterSpacing: 0,
                          color: AppPalette.white,
                        ),
                        children: [
                          TextSpan(
                            text: ' ${AppFormat.currency}',
                            style: AppTypography.caption.copyWith(
                              fontWeight: .w500,
                              color: muted,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const Spacer(),
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            '•••• ${a.last4}',
                            style: AppTypography.bodyMedium.copyWith(
                              letterSpacing: 1.2,
                              color: AppPalette.white,
                            ),
                          ),
                        ),
                        Text(
                          a.expiry ?? '',
                          style: AppTypography.caption.copyWith(
                            color: AppPalette.white,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Circle extends StatelessWidget {
  final double size;
  final double alpha;

  const _Circle({required this.size, required this.alpha});

  @override
  Widget build(BuildContext context) => Container(
    width: size,
    height: size,
    decoration: BoxDecoration(
      color: Colors.white.withValues(alpha: alpha),
      shape: BoxShape.circle,
    ),
  );
}
