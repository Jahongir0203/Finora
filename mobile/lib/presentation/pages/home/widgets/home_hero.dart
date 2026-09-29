import 'dart:math' as math;

import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_avatar.dart';
import 'package:finora/common/widgets/app_banner.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/words/words.dart';
import 'package:flutter/material.dart';

/// Scroll-linked values for the hero and the collapsed bar (§3.2).
abstract final class HomeScrollFx {
  static double offset(ScrollController scroll) =>
      scroll.hasClients ? math.max(0, scroll.offset) : 0;

  /// CollapsedBar progress `p`.
  static double collapse(double y) => ((y - 120) / 60).clamp(0.0, 1.0);
}

/// Dark top block: greeting, balance, income / expenses (§3.1).
class HomeHero extends StatelessWidget {
  final ScrollController scroll;
  final String userName;
  final num balance;
  final num income;
  final num expenses;
  final bool balanceHidden;
  final bool needBalance;
  final bool hasUnread;
  final VoidCallback onToggleBalance;
  final VoidCallback onAddBalance;
  final VoidCallback onBell;
  final VoidCallback onAvatar;

  const HomeHero({
    super.key,
    required this.scroll,
    required this.userName,
    required this.balance,
    required this.income,
    required this.expenses,
    required this.balanceHidden,
    required this.needBalance,
    required this.hasUnread,
    required this.onToggleBalance,
    required this.onAddBalance,
    required this.onBell,
    required this.onAvatar,
  });

  static String greeting(DateTime now) {
    final h = now.hour;
    if (h >= 5 && h < 12) return Words.goodMorning.str;
    if (h >= 12 && h < 18) return Words.goodAfternoon.str;
    return Words.goodEvening.str;
  }

