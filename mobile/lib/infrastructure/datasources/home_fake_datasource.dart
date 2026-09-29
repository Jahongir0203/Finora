import 'package:finora/domain/facades/finance_facade.dart';
import 'package:finora/domain/facades/home_facade.dart';
import 'package:finora/domain/models/home/home_data.dart';
import 'package:injectable/injectable.dart';

/// Builds the Home snapshot from the shared [FinanceFacade].
///
/// TODO: replace with the `/home` endpoint.
@LazySingleton(as: HomeFacade)
class HomeFakeDatasource implements HomeFacade {
  final FinanceFacade _finance;

  HomeFakeDatasource(this._finance);

  @override
  Future<HomeData> getHome() async {
    await Future.delayed(const Duration(milliseconds: 300));
    return _snapshot();
  }

  @override
  Future<HomeData> setBalance(num amount) async {
    await _finance.setStartingBalance(amount);
    return _snapshot();
  }

  HomeData _snapshot() {
    final s = _finance.snapshot;
    final now = DateTime.now();
    final thisMonth = s.transactions.where(
      (t) => t.date.year == now.year && t.date.month == now.month,
    );
    num sum(bool income) => thisMonth
        .where((t) => t.isIncome == income)
        .fold<num>(0, (a, t) => a + t.amount.abs());

    return HomeData(
      userName: s.userName,
      isNew: s.isNew,
      balanceSet: s.balanceSet,
      balance: s.balance,
      monthIncome: sum(true),
      monthExpenses: sum(false),
      transactionsCount: s.transactions.length,
      goalsCount: s.goals.length,
      remindersCount: s.reminders.length,
      recentTransactions: [
        for (final t in s.transactions.take(4))
          TransactionItem(
            id: t.id,
            title: t.title,
            category: t.categoryId,
            categoryLabel: s.category(t.categoryId)?.name ?? '',
            amount: t.amount,
            date: t.date,
          ),
      ],
      upcomingPayments: [
        for (final r in s.reminders.where(
          (r) => r.enabled && r.dueIn(now) >= 0,
        ))
          UpcomingPayment(
            id: r.id,
            title: r.title,
            category: r.categoryId,
            amount: r.amount,
            dueDate: r.dueDate,
          ),
      ],
      // TODO: overall monthly budget and AI estimate come from the backend.
      budget: s.budgets.isEmpty
          ? null
          : BudgetSummary(month: now, spent: 5_460_000, limit: 8_000_000),
      aiSavingAmount: s.transactions.isEmpty ? null : 1_240_000,
      fetchedAt: now,
    );
  }
}
