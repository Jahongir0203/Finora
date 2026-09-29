import 'package:finora/common/helpers/api_call.dart';
import 'package:finora/application/finance/finance_cubit.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/category_icons.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_bottom_sheet.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/widgets/app_text_field.dart';
import 'package:finora/common/widgets/app_toast.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:finora/presentation/pages/pin/widgets/pin_badge.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

/// Edit / New category (docs/screens/PROFILE_SETTINGS.md §5.1).
class CategorySheet extends StatefulWidget {
  /// `null` = new category.
  final Category? category;
  final bool isIncome;

  const CategorySheet({super.key, this.category, this.isIncome = false});

  static Future<void> show(
    BuildContext context, {
    Category? category,
    bool isIncome = false,
  }) {
    final finance = context.read<FinanceCubit>();
    return AppBottomSheet.show(
      context,
      child: BlocProvider.value(
        value: finance,
        child: CategorySheet(
          category: category,
          isIncome: category?.isIncome ?? isIncome,
        ),
      ),
    );
  }

  @override
  State<CategorySheet> createState() => _CategorySheetState();
}

class _CategorySheetState extends State<CategorySheet> {
  late final _name = TextEditingController(text: widget.category?.name);
  late final _budget = TextEditingController(
    text: widget.category?.limit == null
        ? ''
        : AppFormat.spaced(widget.category!.limit!),
  );
  late var _icon = widget.category?.icon ?? 'coffee';
  late var _color = widget.category?.color ?? 0xFF14B8A6;
  var _showError = false;

  bool get _isEdit => widget.category != null;

  @override
  void dispose() {
    _name.dispose();
    _budget.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    if (_name.text.trim().isEmpty) {
      setState(() => _showError = true);
      return;
    }
    final limit = SpacedDigitsFormatter.parse(_budget.text);
    final category = Category(
      id: widget.category?.id ?? '',
      name: _name.text.trim(),
      icon: _icon,
      color: _color,
      isIncome: widget.isIncome,
      limit: widget.isIncome || limit == 0 ? null : limit,
    );
    final finance = context.read<FinanceCubit>().facade;
    if (!await apiRun(() => finance.saveCategory(category)) || !mounted) {
      return;
    }
    Navigator.of(context).pop();
    AppToast.success(
      _isEdit ? Words.categoryUpdated.str : Words.categoryAdded.str,
    );
  }

  Future<void> _delete() async {
    final finance = context.read<FinanceCubit>().facade;
    final id = widget.category!.id;
    // Transactions of a deleted category move to the default one of its type.
    final fallback = widget.isIncome ? 'salary' : 'groceries';
    final ok = await apiRun(
      () => finance.deleteCategory(
        id,
        reassignTo: finance.snapshot.transactionCount(id) > 0 && id != fallback
            ? fallback
            : null,
      ),
    );
    if (!ok || !mounted) return;
    Navigator.of(context).pop();
    AppToast.success(Words.categoryDeleted.str);
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final color = Color(_color);
    final name = _name.text.trim();

    return Column(
      mainAxisSize: .min,
      crossAxisAlignment: .stretch,
      children: [
        SheetHeader(
          title: _isEdit ? Words.editCategory.str : Words.newCategory.str,
        ),
        const SizedBox(height: AppSpacing.lg),
        Center(
          child: PopIn(
            child: AnimatedContainer(
              duration: AppMotion.fast,
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                color: AppPalette.tintOf(color),
                borderRadius: .circular(22),
              ),
              child: Icon(CategoryIcons.of(_icon), size: 32, color: color),
            ),
          ),
        ),
        const SizedBox(height: 10),
        Text(
          name.isEmpty ? Words.categoryName.str : name,
          textAlign: .center,
          style: context.textStyles.titleSmall.copyWith(
            color: name.isEmpty ? c.textTertiary : c.textPrimary,
          ),
        ),
        const SizedBox(height: AppSpacing.lg),
        AppFormField(
          label: Words.name.str,
          hint: Words.categoryNameHint.str,
          controller: _name,
          maxLength: 24,
          errorText: _showError && name.isEmpty ? '' : null,
          onChanged: (_) => setState(() {}),
        ),
        const SizedBox(height: AppSpacing.lg),
        SectionLabel(Words.icon.str),
        const SizedBox(height: AppSpacing.sm),
        GridView.count(
          crossAxisCount: 6,
          mainAxisSpacing: AppSpacing.sm,
          crossAxisSpacing: AppSpacing.sm,
          childAspectRatio: 1.15,
          shrinkWrap: true,
          padding: EdgeInsets.zero,
          physics: const NeverScrollableScrollPhysics(),
          children: [
            for (final icon in CategoryIcons.categoryPicker)
              Semantics(
                selected: icon == _icon,
                button: true,
                child: AppPressable(
                  onTap: () => setState(() => _icon = icon),
                  child: AnimatedContainer(
                    duration: AppMotion.fast,
                    decoration: BoxDecoration(
                      color: icon == _icon
                          ? AppPalette.tintOf(color)
                          : c.background,
                      borderRadius: .circular(AppRadius.md),
                      border: Border.all(
                        color: icon == _icon ? color : Colors.transparent,
                        width: AppSizes.borderThick,
                      ),
                    ),
                    child: Icon(
                      CategoryIcons.of(icon),
                      size: AppSizes.iconTrailing,
                      color: icon == _icon ? color : c.textSecondary,
                    ),
                  ),
                ),
              ),
          ],
        ),
        const SizedBox(height: AppSpacing.lg),
        SectionLabel(Words.color.str),
        const SizedBox(height: AppSpacing.sm),
        Wrap(
          spacing: AppSpacing.md,
          runSpacing: AppSpacing.md,
          children: [
            for (final value in CategoryIcons.colors)
              Semantics(
                selected: value == _color,
                button: true,
                child: GestureDetector(
                  onTap: () => setState(() => _color = value),
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    width: 32,
                    height: 32,
                    decoration: BoxDecoration(
                      color: Color(value),
                      shape: BoxShape.circle,
                      boxShadow: value == _color
                          ? [
                              BoxShadow(color: Color(value), spreadRadius: 5),
                              BoxShadow(color: c.surface, spreadRadius: 3),
                            ]
                          : null,
                    ),
                  ),
                ),
              ),
          ],
        ),
        if (!widget.isIncome) ...[
          const SizedBox(height: AppSpacing.lg),
          AppInlineAmountField(
            label: Words.monthlyBudget.str,
            hint: Words.noLimit.str,
            controller: _budget,
          ),
        ],
        if (_showError && name.isEmpty) ...[
          const SizedBox(height: AppSpacing.md),
          Row(
            spacing: 6,
            children: [
              Icon(FinoraIcons.alert, size: 15, color: c.danger),
              Text(
                Words.giveCategoryName.str,
                style: AppTypography.caption.copyWith(
                  fontWeight: .w500,
                  color: c.danger,
                ),
              ),
            ],
          ),
        ],
        const SizedBox(height: AppSpacing.lg),
        if (_isEdit)
          Row(
            spacing: AppSpacing.md,
            children: [
              Expanded(
                child: AppButton.destructive(
                  text: Words.delete.str,
                  size: AppButtonSize.large,
                  onPressed: _delete,
                ),
              ),
              Expanded(
                flex: 2,
                child: AppButton(
                  text: Words.saveChanges.str,
                  size: AppButtonSize.large,
                  onPressed: _save,
                ),
              ),
            ],
          )
        else
          AppButton(
            text: Words.createCategory.str,
            size: AppButtonSize.large,
            onPressed: _save,
          ),
      ],
    );
  }
}
