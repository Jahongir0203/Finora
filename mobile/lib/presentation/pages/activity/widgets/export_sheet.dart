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
import 'package:finora/di.dart';
import 'package:finora/domain/facades/exports_facade.dart';
import 'package:finora/domain/models/exports/export_models.dart';
import 'package:finora/infrastructure/services/http/api_client.dart';
import 'package:finora/presentation/pages/pin/widgets/pin_badge.dart';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

typedef _Period = ExportPeriod;
typedef _Format = ExportFormat;

enum _Stage { form, progress, done }

/// Export report: form → "Preparing…" → "Report ready"
/// (docs/screens/ACTIVITY_SCAN.md §4).
///
/// Figures come from `GET /exports/preview`; the file is rendered by the
/// server and opened via its one-time download link.
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
  final _exports = di<ExportsFacade>();
  ExportPreview? _preview;
  ExportFile? _file;

  /// Server names of the selected types.
  ExportInclude get _types => {
    if (_include['expenses']!) 'expense',
    if (_include['income']!) 'income',
    if (_include['transfers']!) 'transfer',
  };

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
    _loadPreview();
  }

  Future<void> _loadPreview() async {
    if (!_valid) return;
    final period = _period, types = _types, format = _format;
    try {
      final preview = await _exports.preview(period, types, format);
      // Ignore answers for a selection the user already changed.
      if (!mounted || period != _period || format != _format) return;
      setState(() => _preview = preview);
    } catch (_) {}
  }

  void _update(VoidCallback change) {
    setState(change);
    _loadPreview();
  }

  @override
  void dispose() {
    _progress.dispose();
    super.dispose();
  }

  bool get _valid => _include.values.any((v) => v);

  Future<void> _export() async {
    setState(() => _stage = .progress);
    _progress.repeat();
    try {
      final file = await _exports.export(_period, _types, _format);
      if (!mounted) return;
      setState(() {
        _file = file;
        _stage = .done;
      });
    } catch (e) {
      if (!mounted) return;
      AppToast.error(apiErrorMessage(e));
      setState(() => _stage = .form);
    } finally {
      _progress.stop();
    }
  }

  Future<void> _open() async {
    final url = _file?.downloadUrl;
    if (url == null) return;
    // The link is one-time: the browser downloads and keeps the file.
    await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
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
    final p = _preview;
    final count = p?.count ?? 0;
    final income = p?.income ?? 0;
    final expense = p?.expenses ?? 0;
    final net = p?.net ?? 0;

    final includes = [
      ('expenses', Words.expenses, FinoraIcons.expense),
      ('income', Words.income, FinoraIcons.income),
      ('transfers', Words.transfers, FinoraIcons.transfer),
    ];
    final formats = [
      (_Format.pdf, 'PDF', Words.formatReport.str, FinoraIcons.fileText),
      (_Format.xlsx, 'Excel', '.xlsx', FinoraIcons.fileSheet),
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
          onChanged: (i) => _update(() => _period = _Period.values[i]),
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
                  p?.rangeLabel ?? '',
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
                onTap: () => _update(() => _include[key] = !_include[key]!),
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
                    onTap: () => _update(() => _format = f),
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
            _preview?.fileName ?? '',
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
          _file?.fileName ?? '',
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
                onPressed: _open,
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
