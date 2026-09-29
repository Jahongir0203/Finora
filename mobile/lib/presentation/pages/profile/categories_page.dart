import 'package:auto_route/auto_route.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/application/finance/finance_cubit.dart';
import 'package:finora/common/extensions/format_extensions.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_empty_state.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_list_tiles.dart';
import 'package:finora/common/widgets/app_pressable.dart';
import 'package:finora/common/widgets/app_segment_control.dart';
import 'package:finora/common/widgets/category_chip.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'widgets/category_sheet.dart';

/// Categories (docs/screens/PROFILE_SETTINGS.md §5).
@RoutePage()
class CategoriesPage extends StatefulWidget {
  const CategoriesPage({super.key});

  @override
  State<CategoriesPage> createState() => _CategoriesPageState();
}

class _CategoriesPageState extends State<CategoriesPage> {
  var _income = false;

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final s = context.watch<FinanceCubit>().state;
    final list = s.categories.where((e) => e.isIncome == _income).toList();

    void create() => CategorySheet.show(context, isIncome: _income);

    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: authOverlayStyle(
        context,
      ).copyWith(systemNavigationBarColor: c.background),
      child: Scaffold(
        backgroundColor: c.background,
        body: SafeArea(
          bottom: false,
          child: AppFadeIn(
            horizontal: true,
            child: ListView(
              padding: .fromLTRB(
                20,
                8,
                20,
                28 + MediaQuery.paddingOf(context).bottom,
              ),
              children: [
                PushHeader(
                  title: Words.categories.str,
                  trailing: AppAddButton(
                    semanticLabel: Words.newCategory.str,
                    onPressed: create,
                  ),
                ),
                const SizedBox(height: AppSpacing.lg),
                AppSegmentControl(
                  height: 36,
                  fontSize: 13,
                  trackColor: c.border,
                  index: _income ? 1 : 0,
                  children: [Words.expenses.str, Words.income.str],
                  onChanged: (i) => setState(() => _income = i == 1),
                ),
                const SizedBox(height: AppSpacing.lg),
                if (list.isEmpty)
                  AppEmptyState(
                    icon: FinoraIcons.shapes,
                    title: Words.noCategories.str,
                    message: Words.noCategoriesDesc.str,
                    action: AppButton(
                      text: Words.addCategory.str,
                      size: AppButtonSize.small,
                      expanded: false,
                      onPressed: create,
                    ),
                  )
                else
                  AppListCard(
                    padding: const .symmetric(horizontal: 16),
                    children: [
                      for (final (i, cat) in list.indexed)
                        AppFadeIn(
                          key: ValueKey('${cat.id}-$_income'),
                          index: i,
                          step: const Duration(milliseconds: 40),
                          child: _CategoryRow(
                            category: cat,
                            transactions: s.transactionCount(cat.id),
                            onTap: () =>
                                CategorySheet.show(context, category: cat),
                          ),
                        ),
                    ],
                  ),
                const SizedBox(height: AppSpacing.lg),
                Text(
                  Words.tapCategoryHint.str,
                  textAlign: .center,
                  style: AppTypography.caption.copyWith(color: c.textTertiary),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _CategoryRow extends StatelessWidget {
  final Category category;
  final int transactions;
  final VoidCallback onTap;

  const _CategoryRow({
    required this.category,
    required this.transactions,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final count = Words.nTransactions.tr(args: ['$transactions']);
    final sub = category.limit == null
        ? count
        : '${Words.budgetAmount.tr(args: [category.limit!.toMoney()])} · $count';

    return AppPressable(
      onTap: onTap,
      scale: AppMotion.pressScaleCard,
      child: SizedBox(
        height: 68,
        child: Row(
          spacing: AppSpacing.md,
          children: [
            CategoryTile(category: category),
            Expanded(
              child: Column(
                mainAxisAlignment: .center,
                crossAxisAlignment: .start,
                children: [
                  Text(
                    category.name,
                    style: AppTypography.body.copyWith(
                      fontWeight: .w600,
                      color: c.textPrimary,
                    ),
                  ),
                  Text(
                    sub,
                    maxLines: 1,
                    overflow: .ellipsis,
                    style: AppTypography.caption.copyWith(
                      color: c.textTertiary,
                      fontFeatures: const [FontFeature.tabularFigures()],
                    ),
                  ),
                ],
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
    );
  }
}
