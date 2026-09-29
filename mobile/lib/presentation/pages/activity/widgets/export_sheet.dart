import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_bottom_sheet.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_chip.dart';
import 'package:finora/common/widgets/app_float.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/widgets/app_segment_control.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/presentation/pages/pin/widgets/pin_badge.dart';
import 'package:flutter/material.dart';

enum _Period { daily, weekly, monthly, yearly }

enum _Format {
  pdf('pdf', '1.2 MB'),
  excel('xlsx', '86 KB'),
  csv('csv', '24 KB');

  final String ext;
  final String size;

  const _Format(this.ext, this.size);
}

enum _Stage { form, progress, done }

/// Export report: form → "Preparing…" → "Report ready"
/// (docs/screens/ACTIVITY_SCAN.md §4).
///
/// Figures are mock values from the spec.
// TODO: generate the file via `/export` and share it with share_plus.
class ExportSheet extends StatefulWidget {
  const ExportSheet({super.key});

  static Future<void> show(BuildContext context) =>
      AppBottomSheet.show(context, child: const ExportSheet());

  @override
  State<ExportSheet> createState() => _ExportSheetState();
}

class _ExportSheetState extends State<ExportSheet>
    with SingleTickerProviderStateMixin {
  var _period = _Period.monthly;
  var _format = _Format.pdf;
  var _stage = _Stage.form;
  final _include = {'expenses': true, 'income': true, 'transfers': true};

  // Created eagerly: a lazy controller would first be built in dispose()
  // when the sheet closes without exporting.
  late final AnimationController _progress;

  @override
  void initState() {
    super.initState();
    _progress = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1600),
    );
  }

  // (count, income, expense) per period.
  static const _data = {
    _Period.daily: (2, 12500000, 186400),
    _Period.weekly: (8, 13000000, 767400),
    _Period.monthly: (64, 13000000, 5460000),
    _Period.yearly: (712, 117000000, 52900000),
  };

  @override
  void dispose() {
    _progress.dispose();
    super.dispose();
  }

  bool get _valid => _include.values.any((v) => v);

  String get _locale => context.locale.languageCode;

  String _range(DateTime now) => switch (_period) {
    .daily => DateFormat('d MMM y', _locale).format(now),
    .weekly =>
      '${DateFormat('d', _locale).format(now.subtract(const Duration(days: 6)))} – '
          '${DateFormat('d MMM y', _locale).format(now)}',
    .monthly => DateFormat('MMMM y', _locale).format(now),
    .yearly =>
      '${DateFormat('MMMM', _locale).format(DateTime(now.year))} – '
          '${DateFormat('MMMM y', _locale).format(now)}',
  };

  String _fileName(DateTime now) {
    final mon = DateFormat('MMM', 'en').format(now).toLowerCase();
    final week =
        ((now.difference(DateTime(now.year)).inDays +
                    DateTime(now.year).weekday -
                    1) /
                7)
            .floor() +
        1;
    final part = switch (_period) {
      .daily => '${now.day}$mon${now.year}',
      .weekly => 'w${week}_${now.year}',
      .monthly => '$mon${now.year}',
      .yearly => '${now.year}',
    };
    return 'finora_${_period.name}_$part.${_format.ext}';
  }

  Future<void> _export() async {
    setState(() => _stage = .progress);
    await _progress.forward(from: 0);
    await Future.delayed(const Duration(milliseconds: 100));
    if (mounted) setState(() => _stage = .done);
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedSize(
      duration: AppMotion.push,
      curve: AppMotion.easeSheet,
      alignment: Alignment.bottomCenter,
      child: AnimatedSwitcher(
        duration: AppMotion.fade,
        child: switch (_stage) {
          .form => _form(context),
          .progress => _preparing(context),
          .done => _done(context),
        },
      ),
    );
  }

  Widget _form(BuildContext context) {
    final c = context.appColors;
    final now = DateTime.now();
    final (count, rawIncome, rawExpense) = _data[_period]!;
    final income = _include['income']! ? rawIncome : 0;
    final expense = _include['expenses']! ? rawExpense : 0;
    final net = income - expense;

    final includes = [
      ('expenses', Words.expenses, FinoraIcons.expense),
      ('income', Words.income, FinoraIcons.income),
      ('transfers', Words.transfers, FinoraIcons.transfer),
    ];
    final formats = [
      (_Format.pdf, 'PDF', Words.formatReport.str, FinoraIcons.fileText),
      (_Format.excel, 'Excel', '.xlsx', FinoraIcons.fileSheet),
      (_Format.csv, 'CSV', Words.formatRawData.str, FinoraIcons.file),
    ];

    return Column(
      key: const ValueKey('form'),
      mainAxisSize: .min,
      crossAxisAlignment: .stretch,
      children: [
        SheetHeader(title: Words.exportReport.str),
        const SizedBox(height: AppSpacing.lg),
        AppSegmentControl(
          height: 36,
          fontSize: 13,
          trackColor: c.border,
          index: _period.index,
          children: [
            Words.daily.str,
            Words.weekly.str,
            Words.monthly.str,
            Words.yearly.str,
          ],
          onChanged: (i) => setState(() => _period = _Period.values[i]),
        ),
        const SizedBox(height: AppSpacing.lg),
        Container(
          padding: const .symmetric(horizontal: 14, vertical: 12),
          decoration: BoxDecoration(
            color: c.background,
            borderRadius: .circular(AppRadius.md),
          ),
          child: Row(
            spacing: AppSpacing.md,
            children: [
              Icon(
                FinoraIcons.calendar,
                size: AppSizes.iconTrailing,
                color: c.primaryText,
              ),
              Expanded(
                child: Text(
                  _range(now),
                  style: AppTypography.body.copyWith(
                    fontWeight: .w600,
                    color: c.textPrimary,
                  ),
                ),
              ),
              Text(
                Words.nTransactions.tr(args: ['$count']),
                style: AppTypography.caption.copyWith(color: c.textTertiary),
              ),
            ],
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        Row(
          spacing: AppSpacing.sm,
          children: [
            _SummaryBox(
              label: Words.income.str,
              value: '+${income.toShort()}',
              color: c.primaryText,
            ),
            _SummaryBox(
              label: Words.expenses.str,
              value: '${AppFormat.minus}${expense.toShort()}',
              color: c.textPrimary,
            ),
            _SummaryBox(
              label: Words.net.str,
              value: net < 0 ? net.toShort() : '+${net.toShort()}',
              color: net < 0 ? c.danger : c.primaryText,
            ),
          ],
        ),
        const SizedBox(height: AppSpacing.lg),
        SectionLabel(Words.include.str),
        const SizedBox(height: AppSpacing.sm),
        Wrap(
          spacing: AppSpacing.sm,
          runSpacing: AppSpacing.sm,
          children: [
            for (final (key, label, icon) in includes)
              AppChip(
                label: label.str,
                selected: _include[key]!,
                icon: _include[key]! ? FinoraIcons.check : icon,
                iconColor: c.textSecondary,
                height: 38,
                onTap: () => setState(() => _include[key] = !_include[key]!),
              ),
          ],
        ),
        const SizedBox(height: AppSpacing.lg),
        SectionLabel(Words.format.str),
        const SizedBox(height: AppSpacing.sm),
        Row(
          spacing: AppSpacing.sm,
          children: [
            for (final (f, name, sub, icon) in formats)
              Expanded(
                child: Semantics(
                  selected: f == _format,
                  child: AppPressable(
                    onTap: () => setState(() => _format = f),
                    child: AnimatedContainer(
                      duration: AppMotion.fast,
                      height: 84,
                      decoration: BoxDecoration(
                        color: f == _format ? c.tint : c.surface,
                        borderRadius: .circular(AppRadius.lg),
                        border: Border.all(
                          color: f == _format
                              ? AppPalette.primary500
                              : c.border,
                          width: AppSizes.borderThick,
                        ),
                      ),
                      child: Column(
                        mainAxisAlignment: .center,
                        spacing: 2,
                        children: [
                          Icon(
                            icon,
                            size: AppSizes.iconQuickAction,
                            color: f == _format
                                ? c.primaryText
                                : c.textSecondary,
                          ),
                          const SizedBox(height: 2),
                          Text(
                            name,
                            style: AppTypography.body.copyWith(
                              fontWeight: .w600,
                              color: c.textPrimary,
                            ),
                          ),
                          Text(
                            sub,
                            style: AppTypography.caption.copyWith(
                              fontSize: 12,
                              color: c.textTertiary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
        if (!_valid) ...[
          const SizedBox(height: AppSpacing.md),
          Row(
            spacing: 6,
            children: [
              Icon(FinoraIcons.alert, size: 15, color: c.danger),
              Text(
                Words.selectAtLeastOne.str,
                style: AppTypography.caption.copyWith(
                  fontWeight: .w500,
                  color: c.danger,
                ),
              ),
            ],
          ),
        ],
        const SizedBox(height: AppSpacing.lg),
        AppButton(
          text: Words.exportAs.tr(args: [formats[_format.index].$2]),
          icon: FinoraIcons.export,
          size: AppButtonSize.large,
          onPressed: _valid ? _export : null,
        ),
      ],
    );
  }

  Widget _preparing(BuildContext context) {
    final c = context.appColors;

    return Padding(
      key: const ValueKey('progress'),
      padding: const .symmetric(vertical: 24),
      child: Column(
        mainAxisSize: .min,
        spacing: AppSpacing.md,
        children: [
          AppFloat(
            period: const Duration(milliseconds: 1600),
            distance: 6,
            child: Container(
              width: 76,
              height: 76,
              alignment: .center,
              decoration: BoxDecoration(
                color: c.tint,
                borderRadius: .circular(AppRadius.x2l),
              ),
              child: Icon(FinoraIcons.fileText, size: 34, color: c.primaryText),
            ),
          ),
          const SizedBox(height: AppSpacing.xs),
          Text(
            Words.preparingReport.str,
            style: context.textStyles.titleSmall.copyWith(fontSize: 18),
          ),
          Text(
            _fileName(DateTime.now()),
            style: AppTypography.caption.copyWith(color: c.textTertiary),
          ),
          const SizedBox(height: AppSpacing.sm),
          ClipRRect(
            borderRadius: .circular(AppRadius.full),
            child: AnimatedBuilder(
              animation: _progress,
              builder: (_, _) => LinearProgressIndicator(
                value: _progress.value,
                minHeight: 8,
                color: AppPalette.primary500,
                backgroundColor: c.divider,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _done(BuildContext context) {
    final c = context.appColors;

    return Column(
      key: const ValueKey('done'),
      mainAxisSize: .min,
      crossAxisAlignment: .stretch,
      children: [
        const SizedBox(height: AppSpacing.lg),
        Center(
          child: PopIn(
            duration: const Duration(milliseconds: 600),
            child: Container(
              width: 80,
              height: 80,
              alignment: .center,
              decoration: const BoxDecoration(
                color: AppPalette.primary500,
                shape: BoxShape.circle,
                boxShadow: [
                  BoxShadow(
                    color: Color(0x5910B981),
                    blurRadius: 30,
                    offset: Offset(0, 12),
                  ),
                ],
              ),
              child: const Icon(
                FinoraIcons.check,
                size: 38,
                color: AppPalette.primary950,
              ),
            ),
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        Text(
          Words.reportReady.str,
          textAlign: .center,
          style: context.textStyles.title.copyWith(fontWeight: .w700),
        ),
        const SizedBox(height: AppSpacing.xs),
        Text(
          '${_fileName(DateTime.now())} · ${_format.size}',
          textAlign: .center,
          style: AppTypography.body.copyWith(
            fontSize: 14,
            color: c.textSecondary,
          ),
        ),
        const SizedBox(height: AppSpacing.x2l),
        Row(
          spacing: AppSpacing.md,
          children: [
            Expanded(
              child: AppButton.outline(
                text: Words.share.str,
                icon: FinoraIcons.share,
                onPressed: () => AppToast.info(Words.soon.str),
              ),
            ),
            Expanded(
              child: AppButton(
                text: Words.ready.str,
                onPressed: () => Navigator.of(context).pop(),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class _SummaryBox extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _SummaryBox({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;

    return Expanded(
      child: Container(
        padding: const .all(10),
        decoration: BoxDecoration(
          borderRadius: .circular(AppRadius.md),
          border: Border.all(color: c.border),
        ),
        child: Column(
          crossAxisAlignment: .start,
          spacing: 2,
          children: [
            Text(
              label,
              style: AppTypography.caption.copyWith(color: c.textTertiary),
            ),
            Text(
              value,
              style: AppTypography.amount.copyWith(fontSize: 16, color: color),
            ),
          ],
        ),
      ),
    );
  }
}
