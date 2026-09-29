import 'package:finora/domain/models/finance/finance_models.dart';

/// Transactions, categories, budgets, goals, reminders and accounts.
///
/// Methods throw `ApiFailure` on errors.
abstract class FinanceFacade {
  FinanceSnapshot get snapshot;

  /// Emits after every change.
  Stream<FinanceSnapshot> get changes;

  /// Loads everything from the server.
  Future<void> refresh();

  /// Next page of [FinanceSnapshot.transactions] (Activity).
  Future<void> loadMoreTransactions();

  /// Drops the data of the signed-out user.
  void reset();

  Future<void> setStartingBalance(num amount, {BalanceLocation? location});

  Future<void> addTransaction({
    required String categoryId,
    required num amount,
    String? title,
    String? receiptId,
  });

  Future<void> saveCategory(Category category);

  /// [reassignTo] moves the category's transactions (`409 category_in_use`).
  Future<void> deleteCategory(String id, {String? reassignTo});

  Future<Goal> addGoal({
    required String name,
    required String icon,
    required num target,
    required DateTime due,
    num? autoSave,
  });

  /// [amount] > 0 deposits, < 0 withdraws.
  Future<Goal> moveGoalMoney(String goalId, num amount);

  /// Newest first.
  Future<List<GoalEntry>> goalHistory(String goalId);

  Future<void> setGoalAutoSave(String goalId, num? amount);

  /// Returns the amount moved back to the main account.
  Future<num> deleteGoal(String goalId);

  Future<void> addReminder(Reminder reminder);

  Future<void> setReminderEnabled(String id, bool enabled);

  Future<void> setAccountFrozen(String id, bool frozen);
}
