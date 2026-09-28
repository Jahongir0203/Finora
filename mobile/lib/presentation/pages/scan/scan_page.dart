import 'dart:math' as math;

import 'package:auto_route/auto_route.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/presentation/pages/activity/widgets/add_transaction_sheet.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'widgets/scan_sheets.dart';

/// Receipt / QR scanner (docs/screens/ACTIVITY_SCAN.md §5). Always dark.
///
/// TODO: replace the placeholder viewport with `CameraPreview` (camera) and
/// `MobileScanner` (QR), and run OCR on the captured photo.
@RoutePage()
class ScanPage extends StatefulWidget {
  const ScanPage({super.key});

  @override
  State<ScanPage> createState() => _ScanPageState();
}

class _ScanPageState extends State<ScanPage> {
  var _qr = false;
  var _flash = false;

  static const _overlay = SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
    statusBarBrightness: Brightness.dark,
    systemNavigationBarColor: AppPalette.scanner,
    systemNavigationBarIconBrightness: Brightness.light,
  );

  void _shutter() {
    HapticFeedback.mediumImpact();
    if (_qr) {
      QrErrorSheet.show(context, onManual: _manual);
    } else {
      ReceiptResultSheet.show(context);
    }
  }

  /// Keyboard → back to Home and open New transaction.
  Future<void> _manual() async {
    final router = context.router;
    final navContext = router.navigatorKey.currentContext;
    await router.maybePop();
    if (navContext != null && navContext.mounted) {
      AddTransactionSheet.show(navContext);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: _overlay,
      child: Scaffold(
        backgroundColor: AppPalette.scanner,
        body: SafeArea(
          child: Padding(
            padding: const .fromLTRB(20, 8, 20, 40),
            child: Column(
              spacing: 18,
              children: [
                Row(
                  children: [
                    _RoundButton(
                      icon: FinoraIcons.close,
                      semanticLabel: Words.close.str,
                      onTap: () => context.router.maybePop(),
                    ),
                    Expanded(
                      child: Text(
                        Words.scan.str,
                        textAlign: .center,
                        style: AppTypography.titleSmall.copyWith(
                          color: AppPalette.white,
                        ),
                      ),
                    ),
                    _RoundButton(
                      icon: _flash ? FinoraIcons.flash : FinoraIcons.flashOff,
                      semanticLabel: Words.flash.str,
                      active: _flash,
                      onTap: () => setState(() => _flash = !_flash),
                    ),
                  ],
                ),
                _ModeSwitch(qr: _qr, onChanged: (v) => setState(() => _qr = v)),
                Expanded(child: _Viewport(qr: _qr)),
                Text(
                  _qr ? Words.scanHintQr.str : Words.scanHintReceipt.str,
                  textAlign: .center,
                  style: AppTypography.body.copyWith(
                    fontSize: 14,
                    color: AppPalette.scannerMuted,
                  ),
                ),
                Row(
                  mainAxisAlignment: .spaceBetween,
                  children: [
                    _RoundButton(
                      icon: FinoraIcons.image,
                      size: 52,
                      semanticLabel: Words.gallery.str,
                      onTap: () => AppToast.info(Words.soon.str),
                    ),
                    _Shutter(onTap: _shutter),
                    _RoundButton(
                      icon: FinoraIcons.keyboard,
                      size: 52,
                      semanticLabel: Words.enterManually.str,
                      onTap: _manual,
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _RoundButton extends StatelessWidget {
  final IconData icon;
  final String semanticLabel;
  final VoidCallback onTap;
  final double size;
  final bool active;

  const _RoundButton({
    required this.icon,
    required this.semanticLabel,
    required this.onTap,
    this.size = AppSizes.minTap,
    this.active = false,
  });

  @override
  Widget build(BuildContext context) {
    return AppPressable(
      onTap: onTap,
      semanticLabel: semanticLabel,
      child: AnimatedContainer(
        duration: AppMotion.fast,
        width: size,
        height: size,
        alignment: .center,
        decoration: BoxDecoration(
          color: active ? AppPalette.primary500 : AppPalette.scannerControl,
          shape: BoxShape.circle,
        ),
        child: Icon(
          icon,
          size: AppSizes.iconQuickAction,
          color: active ? AppPalette.primary950 : AppPalette.white,
        ),
      ),
    );
  }
}

class _ModeSwitch extends StatelessWidget {
  final bool qr;
  final ValueChanged<bool> onChanged;

  const _ModeSwitch({required this.qr, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    Widget item(String label, bool value) {
      final active = qr == value;
      return Expanded(
        child: Semantics(
          selected: active,
          button: true,
          child: GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTap: () => onChanged(value),
            child: AnimatedContainer(
              duration: AppMotion.fast,
              height: 36,
              alignment: .center,
              decoration: BoxDecoration(
                color: active ? AppPalette.white : Colors.transparent,
                borderRadius: .circular(AppRadius.sm),
              ),
              child: Text(
                label,
                style: AppTypography.button.copyWith(
                  fontSize: 14,
                  color: active
                      ? AppPalette.scannerInk
                      : AppPalette.scannerMuted,
                ),
              ),
            ),
          ),
        ),
      );
    }

    return Container(
      padding: const .all(AppSpacing.xs),
      decoration: BoxDecoration(
        color: AppPalette.scannerControl,
        borderRadius: .circular(AppRadius.md),
      ),
      child: Row(
        spacing: AppSpacing.xs,
        children: [
          item(Words.receipt.str, false),
          item(Words.qrPayment.str, true),
        ],
      ),
    );
  }
}

/// Placeholder camera area with corner frame and a sweeping scan line.
class _Viewport extends StatefulWidget {
  final bool qr;

  const _Viewport({required this.qr});

  @override
  State<_Viewport> createState() => _ViewportState();
}

class _ViewportState extends State<_Viewport>
    with SingleTickerProviderStateMixin {
  // fnScan: 14% → 86% → 14%, 2.6s.
  late final _scan = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 2600),
  );

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (MediaQuery.disableAnimationsOf(context)) {
      _scan.stop();
    } else if (!_scan.isAnimating) {
      _scan.repeat();
    }
  }

  @override
  void dispose() {
    _scan.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ConstrainedBox(
      constraints: const BoxConstraints(minHeight: 300),
      child: ClipRRect(
        borderRadius: .circular(AppRadius.sheet),
        child: ColoredBox(
          color: AppPalette.scannerViewport,
          child: LayoutBuilder(
            builder: (context, box) => Stack(
              children: [
                Center(
                  child: widget.qr ? const _QrMock() : const _ReceiptMock(),
                ),
                const Positioned.fill(
                  child: Padding(
                    padding: .all(40),
                    child: CustomPaint(painter: _CornersPainter()),
                  ),
                ),
                AnimatedBuilder(
                  animation: _scan,
                  builder: (_, _) {
                    final t = Curves.easeInOut.transform(
                      _scan.value < 0.5
                          ? _scan.value * 2
                          : (1 - _scan.value) * 2,
                    );
                    return Positioned(
                      left: 44,
                      right: 44,
                      top: box.maxHeight * (0.14 + 0.72 * t),
                      child: Container(
                        height: 2,
                        decoration: const BoxDecoration(
                          color: AppPalette.primary500,
                          boxShadow: [
                            BoxShadow(
                              color: Color(0x8C10B981),
                              blurRadius: 16,
                              spreadRadius: 4,
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _CornersPainter extends CustomPainter {
  const _CornersPainter();

  @override
  void paint(Canvas canvas, Size size) {
    const len = 36.0, r = 14.0;
    final paint = Paint()
      ..color = AppPalette.primary500
      ..strokeWidth = 4
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.butt;

    void corner(Offset o, double sx, double sy) {
      final path = Path()
        ..moveTo(o.dx, o.dy + sy * len)
        ..lineTo(o.dx, o.dy + sy * r)
        ..arcToPoint(
          Offset(o.dx + sx * r, o.dy),
          radius: const Radius.circular(r),
          clockwise: sx * sy > 0,
        )
        ..lineTo(o.dx + sx * len, o.dy);
      canvas.drawPath(path, paint);
    }

    corner(Offset.zero, 1, 1);
    corner(Offset(size.width, 0), -1, 1);
    corner(Offset(0, size.height), 1, -1);
    corner(Offset(size.width, size.height), -1, -1);
  }

  @override
  bool shouldRepaint(_CornersPainter oldDelegate) => false;
}

class _ReceiptMock extends StatelessWidget {
  const _ReceiptMock();

  @override
  Widget build(BuildContext context) {
    Widget line(double w, [double h = 8]) => Container(
      width: w,
      height: h,
      margin: const .only(bottom: 12),
      decoration: BoxDecoration(
        color: const Color(0xFFC9CCC7),
        borderRadius: .circular(4),
      ),
    );

    return Transform.rotate(
      angle: -2 * math.pi / 180,
      child: Container(
        width: 200,
        height: 300,
        padding: const .fromLTRB(20, 24, 20, 20),
        decoration: BoxDecoration(
          color: const Color(0xFFECEDE8),
          borderRadius: .circular(6),
          boxShadow: const [
            BoxShadow(
              color: Color(0x66000000),
              blurRadius: 30,
              offset: Offset(0, 12),
            ),
          ],
        ),
        child: Column(
          children: [
            line(100, 12),
            line(66),
            const SizedBox(height: 8),
            for (final w in [160.0, 140.0, 156.0, 118.0, 150.0, 132.0])
              Align(alignment: .centerLeft, child: line(w)),
            const Spacer(),
            Container(height: 1, color: const Color(0xFFB5B8B2)),
            const SizedBox(height: 10),
            Align(alignment: .centerRight, child: line(84, 10)),
          ],
        ),
      ),
    );
  }
}

class _QrMock extends StatelessWidget {
  const _QrMock();

  @override
  Widget build(BuildContext context) {
    Widget finder() => Container(
      width: 48,
      height: 48,
      decoration: BoxDecoration(
        border: Border.all(color: const Color(0xFF1F2925), width: 10),
        borderRadius: .circular(6),
      ),
    );

    return Container(
      width: 180,
      height: 180,
      padding: const .all(22),
      decoration: BoxDecoration(
        color: const Color(0xFFECEDE8),
        borderRadius: .circular(AppRadius.lg),
      ),
      child: Column(
        mainAxisAlignment: .spaceBetween,
        children: [
          Row(mainAxisAlignment: .spaceBetween, children: [finder(), finder()]),
          Row(
            mainAxisAlignment: .spaceBetween,
            children: [
              finder(),
              Container(width: 28, height: 28, color: const Color(0xFF1F2925)),
            ],
          ),
        ],
      ),
    );
  }
}

class _Shutter extends StatelessWidget {
  final VoidCallback onTap;

  const _Shutter({required this.onTap});

  @override
  Widget build(BuildContext context) {
    return AppPressable(
      onTap: onTap,
      semanticLabel: Words.takePhoto.str,
      child: Container(
        width: 78,
        height: 78,
        padding: const .all(5),
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          border: Border.all(color: AppPalette.primary500, width: 4),
        ),
        child: const DecoratedBox(
          decoration: BoxDecoration(
            color: AppPalette.white,
            shape: BoxShape.circle,
          ),
        ),
      ),
    );
  }
}
