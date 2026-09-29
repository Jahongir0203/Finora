import 'package:auto_route/auto_route.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/application/finance/finance_cubit.dart';
import 'package:finora/common/extensions/datetime_extensions.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/category_icons.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_bottom_sheet.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/widgets/app_shake.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/widgets/category_chip.dart';
import 'package:finora/common/helpers/api_call.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/domain/models/receipts/receipt.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

/// "Receipt scanned" (docs/screens/ACTIVITY_SCAN.md §5.1).
class ReceiptResultSheet extends StatelessWidget {
  final Receipt receipt;

  const ReceiptResultSheet({super.key, required this.receipt});

  static Future<void> show(BuildContext context, Receipt receipt) {
    final finance = context.read<FinanceCubit>();
    return AppBottomSheet.show(
      context,
      barrierColor: const Color(0x8C06140E), // rgba(6,20,14,0.55)
      child: BlocProvider.value(
        value: finance,
        child: ReceiptResultSheet(receipt: receipt),
      ),
    );
  }

  String get _categoryId => receipt.suggestedCategoryId ?? 'groceries';

  Future<void> _save(BuildContext context, num total) async {
    final finance = context.read<FinanceCubit>().facade;
    final ok = await apiRun(
      () => finance.addTransaction(
        categoryId: _categoryId,
        amount: -total,
        title: receipt.merchant,
        receiptId: receipt.id,
      ),
    );
    if (!ok || !context.mounted) return;
    Navigator.of(context).pop();
    context.router.maybePop();
    AppToast.success(Words.expenseSaved.str);
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final category = context.watch<FinanceCubit>().state.category(_categoryId);
    final total =
        receipt.total ?? receipt.items.fold<num>(0, (s, e) => s + e.price);
    final now = receipt.date ?? DateTime.now();
    final lineStyle = AppTypography.body.copyWith(color: c.textPrimary);

    return Column(
      mainAxisSize: .min,
      crossAxisAlignment: .stretch,
      children: [
        SheetHeader(
          title: Words.receiptScanned.str,
          leading: Container(
            width: 28,
            height: 28,
            alignment: .center,
            decoration: const BoxDecoration(
              color: AppPalette.primary500,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              FinoraIcons.check,
              size: 16,
              color: AppPalette.primary950,
            ),
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        Container(
          padding: const .all(12),
          decoration: BoxDecoration(
            color: c.background,
            borderRadius: .circular(AppRadius.lg),
          ),
          child: Row(
            spacing: AppSpacing.md,
            children: [
              CategoryTile(category: category),
              Expanded(
                child: Column(
                  crossAxisAlignment: .start,
                  children: [
                    Text(
                      receipt.merchant ?? category?.name ?? '',
                      style: lineStyle.copyWith(fontWeight: .w600),
                    ),
                    Text(
                      '${DateFormat('d MMM y', context.locale.languageCode).format(now)}, ${now.time24}',
                      style: AppTypography.caption.copyWith(
                        color: c.textSecondary,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: AppSpacing.sm),
        for (final (i, ReceiptItem(:name, :quantity, :price))
            in receipt.items.indexed)
          Container(
            padding: const .symmetric(vertical: 8),
            decoration: i == 0
                ? null
                : BoxDecoration(
                    border: Border(top: BorderSide(color: c.divider)),
                  ),
            child: Row(
              children: [
                Expanded(
                  child: Text.rich(
                    TextSpan(
                      text: name,
                      children: [
                        TextSpan(
                          text: ' ×${quantity % 1 == 0 ? quantity.toInt() : quantity}',
                          style: TextStyle(color: c.textTertiary),
                        ),
                      ],
                    ),
                    style: lineStyle.copyWith(fontSize: 14),
                  ),
                ),
                Text(
                  price.toMoney(),
                  style: lineStyle.copyWith(
                    fontSize: 14,
                    fontFeatures: const [FontFeature.tabularFigures()],
                  ),
                ),
              ],
            ),
          ),
        CustomPaint(
          painter: _DashedLinePainter(c.textDisabled),
          child: Padding(
            padding: const .only(top: 12),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    Words.total.str,
                    style: context.textStyles.titleSmall,
                  ),
                ),
                Text(
                  total.toUzs(),
                  style: context.textStyles.titleSmall.copyWith(
                    fontFeatures: const [FontFeature.tabularFigures()],
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        Row(
          children: [
            Expanded(
              child: Text(
                Words.category.str,
                style: AppTypography.body.copyWith(
                  fontSize: 14,
                  color: c.textSecondary,
                ),
              ),
            ),
            Container(
              height: 34,
              padding: const .symmetric(horizontal: 12),
              decoration: BoxDecoration(
                color: c.tint,
                borderRadius: .circular(AppRadius.full),
              ),
              child: Row(
                mainAxisSize: .min,
                spacing: 6,
                children: [
                  Icon(category?.iconData, size: 15, color: c.primaryText),
                  Text(
                    category?.name ?? '',
                    style: AppTypography.bodyMedium.copyWith(
                      fontSize: 14,
                      color: c.primaryText,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.lg),
        Row(
          spacing: AppSpacing.md,
          children: [
            Expanded(
              child: AppButton.outline(
                text: Words.retake.str,
                size: AppButtonSize.large,
                onPressed: () => Navigator.of(context).pop(),
              ),
            ),
            Expanded(
              flex: 2,
              child: AppButton(
                text: Words.saveExpense.str,
                size: AppButtonSize.large,
                onPressed: total > 0 ? () => _save(context, total) : null,
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _DashedLinePainter extends CustomPainter {
  final Color color;

  const _DashedLinePainter(this.color);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 1;
    for (var x = 0.0; x < size.width; x += 7) {
      canvas.drawLine(Offset(x, 0), Offset(x + 4, 0), paint);
    }
  }

  @override
  bool shouldRepaint(_DashedLinePainter old) => old.color != color;
}

/// "No QR code found" (docs/screens/ACTIVITY_SCAN.md §5.2).
class QrErrorSheet extends StatefulWidget {
  final VoidCallback onManual;

  const QrErrorSheet({super.key, required this.onManual});

  static Future<void> show(
    BuildContext context, {
    required VoidCallback onManual,
  }) => AppBottomSheet.show(context, child: QrErrorSheet(onManual: onManual));

  @override
  State<QrErrorSheet> createState() => _QrErrorSheetState();
}

class _QrErrorSheetState extends State<QrErrorSheet> {
  final _shake = AppShakeController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _shake.shake());
  }

  @override
  void dispose() {
    _shake.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Column(
      mainAxisSize: .min,
      crossAxisAlignment: .stretch,
      children: [
        const SizedBox(height: AppSpacing.sm),
        Center(
          child: AppShake(
            controller: _shake,
            child: Container(
              width: 80,
              height: 80,
              alignment: .center,
              decoration: BoxDecoration(
                color: c.dangerSoft,
                shape: BoxShape.circle,
              ),
              child: Icon(FinoraIcons.scan, size: 34, color: c.danger),
            ),
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        Text(
          Words.noQrFound.str,
          textAlign: .center,
          style: context.textStyles.title.copyWith(fontWeight: .w700),
        ),
        const SizedBox(height: AppSpacing.sm),
        Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 290),
            child: Text(
              Words.noQrFoundDesc.str,
              textAlign: .center,
              style: context.textStyles.bodySecondary,
            ),
          ),
        ),
        const SizedBox(height: AppSpacing.x2l),
        AppButton(
          text: Words.tryAgain.str,
          onPressed: () => Navigator.of(context).pop(),
        ),
        const SizedBox(height: AppSpacing.xs),
        AppPressable(
          onTap: () {
            Navigator.of(context).pop();
            widget.onManual();
          },
          child: SizedBox(
            height: 48,
            child: Center(
              child: Text(
                Words.enterManually.str,
                style: AppTypography.button.copyWith(
                  fontSize: 15,
                  color: c.primaryText,
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