  @override
  Widget build(BuildContext context) {
    final top = MediaQuery.paddingOf(context).top;

    final header = Row(
      spacing: AppSpacing.md,
      children: [
        AppPressable(
          onTap: onAvatar,
          semanticLabel: Words.profile.str,
          child: AppAvatar(name: userName, onDark: true, fontSize: 15),
        ),
        Expanded(
          child: Column(
            crossAxisAlignment: .start,
            children: [
              Text(
                greeting(DateTime.now()),
                style: AppTypography.caption.copyWith(
                  color: AppPalette.primary200,
                ),
              ),
              Text(
                userName.split(' ').first,
                maxLines: 1,
                overflow: .ellipsis,
                style: AppTypography.titleSmall.copyWith(
                  color: AppPalette.white,
                ),
              ),
            ],
          ),
        ),
        _Bell(ringing: hasUnread, onTap: onBell),
      ],
    );

    final balanceBlock = Column(
      crossAxisAlignment: .start,
      spacing: AppSpacing.md,
      children: [
        Row(
          children: [
            Expanded(
              child: FittedBox(
                fit: BoxFit.scaleDown,
                alignment: AlignmentDirectional.centerStart,
                child: HeroAmount(
                  value: balance,
                  hidden: balanceHidden,
                  size: 34,
                  currencySize: 18,
                ),
              ),
            ),
            _HeroIconButton(
              icon: balanceHidden ? FinoraIcons.hide : FinoraIcons.show,
              semanticLabel: balanceHidden
                  ? Words.showBalance.str
                  : Words.hideBalance.str,
              onTap: onToggleBalance,
            ),
          ],
        ),
        AnimatedSize(
          duration: AppMotion.fade,
          curve: AppMotion.ease,
          alignment: AlignmentDirectional.topStart,
          child: needBalance
              ? HeroPill(text: Words.addCurrentBalance.str, onTap: onAddBalance)
              : const SizedBox(width: double.infinity),
        ),
      ],
    );

    final flows = Row(
      spacing: AppSpacing.sm,
      children: [
        Expanded(
          child: _FlowCard(
            icon: FinoraIcons.income,
            iconBackground: AppPalette.primary500,
            iconColor: AppPalette.primary950,
            label: Words.income.str,
            amount: '+${AppFormat.spaced(income)}',
          ),
        ),
        Expanded(
          child: _FlowCard(
            icon: FinoraIcons.expense,
            iconBackground: AppPalette.primary200,
            iconColor: AppPalette.primary900,
            label: Words.expenses.str,
            amount: '${AppFormat.minus}${AppFormat.spaced(expenses)}',
          ),
        ),
      ],
    );

    return DecoratedBox(
      decoration: const BoxDecoration(
        color: AppPalette.primary950,
        gradient: RadialGradient(
          center: Alignment.topRight,
          radius: 1.2,
          colors: [AppPalette.heroBlock, AppPalette.primary950],
          stops: [0, 0.6],
        ),
      ),
      child: CustomPaint(
        painter: const _DiagonalGridPainter(),
        child: Padding(
          padding: .fromLTRB(AppSpacing.xl, top + 8, AppSpacing.xl, 48),
          child: AnimatedBuilder(
            animation: scroll,
            builder: (_, _) {
              final y = HomeScrollFx.offset(scroll);
              final headerOpacity = math.max(0.0, 1 - y / 90);

              return Opacity(
                opacity: math.max(0.0, 1 - y / 240),
                child: Transform.translate(
                  offset: Offset(0, y * 0.35),
                  child: Transform.scale(
                    scale: 1 - y / 1400,
                    child: Column(
                      crossAxisAlignment: .stretch,
                      spacing: 26,
                      children: [
                        IgnorePointer(
                          ignoring: headerOpacity < 0.5,
                          child: Opacity(opacity: headerOpacity, child: header),
                        ),
                        balanceBlock,
                        flows,
                      ],
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}

/// Sticky bar that fades in once the hero has scrolled away (§3.2).
class HomeCollapsedBar extends StatelessWidget {
  final ScrollController scroll;
  final String userName;
  final num balance;
  final bool balanceHidden;
  final VoidCallback onAdd;
  final VoidCallback onAvatar;

  const HomeCollapsedBar({
    super.key,
    required this.scroll,
    required this.userName,
    required this.balance,
    required this.balanceHidden,
    required this.onAdd,
    required this.onAvatar,
  });

  @override
  Widget build(BuildContext context) {
    final top = MediaQuery.paddingOf(context).top;

    final bar = Container(
      color: AppPalette.primary950,
      padding: .only(top: top),
      child: SizedBox(
        height: 60,
        child: Padding(
          padding: AppSpacing.screenPadding,
          child: Row(
            spacing: AppSpacing.md,
            children: [
              AppPressable(
                onTap: onAvatar,
                semanticLabel: Words.profile.str,
                child: AppAvatar(
                  name: userName,
                  size: 34,
                  onDark: true,
                  fontSize: 12,
                ),
              ),
              Expanded(
                child: Column(
                  mainAxisAlignment: .center,
                  crossAxisAlignment: .start,
                  children: [
                    Text(
                      Words.totalBalance.str.toUpperCase(),
                      maxLines: 1,
                      style: AppTypography.label.copyWith(
                        fontSize: 11,
                        height: 14 / 11,
                        letterSpacing: 0.66,
                        color: AppPalette.primary200,
                      ),
                    ),
                    FittedBox(
                      fit: BoxFit.scaleDown,
                      alignment: AlignmentDirectional.centerStart,
                      child: HeroAmount(
                        value: balance,
                        hidden: balanceHidden,
                        size: 17,
                        currencySize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              HeroPill(text: Words.add.str, onTap: onAdd),
            ],
          ),
        ),
      ),
    );

    return AnimatedBuilder(
      animation: scroll,
      child: bar,
      builder: (_, child) {
        final p = HomeScrollFx.collapse(HomeScrollFx.offset(scroll));
        if (p == 0) return const SizedBox.shrink();

        return IgnorePointer(
          ignoring: p < 0.5,
          child: Opacity(
            opacity: p,
            child: Transform.translate(
              offset: Offset(0, (1 - p) * -10),
              child: child,
            ),
          ),
        );
      },
    );
  }
}

/// White tabular balance with a smaller `UZS` in `primary200`.
class HeroAmount extends StatelessWidget {
  final num value;
  final bool hidden;
  final double size;
  final double currencySize;

  const HeroAmount({
    super.key,
    required this.value,
    required this.hidden,
    required this.size,
    required this.currencySize,
  });

  @override
  Widget build(BuildContext context) {
    final style = AppTypography.display.copyWith(
      fontSize: size,
      height: 1.2,
      letterSpacing: size * -0.02,
      color: AppPalette.white,
    );

    return Text.rich(
      TextSpan(
        text: hidden ? AppFormat.hiddenBalance : value.toMoney(),
        style: style,
        children: [
          if (!hidden)
            TextSpan(
              text: ' ${AppFormat.currency}',
              style: style.copyWith(
                fontSize: currencySize,
                fontWeight: .w600,
                letterSpacing: 0,
                color: AppPalette.primary200,
              ),
            ),
        ],
      ),
      maxLines: 1,
      semanticsLabel: hidden ? 'Balance hidden' : null,
    );
  }
}

/// 36px `primary500` pill with `plus` (hero "Add your current balance",
/// collapsed bar "Add").
class HeroPill extends StatelessWidget {
  final String text;
  final VoidCallback onTap;

  const HeroPill({super.key, required this.text, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return AppPressable(
      onTap: onTap,
      child: Container(
        height: AppSizes.buttonPill,
        padding: const .only(left: 10, right: 14),
        decoration: BoxDecoration(
          color: c.primary,
          borderRadius: .circular(AppRadius.full),
        ),
        child: Row(
          mainAxisSize: .min,
          spacing: 6,
          children: [
            Icon(FinoraIcons.add, size: AppSizes.iconSm, color: c.onPrimary),
            Text(
              text,
              style: AppTypography.button.copyWith(
                fontSize: 14,
                height: 20 / 14,
                color: c.onPrimary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _HeroIconButton extends StatelessWidget {
  final IconData icon;
  final String semanticLabel;
  final VoidCallback onTap;

  const _HeroIconButton({
    required this.icon,
    required this.semanticLabel,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return AppPressable(
      onTap: onTap,
      semanticLabel: semanticLabel,
      child: SizedBox.square(
        dimension: AppSizes.minTap,
        child: Icon(icon, size: AppSizes.iconQuickAction, color: Colors.white),
      ),
    );
  }
}

class _FlowCard extends StatelessWidget {
  final IconData icon;
  final Color iconBackground;
  final Color iconColor;
  final String label;
  final String amount;

  const _FlowCard({
    required this.icon,
    required this.iconBackground,
    required this.iconColor,
    required this.label,
    required this.amount,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const .all(10),
      decoration: BoxDecoration(
        color: AppPalette.heroBlockAlt,
        borderRadius: .circular(AppRadius.lg),
      ),
      child: Row(
        spacing: AppSpacing.sm,
        children: [
          Container(
            width: 28,
            height: 28,
            alignment: .center,
            decoration: BoxDecoration(
              color: iconBackground,
              borderRadius: .circular(9),
            ),
            child: Icon(icon, size: AppSizes.iconSm, color: iconColor),
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: .start,
              children: [
                Text(
                  label,
                  maxLines: 1,
                  overflow: .ellipsis,
                  style: AppTypography.caption.copyWith(
                    fontSize: 12,
                    height: 16 / 12,
                    color: AppPalette.primary200,
                  ),
                ),
                Text(
                  amount,
                  maxLines: 1,
                  overflow: .ellipsis,
                  style: AppTypography.amount.copyWith(
                    fontSize: 13,
                    height: 18 / 13,
                    color: AppPalette.white,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// 44×44 bell; rings and shows a pulsing badge while there are unread
/// notifications (`fnRing`, `fnPulse`).
class _Bell extends StatefulWidget {
  final bool ringing;
  final VoidCallback onTap;

  const _Bell({required this.ringing, required this.onTap});

  @override
  State<_Bell> createState() => _BellState();
}

class _BellState extends State<_Bell> with SingleTickerProviderStateMixin {
  late final _controller = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 3200),
  );

  static const _deg = math.pi / 180;

  // (progress within the 70–90% window, angle)
  static const _keys = [
    (0.0, 0.0),
    (0.2, 14.0),
    (0.4, -12.0),
    (0.6, 8.0),
    (0.8, -4.0),
    (1.0, 0.0),
  ];

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _sync();
  }

  @override
  void didUpdateWidget(_Bell old) {
    super.didUpdateWidget(old);
    if (old.ringing != widget.ringing) _sync();
  }

  void _sync() {
    final animate = widget.ringing && !MediaQuery.disableAnimationsOf(context);
    if (animate && !_controller.isAnimating) {
      _controller.repeat();
    } else if (!animate) {
      _controller
        ..stop()
        ..value = 0;
    }
  }

  double _angle(double t) {
    if (t < 0.7 || t > 0.9) return 0;
    final w = (t - 0.7) / 0.2;
    for (var i = 1; i < _keys.length; i++) {
      final (p1, a1) = _keys[i];
      if (w <= p1) {
        final (p0, a0) = _keys[i - 1];
        final k = Curves.easeInOut.transform((w - p0) / (p1 - p0));
        return (a0 + (a1 - a0) * k) * _deg;
      }
    }
    return 0;
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AppPressable(
      onTap: widget.onTap,
      semanticLabel: Words.notifications.str,
      child: SizedBox.square(
        dimension: AppSizes.minTap,
        child: Stack(
          alignment: .center,
          children: [
            AnimatedBuilder(
              animation: _controller,
              builder: (_, child) => Transform.rotate(
                angle: _angle(_controller.value),
                alignment: Alignment.topCenter,
                child: child,
              ),
              child: const Icon(
                FinoraIcons.notifications,
                size: AppSizes.iconQuickAction,
                color: Colors.white,
              ),
            ),
            // Spec: 8×8 dot at top 9 / right 10, plus its 2px ring.
            if (widget.ringing)
              const Positioned(
                top: 7,
                right: 8,
                child: AppUnreadDot(
                  color: AppPalette.primary400,
                  ringColor: AppPalette.primary950,
                ),
              ),
          ],
        ),
      ),
    );
  }
}

/// ±45° hairline grid, 44px step (`rgba(167,243,208,0.035)`).
class _DiagonalGridPainter extends CustomPainter {
  const _DiagonalGridPainter();

  static const _step = 44.0;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0x09A7F3D0)
      ..strokeWidth = 1;

    final span = size.width + size.height;
    for (var d = -size.height; d < span; d += _step) {
      canvas
        ..drawLine(Offset(d, 0), Offset(d + size.height, size.height), paint)
        ..drawLine(Offset(d + size.height, 0), Offset(d, size.height), paint);
    }
  }

  @override
  bool shouldRepaint(_DiagonalGridPainter oldDelegate) => false;
}
