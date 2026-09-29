import 'package:finora/common/helpers/api_call.dart';
import 'package:auto_route/auto_route.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:finora/application/finance/finance_cubit.dart';
import 'package:finora/common/theme/core/functions.dart';
import 'package:finora/common/widgets/app_button.dart';
import 'package:finora/common/widgets/app_chip.dart';
import 'package:finora/common/widgets/app_empty_state.dart';
import 'package:finora/common/widgets/app_fade_in.dart';
import 'package:finora/common/widgets/app_header.dart';
import 'package:finora/common/widgets/app_text_field.dart';
import 'package:finora/common/words/words.dart';
import 'package:finora/domain/models/finance/finance_models.dart';
import 'package:finora/presentation/pages/auth/widgets/auth_back_button.dart';
import 'package:finora/presentation/pages/main/main_actions.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'widgets/day_group.dart';

enum ActivityFilter { all, expenses, income }

/// Activity tab (docs/screens/ACTIVITY_SCAN.md §2).
@RoutePage()
class ActivityPage extends StatefulWidget {
  const ActivityPage({super.key});

  @override
  State<ActivityPage> createState() => _ActivityPageState();
}

class _ActivityPageState extends State<ActivityPage> {
  final _search = TextEditingController();
  var _filter = ActivityFilter.all;
  var _loadingMore = false;

  Future<void> _loadMore() async {
    if (_loadingMore) return;
    setState(() => _loadingMore = true);
    final finance = context.read<FinanceCubit>().facade;
    await apiRun(finance.loadMoreTransactions);
    if (mounted) setState(() => _loadingMore = false);
  }

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  void _clear() {
    _search.clear();
    FocusScope.of(context).unfocus();
    setState(() => _filter = .all);
  }

  List<Transaction> _visible(FinanceSnapshot s) {
    final q = _search.text.trim().toLowerCase();
    return s.transactions.where((t) {
      final byType = switch (_filter) {
        .all => true,
        .income => t.amount > 0,
        .expenses => t.amount < 0,
      };
      final name = s.category(t.categoryId)?.name ?? '';
      return byType &&
          (q.isEmpty || '${t.title} $name'.toLowerCase().contains(q));
    }).toList();
  }

  /// Today / Yesterday / `Wed, 24 Sep`.
  String _dayLabel(DateTime d, DateTime now) {
    final days = DateTime.utc(
      now.year,
      now.month,
      now.day,
    ).difference(DateTime.utc(d.year, d.month, d.day)).inDays;
    if (days == 0) return Words.today.str;
    if (days == 1) return Words.yesterday.str;
    return DateFormat('EEE, d MMM', context.locale.languageCode).format(d);
  }

  @override
  Widget build(BuildContext context) {
    final c = context.appColors;
    final snapshot = context.watch<FinanceCubit>().state;
    final list = _visible(snapshot);
    final now = DateTime.now();

    // Group by calendar day, newest first.
    final groups = <DateTime, List<Transaction>>{};
    for (final t in list) {
      groups
          .putIfAbsent(
            DateTime(t.date.year, t.date.month, t.date.day),
            () => [],
          )
          .add(t);
    }

    final filters = [
      (ActivityFilter.all, Words.all),
      (ActivityFilter.expenses, Words.expenses),
      (ActivityFilter.income, Words.income),
    ];

    var index = 0;
    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: authOverlayStyle(context),
      child: Scaffold(
        backgroundColor: c.background,
        body: SafeArea(
          bottom: false,
          child: AppFadeIn(
            child: CustomScrollView(
              slivers: [
                SliverPadding(
                  padding: .fromLTRB(
                    20,
                    8,
                    20,
                    28 + MediaQuery.paddingOf(context).bottom,
                  ),
                  sliver: SliverList.list(
                    children: [
                      TabHeader(
                        title: Words.navActivity.str,
                        actions: [
                          AppIconButton(
                            icon: FinoraIcons.export,
                            semanticLabel: Words.exportReport.str,
                            onPressed: () => MainActions.export(context),
                          ),
                        ],
                      ),
                      if (snapshot.transactions.isNotEmpty) ...[
                        const SizedBox(height: AppSpacing.lg),
                        AppTextField.search(
                          hint: Words.searchTransactions.str,
                          controller: _search,
                          onChanged: (_) => setState(() {}),
                        ),
                        const SizedBox(height: AppSpacing.lg),
                        Row(
                          spacing: AppSpacing.sm,
                          children: [
                            for (final (f, label) in filters)
                              AppChip(
                                label: label.str,
                                selected: _filter == f,
                                onTap: () => setState(() => _filter = f),
                              ),
                          ],
                        ),
                      ],
                      for (final MapEntry(key: day, value: items)
                          in groups.entries) ...[
                        const SizedBox(height: AppSpacing.lg),
                        DayGroup(
                          label: _dayLabel(day, now),
                          total: items.fold<num>(0, (s, t) => s + t.amount),
                          transactions: items,
                          firstIndex: (index += items.length) - items.length,
                        ),
                      ],
                      if (snapshot.hasMoreTransactions && list.isNotEmpty) ...[
                        const SizedBox(height: AppSpacing.lg),
                        Center(
                          child: AppButton.secondary(
                            text: Words.loadMore.str,
                            size: AppButtonSize.small,
                            expanded: false,
                            isLoading: _loadingMore,
                            onPressed: _loadMore,
                          ),
                        ),
                      ],
                      if (snapshot.transactions.isEmpty)
                        Padding(
                          padding: const .only(top: 48),
                          child: AppEmptyState(
                            icon: FinoraIcons.receipt,
                            title: Words.noTransactionsTitle.str,
                            message: Words.activityEmptyDesc.str,
                            action: Row(
                              mainAxisSize: .min,
                              spacing: AppSpacing.sm,
                              children: [
                                AppButton(
                                  text: Words.addTransaction.str,
                                  size: AppButtonSize.small,
                                  expanded: false,
                                  onPressed: () =>
                                      MainActions.newTransaction(context),
                                ),
                                AppButton.secondary(
                                  text: Words.scanReceipt.str,
                                  size: AppButtonSize.small,
                                  expanded: false,
                                  onPressed: () => MainActions.scan(context),
                                ),
                              ],
                            ),
                          ),
                        )
                      else if (list.isEmpty)
                        Padding(
                          padding: const .only(top: 32),
                          child: AppEmptyState(
                            icon: FinoraIcons.noResults,
                            title: Words.nothingFound.str,
                            message: Words.nothingFoundDesc.str,
                            action: AppButton.secondary(
                              text: Words.clearFilters.str,
                              size: AppButtonSize.small,
                              expanded: false,
                              onPressed: _clear,
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
