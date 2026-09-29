/// Everything the Home screen shows (docs/screens/HOME_SCREENS.md §1).
class HomeData {
  final String userName;

  /// True until the Get started checklist is complete (`get_started`).
  final bool isNew;

  /// False when the user skipped Starting balance.
  final bool balanceSet;
  final num balance;
  final num monthIncome;

  /// Positive number.
  final num monthExpenses;

  final bool hasTransactions;
  final bool hasGoals;
  final bool hasReminders;

  /// Bell badge.
  final int unreadNotifications;

  /// Newest first, at most 4.
  final List<TransactionItem> recentTransactions;

  /// Soonest first.
  final List<UpcomingPayment> upcomingPayments;
  final BudgetSummary? budget;

  /// "You could save {amount} UZS this month".
  final num? aiSavingAmount;

  /// When this snapshot was loaded (offline banner).
  final DateTime fetchedAt;

  const HomeData({
    required this.userName,
    required this.isNew,
    required this.balanceSet,
    required this.balance,
    required this.monthIncome,
    required this.monthExpenses,
    required this.hasTransactions,
    required this.hasGoals,
    required this.hasReminders,
    this.unreadNotifications = 0,
    required this.recentTransactions,
    required this.upcomingPayments,
    required this.fetchedAt,
    this.budget,
    this.aiSavingAmount,
  });

  bool isStepDone(ChecklistStep step) => switch (step) {
    .balance => balanceSet,
    .transaction => hasTransactions,
    .goal => hasGoals,
    .reminder => hasReminders,
  };

  int get checklistDone => ChecklistStep.values.where(isStepDone).length;

  bool get needBalance => isNew && !balanceSet;

  bool get showChecklist =>
      isNew && checklistDone < ChecklistStep.values.length;

  /// AI + budget cards.
  bool get showInsights => !isNew;
}

enum ChecklistStep { balance, transaction, goal, reminder }

class TransactionItem {
  final String id;
  final String title;

  /// Category id (`groceries`, `salary`, or a user category uuid).
  final String category;
  final String categoryLabel;

  /// Positive for income, negative for expenses.
  final num amount;
  final DateTime date;

  const TransactionItem({
    required this.id,
    required this.title,
    required this.category,
    required this.categoryLabel,
    required this.amount,
    required this.date,
  });

  bool get isIncome => amount > 0;
}

class UpcomingPayment {
  final String id;
  final String title;
  final String category;
  final num amount;
  final DateTime dueDate;

  const UpcomingPayment({
    required this.id,
    required this.title,
    required this.category,
    required this.amount,
    required this.dueDate,
  });
}

class BudgetSummary {
  /// Any day in the budget's month.
  final DateTime month;
  final num spent;
  final num limit;

  const BudgetSummary({
    required this.month,
    required this.spent,
    required this.limit,
  });

  double get progress => limit <= 0 ? 0 : spent / limit;

  int daysLeft(DateTime now) {
    final lastDay = DateTime(month.year, month.month + 1, 0);
    final today = DateTime(now.year, now.month, now.day);
    return lastDay.difference(today).inDays.clamp(0, 31);
  }
}
