import 'package:finora/domain/models/home/home_data.dart';
import 'package:finora/infrastructure/datasources/finance_fake_store.dart';
import 'package:finora/infrastructure/datasources/home_fake_datasource.dart';
import 'package:flutter_test/flutter_test.dart';

HomeData _data({
  bool isNew = true,
  bool balanceSet = false,
  int transactions = 0,
  int goals = 0,
  int reminders = 0,
}) => HomeData(
  userName: 'Doston Karimov',
  isNew: isNew,
  balanceSet: balanceSet,
  balance: 0,
  monthIncome: 0,
  monthExpenses: 0,
  transactionsCount: transactions,
  goalsCount: goals,
  remindersCount: reminders,
  recentTransactions: const [],
  upcomingPayments: const [],
  fetchedAt: DateTime(2026, 9, 28),
);

void main() {
  group('HomeData', () {
    test('fresh user who skipped balance', () {
      final d = _data();
      expect(d.needBalance, isTrue);
      expect(d.showChecklist, isTrue);
      expect(d.showInsights, isFalse);
      expect(d.checklistDone, 0);
    });

    test('steps complete from real data', () {
      final d = _data(balanceSet: true, transactions: 3, goals: 1);
      expect(d.needBalance, isFalse);
      expect(d.isStepDone(.balance), isTrue);
      expect(d.isStepDone(.transaction), isTrue);
      expect(d.isStepDone(.goal), isTrue);
      expect(d.isStepDone(.reminder), isFalse);
      expect(d.checklistDone, 3);
      expect(d.showChecklist, isTrue);
    });

    test('checklist hides at 4 of 4', () {
      final d = _data(
        balanceSet: true,
        transactions: 1,
        goals: 1,
        reminders: 1,
      );
      expect(d.showChecklist, isFalse);
    });

    test('regular user sees insights, no checklist', () {
      final d = _data(isNew: false);
      expect(d.showInsights, isTrue);
      expect(d.showChecklist, isFalse);
      expect(d.needBalance, isFalse);
    });
  });

  test('BudgetSummary.daysLeft counts to the end of the month', () {
    final b = BudgetSummary(month: DateTime(2026, 9, 1), spent: 1, limit: 2);
    expect(b.daysLeft(DateTime(2026, 9, 28, 15)), 2);
    expect(b.daysLeft(DateTime(2026, 9, 30)), 0);
    expect(b.progress, 0.5);
  });

  test('saving a balance completes step 1 and hides the hero pill', () async {
    final home = HomeFakeDatasource(FinanceFakeStore());
    final before = await home.getHome();
    expect(before.needBalance, isTrue);

    final after = await home.setBalance(100000);
    expect(after.balance, 100000);
    expect(after.needBalance, isFalse);
    expect(after.checklistDone, 1);
    expect(after.showChecklist, isTrue);
  });
}
