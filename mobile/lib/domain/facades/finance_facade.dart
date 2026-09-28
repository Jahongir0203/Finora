import 'package:finora/domain/models/finance/finance_models.dart';

/// Transactions, categories, budgets, goals, reminders and accounts.
abstract class FinanceFacade {
  FinanceSnapshot get snapshot;

  /// Emits after every change.
  Stream<FinanceSnapshot> get changes;

  Future<void> setStartingBalance(num amount, {BalanceLocation? location});

  Future<void> addTransaction({
    required String categoryId,
    required num amount,
    String? title,
  });

  Future<void> saveCategory(Category category);

  Future<void> deleteCategory(String id);

  Future<Goal> addGoal({
    required String name,
    required String icon,
    required num target,
    required DateTime due,
    num? autoSave,
  });

  /// [amount] > 0 deposits, < 0 withdraws.
  Future<Goal> moveGoalMoney(String goalId, num amount);

  Future<void> setGoalAutoSave(String goalId, num? amount);

  Future<void> deleteGoal(String goalId);

  Future<void> addReminder(Reminder reminder);

  Future<void> setReminderEnabled(String id, bool enabled);

  Future<void> setAccountFrozen(String id, bool frozen);
}
