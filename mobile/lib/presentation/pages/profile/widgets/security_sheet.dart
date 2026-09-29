import 'dart:async';

import 'package:auto_route/auto_route.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_bottom_sheet.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/widgets/app_segment_control.dart';
import 'package:finora/common/widgets/app_switch.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/di.dart';
import 'package:finora/infrastructure/services/cache/app_cache.dart';
import 'package:finora/infrastructure/services/security/auto_lock_service.dart';
import 'package:finora/presentation/pages/pin/pin_lock_page.dart';
import 'package:finora/presentation/routes/app_router.dart';
import 'package:flutter/material.dart';

/// Security: auto-lock, Face ID, Change PIN, Lock now
/// (docs/screens/PROFILE_SETTINGS.md §3).
class SecuritySheet extends StatefulWidget {
  const SecuritySheet({super.key});

  static Future<void> show(BuildContext context) =>
      AppBottomSheet.show(context, child: const SecuritySheet());

  @override
  State<SecuritySheet> createState() => _SecuritySheetState();
}

class _SecuritySheetState extends State<SecuritySheet> {
  static const _options = [1, 3, 5];

  final _autoLock = di<AutoLockService>();
  final _cache = di<AppCache>();
  Timer? _ticker;

  @override
  void initState() {
    super.initState();
    _ticker = Timer.periodic(
      const Duration(seconds: 1),
      (_) => setState(() {}),
    );
  }

  @override
  void dispose() {
    _ticker?.cancel();
    super.dispose();
  }

  Future<void> _setMinutes(int m) async {
    await _autoLock.setMinutes(m);
    if (!mounted) return;
    setState(() {});
    AppToast.success(Words.autoLockSet.tr(args: ['$m']));
  }

  void _go(PageRouteInfo route) {
    final router = context.router;
    Navigator.of(context).pop();
    router.root.push(route);
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final left = _autoLock.remaining();
    final mmss =
        '${left.inMinutes}:${(left.inSeconds % 60).toString().padLeft(2, '0')}';

    return Column(
      mainAxisSize: .min,
      crossAxisAlignment: .stretch,
      children: [
        SheetHeader(title: Words.security.str),
        const SizedBox(height: AppSpacing.x2l),
        Text(
          Words.autoLock.str,
          style: AppTypography.body.copyWith(
            fontWeight: .w600,
            color: c.textPrimary,
          ),
        ),
        Text(
          Words.autoLockDesc.str,
          style: AppTypography.caption.copyWith(color: c.textSecondary),
        ),
        const SizedBox(height: AppSpacing.md),
        AppSegmentControl(
          index: _options.indexOf(_autoLock.minutes).clamp(0, 2),
          children: [
            for (final m in _options) Words.minShort.tr(args: ['$m']),
          ],
          onChanged: (i) => _setMinutes(_options[i]),
        ),
        const SizedBox(height: AppSpacing.sm),
        Row(
          spacing: 6,
          children: [
            Icon(FinoraIcons.autoLock, size: 14, color: c.textTertiary),
            Text(
              Words.locksIn.tr(args: [mmss]),
              style: AppTypography.caption.copyWith(
                color: c.textTertiary,
                fontFeatures: const [FontFeature.tabularFigures()],
              ),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.lg),
        Container(
          padding: const .symmetric(horizontal: 14, vertical: 4),
          decoration: BoxDecoration(
            color: c.background,
            borderRadius: .circular(18),
          ),
          child: Column(
            children: [
              SizedBox(
                height: 56,
                child: Row(
                  spacing: AppSpacing.md,
                  children: [
                    Icon(
                      FinoraIcons.faceId,
                      size: AppSizes.iconMd,
                      color: c.primaryText,
                    ),
                    Expanded(
                      child: Text(
                        Words.unlockWithFaceId.str,
                        style: context.textStyles.bodyMedium,
                      ),
                    ),
                    AppSwitch(
                      value: _cache.faceIdEnabled,
                      semanticLabel: Words.unlockWithFaceId.str,
                      onChanged: (v) async {
                        await _cache.setFaceIdEnabled(v);
                        setState(() {});
                      },
                    ),
                  ],
                ),
              ),
              Divider(height: 1, color: c.border),
              AppPressable(
                onTap: () => _go(CreatePinRoute(change: true)),
                scale: AppMotion.pressScaleCard,
                child: SizedBox(
                  height: 56,
                  child: Row(
                    spacing: AppSpacing.md,
                    children: [
                      Icon(
                        FinoraIcons.changePin,
                        size: AppSizes.iconMd,
                        color: c.primaryText,
                      ),
                      Expanded(
                        child: Text(
                          Words.changePin.str,
                          style: context.textStyles.bodyMedium,
                        ),
                      ),
                      Icon(
                        FinoraIcons.forward,
                        size: AppSizes.iconTrailing,
                        color: c.textTertiary,
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        AppButton(
          text: Words.lockNow.str,
          icon: FinoraIcons.lock,
          variant: AppButtonVariant.dark,
          onPressed: () => _go(PinLockRoute(reason: LockReason.manual)),
        ),
      ],
    );
  }
}
